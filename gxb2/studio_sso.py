"""One-time GXB 3 -> Goddess Battle 3 - Trang Chủ Chính Thức SSO, plus owner-only UI unlock."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import time
from . import auth, owner_recovery

STUDIO_ORIGIN = "https://goddessbattle-3.vercel.app"
TICKET_TTL = 75
PANEL_TTL = 600
_PANEL_HEADER = 'gxb3-giftcode-panel-v1'


def _ticket_hash(ticket):
    return hashlib.sha256(ticket.encode('ascii')).hexdigest()


def _ensure(db):
    db.execute("""CREATE TABLE IF NOT EXISTS giftcode_sso_tickets(
        ticket_hash TEXT PRIMARY KEY, session_hash TEXT NOT NULL,
        account_id BIGINT NOT NULL, server_id TEXT NOT NULL,
        expires_at BIGINT NOT NULL)""")


def confirmation_proof(token):
    """A short-lived signed approval bound to the current first-party game session."""
    if not auth.session(token):
        raise ValueError("Bạn cần đăng nhập GXB 3 trước khi đồng bộ")
    expires = int(time.time()) + 120
    payload = f"gxb3-studio-confirm:{expires}".encode("ascii")
    signature = hmac.new(token.encode("ascii"), payload, hashlib.sha256).hexdigest()
    return f"{expires}.{signature}"


def require_confirmation(token, proof):
    """Deny silent account transfer and expired/forged account approvals."""
    try:
        expires_text, supplied = str(proof or "").split(".", 1)
        if not expires_text.isascii() or not expires_text.isdecimal():
            raise ValueError()
        expires = int(expires_text)
        now = int(time.time())
        if not token or not (now < expires <= now + 120):
            raise ValueError()
        payload = f"gxb3-studio-confirm:{expires}".encode("ascii")
        signature = hmac.new(token.encode("ascii"), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, supplied):
            raise ValueError()
    except (ValueError, TypeError, UnicodeError, OverflowError):
        raise ValueError("Xác nhận đồng bộ hết hạn hoặc không hợp lệ. Hãy kiểm tra tài khoản rồi thử lại.") from None


def start(token):
    """Validate the existing first-party cookie, create a single-use, short TTL ticket."""
    ctx = auth.session(token)
    if not ctx:
        raise ValueError("Bạn cần đăng nhập game GXB 3 trước")
    account = ctx['account']
    ticket = secrets.token_urlsafe(36)
    with auth._lock:
        db=auth._db()
        try:
            _ensure(db)
            db.execute("DELETE FROM giftcode_sso_tickets WHERE expires_at<=?",(int(time.time()),))
            db.execute("""INSERT INTO giftcode_sso_tickets
                (ticket_hash,session_hash,account_id,server_id,expires_at)
                VALUES(?,?,?,?,?)""",
                (_ticket_hash(ticket),auth._token_hash(token),int(account['id']),
                 str(account['server_id']),int(time.time())+TICKET_TTL))
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    return ticket


def exchange(ticket,user_agent='',remote_addr=''):
    """Consume ticket atomically, verify original login has not been revoked."""
    ticket = str(ticket or '')
    if len(ticket)<35 or len(ticket)>150:
        raise ValueError("Liên kết đăng nhập không hợp lệ")
    now=int(time.time())
    with auth._lock:
        db=auth._db()
        try:
            _ensure(db)
            sql="SELECT * FROM giftcode_sso_tickets WHERE ticket_hash=?"
            if db.backend=='sqlite':
                db.execute("BEGIN IMMEDIATE")
            elif db.backend=='postgres':
                sql+=" FOR UPDATE"
            row=db.execute(sql,(_ticket_hash(ticket),)).fetchone()
            if not row or int(row['expires_at'])<=now:
                raise ValueError("Liên kết đã hết hạn. Vui lòng mở lại từ game.")
            db.execute("DELETE FROM giftcode_sso_tickets WHERE ticket_hash=?",(_ticket_hash(ticket),))
            original=db.execute("""SELECT 1 FROM sessions s
                JOIN accounts a ON a.id=s.account_id
                WHERE s.token_hash=? AND s.account_id=? AND s.server_id=?
                AND s.expires_at>? AND a.status='active'""",
                (row['session_hash'],int(row['account_id']),row['server_id'],now)).fetchone()
            if not original:
                raise ValueError("Phiên game đã kết thúc. Vui lòng đăng nhập lại.")
            newtoken,_,_=auth._new_session(db,row['account_id'],row['server_id'],
                                            user_agent,remote_addr)
            db.commit()
            return newtoken
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


def unlock(password, game_session, admin_key=None, gm_key=None):
    """Three real credentials plus authenticated canonical SUPER GM session.

    Current keys are read from hashed Neon overrides when owner reset them.
    Old VPS environment secrets cease to authenticate after a reset.
    """
    if not game_session or not auth.session(game_session):
        raise ValueError("Phiên SUPER GM không hợp lệ")
    version=owner_recovery.key_version()
    if not owner_recovery.verify_all(admin_key,password,gm_key):
        raise ValueError("Một hoặc nhiều khóa QTV không chính xác")
    if owner_recovery.key_version()!=version:
        raise ValueError("Bộ khóa quản trị đã thay đổi; hãy dùng bộ mới")
    expiry=int(time.time())+PANEL_TTL
    message=f"{_PANEL_HEADER}:{auth._token_hash(game_session)}:{expiry}:{version}".encode()
    sig=hmac.new(owner_recovery.signing_key(),message,hashlib.sha256).hexdigest()
    return f"{expiry}.{sig}"


def authorized(token,game_session):
    try:
        expiry_str,sig=str(token or '').split('.',1)
        expiry=int(expiry_str)
        if not expiry or expiry<int(time.time()) or expiry>int(time.time())+PANEL_TTL:
            return False
        if not game_session:
            return False
        version=owner_recovery.key_version()
        message=f"{_PANEL_HEADER}:{auth._token_hash(game_session)}:{expiry}:{version}".encode()
        expected=hmac.new(owner_recovery.signing_key(),message,hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected,sig)
    except (ValueError,TypeError,AttributeError,RuntimeError):
        return False
