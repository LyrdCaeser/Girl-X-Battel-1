"""Regression guards for requested GXB 3 native UI and Vietnamese game content.

Static/read-only; no account, production API or Neon mutation.
"""
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/"web"


class RequestedRestorationTests(unittest.TestCase):
    def test_native_gold_gems_controls_and_evolution(self):
        html=(WEB/"index.html").read_text(encoding="utf-8")
        app=(WEB/"app.js").read_text(encoding="utf-8")
        self.assertIn('id="home-add-gold"',html)
        self.assertIn('id="home-add-gems"',html)
        self.assertIn('id="detail-grade-up"',html)
        self.assertIn("action('PARTNER_LEVUP'",app)
        self.assertIn("action('PARTNER_GRADEUP'",app)
        self.assertIn("hero.grade_cost",app)
        self.assertIn("next_awake", (ROOT/"gxb2/engine.py").read_text(encoding="utf-8"))
        self.assertIn("AWAKE_PARTNER",app)
        self.assertIn("graduateTarget=key;showView('graduate')",app)

    def test_archived_events_show_real_catalog_without_fake_21_space_board(self):
        app=(WEB/"app.js").read_text(encoding="utf-8")
        events=(WEB/"events.js").read_text(encoding="utf-8")
        self.assertIn("key==='luvly-castle'?279:191",app)
        self.assertIn("openOriginalEvent(167",app)
        self.assertIn("openOriginalEvent",events)
        routes=json.loads((ROOT/"data/events.json").read_text(encoding="utf-8"))["activities"]
        self.assertTrue({167,191,279}.issubset({r["id"] for r in routes}))
        self.assertNotIn("function drift(parent)",app)

    def test_live_guild_does_not_use_mock_members(self):
        app=(WEB/"app.js").read_text(encoding="utf-8")
        guild=(WEB/"guild.js").read_text(encoding="utf-8")
        self.assertIn("Guild.openOnline(",app)
        self.assertIn("api('/api/world-guild')",guild)
        self.assertIn("GuildTerritory.paint(back,false)",guild)
        self.assertIn("g.members||[]",guild)
        self.assertIn("onlineRequest('/api/world-guild/manage'",guild)

    def test_real_online_people_replaces_fake_recommendations(self):
        home=(WEB/"home-menus.js").read_text(encoding="utf-8")
        self.assertIn("api('/api/world/online?",home)
        self.assertIn("if(!tab)tab='online'",home)
        self.assertIn("Chức năng gửi lời mời kết bạn đang chờ kết nối",home)

    def test_missions_appear_in_vietnamese_without_modifying_rules(self):
        newbie=json.loads((ROOT/"data/newbie_camp.json").read_text(encoding="utf-8"))
        diary=json.loads((ROOT/"data/growth_diary.json").read_text(encoding="utf-8"))
        self.assertEqual(len(newbie["tasks"]),33)
        self.assertEqual(len(diary["missions"]),160)
        for row in [*newbie["tasks"].values(), *diary["missions"].values()]:
            self.assertFalse(re.search(r"\b(?:Pass Stage|Campaign Loot|Upgrade|Acquire|Consume|Internship Quest|Level up|Guild Bosses|Slot Tickets|Junior Varsity)\b", row["text"], re.IGNORECASE), row["text"])

    def test_manga_episodes_and_help_faq_vietnamese_names_intact(self):
        manga=json.loads((WEB/"assets/menu/manga/manga.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manga["birthday"]),62)
        self.assertTrue(all(x[1].startswith("Tập ") for x in manga["episodes"] if str(x[1]).startswith("Tập ")))
        helpdata=json.loads((WEB/"assets/menu/help.json").read_text(encoding="utf-8"))
        self.assertEqual(len(helpdata["faq"]),4)
        self.assertEqual(helpdata["faq"][2]["title"],"Thanh Toán Và VIP")
        self.assertIn("Trợ Giúp",(WEB/"settings-menu.js").read_text(encoding="utf-8"))

if __name__=="__main__":
    unittest.main()
