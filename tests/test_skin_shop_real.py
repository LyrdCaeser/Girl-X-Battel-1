"""Skin Shop: VNĐ bank orders are manual; Crystal debits real wallet; wedding skins never sold."""
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2 import database, live_service, skin_store, skin_bank, skins, giftcodes


class SkinShopTests(unittest.TestCase):
    def setUp(self):
        if database.is_postgres():
            self.skipTest("Only isolated SQLite tests; never mutate production PostgreSQL")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        path = Path(self.tmp.name) / "skin-shop-test.sqlite3"
        self.path = path
        real_connect = database.connect
        p = patch.object(live_service, "_db", lambda: real_connect(path, "live"))
        p.start()
        self.addCleanup(p.stop)
        old_store, old_bank = set(skin_store._READY), set(skin_bank._READY)
        skin_store._READY.clear()
        skin_bank._READY.clear()
        def clean():
            skin_store._READY.clear(); skin_store._READY.update(old_store)
            skin_bank._READY.clear(); skin_bank._READY.update(old_bank)
        self.addCleanup(clean)
        self.normal = next(sid for sid, s in skins.SKINS.items()
                           if not skin_store.is_wedding(sid) and s.get("shop"))
        self.exclusive = next(iter(sorted(skin_store.WEDDING_IDS)))
        db = live_service._db()
        db.execute("""INSERT INTO players(uid,server_id,character_name,created_at,updated_at)
                      VALUES(?,?,?,?,?)""", ("USER1","S1","Nhân vật 1",int(time.time()),int(time.time())))
        db.commit()
        db.close()

    def config(self, sid=None, **changes):
        row = dict(skin_id=self.normal if sid is None else sid, enabled=True,
                   allow_bank=True, allow_crystal=True, price_vnd=65000, price_crystal=20)
        row.update(changes)
        return row

    def test_full_catalog_wedding_exclusive_and_placeholders(self):
        rows = skin_store.catalogue(admin=True)["offers"]
        self.assertEqual(len(rows), len(skins.SKINS))
        self.assertEqual(sum(x["is_wedding"] for x in rows), len(skin_store.WEDDING_IDS))
        self.assertEqual(len(skin_store.WEDDING_IDS), 45)
        self.assertFalse(any(x["is_wedding"] for x in skin_store.catalogue()["offers"]))
        self.assertEqual(sum(r["is_saleable"] for r in rows), 279)
        for sid in skin_store.WEDDING_IDS:
            with self.assertRaisesRegex(ValueError, "cưới"):
                skin_store.update_configs([self.config(sid, is_wedding=False)],"OWNER")
            for kind in ("gold","bank","crystal","ticket"):
                with self.assertRaisesRegex(ValueError, "cưới"):
                    skin_store.purchase({"items":{"1":99999,"2":99999,"74":99999},"partners":[]},sid,kind)
        for row in rows:
            if not row["is_saleable"] and not row["is_wedding"]:
                with self.assertRaises(ValueError):
                    skin_store.update_configs([self.config(row["skin_id"])],"OWNER")

    def test_crystal_purchase_and_gold_no_longer_usable(self):
        skin_store.update_configs([self.config()],"OWNER")
        state={"items":{"1":10000,"2":90,"74":300},"partners":[]}
        before=dict(state["items"])
        for kind in ("gold","ticket","bank"):
            with self.assertRaisesRegex(ValueError, "Phương thức|Chuyển khoản"):
                skins.action(state,{"action":"buy","skin":self.normal,"payment":kind})
        self.assertEqual(state["items"],before)
        result=skins.action(state,{"action":"buy","skin":self.normal,"payment":"crystal"})
        self.assertEqual(result["got"],{str(self.normal):1})
        self.assertEqual(state["items"]["2"],70)
        self.assertEqual(state["items"]["1"],before["1"])
        self.assertEqual(state["skin_shop_purchases"][-1]["currency"],"crystal")
        self.assertTrue(any(x["action"]=="skin_shop.update" for x in live_service.audit()))

    def test_bank_order_is_pending_not_free_skin(self):
        skin_store.update_configs([self.config()],"OWNER")
        order=skin_bank.create("USER1","S1","Nhân vật 1",self.normal)
        self.assertEqual(order["status"],"pending")
        self.assertEqual(order["price_vnd"],65000)
        self.assertEqual(order["zalo_admin"],"0856848557")
        self.assertEqual(len(skin_bank.mine("USER1","S1")["orders"]),1)
        self.assertEqual(skin_bank.create("USER1","S1","Nhân vật 1",self.normal)["id"],order["id"])
        with self.assertRaisesRegex(ValueError,"cưới"):
            skin_bank.create("USER1","S1","Nhân vật 1",self.exclusive)
        with self.assertRaisesRegex(ValueError,"không tồn tại"):
            skin_bank.create("MISSING","S1","A",self.normal)
        db=live_service._db()
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM mail").fetchone()["n"],0)
        db.close()

    def test_bank_review_single_use_atomic_mail_delivery(self):
        skin_store.update_configs([self.config()],"OWNER")
        order=skin_bank.create("USER1","S1","Nhân vật 1",self.normal)
        with self.assertRaisesRegex(ValueError,"Quyết định"):
            skin_bank.review(order["id"],"true","OWNER")
        approved=skin_bank.review(order["id"],True,"OWNER")
        self.assertEqual(approved["status"],"approved")
        self.assertTrue(approved["mail_id"])
        with self.assertRaisesRegex(ValueError,"đã được xử lý"):
            skin_bank.review(order["id"],True,"OWNER")
        db=live_service._db()
        row=db.execute("SELECT * FROM mail WHERE id=?",(approved["mail_id"],)).fetchone()
        db.close()
        import json
        self.assertEqual(json.loads(row["attachments"]),{str(self.normal):1})
        self.assertEqual(row["status"],"pending")
        self.assertEqual(row["uid"],"USER1")
        # Rejected orders never deliver a mail.
        other=next(sid for sid,s in skins.SKINS.items()
                   if sid!=self.normal and not skin_store.is_wedding(sid) and s.get("partners") and s.get("name"))
        skin_store.update_configs([self.config(other)],"OWNER")
        reject=skin_bank.create("USER1","S1","Nhân vật 1",other)
        self.assertEqual(skin_bank.review(reject["id"],False,"OWNER")["status"],"rejected")
        self.assertIsNone(skin_bank.admin_orders("rejected")["orders"][0]["mail_id"])

    def test_prices_disabled_and_atomic_admin_update(self):
        initial=skin_store.offer(self.normal)
        with self.assertRaisesRegex(ValueError,"cưới"):
            skin_store.update_configs([self.config(),self.config(self.exclusive)],"OWNER")
        self.assertEqual(skin_store.offer(self.normal),initial)
        for invalid in (1.2,True,False,-1,"8.3","2e5",None,[],{}):
            with self.subTest(price=repr(invalid)):
                with self.assertRaisesRegex(ValueError,"Giá"):
                    skin_store.update_configs([self.config(price_vnd=invalid)],"OWNER")
        with self.assertRaisesRegex(ValueError,"lớn hơn"):
            skin_store.update_configs([self.config(price_vnd=0)],"OWNER")
        with self.assertRaisesRegex(ValueError,"true hoặc false"):
            skin_store.update_configs([self.config(allow_bank="true")],"OWNER")
        with self.assertRaisesRegex(ValueError,"ngân hàng"):
            skin_store.update_configs([self.config(allow_gold=True)],"OWNER")
        skin_store.update_configs([self.config(price_vnd="65000",price_crystal="20")],"OWNER")
        self.assertEqual(skin_store.offer(self.normal)["price_vnd"],65000)
        skin_store.update_configs([self.config(enabled=False)],"OWNER")
        with self.assertRaisesRegex(ValueError,"mở bán"):
            skin_bank.create("USER1","S1","Nhân vật 1",self.normal)

    def test_protected_routes_and_giftcode_uniqueness(self):
        import inspect
        from server import HTTPHandler
        post=inspect.getsource(HTTPHandler.do_POST)
        get=inspect.getsource(HTTPHandler.do_GET)
        self.assertIn("skin_bank.create",post)
        self.assertIn("skin_bank.review",post)
        self.assertIn("self.gm_key_authorized()",post)
        self.assertIn("studio_sso.authorized",post)
        self.assertIn("self.engine.skins_action(data)",post)
        self.assertIn("skin_bank.mine",get)
        self.assertIn("skin_bank.admin_orders",get)
        self.assertIn("skin_store.catalogue(admin=True)",get)
        self.assertIn("giftcodes.exists(code)",get)


if __name__ == "__main__":
    unittest.main()
