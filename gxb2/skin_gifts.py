"""GXB3 GiftSkin: authenticated recipient verification, manual bank gifts, receipt ledger.

All production money and rewards live in PostgreSQL. Never write a player's
balance in this module: Crystal gifts execute only within Engine's one shared
Postgres player-profile/mail transaction.
"""
from __future__ import annotations

import json
import re
import threading
import time
import uuid

from . import auth, live_service, skin_store

_LOCK = threading.RLock()
_READY = set()
ADMIN_ZALO = "0856848557"
REQUEST_RE = re.compile(r"^GSK-[a-f0-9]{32}$")


def _db():
    db = live_service._db()
    key = (db.backend, db.identity)
    try:
        if key not in _READY:
            with _LOCK:
                if key not in _READY:
                    db.execute("""CREATE TABLE IF NOT EXISTS skin_gift_bank_orders (
                        id TEXT PRIMARY KEY,
                        sender_uid TEXT NOT NULL,
                        sender_server TEXT NOT NULL,
                        recipient_uid TEXT NOT NULL,
                        recipient_server TEXT NOT NULL,
                        recipient_name TEXT NOT NULL,
                        recipient_public_uid TEXT NOT NULL,
                        skin_id INTEGER NOT NULL,
                        skin_name TEXT NOT NULL,
                        price_vnd BIGINT NOT NULL,
                        status TEXT NOT NULL,
                        created_at BIGINT NOT NULL,
                        reviewed_at BIGINT,
                        reviewer TEXT,
                        mail_id TEXT
                    )""")
                    db.execute("""CREATE UNIQUE INDEX IF NOT EXISTS skin_gift_bank_pending_unique
                      ON skin_gift_bank_orders(sender_uid,sender_server,recipient_uid,recipient_server,skin_id)
                      WHERE status='pending'""")
                    db.commit()
                    _READY.add(key)
        return db
    except Exception:
        db.rollback()
        db.close()
        raise


def ensure_crystal_receipts(db):
    """Run inside the existing authoritative player transaction; caller commits."""
    db.execute("""CREATE TABLE IF NOT EXISTS skin_gift_crystal_receipts (
        request_id TEXT PRIMARY KEY,
        sender_uid TEXT NOT NULL,
        sender_server TEXT NOT NULL,
        recipient_uid TEXT NOT NULL,
        recipient_server TEXT NOT NULL,
        recipient_public_uid TEXT NOT NULL,
        recipient_name TEXT NOT NULL,
        skin_id INTEGER NOT NULL,
        price_crystal BIGINT NOT NULL,
        mail_id TEXT NOT NULL UNIQUE,
        created_at BIGINT NOT NULL
    )""")


def verify(sender_uid, recipient_uid, recipient_name, recipient_server):
    match = auth.verify_gift_recipient(recipient_uid, recipient_name,
                                      recipient_server, sender_uid)
    return match


def listing_for(skin_id, payment):
    try:
        sid = int(skin_id)
    except (ValueError, TypeError):
        raise ValueError("Trang phục không hợp lệ") from None
    if skin_store.is_wedding(sid):
        raise ValueError("Trang phục kết duyên không được bán hoặc tặng qua GiftSkin")
    item = skin_store.offer(sid)
    if not item or not item["enabled"] or not item["is_saleable"]:
        raise ValueError("Trang phục chưa được mở bán")
    if payment == "crystal":
        allowed, cost = "allow_crystal", "price_crystal"
    elif payment == "bank":
        allowed, cost = "allow_bank", "price_vnd"
    else:
        raise ValueError("Chỉ nhận Crystal hoặc chuyển khoản VNĐ")
    if not item[allowed] or int(item[cost]) <= 0:
        raise ValueError("Phương thức thanh toán chưa được mở")
    return item, int(item[cost])



def recipient_has_skin(db, uid, server_id, skin_id):
    """Lock Neon profile and check inventory, worn skins, collection and pending mail."""
    try:
        sid = int(skin_id)
    except (TypeError, ValueError):
        raise ValueError("ID trang phục không hợp lệ") from None

    backend = getattr(db, "backend", "")
    if backend not in ("postgres", "sqlite"):
        raise ValueError("Không thể xác minh cơ sở dữ liệu người nhận")

    profile_sql = """SELECT data FROM player_profiles
        WHERE uid=? AND server_id=?"""
    if backend == "postgres":
        profile_sql += " FOR UPDATE"
    row = db.execute(
        profile_sql, (str(uid), str(server_id).upper())
    ).fetchone()
    if not row:
        raise ValueError("Hồ sơ Neon người nhận chưa sẵn sàng; chưa giao quà")

    try:
        state = json.loads(row["data"])
        if not isinstance(state, dict):
            raise ValueError("Dữ liệu hồ sơ không hợp lệ")
        from . import skins as native_skins
        if sid in native_skins.collected(state):
            return True
    except Exception as exc:
        raise ValueError("Không thể xác minh bộ sưu tập người nhận; chưa giao quà") from exc

    messages = db.execute(
        """SELECT attachments FROM mail
           WHERE uid=? AND server_id=? AND status='pending'""",
        (str(uid), str(server_id).upper())
    ).fetchall()

    for message in messages:
        try:
            attachments = message["attachments"]
            if isinstance(attachments, str):
                attachments = json.loads(attachments)
            if not isinstance(attachments, dict):
                raise ValueError("Định dạng vật phẩm trong thư không hợp lệ")
            if int(attachments.get(str(sid), 0) or 0) > 0:
                return True
        except Exception as exc:
            raise ValueError("Không thể xác minh thư đang chờ của người nhận; chưa giao quà") from exc

    return False

def view_recipient(sender_uid, recipient_uid, recipient_name, recipient_server):
    result = verify(sender_uid, recipient_uid, recipient_name, recipient_server)
    # Do not expose the recipient's internal wallet/game UID to the browser.
    return {"verified": True, "display_uid": result["display_uid"],
            "character_name": result["character_name"], "server_id": result["server_id"]}


def create_bank(sender_uid, sender_server, recipient_uid, recipient_name, recipient_server, skin_id):
    sender_uid = str(sender_uid or "")
    sender_server = str(sender_server or "").upper()
    sender = live_service.player(sender_uid, sender_server)
    if not sender or sender.get("status") != "active":
        raise ValueError("Phiên người tặng không hợp lệ")
    target = verify(sender_uid, recipient_uid, recipient_name, recipient_server)
    item, price = listing_for(skin_id, "bank")
    sid = item["skin_id"]
    now = int(time.time())
    oid = "GSKBANK-" + uuid.uuid4().hex[:16].upper()
    with _LOCK:
        db = _db()
        try:
            db.execute("BEGIN IMMEDIATE")
            already_owned = recipient_has_skin(
                db, target["uid"], target["server_id"], sid
            )
            existing = db.execute("""SELECT * FROM skin_gift_bank_orders
                WHERE sender_uid=? AND sender_server=? AND recipient_uid=?
                  AND recipient_server=? AND skin_id=? AND status='pending'""",
                (sender_uid, sender_server, target["uid"], target["server_id"], sid)).fetchone()
            if existing:
                if already_owned:
                    db.execute("""UPDATE skin_gift_bank_orders
                        SET status='rejected',reviewed_at=?,reviewer=?,mail_id=NULL
                        WHERE id=? AND status='pending'""",
                        (now, "SYSTEM_GIFTSKIN", existing["id"]))
                    live_service._audit(db, "giftskin.bank.auto_reject",
                        str(existing["id"]),
                        {"reason":"recipient_already_owns_skin","skin_id":sid},
                        "SYSTEM_GIFTSKIN")
                    db.commit()
                    updated = db.execute(
                        "SELECT * FROM skin_gift_bank_orders WHERE id=?",
                        (existing["id"],)
                    ).fetchone()
                    return _bank_view(updated)
                db.commit()
                return _bank_view(existing)
            if already_owned:
                raise ValueError("Người nhận đã sở hữu trang phục này; không thể tạo đơn tặng")
            outstanding = db.execute("""SELECT COUNT(*) AS n FROM skin_gift_bank_orders
                WHERE sender_uid=? AND status='pending'""", (sender_uid,)).fetchone()
            if int(outstanding["n"]) >= 5:
                raise ValueError("Bạn đang có 5 đơn tặng chưa được duyệt")
            db.execute("""INSERT INTO skin_gift_bank_orders
                (id,sender_uid,sender_server,recipient_uid,recipient_server,recipient_name,
                 recipient_public_uid,skin_id,skin_name,price_vnd,status,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,'pending',?)""",
                (oid,sender_uid,sender_server,target["uid"],target["server_id"],
                 target["character_name"],target["display_uid"],sid,item["name"],price,now))
            live_service._audit(db,"giftskin.bank.create",f"{sender_server}:{sender_uid}",
                {"order_id":oid,"recipient_uid":target["display_uid"],"skin_id":sid,"price_vnd":price},"PLAYER")
            db.commit()
            return _bank_view(db.execute("SELECT * FROM skin_gift_bank_orders WHERE id=?",(oid,)).fetchone())
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


def _bank_view(row):
    result = dict(row)
    # Canonical internal IDs must not leak through public GiftSkin lists.
    result.pop("recipient_uid",None)
    result["payment"] = "bank"
    result["zalo_admin"] = ADMIN_ZALO
    return result


def mine(sender_uid):
    db = _db()
    try:
        rows = db.execute("""SELECT * FROM skin_gift_bank_orders
            WHERE sender_uid=? ORDER BY created_at DESC LIMIT 60""",(str(sender_uid),)).fetchall()
        return {"orders":[_bank_view(r) for r in rows], "zalo_admin":ADMIN_ZALO}
    finally:
        db.close()


def admin_orders(status="pending"):
    if status not in ("pending","approved","rejected","all"):
        raise ValueError("Trạng thái đơn không hợp lệ")
    db = _db()
    try:
        if status == "all":
            rows = db.execute("SELECT * FROM skin_gift_bank_orders ORDER BY created_at DESC LIMIT 200").fetchall()
        else:
            rows = db.execute("""SELECT * FROM skin_gift_bank_orders WHERE status=?
                ORDER BY created_at DESC LIMIT 200""",(status,)).fetchall()
        return {"orders":[dict(x) for x in rows],"zalo_admin":ADMIN_ZALO}
    finally:
        db.close()


def review(order_id, approve, reviewer):
    if type(approve) is not bool:
        raise ValueError("Quyết định duyệt đơn không hợp lệ")
    with _LOCK:
        db = _db()
        try:
            db.execute("BEGIN IMMEDIATE")
            query = "SELECT * FROM skin_gift_bank_orders WHERE id=?"
            if db.backend == "postgres":
                query += " FOR UPDATE"
            row = db.execute(query,(str(order_id or ""),)).fetchone()
            if not row:
                raise ValueError("Không tìm thấy đơn GiftSkin")
            if row["status"] != "pending":
                raise ValueError("Đơn GiftSkin đã được xử lý")
            if skin_store.is_wedding(row["skin_id"]):
                raise ValueError("Skin kết duyên tuyệt đối không được giao")
            mail_id = None
            now = int(time.time())
            if approve:
                # Recheck recipient's world status before mailing, using DB snapshot.
                player = db.execute("""SELECT status,character_name FROM players
                    WHERE uid=? AND server_id=?""",(row["recipient_uid"],row["recipient_server"])).fetchone()
                if not player or player["status"] != "active" or player["character_name"] != row["recipient_name"]:
                    raise ValueError("Người nhận không còn hợp lệ; chưa giao quà")
                if recipient_has_skin(db, row["recipient_uid"], row["recipient_server"], row["skin_id"]):
                    approve = False
                    live_service._audit(db, "giftskin.bank.auto_reject", str(row["id"]),
                        {"reason":"recipient_already_owns_skin","skin_id":int(row["skin_id"])},
                        str(reviewer))
                if approve:
                    mail_id = "MAIL-" + uuid.uuid4().hex[:16].upper()
                    db.execute("""INSERT INTO mail
                        (id,uid,server_id,character_name,title,body,attachments,status,created_at,operator)
                        VALUES (?,?,?,?,?,?,?,'pending',?,?)""",
                        (mail_id,row["recipient_uid"],row["recipient_server"],row["recipient_name"],
                         "Quà GiftSkin từ người chơi",
                         "Đơn "+str(row["id"])+" đã được quản trị xác nhận thanh toán. Nhận trang phục trong thư.",
                         json.dumps({str(row["skin_id"]):1}),now,"GIFTSKIN_BANK"))
                    live_service._audit(db,"giftskin.bank.mail",f"{row['recipient_server']}:{row['recipient_uid']}",
                        {"order_id":row["id"],"mail_id":mail_id,"skin_id":row["skin_id"]},str(reviewer))
            db.execute("""UPDATE skin_gift_bank_orders
                SET status=?,reviewed_at=?,reviewer=?,mail_id=? WHERE id=?""",
                ("approved" if approve else "rejected",now,str(reviewer),mail_id,row["id"]))
            live_service._audit(db,"giftskin.bank.review",str(row["id"]),
                {"approve":approve,"mail_id":mail_id,"recipient":row["recipient_public_uid"]},str(reviewer))
            db.commit()
            return _bank_view(db.execute("SELECT * FROM skin_gift_bank_orders WHERE id=?",(row["id"],)).fetchone())
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
