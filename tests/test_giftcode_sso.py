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

    def test_redirect_finishes_http11_response_without_hanging(self):
        """A Chrome tab must not wait for an unterminated 303 keep-alive body."""
        import http.client
        import threading
        from http.server import ThreadingHTTPServer
        from server import HTTPHandler

        class TestHandler(HTTPHandler):
            def reject_unauthorized_admin_mode(self):
                return False
            def require_auth(self):
                return {'account': {'uid': 'TEST', 'server_id': 'S1'}}
            def session_token(self):
                return 'test-session'

        server=ThreadingHTTPServer(('127.0.0.1', 0), TestHandler)
        thread=threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        connection=http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=3)
        try:
            with patch.object(studio_sso, 'start', return_value='example-single-use-ticket'):
                connection.request('GET', '/api/giftcode/sso/start')
                response=connection.getresponse()
                self.assertEqual(response.status,303)
                self.assertEqual(response.getheader('Content-Length'),'0')
                self.assertEqual(response.getheader('Connection'),'close')
                self.assertEqual(response.getheader('Cache-Control'),'no-store')
                self.assertEqual(response.getheader('Referrer-Policy'),'no-referrer')
                self.assertEqual(
                    response.getheader('Location'),
                    studio_sso.STUDIO_ORIGIN+'/?ticket=example-single-use-ticket')
                self.assertEqual(response.read(),b'')
        finally:
            connection.close()
            server.shutdown()
            server.server_close()
            thread.join(timeout=4)

    def test_panel_lock_requires_configured_secret_and_session(self):
        keys = {"GXB3_ADMIN_KEY":"OwnerAccess123!", "GXB3_GIFTCODE_PANEL_KEY":"ExamplePass123!",
                "GXB3_GM_ACTION_KEY":"x"*40}
        with patch.dict("os.environ", keys):
            with self.assertRaisesRegex(ValueError,"không chính xác"):
                studio_sso.unlock("bad", self.token, keys["GXB3_ADMIN_KEY"], keys["GXB3_GM_ACTION_KEY"])
            for omitted in ("admin", "panel", "gm"):
                with self.assertRaisesRegex(ValueError,"không chính xác"):
                    studio_sso.unlock(
                        "bad" if omitted=="panel" else keys["GXB3_GIFTCODE_PANEL_KEY"],
                        self.token,
                        "bad" if omitted=="admin" else keys["GXB3_ADMIN_KEY"],
                        "bad" if omitted=="gm" else keys["GXB3_GM_ACTION_KEY"])
            access=studio_sso.unlock(keys["GXB3_GIFTCODE_PANEL_KEY"], self.token,
                keys["GXB3_ADMIN_KEY"], keys["GXB3_GM_ACTION_KEY"])
            self.assertTrue(studio_sso.authorized(access,self.token))
            self.assertFalse(studio_sso.authorized(access,'another-session'))
        with patch.dict("os.environ",{"GXB3_GIFTCODE_PANEL_KEY":""}):
            with self.assertRaisesRegex(RuntimeError,"chưa cấu hình"):
                studio_sso.unlock("ExamplePass123!",self.token)

if __name__=="__main__":
    unittest.main()
