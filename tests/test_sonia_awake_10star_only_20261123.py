"""Real GXB3 awakening contract in a disposable local sqlite profile.
No live account, Neon, or player resources are accessed.
"""
import tempfile
import unittest
from pathlib import Path
from gxb2.engine import Engine, TABLES, GameError

SONIA=758001

class SoniaAwakeTenStarOnly(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='gxb3-sonia-awake-regression-')
        self.addCleanup(self.tmp.cleanup)
        self.engine=Engine(Path(self.tmp.name)/'profile.sqlite3')
        self.addCleanup(self.engine.close)

    @staticmethod
    def copy(pid,star):
        return {'partner_id':pid,'table_id':SONIA,'lv':1,'grade':0,
                'awake':star-10,'equips':[],'pos':0,'show_skin':1}

    def state(self,target,material):
        s=self.engine._load()
        s['partners']=[self.copy(100,target),self.copy(101,material)]
        s['formation']=[]
        s['next_partner_id']=102
        s['items']['10']=30000
        self.engine._save_profile(s)
        self.engine.db.commit()
        return s

    def test_11_to_12_valid_ten_star_duplicate_consumed_once(self):
        self.state(11,10)
        before=self.engine.snapshot()
        h=next(p for p in before['roster'] if p['partner_id']==100)
        self.assertEqual(h['next_awake']['material'],[SONIA])
        self.assertEqual(h['next_awake']['star'],12)
        self.engine.handle('AWAKE_PARTNER',{'partner_id':100,'material_ids':[101]})
        after=self.engine.snapshot()
        self.assertEqual(len(after['roster']),1)
        self.assertEqual(after['roster'][0]['partner_id'],100)
        self.assertEqual(after['roster'][0]['stars'],12)
        self.assertEqual(after['items']['10'],20000)
        with self.assertRaises(GameError):
            self.engine.handle('AWAKE_PARTNER',{'partner_id':100,'material_ids':[101]})
        self.assertEqual(self.engine.snapshot()['roster'][0]['stars'],12)

    def test_11_to_12_eleven_star_duplicate_is_rejected_without_loss(self):
        self.state(11,11)
        before=self.engine.snapshot()
        with self.assertRaisesRegex(GameError,'materiales'):
            self.engine.handle('AWAKE_PARTNER',{'partner_id':100,'material_ids':[101]})
        after=self.engine.snapshot()
        self.assertEqual(after['items']['10'],before['items']['10'])
        self.assertEqual([(p['partner_id'],p['stars']) for p in after['roster']],
                         [(p['partner_id'],p['stars']) for p in before['roster']])

    def test_all_11_to_15_stars_require_unawakened_sonia_copy(self):
        for source_star in (10,11,12,13,14):
            with self.subTest(star=source_star):
                s={'partner_id':100,'table_id':SONIA,'lv':1,'grade':0,
                   'awake':source_star-10,'equips':[],'pos':0,'show_skin':1}
                recipe=self.engine.awake_recipe(s)
                self.assertEqual(recipe['material'],[SONIA])
                self.assertEqual(recipe['star'],source_star+1)
        self.assertEqual(int(TABLES['partner']['758001']['max_star']),10)

if __name__=='__main__':unittest.main()
