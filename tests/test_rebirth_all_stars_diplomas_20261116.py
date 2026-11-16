"""Offline rebirth regressions; each test uses a temporary SQLite state, never Neon."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2.engine import (
    Engine, GameError, REBIRTH_DIPLOMA_LOW, REBIRTH_DIPLOMA_HIGH,
    REBIRTH_FREE_PER_DAY, TABLES,
)


def build(pid, table, awake=0, **kwargs):
    return {
        'partner_id':pid,'table_id':table,'lv':1,'grade':0,
        'awake':awake,'equips':[],'pos':0,'show_skin':1,**kwargs
    }


class RebirthRulesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.game = Engine(Path(self.temp.name)/'rebirth-test.sqlite3')
        self.state = self.game._load()
        self.state['rebirth'] = {'day':self.game.rebirth_day(),'used':0}

    def tearDown(self):
        self.game.close()
        self.temp.cleanup()

    def add(self, table, awake=0, **kwargs):
        pid = max(p['partner_id'] for p in self.state['partners'])+1
        self.state['partners'].append(build(pid, table, awake, **kwargs))
        self.state['next_partner_id'] = max(self.state['next_partner_id'], pid+1)
        return pid

    def dispatch(self, pid):
        return self.game._dispatch(
            'ROLLBACK_PARTNER', {'partner_id':pid}, self.state)

    def test_all_stars_including_six_seven_through_twentyfive(self):
        cases=[
            (41001,0), (51001,0),
            (651001,0), (651001,1), (651001,2), (651001,3),
            (751001,0), (751001,1), (751001,5),
            (751001,6), (751001,10), (751001,15),
            (757001,0), (757001,5),
            (561001,0), (661001,0), (761001,0),
        ]
        for tid, awake in cases:
            with self.subTest(tid=tid,awake=awake):
                pid=self.add(tid,awake)
                before=json.loads(json.dumps(self.state))
                plan=self.game.rebirth_plan(self.state,pid)
                self.assertEqual(before,self.state)
                self.assertTrue(plan['returns'])
                self.assertTrue(all(x['table_id'] in [int(k) for k in TABLES['partner']] for x in plan['returns']))
                self.assertEqual(plan['stars'],int(TABLES['partner'][str(tid)]['max_star'])+awake)
                self.state['partners'].pop()

    def test_five_free_uses_and_sixth_low_diploma(self):
        ids=[self.add(651001) for _ in range(6)]
        for i,pid in enumerate(ids[:5]):
            plan=self.game.rebirth_plan(self.state,pid)
            self.assertTrue(plan['is_free'])
            self.assertEqual(plan['free_left'],5-i)
            self.dispatch(pid)
            self.assertEqual(self.state['rebirth']['used'],i+1)
        sixth=ids[5]
        plan=self.game.rebirth_plan(self.state,sixth)
        self.assertEqual(plan['cost'], {REBIRTH_DIPLOMA_LOW:1})
        self.assertFalse(plan['can_afford'])
        snapshot=json.loads(json.dumps(self.state))
        with self.assertRaisesRegex(GameError,'Diploma'):
            self.dispatch(sixth)
        self.assertEqual(snapshot,self.state)
        self.state['items'][REBIRTH_DIPLOMA_LOW]=1
        self.state['items'][REBIRTH_DIPLOMA_HIGH]=19
        self.dispatch(sixth)
        self.assertEqual(self.state['items'][REBIRTH_DIPLOMA_LOW],0)
        self.assertEqual(self.state['items'][REBIRTH_DIPLOMA_HIGH],19)
        self.assertEqual(self.state['rebirth']['used'],5)

    def test_10star_high_diploma_after_free_limit_does_not_use_low(self):
        pid=self.add(751001)
        self.state['rebirth']['used']=5
        plan=self.game.rebirth_plan(self.state,pid)
        self.assertEqual(plan['cost'],{REBIRTH_DIPLOMA_HIGH:5})
        self.assertFalse(plan['can_afford'])
        self.state['items'][REBIRTH_DIPLOMA_HIGH]=5
        self.state['items'][REBIRTH_DIPLOMA_LOW]=99
        self.dispatch(pid)
        self.assertEqual(self.state['items'][REBIRTH_DIPLOMA_HIGH],0)
        self.assertEqual(self.state['items'][REBIRTH_DIPLOMA_LOW],99)

    def test_16_to_25_uses_baseline_with_warning(self):
        for awake in range(6,16):
            pid=self.add(751001,awake)
            plan=self.game.rebirth_plan(self.state,pid)
            self.assertTrue(plan['limited_recipe'])
            self.assertIn('15★',plan['warning'])
            self.assertEqual(plan['stars'],10+awake)
            self.assertTrue(plan['returns'])
            self.state['partners'].pop()

    def test_universe_keeps_native_10star_identity_and_returns_equipment(self):
        pid=self.add(757001,3)
        plan=self.game.rebirth_plan(self.state,pid)
        self.assertEqual(plan['returns'],[{'table_id':757001,'count':1,'awake':0}])
        self.dispatch(pid)
        self.assertIn(757001,[g['table_id'] for g in self.state['partners']])
        self.assertNotIn(pid,[g['partner_id'] for g in self.state['partners']])

    def test_6star_uses_native_material_table_and_lower_diploma(self):
        pid=self.add(651001)
        plan=self.game.rebirth_plan(self.state,pid)
        self.assertIn({'table_id':51001,'count':2,'awake':0},plan['returns'])
        self.assertIn({'table_id':561001,'count':4,'awake':0},plan['returns'])
        self.state['rebirth']['used']=5
        self.assertEqual(self.game.rebirth_plan(self.state,pid)['cost'],{'47001':1})

    def test_low_star_5_or_below_can_reset(self):
        for tid in (41001,51001):
            pid=self.add(tid)
            plan=self.game.rebirth_plan(self.state,pid)
            self.assertEqual(plan['returns'],[{'table_id':tid,'count':1,'awake':0}])
            self.state['partners'].pop()

    def test_different_day_resets_free_allowance(self):
        pid=self.add(751001)
        self.state['rebirth']={'day':'2026-10-01','used':5}
        plan=self.game.rebirth_plan(self.state,pid)
        self.assertTrue(plan['is_free'])
        self.assertEqual(plan['cost'],{})
        self.assertEqual(plan['free_left'],5)

    def test_pending_exchange_and_locked_are_rejected(self):
        pid=self.add(751001,flags=[1])
        with self.assertRaisesRegex(GameError,'mở khóa'):
            self.game.rebirth_plan(self.state,pid)
        self.state['partners'][-1]['flags']=[]
        self.state['exchange']={'partner_id':pid}
        with self.assertRaisesRegex(GameError,'giao dịch'):
            self.game.rebirth_plan(self.state,pid)

    def test_duplicate_diploma_art_while_distinct_item_identity(self):
        items=json.loads(Path('web/assets/items-catalog.json').read_text())
        original,clone=items[REBIRTH_DIPLOMA_HIGH],items[REBIRTH_DIPLOMA_LOW]
        self.assertEqual(original['icon'],clone['icon'])
        self.assertNotEqual(original['id'],clone['id'])
        self.assertNotEqual(original['name'],clone['name'])
        self.assertEqual(clone['icon'],'icon_47')

    def test_outdated_next_partner_id_does_not_delete_returned_girls(self):
        pid=self.add(757003)
        self.state['next_partner_id']=pid
        plan=self.game.rebirth_plan(self.state,pid)
        self.dispatch(pid)
        expected=[g for g in self.state['partners'] if g['table_id']==757003]
        self.assertEqual(len(expected),1)
        self.assertNotEqual(expected[0]['partner_id'],pid)
        self.assertEqual(len(set(g['partner_id'] for g in self.state['partners'])),
                         len(self.state['partners']))

    def test_real_handle_persists_validated_rollback_without_neon(self):
        pid=self.add(757001)
        self.game._save_profile(self.state)
        self.game.db.commit()
        packets=self.game.handle('ROLLBACK_PARTNER',{'partner_id':pid})
        self.assertTrue(packets)
        saved=self.game._load()
        self.assertEqual(saved['rebirth']['used'],1)
        self.assertEqual(saved['last_rollback']['partner_id'],pid)
        self.assertNotIn(pid,[g['partner_id'] for g in saved['partners']])
        self.assertEqual(sum(g['table_id']==757001 for g in saved['partners']),1)

    def test_free_and_paid_shared_between_normal_and_cosmos(self):
        self.state['rebirth']['used']=4
        cosmos=self.add(757002)
        self.dispatch(cosmos)
        self.assertEqual(self.state['rebirth']['used'],5)
        standard=self.add(651001)
        self.assertEqual(self.game.rebirth_plan(self.state,standard)['cost'],{'47001':1})


if __name__=='__main__':
    unittest.main()
