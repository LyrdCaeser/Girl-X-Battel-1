"""Read-only editorial checks for Vietnamese GXB 3 story text.

Only dialogue fields and chapter titles should be edited; gameplay/event fields,
IDs, links and assets are deliberately left untouched.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StoryVietnameseEditorialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.story = json.loads((ROOT / "data" / "story.json").read_text(encoding="utf-8"))

    def test_story_data_keeps_original_gameplay_structure(self):
        data = self.story
        self.assertEqual(len(data["lines"]), 3369)
        self.assertEqual(len(data["list"]), 230)
        self.assertEqual(len(data["forts"]), 19)
        self.assertEqual(len(data["episodes"]), 3)
        self.assertEqual(data["lines"]["1"]["x"], 2)
        self.assertEqual(data["lines"]["2027"]["x"], -1)  # Original scene endpoint
        self.assertEqual(data["lines"]["1659"]["x"], 1660)
        self.assertNotIn("d", data["lines"]["1659"], "Non-dialogue scene controls must stay intact")

    def test_clearly_english_interjections_are_localized_in_context(self):
        lines = self.story["lines"]
        expected = {
            "966": "Gì cơ?",
            "945": "(Thở phào)...",
            "1418": "(Bóng dáng Hỗn Loạn—)",
            "1657": "(Thanh tẩy——)",
            "1663": "Tên",
            "1967": "TIỀN BỐI!!",
            "2027": "TẬP HỢP!!",
            "2223": "Ái da!!",
            "2420": "(Hít mạnh)...",
            "2470": "Tại saooo?!",
        }
        for line_id, translation in expected.items():
            with self.subTest(line=line_id):
                self.assertEqual(lines[line_id]["d"], translation)

    def test_chapter_titles_are_vietnamese_without_renaming_characters(self):
        chapters = self.story["list"]
        self.assertEqual(chapters[88]["name"], "Thế Bế Tắc")
        self.assertEqual(chapters[140]["name"], "Cuộc Truy Đuổi")
        self.assertEqual(chapters[187]["name"], "Lời Thề")
        self.assertEqual(chapters[66]["name"], "Nobunaga")


    def test_memories_screen_has_no_english_or_spanish_player_prompts(self):
        source = (ROOT / "web" / "story.js").read_text(encoding="utf-8")
        self.assertIn("Chìa Khóa Ký Ức", source)
        self.assertIn("Hoàn thành phần cốt truyện trước để mở khóa.", source)
        self.assertIn("Tự Động", source)
        self.assertIn("Nhật Ký", source)
        for forbidden in (
            "Pass Campaign ", "Unlock by completing", "Key of Memory",
            "o usa ", "tienes ", "'Memories'", "'Recall'", "'Auto'",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
