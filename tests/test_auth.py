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
        registered = auth.register("Player_01", "StrongPass123", "Waifu", "S1", "p@example.com")
        self.assertTrue(registered["token"])
        self.assertEqual(registered["account"]["uid"], "GXB3-00000001")
        current = auth.session(registered["token"])
        self.assertEqual(current["character_name"], "Waifu")

        auth.logout(registered["token"])
        self.assertIsNone(auth.session(registered["token"]))

        logged = auth.login("player_01", "StrongPass123", "S1", "127.0.0.1")
        self.assertEqual(logged["account"]["uid"], "GXB3-00000001")

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


if __name__ == "__main__":
    unittest.main()
