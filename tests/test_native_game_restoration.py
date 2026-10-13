"""Regression guards for existing game windows; never replace them with new modals.

Read-only inspection of source and JSON. No player data, API or Neon writes.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NativeGameWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = (ROOT / "web/index.html").read_text(encoding="utf-8")
        cls.lobby = (ROOT / "web/lobby-dialogue.js").read_text(encoding="utf-8")
        cls.mail = (ROOT / "web/mail.js").read_text(encoding="utf-8")
        cls.home = (ROOT / "web/home-menus.js").read_text(encoding="utf-8")
        cls.payment = (ROOT / "web/payment.js").read_text(encoding="utf-8")

    def test_original_lobby_and_story_dialogue_remain(self):
        self.assertIn('class="home-stage"', self.index)
        self.assertNotIn("gxb3-lobby-speech", self.lobby)
        self.assertNotIn("createElement('button')", self.lobby)
        self.assertIn("translateQuote", self.lobby)
        story = (ROOT / "web/story.js").read_text(encoding="utf-8")
        self.assertIn("'sp-dialog'", story)
        self.assertIn("'sp-name'", story)

    def test_original_mail_interface_handles_live_rewards(self):
        self.assertIn('data-coming="Mail"', self.index)
        self.assertIn("HomeMenus.open('mail'", self.mail)
        self.assertNotIn("stopImmediatePropagation", self.mail)
        self.assertIn("function mail(parent)", self.home)
        self.assertIn("function serverMail(parent)", self.home)
        self.assertIn("api('/api/mail/claim'", self.home)
        self.assertIn("['friend','Thư Bạn Bè']", self.home)
        self.assertIn("['system','Thư Hệ Thống']", self.home)

    def test_vip_original_progress_and_topup_catalog_preserved(self):
        self.assertIn('id="profile-vip"', self.index)
        self.assertIn('id="vip-level"', self.index)
        self.assertIn('id="vip-perks"', self.index)
        self.assertIn('id="vip-packages-open"', self.index)
        self.assertNotIn('id="payment-open"', self.index)
        self.assertIn("api('/api/payment/packages')", self.home)
        self.assertIn("GxbPayment?.open(pack.id)", self.home)
        self.assertIn("api('/api/order/create'", self.payment)
        self.assertIn("zalo.me/", self.payment)
        self.assertNotIn("GXB3-000001", self.payment)

    def test_events_catalog_is_vietnamese_without_rewriting_gameplay(self):
        catalog = json.loads((ROOT / "data/events.json").read_text(encoding="utf-8"))
        self.assertGreater(len(catalog["activities"]), 300)
        remaining = [
            (row.get("id"), field, row[field])
            for row in catalog["activities"]
            for field in ("title", "desc")
            if isinstance(row.get(field), str)
            and re.search(r"[A-Za-z]", row[field])
            and not re.search(r"[À-ỹĐđ]", row[field])
        ]
        self.assertEqual(remaining, [])

    def test_partner_dialogue_words_change_without_removing_lines(self):
        plot = json.loads((ROOT / "data/partner_plot.json").read_text(encoding="utf-8"))
        self.assertGreater(len(plot["lines"]), 5000)
        self.assertEqual(plot["lines"]["63"]["d"], "Á!")
        self.assertEqual(plot["lines"]["94"]["d"], "Ái da!")
        self.assertEqual(plot["lines"]["183"]["d"], "(Sững sờ)...")
        self.assertEqual(plot["lines"]["3379"]["d"], "Tên")


if __name__ == "__main__":
    unittest.main()
