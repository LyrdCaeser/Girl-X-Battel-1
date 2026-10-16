"""Owner-only GM access without touching production accounts, money, or guild data."""
import os
import unittest
from unittest.mock import patch

from server import HTTPHandler


class SuperGmSecurityTests(unittest.TestCase):
    def setUp(self):
        self.handler = object.__new__(HTTPHandler)
        self.owner = {"uid": "GXB3-00000001",
                      "email": "trieuquangholuxury@gmail.com"}
        self.env = patch.dict(os.environ, {
            "GXB3_OWNER_EMAIL": "trieuquangholuxury@gmail.com",
            "GXB3_OWNER_UID": "GXB3-00000001",
        })
        self.env.start()
        self.addCleanup(self.env.stop)

    def impersonate(self, account):
        self.handler.auth_context = lambda: (
            {"account": account} if account else None
        )

    def test_owner_uid_and_email_both_required(self):
        self.impersonate(self.owner)
        self.assertTrue(self.handler.is_super_gm())
        self.assertTrue(self.handler.admin_authorized())

    def test_wrong_uid_cannot_access_gm_even_same_email(self):
        self.impersonate({**self.owner, "uid": "GXB3-00000002"})
        self.assertFalse(self.handler.admin_authorized())

    def test_wrong_email_cannot_access_gm_even_same_uid(self):
        self.impersonate({**self.owner, "email": "hacker@example.com"})
        self.assertFalse(self.handler.admin_authorized())

    def test_anonymous_is_not_gm(self):
        self.impersonate(None)
        self.assertFalse(self.handler.admin_authorized())

    def test_email_case_folding(self):
        self.impersonate({**self.owner, "email": "TrieuQuangHoLuxury@GMAIL.COM"})
        self.assertTrue(self.handler.admin_authorized())

    def test_gm_key_requires_owner_session_and_exact_second_factor(self):
        key = "test-GM-key-" + "x" * 40
        with patch.dict(os.environ, {"GXB3_GM_ACTION_KEY": key,
                                  "GXB3_ADMIN_KEY": "TestAdminKey123",
                                  "GXB3_GIFTCODE_PANEL_KEY": "TestPanelKey123"}):
            self.impersonate(self.owner)
            self.handler.headers = {"X-GXB3-GM-Key": key}
            self.assertTrue(self.handler.gm_key_authorized())
            self.handler.headers = {"X-GXB3-GM-Key": key[:-1]}
            self.assertFalse(self.handler.gm_key_authorized())
            self.handler.headers = {"X-GXB3-GM-Key": key}
            self.impersonate({**self.owner, "uid": "GXB3-00000003"})
            self.assertFalse(self.handler.gm_key_authorized())

    def test_value_moving_admin_routes_require_second_factor(self):
        from pathlib import Path
        source = (Path(__file__).resolve().parents[1] / "server.py").read_text()
        source = source[source.index("    def do_POST(self):"):]
        for endpoint in ("/api/admin/mail/send", "/api/admin/order/review",
                         "/api/admin/topup-packages"):
            with self.subTest(endpoint=endpoint):
                start = source.index("if path == '" + endpoint + "':")
                route = source[start:source.index("            if path ==",start+5)]
                self.assertIn("self.admin_authorized()", route)
                self.assertIn("self.gm_key_authorized()", route)

    def test_legacy_secret_does_not_override_account_identity(self):
        self.impersonate({**self.owner, "uid": "GXB3-00000003"})
        self.handler.headers = {"X-GXB2-Admin-Key": "a" * 50}
        self.assertFalse(self.handler.admin_authorized())


if __name__ == "__main__":
    unittest.main()
