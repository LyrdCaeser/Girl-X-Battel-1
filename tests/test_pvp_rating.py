import tempfile
import unittest
from pathlib import Path

from gxb2 import live_service


class PvpRatingTests(unittest.TestCase):
    def setUp(self):
        self.old = live_service.DB_PATH
        self.tmp = tempfile.TemporaryDirectory()
        live_service.DB_PATH = Path(self.tmp.name) / "live.sqlite3"

    def tearDown(self):
        live_service.DB_PATH = self.old
        self.tmp.cleanup()

    def test_authoritative_result_updates_rating(self):
        live_service.register_player("P100", "S1", "Alpha")
        live_service.register_player("P200", "S1", "Beta")
        live_service.enqueue_pvp("P100", "S1", "Alpha", "arena", 1200)
        matched = live_service.enqueue_pvp("P200", "S1", "Beta", "arena", 1100)
        match = matched["match"]
        result = live_service.finish_authoritative_pvp(
            match["id"], "P100",
            {"uid":"P100","server_id":"S1","name":"Alpha","power":1200,"team":[]},
            {"uid":"P200","server_id":"S1","name":"Beta","power":1100,"team":[]},
            {"isWin":1,"frames":[],"total_round":3},
        )
        self.assertEqual(result["status"], "finished")
        self.assertEqual(result["winner_uid"], "P100")
        winner = live_service.pvp_rating("P100", "S1", "arena")
        loser = live_service.pvp_rating("P200", "S1", "arena")
        self.assertGreater(winner["rating"], 1000)
        self.assertLess(loser["rating"], 1000)
        self.assertEqual(winner["wins"], 1)
        self.assertEqual(loser["losses"], 1)


if __name__ == "__main__":
    unittest.main()
