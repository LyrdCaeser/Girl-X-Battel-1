"""Test dialogue migration without downloading the translation model or editing data."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import translate_vi_dialogue as tr


class VietnameseCorpusTests(unittest.TestCase):
    def test_existing_vietnamese_is_not_overwritten(self):
        self.assertFalse(tr.needs_translation("Đã đánh bại thủ lĩnh!"))
        self.assertTrue(tr.needs_translation("Defeat the Guild Boss!"))

    def test_markup_and_original_newlines_are_preserved(self):
        text = "Hello {1}\n[c][abc123]Attack[-]"
        pieces = tr.parts(text)
        self.assertIn("{1}", pieces)
        self.assertIn("\n", pieces)
        self.assertIn("[c]", pieces)
        self.assertIn("[abc123]", pieces)
        self.assertIn("[-]", pieces)

    def test_apply_never_touches_mechanics_or_character_names(self):
        original = {
            "data/story.json": {
                "lines": {"1": {"d": "Hello", "n": "Gambler", "x": 2, "bg": "gb"}},
                "list": [], "forts": [], "episodes": [], "text": {}
            },
            "data/partner_plot.json": {"lines": {}, "titles": {}},
            "web/assets/girl-details.json": {
                "41001": {"quote": "Hello", "stats": {"base_hp": 999},
                          "skills": [{"id": 4100101, "name": "Blood Strike"}]}
            },
        }
        samples = copy.deepcopy(original)
        rows, fragments = tr.gather(samples)
        self.assertEqual(fragments, ["Hello"])
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(tr, "ROOT", Path(directory)):
                for path in samples:
                    (Path(directory) / path).parent.mkdir(parents=True, exist_ok=True)
                tr.apply(samples, rows, {"Hello": "Xin chào"}, 0)
        self.assertEqual(samples["data/story.json"]["lines"]["1"]["n"], "Gambler")
        self.assertEqual(samples["data/story.json"]["lines"]["1"]["x"], 2)
        girl = samples["web/assets/girl-details.json"]["41001"]
        self.assertEqual(girl["quote"], "Xin chào")
        self.assertEqual(girl["stats"], original["web/assets/girl-details.json"]["41001"]["stats"])
        self.assertEqual(girl["skills"], original["web/assets/girl-details.json"]["41001"]["skills"])


if __name__ == "__main__":
    unittest.main()
