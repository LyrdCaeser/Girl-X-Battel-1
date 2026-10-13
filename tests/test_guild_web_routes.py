"""Guard the production guild UI from falling back to local simulated members.

Only verifies read-only source wiring; never writes player or guild state.
"""
import unittest
from pathlib import Path

WEB = Path(__file__).resolve().parents[1] / "web"


class GuildWebRoutingTests(unittest.TestCase):
    def test_all_guild_menu_entries_use_online_service_only(self):
        app = (WEB / "app.js").read_text(encoding="utf-8")
        self.assertEqual(app.count("GxbOnline.open('guild')"), 2)
        self.assertNotIn("Guild.open(", app)
        self.assertIn("Bang Hội Online chưa sẵn sàng", app)

    def test_guild_online_reads_real_authenticated_endpoint(self):
        hub = (WEB / "online-hub.js").read_text(encoding="utf-8")
        self.assertIn("get('/api/world-guild')", hub)
        self.assertIn("post('/api/world-guild/manage'", hub)
        self.assertIn("post('/api/world-guild/action'", hub)


if __name__ == "__main__":
    unittest.main()
