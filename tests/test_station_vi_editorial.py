"""Editorial regressions for source-faithful Station Vietnamese descriptions.

This is not a declaration that machine-translated prose has been human-reviewed.
It checks curated high-risk game semantics and publisher IDs before release.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import polish_station_vi as station


class StationEditorialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = station.build()
        cls.girls = cls.doc["girls"]

    def profile(self, cid):
        return self.girls[str(cid)]["desc"]

    def skill(self, cid, sid):
        return self.girls[str(cid)]["skills"][str(sid)]

    def test_editorial_coverage_and_publisher_invariance(self):
        self.assertEqual(len([key for key in station.OVERRIDES if key.startswith("profile/")]), 104)
        self.assertGreaterEqual(len([key for key in station.OVERRIDES if key.startswith("skill/")]), 104)
        self.assertEqual(len(self.doc["review_warnings"]), 0, self.doc["review_warnings"][:5])
        self.assertFalse(self.doc["reviewed"])
        self.assertEqual(sum(bool(g["desc"]) for g in self.girls.values()), 105)
        self.assertEqual(sum(len(g["skills"]) for g in self.girls.values()), 417)

    def test_bleed_vs_lifesteal_and_freeze(self):
        gambler = self.skill(851002, 75100801)
        self.assertIn("Chảy Máu", gambler)
        self.assertIn("2 kẻ", gambler)
        self.assertIn("6 sao", gambler)
        self.assertIn("3 kẻ", gambler)
        self.assertIn("10 sao", gambler)
        self.assertIn("hồi HP", gambler)
        self.assertIn("Đóng Băng", self.skill(851006, 75100901))
        self.assertIn("Hóa Đá", self.skill(851008, 75101001))

    def test_ultimate_and_shields(self):
        self.assertIn("bỏ qua Giáp", self.skill(856006, 75600601))
        self.assertIn("4 kẻ", self.skill(856006, 75600601))
        self.assertIn("HP tối đa", self.skill(856006, 75600603))
        self.assertIn("một lần mỗi trận", self.skill(851001, 75100504))
        self.assertIn("30%", self.skill(855012, 75501104))
        self.assertIn("hiệp 5", self.skill(855012, 75501104))
        self.assertIn("12", self.skill(856012, 75601204))
        self.assertIn("Điểm Khiên", self.skill(856010, 75601004))

    def test_cosmic_special_rules(self):
        self.assertIn("100 Năng Lượng", self.skill(857001, 757001401))
        self.assertIn("3 cộng dồn", self.skill(857002, 757002401))
        self.assertIn("Bùng Nổ Tinh Tú", self.skill(857001, 757001401))
        self.assertIn("HP tối đa", self.profile(857002))
        self.assertIn("Chí Mạng", self.skill(857003, 757003201))

    def test_no_raw_publisher_markup_in_curated_output(self):
        for cid, row in self.girls.items():
            for label, value in [("profile", row["desc"]), *row["skills"].items()]:
                self.assertFalse(re.search(r"\[(?:c|/c|-|[0-9a-f]{6})\]", value, re.I),
                                 f"{cid}/{label}: raw markup")
                self.assertFalse(re.search(r"\b(?:Damage Dealer|House Ghost|Armor Break)\b", value, re.I),
                                 f"{cid}/{label}: untranslated combat term")


if __name__ == "__main__":
    unittest.main()
