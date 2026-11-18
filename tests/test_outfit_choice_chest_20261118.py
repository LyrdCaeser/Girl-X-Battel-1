"""Local-only checks: no Neon or production accounts touched."""
import unittest, tempfile
from pathlib import Path
from unittest.mock import patch
from gxb2 import bag_use, dress
from gxb2.engine import Engine, GameError

class OutfitChestTests(unittest.TestCase):
    def test_authoritative_option_images_and_vietnamese(self):
        options=bag_use.describe(4601003)
        self.assertTrue(options['usable'])
        self.assertEqual([x['id'] for x in options['choices']],
                         [3100296,3100302,3100308,3100314,3100320])
        self.assertEqual([x['amount'] for x in options['choices']],[1]*5)
        for option in options['choices']:
            self.assertIn('Tinh Tú',option['name'])
            self.assertNotIn('Vật phẩm #',option['name'])
            self.assertIn('· 2★',option['name'])
            self.assertTrue((bag_use.ROOT/'web'/option['image'].lstrip('/')).is_file())
            self.assertEqual(option['quality'],6)

    def test_grants_outfit_then_duplicate_shards_not_invisible_item(self):
        with tempfile.TemporaryDirectory() as td:
            engine=Engine(Path(td)/'isolated.sqlite3',developer=False)
            self.addCleanup(engine.close)
            with patch.object(engine,'snapshot',side_effect=engine._load):
                state=engine._load()
                state['items']['4601003']=3
                state['items']['3100296']=0
                engine._save_profile(state)
                engine.db.commit()
                first=engine.use_bag_item(4601003,3100296,1)
                self.assertEqual(first['rewards'],{'3100296':1})
                # The actual persisted Outfit collection is the authoritative check.
                stored=engine._load()
                self.assertEqual(dress.saved(stored)['owned']['101050'],2)
                self.assertEqual(stored['items'].get('3100296',0),0)
                second=engine.use_bag_item(4601003,3100296,1)
                self.assertEqual(second['state']['items']['4601003'],1)
                self.assertEqual(engine._load()['items'].get('3200295',0),50)
                self.assertEqual(engine._load()['items'].get('3100296',0),0)
                with self.assertRaises(GameError):
                    engine.use_bag_item(4601003,999999,1)
                self.assertEqual(engine._load()['items']['4601003'],1)
