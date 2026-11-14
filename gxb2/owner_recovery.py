"""SUPER GM-only recovery of the three admin keys through authenticator TOTP.

Only an already authenticated canonical owner may enroll or reset. Enrollment
requires all CURRENT admin keys; losing them before enrollment requires a VPS
operator, not a public bypass. Stored overrides are PBKDF2 hashes; game data,
accounts, balances and session cookies are never overwritten by a reset.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import secrets
import threading
import time
from urllib.parse import quote

from . import auth

_LOCK = threading.RLock()
_READY = set()
CODE_RE = re.compile(r"^[0-9]{6}$")
BACKUP_RE = re.compile(r"^GXB3-[A-F0-9]{4}(?:-[A-F0-9]{4}){3}$")
KEY_FIELDS = ("admin", "panel", "gm")
ENV_KEYS = {"admin": "GXB3_ADMIN_KEY",
            "panel": "GXB3_GIFTCODE_PANEL_KEY",
            "gm": "GXB3_GM_ACTION_KEY"}
MIN_LENGTH = {"admin": 12, "panel": 12, "gm": 24}
ITERATIONS = 240_000
ENROLL_TTL = 600
MAX_FAILURES = 5
LOCK_SECONDS = 15 * 60


def _master():
    """Existing independent VPS secrets root a server-only, stable TOTP key.

    Never store the raw TOTP seed or backups in Neon. After a key reset the
    ORIGINAL server environment remains stable; the active admin keys become
    the irreversible DB overrides. Moving servers must preserve those envs.
    """
    values = [os.environ.get(ENV_KEYS[k], "") for k in KEY_FIELDS]
    if any(len(v) < MIN_LENGTH[k] for k, v in zip(KEY_FIELDS, values)):
        raise RuntimeError("VPS chưa cấu hình đủ ba khóa quản trị gốc")
    return hashlib.sha256(("\x00".join(values) + "\x00gxb3-recovery-v1").encode()).digest()


def _ensure(db):
    identity = (db.backend, db.identity)
    if identity in _READY:
        return
    with _LOCK:
        if identity in _READY:
            return
        db.execute("""CREATE TABLE IF NOT EXISTS owner_security (
            id INTEGER PRIMARY KEY CHECK(id=1), owner_uid TEXT NOT NULL,
            nonce TEXT NOT NULL DEFAULT '', enrolled INTEGER NOT NULL DEFAULT 0,
            pending_nonce TEXT NOT NULL DEFAULT '',
            pending_session TEXT NOT NULL DEFAULT '',
            pending_at BIGINT NOT NULL DEFAULT 0,
            last_counter BIGINT NOT NULL DEFAULT -1,
            version BIGINT NOT NULL DEFAULT 0,
            failures INTEGER NOT NULL DEFAULT 0,
            blocked_until BIGINT NOT NULL DEFAULT 0,
            updated_at BIGINT NOT NULL DEFAULT 0
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS owner_key_overrides (
            key_name TEXT PRIMARY KEY, salt TEXT NOT NULL, key_hash TEXT NOT NULL
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS owner_recovery_backups (
            code_hash TEXT PRIMARY KEY, used_at BIGINT NOT NULL DEFAULT 0
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS owner_recovery_events (
            id TEXT PRIMARY KEY, owner_uid TEXT NOT NULL, action TEXT NOT NULL,
            created_at BIGINT NOT NULL
        )""")
        db.commit()
        _READY.add(identity)


def _db():
    db = auth._db()
    try:
        _ensure(db)
        return db
    except Exception:
        db.rollback()
        db.close()
        raise


def _owner_uid(token):
    session = auth.session(token)
    if not session:
        raise ValueError("Cần đăng nhập tài khoản SUPER GM")
    a = session["account"]
    canonical = os.environ.get("GXB3_OWNER_UID", "GXB3-00000001").strip()
    email = os.environ.get("GXB3_OWNER_EMAIL", "trieuquangholuxury@gmail.com").strip().casefold()
    if not canonical or not email or str(a.get("uid")) != canonical or str(a.get("email") or "").casefold() != email:
        raise ValueError("Chỉ SUPER GM chính thức được sử dụng khôi phục")
    return canonical


def _read(db, *, locked=False):
    sql = "SELECT * FROM owner_security WHERE id=1"
    if locked and db.backend == "postgres":
        sql += " FOR UPDATE"
    return db.execute(sql).fetchone()


def _verify_hash(raw, salt, digest):
    if not isinstance(raw, str) or len(raw) > 1024:
        return False
    got = hashlib.pbkdf2_hmac("sha256", raw.encode(), bytes.fromhex(salt), ITERATIONS).hex()
    return hmac.compare_digest(got, digest)


def _hash_key(raw):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", raw.encode(), salt, ITERATIONS)
    return salt.hex(), digest.hex()


def _current_keys(db, supplied):
    if not isinstance(supplied, dict):
        return False
    rows = {r["key_name"]: r for r in db.execute("SELECT * FROM owner_key_overrides").fetchall()}
    valid = True
    for k in KEY_FIELDS:
        candidate = supplied.get(k)
        if k in rows:
            row = rows[k]
            result = _verify_hash(candidate, row["salt"], row["key_hash"])
        else:
            original = os.environ.get(ENV_KEYS[k], "")
            result = (isinstance(candidate, str) and len(candidate) <= 1024
                      and len(original) >= MIN_LENGTH[k]
                      and hmac.compare_digest(original.encode(), candidate.encode()))
        valid = bool(result) and valid
    return valid


def verify_all(admin, panel, gm):
    _master()
    db = _db()
    try:
        return _current_keys(db, {"admin": admin, "panel": panel, "gm": gm})
    finally:
        db.close()


def verify_key(key_name, supplied):
    if key_name not in KEY_FIELDS:
        return False
    _master()
    db = _db()
    try:
        row = db.execute("SELECT salt,key_hash FROM owner_key_overrides WHERE key_name=?",
                         (key_name,)).fetchone()
        if row:
            return _verify_hash(supplied, row["salt"], row["key_hash"])
        original = os.environ.get(ENV_KEYS[key_name], "")
        return bool(isinstance(supplied, str) and len(original) >= MIN_LENGTH[key_name]
                    and len(supplied) <= 1024
                    and hmac.compare_digest(original.encode(), supplied.encode()))
    finally:
        db.close()


def key_version():
    db = _db()
    try:
        row = _read(db)
        return int(row["version"]) if row else 0
    finally:
        db.close()


def signing_key():
    """Signing key is independent of user-resettable keys."""
    return hmac.new(_master(), b"gxb3-admin-panel-signing-v2", hashlib.sha256).digest()


def status(token):
    uid = _owner_uid(token)
    db = _db()
    try:
        row = _read(db)
        if row and row["owner_uid"] != uid:
            raise ValueError("Cấu hình khôi phục không thuộc chủ tài khoản hiện tại")
        left = db.execute("SELECT COUNT(*) AS n FROM owner_recovery_backups WHERE used_at=0").fetchone()
        return {"enrolled": bool(row and row["enrolled"]),
                "backup_remaining": int(left["n"]) if row and row["enrolled"] else 0}
    finally:
        db.close()


def _secret(nonce):
    digest = hmac.new(_master(), ("gxb3-totp-seed:" + nonce).encode(), hashlib.sha256).digest()
    return digest[:20]


def _totp_at(secret, step):
    value = hmac.new(secret, int(step).to_bytes(8, "big"), hashlib.sha1).digest()
    offset = value[-1] & 15
    num = int.from_bytes(value[offset:offset+4], "big") & 0x7fffffff
    return f"{num % 1_000_000:06d}"


def _counter(nonce, value, last=-1, *, now=None):
    code = str(value or "").strip()
    if not CODE_RE.fullmatch(code):
        return None
    step = int(time.time() if now is None else now) // 30
    key = _secret(nonce)
    # 30 seconds of clock skew in either direction; never reuse a past counter.
    for i in (step-1, step, step+1):
        if i >= 0 and i > int(last) and hmac.compare_digest(_totp_at(key,i),code):
            return i
    return None


def _backup_hash(value):
    normalized = str(value or "").strip().upper()
    if not BACKUP_RE.fullmatch(normalized):
        return None
    return hmac.new(_master(), ("gxb3-backup:" + normalized).encode(), hashlib.sha256).hexdigest()


def _new_backups(db):
    db.execute("DELETE FROM owner_recovery_backups")
    codes = []
    for _ in range(8):
        h = secrets.token_hex(8).upper()
        code = "GXB3-" + "-".join(h[i:i+4] for i in range(0,16,4))
        db.execute("INSERT INTO owner_recovery_backups(code_hash,used_at) VALUES(?,0)",
                   (_backup_hash(code),))
        codes.append(code)
    return codes


def _event(db, uid, action):
    db.execute("INSERT INTO owner_recovery_events(id,owner_uid,action,created_at) VALUES(?,?,?,?)",
               (secrets.token_hex(16),uid,action,int(time.time())))


def enrollment_start(token, keys):
    uid = _owner_uid(token)
    if not verify_all(keys.get("admin"), keys.get("panel"), keys.get("gm")):
        raise ValueError("Không thể thiết lập: ba khóa quản trị hiện tại không đúng")
    nonce = secrets.token_urlsafe(32)
    now = int(time.time())
    db = _db()
    try:
        db.execute("BEGIN IMMEDIATE")
        row = _read(db, locked=True)
        if row and row["enrolled"]:
            raise ValueError("Google Authenticator đã liên kết; không được ghi đè khi chưa xác thực")
        if row and row["owner_uid"] != uid:
            raise ValueError("Cấu hình khôi phục thuộc chủ tài khoản khác")
        db.execute("""INSERT INTO owner_security
            (id,owner_uid,pending_nonce,pending_session,pending_at,updated_at)
            VALUES(1,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
            pending_nonce=excluded.pending_nonce,
            pending_session=excluded.pending_session,
            pending_at=excluded.pending_at,updated_at=excluded.updated_at""",
            (uid,nonce,auth._token_hash(token),now,now))
        _event(db,uid,"totp.enroll.start")
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    secret=base64.b32encode(_secret(nonce)).decode().rstrip("=")
    uri="otpauth://totp/" + quote("Goddess Battle 3:SUPER GM",safe="") + (
        "?secret=" + secret + "&issuer=" + quote("Goddess Battle 3",safe="")
        + "&algorithm=SHA1&digits=6&period=30")
    return {"secret":secret,"otpauth_url":uri,"expires_in":ENROLL_TTL}


def enrollment_confirm(token, code):
    uid = _owner_uid(token)
    now = int(time.time())
    db = _db()
    try:
        db.execute("BEGIN IMMEDIATE")
        row = _read(db,locked=True)
        if (not row or row["owner_uid"] != uid or row["enrolled"]
            or not row["pending_nonce"] or
            row["pending_session"] != auth._token_hash(token)
            or now - int(row["pending_at"]) > ENROLL_TTL):
            raise ValueError("Phiên thiết lập đã hết hạn; hãy bắt đầu lại")
        if int(row["blocked_until"]) > now:
            raise ValueError("Xác thực bị tạm khóa; thử lại sau")
        step=_counter(row["pending_nonce"],code,row["last_counter"],now=now)
        if step is None:
            _failure(db,now)
            db.commit()
            raise ValueError("Mã Google Authenticator không chính xác")
        codes=_new_backups(db)
        db.execute("""UPDATE owner_security SET enrolled=1,nonce=pending_nonce,
            pending_nonce='',pending_session='',pending_at=0,last_counter=?,
            failures=0,blocked_until=0,updated_at=? WHERE id=1""",(step,now))
        _event(db,uid,"totp.enroll.confirm")
        db.commit()
        return {"enrolled":True,"backup_codes":codes}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _failure(db, now):
    row=_read(db)
    count=int(row["failures"])+1
    blocked=now+LOCK_SECONDS if count >= MAX_FAILURES else 0
    db.execute("UPDATE owner_security SET failures=?,blocked_until=? WHERE id=1",
               (count,blocked))


def _validate_new_keys(values):
    if not isinstance(values,dict):
        raise ValueError("Bộ khóa mới không hợp lệ")
    cleaned={}
    for name in KEY_FIELDS:
        raw=values.get(name)
        minimum=MIN_LENGTH[name]
        if not isinstance(raw,str) or not minimum <= len(raw) <= 128:
            raise ValueError("Khóa mới phải đủ độ dài: quản trị 12, bảo vệ 12, QTV 24 ký tự")
        if any(ord(ch)<33 or ord(ch)>126 for ch in raw):
            raise ValueError("Khóa chỉ được chứa ký tự ASCII in được, không có khoảng trắng")
        if raw.islower() or raw.isupper() or not any(ch.isdigit() for ch in raw):
            raise ValueError("Mỗi khóa mới cần chữ hoa, chữ thường và số")
        cleaned[name]=raw
    if len(set(cleaned.values()))!=3:
        raise ValueError("Ba khóa mới phải khác nhau")
    return cleaned


def _check_factor(db, row, value, now):
    """Only call on a row locked for update inside a transaction."""
    step = _counter(row["nonce"],value,row["last_counter"],now=now)
    if step is not None:
        return ("totp",step)
    digest = _backup_hash(value)
    if digest:
        item=db.execute("""SELECT code_hash FROM owner_recovery_backups
            WHERE code_hash=? AND used_at=0""",(digest,)).fetchone()
        if item:
            return ("backup",digest)
    return None


def reset_keys(token, factor, new_keys):
    uid=_owner_uid(token)
    clean=_validate_new_keys(new_keys)
    now=int(time.time())
    db=_db()
    try:
        db.execute("BEGIN IMMEDIATE")
        row=_read(db,locked=True)
        if not row or row["owner_uid"]!=uid or not row["enrolled"]:
            raise ValueError("Chưa liên kết Authenticator với tài khoản SUPER GM")
        if int(row["blocked_until"])>now:
            raise ValueError("Đang tạm khóa thao tác khôi phục; thử lại sau")
        verified=_check_factor(db,row,factor,now)
        if not verified:
            _failure(db,now)
            db.commit()
            raise ValueError("Mã Authenticator hoặc mã dự phòng không hợp lệ")
        for key in KEY_FIELDS:
            salt,digest=_hash_key(clean[key])
            db.execute("""INSERT INTO owner_key_overrides(key_name,salt,key_hash)
                VALUES(?,?,?) ON CONFLICT(key_name) DO UPDATE SET
                salt=excluded.salt,key_hash=excluded.key_hash""",
                (key,salt,digest))
        if verified[0]=="totp":
            db.execute("""UPDATE owner_security SET last_counter=?,version=version+1,
                failures=0,blocked_until=0,updated_at=? WHERE id=1""",
                (verified[1],now))
        else:
            db.execute("""UPDATE owner_recovery_backups SET used_at=?
                WHERE code_hash=? AND used_at=0""",(now,verified[1]))
            db.execute("""UPDATE owner_security SET version=version+1,
                failures=0,blocked_until=0,updated_at=? WHERE id=1""",(now,))
        _event(db,uid,"admin.keys.reset")
        db.commit()
        return {"reset":True,"message":"Đã thay cả 3 khóa quản trị; mọi quyền mở khóa cũ đã hết hiệu lực."}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def rotate_backups(token, code):
    uid=_owner_uid(token)
    now=int(time.time())
    db=_db()
    try:
        db.execute("BEGIN IMMEDIATE")
        row=_read(db,locked=True)
        if not row or row["owner_uid"] != uid or not row["enrolled"]:
            raise ValueError("Google Authenticator chưa được liên kết")
        if int(row["blocked_until"])>now:
            raise ValueError("Thao tác xác thực tạm khóa")
        step=_counter(row["nonce"],code,row["last_counter"],now=now)
        if step is None:
            _failure(db,now)
            db.commit()
            raise ValueError("Mã Authenticator không chính xác")
        codes=_new_backups(db)
        db.execute("""UPDATE owner_security SET last_counter=?,failures=0,
            blocked_until=0,updated_at=? WHERE id=1""",(step,now))
        _event(db,uid,"totp.backups.rotate")
        db.commit()
        return {"backup_codes":codes}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
