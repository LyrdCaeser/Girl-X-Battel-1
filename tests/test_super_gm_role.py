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

    def test_legacy_secret_does_not_override_account_identity(self):
        self.impersonate({**self.owner, "uid": "GXB3-00000003"})
        self.handler.headers = {"X-GXB2-Admin-Key": "a" * 50}
        self.assertFalse(self.handler.admin_authorized())


if __name__ == "__main__":
    unittest.main()
