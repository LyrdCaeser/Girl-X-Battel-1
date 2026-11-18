"""S4 removal tests use only a temporary SQLite database, never live Neon."""
import json
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from gxb2 import live_service, database, s4_gm, s4_exclusive, auth
from gxb2.player_engines import PlayerEnginePool

class TestS4GMDelete(unittest.TestCase):
    def setUp(self):
        if database.is_postgres():
            self.skipTest('Never run destructive tests on production Neon')
        td=tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.root=Path(td.name)
        base=database.connect
        live=patch.object(live_service,'_db',lambda:base(self.root/'isolated_live.sqlite3','live'))
        live.start();self.addCleanup(live.stop)
        self.auth_db=patch.object(auth,'_db',lambda:base(self.root/'isolated_auth.sqlite3','auth'))
        self.auth_db.start();self.addCleanup(self.auth_db.stop)
        with s4_gm._lock:
            old=dict(s4_gm._challenges)
            s4_gm._challenges.clear()
        def restore():
            with s4_gm._lock:
                s4_gm._challenges.clear()
                s4_gm._challenges.update(old)
        self.addCleanup(restore)
        live_service.create_world('S4',s4_exclusive.NAME)
        live_service.register_player('UID-1','S4','Hero S4')
        live_service.register_player('UID-1','S1','Hero S1')
        live_service.register_player('UID-2','S4','Other S4')
        db=live_service._db()
        db.execute("""CREATE TABLE IF NOT EXISTS player_profiles(
            uid TEXT NOT NULL,server_id TEXT NOT NULL,data TEXT NOT NULL,
            updated_at INTEGER NOT NULL,PRIMARY KEY(uid,server_id))""")
        db.execute("""CREATE TABLE IF NOT EXISTS player_battles(
            uid TEXT NOT NULL,server_id TEXT NOT NULL,id INTEGER NOT NULL,
            stage INTEGER NOT NULL,report TEXT NOT NULL,PRIMARY KEY(uid,server_id,id))""")
        for uid,world,payload in (('UID-1','S4',{'girls':[25,25], 's4_exclusive_claimed':True}),
                                  ('UID-1','S1',{'vip_paid_exp':3100000}),
                                  ('UID-2','S4',{'girls':[6]})):
            db.execute('INSERT INTO player_profiles VALUES(?,?,?,1)',
                       (uid,world,json.dumps(payload)))
        db.execute('INSERT INTO player_battles VALUES(?,?,?,?,?)',
                   ('UID-1','S4',1,44,'{"won":true}'))
        for mid,uid,world in [('S4-GIFT','UID-1','S4'),('S1-KEY','UID-1','S1'),
                              ('OTHER-GIFT','UID-2','S4')]:
            db.execute("""INSERT INTO mail
                   (id,uid,server_id,character_name,title,body,attachments,
                    status,created_at,operator)
                   VALUES(?,?,?,?,?,?,?,'claimed',100,'TEST')""",
                   (mid,uid,world,'Example','Gift','Body','{}'))
        db.commit();db.close()

    def query(self,sql,params=()):
        db=live_service._db()
        try:return [dict(x) for x in db.execute(sql,params).fetchall()]
        finally:db.close()

    def test_preview_is_readonly(self):
        before=self.query('SELECT * FROM players')
        result=s4_gm.preview('UID-1')
        self.assertEqual(result['character_name'],'Hero S4')
        self.assertEqual(result['server_id'],'S4')
        self.assertTrue(result['can_delete'])
        self.assertEqual(result['counts']['player_battles'],1)
        self.assertTrue(result['nonce'])
        self.assertEqual(self.query('SELECT * FROM players'),before)
        self.assertFalse(self.query("SELECT 1 FROM sqlite_master WHERE name='s4_character_archives'"))

    def test_delete_archives_exact_world_and_recreation(self):
        snap=s4_gm.preview('UID-1')
        with self.assertRaisesRegex(ValueError,'XOA S4'):
            s4_gm.delete('UID-1','Hero S4',snap['nonce'],'XOA S1','GM')
        result=s4_gm.delete('UID-1','Hero S4',snap['nonce'],'XOA S4','GM')
        self.assertTrue(result['archived'])
        self.assertEqual(result['deleted_rows']['players'],1)
        self.assertEqual(result['deleted_rows']['player_battles'],1)
        self.assertIsNone(live_service.player('UID-1','S4'))
        self.assertIsNotNone(live_service.player('UID-1','S1'))
        self.assertIsNotNone(live_service.player('UID-2','S4'))
        self.assertEqual(self.query('SELECT id FROM mail ORDER BY id'),
                         [{'id':'OTHER-GIFT'},{'id':'S1-KEY'}])
        self.assertEqual(self.query('SELECT uid,server_id FROM player_profiles ORDER BY server_id,uid'),
                         [{'uid':'UID-1','server_id':'S1'},{'uid':'UID-2','server_id':'S4'}])
        archived=self.query('SELECT * FROM s4_character_archives')
        self.assertEqual(len(archived),1)
        self.assertEqual(archived[0]['id'],result['archive_id'])
        backup=json.loads(archived[0]['snapshot'])
        self.assertEqual(backup['mail'][0]['id'],'S4-GIFT')
        self.assertIn('s4_exclusive_claimed',backup['player_profiles'][0]['data'])
        self.assertTrue(self.query("SELECT 1 FROM audit WHERE action='admin.s4.character_delete'"))
        with self.assertRaisesRegex(ValueError,'hết hạn'):
            s4_gm.delete('UID-1','Hero S4',snap['nonce'],'XOA S4','GM')
        live_service.register_player('UID-1','S4','New Hero')
        with patch.object(s4_exclusive,'ensure_vip15',return_value=3100000):
            s4_exclusive.ensure_welcome('UID-1','S4','New Hero')
        rows=live_service.mailbox('UID-1','S4')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['attachments'],{s4_exclusive.KEY:1})

    def test_requires_matching_target_and_valid_preview(self):
        preview=s4_gm.preview('UID-1')
        for name,uid,nonce,phrase in [
             ('wrong name','UID-1',preview['nonce'],'XOA S4'),
             ('Hero S4','UID-2',preview['nonce'],'XOA S4'),
             ('Hero S4','UID-1','invalid','XOA S4')]:
            with self.assertRaises(ValueError):
                s4_gm.delete(uid,name,nonce,phrase,'GM')
        self.assertIsNotNone(live_service.player('UID-1','S4'))
        with self.assertRaisesRegex(ValueError,'Không tìm thấy'):
            s4_gm.preview('UID-NOT-EXIST')

    def test_blocks_social_link_and_pending_order(self):
        db=live_service._db()
        db.execute("INSERT INTO friendships(uid_a,uid_b,server_id,created_at) VALUES('UID-1','UID-2','S4',0)")
        db.commit();db.close()
        p=s4_gm.preview('UID-1')
        self.assertFalse(p['can_delete'])
        self.assertTrue(any(x['reason']=='Bạn bè' for x in p['blockers']))
        self.assertNotIn('nonce',p)
        db=live_service._db()
        db.execute("DELETE FROM friendships WHERE server_id='S4'")
        db.commit();db.close()
        p=s4_gm.preview('UID-1')
        db=live_service._db()
        db.execute("""INSERT INTO orders (id,uid,server_id,character_name,package,
            note,status,reward,created_at) VALUES(?,?,?,?,?,'','pending','{}',0)""",
            ('ORD-S4','UID-1','S4','Hero S4','CUSTOM'))
        db.commit();db.close()
        with self.assertRaisesRegex(ValueError,'liên kết'):
            s4_gm.delete('UID-1','Hero S4',p['nonce'],'XOA S4','GM')
        self.assertIsNotNone(live_service.player('UID-1','S4'))
        self.assertFalse(self.query(
            "SELECT 1 FROM sqlite_master WHERE name='s4_character_archives'"))

    def test_archive_failure_rolls_back_all_deletions(self):
        p=s4_gm.preview('UID-1')
        with patch.object(s4_gm,'_capture',side_effect=ValueError('FAIL BACKUP')):
            with self.assertRaisesRegex(ValueError,'FAIL BACKUP'):
                s4_gm.delete('UID-1','Hero S4',p['nonce'],'XOA S4','GM')
        self.assertIsNotNone(live_service.player('UID-1','S4'))
        self.assertEqual(len(live_service.mailbox('UID-1','S4')),1)

    def test_pool_evicts_only_s4(self):
        class FakeEngine:
            lock=threading.RLock()
            def __init__(self):self.closed=False
            def close(self):self.closed=True
        pool=PlayerEnginePool()
        s1,s4=FakeEngine(),FakeEngine()
        pool._engines={('UID-1','S1'):s1,('UID-1','S4'):s4}
        self.assertEqual(pool.run_exclusive('UID-1','S4',lambda:'ok'),'ok')
        self.assertTrue(s4.closed)
        self.assertFalse(s1.closed)
        self.assertIn(('UID-1','S1'),pool._engines)
        self.assertNotIn(('UID-1','S4'),pool._engines)

    def test_revoke_only_s4_sessions(self):
        db=auth._db()
        # The real auth schema is bootstrapped by database.connect.
        db.execute("""INSERT INTO accounts(id,uid,username,email,password_hash,salt,status,created_at,last_login)
                    VALUES(1,'UID-1','tester','', 'hash','salt','active',0,0)""")
        for world,i in [('S1',1),('S4',2)]:
            db.execute("""INSERT INTO sessions(token_hash,session_id,account_id,server_id,
                       user_agent,remote_addr,created_at,last_seen,expires_at)
                       VALUES(?,?,?,?,?,?,0,0,99999999999)""",
                       (f'token{i}',f'session{i}',1,world,'test','localhost'))
        db.commit();db.close()
        result=auth.revoke_world_sessions('UID-1','S4')
        self.assertEqual(result['revoked'],1)
        db=auth._db()
        try:
            self.assertEqual([x['server_id'] for x in db.execute(
                'SELECT server_id FROM sessions').fetchall()],['S1'])
        finally:db.close()
        with self.assertRaisesRegex(ValueError,'S4'):
            auth.revoke_world_sessions('UID-1','S1')

if __name__=='__main__':
    unittest.main()
