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
        self.db.execute("INSERT INTO worlds(server_id,name,status,created_at) VALUES(?,?,?,?) ON CONFLICT(server_id) DO NOTHING",
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

    def test_approved_paid_package_issues_vip_exp_to_correct_mail_only_once(self):
        from gxb2 import vip
        official_pack={
            "id":"MONTHLY_CARD", "name":"Thẻ Tháng",
            "price_label":"QTV xác nhận giá", "manual_reward":False,
            "reward":{vip.VIP_EXP_REWARD_ID:150}, "enabled":True,
        }
        with patch.object(live_service.topup,"package",return_value=official_pack):
            created=live_service.create_order("RC7-USER","S1","User Test","MONTHLY_CARD")
        self.assertEqual(live_service.mailbox("RC7-USER","S1"),[])
        live_service.review_order(created["id"],True,reviewer="TEST_GM")
        self.assertEqual(live_service.mailbox("RC7-ADMIN","S1"),[])
        pending=live_service.mailbox("RC7-USER","S1")
        self.assertEqual(len(pending),1)
        with self.assertRaises(ValueError):
            live_service.claim_mail(pending[0]["id"],"RC7-ADMIN","S1")
        contents=live_service.claim_mail(pending[0]["id"],"RC7-USER","S1")
        account={"items":{"1":0}}
        self.assertEqual(vip.claim_reward(account,contents),150)
        self.assertEqual(account["vip_paid_exp"],150)
        self.assertNotIn(vip.VIP_EXP_REWARD_ID,contents)
        with self.assertRaises(ValueError):
            live_service.claim_mail(pending[0]["id"],"RC7-USER","S1")

    def test_manually_fulfilled_weekly_card_includes_original_vip_exp(self):
        from gxb2 import vip
        pack={"id":"WEEKLY_CARD","name":"Thẻ Tuần","price_label":"QTV xác nhận",
              "manual_reward":True,"reward":{vip.VIP_EXP_REWARD_ID:50},"enabled":True}
        with patch.object(live_service.topup,"package",return_value=pack):
            placed=live_service.create_order("RC7-USER","S1","User Test","WEEKLY_CARD")
        with self.assertRaises(ValueError):
            live_service.review_order(placed["id"],True,{},reviewer="TEST_GM")
        self.assertEqual(live_service.order(placed["id"])["status"],"pending")
        live_service.review_order(placed["id"],True,{"2":120},reviewer="TEST_GM")
        mails=live_service.mailbox("RC7-USER","S1")
        self.assertEqual(len(mails),1)
        self.assertEqual(mails[0]["attachments"],{"2":120,vip.VIP_EXP_REWARD_ID:50})
        self.assertEqual(live_service.mailbox("RC7-ADMIN","S1"),[])

    def test_failed_mail_insert_does_not_approve_paid_order(self):
        from gxb2 import vip
        pack={"id":"MONTHLY_CARD","name":"Thẻ Tháng","price_label":"QTV xác nhận",
              "manual_reward":False,"reward":{vip.VIP_EXP_REWARD_ID:100},"enabled":True}
        with patch.object(live_service.topup,"package",return_value=pack):
            placed=live_service.create_order("RC7-USER","S1","User Test","MONTHLY_CARD")
        db=live_service._db()
        try:
            db.execute("""CREATE TRIGGER reject_paid_mail BEFORE INSERT ON mail
                          BEGIN SELECT RAISE(ABORT, 'simulated mail insert failure'); END""")
            db.commit()
        finally:
            db.close()
        with self.assertRaises(Exception):
            live_service.review_order(placed["id"],True,reviewer="TEST_GM")
        self.assertEqual(live_service.order(placed["id"])["status"],"pending")
        self.assertEqual(live_service.mailbox("RC7-USER","S1"),[])

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
