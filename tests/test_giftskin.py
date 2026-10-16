"""GiftSkin and global account uniqueness regression checks, isolated SQLite only.

Never touches production Neon. The Crystal/Postgres path is additionally
verified by production integration smoke checks after deployment.
"""
import inspect
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2 import auth, database, live_service, skin_store, skin_gifts, skins


class GiftSkinTests(unittest.TestCase):
    def setUp(self):
        if database.is_postgres():
            self.skipTest("GiftSkin unit tests must never modify production Neon")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        old_auth, old_live = auth.DB_PATH, live_service.DB_PATH
        auth.DB_PATH = base / "auth.sqlite3"
        live_service.DB_PATH = base / "live.sqlite3"
        self.addCleanup(lambda: setattr(auth,"DB_PATH",old_auth))
        self.addCleanup(lambda: setattr(live_service,"DB_PATH",old_live))
        old_sets = [set(skin_store._READY),set(skin_gifts._READY)]
        skin_store._READY.clear()
        skin_gifts._READY.clear()
        def restore():
            skin_store._READY.clear()
            skin_store._READY.update(old_sets[0])
            skin_gifts._READY.clear()
            skin_gifts._READY.update(old_sets[1])
        self.addCleanup(restore)
        self.sender = auth.register("GiverUnique", "StrongPass123", "Người tặng", "S1")
        self.recipient = auth.register("ReceiverUnique", "StrongPass123", "Người nhận", "S1")
        self.other = auth.register("OtherUnique", "StrongPass123", "Người khác", "S1")
        self.sid = next(s for s,r in skins.SKINS.items()
                        if not skin_store.is_wedding(s) and r.get("name") and r.get("partners"))
        skin_store.update_configs([{
            "skin_id":self.sid,"enabled":True,"allow_bank":True,"allow_crystal":True,
            "price_vnd":129000,"price_crystal":45,
        }],"TEST")

    def details(self):
        return (self.sender["account"]["uid"], "S1",
                self.recipient["account"]["display_uid"], "Người nhận", "S1", self.sid)

    def test_public_uid_and_duplicate_usernames_never_alias_each_other(self):
        for account in (self.sender,self.recipient,self.other):
            self.assertRegex(account["account"]["display_uid"],r"^GB3-[1-9][0-9]{8}$")
        self.assertEqual(len({
            self.sender["account"]["uid"],
            self.recipient["account"]["uid"],
            self.other["account"]["uid"],
        }), 3)
        with self.assertRaisesRegex(ValueError,"Tên đăng nhập đã tồn tại"):
            auth.register("giverunique","StrongPass123","Other name","S1")
        with self.assertRaisesRegex(ValueError,"Tên đăng nhập đã tồn tại"):
            auth.register("  GIVERUNIQUE ","StrongPass123","Other name","S1")
        db=auth._db()
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM accounts").fetchone()["n"],3)
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM account_public_uids").fetchone()["n"],3)
        db.close()
        self.assertEqual(auth.session(self.sender["token"])["character_name"],"Người tặng")

    def test_uid_generation_collision_rolls_back_not_overwrites(self):
        same_id = int(self.sender["account"]["display_uid"][4:])
        with patch.object(auth.secrets, "randbelow", return_value=same_id-100_000_000):
            with self.assertRaisesRegex(RuntimeError,"duy nhất"):
                auth.register("FourthUnique","StrongPass123","New","S1")
        db=auth._db()
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM accounts").fetchone()["n"],3)
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM account_public_uids").fetchone()["n"],3)
        db.close()

    def test_giftskin_never_accepts_wrong_recipient_or_wedding_costume(self):
        sender,world,uid,name,to_world,sid=self.details()
        r=skin_gifts.view_recipient(sender,uid,name,to_world)
        self.assertEqual(r,{"verified":True,"display_uid":uid,
                            "character_name":"Người nhận","server_id":"S1"})
        self.assertNotIn("uid",r)
        with self.assertRaisesRegex(ValueError,"không khớp"):
            skin_gifts.create_bank(sender,world,uid,"Sai tên",to_world,sid)
        with self.assertRaisesRegex(ValueError,"không khớp"):
            skin_gifts.create_bank(sender,world,uid,name,"S2",sid)
        with self.assertRaisesRegex(ValueError,"tự tặng"):
            skin_gifts.create_bank(sender,world,self.sender["account"]["display_uid"],
                                   "Người tặng",world,sid)
        wedding = next(iter(skin_store.WEDDING_IDS))
        with self.assertRaisesRegex(ValueError,"kết duyên"):
            skin_gifts.create_bank(sender,world,uid,name,to_world,wedding)

    def test_bank_gift_remains_pending_until_super_gm_approval(self):
        receipt=skin_gifts.create_bank(*self.details())
        self.assertEqual(receipt["status"],"pending")
        self.assertEqual(receipt["price_vnd"],129000)
        self.assertEqual(receipt["recipient_public_uid"],self.recipient["account"]["display_uid"])
        self.assertNotIn("recipient_uid",receipt)
        self.assertEqual(skin_gifts.create_bank(*self.details())["id"],receipt["id"])
        db=live_service._db()
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM mail").fetchone()["n"],0)
        db.close()
        approved=skin_gifts.review(receipt["id"],True,"OWNER")
        self.assertEqual(approved["status"],"approved")
        self.assertTrue(approved["mail_id"])
        db=live_service._db()
        mail=db.execute("SELECT * FROM mail WHERE id=?",(approved["mail_id"],)).fetchone()
        db.close()
        self.assertEqual(mail["uid"],self.recipient["account"]["uid"])
        self.assertEqual(mail["server_id"],"S1")
        self.assertEqual(mail["status"],"pending")
        with self.assertRaisesRegex(ValueError,"đã được xử lý"):
            skin_gifts.review(receipt["id"],True,"OWNER")
        self.assertEqual(len(skin_gifts.mine(self.sender["account"]["uid"])["orders"]),1)
        self.assertEqual(len(skin_gifts.mine(self.other["account"]["uid"])["orders"]),0)

    def test_bank_gift_audit_failure_rolls_back_mail_and_review(self):
        receipt=skin_gifts.create_bank(*self.details())
        with patch.object(live_service,"_audit",side_effect=RuntimeError("audit failed")):
            with self.assertRaisesRegex(RuntimeError,"audit failed"):
                skin_gifts.review(receipt["id"],True,"OWNER")
        db=live_service._db()
        self.assertEqual(db.execute("SELECT status FROM skin_gift_bank_orders WHERE id=?",
                        (receipt["id"],)).fetchone()["status"],"pending")
        self.assertEqual(db.execute("SELECT COUNT(*) AS n FROM mail").fetchone()["n"],0)
        db.close()

    def test_crystal_gifts_require_authoritative_postgres_profile_and_mail(self):
        from gxb2.engine import Engine
        source=inspect.getsource(Engine.gift_skin_crystal)
        for clause in ("ScopedPostgresPlayerDB","borrowed_live_transaction",
                       "ensure_crystal_receipts","self._save_profile(state)",
                       "self.db.commit()","self.db.rollback()","request_id"):
            self.assertIn(clause,source)
        self.assertIn("recipient",source)
        self.assertFalse(skin_store.is_wedding(self.sid))


if __name__=="__main__":
    unittest.main()
