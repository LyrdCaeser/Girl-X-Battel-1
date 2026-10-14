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
