import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from gxb2 import auth, database
from tools import reset_owner_game_password as reset


class ResetOwnerGamePasswordTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        path = Path(self.tmp.name) / "auth.sqlite3"
        self.patch_db = patch.object(auth, "_db", lambda: database.connect(path, "auth"))
        self.patch_db.start()
        self.addCleanup(self.patch_db.stop)
        self.env = patch.dict(os.environ, {
            "GXB3_OWNER_UID": "GXB3-00000001",
            "GXB3_OWNER_EMAIL": "owner@example.test",
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        db = auth._db()
        db.execute("""INSERT INTO accounts(uid,username,email,password_hash,salt,status,created_at)
                      VALUES(?,?,?,?,?,'active',?)""",
                   ("GXB3-00000001","Admin","owner@example.test","oldhash","00",int(time.time())))
        db.execute("""INSERT INTO accounts(uid,username,email,password_hash,salt,status,created_at)
                      VALUES(?,?,?,?,?,'active',?)""",
                   ("GB3-123456789","Player","player@example.test","pwh","00",int(time.time())))
        db.execute("""INSERT INTO sessions(token_hash,account_id,server_id,created_at,expires_at,last_seen,session_id)
                      VALUES('old-session',1,'S1',1,9999999999,1,'SES-OLD')""")
        db.execute("""INSERT INTO sessions(token_hash,account_id,server_id,created_at,expires_at,last_seen,session_id)
                      VALUES('player-session',2,'S1',1,9999999999,1,'SES-PLAYER')""")
        db.commit()
        db.close()

    def test_reset_only_exact_owner_credentials_recovery_and_sessions(self):
        result = reset.reset_existing_owner_account("NewSecurePass123", "ABCD-EFGH-IJKL-MNOP")
        self.assertEqual(result, {"uid":"GXB3-00000001","username":"Admin"})
        self.assertTrue(auth.login("Admin","NewSecurePass123","S1")["account"]["uid"] == "GXB3-00000001")
        db = auth._db()
        owner = db.execute("SELECT * FROM accounts WHERE uid='GXB3-00000001'").fetchone()
        player = db.execute("SELECT * FROM accounts WHERE uid='GB3-123456789'").fetchone()
        self.assertNotEqual(owner["password_hash"],"oldhash")
        self.assertEqual(player["password_hash"],"pwh")
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM sessions WHERE account_id=1").fetchone()["n"],1)
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM sessions WHERE account_id=2").fetchone()["n"],1)
        recovery = db.execute("SELECT * FROM recovery_codes WHERE account_id=1").fetchone()
        self.assertEqual(recovery["used_at"],0)
        self.assertEqual(recovery["code_hash"],auth._recovery_hash("ABCD-EFGH-IJKL-MNOP"))
        db.close()

    def test_wrong_email_fails_closed(self):
        with patch.dict(os.environ, {"GXB3_OWNER_EMAIL":"attacker@example.test"}):
            with self.assertRaisesRegex(RuntimeError,"SUPER GM"):
                reset.reset_existing_owner_account("NewSecurePass123","ABCD-EFGH-IJKL-MNOP")
        db=auth._db()
        self.assertEqual(db.execute("SELECT password_hash FROM accounts WHERE id=1").fetchone()["password_hash"],"oldhash")
        db.close()

    def test_password_policy_rejects_weak_password_before_write(self):
        with self.assertRaises(ValueError):
            reset.reset_existing_owner_account("weak","ABCD-EFGH-IJKL-MNOP")
        db=auth._db()
        self.assertEqual(db.execute("SELECT password_hash FROM accounts WHERE id=1").fetchone()["password_hash"],"oldhash")
        db.close()


if __name__ == "__main__":
    unittest.main()
