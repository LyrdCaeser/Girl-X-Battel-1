"""Offline regression for root-only first-time recovery.

No production Neon access and no file in /proc or systemd is read here.
"""
import importlib.util
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2 import auth, database, owner_recovery

SCRIPT=Path(__file__).resolve().parents[1]/"tools/bootstrap_owner_recovery.py"
spec=importlib.util.spec_from_file_location("gxb3_root_bootstrap",SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

KEY_ENV={
 "GXB3_ADMIN_KEY":"OriginalAdminKey123!",
 "GXB3_GIFTCODE_PANEL_KEY":"OriginalPanelKey123!",
 "GXB3_GM_ACTION_KEY":"OriginalVeryLongActionKey123456!",
 "GXB3_OWNER_UID":"GXB3-00000001",
 "GXB3_OWNER_EMAIL":"owner-test@example.com",
}
NEW_KEYS={"admin":"NewAdminValue456","panel":"NewPanelValue456",
          "gm":"NewActionValue456789012345"}
OWNER_DATA={"uid":"GXB3-00000001","username":"owner-test","email":"owner-test@example.com"}


class RootBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        path=Path(self.tmp.name)/"isolated.sqlite"
        old=set(owner_recovery._READY)
        owner_recovery._READY.clear()
        self.addCleanup(lambda:(owner_recovery._READY.clear(), owner_recovery._READY.update(old)))
        connect=database.connect
        def newdb():
            return connect(path,"auth")
        a=patch.object(auth,"_db",newdb)
        a.start();self.addCleanup(a.stop)
        p=patch.dict(os.environ,KEY_ENV)
        p.start();self.addCleanup(p.stop)
        db=auth._db()
        db.execute("""INSERT INTO accounts(uid,username,email,password_hash,salt,status,created_at)
                   VALUES(?,?,?,?,?,'active',?)""",
                   (OWNER_DATA["uid"],OWNER_DATA["username"],OWNER_DATA["email"],"x","s",int(time.time())))
        db.commit();db.close()

    def _token(self):
        nonce="offline-nonce-for-test"
        counter=int(time.time())//30
        return nonce,counter,owner_recovery._totp_at(owner_recovery._secret(nonce),counter)

    def test_root_bootstrap_issues_hashes_for_three_new_keys_no_game_writes(self):
        nonce,counter,otp=self._token()
        self.assertEqual(owner_recovery._counter(nonce,otp,-1),counter)
        backups=module.apply_first_time_recovery(nonce,counter,NEW_KEYS)
        self.assertEqual(len(backups),8)
        self.assertTrue(owner_recovery.verify_all(NEW_KEYS["admin"],NEW_KEYS["panel"],NEW_KEYS["gm"]))
        self.assertFalse(owner_recovery.verify_all(KEY_ENV["GXB3_ADMIN_KEY"],KEY_ENV["GXB3_GIFTCODE_PANEL_KEY"],KEY_ENV["GXB3_GM_ACTION_KEY"]))
        db=auth._db()
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM accounts").fetchone()["n"],1)
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM owner_key_overrides").fetchone()["n"],3)
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM owner_recovery_backups WHERE used_at=0").fetchone()["n"],8)
        row=db.execute("SELECT * FROM owner_security WHERE id=1").fetchone()
        self.assertEqual(row["nonce"],nonce)
        self.assertEqual(row["last_counter"],counter)
        self.assertEqual(row["version"],1)
        self.assertNotIn(NEW_KEYS["admin"],str(dict(row)))
        db.close()

    def test_existing_enrollment_does_not_get_overwritten(self):
        nonce,counter,_=self._token()
        module.apply_first_time_recovery(nonce,counter,NEW_KEYS)
        with self.assertRaisesRegex(RuntimeError,"đã liên kết"):
            module.apply_first_time_recovery("new-nonce",counter+1,NEW_KEYS)
        db=auth._db()
        self.assertEqual(db.execute("SELECT nonce FROM owner_security").fetchone()["nonce"],nonce)
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM owner_key_overrides").fetchone()["n"],3)
        db.close()

    def test_noncanonical_owner_account_does_not_become_super_gm(self):
        with patch.dict(os.environ,{"GXB3_OWNER_UID":"GXB3-00000199"}):
            nonce,counter,_=self._token()
            with self.assertRaisesRegex(RuntimeError,"SUPER GM"):
                module.apply_first_time_recovery(nonce,counter,NEW_KEYS)
        db=auth._db()
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM owner_key_overrides").fetchone()["n"],0)
        db.close()

    def test_on_failure_transaction_rolls_back_changes(self):
        nonce,counter,_=self._token()
        with patch.object(owner_recovery,"_new_backups",side_effect=RuntimeError("simulated failure")):
            with self.assertRaisesRegex(RuntimeError,"simulated failure"):
                module.apply_first_time_recovery(nonce,counter,NEW_KEYS)
        db=auth._db()
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM owner_key_overrides").fetchone()["n"],0)
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM owner_security").fetchone()["n"],0)
        db.close()

    def test_systemd_environment_loader_never_displays_secrets(self):
        with patch.object(module.subprocess,"run",return_value=type("R",(),{"stdout":"0\n"})()):
            with self.assertRaisesRegex(RuntimeError,"chưa chạy"):
                module.load_running_service_environment()

    def test_live_command_requires_root_tty_before_touching_database(self):
        with patch.object(module.os,"geteuid",return_value=1001):
            with self.assertRaisesRegex(RuntimeError,"root"):
                module.main()


if __name__=="__main__":
    unittest.main()
