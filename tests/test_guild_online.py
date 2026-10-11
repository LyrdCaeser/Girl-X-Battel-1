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

    def test_guild_war_score_progression_and_rewards(self):
        for uid,name,power in [("GA","GuildA",2200),("GB","GuildB",2100)]:
            live_service.register_player(uid,"S1",name)
            live_service.touch_presence(uid,"S1",name,80,power)
        ga=live_service.create_world_guild("GA","S1","GuildA","Alpha","",2200)
        gb=live_service.create_world_guild("GB","S1","GuildB","Beta","",2100)
        war=live_service.schedule_guild_war("GA","S1",gb["id"],3600)

        db=live_service._db()
        db.execute("UPDATE guild_wars SET status='active',starts_at=0 WHERE id=?",(war["id"],))
        db.commit(); db.close()

        prep=live_service.prepare_guild_war_attack("GA","S1",war["id"],"GB")
        self.assertEqual(prep["defender"]["guild_id"],gb["id"])
        result=live_service.record_guild_war_battle(
            war["id"],"GA","GB",
            {"uid":"GA","server_id":"S1","power":2200,"team":[]},
            {"uid":"GB","server_id":"S1","power":2100,"team":[]},
            {"isWin":1,"frames":[],"total_round":5},
        )
        self.assertEqual(result["winner_uid"],"GA")
        detail=live_service.guild_war_detail("GA","S1",war["id"])
        self.assertGreater(detail["war"]["score_a"],0)
        self.assertGreater(live_service.guild_for_player("GA","S1")["exp"],0)
        member=next(x for x in live_service.guild_for_player("GA","S1")["members"] if x["uid"]=="GA")
        self.assertGreater(member["contribution"],0)

        settled=live_service.settle_guild_war(war["id"],force=True)
        self.assertEqual(settled["status"],"finished")
        self.assertEqual(settled["winner_guild"],ga["id"])
        self.assertTrue(any(m["operator"]=="GUILD_WAR" for m in live_service.mailbox("GA","S1")))
        self.assertTrue(any(m["operator"]=="GUILD_WAR" for m in live_service.mailbox("GB","S1")))


if __name__ == "__main__":
    unittest.main()
