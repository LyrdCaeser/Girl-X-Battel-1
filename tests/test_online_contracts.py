import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OnlineContractTests(unittest.TestCase):
    def test_main_api_preserves_same_origin_login_cookie(self):
        source = (ROOT / "web" / "app.js").read_text()
        self.assertIn("credentials:'same-origin'", source)

    def test_expired_device_session_is_handled_as_auth_error(self):
        source = (ROOT / "server.py").read_text()
        self.assertIn("if path == '/api/auth/sessions':", source)
        self.assertIn("except ValueError as exc:", source)
        self.assertIn("return self.send(401, {'error': str(exc)})", source)


if __name__ == "__main__":
    unittest.main()
