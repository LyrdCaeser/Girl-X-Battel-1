"""Regression for 19:46 production: malformed saved 3v3 teams broke status JSON."""
import copy
import tempfile
import unittest
from pathlib import Path
from gxb2.engine import Engine, GameError

ROOT=Path(__file__).resolve().parents[1]


class Arena3v3InvalidSavedFormation(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.engine=Engine(Path(self.tmp.name)/'profile.sqlite3')
        self.engine.ensure_pvp_arena3v3()
    def tearDown(self):
        self.engine.close()
        self.tmp.cleanup()

    def corrupt(self, saved):
        state=self.engine._load()
        state['arena3v3']['teams']=saved
        self.engine._save_profile(state)
        self.engine.db.commit()
        return copy.deepcopy(self.engine._load())

    def test_invalid_owned_team_does_not_crash_ladder_or_modify_neon_like_profile(self):
        roster=self.engine._load()['partners']
        ids=[int(v['partner_id']) for v in roster[:3]]
        self.assertEqual(len(ids),3)
        corrupted=[
            [{'partner_id':ids[0],'pos':1},{'partner_id':ids[1],'pos':1}],
            [{'partner_id':999999999,'pos':3}],
            [{'partner_id':ids[2],'pos':4}]
        ]
        before=self.corrupt(corrupted)
        result=self.engine.ensure_pvp_arena3v3()
        self.assertTrue(result['needs_repair'])
        self.assertEqual(result['teams'],[])
        self.assertEqual(result['draft_teams'],[
            [{'partner_id':ids[0],'pos':1}],
            [],
            [{'partner_id':ids[2],'pos':4}]
        ])
        self.assertEqual(result['tickets'],before['items'].get('34',0))
        self.assertIn('Đội hình',result['warning'])
        self.assertEqual(self.engine._load(),before)
        with self.assertRaises(GameError):
            self.engine.pvp_arena3v3_snapshot()
        # A real player must explicitly save three valid owned teams to fight.
        repaired=[[{'partner_id':ids[0],'pos':1}],
                  [{'partner_id':ids[1],'pos':2}],
                  [{'partner_id':ids[2],'pos':3}]]
        self.engine.save_pvp_arena3v3_teams(repaired)
        result=self.engine.ensure_pvp_arena3v3()
        self.assertFalse(result['needs_repair'])
        self.assertEqual(result['teams'],repaired)
        self.assertEqual(self.engine._load()['items'],before['items'])

    def test_malformed_history_is_non_destructive_and_never_grants_ticket_twice(self):
        for malformed in ([[],[],[]], [{'partner_id':'n/a'}], 'not a list',
                          [[{'partner_id':-1,'pos':9}],[],[]],
                          [[None],[],[]]):
            before=self.corrupt(malformed)
            result=self.engine.ensure_pvp_arena3v3()
            if malformed == [[],[],[]]:
                self.assertTrue(result['needs_repair'])
            else:
                self.assertTrue(result['needs_repair'])
            self.assertEqual(len(result['draft_teams']),3)
            self.assertFalse(result['teams'])
            self.assertEqual(self.engine._load(),before)
        self.assertEqual(self.engine.ensure_pvp_arena3v3()['tickets'],
                         self.engine._load()['items'].get('34',0))

    def test_browser_recovers_partial_draft_with_warning_and_no_zero_time_before_load(self):
        ui=(ROOT/'web/arena-online-native.js').read_text()
        self.assertIn('data?.arena3v3?.draft_teams',ui)
        self.assertIn("data.arena3v3.warning",ui)
        self.assertIn('Đang tải mùa Đấu Trường',ui)
        self.assertIn("panel=mode==='arena3v3'?'teams':'defense'",ui)
        self.assertIn("post('/api/pvp/arena3v3/teams',{teams})",ui)
        server=(ROOT/'server.py').read_text()
        self.assertIn("return self.send(503, {",server)
        self.assertIn("return self.send(409, {'error': str(exc)})",server)


if __name__=='__main__':
    unittest.main()
