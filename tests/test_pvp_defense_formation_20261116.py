import tempfile
import unittest
from pathlib import Path

from gxb2.engine import Engine, GameError


class PvPDefenseFormationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="gxb3-pvp-defense-")
        self.engine = Engine(Path(self.tmp.name) / "profile.sqlite3")

    def tearDown(self):
        self.engine.close()
        self.tmp.cleanup()

    def test_defense_is_saved_separately_and_used_only_for_defending(self):
        before = self.engine._load()
        attack = list(before["formation"])
        pid = int(before["partners"][-1]["partner_id"])
        saved = self.engine.save_pvp_defense_formation(
            [{"partner_id": pid, "pos": 6}]
        )
        self.assertEqual(saved["formation"], [{"partner_id": pid, "pos": 6}])
        after = self.engine._load()
        self.assertEqual(after["formation"], attack)
        self.assertEqual(after["pvp_defense"], [{"partner_id": pid, "pos": 6}])
        self.assertEqual(
            [x["pos"] for x in self.engine.pvp_team_snapshot(defense=True)["team"]],
            [6],
        )
        self.assertEqual(
            [x["pos"] for x in self.engine.pvp_team_snapshot()["team"]],
            [x["pos"] for x in attack],
        )

    def test_defense_rejects_unowned_or_duplicate_slots(self):
        with self.assertRaises(GameError):
            self.engine.save_pvp_defense_formation(
                [{"partner_id": 999999, "pos": 1}]
            )
        pid = int(self.engine._load()["partners"][0]["partner_id"])
        with self.assertRaises(GameError):
            self.engine.save_pvp_defense_formation(
                [{"partner_id": pid, "pos": 1}, {"partner_id": pid, "pos": 2}]
            )

    def test_original_six_slot_editor_and_http_route_are_present(self):
        root = Path(__file__).resolve().parents[1]
        ui = (root / "web" / "arena-online-native.js").read_text()
        server = (root / "server.py").read_text()
        self.assertIn("Hàng Trước',[1,2]", ui)
        self.assertIn("Hàng Sau',[3,4,5,6]", ui)
        self.assertIn("Lưu Đội Hình Phòng Thủ", ui)
        self.assertIn("nativeCardStars(hero,'ar-defense-candidate-stars')", ui)
        self.assertIn("nativeCardStars(hero,'ar-defense-slot-native-stars')", ui)
        css = (root / "web" / "arena3v3.css").read_text()
        self.assertIn("grid-template-columns:repeat(4,minmax(0,1fr))", css)
        self.assertIn("object-fit:contain!important", css)
        self.assertIn("post('/api/pvp/defense'", ui)
        self.assertIn("path == '/api/pvp/defense'", server)
        self.assertIn("pvp_team_snapshot(defense=True)", server)


if __name__ == "__main__":
    unittest.main()
