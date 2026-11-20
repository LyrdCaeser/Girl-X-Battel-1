"""Regression guard: publisher Station descriptions must be translated by stable IDs."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "web/assets/station/station.json"
TARGET = ROOT / "web/assets/station/station-vi.json"


class StationVietnameseTests(unittest.TestCase):
    def test_original_publisher_tables_have_expected_counts(self):
        base = json.loads(SOURCE.read_text(encoding="utf-8"))["girls"]
        descriptions = {cid for cid, girl in base.items() if girl.get("desc", "").strip()}
        skills = {(cid, str(x["id"])) for cid, girl in base.items()
                  for x in girl.get("skills", []) if x.get("desc", "").strip()}
        self.assertEqual(len(descriptions), 105)
        self.assertEqual(len(skills), 417)

    def test_completed_overlay_matches_every_original_record(self):
        if not TARGET.exists():
            self.skipTest("Machine-translation GitHub Actions job has not produced station-vi.json yet")
        base = json.loads(SOURCE.read_text(encoding="utf-8"))["girls"]
        doc = json.loads(TARGET.read_text(encoding="utf-8"))
        self.assertEqual(doc["source_sha256"], hashlib.sha256(SOURCE.read_bytes()).hexdigest())
        self.assertEqual(doc.get("reviewed"), False)  # Flag machine translation accurately.
        got = doc["girls"]
        pcount = scount = 0
        for cid, girl in base.items():
            record = got.get(cid, {})
            if girl.get("desc", "").strip():
                translated = record.get("desc")
                self.assertIsInstance(translated, str, f"Missing strategy {cid}")
                self.assertTrue(translated.strip() and translated != girl["desc"], cid)
                pcount += 1
            for skill in girl.get("skills", []):
                if skill.get("desc", "").strip():
                    translated = record.get("skills", {}).get(str(skill["id"]))
                    self.assertIsInstance(translated, str, f"Missing skill {cid}/{skill['id']}")
                    self.assertTrue(translated.strip() and translated != skill["desc"], str(skill["id"]))
                    scount += 1
        self.assertEqual((pcount, scount), (105, 417))


if __name__ == "__main__":
    unittest.main()
