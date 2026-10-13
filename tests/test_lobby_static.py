"""Regression test for the lobby assets served by GXB3, not just file existence."""
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from server import HTTPHandler


class QuietHandler(HTTPHandler):
    def log_message(self, *args):
        pass


class LobbyAssetsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.http.public_origin = ""
        cls.http.trust_proxy = False
        cls.worker = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.worker.join(timeout=5)

    def test_lobby_javascript(self):
        with urlopen(f"http://127.0.0.1:{self.http.server_port}/lobby-dialogue.js", timeout=5) as response:
            self.assertEqual(response.status, 200)
            self.assertIn("javascript", response.headers["Content-Type"])
            self.assertIn(b"LobbyDialogue", response.read())

    def test_lobby_css(self):
        with urlopen(f"http://127.0.0.1:{self.http.server_port}/lobby-dialogue.css", timeout=5) as response:
            self.assertEqual(response.status, 200)
            self.assertIn("text/css", response.headers["Content-Type"])
            self.assertIn(b"#gxb3-lobby-speech", response.read())

    def test_other_mobile_stylesheets(self):
        """Assets used in index.html must be served even if not manually listed."""
        for name in ("mobile-native.css", "mobile-layout.css"):
            with self.subTest(name=name), urlopen(
                f"http://127.0.0.1:{self.http.server_port}/{name}", timeout=5
            ) as response:
                self.assertEqual(response.status, 200)
                self.assertIn("text/css", response.headers["Content-Type"])
                self.assertTrue(response.read())

    def test_lobby_cache_busting_query(self):
        with urlopen(
            f"http://127.0.0.1:{self.http.server_port}/lobby-dialogue.js?v=20261013",
            timeout=5,
        ) as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b"LobbyDialogue", response.read())

    def test_static_fallback_does_not_expose_nonpublic_files(self):
        for name in ("server.py", ".env.production.example",
                     "missing-script.js", "assets/../server.py"):
            with self.subTest(name=name):
                with self.assertRaises(HTTPError) as caught:
                    urlopen(f"http://127.0.0.1:{self.http.server_port}/{name}", timeout=5)
                self.assertEqual(caught.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
