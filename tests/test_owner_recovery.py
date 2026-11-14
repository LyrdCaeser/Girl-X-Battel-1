"""Isolated SQLite regression for owner TOTP and irreversible Neon admin-key overrides.

Never writes to game production, never invokes the real owner account.
"""
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2 import auth, database, owner_recovery, studio_sso

ORIGINAL={
    "GXB3_ADMIN_KEY":"OwnerAccess123!",
    "GXB3_GIFTCODE_PANEL_KEY":"PanelAccess123!",
    "GXB3_GM_ACTION_KEY":"OwnerGMActionSecret12345678!",
    "GXB3_OWNER_EMAIL":"owner-test@example.com",
    "GXB3_OWNER_UID":"GXB3-00000001",
}
CURRENT={"admin":ORIGINAL["GXB3_ADMIN_KEY"],"panel":ORIGINAL["GXB3_GIFTCODE_PANEL_KEY"],
         "gm":ORIGINAL["GXB3_GM_ACTION_KEY"]}
NEW={"admin":"DifferentAdminKey123","panel":"DifferentPanelKey123",
     "gm":"DifferentActionKey123456789"}
OWNER={"account":{"uid":"GXB3-00000001","email":"owner-test@example.com"}}
PLAYER={"account":{"uid":"GB3-987654321","email":"other@example.com"}}


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        path=Path(self.tmp.name)/"isolated-auth.sqlite3"
        old=set(owner_recovery._READY)
        owner_recovery._READY.clear()
        self.addCleanup(lambda: (owner_recovery._READY.clear(),owner_recovery._READY.update(old)))
        connect=database.connect
        p=patch.object(auth,"_db",lambda:connect(path,"auth"))
        p.start();self.addCleanup(p.stop)
        p=patch.object(auth,"session",return_value=OWNER)
        p.start();self.addCleanup(p.stop)
        p=patch.dict(os.environ,ORIGINAL)
        p.start();self.addCleanup(p.stop)
        self.token="gxb3-authenticated-owner-session"

    def _pair(self):
        result=owner_recovery.enrollment_start(self.token,CURRENT)
        self.assertIn("otpauth://totp/",result["otpauth_url"])
        self.assertEqual(len(result["secret"]),32)
        db=auth._db()
        rec=db.execute("SELECT * FROM owner_security WHERE id=1").fetchone()
        db.close()
        code=owner_recovery._totp_at(owner_recovery._secret(rec["pending_nonce"]),
                                      int(time.time())//30)
        result=owner_recovery.enrollment_confirm(self.token,code)
        self.assertEqual(len(result["backup_codes"]),8)
        self.assertTrue(owner_recovery.status(self.token)["enrolled"])
        return list(result["backup_codes"])

    def test_cannot_enroll_without_all_original_credentials(self):
        with self.assertRaisesRegex(ValueError,"ba khóa"):
            owner_recovery.enrollment_start(self.token,{**CURRENT,"panel":"wrong"})
        self.assertFalse(owner_recovery.status(self.token)["enrolled"])
        with patch.object(auth,"session",return_value=PLAYER):
            with self.assertRaisesRegex(ValueError,"SUPER GM"):
                owner_recovery.enrollment_start(self.token,CURRENT)
            with self.assertRaisesRegex(ValueError,"SUPER GM"):
                owner_recovery.status(self.token)

    def test_enrollment_generates_once_visible_backup_codes_and_never_stores_plaintext(self):
        codes=self._pair()
        db=auth._db()
        row=db.execute("SELECT * FROM owner_security WHERE id=1").fetchone()
        plaintext=str(row)
        hashes=[x["code_hash"] for x in db.execute("SELECT code_hash FROM owner_recovery_backups").fetchall()]
        db.close()
        self.assertEqual(int(row["enrolled"]),1)
        self.assertEqual(row["pending_nonce"],"")
        self.assertNotIn("secret",plaintext)
        self.assertEqual(len(hashes),8)
        for c in codes:
            self.assertNotIn(c,plaintext)
            self.assertNotIn(c,hashes)
        with self.assertRaisesRegex(ValueError,"đã liên kết"):
            owner_recovery.enrollment_start(self.token,CURRENT)

    def test_backup_reset_rotates_three_keys_and_invalidates_existing_access(self):
        codes=self._pair()
        old_token=studio_sso.unlock(CURRENT["panel"],self.token,CURRENT["admin"],CURRENT["gm"])
        self.assertTrue(studio_sso.authorized(old_token,self.token))
        r=owner_recovery.reset_keys(self.token,codes[0],NEW)
        self.assertTrue(r["reset"])
        self.assertFalse(studio_sso.authorized(old_token,self.token))
        self.assertTrue(owner_recovery.verify_all(NEW["admin"],NEW["panel"],NEW["gm"]))
        self.assertFalse(owner_recovery.verify_all(CURRENT["admin"],CURRENT["panel"],CURRENT["gm"]))
        self.assertTrue(owner_recovery.verify_key("gm",NEW["gm"]))
        self.assertFalse(owner_recovery.verify_key("gm",CURRENT["gm"]))
        self.assertEqual(owner_recovery.status(self.token)["backup_remaining"],7)
        with self.assertRaisesRegex(ValueError,"không hợp lệ"):
            owner_recovery.reset_keys(self.token,codes[0],NEW)
        unlocked=studio_sso.unlock(NEW["panel"],self.token,NEW["admin"],NEW["gm"])
        self.assertTrue(studio_sso.authorized(unlocked,self.token))
        with self.assertRaisesRegex(ValueError,"không chính xác"):
            studio_sso.unlock(CURRENT["panel"],self.token,CURRENT["admin"],CURRENT["gm"])

    def test_otp_is_single_use_and_backup_rotation_requires_new_otp(self):
        old_codes=self._pair()
        db=auth._db()
        row=db.execute("SELECT nonce FROM owner_security WHERE id=1").fetchone()
        db.close()
        future=int(time.time())+95
        otp=owner_recovery._totp_at(owner_recovery._secret(row["nonce"]),future//30)
        with patch.object(owner_recovery.time,"time",return_value=future):
            rotated=owner_recovery.rotate_backups(self.token,otp)
            self.assertEqual(len(rotated["backup_codes"]),8)
            with self.assertRaisesRegex(ValueError,"không chính xác"):
                owner_recovery.rotate_backups(self.token,otp)
            with self.assertRaisesRegex(ValueError,"không hợp lệ"):
                owner_recovery.reset_keys(self.token,old_codes[0],NEW)
            self.assertTrue(owner_recovery.reset_keys(self.token,rotated["backup_codes"][0],NEW)["reset"])

    def test_factor_lockout_and_no_partial_key_write(self):
        self._pair()
        for _ in range(4):
            with self.assertRaisesRegex(ValueError,"không hợp lệ"):
                owner_recovery.reset_keys(self.token,"000000",NEW)
        with self.assertRaisesRegex(ValueError,"không hợp lệ"):
            owner_recovery.reset_keys(self.token,"000000",NEW)
        with self.assertRaisesRegex(ValueError,"tạm khóa"):
            owner_recovery.reset_keys(self.token,"000000",NEW)
        self.assertTrue(owner_recovery.verify_all(CURRENT["admin"],CURRENT["panel"],CURRENT["gm"]))
        db=auth._db()
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM owner_key_overrides").fetchone()["n"],0)
        db.close()

    def test_owner_routes_are_still_session_and_privilege_guarded(self):
        import inspect
        from server import HTTPHandler
        source=inspect.getsource(HTTPHandler.do_POST)
        get=inspect.getsource(HTTPHandler.do_GET)
        self.assertIn("if not self.is_super_gm():",source)
        self.assertIn("owner_recovery.enrollment_start",source)
        self.assertIn("owner_recovery.reset_keys",source)
        self.assertIn("owner_recovery.status",get)
        self.assertIn("owner_recovery.verify_key",inspect.getsource(HTTPHandler.gm_key_authorized))


if __name__=="__main__":
    unittest.main()
