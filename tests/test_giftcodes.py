"""Giftcode Studio tests use isolated SQLite, never production Neon."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from gxb2 import giftcodes, live_service, database

class GiftcodeStudioTests(unittest.TestCase):
    def setUp(self):
        if database.is_postgres():
            self.skipTest("Use only isolated SQLite for giftcode tests")
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        dbpath=Path(self.temp.name)/"giftcode.sqlite3"
        raw_connect=database.connect
        p=patch.object(live_service,"_db",lambda:raw_connect(dbpath,"live"))
        p.start(); self.addCleanup(p.stop)
        old=giftcodes._READY
        giftcodes._READY=False
        self.addCleanup(setattr,giftcodes,"_READY",old)
        live_service.register_player("GXB-TEST-A","S1","Alice")
        live_service.register_player("GXB-TEST-B","S1","Bob")
    def issue(self,**changes):
        payload=dict(title="Giftcode Test",message="Test Gift",
                     rewards={"1":100,"2":25},server_id="S1",max_uses=2)
        payload.update(changes)
        return giftcodes.create(payload,"GM-TEST")
    def test_create_and_redeem_via_original_mail(self):
        code=self.issue()
        self.assertRegex(code['code'],r"^GXB3-[0-9A-F]{16}$")
        self.assertEqual(giftcodes.list_codes()[0]['used_count'],0)
        result=giftcodes.redeem(code['code'],"GXB-TEST-A","S1")
        self.assertTrue(result['ok'])
        mail=live_service.mailbox("GXB-TEST-A","S1")
        self.assertEqual(len(mail),1)
        self.assertEqual(mail[0]['attachments'],{"1":100,"2":25})
        self.assertEqual(mail[0]['id'],result['mail_id'])
        with self.assertRaisesRegex(ValueError,'đã sử dụng'):
            giftcodes.redeem(code['code'],"GXB-TEST-A","S1")
        self.assertEqual(giftcodes.list_codes()[0]['used_count'],1)
        self.assertEqual(len(giftcodes.redemptions(code['code'])),1)
    def test_cap_revocation_and_server_scope(self):
        code=self.issue(max_uses=1)
        giftcodes.redeem(code['code'],"GXB-TEST-A","S1")
        with self.assertRaisesRegex(ValueError,'hết lượt'):
            giftcodes.redeem(code['code'],"GXB-TEST-B","S1")
        self.assertEqual(live_service.mailbox("GXB-TEST-B","S1"),[])
        another=self.issue()
        giftcodes.revoke(another['code'],"GM-TEST")
        with self.assertRaisesRegex(ValueError,'đã bị khóa'):
            giftcodes.redeem(another['code'],"GXB-TEST-B","S1")
        live_service.create_world("S2","Server 2")
        s2=self.issue(server_id="S2")
        with self.assertRaisesRegex(ValueError,'không áp dụng'):
            giftcodes.redeem(s2['code'],"GXB-TEST-A","S1")
    def test_invalid_catalog_and_failed_mail_insert_roll_back(self):
        with self.assertRaises(ValueError):
            self.issue(rewards={"999999999":10})
        c=self.issue()
        db=live_service._db()
        try:
            db.execute("""CREATE TRIGGER reject_gift_mail BEFORE INSERT ON mail
                          BEGIN SELECT RAISE(ABORT,'mock mail failure'); END""")
            db.commit()
        finally:
            db.close()
        with self.assertRaises(Exception):
            giftcodes.redeem(c['code'],"GXB-TEST-A","S1")
        self.assertEqual(giftcodes.list_codes()[0]['used_count'],0)
        self.assertEqual(giftcodes.redemptions(c['code']),[])
        self.assertEqual(live_service.mailbox("GXB-TEST-A","S1"),[])
    def test_super_gm_and_key_required_for_creation(self):
        import inspect
        from server import HTTPHandler
        source=inspect.getsource(HTTPHandler.do_POST)
        route=source[source.index("if path.startswith('/api/giftcode/admin/'):"):]
        self.assertIn('self.admin_authorized()',route)
        self.assertIn('self.gm_key_authorized()',route)
        self.assertIn("giftcodes.redeem(data.get('code'),account['uid'],account['server_id'])",source)

if __name__=="__main__":
    unittest.main()
