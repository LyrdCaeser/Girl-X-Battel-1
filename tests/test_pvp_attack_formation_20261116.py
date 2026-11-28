"""Authenticated PvP attacker chooses an owned six-slot team; no premature UI result."""
import tempfile
import unittest
from pathlib import Path
from gxb2.engine import Engine, GameError


class AttackFormationTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.game=Engine(Path(self.temp.name)/'player.sqlite3')
    def tearDown(self):
        self.game.close()
        self.temp.cleanup()

    def test_only_selected_owned_goddesses_and_slots_are_used(self):
        before=self.game.snapshot()
        roster=before['roster']
        self.assertGreaterEqual(len(roster),2)
        ids=[int(x['partner_id']) for x in roster[:2]]
        team=[{'partner_id':ids[0],'pos':1},{'partner_id':ids[1],'pos':5}]
        snap=self.game.pvp_team_snapshot(formation_override=team)
        self.assertEqual([(h['partner_id'],h['pos']) for h in snap['team']],[(ids[0],1),(ids[1],5)])
        self.assertEqual(self.game.snapshot()['formation'],before['formation'])

    def test_rejects_invalid_and_duplicate_attack_teams(self):
        before=self.game.snapshot()
        own=int(before['roster'][0]['partner_id'])
        bad=[
            [],
            [{'partner_id':own,'pos':0}],
            [{'partner_id':own,'pos':7}],
            [{'partner_id':999999999,'pos':1}],
            [{'partner_id':own,'pos':1},{'partner_id':own,'pos':2}],
            [{'partner_id':own,'pos':1},{'partner_id':own,'pos':1}],
            [{'partner_id':str(own),'pos':1}],
            [None],
        ]
        for group in bad:
            with self.subTest(team=group),self.assertRaises(GameError):
                self.game.pvp_team_snapshot(formation_override=group)
        with self.assertRaisesRegex(GameError,'phòng thủ'):
            self.game.pvp_team_snapshot(defense=True,formation_override=[{'partner_id':own,'pos':1}])

    def test_ui_has_no_result_before_battle_replay(self):
        js=(Path(__file__).resolve().parents[1]/'web/arena-online-native.js').read_text()
        segment=js.split('async function fightSingle(match)',1)[1].split('async function pay3v3(',1)[0]
        self.assertIn("panel='replay-loading'",segment)
        self.assertIn('await liveWatch',segment)
        self.assertLess(segment.index('await liveWatch'),segment.index("panel='result'"))
        self.assertIn("formation_override=data.get('formation')",(Path(__file__).resolve().parents[1]/'server.py').read_text())


if __name__=='__main__':
    unittest.main()
