import tempfile
import unittest
from pathlib import Path

from gxb2 import live_service
from gxb2.engine import Engine, TABLES


class SelectedOpponentMailCampaignTests(unittest.TestCase):
    def setUp(self):
        self.old = live_service.DB_PATH
        self.tmp = tempfile.TemporaryDirectory()
        live_service.DB_PATH = Path(self.tmp.name) / "live.sqlite3"

    def tearDown(self):
        live_service.DB_PATH = self.old
        self.tmp.cleanup()

    def _player(self, uid, name, power):
        live_service.register_player(uid, "S1", name)
        live_service.touch_presence(uid, "S1", name, level=50, power=power)

    def test_selected_challenge_uses_real_player_and_is_not_random_queue(self):
        self._player("ME", "Mình", 100000)
        self._player("RIVAL", "Đối thủ", 105000)
        candidates = live_service.pvp_candidates("ME", "S1", "arena")
        self.assertEqual(candidates[0]["uid"], "RIVAL")
        result = live_service.challenge_pvp("ME", "S1", "Mình", "arena", "RIVAL", "S1", 100000)
        self.assertEqual(result["status"], "matched")
        self.assertEqual(result["match"]["player_a"], "ME")
        self.assertEqual(result["match"]["player_b"], "RIVAL")
        self.assertEqual(result["match"]["status"], "active")
        self.assertEqual(live_service.pvp_status("RIVAL", "S1", "arena")["status"], "idle")

    def test_leaderboard_falls_back_to_saved_power_before_first_battle(self):
        self._player("LOW", "Thấp", 100)
        self._player("HIGH", "Cao", 900)
        board = live_service.pvp_rating_board("arena", server_id="S1")
        self.assertEqual([row["uid"] for row in board], ["HIGH", "LOW"])
        self.assertTrue(all(row["rank_basis"] == "power" for row in board))

    def test_fixed_season_is_exactly_30_days(self):
        window = live_service.pvp_season_window("arena", "S1")
        self.assertEqual(window["end_at"] - window["start_at"], 30 * 86400)

    def test_top_three_receive_automatic_mail_after_30_day_season(self):
        for uid, name, power in (("A", "Hạng A", 300), ("B", "Hạng B", 200), ("C", "Hạng C", 100), ("D", "Hạng D", 50)):
            self._player(uid, name, power)
        db = live_service._db()
        db.execute("UPDATE worlds SET created_at=100 WHERE server_id='S1'")
        db.commit(); db.close()
        result = live_service.settle_previous_pvp_season("arena", "S1", now=100 + 31 * 86400)
        self.assertEqual(result["issued"], 3)
        self.assertTrue(live_service.mailbox("A", "S1"))
        self.assertTrue(live_service.mailbox("B", "S1"))
        self.assertTrue(live_service.mailbox("C", "S1"))
        self.assertFalse(live_service.mailbox("D", "S1"))
        self.assertEqual(live_service.settle_previous_pvp_season("arena", "S1", now=100 + 31 * 86400)["issued"], 0)

    def test_server_mail_red_dot_state_can_be_marked_read(self):
        self._player("MAIL", "Người nhận", 1)
        sent = live_service.send_mail("MAIL", "S1", "Người nhận", "Quà", "Nội dung", {"1": 10})
        self.assertFalse(live_service.mailbox("MAIL", "S1")[0]["read"])
        live_service.mark_mail_read("MAIL", "S1", sent["id"])
        self.assertTrue(live_service.mailbox("MAIL", "S1")[0]["read"])

    def test_super_gm_can_clear_all_campaign_stages(self):
        engine = Engine(Path(self.tmp.name) / "profile.sqlite3")
        try:
            state = engine.developer_action({"action": "campaign_all"}, super_gm=True)
            self.assertEqual(state["max_stage"], max(map(int, TABLES["stage"])))
            self.assertEqual(state["current_stage"], state["max_stage"])
        finally:
            engine.close()


if __name__ == "__main__":
    unittest.main()
