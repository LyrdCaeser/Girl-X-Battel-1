import tempfile
import unittest
from pathlib import Path

from gxb2 import live_service


class GuildAndSeasonTests(unittest.TestCase):
    def setUp(self):
        self.old = live_service.DB_PATH
        self.tmp = tempfile.TemporaryDirectory()
        live_service.DB_PATH = Path(self.tmp.name) / "live.sqlite3"

    def tearDown(self):
        live_service.DB_PATH = self.old
        self.tmp.cleanup()

    def test_guild_application_roles_chat_and_mail(self):
        for uid, name, power in [("L1","Leader",2000),("D1","Deputy",1800),("M1","Member",1500)]:
            live_service.register_player(uid, "S1", name)
            live_service.touch_presence(uid, "S1", name, 50, power)

        guild = live_service.create_world_guild("L1","S1","Leader","Moon", "Welcome", 2000)
        live_service.apply_world_guild("D1","S1","Deputy",guild["id"],1800)
        live_service.review_guild_application("L1","S1","D1",True)
        live_service.set_guild_role("L1","S1","D1","deputy")

        live_service.apply_world_guild("M1","S1","Member",guild["id"],1500)
        live_service.review_guild_application("D1","S1","M1",True)
        data = live_service.guild_for_player("M1","S1")
        self.assertEqual(data["name"], "Moon")
        self.assertEqual(data["member_count"], 3)

        live_service.send_guild_chat("M1","S1","Member","hello guild")
        chat = live_service.guild_chat("L1","S1")
        self.assertEqual(chat[-1]["message"], "hello guild")

        mail = live_service.send_guild_mail("D1","S1","Guild News","Hello members")
        self.assertEqual(mail["sent"], 3)
        self.assertEqual(len(live_service.mailbox("M1","S1")), 1)

        live_service.kick_guild_member("D1","S1","M1")
        self.assertIsNone(live_service.guild_for_player("M1","S1"))
        live_service.transfer_guild_leader("L1","S1","D1")
        self.assertEqual(live_service.guild_for_player("D1","S1")["role"], "leader")

    def test_previous_season_reward_claim(self):
        live_service.register_player("P1","S1","Player")
        season = live_service.previous_pvp_season()
        db = live_service._db()
        db.execute("""INSERT INTO pvp_ratings(uid,server_id,mode,season_id,rating,wins,losses,matches,updated_at)
                      VALUES(?,?,?,?,?,?,?, ?,?)""",
                   ("P1","S1","arena",season,1500,12,4,16,1))
        db.commit(); db.close()

        status = live_service.pvp_season_claim_status("P1","S1","arena")
        self.assertTrue(status["eligible"])
        self.assertFalse(status["claimed"])
        claimed = live_service.claim_pvp_season_reward("P1","S1","Player","arena")
        self.assertTrue(claimed["ok"])
        self.assertTrue(live_service.pvp_season_claim_status("P1","S1","arena")["claimed"])
        self.assertEqual(len(live_service.mailbox("P1","S1")), 1)


if __name__ == "__main__":
    unittest.main()
