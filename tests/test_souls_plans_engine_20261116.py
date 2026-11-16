"""API-facing soul engine persists Anima plans, remains in user's own profile."""
import tempfile
import unittest
from pathlib import Path
from gxb2 import souls
from gxb2.engine import Engine, GameError

class AnimaEnginePlans(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.game=Engine(Path(self.temp.name)/'game.sqlite3')
        st=self.game._load()
        self.pid=st['partners'][0]['partner_id']
        p=st['partners'][0]
        p['lv']=250
        self.sid=int(souls.new_soul(st,int(sorted(souls.E1)[0])))
        p['souls']=[self.sid,0,0,0,0]
        st['souls']['items'][str(self.sid)]['owner']=self.pid
        souls.sync(st,p)
        self.game._save_profile(st)
        self.game.db.commit()
    def tearDown(self):
        self.game.close()
        self.temp.cleanup()
    def action(self,name,plan=1):
        return self.game.souls_action({'action':name,'partner_id':self.pid,'plan':plan})
    def test_real_engine_transaction_and_snapshot_are_consistent(self):
        baseline=self.game.snapshot()
        self.action('plan_save')
        after=self.game.snapshot()
        self.assertEqual(after['souls_info']['plans'][str(self.pid)]['1'],
                         [self.sid,0,0,0,0])
        self.assertEqual(after['items'],baseline['items'])
        self.game.souls_action({'action':'unequip','partner_id':self.pid})
        self.action('plan_apply')
        restored=self.game.snapshot()
        self.assertEqual(next(x['souls'] for x in restored['roster'] if x['partner_id']==self.pid),
                         [self.sid,0,0,0,0])
        self.assertEqual(restored['souls_info']['items'][str(self.sid)]['owner'],self.pid)
        self.assertEqual(restored['items'],baseline['items'])
        self.action('plan_delete')
        self.assertFalse(self.game.snapshot()['souls_info']['plans'].get(str(self.pid)))
    def test_rejects_invalid_plan_and_keeps_snapshot(self):
        before=self.game.snapshot()
        with self.assertRaises(GameError):
            self.action('plan_apply')
        self.assertEqual(self.game.snapshot()['souls_info']['items'],before['souls_info']['items'])
        self.assertEqual(self.game.snapshot()['items'],before['items'])
if __name__=='__main__':unittest.main()
