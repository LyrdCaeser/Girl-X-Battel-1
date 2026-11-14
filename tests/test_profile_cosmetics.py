import tempfile
import unittest
from pathlib import Path

from gxb2.engine import Engine, GameError


class ProfileCosmeticUnlockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.engine = Engine(Path(self.tmp.name) / "profile.sqlite3")

    def tearDown(self):
        self.engine.close()
        self.tmp.cleanup()

    def test_locked_collection_cosmetics_cannot_be_equipped(self):
        state = self.engine.snapshot()
        self.assertNotIn("head_1002", state["profile_unlocks"]["heads"])
        self.assertNotIn("frame_8001", state["profile_unlocks"]["frames"])
        with self.assertRaises(GameError):
            self.engine.update_profile({"avatar": "head_1002"})
        with self.assertRaises(GameError):
            self.engine.update_profile({"frame": "frame_8001"})

    def test_owned_collection_items_unlock_cosmetics(self):
        with self.engine.lock:
            state = self.engine._load()
            state["items"]["1002"] = 1
            state["items"]["8001"] = 1
            self.engine._save_profile(state)
            self.engine.db.commit()
        snap = self.engine.snapshot()
        self.assertIn("head_1002", snap["profile_unlocks"]["heads"])
        self.assertIn("frame_8001", snap["profile_unlocks"]["frames"])
        self.engine.update_profile({"avatar": "head_1002", "frame": "frame_8001"})
        snap = self.engine.snapshot()
        self.assertEqual(snap["profile"]["avatar"], "head_1002")
        self.assertEqual(snap["profile"]["frame"], "frame_8001")


if __name__ == "__main__":
    unittest.main()
