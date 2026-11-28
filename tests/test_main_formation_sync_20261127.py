import copy
import tempfile
import unittest
from pathlib import Path
from gxb2.engine import Engine, GameError
from gxb2 import arena3v3

class MainFormationSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.engine=Engine(Path(self.temp.name)/'profile.sqlite3')
        self.addCleanup(self.engine.close)

    def test_save_all_worlds_and_preserve_other_teams(self):
        for world in ('S1','S2','S3','S4','S5'):
            with self.subTest(world=world):
                state=self.engine._load()
                state['server_id']=world
                ids=[x['partner_id'] for x in state['partners']]
                self.assertGreaterEqual(len(ids),3)
                a,b,c=ids[:3]
                new=[{'partner_id':b,'pos':5}]
                rest2=[{'partner_id':a,'pos':3}]
                rest3=[{'partner_id':c,'pos':6}]
                state['arena3v3']={'teams':[[{'partner_id':a,'pos':1}], [{'partner_id':b,'pos':1},*rest2],rest3], 'custom':42}
                old_items=copy.deepcopy(state['items'])
                old_partners=copy.deepcopy(state['partners'])
                self.engine._save_profile(state);self.engine.db.commit()
                self.engine.handle('SET_HANG_TEAM',{'partners':new})
                after=self.engine._load()
                self.assertEqual(after['formation'],new)
                self.assertEqual(after['pvp_defense'],new)
                self.assertEqual(after['arena3v3']['teams'],[new,rest2,rest3])
                self.assertEqual(after['arena3v3']['custom'],42)
                self.assertEqual(after['items'],old_items)
                self.assertEqual(after['partners'],old_partners)
                self.assertEqual(self.engine.map_info(after)['hang_team'],new)
                for defense in (True,False):
                    snap=self.engine.pvp_team_snapshot(defense=defense)
                    self.assertEqual([(x['partner_id'],x['pos']) for x in snap['team']],[(b,5)])
                for mode in ('arena','cross'):
                    self.assertEqual(self.engine.pvp_public_profile(mode)['teams'][0][0]['pos'],5)
                self.assertEqual(self.engine.pvp_arena3v3_teams(),[new,rest2,rest3])
                self.assertEqual(self.engine.pvp_arena3v3_snapshot()['teams'][0][0]['partner_id'],b)
                before=copy.deepcopy(after)
                with self.assertRaises(GameError):
                    self.engine.handle('SET_HANG_TEAM',{'partners':[{'partner_id':999999,'pos':1}]})
                self.assertEqual(self.engine._load(),before)

    def test_new_team_partial_and_first_open_reward_once(self):
        state=self.engine._load()
        state.pop('arena3v3',None)
        self.engine._save_profile(state);self.engine.db.commit()
        first=state['partners'][0]['partner_id']
        team=[{'partner_id':first,'pos':2}]
        self.engine.handle('SET_HANG_TEAM',{'partners':team})
        after=self.engine._load()
        self.assertEqual(after['arena3v3']['teams'],[team,[],[]])
        self.assertEqual(after['items'],state['items'])
        with self.assertRaises(GameError):self.engine.pvp_arena3v3_snapshot()
        info=self.engine.ensure_pvp_arena3v3()
        self.assertTrue(info['needs_repair'])
        self.assertEqual(info['draft_teams'],[team,[],[]])
        expected=int(state['items'].get('34',0))+int(arena3v3.OPEN.get('34',arena3v3.OPEN.get(34,0)))
        self.assertEqual(info['tickets'],expected)
        self.assertEqual(self.engine.ensure_pvp_arena3v3()['tickets'],expected)
        self.engine.handle('SET_HANG_TEAM',{'partners':team})
        self.assertEqual(self.engine.ensure_pvp_arena3v3()['tickets'],expected)

if __name__=='__main__':unittest.main()
