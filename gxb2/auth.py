from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import sqlite3
import threading
import time
from pathlib import Path

from . import live_service

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "state" / "auth.sqlite3"
SESSION_TTL = 30 * 24 * 60 * 60
PBKDF2_ROUNDS = 310_000
_lock = threading.RLock()
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{4,24}$")


def _db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS accounts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT UNIQUE,
        username TEXT NOT NULL UNIQUE COLLATE NOCASE,
        email TEXT NOT NULL DEFAULT '',
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at INTEGER NOT NULL,
        last_login INTEGER NOT NULL DEFAULT 0
    )""")
    db.execute("""CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_email
                  ON accounts(email COLLATE NOCASE) WHERE email <> ''""")
    db.execute("""CREATE TABLE IF NOT EXISTS sessions(
        token_hash TEXT PRIMARY KEY,
        account_id INTEGER NOT NULL,
        server_id TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL,
        last_seen INTEGER NOT NULL,
        FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS login_attempts(
        bucket TEXT PRIMARY KEY,
        count INTEGER NOT NULL,
        first_at INTEGER NOT NULL,
        blocked_until INTEGER NOT NULL DEFAULT 0
    )""")
    db.commit()
    return db


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS).hex()


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("ascii")).hexdigest()


def _clean_username(value):
    value = str(value or "").strip()
    if not USERNAME_RE.fullmatch(value):
        raise ValueError("Tên đăng nhập phải dài 4–24 ký tự và chỉ gồm chữ, số, _, -, .")
    return value


def _clean_password(value):
    value = str(value or "")
    if not 8 <= len(value) <= 128:
        raise ValueError("Mật khẩu phải dài từ 8 đến 128 ký tự")
    if value.lower() == value or value.upper() == value or not any(ch.isdigit() for ch in value):
        raise ValueError("Mật khẩu phải có chữ hoa, chữ thường và số")
    return value


def _clean_email(value):
    value = str(value or "").strip().lower()
    if value and (len(value) > 254 or "@" not in value or value.startswith("@") or value.endswith("@")):
        raise ValueError("Email không hợp lệ")
    return value


def _public_account(row, server_id=None):
    return {
        "id": int(row["id"]),
        "uid": row["uid"],
        "username": row["username"],
        "email": row["email"],
        "status": row["status"],
        "server_id": server_id,
    }


def _check_rate_limit(bucket):
    now = int(time.time())
    with _lock:
        db = _db()
        row = db.execute("SELECT * FROM login_attempts WHERE bucket=?", (bucket,)).fetchone()
        if row and int(row["blocked_until"]) > now:
            wait = int(row["blocked_until"]) - now
            db.close()
            raise ValueError(f"Đăng nhập tạm khóa. Thử lại sau {wait} giây")
        if row and now - int(row["first_at"]) > 900:
            db.execute("DELETE FROM login_attempts WHERE bucket=?", (bucket,))
            db.commit()
        db.close()


def _failed_login(bucket):
    now = int(time.time())
    with _lock:
        db = _db()
        row = db.execute("SELECT * FROM login_attempts WHERE bucket=?", (bucket,)).fetchone()
        if not row:
            db.execute("INSERT INTO login_attempts(bucket,count,first_at,blocked_until) VALUES(?,1,?,0)", (bucket, now))
        else:
            count = int(row["count"]) + 1
            blocked = now + min(900, 30 * (2 ** max(0, count - 5))) if count >= 5 else 0
            db.execute("UPDATE login_attempts SET count=?,blocked_until=? WHERE bucket=?", (count, blocked, bucket))
        db.commit(); db.close()


def _clear_attempts(bucket):
    with _lock:
        db = _db(); db.execute("DELETE FROM login_attempts WHERE bucket=?", (bucket,)); db.commit(); db.close()


def _new_session(db, account_id, server_id):
    now = int(time.time())
    token = secrets.token_urlsafe(32)
    db.execute("DELETE FROM sessions WHERE expires_at<=?", (now,))
    db.execute("INSERT INTO sessions(token_hash,account_id,server_id,created_at,expires_at,last_seen) VALUES(?,?,?,?,?,?)",
               (_token_hash(token), int(account_id), server_id, now, now + SESSION_TTL, now))
    return token, now + SESSION_TTL


def register(username, password, character_name, server_id="S1", email=""):
    username = _clean_username(username)
    password = _clean_password(password)
    email = _clean_email(email)
    character_name = str(character_name or "").strip()
    server_id = str(server_id or "S1").strip().upper()
    if not 2 <= len(character_name) <= 20 or any(ord(c) < 32 for c in character_name):
        raise ValueError("Tên Nhân Vật phải dài 2–20 ký tự")
    worlds = {w["server_id"]: w for w in live_service.worlds()}
    world = worlds.get(server_id)
    if not world: raise ValueError("Server không tồn tại")
    if world["status"] != "online": raise ValueError("Server hiện không mở đăng ký")

    salt = secrets.token_bytes(16)
    pwh = _hash_password(password, salt)
    now = int(time.time())
    with _lock:
        db = _db()
        try:
            cur = db.execute("""INSERT INTO accounts(uid,username,email,password_hash,salt,status,created_at,last_login)
                                VALUES(NULL,?,?,?,?,'active',?,?)""",
                             (username, email, pwh, salt.hex(), now, now))
            account_id = int(cur.lastrowid)
            uid = f"GXB3-{account_id:08d}"
            db.execute("UPDATE accounts SET uid=? WHERE id=?", (uid, account_id))
            token, expires = _new_session(db, account_id, server_id)
            db.commit()
        except sqlite3.IntegrityError as exc:
            db.rollback(); db.close()
            msg = str(exc).lower()
            if "username" in msg: raise ValueError("Tên đăng nhập đã tồn tại")
            if "email" in msg: raise ValueError("Email đã được sử dụng")
            raise ValueError("Không thể tạo tài khoản")
        row = db.execute("SELECT * FROM accounts WHERE id=?", (account_id,)).fetchone()
        db.close()
    live_service.register_player(uid, server_id, character_name)
    return {"account": _public_account(row, server_id), "character_name": character_name, "token": token, "expires_at": expires}


def login(username, password, server_id="S1", remote=""):
    username = str(username or "").strip()
    password = str(password or "")
    server_id = str(server_id or "S1").strip().upper()
    bucket = hashlib.sha256(f"{remote}|{username.casefold()}".encode()).hexdigest()
    _check_rate_limit(bucket)
    with _lock:
        db = _db()
        row = db.execute("SELECT * FROM accounts WHERE username=? COLLATE NOCASE", (username,)).fetchone()
        valid = False
        if row:
            calc = _hash_password(password, bytes.fromhex(row["salt"]))
            valid = hmac.compare_digest(calc, row["password_hash"])
        if not valid:
            db.close(); _failed_login(bucket); raise ValueError("Tên đăng nhập hoặc mật khẩu không đúng")
        if row["status"] != "active":
            db.close(); raise ValueError("Tài khoản đăng nhập đang bị khóa")
        world = next((w for w in live_service.worlds() if w["server_id"] == server_id), None)
        if not world:
            db.close(); raise ValueError("Server không tồn tại")
        if world["status"] == "closed":
            db.close(); raise ValueError("Server đã đóng")
        player = live_service.player(row["uid"], server_id)
        if not player:
            db.close(); raise ValueError("Tài khoản chưa có nhân vật ở server này")
        if player["status"] == "banned":
            db.close(); raise ValueError("Nhân vật ở server này đang bị khóa")
        token, expires = _new_session(db, row["id"], server_id)
        db.execute("UPDATE accounts SET last_login=? WHERE id=?", (int(time.time()), row["id"]))
        db.commit(); db.close()
    _clear_attempts(bucket)
    return {"account": _public_account(row, server_id), "character_name": player["character_name"], "token": token, "expires_at": expires}


def session(token):
    if not token: return None
    now = int(time.time())
    th = _token_hash(token)
    with _lock:
        db = _db()
        row = db.execute("""SELECT s.server_id,s.expires_at,a.* FROM sessions s
                            JOIN accounts a ON a.id=s.account_id WHERE s.token_hash=?""", (th,)).fetchone()
        if not row or int(row["expires_at"]) <= now:
            if row: db.execute("DELETE FROM sessions WHERE token_hash=?", (th,)); db.commit()
            db.close(); return None
        if row["status"] != "active":
            db.close(); return None
        db.execute("UPDATE sessions SET last_seen=? WHERE token_hash=?", (now, th)); db.commit(); db.close()
    player = live_service.player(row["uid"], row["server_id"])
    if not player or player["status"] == "banned": return None
    return {"account": _public_account(row, row["server_id"]), "character_name": player["character_name"], "player": player}


def logout(token):
    if not token: return
    with _lock:
        db = _db(); db.execute("DELETE FROM sessions WHERE token_hash=?", (_token_hash(token),)); db.commit(); db.close()


def switch_server(token, server_id):
    current = session(token)
    if not current: raise ValueError("Phiên đăng nhập đã hết hạn")
    server_id = str(server_id or "").strip().upper()
    player = live_service.player(current["account"]["uid"], server_id)
    if not player: raise ValueError("Chưa có nhân vật ở server này")
    if player["status"] == "banned": raise ValueError("Nhân vật ở server này đang bị khóa")
    world = next((w for w in live_service.worlds() if w["server_id"] == server_id), None)
    if not world or world["status"] == "closed": raise ValueError("Server không khả dụng")
    with _lock:
        db=_db()
        db.execute("UPDATE sessions SET server_id=?,last_seen=? WHERE token_hash=?",
                   (server_id,int(time.time()),_token_hash(token)))
        db.commit(); db.close()
    return session(token)
