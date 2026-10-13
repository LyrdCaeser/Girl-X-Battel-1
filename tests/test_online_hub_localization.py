"""Read-only safeguards for the real multiplayer UI and Vietnamese labels.

Checks only static frontend files. No API requests or database mutations.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OnlineHubVietnameseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub = (ROOT / "web" / "online-hub.js").read_text(encoding="utf-8")
        cls.locale = json.loads((ROOT / "localization" / "vi.json").read_text(encoding="utf-8"))

    def test_all_literal_multiplayer_labels_have_vietnamese_entries(self):
        labels = set(re.findall(r"\\bT\\(\\s*['\"]([^'\"]+)['\"]\\s*\\)", self.hub))
        self.assertGreater(len(labels), 75)
        missing = sorted(labels.difference(self.locale))
        self.assertFalse(missing, "Multiplayer labels missing translations: " + repr(missing))

    def test_online_titles_and_battle_progress_do_not_show_english(self):
        self.assertEqual(self.locale["Server"], "Máy Chủ")
        self.assertEqual(self.locale["GXB 3 Online"], "GXB 3 Trực Tuyến")
        self.assertEqual(self.locale["Server is simulating battle…"], "Máy chủ đang xử lý trận đấu…")
        self.assertNotIn("mô phỏng", self.locale["The server loads both saved teams and simulates the result. The client cannot submit a winner."])

    def test_api_roles_are_only_localized_for_display(self):
        self.assertIn("guildRoleLabel(g.role)", self.hub)
        self.assertIn("guildRoleLabel(m.role)", self.hub)
        self.assertIn("pvpModeLabel(m.mode)", self.hub)
        self.assertIn("matchStatusLabel(m.status)", self.hub)
        self.assertIn("get('/api/world-guild')", self.hub)
        self.assertIn("post('/api/pvp/match/battle'", self.hub)
        self.assertNotIn("if(timer)clearInterval(timer)", self.hub)


if __name__ == "__main__":
    unittest.main()
