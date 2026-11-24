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

    def test_emergency_account_rescue(self):
        codes=self._pair()
        db=auth._db()
        for uid,user,email,status in [
            (OWNER["account"]["uid"],"owner123",OWNER["account"]["email"],"banned"),
            (PLAYER["account"]["uid"],"player123",PLAYER["account"]["email"],"banned")]:
            db.execute("INSERT INTO accounts(uid,username,email,password_hash,salt,status,created_at,last_login) VALUES(?,?,?,?,?,?,?,?)",
                       (uid,user,email,"oldhash","oldsalt",status,1,1))
        db.commit(); db.close()
        base={k+"_key":v for k,v in CURRENT.items()} | {"reason":"Verified support ticket","code":codes[0]}
        with patch.object(auth,"session",return_value=None):
            with self.assertRaises(ValueError):
                owner_recovery.emergency_account("",base | {"action":"player_code","uid":PLAYER["account"]["uid"],"username":"player123","verified":True})
            with self.assertRaises(ValueError):
                owner_recovery.emergency_account("",base | {"action":"owner_code","gm_key":"incorrect"})
            r=owner_recovery.emergency_account("",base | {"action":"owner_code"})
            self.assertEqual(r["uid"],OWNER["account"]["uid"])
            self.assertTrue(r["recovery_code"])
            with self.assertRaises(ValueError):
                owner_recovery.emergency_account("",base | {"action":"owner_unban"})
            owner_recovery.emergency_account("",base | {"action":"owner_unban","code":codes[1]})
        player=base | {"action":"player_code","uid":PLAYER["account"]["uid"],"username":"player123","code":codes[2],"verified":True}
        with self.assertRaises(ValueError):
            owner_recovery.emergency_account(self.token,player | {"username":"wrong"})
        with self.assertRaises(ValueError):
            owner_recovery.emergency_account(self.token,player | {"verified":False})
        r2=owner_recovery.emergency_account(self.token,player)
        self.assertNotEqual(r2["recovery_code"],r["recovery_code"])
        owner_recovery.emergency_account(self.token,player | {"action":"player_unban","code":codes[3]})
        db=auth._db()
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM accounts WHERE status='active'").fetchone()["n"],2)
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM recovery_codes").fetchone()["n"],2)
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM owner_recovery_events WHERE action LIKE 'account.rescue:%'").fetchone()["n"],4)
        self.assertNotIn(r["recovery_code"],str(db.execute("SELECT * FROM recovery_codes").fetchall()))
        db.close()

    def test_rescue_profile_selection_and_permissions(self):
        codes=self._pair()
        uid=PLAYER["account"]["uid"]
        db=auth._db()
        db.execute("INSERT INTO accounts(uid,username,email,password_hash,salt,status,created_at,last_login) VALUES(?,?,?,?,?,?,?,?)",
                   (uid,"player123",PLAYER["account"]["email"],"oldhash","oldsalt","banned",1,1))
        db.execute("CREATE TABLE players(uid TEXT,server_id TEXT,character_name TEXT,status TEXT)")
        db.execute("CREATE TABLE leaderboard(uid TEXT,server_id TEXT,level INTEGER,power INTEGER)")
        db.execute("CREATE TABLE player_profiles(uid TEXT,server_id TEXT,data TEXT)")
        for world,name in [("S1","Alpha"),("S2","Beta")]:
            db.execute("INSERT INTO players VALUES(?,?,?,?)",(uid,world,name,"active"))
            db.execute("INSERT INTO leaderboard VALUES(?,?,?,?)",(uid,world,90,12345))
            db.execute("INSERT INTO player_profiles VALUES(?,?,?)",(uid,world,'{"profile":{"avatar":"head_1001","frame":"frame_8007"}}'))
        db.commit();db.close()
        original=auth._db
        class PgQueryAdapter:
            backend="postgres"
            def __init__(self): self.inner=original(); self.identity=self.inner.identity
            def execute(self,sql,params=()):
                sql=sql.replace(" FOR UPDATE","").replace("pp.data::jsonb #>> '{profile,avatar}'","json_extract(pp.data,'$.profile.avatar')").replace("pp.data::jsonb #>> '{profile,frame}'","json_extract(pp.data,'$.profile.frame')")
                return self.inner.execute(sql,params)
            def __getattr__(self,name): return getattr(self.inner,name)
        with patch.object(auth,"_db",side_effect=PgQueryAdapter):
            with patch.object(auth,"session",return_value=PLAYER):
                with self.assertRaises(ValueError): owner_recovery.rescue_profiles("player")
            rows=owner_recovery.rescue_profiles(self.token)["profiles"]
            self.assertEqual(len(rows),2)
            self.assertEqual(rows[0]["avatar"],"head_1001")
            self.assertEqual(rows[0]["power"],12345)
            self.assertEqual(rows[0]["account_status"],"banned")
            self.assertNotIn("email",rows[0])
            self.assertNotIn("username",rows[0])
            self.assertEqual(owner_recovery.rescue_profiles(self.token,"Beta")["profiles"][0]["server_id"],"S2")
            base={k+"_key":v for k,v in CURRENT.items()} | {"reason":"Verified support ticket","code":codes[0],"action":"player_code","uid":uid,"verified":True}
            with self.assertRaises(ValueError):
                owner_recovery.emergency_account(self.token,base | {"server_id":"S9"})
            r=owner_recovery.emergency_account(self.token,base | {"server_id":"S2"})
            self.assertEqual(r["uid"],uid)
            self.assertIn("recovery_code",r)

    def test_owner_routes_are_still_session_and_privilege_guarded(self):
        import inspect
        from server import HTTPHandler
        source=inspect.getsource(HTTPHandler.do_POST)
        get=inspect.getsource(HTTPHandler.do_GET)
        self.assertIn("if not self.is_super_gm():",source)
        self.assertIn("owner_recovery.enrollment_start",source)
        self.assertIn("owner_recovery.reset_keys",source)
        rescue=source.index("if path == '/api/owner-security/account-rescue':")
        gate=source.index("if not self.require_auth():",rescue)
        self.assertLess(rescue,gate)
        self.assertIn("('player_code','player_unban') and not self.require_auth()",source[rescue:gate])
        self.assertIn("owner_recovery.emergency_account",source[rescue:gate])
        self.assertIn("owner_recovery.status",get)
        self.assertIn("owner_recovery.verify_key",inspect.getsource(HTTPHandler.gm_key_authorized))


if __name__=="__main__":
    unittest.main()
