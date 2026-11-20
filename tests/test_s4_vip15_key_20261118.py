"""S4 VIP15 key issuance/claim tests with synthetic UID and isolated sqlite only."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from gxb2 import s4_exclusive, vip, live_service, auth
from gxb2.engine import Engine

class TestS4Key(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'isolated_mail.sqlite3'
        db = sqlite3.connect(self.path)
        db.executescript('''
           CREATE TABLE players(uid TEXT,server_id TEXT,character_name TEXT,status TEXT);
           CREATE TABLE mail(id TEXT PRIMARY KEY,uid TEXT,server_id TEXT,
             character_name TEXT,title TEXT,body TEXT,attachments TEXT,
             status TEXT,created_at INTEGER,claimed_at INTEGER DEFAULT 0,
             read_at INTEGER DEFAULT 0,operator TEXT);
           CREATE TABLE audit(at INTEGER,operator TEXT,action TEXT,target TEXT,detail TEXT);
        ''')
        for s in ('S1','S2','S99'):
            db.execute("INSERT INTO players VALUES('KEY-UID',?,?,'active')",
                       (s,'Test '+s))
        db.commit();db.close()
        def open_db():
            conn = sqlite3.connect(self.path)
            conn.row_factory = sqlite3.Row
            return conn
        self.mock_db = patch.object(live_service, '_db', open_db)
        self.mock_db.start()
        self.addCleanup(self.mock_db.stop)
        self.need = int(next(x['need_exp'] for x in vip.LEVELS if x['level'] == 15))

    def state(self,world='S1',earned=None):
        return dict(uid='KEY-UID',server_id=world,name='Test '+world,
                    vip_paid_exp=self.need if earned is None else earned)

    def test_one_milestone_mail_for_future_server_and_current_server(self):
        self.assertFalse(s4_exclusive.ensure_key_mail(self.state(earned=self.need-1)))
        self.assertTrue(s4_exclusive.ensure_key_mail(self.state(world='S99')))
        self.assertFalse(s4_exclusive.ensure_key_mail(self.state(world='S1')))
        self.assertFalse(s4_exclusive.ensure_key_mail(self.state(world='S2')))
        self.assertFalse(s4_exclusive.ensure_key_mail(self.state(world='S4')))
        db=sqlite3.connect(self.path)
        row=db.execute('SELECT id,server_id,attachments,title,status FROM mail').fetchone()
        self.assertEqual(db.execute('SELECT count(*) FROM mail').fetchone()[0],1)
        self.assertEqual(row[0],s4_exclusive.access_key_mail_id('KEY-UID'))
        self.assertEqual(row[1],'S99')
        self.assertEqual(json.loads(row[2]),{s4_exclusive.ACCESS_KEY:1})
        self.assertIn('VIP 15',row[3])
        self.assertEqual(row[4],'pending')
        db.close()

    def test_claimed_key_only_unlocks_same_uid(self):
        s4_exclusive.ensure_key_mail(self.state())
        self.assertFalse(s4_exclusive.key_claimed('KEY-UID'))
        with self.assertRaisesRegex(ValueError,'Chìa Khóa'):
            s4_exclusive.ensure_key_claimed('KEY-UID','S4')
        db=sqlite3.connect(self.path)
        db.execute("UPDATE mail SET status='claimed' WHERE uid='KEY-UID'")
        db.commit();db.close()
        self.assertTrue(s4_exclusive.key_claimed('KEY-UID'))
        self.assertFalse(s4_exclusive.key_claimed('KEY-OTHER'))
        self.assertTrue(s4_exclusive.ensure_key_claimed('KEY-UID','S4'))
        self.assertTrue(s4_exclusive.ensure_key_claimed('KEY-OTHER','S99'))
        with self.assertRaisesRegex(ValueError,'Chìa Khóa'):
            s4_exclusive.ensure_key_claimed('KEY-OTHER','S4')

    def test_current_s4_cannot_mint_key(self):
        db=sqlite3.connect(self.path)
        db.execute("INSERT INTO players VALUES('KEY-UID','S4','Special','active')")
        db.commit();db.close()
        self.assertFalse(s4_exclusive.ensure_key_mail(self.state('S4')))
        self.assertFalse(s4_exclusive.key_claimed('KEY-UID'))

    def test_unauthorized_uid_is_not_sent_mail(self):
        x=self.state('S99');x['uid']='OTHER'
        with self.assertRaisesRegex(ValueError, 'nhân vật'):
            s4_exclusive.ensure_key_mail(x)
        db=sqlite3.connect(self.path)
        self.assertEqual(db.execute('SELECT COUNT(*) FROM mail').fetchone()[0],0)
        db.close()

    def test_s4_character_gate_requires_claimed_key_even_if_vip15(self):
        current={'account':{'uid':'KEY-UID','server_id':'S1'},'character_name':'Test S1'}
        with patch.object(auth,'session',return_value=current), \
             patch.object(s4_exclusive,'ensure_open',return_value={}), \
             patch.object(s4_exclusive,'ensure_vip15',return_value=self.need), \
             patch.object(s4_exclusive,'ensure_key_claimed',side_effect=ValueError('Chìa Khóa')), \
             patch.object(live_service,'register_player') as register:
            with self.assertRaisesRegex(ValueError,'Chìa Khóa'):
                auth.create_character('FAKE-TOKEN','S4','Special')
            register.assert_not_called()

    def test_existing_vip15_snapshot_issues_one_mail(self):
        e=Engine(Path(self.tmp.name)/'player_s1.sqlite3',identity=('KEY-UID','S1'))
        self.addCleanup(e.close)
        e.bind_identity('KEY-UID','S1','Test S1')
        state=e._load()
        state['vip_paid_exp']=self.need
        e._save_profile(state)
        e.db.commit()
        e.snapshot()
        e.snapshot()
        db=sqlite3.connect(self.path)
        self.assertEqual(db.execute('SELECT COUNT(*) FROM mail').fetchone()[0],1)
        db.close()

    def test_paid_vip_claim_issues_key_and_key_claim_adds_bag_item(self):
        e=Engine(Path(self.tmp.name)/'player_s1.sqlite3',identity=('KEY-UID','S1'))
        self.addCleanup(e.close)
        e.bind_identity('KEY-UID','S1','Test S1')
        current=e._load()
        current['vip_paid_exp']=self.need-10
        e._save_profile(current);e.db.commit()
        db=sqlite3.connect(self.path)
        db.execute("""INSERT INTO mail(id,uid,server_id,character_name,title,body,attachments,
             status,created_at,operator) VALUES(?,?,?,?,?,?,?,'pending',?,'GM')""",
             ('GM-PAID','KEY-UID','S1','Test S1','VIP','EXP',
              json.dumps({vip.VIP_EXP_REWARD_ID:20}),1))
        db.commit();db.close()
        result=e.claim_live_mail('GM-PAID')
        self.assertGreaterEqual(result['state']['vip_info']['level'],15)
        db=sqlite3.connect(self.path)
        self.assertEqual(db.execute('SELECT COUNT(*) FROM mail WHERE operator=?',
                                    (s4_exclusive.ACCESS_OPERATOR,)).fetchone()[0],1)
        db.close()
        keyid=s4_exclusive.access_key_mail_id('KEY-UID')
        prize=e.claim_live_mail(keyid)
        self.assertEqual(prize['attachments'],{s4_exclusive.ACCESS_KEY:1})
        self.assertEqual(prize['state']['items']['990004'],1)
        self.assertTrue(s4_exclusive.key_claimed('KEY-UID'))
        with self.assertRaisesRegex(ValueError,'Thư đã'):
            e.claim_live_mail(keyid)
        db=sqlite3.connect(self.path)
        self.assertEqual(db.execute('SELECT COUNT(*) FROM mail WHERE operator=?',
                                    (s4_exclusive.ACCESS_OPERATOR,)).fetchone()[0],1)
        db.close()

if __name__=='__main__':
    unittest.main()
