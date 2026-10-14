"""RC7 GM gift integration: two isolated real users, replay protection, and shard catalog.

Local temporary SQLite only. Production Neon/accounts and player saves are untouched.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2 import database, gm_catalog, live_service


class GmMailRC7Tests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path=Path(self.directory.name)/"mail.sqlite3"
        original=database.connect
        self.provider=patch.object(live_service,"_db",lambda: original(self.path,"live"))
        self.provider.start()
        self.addCleanup(self.provider.stop)
        self.db=live_service._db()
        self.db.execute("INSERT INTO worlds(server_id,name,status,created_at) VALUES(?,?,?,?)",
                        ("S1","Test","online",1))
        self.db.commit();self.db.close()
        live_service.register_player("RC7-ADMIN","S1","Admin Test")
        live_service.register_player("RC7-USER","S1","User Test")

    def test_mail_visible_only_to_exact_uid_and_server(self):
        sent=live_service.send_mail("RC7-ADMIN","S1","Admin Test",
            "Gift","Thank you",{"2":100,"930080":50},"TEST")
        self.assertEqual(len(live_service.mailbox("RC7-ADMIN","S1")),1)
        self.assertEqual(live_service.mailbox("RC7-USER","S1"),[])
        self.assertEqual(live_service.mailbox("RC7-ADMIN","S2"),[])
        with self.assertRaises(ValueError):
            live_service.claim_mail(sent["id"],"RC7-USER","S1")
        self.assertEqual(live_service.claim_mail(sent["id"],"RC7-ADMIN","S1"),
                         {"2":100,"930080":50})
        with self.assertRaises(ValueError):
            live_service.claim_mail(sent["id"],"RC7-ADMIN","S1")

    def test_wrong_character_name_rejected(self):
        with self.assertRaises(ValueError):
            live_service.send_mail("RC7-USER","S1","Admin Test",
                "gift","",{"1":10},"TEST")

    def test_claim_rollback_leaves_mail_pending(self):
        sent=live_service.send_mail("RC7-USER","S1","User Test","Gift","",{"1":75},"TEST")
        db=live_service._db()
        try:
            db.execute("BEGIN IMMEDIATE")
            result=live_service.claim_mail(sent["id"],"RC7-USER","S1",db=db)
            self.assertEqual(result,{"1":75})
            db.rollback()
        finally:
            db.close()
        self.assertEqual(live_service.mailbox("RC7-USER","S1")[0]["status"],"pending")

    def test_catalog_only_accepts_real_shards_and_items(self):
        catalog=gm_catalog.catalog()
        self.assertGreater(len(catalog["items"]),100)
        self.assertGreater(len(catalog["shards"]),50)
        test_shard=next(x for x in catalog["shards"] if x["id"]==930080)
        self.assertEqual(test_shard["girl_id"],51003)
        self.assertEqual(test_shard["required"],50)
        self.assertEqual(test_shard["stars"],5)
        self.assertEqual(gm_catalog.validate_gift({"930080":50,"2":100}),{"930080":50,"2":100})
        for invalid in ({"999999999":1},{"2":-1},{"2":0},{"2":"nhiều"},{"2":2000001}):
            with self.subTest(invalid=invalid),self.assertRaises(ValueError):
                gm_catalog.validate_gift(invalid)


if __name__=="__main__":
    unittest.main()
