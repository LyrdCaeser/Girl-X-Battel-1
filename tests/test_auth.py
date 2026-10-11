import tempfile
import unittest
from pathlib import Path

from gxb2 import auth, live_service


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_auth = auth.DB_PATH
        self.old_live = live_service.DB_PATH
        auth.DB_PATH = Path(self.tmp.name) / "auth.sqlite3"
        live_service.DB_PATH = Path(self.tmp.name) / "live.sqlite3"

    def tearDown(self):
        auth.DB_PATH = self.old_auth
        live_service.DB_PATH = self.old_live
        self.tmp.cleanup()

    def test_register_login_session_logout(self):
        registered = auth.register("Player_01", "StrongPass123", "Waifu", "S1", "p@example.com", "UA", "127.0.0.1")
        self.assertTrue(registered["token"])
        self.assertTrue(registered["recovery_code"])
        self.assertEqual(registered["account"]["uid"], "GXB3-00000001")
        current = auth.session(registered["token"])
        self.assertEqual(current["character_name"], "Waifu")

        auth.logout(registered["token"])
        self.assertIsNone(auth.session(registered["token"]))

        logged = auth.login("player_01", "StrongPass123", "S1", "127.0.0.1", "UA2")
        self.assertEqual(logged["account"]["uid"], "GXB3-00000001")
        sessions = auth.sessions_for_token(logged["token"])
        self.assertEqual(len(sessions), 1)
        self.assertTrue(sessions[0]["current"])
        self.assertEqual(sessions[0]["user_agent"], "UA2")

    def test_password_is_hashed_and_duplicate_username_rejected(self):
        auth.register("Player_02", "AnotherPass123", "Heroine", "S1")
        db = auth._db()
        row = db.execute("SELECT password_hash,salt FROM accounts WHERE username='Player_02'").fetchone()
        db.close()
        self.assertNotEqual(row["password_hash"], "AnotherPass123")
        self.assertTrue(row["salt"])
        with self.assertRaises(ValueError):
            auth.register("player_02", "DifferentPass123", "Other", "S1")

    def test_one_account_can_create_character_on_second_world(self):
        registered = auth.register("Player_03", "AnotherPass123", "Main", "S1")
        live_service.create_world("S2", "Server 2")
        current = auth.create_character(registered["token"], "S2", "Alt")
        self.assertEqual(current["account"]["server_id"], "S2")
        self.assertEqual(current["character_name"], "Alt")
        switched = auth.switch_server(registered["token"], "S1")
        self.assertEqual(switched["character_name"], "Main")

    def test_global_ban_revokes_sessions(self):
        registered = auth.register("Player_04", "AnotherPass123", "Main", "S1")
        self.assertIsNotNone(auth.session(registered["token"]))
        account = auth.set_account_status(registered["account"]["uid"], True, "abuse")
        self.assertEqual(account["status"], "banned")
        self.assertIsNone(auth.session(registered["token"]))
        with self.assertRaises(ValueError):
            auth.login("Player_04", "AnotherPass123", "S1", "127.0.0.1")
        auth.set_account_status(registered["account"]["uid"], False)
        logged = auth.login("Player_04", "AnotherPass123", "S1", "127.0.0.1")
        self.assertTrue(logged["token"])


    def test_recovery_code_resets_password_and_revokes_sessions(self):
        registered = auth.register("Recover_01", "StrongPass123", "RecoverHero", "S1")
        second = auth.login("Recover_01", "StrongPass123", "S1", "127.0.0.1")
        self.assertGreaterEqual(len(auth.sessions_for_token(second["token"])), 2)
        auth.reset_password("Recover_01", registered["recovery_code"], "NewStrong456")
        self.assertIsNone(auth.session(registered["token"]))
        self.assertIsNone(auth.session(second["token"]))
        with self.assertRaises(ValueError):
            auth.login("Recover_01", "StrongPass123", "S1", "127.0.0.1")
        fresh = auth.login("Recover_01", "NewStrong456", "S1", "127.0.0.1")
        self.assertTrue(fresh["token"])
        with self.assertRaises(ValueError):
            auth.reset_password("Recover_01", registered["recovery_code"], "AgainStrong789")

    def test_server_policy_blocks_registration_and_character_creation(self):
        live_service.create_world("S2", "Server 2")
        live_service.set_world_policy("S2", registration_open=False, message="Đóng đăng ký")
        with self.assertRaises(ValueError):
            auth.register("Blocked_1", "StrongPass123", "Nope", "S2")
        first = auth.register("Allowed_1", "StrongPass123", "Main", "S1")
        live_service.set_world_policy("S2", registration_open=True, character_creation_open=False, message="Đóng tạo NV")
        with self.assertRaises(ValueError):
            auth.create_character(first["token"], "S2", "Alt")

    def test_revoke_single_session(self):
        registered = auth.register("Session_1", "StrongPass123", "Main", "S1")
        second = auth.login("Session_1", "StrongPass123", "S1", "127.0.0.2", "Other Device")
        rows = auth.sessions_for_token(registered["token"])
        target = next(x for x in rows if not x["current"])
        auth.revoke_session(registered["token"], target["session_id"])
        self.assertIsNone(auth.session(second["token"]))
        self.assertIsNotNone(auth.session(registered["token"]))

if __name__ == "__main__":
    unittest.main()
