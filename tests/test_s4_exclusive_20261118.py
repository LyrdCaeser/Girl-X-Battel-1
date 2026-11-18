"""All tests isolated; never reads/writes the production Neon account or mail."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timezone

from gxb2 import s4_exclusive, goddess_gifts, dress, game_calendar, vip, auth, live_service
from gxb2.engine import Engine, new_state


class S4Tests(unittest.TestCase):
    def test_vip15_exclusive_gate(self):
        minexp = next(int(x['need_exp']) for x in vip.LEVELS if x['level'] == 15)
        with patch.object(s4_exclusive, 'paid_exp_in_other_worlds', return_value=minexp-1):
            self.assertEqual(s4_exclusive.ensure_vip15('uid-test', 'S3'), 0)
            with self.assertRaisesRegex(ValueError, 'VIP 15'):
                s4_exclusive.ensure_vip15('uid-test', 'S4')
        with patch.object(s4_exclusive, 'paid_exp_in_other_worlds', return_value=minexp):
            self.assertEqual(s4_exclusive.ensure_vip15('uid-test', 's4'), minexp)

    def test_create_character_blocks_nonvip_before_player_write(self):
        current={'account':{'uid':'U-TEST','server_id':'S1'},'character_name':'Hero'}
        with patch.object(auth, 'session', return_value=current), \
             patch.object(s4_exclusive,'ensure_open',return_value={}), \
             patch.object(s4_exclusive,'ensure_vip15',side_effect=ValueError('VIP 15')), \
             patch.object(live_service,'register_player') as register:
            with self.assertRaisesRegex(ValueError,'VIP 15'):
                auth.create_character('fake-token','S4','Test Character')
            register.assert_not_called()

    def test_welcome_once_and_exact_uid_world(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'world.sqlite3'
            db=sqlite3.connect(path)
            db.executescript("""CREATE TABLE players(uid TEXT,server_id TEXT,character_name TEXT,status TEXT);
                CREATE TABLE mail(id TEXT PRIMARY KEY,uid TEXT,server_id TEXT,
                 character_name TEXT,title TEXT,body TEXT,attachments TEXT,
                 status TEXT,created_at INTEGER,operator TEXT);""")
            db.execute("INSERT INTO players VALUES('U-TEST','S4','Special','active')")
            db.execute("INSERT INTO players VALUES('U-TEST','S1','Regular','active')")
            db.commit();db.close()
            def open_db():
                return sqlite3.connect(path)
            with patch.object(s4_exclusive,'ensure_vip15',return_value=3100000),\
                 patch.object(live_service,'_db',open_db):
                self.assertFalse(s4_exclusive.ensure_welcome('U-TEST','S1','Regular'))
                self.assertTrue(s4_exclusive.ensure_welcome('U-TEST','S4','Special'))
                self.assertTrue(s4_exclusive.ensure_welcome('U-TEST','S4','Special'))
            db=sqlite3.connect(path)
            rows=db.execute('SELECT uid,server_id,attachments,status FROM mail').fetchall();db.close()
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0][0:2],('U-TEST','S4'))
            self.assertEqual(rows[0][3],'pending')
            self.assertIn(s4_exclusive.KEY,rows[0][2])

    def test_gifts_idempotent_25_star_level_one_without_items(self):
        from types import SimpleNamespace
        state = new_state()
        state.update({'server_id': 'S4', 'uid':'TEST-ISOLATED-S4'})
        standard = len(state['partners'])
        cap=lambda p,real=True: Engine.level_cap(SimpleNamespace(developer=False),p,real=real)
        got = s4_exclusive.grant_bundle(state,1,cap)
        gifted=state['partners'][standard:]
        self.assertEqual(len(gifted), 104)
        self.assertEqual(got['wish_count'],104)
        self.assertEqual(len({p['table_id'] for p in gifted}),104)
        self.assertTrue(all(p['lv']==1 and p['awake']==15 and not any(p['equips']) for p in gifted))
        self.assertTrue(all(p.get('pos')==0 for p in gifted))
        self.assertEqual(got['skin_count'],324)
        self.assertEqual(len(got['skin_details']),324)
        self.assertEqual({x['id'] for x in got['skin_details']},set(got['skin_ids']))
        self.assertTrue(all(isinstance(x['name'],str) and x['name'] for x in got['skin_details']))
        self.assertEqual(len(state['skins']['collected']),324)
        self.assertEqual(len(state['dress']['owned']),242)
        self.assertTrue(all(
            int(v)==dress.max_star(int(did)) for did,v in state['dress']['owned'].items()))
        with self.assertRaisesRegex(ValueError,'đã nhận'):
            s4_exclusive.grant_bundle(state,1,cap)
        with self.assertRaisesRegex(ValueError,'chỉ dành cho S4'):
            s4_exclusive.grant_bundle({'server_id':'S2'},1,cap)

    def test_catalog_expansion_reconciles_old_24_rewards_without_duplicates(self):
        state=new_state()
        state.update({'uid':'TEST-ISOLATED-S4','server_id':'S4'})
        from gxb2 import wish
        old_target={goddess_gifts.resolve(x,25)[0] for x in wish.D['partners']}
        for tid in sorted(old_target):
            goddess_gifts.grant(
                state,{'girl_id':tid,'stars':25,'level':1,'stats':{}},lambda *a,**kw:666)
        state.setdefault('skins',{})['collected']=list(
            s4_exclusive._skin_ids(old_target)[:76])
        state['s4_exclusive_claimed']=True
        old_skins=set(state['skins']['collected'])
        old_ids=[p['partner_id'] for p in state['partners']]
        before={p['table_id'] for p in state['partners'] if p['awake']>=15}
        bonus=s4_exclusive.grant_bundle(state,3,lambda *a,**kw:666)
        self.assertEqual(bonus['wish_count'],104-len(before))
        self.assertEqual(bonus['skin_count'],324-len(old_skins))
        self.assertEqual(set(bonus['skin_ids'])&old_skins,set())
        self.assertEqual(len({p['table_id'] for p in state['partners'] if p['awake']>=15}),104)
        self.assertEqual(len(state['skins']['collected']),324)
        self.assertEqual([p['partner_id'] for p in state['partners'][:len(old_ids)]],old_ids)
        self.assertEqual(state['s4_catalog_version'],2)
        with self.assertRaisesRegex(ValueError,'đã nhận'):
            s4_exclusive.grant_bundle(state,3,lambda *a,**kw:666)

    def test_catalog_compensation_mail_is_idempotent_and_s4_only(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'mail.sqlite3'
            db=sqlite3.connect(path)
            db.executescript("""CREATE TABLE players(uid TEXT,server_id TEXT,status TEXT);
             CREATE TABLE mail(id TEXT PRIMARY KEY,uid TEXT,server_id TEXT,
              character_name TEXT,title TEXT,body TEXT,attachments TEXT,
              status TEXT,created_at INTEGER,operator TEXT);""")
            db.execute("INSERT INTO players VALUES('TEST-S4','S4','active')")
            db.commit();db.close()
            with patch.object(live_service,'_db',lambda:sqlite3.connect(path)):
                self.assertFalse(s4_exclusive.ensure_catalog_upgrade('TEST-S4','S1','X'))
                self.assertTrue(s4_exclusive.ensure_catalog_upgrade('TEST-S4','S4','X'))
                self.assertTrue(s4_exclusive.ensure_catalog_upgrade('TEST-S4','S4','X'))
            with sqlite3.connect(path) as db:
                r=db.execute("SELECT id,uid,server_id,attachments FROM mail").fetchall()
                self.assertEqual(len(r),1)
                self.assertEqual(r[0][1:3],('TEST-S4','S4'))
                self.assertEqual(__import__('json').loads(r[0][3]),{s4_exclusive.KEY:3})

    def test_30_day_calendar_s4_only(self):
        now=int(datetime(2026,11,18,tzinfo=timezone.utc).timestamp())
        a=game_calendar.snapshot(now,server_id='S4')
        b=game_calendar.snapshot(now,server_id='S4')
        regular=game_calendar.snapshot(now,server_id='S2')
        self.assertTrue(a['exclusive_s4'])
        self.assertEqual(len(a['featured_30_days']),30)
        self.assertEqual(a['featured_30_days'],b['featured_30_days'])
        self.assertGreater(len(a['events']),len(regular['events']))
        self.assertNotIn('exclusive_s4',regular)
        self.assertNotEqual(a['featured_30_days'][0]['ids'],a['featured_30_days'][1]['ids'])
        self.assertEqual(a['featured_30_days'][0]['day'],'2026-11-18')


if __name__=='__main__':
    unittest.main()
