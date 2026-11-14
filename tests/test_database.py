import tempfile
import unittest
from pathlib import Path

from gxb2 import database


@unittest.skipIf(database.is_postgres(), "SQLite adapter test")
class DatabaseAdapterTests(unittest.TestCase):
    def test_auth_and_live_schema_are_initialized_per_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            a1 = Path(tmp) / "a1.sqlite3"
            a2 = Path(tmp) / "a2.sqlite3"
            live = Path(tmp) / "live.sqlite3"

            db = database.connect(a1, "auth")
            tables = {r["name"] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            db.close()
            self.assertIn("accounts", tables)
            self.assertIn("sessions", tables)

            db = database.connect(a2, "auth")
            tables2 = {r["name"] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            db.close()
            self.assertIn("recovery_codes", tables2)

            db = database.connect(live, "live")
            worlds = db.execute("SELECT server_id FROM worlds").fetchall()
            db.close()
            self.assertEqual(worlds[0]["server_id"], "S1")


if __name__ == "__main__":
    unittest.main()
