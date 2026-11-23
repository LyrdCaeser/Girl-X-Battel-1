"""Real Sonia 12★–15★ awakening, disposable SQLite only; never touch Neon."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from gxb2.engine import Engine, TABLES, GameError

SONIA = 758001
# Requirements are separate real goddess copies; a tuple is (ID, owned star).
RECIPES = {
    12: ([(SONIA,10),(757001,10)],10000),
    13: ([(SONIA,10),(757001,10),(55014,5),(53019,5),(55012,5)],15000),
    14: ([(SONIA,10),(653026,6),(655023,6),(757002,14)],15000),
    15: ([(SONIA,10),(SONIA,10),(SONIA,10),(757003,11),(753019,10)],20000),
}
FORMULAS={
    11:[758001],
    12:[758001,109999],
    13:[758001,109999,55014,53019,55012],
    14:[758001,653026,655023,7999],
    15:[758001,758001,758001,117999,753019],
}

class SoniaRitualTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(prefix='gxb3-sonia-ritual-')
        self.addCleanup(self.folder.cleanup)
        self.engine=Engine(Path(self.folder.name)/'qa.sqlite3')
        self.addCleanup(self.engine.close)

    def girl(self,pid,table_id,star,locked=False):
        row=TABLES['partner'][str(table_id)]
        base=int(row['max_star'])
        self.assertGreaterEqual(star,base)
        return {'partner_id':pid,'table_id':table_id,'lv':1,'grade':0,
                'awake':star-base,'equips':[],'pos':0,'show_skin':1,
                'flags':[True] if locked else []}

    def seed(self,target,materials):
        state=self.engine._load()
        host=self.girl(101,SONIA,target-1)
        extras=[self.girl(i+102,table,star) for i,(table,star) in enumerate(materials)]
        state['partners']=[host,*extras]
        state['formation']=[]
        state['next_partner_id']=500
        state['items']['10']=120000
        self.engine._save_profile(state)
        self.engine.db.commit()
        return [p['partner_id'] for p in extras]

    def act(self,ids):
        return self.engine.handle('AWAKE_PARTNER',{'partner_id':101,'material_ids':ids})

    def test_exclusive_sonia_formulas_server_and_non_sonia_unchanged(self):
        for star,required in FORMULAS.items():
            with self.subTest(star=star):
                recipe=self.engine.awake_recipe(self.girl(101,SONIA,star-1))
                self.assertEqual(recipe['material'],required)
                self.assertEqual(recipe['star'],star)
                self.assertEqual(recipe['group'],8)
        other=self.engine.awake_recipe(self.girl(102,757001,10))
        self.assertNotEqual(other['material'],FORMULAS[12])
        self.assertEqual(int(TABLES['partner']['758001']['max_star']),10)

    def test_every_stage_accepts_precise_recipe_and_debits_once(self):
        for target,(materials,cost) in RECIPES.items():
            with self.subTest(target=target):
                ids=self.seed(target,materials)
                self.act(list(reversed(ids)))  # unsorted client IDs are valid
                s=self.engine._load()
                self.assertEqual([(p['partner_id'],p['table_id']) for p in s['partners']],[(101,SONIA)])
                self.assertEqual(s['partners'][0]['awake'],target-10)
                self.assertEqual(s['items']['10'],120000-cost)
                self.assertEqual(s['next_partner_id'],500)
                before=copy.deepcopy(s)
                with self.assertRaises(GameError):
                    self.act(ids)
                self.assertEqual(self.engine._load()['items'],before['items'])
                self.assertEqual(self.engine._load()['partners'],before['partners'])

    def test_eleven_star_original_unchanged(self):
        ids=self.seed(11,[(SONIA,10)])
        self.act(ids)
        self.assertEqual(self.engine._load()['partners'][0]['awake'],1)

    def test_invalid_or_missing_materials_never_cost_gold_or_remove_girls(self):
        scenarios=[
            (12,[(SONIA,10)],None),  # Missing 10★ any
            (12,[(SONIA,11),(757001,10)],None), # 11★ Sonia invalid
            (12,[(SONIA,10),(55014,5)],None),  # any 10★ must truly be 10★
            (13,[(SONIA,10),(757001,10),(655023,6),(53019,5),(55012,5)],None),
            (14,[(SONIA,10),(653026,6),(655023,6),(753019,10)],None),
            (15,[(SONIA,10),(SONIA,10),(SONIA,10),(757001,10),(753019,10)],None),
            (15,[(SONIA,10),(SONIA,10),(SONIA,10),(757003,11),(653026,6)],None),
            (15,[(SONIA,10),(SONIA,10),(757003,11),(753019,10)],None),
        ]
        for star,materials,_ in scenarios:
            with self.subTest(target=star,materials=materials):
                ids=self.seed(star,materials)
                before=copy.deepcopy(self.engine._load())
                with self.assertRaises(GameError):
                    self.act(ids)
                after=self.engine._load()
                self.assertEqual(after['partners'],before['partners'])
                self.assertEqual(after['items'],before['items'])

    def test_locked_copy_and_duplicate_selection_rejected(self):
        ids=self.seed(12,RECIPES[12][0])
        saved=self.engine._load()
        saved['partners'][1]['flags']=[True]
        self.engine._save_profile(saved);self.engine.db.commit()
        with self.assertRaises(GameError):self.act(ids)
        self.assertEqual(self.engine._load()['items']['10'],120000)
        with self.assertRaises(GameError):self.act([ids[0],ids[0]])
        self.assertEqual(self.engine._load()['items']['10'],120000)

    def test_cosmos_11_mandatory_for_15_but_any_rank_for_14(self):
        for star in (10,11,13,25):
            with self.subTest(star=star):
                mats=[(SONIA,10),(653026,6),(655023,6),(757001,star)]
                ids=self.seed(14,mats)
                self.act(ids)
                self.assertEqual(self.engine._load()['partners'][0]['awake'],4)
        # 7999 is never an available material code for other factions.
        partner=self.girl(400,757001,10)
        with self.assertRaises(GameError):
            self.engine.match_materials({400:partner},[400],[7999],group=3)

if __name__=='__main__':unittest.main()
