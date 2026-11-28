"""Manual bank-transfer Skin orders. Only verified owner approval delivers game mail.

No automatic bank API or receipt verification is claimed. Zalo is contact only.
Orders, audit, and mail delivery use the live server's shared PostgreSQL/SQLite DB.
"""
from __future__ import annotations

import json
import threading
import time
import uuid

from . import live_service, skin_store, skins

_LOCK = threading.RLock()
_READY = set()
ADMIN_ZALO = "0856848557"


def _db():
    db = live_service._db()
    key = (db.backend, db.identity)
    try:
        if key not in _READY:
            with _LOCK:
                if key not in _READY:
                    db.execute("""CREATE TABLE IF NOT EXISTS skin_bank_orders (
                        id TEXT PRIMARY KEY,
                        uid TEXT NOT NULL,
                        server_id TEXT NOT NULL,
                        character_name TEXT NOT NULL,
                        skin_id INTEGER NOT NULL,
                        skin_name TEXT NOT NULL,
                        price_vnd BIGINT NOT NULL,
                        status TEXT NOT NULL,
                        created_at BIGINT NOT NULL,
                        reviewed_at BIGINT,
                        reviewer TEXT,
                        mail_id TEXT
                    )""")
                    db.commit()
                    _READY.add(key)
        return db
    except Exception:
        db.rollback()
        db.close()
        raise


def _view(row):
    data = dict(row)
    data["payment"] = "bank"
    data["zalo_admin"] = ADMIN_ZALO
    return data


def create(uid, server_id, character_name, skin_id, *, already_owned=False):
    try:
        sid = int(skin_id)
    except (TypeError, ValueError):
        raise ValueError("Trang phục không hợp lệ") from None
    if already_owned:
        raise ValueError("Trang phục đã mở khóa vĩnh viễn; không cần đặt mua lại")
    if skin_store.is_wedding(sid):
        raise ValueError("Skin cưới là phần thưởng độc quyền, không được phép bán")
    listing = skin_store.offer(sid)
    if not listing or not listing["is_saleable"] or not listing["enabled"] or not listing["allow_bank"]:
        raise ValueError("Skin chưa được mở bán bằng chuyển khoản ngân hàng")
    price = int(listing["price_vnd"])
    if price <= 0:
        raise ValueError("Giá VNĐ chưa được cấu hình")
    target = live_service.player(uid, server_id)
    if not target or target.get("status") == "banned":
        raise ValueError("Tài khoản không tồn tại hoặc đã bị khóa")
    if str(target["character_name"]).casefold() != str(character_name).casefold():
        raise ValueError("Thông tin nhân vật không khớp tài khoản")
    uid, server_id = str(uid), str(server_id).upper()
    now = int(time.time())
    oid = "SKBANK-" + uuid.uuid4().hex[:16].upper()
    with _LOCK:
        db = _db()
        try:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute("""SELECT * FROM skin_bank_orders
                WHERE uid=? AND server_id=? AND skin_id=? AND status='pending'
                LIMIT 1""",(uid,server_id,sid)).fetchone()
            if existing:
                db.commit()
                return _view(existing)
            outstanding = db.execute("""SELECT COUNT(*) AS n FROM skin_bank_orders
                WHERE uid=? AND server_id=? AND status='pending'""",(uid,server_id)).fetchone()
            if int(outstanding["n"]) >= 5:
                raise ValueError("Bạn đang có quá nhiều đơn chờ duyệt; hãy liên hệ quản trị")
            db.execute("""INSERT INTO skin_bank_orders
                (id,uid,server_id,character_name,skin_id,skin_name,price_vnd,status,created_at)
                VALUES (?,?,?,?,?,?,?,'pending',?)""",
                (oid,uid,server_id,target["character_name"],sid,listing["name"],price,now))
            live_service._audit(db,"skin_bank.create",f"{server_id}:{uid}",
                {"order_id":oid,"skin_id":sid,"price_vnd":price},"PLAYER")
            db.commit()
            return _view(db.execute("SELECT * FROM skin_bank_orders WHERE id=?",(oid,)).fetchone())
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


def mine(uid, server_id):
    db = _db()
    try:
        rows = db.execute("""SELECT * FROM skin_bank_orders
            WHERE uid=? AND server_id=? ORDER BY created_at DESC LIMIT 50""",
            (str(uid),str(server_id).upper())).fetchall()
        return {"orders":[_view(row) for row in rows],"zalo_admin":ADMIN_ZALO}
    finally:
        db.close()


def admin_orders(status="pending"):
    if status not in ("pending","approved","rejected","all"):
        raise ValueError("Trạng thái đơn không hợp lệ")
    db = _db()
    try:
        if status == "all":
            rows = db.execute("SELECT * FROM skin_bank_orders ORDER BY created_at DESC LIMIT 200").fetchall()
        else:
            rows = db.execute("""SELECT * FROM skin_bank_orders
                WHERE status=? ORDER BY created_at DESC LIMIT 200""",(status,)).fetchall()
        return {"orders":[_view(row) for row in rows],"zalo_admin":ADMIN_ZALO}
    finally:
        db.close()


def review(order_id, approve, reviewer):
    """Approval must follow *manual* verification of a real bank transfer."""
    if type(approve) is not bool:
        raise ValueError("Quyết định duyệt đơn không hợp lệ")
    order_id = str(order_id or "").strip()
    with _LOCK:
        db = _db()
        try:
            db.execute("BEGIN IMMEDIATE")
            # Prevent concurrent approvals in PostgreSQL in different workers.
            q = "SELECT * FROM skin_bank_orders WHERE id=?"
            if db.backend == "postgres":
                q += " FOR UPDATE"
            order = db.execute(q,(order_id,)).fetchone()
            if not order:
                raise ValueError("Không tìm thấy đơn Skin")
            if order["status"] != "pending":
                raise ValueError("Đơn đã được xử lý, không thể duyệt lại")
            sid = int(order["skin_id"])
            if sid not in skins.SKINS or skin_store.is_wedding(sid):
                raise ValueError("Skin cưới hoặc dữ liệu không hợp lệ, không được giao")
            mail_id = None
            now = int(time.time())
            if approve:
                # Mail is awarded in the same DB transaction, never before approval.
                mail_id = "MAIL-" + uuid.uuid4().hex[:16].upper()
                items = json.dumps({str(sid):1})
                db.execute("""INSERT INTO mail
                    (id,uid,server_id,character_name,title,body,attachments,status,created_at,operator)
                    VALUES (?,?,?,?,?,?,?,'pending',?,?)""",
                    (mail_id,order["uid"],order["server_id"],order["character_name"],
                     "Trang phục đã thanh toán",
                     f"Đơn {order_id} đã được QTV xác nhận nhận tiền. Nhận trang phục qua thư.",
                     items,now,str(reviewer)))
                live_service._audit(db,"skin_bank.mail",f"{order['server_id']}:{order['uid']}",
                    {"order_id":order_id,"mail_id":mail_id,"skin_id":sid},str(reviewer))
            db.execute("""UPDATE skin_bank_orders
                SET status=?,reviewed_at=?,reviewer=?,mail_id=? WHERE id=?""",
                ("approved" if approve else "rejected",now,str(reviewer),mail_id,order_id))
            live_service._audit(db,"skin_bank.review",f"{order['server_id']}:{order['uid']}",
                {"order_id":order_id,"approved":approve,"skin_id":sid,"price_vnd":int(order["price_vnd"])},
                str(reviewer))
            db.commit()
            return _view(db.execute("SELECT * FROM skin_bank_orders WHERE id=?",(order_id,)).fetchone())
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
