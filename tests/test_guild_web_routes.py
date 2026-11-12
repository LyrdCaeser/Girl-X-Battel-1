"""Guard the production guild UI from falling back to local simulated members.

Only verifies read-only source wiring; never writes player or guild state.
"""
import unittest
from pathlib import Path

WEB = Path(__file__).resolve().parents[1] / "web"


class GuildWebRoutingTests(unittest.TestCase):
    def test_all_guild_menu_entries_use_online_service_only(self):
        app = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertEqual(app.count("Guild.openOnline(key,origin||view)"), 2)
        self.assertNotIn("Guild.open(", app)
        self.assertIn("Bang Hội chưa sẵn sàng", app)

    def test_guild_online_reads_real_authenticated_endpoint(self):
        guild = (WEB / "guild.js").read_text(encoding="utf-8")
        self.assertIn("api('/api/world-guild')", guild)
        self.assertIn("'/api/world-guild/manage'", guild)
        self.assertIn("'/api/world-guild/action'", guild)
        self.assertIn("GuildTerritory.paint(back,false)", guild)
        self.assertIn("renderOnlineGuild", guild)

    def test_online_guild_exposes_real_management_mail_ranking_and_war_actions(self):
        guild = (WEB / "guild.js").read_text(encoding="utf-8")
        for action in ("role", "kick", "transfer", "mail", "war", "review", "chat"):
            self.assertIn("action:'" + action + "'", guild)
        self.assertIn("/api/guild-war?war_id=", guild)
        self.assertIn("/api/guild-war/battle", guild)
        self.assertIn("/api/world-guild/manage", guild)
        self.assertIn("Thành Viên Thật", guild)
        self.assertIn("Xếp Hạng Bang Hội", guild)
        self.assertIn("'guild-dining':'cafeteria'", guild)
        self.assertIn("'guild-gym':'gym'", guild)
        self.assertIn("'/api/world-guild/activity'", guild)
        self.assertIn("onlineActivity('donate'", guild)
        self.assertIn("onlineActivity('boss_fight'", guild)
        self.assertIn("Đơn Hàng", guild)
        self.assertIn("Boss Bang Hội", guild)
        self.assertNotIn("đang tạm khóa", guild)


    def test_cafeteria_and_gym_posts_use_authenticated_player_engine_bridge(self):
        server = (Path(__file__).resolve().parents[1] / "server.py").read_text(encoding="utf-8")
        engine = (Path(__file__).resolve().parents[1] / "gxb2/engine.py").read_text(encoding="utf-8")
        self.assertIn("if path == '/api/world-guild/activity':", server)
        self.assertIn("self.engine.world_guild_activity_action(data, account['uid'], account['server_id'])", server)
        self.assertIn("self.db.borrowed_live_transaction()", engine)
        self.assertIn("world_guild_progress", (Path(__file__).resolve().parents[1] / "gxb2/database.py").read_text(encoding="utf-8"))

    def test_junior_varsity_uses_online_real_player_entry_not_local_bot_api(self):
        arena = (WEB / "arena.js").read_text(encoding="utf-8")
        self.assertIn("GxbOnline.open('pvp','arena')", arena)
        self.assertNotIn("act({action:'open'})", arena)


if __name__ == "__main__":
    unittest.main()
