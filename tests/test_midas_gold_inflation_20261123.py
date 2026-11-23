"""Native Midas economy: 400 original rows, capped VIP gain,
real diamond costs and daily limits; all state is isolated.
"""
import json
import tempfile
import unittest
from pathlib import Path
from gxb2 import midas
from gxb2.engine import Engine

ROOT = Path(__file__).resolve().parents[1]
NOW = 1795438800

class MidasGoldInflationRegression(unittest.TestCase):
    def state(self, vip=0):
        return {'vip':vip,'items':{'1':0,'2':100000},
                'midas':{'day':'','free':0,'buys':0}}

    def test_native_400_levels_are_exact_original_source_not_gold_new(self):
        decoded=json.loads((ROOT/'data/recovered/tables/midas.json').read_text())['rows']
        self.assertEqual(len(decoded),400)
        self.assertEqual(set(midas.DATA['gold_native']),set(decoded))
        for level,row in decoded.items():
            self.assertEqual(midas.DATA['gold_native'][level],row[1])
            self.assertEqual(midas.DATA['gold'][level],row[2])
            self.assertEqual(int(row[2].split('#')[1]),
                             3*int(row[1].split('#')[1]))
        self.assertEqual(midas.base(self.state(),400),420000)
        self.assertEqual(midas.base(self.state(),1),10000)
        self.assertEqual(midas.base(self.state(),999),midas.base(self.state(),400))

    def test_vip_extra_is_progressive_but_not_fivefold(self):
        free=[midas.base(self.state(v),400) for v in range(17)]
        self.assertEqual(free[0],420000)
        self.assertEqual(free[15],756000)
        self.assertTrue(all(a<=b for a,b in zip(free,free[1:])))
        self.assertLessEqual(max(free),756000)

    def test_free_only_once_and_rollback_is_untouched(self):
        state=self.state()
        first=midas.snapshot(state,400,NOW)
        self.assertTrue(first['free_ready'])
        gold=midas.action(state,{'action':'free'},400,NOW)['got']['1']
        self.assertEqual(gold,420000)
        self.assertEqual(state['items']['1'],420000)
        try:
            midas.action(state,{'action':'free'},400,NOW)
        except ValueError:
            pass
        else:
            self.fail('Second free Midas grant must not be allowed')
        self.assertEqual(state['items']['1'],420000)

    def test_vip15_16_paid_purchases_preview_cost_and_total(self):
        state=self.state(15)
        free=midas.action(state,{'action':'free'},400,NOW)['got']['1']
        self.assertEqual(free,756000)
        purchases=midas.vip(state)['times']
        self.assertEqual(purchases,16)
        totals=0;diamond_spent=0
        for i in range(purchases):
            before=midas.snapshot(state,400,NOW)
            self.assertEqual(before['buys'],i)
            self.assertEqual(before['times'],purchases)
            self.assertGreater(before['next_gold'],0)
            self.assertEqual(before['next_cost'],{'2':int(midas.DATA['buy'][i]['cost'].split('#')[1])})
            diamonds=state['items']['2']
            got=midas.action(state,{'action':'buy'},400,NOW)['got']['1']
            self.assertEqual(got,before['next_gold'])
            self.assertEqual(state['items']['2'],diamonds-before['next_cost']['2'])
            diamond_spent+=before['next_cost']['2'];totals+=got
        self.assertEqual(diamond_spent,21150)
        self.assertEqual(totals,22154580)
        self.assertEqual(state['items']['1'],22910580)
        self.assertLess(state['items']['1'],25000000)
        after=midas.snapshot(state,400,NOW)
        self.assertIsNone(after['next_cost'])
        self.assertEqual(after['next_gold'],0)
        owned_before=dict(state['items'])
        with self.assertRaises(ValueError):midas.action(state,{'action':'buy'},400,NOW)
        self.assertEqual(state['items'],owned_before)

    def test_no_vip_low_level_reward_does_not_inflate_new_accounts(self):
        state=self.state(0)
        midas.action(state,{'action':'free'},1,NOW)
        for i in range(5):
            info=midas.snapshot(state,1,NOW)
            self.assertEqual(info['next_cost']['2'],[50,100,200,400,600][i])
            midas.action(state,{'action':'buy'},1,NOW)
        self.assertLess(state['items']['1'],100000)
        self.assertEqual(state['items']['2'],100000-1350)

    def test_new_day_resets_free_and_buy_count(self):
        state=self.state()
        midas.action(state,{'action':'free'},400,NOW)
        midas.action(state,{'action':'buy'},400,NOW)
        later=NOW+2*86400
        info=midas.snapshot(state,400,later)
        self.assertTrue(info['free_ready'])
        self.assertEqual(info['buys'],0)
        self.assertEqual(info['next_cost'],{'2':50})
        midas.action(state,{'action':'free'},400,later)
        self.assertEqual(state['midas']['buys'],0)
        self.assertEqual(state['items']['1'],840000+441000)

    def test_engine_real_midas_endpoint_on_isolated_profile(self):
        with tempfile.TemporaryDirectory(prefix='gxb3-midas-capped-engine-') as d:
            engine=Engine(Path(d)/'sandbox.sqlite3')
            try:
                old=engine.snapshot()
                # No live profile is ever accessed; only the stand-alone SQLite.
                result=engine.midas_action({'action':'free'})
                self.assertEqual(result['got']['1'],midas.base({'vip':0},old['level']))
                second=engine.snapshot()
                self.assertEqual(second['items']['1']-old['items']['1'],result['got']['1'])
            finally:
                engine.close()

    def test_actual_assistant_one_tap_16_purchases_no_second_grant(self):
        # Reproduce the user's two-line summary (Free + Bought) on a fresh
        # isolated account with Lv.400, VIP15 and 30K Diamonds.
        from gxb2 import vip
        from gxb2.engine import TABLES
        with tempfile.TemporaryDirectory(prefix='gxb3-midas-assistant-repro-') as d:
            engine=Engine(Path(d)/'profile.sqlite3')
            try:
                state=engine._load()
                state['vip_paid_exp']=int(vip.LEVELS[15]['need_exp'])
                state['items']['3']=int(TABLES['exp_player']['400']['all_exp'])
                state['items']['2']=30000
                state['items']['1']=0
                engine._save_profile(state)
                engine.db.commit()
                first=engine.assistant_run({'steps':['midas'],'opts':{'midas_buy':20}})
                rows=first['report']
                self.assertEqual([r['ok'] for r in rows],[True,True])
                self.assertEqual(rows[0]['got']['1'],756000)
                self.assertEqual(rows[1]['got']['1'],22154580)
                actual=first['state']
                self.assertEqual(actual['items']['1'],22910580)
                self.assertEqual(actual['items']['2'],30000-21150)
                self.assertEqual(actual['midas_info']['buys'],16)
                second=engine.assistant_run({'steps':['midas'],'opts':{'midas_buy':20}})
                self.assertTrue(all(not r['ok'] for r in second['report']))
                self.assertEqual(second['state']['items']['1'],actual['items']['1'])
                self.assertEqual(second['state']['items']['2'],actual['items']['2'])
            finally:
                engine.close()

if __name__=='__main__':
    unittest.main()
