"""Three-key Studio gate: none of the keys alone can expose giftcode or paid skin administration."""
import os
import unittest
from unittest.mock import patch
from gxb2 import studio_sso

KEYS = {
    "GXB3_ADMIN_KEY":"owner-access-password-only",
    "GXB3_GIFTCODE_PANEL_KEY":"studio-private-panel-only",
    "GXB3_GM_ACTION_KEY":"gxb3-explicit-high-trust-operations-2026",
}


class StudioThreeKeyTests(unittest.TestCase):
    def test_all_three_keys_and_authenticated_session_required(self):
        with patch.dict(os.environ, KEYS), patch.object(studio_sso.auth, 'session', return_value={'account': {'uid': 'OWNER'}}):
            token = studio_sso.unlock(KEYS['GXB3_GIFTCODE_PANEL_KEY'], 'session-token',
                 KEYS['GXB3_ADMIN_KEY'], KEYS['GXB3_GM_ACTION_KEY'])
            self.assertTrue(studio_sso.authorized(token, 'session-token'))
            self.assertFalse(studio_sso.authorized(token, 'another-session'))
            for value in ('wrong-admin-key', '', None):
                with self.assertRaises(ValueError):
                    studio_sso.unlock(KEYS['GXB3_GIFTCODE_PANEL_KEY'], 'session-token',
                         value, KEYS['GXB3_GM_ACTION_KEY'])
            for value in ('wrong-panel-key', '', None):
                with self.assertRaises(ValueError):
                    studio_sso.unlock(value, 'session-token',
                         KEYS['GXB3_ADMIN_KEY'], KEYS['GXB3_GM_ACTION_KEY'])
            for value in ('wrong-gm-key', '', None):
                with self.assertRaises(ValueError):
                    studio_sso.unlock(KEYS['GXB3_GIFTCODE_PANEL_KEY'], 'session-token',
                         KEYS['GXB3_ADMIN_KEY'], value)
        with patch.dict(os.environ, KEYS), patch.object(studio_sso.auth, 'session', return_value=None):
            with self.assertRaises(ValueError):
                studio_sso.unlock(KEYS['GXB3_GIFTCODE_PANEL_KEY'], 'session-token',
                    KEYS['GXB3_ADMIN_KEY'], KEYS['GXB3_GM_ACTION_KEY'])

    def test_server_must_have_each_key_configured(self):
        for missing in KEYS:
            with patch.dict(os.environ, {**KEYS,missing:''}),patch.object(studio_sso.auth, 'session', return_value={'account': {'uid': 'OWNER'}}):
                with self.assertRaises(RuntimeError):
                    studio_sso.unlock(KEYS['GXB3_GIFTCODE_PANEL_KEY'], 'session-token',
                        KEYS['GXB3_ADMIN_KEY'], KEYS['GXB3_GM_ACTION_KEY'])


if __name__ == '__main__':
    unittest.main()
