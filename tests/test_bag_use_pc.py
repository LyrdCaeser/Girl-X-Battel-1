"""GXB3 Bag Use regression: isolated local player DB, no Neon or live account writes."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2.engine import Engine, GameError


class BagUseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.engine=Engine(Path(self.tmp.name)/'bag.sqlite3',developer=False)
        self.addCleanup(self.engine.close)
        state=self.engine._load()
        state['items']['133']=3
        state['items']['207']=2
        state['items']['4102003']=1
        state['items']['930187']=0
        state['items']['930188']=0
        state['items']['930194']=0
        state['items']['930195']=0
        self.engine._save_profile(state)
        self.engine.db.commit()
        # No production mailbox or world registration during snapshot().
        self.snap=patch.object(self.engine,'snapshot',side_effect=self.engine._load)
        self.snap.start()
        self.addCleanup(self.snap.stop)

    def test_original_table_is_the_only_source_for_all_available_chests(self):
        from gxb2 import bag_use
        src=bag_use._table('giftbox_optional')
        source_gifts=bag_use._table('gift')
        recipes=bag_use.recipes()
        choices={k:v for k,v in recipes.items() if v['kind']=='choice'}
        gifts={k:v for k,v in recipes.items() if v['kind']=='gift'}
        self.assertEqual(len(src['rows']),387)
        self.assertEqual(len(choices),383)
        self.assertGreaterEqual(len(gifts),65)
        self.assertEqual(len(gifts),71)
        self.assertEqual(len(recipes),454)
        self.assertEqual(choices['133']['choices'],{'930187':50,'930188':50})
        # Four legacy boxes have optional rows, but original item type=14
        # and gift IDs make them guaranteed multi-item sets, not choices.
        self.assertIn('4601013', gifts)
        self.assertNotIn('4601013', choices)
        self.assertNotIn('4706001', recipes)
        self.assertIn('135',gifts)
        self.assertNotIn('17',gifts)

    def test_options_include_other_publisher_defined_choice_chests(self):
        from gxb2 import bag_use
        academy=bag_use.describe(125)
        self.assertTrue(academy['usable'])
        self.assertEqual(len(academy['choices']),8)
        multi=bag_use.describe(4101001)
        self.assertTrue(multi['usable'])
        self.assertGreater(len(multi['choices']),20)
        self.assertFalse(bag_use.describe(17)['usable'])

    def test_fixed_gifts_and_random_original_dropbox(self):
        state=self.engine._load()
        state['items']['149']=1
        state['items']['192']=1
        self.engine._save_profile(state)
        self.engine.db.commit()
        got=self.engine.use_bag_item(149,None,1)
        self.assertEqual(got['rewards'],{'1166':1,'2166':1,'3166':1,'4166':1})
        self.assertEqual(got['state']['items']['149'],0)
        got=self.engine.use_bag_item(192,None,1)
        self.assertEqual(got['state']['items']['192'],0)
        self.assertTrue(got['rewards'])
        from gxb2 import bag_use
        pool=bag_use.recipes()['192']['pools']
        allowed={str(line[0]) for group in pool for line in group}
        self.assertTrue(set(got['rewards']).issubset(allowed))

    def test_girls_chest_gives_selected_shards_and_consumes_exactly_one(self):
        r=self.engine.use_bag_item(133,930188,1)
        self.assertEqual(r['state']['items']['133'],2)
        self.assertEqual(r['state']['items']['930188'],50)
        self.assertEqual(r['state']['items']['930187'],0)
        self.assertEqual(r['rewards'],{'930188':50})
        r=self.engine.use_bag_item(133,930187,2)
        self.assertEqual(r['state']['items']['133'],0)
        self.assertEqual(r['state']['items']['930187'],100)

    def test_other_original_choice_chests(self):
        r=self.engine.use_bag_item(207,930195,1)
        self.assertEqual(r['state']['items']['207'],1)
        self.assertEqual(r['state']['items']['930195'],50)
        r=self.engine.use_bag_item(4102003,930187,1)
        self.assertEqual(r['state']['items']['4102003'],0)
        self.assertEqual(r['state']['items']['930187'],50)

    def test_reject_forged_reward_and_unsupported_box_without_spending(self):
        for item,reward in ((133,930194),(207,930188),(133,9999),(17,930187)):
            with self.subTest(item=item,reward=reward),self.assertRaises(GameError):
                self.engine.use_bag_item(item,reward,1)
        self.assertEqual(self.engine._load()['items']['133'],3)
        self.assertEqual(self.engine._load()['items']['207'],2)

    def test_reject_overuse_invalid_types_and_rollback_failure(self):
        for qty in (0,-1,4,51,True,1.5,'1.5','invalid'):
            with self.subTest(qty=qty),self.assertRaises(GameError):
                self.engine.use_bag_item(133,930187,qty)
        with patch.object(self.engine,'_save_profile',side_effect=RuntimeError('force rollback')):
            with self.assertRaisesRegex(RuntimeError,'force rollback'):
                self.engine.use_bag_item(133,930188,1)
        self.assertEqual(self.engine._load()['items']['133'],3)
        self.assertEqual(self.engine._load()['items']['930188'],0)

    def test_reject_manual_choice_for_random_or_fixed_chests(self):
        state=self.engine._load()
        state['items']['149']=1
        state['items']['192']=1
        self.engine._save_profile(state)
        self.engine.db.commit()
        with self.assertRaises(ValueError):
            self.engine.use_bag_item(149,930187,1)
        with self.assertRaises(ValueError):
            self.engine.use_bag_item(192,930187,1)
        self.assertEqual(self.engine._load()['items']['149'],1)
        self.assertEqual(self.engine._load()['items']['192'],1)

    def test_shards_original_tab_and_four_column_mobile_geometry(self):
        root=Path(__file__).resolve().parents[1]
        app=(root/'web/app.js').read_text(encoding='utf-8')
        css=(root/'web/bag-actions.css').read_text(encoding='utf-8')
        from json import loads
        catalog=loads((root/'web/assets/items-catalog.json').read_text(encoding='utf-8'))
        shards=[i for i in catalog.values() if i['category']==3]
        self.assertEqual(len(shards),275)
        self.assertIn("[3,'Mảnh Nữ Thần']",app)
        self.assertIn("grid-template-columns:repeat(4,minmax(0,1fr))",css)
        self.assertIn("item.category===bagTab",app)

    def test_smithy_respects_all_original_ingredients_and_never_divides_zero(self):
        root=Path(__file__).resolve().parents[1]
        frontend=(root/'web/equipment.js').read_text(encoding='utf-8')
        self.assertIn("cost(info,r.need_formula",frontend)
        self.assertIn("Number(v)<=0",frontend)
        self.assertNotIn("const [[src,per],gold]",frontend)

    def test_market_original_amounts_are_not_adjusted_to_match_screenshots(self):
        from gxb2 import shops
        raw=shops.DATA
        def sample(group):
            return next(row for row in raw['dropbox'].values() if row['dropbox_id']==group)
        self.assertEqual(sample(31031)['item'],'9#20000000')
        self.assertEqual(sample(31031)['cost'],'2#3600')
        # Market is authoritative: item amount and currency must come from
        # the same original dropbox row (never an invented card price).
        for offer in shops.goods(7):
            row=raw['tables']['shop_black_new'][offer['index']-1]
            pool=sample(row['dropbox_id'])
            self.assertEqual(offer['item'],shops.pair(pool['item']))

    def test_native_client_use_button_and_real_pc_window(self):
        root=Path(__file__).resolve().parents[1]
        app=(root/'web/app.js').read_text(encoding='utf-8')
        html=(root/'web/index.html').read_text(encoding='utf-8')
        frame=(root/'web/frame.js').read_text(encoding='utf-8')
        windows=(root/'clients/windows/gxb3_launcher.py').read_text(encoding='utf-8')
        css=(root/'web/desktop-layout.css').read_text(encoding='utf-8')
        self.assertIn('/api/inventory/use',app)
        self.assertIn('id="bag-detail-use"',html)
        self.assertIn('bag-actions.css',html)
        self.assertIn('desktop-layout.css',html)
        self.assertIn('fullscreen=True',windows)
        self.assertIn('client=windows',windows)
        self.assertIn('forceDesktop',frame)
        self.assertIn('.gxb-desktop #app-frame .bag-grid',css)
        self.assertNotIn('.gxb-mobile',css)

if __name__=='__main__':
    unittest.main()
