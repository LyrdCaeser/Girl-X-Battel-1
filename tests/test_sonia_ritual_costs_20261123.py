"""Sonia-only dual-resource contracts tested with temporary SQLite accounts.

Tests never access Neon, remote profile data, live mail or production player state.
"""
import copy
import tempfile
import unittest
from pathlib import Path

from gxb2.engine import Engine, TABLES, GameError
from gxb2 import chaos_summon, local_config

SONIA=758001
SOUL_GEM='417'
HONOR_BADGE='173'
LUNCH='10'
FIRST=[100,200,350,500,750]
HONORS=[4,6,8,10,12,15,18,21,25,30]
LUNCHES=[10000,10000,15000,15000,20000,25000,30000,35000,40000,50000,
         60000,70000,80000,90000,100000]

class SoniaRitualCurrencyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='gxb3-sonia-resource-qa-')
        self.addCleanup(self.temp.cleanup)
        self.engine=Engine(Path(self.temp.name)/'qa.sqlite3')
        self.addCleanup(self.engine.close)

    @staticmethod
    def girl(pid,table_id,star):
        row=TABLES['partner'][str(table_id)]
        return {'partner_id':pid,'table_id':table_id,'lv':1,'grade':0,
                'awake':star-int(row['max_star']),'equips':[],'pos':0,'show_skin':1}

    def seed(self,target,materials,soul=0,honor=0):
        state=self.engine._load()
        state['partners']=[self.girl(101,SONIA,target-1)]+[
            self.girl(102+i,table_id,stars) for i,(table_id,stars) in enumerate(materials)]
        state['formation']=[]
        state['next_partner_id']=800
        state['items'][LUNCH]=150000
        state['items'][SOUL_GEM]=soul
        state['items'][HONOR_BADGE]=honor
        self.engine._save_profile(state)
        self.engine.db.commit()
        return [x['partner_id'] for x in state['partners'][1:]]

    def perform(self,ids):
        self.engine.handle('AWAKE_PARTNER',{'partner_id':101,'material_ids':ids})

    def test_identifiers_are_real_existing_items_and_artwork(self):
        import json
        items=json.loads((Path(__file__).resolve().parents[1]/
                          'web/assets/items-catalog.json').read_text())
        for item_id,name in ((LUNCH,'Lunch Box'),(SOUL_GEM,'Soul Gem'),
                             (HONOR_BADGE,'Honor Badge')):
            self.assertEqual(items[item_id]['name'],name)
            self.assertTrue((Path(__file__).resolve().parents[1]/
                'web/assets/item-icons'/f"icon_{item_id}.png").is_file())

    def test_costs_for_every_stage_and_other_goddesses_unchanged(self):
        for target in range(11,26):
            with self.subTest(star=target):
                recipe=self.engine.awake_recipe(self.girl(1,SONIA,target-1))
                expected={LUNCH:LUNCHES[target-11]}
                expected[SOUL_GEM if target<=15 else HONOR_BADGE]=(
                    FIRST[target-11] if target<=15 else HONORS[target-16])
                self.assertEqual(recipe['cost'],expected)
                self.assertEqual(set(recipe['cost']),set(expected))
        # Another native 10★ heroine must not acquire Sonia's Badge costs.
        other=self.engine.awake_recipe(self.girl(99,755013,15))
        self.assertEqual(other['cost'],{LUNCH:25000})
        self.assertNotIn(SOUL_GEM,other['cost'])
        self.assertNotIn(HONOR_BADGE,other['cost'])

    def test_roster_preview_shows_same_two_costs_as_the_authoritative_recipe(self):
        for target in (11,12,15,16,20,25):
            with self.subTest(target=target):
                state=self.engine._load()
                state['partners']=[self.girl(101,SONIA,target-1)]
                state['formation']=[]
                self.engine._save_profile(state)
                self.engine.db.commit()
                roster=self.engine.snapshot()['roster']
                shown=next(g for g in roster if g['partner_id']==101)
                assert shown['next_awake']
                cost=shown['next_awake']['cost']
                raw=self.engine.awake_recipe(state['partners'][0])['cost']
                self.assertEqual(cost,{k:local_config.scale_cost(v) for k,v in raw.items()})
                self.assertEqual(len(cost),2)

    def test_11_to_15_consumes_both_items_once_and_preserves_badges(self):
        materials=[(SONIA,10)]
        ids=self.seed(11,materials,soul=1000,honor=200)
        self.perform(ids)
        state=self.engine._load()
        self.assertEqual(state['partners'][0]['awake'],1)
        self.assertEqual(state['items'][LUNCH],140000)
        self.assertEqual(state['items'][SOUL_GEM],900)
        self.assertEqual(state['items'][HONOR_BADGE],200)
        before=copy.deepcopy(state)
        with self.assertRaises(GameError):
            self.perform(ids)
        after=self.engine._load()
        self.assertEqual(before['items'],after['items'])
        self.assertEqual(before['partners'],after['partners'])

    def test_missing_soul_11_to_15_never_spends_meal_or_goddesses(self):
        ids=self.seed(12,[(SONIA,10),(757001,10)],soul=199,honor=200)
        before=copy.deepcopy(self.engine._load())
        with self.assertRaisesRegex(GameError,'Không đủ tài nguyên'):
            self.perform(ids)
        after=self.engine._load()
        self.assertEqual(after['items'],before['items'])
        self.assertEqual(after['partners'],before['partners'])

    def test_16_to_25_consumes_meals_badges_not_soul(self):
        # Actual 25★ 5 matching 10★ copies + 10 valid group-5, 8★ support
        # goddesses. Verifies the highly demanding original 16–25★ route.
        for target in (16,25):
            with self.subTest(target=target):
                copies=1 if target==16 else 5
                supports=1 if target==16 else 10
                mats=[(SONIA,10)]*copies+[(55014,8)]*supports
                ids=self.seed(target,mats,soul=1234,honor=100)
                before=copy.deepcopy(self.engine._load())
                self.perform(ids)
                after=self.engine._load()
                self.assertEqual(len(after['partners']),1)
                self.assertEqual(after['partners'][0]['awake'],target-10)
                self.assertEqual(after['items'][SOUL_GEM],1234)
                self.assertEqual(after['items'][HONOR_BADGE],
                                 100-HONORS[target-16])
                self.assertEqual(after['items'][LUNCH],
                                 150000-LUNCHES[target-11])

    def test_missing_honor_badges_rolls_back_entire_25_star_transaction(self):
        mats=[(SONIA,10)]*5+[(55014,8)]*10
        ids=self.seed(25,mats,soul=999999,honor=29)
        before=copy.deepcopy(self.engine._load())
        with self.assertRaisesRegex(GameError,'Không đủ tài nguyên'):
            self.perform(ids)
        after=self.engine._load()
        self.assertEqual(before['items'],after['items'])
        self.assertEqual(before['partners'],after['partners'])
        self.assertEqual(before['formation'],after['formation'])

if __name__=='__main__':
    unittest.main()
