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
        s['partners']=[self.copy(100,target),self.copy(101,material),
                       {'partner_id':102,'table_id':757001,'lv':1,'grade':0,
                        'awake':0,'equips':[],'pos':0,'show_skin':1}]
        s['formation']=[]
        s['next_partner_id']=102
        s['items']['10']=30000
        s['items']['417']=10000
        self.engine._save_profile(s)
        self.engine.db.commit()
        return s

    def test_11_to_12_valid_ten_star_duplicate_consumed_once(self):
        self.state(11,10)
        before=self.engine.snapshot()
        h=next(p for p in before['roster'] if p['partner_id']==100)
        self.assertEqual(h['next_awake']['material'],[SONIA,109999])
        self.assertEqual(h['next_awake']['star'],12)
        self.engine.handle('AWAKE_PARTNER',{'partner_id':100,'material_ids':[101,102]})
        after=self.engine.snapshot()
        self.assertEqual(len(after['roster']),1)
        self.assertEqual(after['roster'][0]['partner_id'],100)
        self.assertEqual(after['roster'][0]['stars'],12)
        self.assertEqual(after['items']['10'],20000)
        with self.assertRaises(GameError):
            self.engine.handle('AWAKE_PARTNER',{'partner_id':100,'material_ids':[101,102]})
        self.assertEqual(self.engine.snapshot()['roster'][0]['stars'],12)

    def test_11_to_12_eleven_star_duplicate_is_rejected_without_loss(self):
        self.state(11,11)
        before=self.engine.snapshot()
        with self.assertRaisesRegex(GameError,'materiales'):
            self.engine.handle('AWAKE_PARTNER',{'partner_id':100,'material_ids':[101,102]})
        after=self.engine.snapshot()
        self.assertEqual(after['items']['10'],before['items']['10'])
        self.assertEqual([(p['partner_id'],p['stars']) for p in after['roster']],
                         [(p['partner_id'],p['stars']) for p in before['roster']])

    def test_11_to_15_requires_original_sonia_copies_and_new_sacrifices(self):
        expected={
            11:[SONIA],
            12:[SONIA,109999],
            13:[SONIA,109999,55014,53019,55012],
            14:[SONIA,653026,655023,7999],
            15:[SONIA,SONIA,SONIA,117999,753019],
        }
        for target,materials in expected.items():
            with self.subTest(star=target):
                recipe=self.engine.awake_recipe(self.copy(100,target-1))
                self.assertEqual(recipe['material'],materials)
                self.assertEqual(recipe['star'],target)
        self.assertEqual(int(TABLES['partner']['758001']['max_star']),10)

if __name__=='__main__':unittest.main()
