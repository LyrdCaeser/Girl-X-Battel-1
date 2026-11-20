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

    def test_authenticated_player_requests_do_not_take_duplicate_snapshot_for_ban_check(self):
        source = (ROOT / "server.py").read_text(encoding="utf-8")
        self.assertIn("if not self.require_auth():", source)
        self.assertIn("Do not take a full gameplay snapshot just to repeat that account check.", source)
        self.assertNotIn("account_state = self.engine.snapshot()", source)

    def test_identity_bound_player_snapshot_does_not_upsert_live_player(self):
        import tempfile
        from unittest.mock import patch
        from pathlib import Path
        from gxb2.engine import Engine
        from gxb2 import live_service
        with tempfile.TemporaryDirectory(prefix="gxb3-snapshot-test-") as td:
            engine = Engine(Path(td) / "player.sqlite3", identity=("GB3-123456789", "S1"))
            try:
                with patch.object(live_service, "register_player") as register, \
                     patch.object(live_service, "mailbox", return_value=[]), \
                     patch.object(live_service, "worlds", return_value=[]):
                    state = engine.snapshot()
                register.assert_not_called()
                self.assertEqual(state["account_status"], "active")
            finally:
                engine.close()


if __name__ == "__main__":
    unittest.main()
