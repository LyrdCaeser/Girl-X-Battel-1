"""Strictly S4-only, audited GM character removal with in-transaction archive.

A normal account, S1/S2/S3 profiles, VIP15 entitlement, giftcode history and
payment history are never deleted here. The actual destructive operation
requires a fresh one-time server challenge and an exact character-name match.
"""
from __future__ import annotations

import json
import secrets
import threading
import time

from . import live_service

WORLD = "S4"
PREVIEW_TTL = 120
MAX_ARCHIVE_BYTES = 32 * 1024 * 1024
_lock = threading.RLock()
_challenges = {}

# All of these tables are owned by a UID+world and their rows are archived
# before removal. The worlds table, account records and financial ledgers are
# intentionally not touched.
SCOPED_TABLES = (
    "players", "player_profiles", "player_battles", "mail", "presence",
    "leaderboard", "pvp_queue", "pvp_ratings", "pvp_season_claims",
)

# Never silently break somebody else's active social/guild relationship or
# live battle. Require the GM to resolve these first.
BLOCKERS = (
    ("Đơn nạp chưa kết thúc", "orders",
        "uid=? AND server_id=? AND status NOT IN ('approved','rejected','cancelled','canceled','completed','expired')",
        ("uid", "server")),
    ("Thành viên Bang Hội", "world_guild_members", "uid=? AND server_id=?", ("uid", "server")),
    ("Chủ Bang Hội", "world_guilds", "owner_uid=? AND server_id=?", ("uid", "server")),
    ("Đơn xin vào Bang Hội", "world_guild_applications", "uid=? AND server_id=?", ("uid", "server")),
    ("Kết hôn", "player_marriages", "(uid_a=? OR uid_b=?) AND server_id=?", ("uid", "uid", "server")),
    ("Bạn bè", "friendships", "(uid_a=? OR uid_b=?) AND server_id=?", ("uid", "uid", "server")),
    ("Lời mời kết bạn", "friend_requests", "(requester_uid=? OR recipient_uid=?) AND server_id=?", ("uid", "uid", "server")),
    ("Trận PvP chưa kết thúc", "pvp_matches",
        "(player_a=? OR player_b=?) AND server_id=? AND status NOT IN ('resolved','completed','cancelled','expired')",
        ("uid", "uid", "server")),
)


def _uid(value):
    value=str(value or "").strip()
    if not value or len(value)>64 or any(ord(c)<33 for c in value):
        raise ValueError("UID nhân vật S4 không hợp lệ")
    return value


def _exists(db, table):
    # Literal known table names only, never a caller-controlled SQL identifier.
    if db.backend == "postgres":
        return bool(db.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_schema=current_schema() AND table_name=?",
            (table,)).fetchone())
    return bool(db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table,)).fetchone())


def _blockers(db, uid):
    result=[]
    for label,table,where,params in BLOCKERS:
        if not _exists(db,table):
            continue
        args=tuple(uid if field=="uid" else WORLD for field in params)
        row=db.execute(f"SELECT COUNT(*) AS n FROM {table} WHERE {where}",args).fetchone()
        if int(row["n"]):
            result.append({"reason":label,"count":int(row["n"])})
    return result


def _character(db, uid, lock=False):
    sql="SELECT uid,server_id,character_name,status,created_at FROM players WHERE uid=? AND server_id=?"
    if lock and db.backend=="postgres":
        sql+=" FOR UPDATE"
    row=db.execute(sql,(uid,WORLD)).fetchone()
    return dict(row) if row else None


def _counts(db, uid):
    result={}
    for table in SCOPED_TABLES:
        if _exists(db,table):
            row=db.execute(f"SELECT COUNT(*) AS n FROM {table} WHERE uid=? AND server_id=?",
                           (uid,WORLD)).fetchone()
            result[table]=int(row["n"])
    return result


def preview(uid):
    """Read-only preview. No production character is changed by this action."""
    uid=_uid(uid)
    db=live_service._db()
    try:
        char=_character(db,uid)
        if not char:
            raise ValueError("Không tìm thấy nhân vật của UID này tại S4")
        blockers=_blockers(db,uid)
        counts=_counts(db,uid)
        result={
            "uid":uid,"server_id":WORLD,
            "character_name":char["character_name"],
            "created_at":int(char["created_at"]),
            "counts":counts,"blockers":blockers,"can_delete":not bool(blockers),
            "notice":("Chỉ xóa nhân vật và dữ liệu S4. Tài khoản, VIP 15, "
                      "chìa khóa S4, nhân vật S1–S3 và lịch sử nạp được giữ nguyên. "
                      "Hồ sơ S4 được lưu bản sao trước khi xóa."),
        }
    finally:
        db.close()
    if not blockers:
        with _lock:
            now=time.time()
            for key, row in list(_challenges.items()):
                if row["expires"] < now:
                    _challenges.pop(key,None)
            token=secrets.token_urlsafe(24)
            _challenges[token]={
                "uid":uid,"character_name":char["character_name"],
                "created_at":int(char["created_at"]),"expires":now+PREVIEW_TTL,
            }
        result["nonce"]=token
        result["expires_in_seconds"]=PREVIEW_TTL
    return result


def _capture(db, uid):
    snapshot={}
    for table in SCOPED_TABLES:
        if not _exists(db,table):
            continue
        rows=db.execute(f"SELECT * FROM {table} WHERE uid=? AND server_id=?",
                        (uid,WORLD)).fetchall()
        snapshot[table]=[dict(row) for row in rows]
    # Store a full, portable snapshot in Neon before any DELETE.
    raw=json.dumps(snapshot,ensure_ascii=False,separators=(",",":"),default=str)
    if len(raw.encode("utf-8"))>MAX_ARCHIVE_BYTES:
        raise ValueError("Dữ liệu S4 quá lớn để lưu bản sao an toàn; không xóa")
    return raw


def delete(uid, character_name, nonce, confirmation, operator):
    """SUPER GM only: archive + remove just one UID/S4, transactionally.

    Caller MUST require SUPER GM + GM action key and hold the target
    player-engine pool lock. No post-delete mutations in this transaction.
    """
    uid=_uid(uid)
    character_name=str(character_name or "").strip()
    if confirmation != "XOA S4":
        raise ValueError('Nhập chính xác "XOA S4" để xác nhận')
    token=str(nonce or "")
    with _lock:
        challenge=_challenges.pop(token,None)
    if not challenge or challenge["expires"]<time.time():
        raise ValueError("Xác nhận đã hết hạn. Hãy kiểm tra S4 một lần nữa")
    if uid!=challenge["uid"] or character_name!=challenge["character_name"]:
        raise ValueError("UID hoặc tên nhân vật không khớp bản xem trước S4")
    db=live_service._db()
    try:
        if db.backend=="sqlite":
            db.execute("BEGIN IMMEDIATE")
        char=_character(db,uid,lock=True)
        if not char:
            raise ValueError("Nhân vật S4 không còn tồn tại")
        if (char["character_name"]!=character_name
                or int(char["created_at"])!=challenge["created_at"]):
            raise ValueError("Nhân vật S4 đã thay đổi; cần kiểm tra lại")
        blockers=_blockers(db,uid)
        if blockers:
            raise ValueError("Có dữ liệu liên kết S4 đang hoạt động, không thể xóa: "+
                             ", ".join(x["reason"] for x in blockers))
        raw=_capture(db,uid)
        now=int(time.time())
        backup_id="S4-ARCH-"+secrets.token_hex(12).upper()
        db.execute("""CREATE TABLE IF NOT EXISTS s4_character_archives(
            id TEXT PRIMARY KEY,uid TEXT NOT NULL,server_id TEXT NOT NULL,
            character_name TEXT NOT NULL,created_at BIGINT NOT NULL,
            deleted_at BIGINT NOT NULL,operator TEXT NOT NULL,snapshot TEXT NOT NULL
        )""")
        db.execute("""INSERT INTO s4_character_archives
             (id,uid,server_id,character_name,created_at,deleted_at,operator,snapshot)
             VALUES(?,?,?,?,?,?,?,?)""",
             (backup_id,uid,WORLD,character_name,char["created_at"],now,str(operator)[:100],raw))
        removed={}
        # The 'players' row goes last; no UID-only table can be changed.
        for table in (*[x for x in SCOPED_TABLES if x!="players"],"players"):
            if not _exists(db,table):
                continue
            cur=db.execute(f"DELETE FROM {table} WHERE uid=? AND server_id=?",(uid,WORLD))
            removed[table]=int(cur.rowcount)
        if removed.get("players")!=1:
            raise ValueError("Không xác minh được thao tác xóa nhân vật S4; đã hủy")
        live_service._audit(db,"admin.s4.character_delete",f"{WORLD}:{uid}",
            {"archive_id":backup_id,"character_name":character_name,
             "deleted_rows":removed,"retained":"account, other worlds, VIP, billing, redemption history"},
            str(operator))
        db.commit()
        return {"ok":True,"uid":uid,"server_id":WORLD,
                "character_name":character_name,"archive_id":backup_id,
                "deleted_rows":removed,"archived":True}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
