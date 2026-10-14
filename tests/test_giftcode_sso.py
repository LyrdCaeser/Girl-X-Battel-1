"""Cross-domain Giftcode SSO: one-time, short-lived, tied to original game session."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from gxb2 import auth, live_service, database, studio_sso

class GiftcodeSsoTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base=Path(self.temp.name)
        original=database.connect
        a=patch.object(auth,"_db",lambda: original(base/"accounts.sqlite3","auth"))
        b=patch.object(live_service,"_db",lambda: original(base/"live.sqlite3","live"))
        a.start();b.start();self.addCleanup(a.stop);self.addCleanup(b.stop)
        account=auth.register("SsoTestUser", "TestPassword123A", "Nhân Vật", "S1")
        self.token=account['token']

    def test_game_login_converts_to_one_time_studio_session(self):
        ticket=studio_sso.start(self.token)
        self.assertNotEqual(ticket,self.token)
        second=studio_sso.exchange(ticket,'test-browser','test-ip')
        self.assertNotEqual(second,self.token)
        self.assertEqual(auth.session(second)['account']['username'],"SsoTestUser")
        with self.assertRaisesRegex(ValueError,"Liên kết"):
            studio_sso.exchange(ticket)
        self.assertTrue(auth.session(self.token))

    def test_revoked_game_session_prevents_exchange(self):
        ticket=studio_sso.start(self.token)
        auth.logout(self.token)
        with self.assertRaisesRegex(ValueError,"Phiên game"):
            studio_sso.exchange(ticket)

    def test_panel_lock_requires_configured_secret_and_session(self):
        with patch.dict("os.environ",{"GXB3_GIFTCODE_PANEL_KEY":"ExamplePass123!","GXB3_GM_ACTION_KEY":"x"*40}):
            with self.assertRaisesRegex(ValueError,"không chính xác"):
                studio_sso.unlock("bad",self.token)
            access=studio_sso.unlock("ExamplePass123!",self.token)
            self.assertTrue(studio_sso.authorized(access,self.token))
            self.assertFalse(studio_sso.authorized(access,'another-session'))
        with patch.dict("os.environ",{"GXB3_GIFTCODE_PANEL_KEY":""}):
            with self.assertRaisesRegex(RuntimeError,"Chưa cấu hình"):
                studio_sso.unlock("ExamplePass123!",self.token)

if __name__=="__main__":
    unittest.main()
