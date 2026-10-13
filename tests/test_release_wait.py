"""Release gating tests: transient startup 502 must not be reported as a failed build.

All network calls are mocked; no access to production VPS or Neon.
"""
import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "verify_vps_release.py"
SPEC = importlib.util.spec_from_file_location("gxb3_release_checker", SCRIPT)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class Reply:
    def __init__(self, data, status=200):
        self.data = json.dumps(data).encode()
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, _size=8192):
        return self.data


class WaitForReadyTests(unittest.TestCase):
    def test_eventually_ready_after_connection_refused_and_proxy_error(self):
        calls = []

        def fake_open(_req, timeout=4):
            calls.append(timeout)
            if len(calls) < 3:
                raise URLError("startup delayed")
            return Reply({"ready": True, "database": "postgres"})

        with patch.object(release, "urlopen", side_effect=fake_open):
            self.assertTrue(release.wait_ready("test", "http://127.0.0.1:9080",
                                              require_postgres=True, timeout=1, interval=.001))
        self.assertEqual(len(calls), 3)

    def test_local_ready_rejects_non_postgres_state(self):
        with patch.object(release, "urlopen", return_value=Reply({"ready": True, "database": "sqlite"})):
            self.assertFalse(release.wait_ready("test", "http://127.0.0.1:9080",
                                               require_postgres=True, timeout=.02, interval=.005))

    def test_https_ready_can_be_database_agnostic(self):
        with patch.object(release, "urlopen", return_value=Reply({"ready": True})):
            self.assertTrue(release.wait_ready("test", "https://game.example.test",
                                              timeout=0, interval=.001))


if __name__ == "__main__":
    unittest.main()
