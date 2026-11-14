"""Original roster 4★→5★/5★→6★ and max-level transaction regression."""
import tempfile
import unittest
from pathlib import Path
from gxb2 import engine, goddess_gifts


class NativeAwakeningAndFastLevel(unittest.TestCase):
    def setUp(self):
        self.dir=tempfile.TemporaryDirectory(prefix='gxb3-awake-all-')
        self.addCleanup(self.dir.cleanup)
        self.game=engine.Engine(Path(self.dir.name)/'state.sqlite3')
        self.addCleanup(self.game.close)

    def _set_roster(self,tid,*,level=1,grade=0,items=None):
        self.game.db.execute('BEGIN IMMEDIATE')
        state=self.game._load()
        state['partners']=[{'partner_id':1234,'table_id':tid,'lv':level,'grade':grade,'awake':0,'equips':[], 'pos':0, 'show_skin':1}]
        state['next_partner_id']=1235
        if items:state['items'].update(items)
        self.game._save_profile(state);self.game.db.commit()
        return state

    def test_all_647_native_partner_rows_and_4_5_composition_index(self):
        p=engine.TABLES['partner']
        self.assertEqual(len(p),647)
        fours=[v for v in p.values() if int(v.get('max_star') or 0)==4 and v.get('show_in_guide')]
        self.assertEqual(len(fours),38)
        for row in fours:
            recipe=engine.COMPOSE_BY_SOURCE.get(int(row['id']))
            self.assertTrue(recipe)
            self.assertEqual(recipe['star'],5)
            self.assertEqual(recipe['kind'],'compose')
            self.assertEqual(recipe['source'],row['id'])
            self.assertEqual(len(recipe['material']),11)
        six=[v for v in p.values() if int(v.get('max_star') or 0)==6 and v.get('show_in_guide')]
        self.assertEqual(len(six),115)
        for row in six:
            material=str(row.get('material') or '').split('|')
            if len(material)==5 and str(material[0]) in p:
                source=int(material[0]); recipe=engine.COMPOSE_BY_SOURCE.get(source)
                self.assertTrue(recipe,(row['id'],source))
                self.assertEqual(recipe['target'],row['id'])
                self.assertEqual(recipe['material'],[int(x) for x in material])
        self.assertEqual(len(engine.COMPOSE_BY_SOURCE),153)

    def test_4star_and_5star_detail_snapshot_returns_original_recipe(self):
        for source,target_star in ((41001,5),(51017,6),(651024,7)):
            self._set_roster(source)
            snap=self.game.snapshot()
            hero=next(g for g in snap['roster'] if g['partner_id']==1234)
            self.assertEqual(hero['stars'],int(engine.TABLES['partner'][str(source)]['max_star']))
            self.assertIsNotNone(hero['next_awake'],(source,hero['stars']))
            self.assertEqual(hero['next_awake']['star'],target_star)
            self.assertEqual(hero['next_awake']['kind'],'compose' if target_star<=6 else 'awake')
        self._set_roster(541001)  # archived 5★ reissue, no original 6★ form
        self.assertIsNone(next(x for x in self.game.snapshot()['roster'] if x['partner_id']==1234)['next_awake'])

    def test_max_level_consumes_exact_original_resources_and_grade(self):
        self._set_roster(41001,items={'1':10**12,'9':10**12,'10':10**12})
        before=self.game.snapshot()
        previous=dict(before['items'])
        result=self.game.level_up_max(1234)
        after=result['state']
        girl=next(x for x in after['roster'] if x['partner_id']==1234)
        self.assertGreater(result['levels_gained'],0)
        self.assertEqual(girl['grade'],int(engine.TABLES['partner']['41001']['max_grade']))
        self.assertEqual(girl['lv'],girl['level_cap'])
        self.assertEqual(after['next_partner_id'],before['next_partner_id'])
        self.assertEqual(len(after['roster']),len(before['roster']))
        for k,n in result['cost'].items():
            self.assertEqual(previous.get(k,0)-after['items'].get(k,0),n)
        with self.assertRaises(engine.GameError):self.game.level_up_max(1234)

    def test_fast_level_partial_resources_never_creates_money_or_fakes_stars(self):
        before=self._set_roster(51017,items={'1':10**9,'9':10**7})
        output=self.game.level_up_max(1234)
        hero=next(x for x in output['state']['roster'] if x['partner_id']==1234)
        self.assertEqual(hero['stars'],5)
        self.assertEqual(hero['table_id'],51017)
        self.assertLessEqual(hero['lv'],hero['level_cap'])
        self.assertGreater(hero['lv'],1)
        for k,v in before['items'].items():
            self.assertGreaterEqual(v,int(output['state']['items'].get(k,0)))
        with self.assertRaises(engine.GameError):self.game.level_up_max(9999999)

    def test_real_protocol_four_star_to_five_star_composition(self):
        # Exact 11-material original Graduate recipe. No mock participant,
        # no rewards or synthetic formulas: genuine server handle & p.encode.
        recipe=engine.GRADUATE['541001']
        self.assertEqual(recipe['source'],41001)
        def material_tid(code):
            if code%1000!=999:return code
            group=(code//1000)%10;star=code//10000
            return next(int(k) for k,v in engine.TABLES['partner'].items()
                        if int(v['group'])==group and int(v['max_star'])==star)
        with self.game.lock:
            self.game.db.execute('BEGIN IMMEDIATE')
            state=self.game._load()
            values=[41001]+[material_tid(x) for x in recipe['material']]
            state['partners']=[{'partner_id':i+101,'table_id':tid,'lv':1,'grade':0,'awake':0,
                                'equips':[],'pos':0,'show_skin':1} for i,tid in enumerate(values)]
            state['formation']=[];state['next_partner_id']=1000
            self.game._save_profile(state);self.game.db.commit()
        ids=list(range(101,101+len(values)))
        packets=self.game.handle('COMPOSE_PARTNER',{'table_id':541001,'material_ids':ids})
        self.assertTrue(packets)
        after=self.game._load()
        self.assertEqual(len(after['partners']),1)
        self.assertEqual(after['partners'][0]['table_id'],541001)
        self.assertEqual(after['partners'][0]['partner_id'],101)
        self.assertEqual(after['next_partner_id'],1000)
        self.assertEqual(after['formation'],[])
        with self.assertRaises(engine.GameError):self.game.handle('COMPOSE_PARTNER',{'table_id':541001,'material_ids':ids})

    def test_real_protocol_apollis_five_star_to_six_star_compose(self):
        recipe=engine.ASCENSION['655023:6']
        self.assertEqual(recipe['source'],55014)
        with self.game.lock:
            self.game.db.execute('BEGIN IMMEDIATE')
            state=self.game._load()
            values=[55014]+[55014]+[55001]*4
            state['partners']=[{'partner_id':i+201,'table_id':tid,'lv':1,'grade':0,'awake':0,
                                'equips':[],'pos':0,'show_skin':1} for i,tid in enumerate(values)]
            state['formation']=[];state['next_partner_id']=1000
            self.game._save_profile(state);self.game.db.commit()
        ids=list(range(201,201+len(values)))
        packets=self.game.handle('COMPOSE_PARTNER',{'table_id':655023,'material_ids':ids})
        self.assertTrue(packets)
        after=self.game._load()
        self.assertEqual(len(after['partners']),1)
        self.assertEqual(after['partners'][0]['table_id'],655023)
        self.assertEqual(after['partners'][0]['partner_id'],201)

    def test_seven_factions_all_have_original_image_and_stars(self):
        catalog=goddess_gifts.catalog()
        self.assertEqual(len(catalog),446)
        self.assertEqual({g['group'] for g in catalog},set(range(1,8)))
        for girl in catalog:
            self.assertTrue(girl['image'].startswith('/assets/'))
            for star in girl['stars']:
                form,awake=goddess_gifts.resolve(girl['id'],star)
                self.assertIn(str(form),engine.TABLES['partner'])
                self.assertEqual(int(engine.TABLES['partner'][str(form)]['max_star'])+awake,star)


if __name__=='__main__':unittest.main()
