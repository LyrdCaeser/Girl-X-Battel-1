import tempfile
import unittest
from pathlib import Path

from gxb2 import live_service


class LiveServiceTests(unittest.TestCase):
    def setUp(self):
        self.old = live_service.DB_PATH
        self.tmp = tempfile.TemporaryDirectory()
        live_service.DB_PATH = Path(self.tmp.name) / "live.sqlite3"

    def tearDown(self):
        live_service.DB_PATH = self.old
        self.tmp.cleanup()

    def test_world_player_ban_mail_and_order_flow(self):
        live_service.create_world("S2", "Server 2")
        p = live_service.register_player("U100", "S2", "Alice")
        self.assertEqual(p["status"], "active")

        mail = live_service.send_mail("U100", "S2", "Alice", "Gift", "Hello", {"2": 100})
        self.assertEqual(mail["attachments"]["2"], 100)
        got = live_service.claim_mail(mail["id"], "U100", "S2")
        self.assertEqual(got, {"2": 100})

        order = live_service.create_order("U100", "S2", "Alice", "Pack A")
        approved = live_service.review_order(order["id"], True, {"2": 500})
        self.assertEqual(approved["status"], "approved")
        self.assertTrue(any(m["title"] == "Nạp thành công" for m in live_service.mailbox("U100", "S2")))

        banned = live_service.set_ban("U100", "S2", True, "test")
        self.assertEqual(banned["status"], "banned")
        with self.assertRaises(ValueError):
            live_service.create_order("U100", "S2", "Alice", "Pack B")
        live_service.set_ban("U100", "S2", False)
        self.assertEqual(live_service.player("U100", "S2")["status"], "active")

        live_service.touch_presence("U100", "S2", "Alice", level=88, power=123456)
        online = live_service.online_players("S2")
        self.assertEqual(online[0]["uid"], "U100")
        board = live_service.leaderboard("S2")
        self.assertEqual(board[0]["rank"], 1)
        self.assertEqual(board[0]["power"], 123456)

    def test_name_must_match_for_gm_mail(self):
        live_service.register_player("U1", "S1", "Hero")
        with self.assertRaises(ValueError):
            live_service.send_mail("U1", "S1", "Wrong", "Gift", "", {"1": 1})

    def test_shared_guild_and_pvp_matchmaking(self):
        live_service.register_player("U1", "S1", "Alpha")
        live_service.register_player("U2", "S1", "Beta")
        guild = live_service.create_world_guild("U1", "S1", "Alpha", "Moon Guild", "Welcome", 1000)
        self.assertEqual(guild["role"], "leader")
        joined = live_service.join_world_guild("U2", "S1", "Beta", guild["id"], 900)
        self.assertEqual(joined["member_count"], 2)

        first = live_service.enqueue_pvp("U1", "S1", "Alpha", "arena", 1000)
        self.assertEqual(first["status"], "waiting")
        second = live_service.enqueue_pvp("U2", "S1", "Beta", "arena", 950)
        self.assertEqual(second["status"], "matched")
        match = second["match"]
        active = live_service.activate_pvp_match(match["id"], "U1")
        self.assertEqual(active["status"], "active")

        live_service.leave_world_guild("U2", "S1")
        self.assertIsNone(live_service.guild_for_player("U2", "S1"))


if __name__ == "__main__":
    unittest.main()
