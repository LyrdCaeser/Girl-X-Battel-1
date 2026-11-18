"""Source-level route assertions; no production calls or mutations."""
import inspect
import unittest

from server import HTTPHandler
from gxb2 import s4_gm

class S4GMSecurityRoutes(unittest.TestCase):
    def test_admin_and_second_factor_gate_delete(self):
        code=inspect.getsource(HTTPHandler.do_POST)
        start=code.index("if path in ('/api/admin/s4/character/preview','/api/admin/s4/character/delete'):")
        end=code.index("if path == '/api/admin/s4/giftcode/create':",start)
        route=code[start:end]
        self.assertIn('self.admin_authorized()',route)
        self.assertIn('self.gm_key_authorized()',route)
        self.assertIn("self.server.player_engines.run_exclusive(",route)
        self.assertIn("auth.revoke_world_sessions(uid,'S4')",route)
        self.assertIn("s4_gm.preview(data.get('uid'))",route)
        self.assertIn("s4_gm.delete(",route)

    def test_code_factory_requires_two_factors(self):
        code=inspect.getsource(HTTPHandler.do_POST)
        start=code.index("if path == '/api/admin/s4/giftcode/create':")
        end=code.index("if path == '/api/admin/goddess-gift/create':",start)
        route=code[start:end]
        self.assertIn('self.admin_authorized()',route)
        self.assertIn('self.gm_key_authorized()',route)
        self.assertIn('giftcodes.create_s4_exclusive',route)

    def test_delete_targets_only_s4_tables(self):
        self.assertEqual(s4_gm.WORLD,'S4')
        self.assertNotIn('accounts',s4_gm.SCOPED_TABLES)
        self.assertNotIn('orders',s4_gm.SCOPED_TABLES)
        self.assertNotIn('giftcode_redemptions',s4_gm.SCOPED_TABLES)
        self.assertIn('player_profiles',s4_gm.SCOPED_TABLES)
        self.assertIn('mail',s4_gm.SCOPED_TABLES)
        code=inspect.getsource(s4_gm.delete)
        self.assertIn('s4_character_archives',code)
        self.assertIn('db.commit()',code)
        self.assertIn('db.rollback()',code)
        self.assertIn('(uid,WORLD)',code)
        self.assertIn('XOA S4',code)

if __name__=='__main__':
    unittest.main()
