"""Regression test for the lobby assets served by GXB3, not just file existence."""
import threading
import unittest
from http.server import ThreadingHTTPServer
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


if __name__ == "__main__":
    unittest.main()
