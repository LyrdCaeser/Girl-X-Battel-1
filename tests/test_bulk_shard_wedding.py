"""Source-gated, non-production regression tests for publisher shards and Dates/Oath."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from gxb2.engine import Engine, GameError
from gxb2 import relations

ROOT=Path(__file__).resolve().parents[1]

class BulkShardAndWeddingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.engine=Engine(Path(self.tmp.name)/'shards.sqlite3',developer=False)
        self.addCleanup(self.engine.close)
        self.patch=patch.object(self.engine,'snapshot',side_effect=self.engine._load)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def seed(self, key, value):
        state=self.engine._load()
        state['items'][str(key)]=value
        self.engine._save_profile(state)
        self.engine.db.commit()

    def test_bulk_summon_uses_exact_publisher_recipe(self):
        # Apollis: recovered summon 10284 costs item 930235 x50 per draw.
        self.seed(930235,500)
        before=self.engine._load()
        n=len(before['partners'])
        self.engine.handle('SUMMON',{'summon_id':10284,'times':5})
        after=self.engine._load()
        self.assertEqual(after['items']['930235'],250)
        self.assertEqual(len(after['partners']),n+5)
        self.assertTrue(all(p['table_id']==55014 for p in after['partners'][n:]))

    def test_invalid_quantity_and_missing_shards_preserve_state(self):
        self.seed(930235,100)
        before=self.engine._load()
        for times in (0,-1,51,1.5,'bad'):
            with self.subTest(times=times),self.assertRaises((GameError,ValueError,TypeError)):
                self.engine.handle('SUMMON',{'summon_id':10284,'times':times})
        with self.assertRaises(GameError):
            self.engine.handle('SUMMON',{'summon_id':10284,'times':3})
        after=self.engine._load()
        self.assertEqual(after['items']['930235'],100)
        self.assertEqual(len(after['partners']),len(before['partners']))

    def test_existing_oath_still_requires_original_intimacy_and_ring(self):
        state=self.engine._load()
        partner=state['partners'][0]
        partner['love_point']=relations.BASE_MAX
        partner['is_vowed']=0
        state['items']['45']=1
        self.engine._save_profile(state)
        self.engine.db.commit()
        pid=partner['partner_id']
        self.engine.relations_action({'action':'vow','partner_id':pid})
        after=self.engine._load()
        vowed=next(p for p in after['partners'] if p['partner_id']==pid)
        self.assertEqual(vowed['is_vowed'],1)
        self.assertGreater(vowed['wedding_date'],0)
        self.assertEqual(after['items']['45'],0)
        with self.assertRaises(ValueError):
            self.engine.relations_action({'action':'vow','partner_id':pid})
        self.assertEqual(self.engine._load()['items']['45'],0)

    def test_shard_icons_reference_existing_publisher_portraits(self):
        app=(ROOT/'web/app.js').read_text(encoding='utf8')
        for tid in (757001,55014):
            self.assertTrue((ROOT/f'web/assets/original-ui/portraits/partner_avatar_{tid}.png').exists())
        self.assertIn("if(tid===757001||tid===55014)",app)
        self.assertIn("if(String(item?.id)==='930220')",app)
        self.assertIn("if(String(item?.id)==='930235')",app)

if __name__=='__main__':
    unittest.main()
