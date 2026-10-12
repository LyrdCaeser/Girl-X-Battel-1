import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2.engine import Engine


class ReleaseCoreFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.engine = Engine(Path(self.tmp.name) / "profile.sqlite3")

    def tearDown(self):
        self.engine.close()
        self.tmp.cleanup()

    def test_regular_summon_persists_and_returns_partner_result(self):
        before = self.engine.snapshot()
        before_count = len(before["partners"])
        packets = self.engine.handle("SUMMON", {"summon_id": 1, "times": 1})
        self.assertGreaterEqual(len(packets), 1)
        result = packets[0][2]["summon_result"]
        self.assertEqual(len(result["partners"]), 1)
        after = self.engine.snapshot()
        self.assertEqual(len(after["partners"]), before_count + 1)
        self.assertEqual(after["partners"][-1]["partner_id"], result["partners"][0]["partner_id"])

    def test_first_campaign_fight_progresses_even_without_visual_runtime(self):
        state = self.engine._load()
        formation = list(state["formation"])
        fake_report = {
            "isWin": 1,
            "frames": [],
            "hurts": [],
            "hp": [],
            "teamA": [],
            "teamB": [],
            "groupBuffA": [],
            "groupBuffB": [],
            "total_round": 1,
        }
        with patch.object(self.engine, "_simulate", return_value=fake_report):
            packets, report = self.engine._dispatch(
                "MAP_FIGHT",
                {"map_type": 1, "stage_id": 1, "partners": formation},
                state,
            )
        self.assertEqual(report["isWin"], 1)
        self.assertIn(1, state["cleared"])
        self.assertEqual(state["max_stage"], 1)
        self.assertTrue(packets)


if __name__ == "__main__":
    unittest.main()
