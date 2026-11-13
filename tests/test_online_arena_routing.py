import tempfile
import json
import unittest
from pathlib import Path

from gxb2 import live_service, topup
from gxb2.engine import Engine, GameError, TABLES
from gxb2.battle import attributes

ROOT = Path(__file__).resolve().parents[1]


class OnlineArenaRoutingTests(unittest.TestCase):
    def setUp(self):
        self.old_db = live_service.DB_PATH
        self.old_topup = topup.OVERRIDE_PATH
        self.tmp = tempfile.TemporaryDirectory()
        live_service.DB_PATH = Path(self.tmp.name) / "live.sqlite3"
        topup.OVERRIDE_PATH = Path(self.tmp.name) / "topup.json"

    def tearDown(self):
        live_service.DB_PATH = self.old_db
        topup.OVERRIDE_PATH = self.old_topup
        self.tmp.cleanup()


    def test_16_to_25_star_runtime_attributes_apply_approved_growth(self):
        runtime = ROOT / "runtime" / "luajit-linux-x64"
        if not runtime.exists():
            self.skipTest("Bundled compatible Linux LuaJIT is unavailable")
        import os
        from unittest.mock import patch
        base = {"partner_id": 71, "table_id": 757001, "lv": 330, "grade": 0,
                "awake": 5, "equips": [], "pos": 1, "show_skin": 1,
                "ex_skills": [0, 0, 0, 0]}
        with patch.dict(os.environ, {"GXB2_LUAJIT": str(runtime)}):
            baseline = attributes([base])["71"]
            for target_star in range(16, 26):
                partner = {**base, "awake": target_star - 10}
                actual = attributes([partner])["71"]
                steps = target_star - 15
                hp, atk = int(baseline["hp"]), int(baseline["atk"])
                hp_cycle = (14.56, 14.56, 9.62, 9.62)
                atk_cycle = (10.40, 10.40, 7.49, 7.49)
                for step in range(steps):
                    hp = int(hp * (1 + hp_cycle[step % 4] / 100))
                    atk = int(atk * (1 + atk_cycle[step % 4] / 100))
                arm = int(baseline["arm"] * (1 + 0.02 * steps))
                self.assertEqual(actual["hp"], hp, f"HP mismatch at {target_star}★")
                self.assertEqual(actual["atk"], atk, f"ATK mismatch at {target_star}★")
                self.assertEqual(actual["arm"], arm, f"DEF mismatch at {target_star}★")
                self.assertGreater(actual["power"], baseline["power"])

    def test_native_10_to_15_star_runtime_attributes_remain_unchanged(self):
        runtime = ROOT / "runtime" / "luajit-linux-x64"
        if not runtime.exists():
            self.skipTest("Bundled compatible Linux LuaJIT is unavailable")
        import os
        from unittest.mock import patch
        base = {"partner_id": 72, "table_id": 757001, "lv": 330, "grade": 0,
                "awake": 0, "equips": [], "pos": 1, "show_skin": 1,
                "ex_skills": [0, 0, 0, 0]}
        expected = {
            10: (465433, 37588, 2027), 11: (531210, 41381, 2027),
            12: (606567, 45569, 2027), 13: (692900, 50195, 2027),
            14: (758246, 53870, 2027), 15: (829879, 57821, 2027),
        }
        with patch.dict(os.environ, {"GXB2_LUAJIT": str(runtime)}):
            for star, (hp, atk, arm) in expected.items():
                partner = {**base, "awake": star - 10}
                actual = attributes([partner])["72"]
                self.assertEqual((actual["hp"], actual["atk"], actual["arm"]),
                                 (hp, atk, arm), f"Native stats changed at {star}★")

    def test_limit_break_ui_displays_defense_baseline_for_16_to_25(self):
        source = (ROOT / "web/girl-ui.js").read_text(encoding="utf-8")
        self.assertIn("row('DEF',String(100+(targetStar-15)*2)+'% so với 15★')", source)

    def test_junior_varsity_entry_uses_real_online_pvp(self):
        source = (ROOT / "web/arena.js").read_text(encoding="utf-8")
        self.assertIn("NativeOnlineArenas.open(mode,from)", source)
        self.assertIn("arena_scene", source)
        self.assertNotIn("act({action:'open'})", source)



    def test_pvp_board_lists_real_active_players_before_their_first_match(self):
        live_service.create_world("S2", "Server 2")
        live_service.register_player("U21", "S1", "Real Alpha")
        live_service.register_player("U22", "S1", "Real Beta")
        live_service.register_player("U23", "S2", "Real Gamma")
        live_service.touch_presence("U21", "S1", "Real Alpha", level=50, power=250000)
        live_service.touch_presence("U22", "S1", "Real Beta", level=60, power=300000)
        live_service.touch_presence("U23", "S2", "Real Gamma", level=70, power=400000)
        db = live_service._db()
        db.execute("INSERT INTO pvp_ratings(uid,server_id,mode,season_id,rating,wins,losses,matches,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
                   ("U22", "S1", "team", live_service.current_pvp_season(), 1120, 2, 0, 2, 123))
        db.commit()
        db.close()

        same_server = live_service.pvp_rating_board("team", server_id="S1")
        self.assertEqual({r["uid"] for r in same_server}, {"U21", "U22"})
        beta = next(r for r in same_server if r["uid"] == "U22")
        alpha = next(r for r in same_server if r["uid"] == "U21")
        self.assertEqual(beta["rating"], 1120)
        self.assertEqual(beta["wins"], 2)
        self.assertEqual(alpha["rating"], 1000)
        self.assertEqual(alpha["matches"], 0)

        cross_server = live_service.pvp_rating_board("cross")
        self.assertEqual({r["uid"] for r in cross_server}, {"U21", "U22", "U23"})
        self.assertEqual(next(r for r in cross_server if r["uid"] == "U23")["character_name"], "Real Gamma")

    def test_cross_server_queue_never_matches_same_server_and_matches_different_server(self):
        live_service.create_world("S2", "Server 2")
        first = live_service.enqueue_pvp("U1", "S1", "Alpha", "cross", 1000)
        second = live_service.enqueue_pvp("U2", "S1", "Beta", "cross", 900)
        self.assertEqual(first["status"], "waiting")
        self.assertEqual(second["status"], "waiting")
        third = live_service.enqueue_pvp("U3", "S2", "Gamma", "cross", 950)
        self.assertEqual(third["status"], "matched")
        self.assertEqual(third["match"]["mode"], "cross")
        self.assertNotEqual(third["match"]["server_a"], third["match"]["server_b"])

    def test_team_arena_matches_real_players_on_same_server(self):
        first = live_service.enqueue_pvp("U10", "S1", "Team Alpha", "team", 1000)
        second = live_service.enqueue_pvp("U11", "S1", "Team Beta", "team", 1050)
        self.assertEqual(first["status"], "waiting")
        self.assertEqual(second["status"], "matched")
        self.assertEqual(second["match"]["mode"], "team")
        self.assertEqual(second["match"]["server_a"], "S1")
        self.assertEqual(second["match"]["server_b"], "S1")

    def test_universe_host_can_awaken_16_star_with_own_copy_and_six_faction_sacrifice(self):
        with tempfile.TemporaryDirectory(prefix="gxb3-universe-awake-") as td:
            engine = Engine(Path(td) / "profile.sqlite3")
            try:
                universe = next(r for r in TABLES["partner"].values()
                                if int(r.get("group") or 0) == 7
                                and int(r.get("max_star") or 0) == 10
                                and r.get("show_in_guide"))
                sacrifice = next(r for r in TABLES["partner"].values()
                                 if 1 <= int(r.get("group") or 0) <= 6
                                 and int(r.get("max_star") or 0) == 10
                                 and Engine.awake25_valid_goddess(r))
                state = engine._load()
                state["partners"] = [
                    {"partner_id": 1, "table_id": int(universe["id"]), "lv": 330,
                     "grade": 0, "awake": 5, "equips": [], "pos": 0, "show_skin": 1},
                    {"partner_id": 2, "table_id": int(universe["id"]), "lv": 250,
                     "grade": 0, "awake": 0, "equips": [], "pos": 0, "show_skin": 1},
                    {"partner_id": 3, "table_id": int(sacrifice["id"]), "lv": 250,
                     "grade": 0, "awake": 0, "equips": [], "pos": 0, "show_skin": 1},
                ]
                state["formation"] = []
                state["items"]["10"] = 25000
                engine._save_profile(state)
                engine.db.commit()
                engine.handle("AWAKE_PARTNER", {"partner_id": 1, "material_ids": [2, 3]})
                after = engine._load()
                self.assertEqual(next(x for x in after["partners"] if x["partner_id"] == 1)["awake"], 6)
                self.assertEqual({x["partner_id"] for x in after["partners"]}, {1})
                self.assertEqual(after["items"]["10"], 0)
            finally:
                engine.close()

    def test_universe_goddess_is_rejected_as_generic_sacrifice_for_other_faction(self):
        with tempfile.TemporaryDirectory(prefix="gxb3-universe-reject-") as td:
            engine = Engine(Path(td) / "profile.sqlite3")
            try:
                host = next(r for r in TABLES["partner"].values()
                            if int(r.get("group") or 0) == 1
                            and int(r.get("max_star") or 0) == 10
                            and r.get("show_in_guide"))
                universe = next(r for r in TABLES["partner"].values()
                                if int(r.get("group") or 0) == 7
                                and int(r.get("max_star") or 0) == 10
                                and r.get("show_in_guide"))
                state = engine._load()
                state["partners"] = [
                    {"partner_id": 11, "table_id": int(host["id"]), "lv": 330,
                     "grade": 0, "awake": 5, "equips": [], "pos": 0, "show_skin": 1},
                    {"partner_id": 12, "table_id": int(host["id"]), "lv": 250,
                     "grade": 0, "awake": 0, "equips": [], "pos": 0, "show_skin": 1},
                    {"partner_id": 13, "table_id": int(universe["id"]), "lv": 250,
                     "grade": 0, "awake": 0, "equips": [], "pos": 0, "show_skin": 1},
                ]
                state["formation"] = []
                state["items"]["10"] = 25000
                engine._save_profile(state)
                engine.db.commit()
                with self.assertRaises(GameError):
                    engine.handle("AWAKE_PARTNER", {"partner_id": 11, "material_ids": [12, 13]})
                after = engine._load()
                self.assertEqual({x["partner_id"] for x in after["partners"]}, {11, 12, 13})
                self.assertEqual(next(x for x in after["partners"] if x["partner_id"] == 11)["awake"], 5)
                self.assertEqual(after["items"]["10"], 25000)
            finally:
                engine.close()

    def test_universe_goddesses_are_not_generic_sacrifice_materials(self):
        rows = [r for r in TABLES["partner"].values()
                if int(r.get("group") or 0) == 7 and int(r.get("max_star") or 0) == 10
                and r.get("show_in_guide")]
        valid = [r for r in rows if Engine.awake25_valid_goddess(r)]
        self.assertEqual(len(rows), 3)
        self.assertEqual(valid, [])

    def test_universe_goddess_can_advance_with_own_copy_and_six_faction_sacrifice_pool(self):
        engine = Engine.__new__(Engine)
        universe = next(r for r in TABLES["partner"].values()
                        if int(r.get("group") or 0) == 7 and int(r.get("max_star") or 0) == 10
                        and r.get("show_in_guide"))
        same_character_copy = dict(universe)
        other_universe = next(r for r in TABLES["partner"].values()
                              if int(r.get("group") or 0) == 7 and int(r.get("max_star") or 0) == 10
                              and r.get("show_in_guide") and r.get("id") != universe.get("id"))
        faction_sacrifice = next(r for r in TABLES["partner"].values()
                                 if 1 <= int(r.get("group") or 0) <= 6
                                 and int(r.get("max_star") or 0) == 10
                                 and Engine.awake25_valid_goddess(r))
        self.assertTrue(engine.awake25_same_character(universe, same_character_copy))
        self.assertFalse(engine.awake25_same_character(universe, other_universe))
        self.assertTrue(Engine.awake25_valid_goddess(faction_sacrifice))

    def test_16_to_25_star_recipe_counts_and_costs_are_present_for_universe(self):
        engine = Engine.__new__(Engine)
        universe = next(r for r in TABLES["partner"].values()
                        if int(r.get("group") or 0) == 7 and int(r.get("max_star") or 0) == 10
                        and r.get("show_in_guide"))
        expected_copies = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
        expected_sacrifices = list(range(1, 11))
        expected_costs = [25000, 30000, 35000, 40000, 50000,
                          60000, 70000, 80000, 90000, 100000]
        for index, star in enumerate(range(16, 26)):
            recipe = engine.awake_recipe({"table_id": int(universe["id"]), "awake": star - 11})
            self.assertTrue(recipe["awake25"])
            self.assertEqual(recipe["star"], star)
            self.assertEqual(recipe["copies"], expected_copies[index])
            self.assertEqual(recipe["sacrifices"], expected_sacrifices[index])
            self.assertEqual(recipe["cost"], {"10": expected_costs[index]})
            self.assertEqual(recipe["group"], 7)

    def test_arena3v3_entry_routes_to_live_team_pvp_and_blocks_local_simulator(self):
        client = (ROOT / "web/arena3v3.js").read_text(encoding="utf-8")
        open_block = client.split(" function open(", 1)[1].split("\n function icon", 1)[0]
        self.assertIn("NativeOnlineArenas.open('arena3v3',from)", open_block)
        self.assertNotIn("showView('arena3v3')", open_block)
        self.assertNotIn("act({action:'open'})", open_block)
        online = (ROOT / "web/online-hub.js").read_text(encoding="utf-8")
        self.assertIn("['arena3v3','Đấu Trường 3v3']", online)
        self.assertIn("/api/pvp/arena3v3/teams", online)
        self.assertIn("/api/pvp/arena3v3/pay", online)
        self.assertIn("/api/pvp/arena3v3/round", online)
        self.assertIn("Thi Đấu Lượt", online)
        server = (ROOT / "server.py").read_text(encoding="utf-8")
        self.assertIn("path == '/api/arena3v3/action':\n                return self.send(410", server)
        self.assertIn("match.get('mode') == 'arena3v3'", server)
        self.assertIn("phải hoàn tất đủ loạt đấu", server)

    def test_modified_client_assets_are_cache_busted(self):
        index = (ROOT / "web/index.html").read_text(encoding="utf-8")
        for asset in ("app.js", "arena.js", "arena3v3.js", "online-hub.js", "guild.js",
                      "girl-ui.js", "auth.js", "settings-menu.js", "skins.js"):
            self.assertRegex(index, rf'<script src="/{asset}\?v=(?:20261112|20261113|1\.1\.2)-[^" ]+"')
        self.assertIn('href="/online-hub.css?v=20261112-live-arena3v3-r2"', index)
        self.assertIn('href="/guild.css?v=20261113-native-online-r1"', index)
        self.assertIn('src="/arena-online-native.js?v=20261113-original-native-r1"', index)

    def test_high_density_avatars_are_served_from_a_confined_webp_asset_root(self):
        server = (ROOT / "server.py").read_text(encoding="utf-8")
        self.assertIn("('/assets/avatar-hd/', ROOT/'web/assets/avatar-hd')", server)
        self.assertIn("candidate = (folder / path[len(prefix):]).resolve()", server)
        self.assertIn("candidate.is_relative_to(folder.resolve()) and candidate.is_file()", server)
        self.assertIn("'.webp':'image/webp'", server)
        catalog = json.loads((ROOT / "web/assets/avatars.json").read_text(encoding="utf-8"))
        avatar = next(row for row in catalog.values() if row.get("src"))
        self.assertTrue(avatar['src'].startswith('/assets/avatar-hd/portraits/'))
        self.assertTrue(avatar['src'].endswith('.webp?v=1.1.2'))

    def test_gxb3_tests_workflow_runs_for_production_pull_requests(self):
        workflow = (ROOT / ".github/workflows/gxb3-tests.yml").read_text(encoding="utf-8")
        self.assertIn("pull_request:\n    branches: [main, snez-vietnamese]", workflow)


if __name__ == "__main__":
    unittest.main()
