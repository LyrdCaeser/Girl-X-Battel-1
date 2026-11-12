import tempfile
import unittest
from pathlib import Path

from gxb2 import live_service, guild as guild_rules


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


    def _guild_activity_action(self, uid, state, request, now=None, fight=lambda row: (True, 0)):
        db = live_service._db()
        try:
            db.execute("BEGIN IMMEDIATE")
            result = live_service.guild_activity_action_db(
                db, uid, "S1", state, request, int(now or 1_800_000_000), fight)
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def test_guild_checkin_and_boss_attempts_are_per_real_member(self):
        for uid, name in (("GL1", "Leader"), ("GM2", "Member")):
            live_service.register_player(uid, "S1", name)
        created = live_service.create_world_guild("GL1", "S1", "Leader", "SharedHall", "", 1000)
        live_service.apply_world_guild("GM2", "S1", "Member", created["id"], 900)
        live_service.review_guild_application("GL1", "S1", "GM2", True)
        now = 1_800_000_000
        one = {"level": 50, "items": {"2": 500, "4": 0}}
        two = {"level": 50, "items": {"2": 500, "4": 0}}

        first = self._guild_activity_action("GL1", one, {"action": "checkin"}, now)
        second = self._guild_activity_action("GM2", two, {"action": "checkin"}, now)
        self.assertEqual(first["got"], {"4": 50})
        self.assertEqual(second["got"], {"4": 50})
        with self.assertRaisesRegex(ValueError, "điểm danh"):
            self._guild_activity_action("GL1", one, {"action": "checkin"}, now + 1)

        # Boss unlock/clear progress is shared, while attempts/cooldown belong to each UID.
        a = self._guild_activity_action("GL1", one, {"action": "boss_fight", "boss": 1}, now + 2)
        b = self._guild_activity_action("GM2", two, {"action": "boss_fight", "boss": 2}, now + 3)
        self.assertTrue(a["win"]); self.assertTrue(b["win"])
        # Member GL1 owns an independent 4-fight / 16-hour budget: first two free,
        # then the original 40 and 80 Gem costs. Member GM2 still has a fresh budget.
        self._guild_activity_action("GL1", one, {"action": "boss_fight", "boss": 3}, now + 4)  # second attempt: free
        self._guild_activity_action("GL1", one, {"action": "boss_fight", "boss": 4}, now + 5)  # third attempt: 40 Gems
        self.assertEqual(int(one["items"]["2"]), 460)
        self._guild_activity_action("GL1", one, {"action": "boss_fight", "boss": 5}, now + 6)  # fourth attempt: 80 Gems
        self.assertEqual(int(one["items"]["2"]), 380)
        a_view = live_service.guild_activity_snapshot("GL1", "S1")
        b_view = live_service.guild_activity_snapshot("GM2", "S1")
        self.assertEqual(a_view["boss"]["fights"], 4)
        self.assertIsNone(a_view["boss"]["cost"])
        self.assertEqual(b_view["boss"]["fights"], 1)
        self.assertEqual(a_view["boss"]["current"], 6)
        self.assertEqual(b_view["boss"]["current"], 6)
        self.assertEqual(a_view["boss"]["cleared"], [1, 2, 3, 4, 5])
        with self.assertRaisesRegex(ValueError, "hết lượt"):
            self._guild_activity_action("GL1", one, {"action": "boss_fight", "boss": 6}, now + 7)
        reset = self._guild_activity_action("GL1", one, {"action": "boss_fight", "boss": 6}, now + 6 + 57600)
        self.assertTrue(reset["win"])
        self.assertEqual(live_service.guild_activity_snapshot("GL1", "S1")["boss"]["fights"], 1)

    def test_cafeteria_keeps_original_mill_threshold_and_order_rewards(self):
        live_service.register_player("CF1", "S1", "Canteen")
        created = live_service.create_world_guild("CF1", "S1", "Canteen", "MillHall", "", 1000)
        db = live_service._db()
        db.execute("UPDATE world_guilds SET exp=?,level=8 WHERE id=?",
                   (int(guild_rules.EXP[8]["all_exp"]), int(created["id"])))
        db.commit(); db.close()
        activity = live_service.guild_activity_snapshot("CF1", "S1")
        self.assertTrue(activity["orders"]["open"])
        self.assertEqual(activity["orders"]["open_level"], 8)
        self.assertEqual(activity["orders"]["slots"], 1)
        self.assertEqual(activity["mill"]["level"], 1)

        player = {"level": 80, "items": {"1": 20_000_000, "2": 100, "4": 0}}
        for _ in range(12):
            self._guild_activity_action("CF1", player, {"action": "donate", "index": 1})
        activity = live_service.guild_activity_snapshot("CF1", "S1")
        self.assertEqual(activity["mill"]["gold"], 12_000_000)
        self.assertEqual(activity["mill"]["level"], 2)
        self.assertEqual(activity["mill"]["factor"], 11000)
        self.assertEqual(player["items"]["1"], 8_000_000)

        order = activity["orders"]["list"][0]
        now = 1_800_000_100
        self._guild_activity_action("CF1", player, {"action": "order_start", "slot": 0}, now)
        before_gold = int(player["items"].get("1", 0))
        before_coin = int(player["items"].get("4", 0))
        self._guild_activity_action("CF1", player, {"action": "order_complete", "slot": 0}, now + int(order["time"]))
        factor = 1.1  # The original 12,000,000 Gold threshold unlocks level-2 11000 factor.
        expected = guild_rules.pairs(order["awards"])
        self.assertEqual(int(player["items"]["1"]) - before_gold, int(expected.get("1", 0) * factor))
        self.assertEqual(int(player["items"]["4"]) - before_coin, int(expected.get("4", 0) * factor))
        with self.assertRaisesRegex(ValueError, "chưa hoàn tất"):
            self._guild_activity_action("CF1", player, {"action": "order_complete", "slot": 0}, now + int(order["time"]) + 1)



    def test_engine_activity_action_returns_profile_with_real_checkin_rewards(self):
        from gxb2.engine import Engine
        player_db = Path(self.tmp.name) / "player.sqlite3"
        engine = Engine(player_db)
        try:
            state = engine._load()
            state['uid'] = 'ENG1'; state['server_id'] = 'S1'; state['name'] = 'EngineGuild'
            state['max_stage'] = 40; state['items']['4'] = 0
            engine._save_profile(state); engine.db.commit()
            live_service.register_player('ENG1', 'S1', 'EngineGuild')
            live_service.create_world_guild('ENG1', 'S1', 'EngineGuild', 'EngineHall', '', 1000)
            result = engine.world_guild_activity_action({'action': 'checkin'}, 'ENG1', 'S1')
            self.assertEqual(int(result['state']['items']['4']), 50)
            self.assertEqual(int(result['state']['account_status'] == 'active'), 1)
            self.assertEqual(live_service.guild_for_player('ENG1', 'S1')['exp'], 30)
        finally:
            engine.close()



    def test_engine_gym_boss_produces_original_runtime_battle_report(self):
        from gxb2.engine import Engine
        from gxb2.battle import luajit_runtime
        player_db = Path(self.tmp.name) / "boss-player.sqlite3"
        engine = Engine(player_db)
        try:
            state = engine._load()
            state['uid'] = 'BOSSENG'; state['server_id'] = 'S1'; state['name'] = 'BossEngine'
            state['items']['2'] = 500
            engine._save_profile(state); engine.db.commit()
            live_service.register_player('BOSSENG', 'S1', 'BossEngine')
            live_service.create_world_guild('BOSSENG', 'S1', 'BossEngine', 'BattleHall', '', 1000)
            before_gold = int(state['items'].get('1', 0))
            before_coin = int(state['items'].get('4', 0))
            result = engine.world_guild_activity_action(
                {'action': 'boss_fight', 'boss': 1}, 'BOSSENG', 'S1')
            report = result.get('report') or {}
            self.assertIn(luajit_runtime().name, ('luajit-linux-x64', 'luajit'))
            self.assertIsInstance(report.get('frames'), list)
            self.assertIn(report.get('isWin'), (0, 1))
            self.assertGreater(int(result['state']['items']['1']), before_gold)
            self.assertGreater(int(result['state']['items']['4']), before_coin)
            self.assertEqual(live_service.guild_activity_snapshot('BOSSENG', 'S1')['boss']['fights'], 1)
        finally:
            engine.close()


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
        first_score=int(detail["war"]["score_a"])
        first_exp=int(live_service.guild_for_player("GA","S1")["exp"])
        member=next(x for x in live_service.guild_for_player("GA","S1")["members"] if x["uid"]=="GA")
        first_contrib=int(member["contribution"])
        self.assertGreater(first_score,0)
        self.assertGreater(first_exp,0)
        self.assertGreater(first_contrib,0)

        # Retrying the same authoritative pair must be idempotent: no double
        # score, Guild EXP or contribution even across multiple workers.
        repeated=live_service.record_guild_war_battle(
            war["id"],"GA","GB",
            {"uid":"GA","server_id":"S1","power":2200,"team":[]},
            {"uid":"GB","server_id":"S1","power":2100,"team":[]},
            {"isWin":1,"frames":[],"total_round":5},
        )
        self.assertTrue(repeated["idempotent"])
        self.assertEqual(repeated["battle_id"],result["battle_id"])
        detail2=live_service.guild_war_detail("GA","S1",war["id"])
        self.assertEqual(int(detail2["war"]["score_a"]),first_score)
        self.assertEqual(int(live_service.guild_for_player("GA","S1")["exp"]),first_exp)
        member2=next(x for x in live_service.guild_for_player("GA","S1")["members"] if x["uid"]=="GA")
        self.assertEqual(int(member2["contribution"]),first_contrib)

        settled=live_service.settle_guild_war(war["id"],force=True)
        self.assertEqual(settled["status"],"finished")
        self.assertEqual(settled["winner_guild"],ga["id"])
        self.assertTrue(any(m["operator"]=="GUILD_WAR" for m in live_service.mailbox("GA","S1")))
        self.assertTrue(any(m["operator"]=="GUILD_WAR" for m in live_service.mailbox("GB","S1")))

    def test_auto_settle_previous_pvp_season(self):
        live_service.register_player("AUTO1","S1","AutoPlayer")
        season=live_service.previous_pvp_season()
        db=live_service._db()
        db.execute("""INSERT INTO pvp_ratings(uid,server_id,mode,season_id,rating,wins,losses,matches,updated_at)
                      VALUES(?,?,?,?,?,?,?,?,?)""",
                   ("AUTO1","S1","cross",season,1250,8,3,11,1))
        db.commit(); db.close()
        result=live_service.settle_previous_pvp_season()
        self.assertEqual(result["issued"],1)
        status=live_service.pvp_season_claim_status("AUTO1","S1","cross")
        self.assertTrue(status["claimed"])
        self.assertTrue(any(m["operator"]=="PVP_SEASON" for m in live_service.mailbox("AUTO1","S1")))


if __name__ == "__main__":
    unittest.main()
