"""Skin Shop release tests: isolated SQLite, immutable source wedding flags, real wallet mutations."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2 import database, live_service, skin_store, skins, giftcodes


class SkinShopTests(unittest.TestCase):
    def setUp(self):
        if database.is_postgres():
            self.skipTest("Only isolated SQLite tests; never touch production PostgreSQL")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        path = Path(self.tmp.name) / "skin-shop-test.sqlite3"
        connect = database.connect
        p = patch.object(live_service, "_db", lambda: connect(path, "live"))
        p.start()
        self.addCleanup(p.stop)
        original = set(skin_store._READY)
        skin_store._READY.clear()
        self.addCleanup(lambda: (skin_store._READY.clear(), skin_store._READY.update(original)))
        self.normal = next(sid for sid, s in skins.SKINS.items() if not skin_store.is_wedding(sid) and s.get("shop"))
        self.exclusive = next(iter(sorted(skin_store.WEDDING_IDS)))

    def config(self, sid=None, **changes):
        sid = self.normal if sid is None else sid
        r = dict(skin_id=sid, enabled=True, allow_gold=True, allow_crystal=True,
                 allow_ticket=False, price_gold=300, price_crystal=20)
        r.update(changes)
        return r

    def test_full_publisher_catalog_and_immutable_marriage_source(self):
        all_rows = skin_store.catalogue(admin=True)["offers"]
        self.assertEqual(len(all_rows), len(skins.SKINS))
        self.assertEqual(sum(x["is_wedding"] for x in all_rows), len(skin_store.WEDDING_IDS))
        self.assertEqual(len(skin_store.WEDDING_IDS), 45)
        self.assertFalse(any(x["is_wedding"] for x in skin_store.catalogue()["offers"]))
        for sid in skin_store.WEDDING_IDS:
            self.assertFalse(skin_store.offer(sid))
            with self.assertRaisesRegex(ValueError, "cưới"):
                skin_store.update_configs([self.config(sid, is_wedding=False)], "OWNER")
            for kind in ("gold", "crystal", "ticket"):
                with self.assertRaisesRegex(ValueError, "cưới"):
                    skin_store.purchase({"items": {"1":99999,"2":99999,"74":99999},
                                         "partners":[]}, sid, kind)

    def test_gold_crystal_wallet_real_purchase_and_audit(self):
        skin_store.update_configs([self.config()], "OWNER")
        state = {"items": {"1":1000,"2":200,"74":10}, "partners":[]}
        got = skins.action(state, {"action":"buy","skin":self.normal,"payment":"gold"})
        self.assertEqual(got["got"], {str(self.normal):1})
        self.assertEqual(state["items"]["1"], 700)
        self.assertEqual(state["items"][str(self.normal)], 1)
        self.assertEqual(state["skin_shop_purchases"][-1]["currency"], "gold")
        skins.action(state, {"action":"buy","skin":self.normal,"payment":"crystal"})
        self.assertEqual(state["items"]["2"], 180)
        self.assertEqual(state["items"][str(self.normal)], 2)
        rows = live_service.audit()
        self.assertTrue(any(row["action"]=="skin_shop.update" for row in rows))

    def test_disabled_invalid_currency_insufficient_and_no_negative_balances(self):
        skin_store.update_configs([self.config(enabled=False)], "OWNER")
        state = {"items":{"1":100,"2":30,"74":5}, "partners":[]}
        before = dict(state["items"])
        for kind in ("gold", "crystal", "ticket"):
            with self.assertRaises(ValueError):
                skins.action(state, {"action":"buy","skin":self.normal,"payment":kind})
        self.assertEqual(state["items"], before)
        skin_store.update_configs([self.config()], "OWNER")
        with self.assertRaisesRegex(ValueError, "Không đủ"):
            skins.action(state, {"action":"buy","skin":self.normal,"payment":"gold"})
        with self.assertRaisesRegex(ValueError, "Phương thức"):
            skins.action(state, {"action":"buy","skin":self.normal,"payment":"ticket"})
        self.assertEqual(state["items"], before)

    def test_ticket_purchase_remains_compatible_and_admin_can_disable(self):
        first = skin_store.offer(self.normal)
        self.assertTrue(first["enabled"])
        self.assertTrue(first["allow_ticket"])
        self.assertGreater(first["price_ticket"], 0)
        state = {"items":{"74":first["price_ticket"],"1":0,"2":0}, "partners":[]}
        skins.action(state, {"action":"buy","skin":self.normal})
        self.assertEqual(state["items"]["74"], 0)
        skin_store.update_configs([self.config(allow_gold=False, allow_crystal=False,
                                               allow_ticket=False,enabled=False)], "OWNER")
        with self.assertRaises(ValueError):
            skins.action(state, {"action":"buy","skin":self.normal})

    def test_invalid_update_is_atomic_and_rejects_client_wedding_override(self):
        before = skin_store.offer(self.normal)
        with self.assertRaisesRegex(ValueError, "cưới"):
            skin_store.update_configs([self.config(), self.config(self.exclusive, is_wedding=False)], "OWNER")
        self.assertEqual(skin_store.offer(self.normal), before)
        with self.assertRaisesRegex(ValueError,"lớn hơn"):
            skin_store.update_configs([self.config(price_gold=0)], "OWNER")
        with self.assertRaisesRegex(ValueError,"true hoặc false"):
            skin_store.update_configs([self.config(enabled="true")], "OWNER")

    def test_server_admin_checks_and_giftcode_uniqueness(self):
        import inspect
        from server import HTTPHandler
        post = inspect.getsource(HTTPHandler.do_POST)
        self.assertIn("path.startswith('/api/skin-shop/admin/')",post)
        self.assertIn("self.admin_authorized()",post)
        self.assertIn("self.gm_key_authorized()",post)
        self.assertIn("studio_sso.authorized",post)
        self.assertIn("skin_store.update_configs",post)
        self.assertIn("self.engine.skins_action(data)",post)
        src = inspect.getsource(HTTPHandler.do_GET)
        self.assertIn("skin_store.catalogue(admin=True)",src)
        self.assertIn("giftcodes.exists(code)",src)


if __name__ == "__main__":
    unittest.main()
