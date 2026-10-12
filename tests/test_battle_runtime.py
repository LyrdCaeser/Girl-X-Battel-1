import shutil
import tempfile
import unittest
from pathlib import Path

from gxb2.engine import Engine
from gxb2.battle import simulate, ONLINE_BATTLE_ID, normalize_online_seed
from gxb2 import chimes, guild_lab, home_systems


@unittest.skipUnless(shutil.which("luajit"), "LuaJIT is required for runtime battle smoke test")
class BattleRuntimeTests(unittest.TestCase):
    def test_symmetric_pvp_bonus_payload_runs_in_luajit(self):
        with tempfile.TemporaryDirectory() as tmp:
            engine = Engine(Path(tmp) / "player.sqlite3")
            try:
                with engine.lock:
                    state = engine._load()

                    skill_id = next(iter(guild_lab.ROWS))
                    state["guild_lab"] = {"levels": {str(skill_id): 1}, "reset_times": {}}

                    chime_id = next(iter(chimes.CHIMES))
                    state["chimes"] = {str(chime_id): {"lev": 0, "buffs": [0, 0, 0, 0]}}

                    open_pet = next((pid for pid, row in home_systems.ROWS["pet"].items()
                                     if row.get("is_open") == "1"), None)
                    if open_pet:
                        state["home_systems"] = {
                            "selected_pet": int(open_pet),
                            "pets": {str(open_pet): {"lv": 1, "grade": 1, "skills": [0, 0, 0, 0]}}
                        }
                    engine._save_profile(state)
                    engine.db.commit()

                try:
                    snap = engine.pvp_team_snapshot()
                except RuntimeError as exc:
                    if "cannot load incompatible bytecode" in str(exc):
                        self.skipTest("Archived battle bytecode requires the bundled/original compatible LuaJIT runtime")
                    raise
                self.assertTrue(snap["team"])
                self.assertTrue(snap["guild_skills"])
                self.assertTrue(snap["chime_bonus"])

                try:
                    report = simulate(
                    snap["team"], snap["team"],
                    battle_id=ONLINE_BATTLE_ID, seed=normalize_online_seed(123456),
                    pet_a=snap.get("pet"), pet_b=snap.get("pet"),
                    guild_skills_a=snap["guild_skills"],
                    guild_skills_b=snap["guild_skills"],
                    chime_bonus_a=snap["chime_bonus"],
                    chime_bonus_b=snap["chime_bonus"],
                        battle_type=1,
                    )
                except RuntimeError as exc:
                    if "cannot load incompatible bytecode" in str(exc):
                        self.skipTest("Archived battle bytecode requires the bundled/original compatible LuaJIT runtime")
                    raise
                self.assertIn(report["isWin"], (0, 1))
                self.assertIsInstance(report["frames"], list)
            finally:
                engine.close()


if __name__ == "__main__":
    unittest.main()
