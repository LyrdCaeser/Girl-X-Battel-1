"""Replay uses the actual LuaJIT report and only the two original PvP participants.

No Neon / production data or online connection is touched by these unit tests.
"""
import copy
import unittest
from gxb2.pvp_render import for_viewer


class PvPReplayOrientationTests(unittest.TestCase):
    def setUp(self):
        self.raw={
            'isWin':1,'total_round':2,'total_harm':77,
            'teamA':[{'pos':1,'table_id':41001,'level':12,'skin_id':0,'name':'A'}],
            'teamB':[{'pos':2,'table_id':41002,'level':15,'skin_id':123,'name':'B'}],
            'frames':[{'round':1,'pos':1,'skill_id':4100101,
                       'targets':[8], 'targets_2':[1],
                       'eps':[{'pos':1,'ep':40},{'pos':14,'ep':60}],
                       'buffs':[{'pos':8,'f_pos':1,'hp':40,'buffOn':2}]},
                      {'round':2,'pos':8,'skill_id':4100201,
                       'targets':[1], 'eps':[{'pos':13,'ep':55}],
                       'buffs':[{'pos':1,'f_pos':8,'hp':20,'buffOn':2}]}],
            'hp':[{'pos':1,'hp':20},{'pos':8,'hp':40}],
            'hurts':[{'pos':1,'hurt':20},{'pos':8,'hurt':60}],
        }

    def test_player_a_sees_own_side_on_left_and_winner_unchanged(self):
        value=for_viewer(self.raw,'UID-A','UID-A','UID-B',pet_a={'pet_id':10},pet_b={'pet_id':20})
        self.assertEqual(value['isWin'],1)
        self.assertEqual([u['pos'] for u in value['display_units']],[1,8])
        self.assertEqual(value['frames'][0]['pos'],1)
        self.assertEqual(value['petA']['pet_id'],10)

    def test_player_b_sees_own_team_on_left_without_flipping_winner_in_storage(self):
        original=copy.deepcopy(self.raw)
        value=for_viewer(self.raw,'UID-B','UID-A','UID-B',pet_a={'pet_id':10},pet_b={'pet_id':20})
        self.assertEqual(value['isWin'],0)
        self.assertEqual([u['pos'] for u in value['display_units']],[7,2])
        self.assertEqual(value['frames'][0]['pos'],7)
        self.assertEqual(value['frames'][0]['targets'],[2])
        self.assertEqual(value['frames'][0]['eps'],[{'pos':7,'ep':40},{'pos':13,'ep':60}])
        self.assertEqual(value['frames'][0]['buffs'][0]['pos'],2)
        self.assertEqual(value['frames'][0]['buffs'][0]['f_pos'],7)
        self.assertEqual(value['hp'],[{'pos':7,'hp':20},{'pos':2,'hp':40}])
        self.assertEqual(value['petA']['pet_id'],20)
        self.assertEqual(value['display_units'][0]['name'],'A')
        self.assertEqual(self.raw,original, 'PvP source report is immutable across views')

    def test_real_luajit_frames_are_replayable_for_both_players(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from gxb2.engine import Engine, TABLES
        from gxb2.battle import simulate, ONLINE_BATTLE_ID
        with TemporaryDirectory(prefix='gxb3-real-pvp-replay-') as td:
            engine=Engine(Path(td)/'replay-test.sqlite3')
            try:
                snap=engine.pvp_team_snapshot()
                try:
                    raw=simulate(snap['team'],snap['team'],battle_id=ONLINE_BATTLE_ID,
                                 seed=12004,battle_type=1)
                except RuntimeError as exc:
                    if 'cannot load incompatible bytecode' in str(exc):
                        self.skipTest('Original LuaJIT battle bytecode unavailable in this runner')
                    raise
                self.assertTrue(raw['frames'])
                for viewer in ('UID-A','UID-B'):
                    playback=for_viewer(raw,viewer,'UID-A','UID-B',names=TABLES['names'])
                    self.assertEqual(len(playback['frames']),len(raw['frames']))
                    self.assertEqual(playback['isWin'],raw['isWin'] if viewer=='UID-A' else 1-raw['isWin'])
                    self.assertGreaterEqual(len(playback['display_units']),2)
                    self.assertEqual(len({x['pos'] for x in playback['display_units']}),
                                     len(playback['display_units']))
                    self.assertTrue(all(x['name'] for x in playback['display_units']))
                    self.assertTrue(all(1<=x['pos']<=12 for x in playback['display_units']))
            finally:
                engine.close()

    def test_nonparticipant_is_rejected_even_if_it_knows_match_id(self):
        with self.assertRaises(PermissionError):
            for_viewer(self.raw,'UID-INTRUDER','UID-A','UID-B')
        with self.assertRaises(ValueError):
            for_viewer({},'UID-A','UID-A','UID-B')
        with self.assertRaises(ValueError):
            for_viewer(self.raw,'UID-A','UID-A','UID-A')


if __name__=='__main__':
    unittest.main()
