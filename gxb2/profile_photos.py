"""Safe, public WebP profile pictures; authoritative bytes live in Neon.

Uploaded pictures are untrusted. Pillow decodes/re-encodes without EXIF or
embedded metadata. Opaque names are not player-controlled paths. Each (UID,
world) retains only its current personal image, with a separate token for
immutable browser caching and no filesystem dependency during deployments.
"""
from __future__ import annotations

import io
import os
import re
import secrets
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path

from . import database

UPLOAD_COOLDOWN_SECONDS = 24 * 60 * 60
MAX_UPLOAD_BYTES = 3 * 1024 * 1024
MAX_PIXELS = 12_000_000
MAX_STORED_BYTES = 240 * 1024
OUTPUT_SIZE = 320
AVATAR_RE = re.compile(r"custom_[0-9a-f]{32}\Z")
LOCAL_DB = Path(os.environ.get('GXB3_PROFILE_PHOTOS_SQLITE', str(Path(__file__).resolve().parents[1] / 'state' / 'profile-photos.sqlite3')))
_ready = set()
_lock = threading.RLock()


class PhotoCooldownError(ValueError):
    """A verified player tried another upload before 24h elapsed."""
    def __init__(self, retry_after: int):
        self.retry_after = max(1, int(retry_after))
        super().__init__('Chỉ được tải hoặc thay ảnh đại diện cá nhân một lần mỗi 24 giờ.')


def _value(row, column):
    return row[column] if database.POSTGRES else row[0]


@contextmanager
def _connection():
    if database.POSTGRES:
        conn = database.acquire_postgres()
        try:
            yield conn
        finally:
            database.release_postgres(conn)
    else:
        LOCAL_DB.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(LOCAL_DB, timeout=15)
        try:
            yield conn
        finally:
            conn.close()


def _sql(query: str) -> str:
    return query.replace('?', '%s') if database.POSTGRES else query


def _schema():
    key = ('postgres', database.DATABASE_URL) if database.POSTGRES else ('sqlite', str(LOCAL_DB))
    if key in _ready:
        return
    with _lock:
        if key in _ready:
            return
        with _connection() as conn:
            try:
                conn.execute('''CREATE TABLE IF NOT EXISTS profile_avatar_photos (
                    avatar_key TEXT PRIMARY KEY,
                    uid TEXT NOT NULL,
                    server_id TEXT NOT NULL,
                    picture ''' + ('BYTEA' if database.POSTGRES else 'BLOB') + ''' NOT NULL,
                    updated_at BIGINT NOT NULL
                )''')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_profile_avatar_photos_owner ON profile_avatar_photos(uid,server_id)')
                # One rolling upload allowance for ACCOUNT UID, across worlds,
                # client sessions, server restarts and avatar deletion.
                conn.execute("""CREATE TABLE IF NOT EXISTS profile_avatar_upload_cooldowns (
                    uid TEXT PRIMARY KEY,
                    last_upload_at BIGINT NOT NULL
                )""")
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        _ready.add(key)


def normalize_image(raw: bytes, content_type: str) -> bytes:
    """Decode only actual JPEG/PNG/WebP; strip metadata, bound pixels, square-crop."""
    from PIL import Image, ImageOps, UnidentifiedImageError

    if content_type.split(';', 1)[0].strip().lower() not in ('image/jpeg', 'image/png', 'image/webp'):
        raise ValueError('Chỉ chấp nhận ảnh JPG, PNG hoặc WebP.')
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_UPLOAD_BYTES:
        raise ValueError('Ảnh tải lên tối đa 3 MB.')
    try:
        with Image.open(io.BytesIO(raw)) as original:
            if original.format not in ('JPEG', 'PNG', 'WEBP'):
                raise ValueError('Nội dung tệp không phải ảnh JPG/PNG/WebP hợp lệ.')
            if getattr(original, 'is_animated', False):
                raise ValueError('Không hỗ trợ ảnh động làm avatar.')
            if original.width <= 0 or original.height <= 0 or original.width * original.height > MAX_PIXELS:
                raise ValueError('Ảnh quá lớn, hãy chọn ảnh nhỏ hơn.')
            # Rotate from EXIF but do not copy metadata to the output.
            resized = ImageOps.fit(ImageOps.exif_transpose(original).convert('RGB'),
                                   (OUTPUT_SIZE, OUTPUT_SIZE), method=Image.Resampling.LANCZOS,
                                   centering=(0.5, 0.5))
            output = io.BytesIO()
            resized.save(output, format='WEBP', quality=80, method=4, exact=False)
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError, OverflowError) as exc:
        raise ValueError('Ảnh bị hỏng hoặc định dạng không hợp lệ.') from exc
    blob = output.getvalue()
    if not blob.startswith(b'RIFF') or blob[8:12] != b'WEBP' or len(blob) > MAX_STORED_BYTES:
        raise ValueError('Không thể tối ưu ảnh, hãy chọn ảnh khác.')
    return blob


def _last_upload(conn, uid: str) -> int:
    previous = conn.execute(_sql('SELECT MAX(updated_at) AS last FROM profile_avatar_photos WHERE uid=?'),
                            (str(uid),)).fetchone()
    quota = conn.execute(_sql('SELECT last_upload_at FROM profile_avatar_upload_cooldowns WHERE uid=?'),
                         (str(uid),)).fetchone()
    return max(int(_value(previous, 'last') or 0), int(_value(quota, 'last_upload_at') or 0) if quota else 0)


def remaining(uid: str, *, now: int | None = None) -> int:
    """Persistent account-wide 24-hour cooldown, including legacy photo rows."""
    _schema()
    when = int(time.time() if now is None else now)
    with _connection() as conn:
        until = _last_upload(conn, uid) + UPLOAD_COOLDOWN_SECONDS
    return max(0, until - when)


def store(uid: str, server_id: str, webp: bytes, *, now: int | None = None) -> str:
    """Atomically reserve 24h upload allowance and insert the new image.

    Conditional UPSERT serializes simultaneous requests, even across sessions
    and different server worlds. Neither deletion nor a restart resets it.
    """
    _schema()
    when = int(time.time() if now is None else now)
    owner = str(uid)
    key = 'custom_' + secrets.token_hex(16)
    assert AVATAR_RE.fullmatch(key)
    with _connection() as conn:
        try:
            last = _last_upload(conn, owner)
            if last and when < last + UPLOAD_COOLDOWN_SECONDS:
                raise PhotoCooldownError(last + UPLOAD_COOLDOWN_SECONDS - when)
            reserved = conn.execute(_sql("""INSERT INTO profile_avatar_upload_cooldowns(uid,last_upload_at)
                    VALUES(?,?)
                    ON CONFLICT(uid) DO UPDATE SET last_upload_at=excluded.last_upload_at
                    WHERE profile_avatar_upload_cooldowns.last_upload_at <= ?"""),
                    (owner, when, when - UPLOAD_COOLDOWN_SECONDS))
            if reserved.rowcount != 1:
                latest = _last_upload(conn, owner)
                raise PhotoCooldownError(latest + UPLOAD_COOLDOWN_SECONDS - when)
            conn.execute(_sql("""INSERT INTO profile_avatar_photos(avatar_key,uid,server_id,picture,updated_at)
                    VALUES(?,?,?,?,?)"""),
                    (key, owner, str(server_id).upper(), webp, when))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    return key


def cancel_uncommitted(uid: str, server_id: str, key: str) -> None:
    """Undo photo and cooldown if the player-profile commit fails."""
    if not AVATAR_RE.fullmatch(str(key)):
        return
    _schema()
    with _connection() as conn:
        try:
            row = conn.execute(_sql("""SELECT updated_at FROM profile_avatar_photos
                    WHERE uid=? AND server_id=? AND avatar_key=?"""),
                    (str(uid), str(server_id).upper(), key)).fetchone()
            if row is not None:
                timestamp = int(_value(row, 'updated_at'))
                conn.execute(_sql("""DELETE FROM profile_avatar_photos
                        WHERE uid=? AND server_id=? AND avatar_key=?"""),
                        (str(uid), str(server_id).upper(), key))
                conn.execute(_sql("""DELETE FROM profile_avatar_upload_cooldowns
                        WHERE uid=? AND last_upload_at=?"""), (str(uid), timestamp))
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def prune_replaced(uid: str, server_id: str, active_key: str) -> int:
    """After profile commit, delete EVERY old image for this UID + world."""
    if not AVATAR_RE.fullmatch(str(active_key)):
        raise ValueError('Mã ảnh đang sử dụng không hợp lệ')
    _schema()
    with _connection() as conn:
        try:
            result = conn.execute(_sql("""DELETE FROM profile_avatar_photos
                    WHERE uid=? AND server_id=? AND avatar_key<>?"""),
                    (str(uid), str(server_id).upper(), active_key))
            conn.commit()
            return result.rowcount
        except Exception:
            conn.rollback()
            raise


def read(key: str) -> bytes | None:
    if not AVATAR_RE.fullmatch(str(key)):
        return None
    _schema()
    with _connection() as conn:
        cur = conn.execute(_sql('SELECT picture FROM profile_avatar_photos WHERE avatar_key=?'), (key,))
        row = cur.fetchone()
        return bytes(row['picture'] if database.POSTGRES else row[0]) if row else None


def remove_all_owned(uid: str, server_id: str) -> int:
    """Delete every stored photo in this single UID/world, NOT its cooldown."""
    _schema()
    with _connection() as conn:
        try:
            result = conn.execute(_sql('DELETE FROM profile_avatar_photos WHERE uid=? AND server_id=?'),
                                  (str(uid), str(server_id).upper()))
            conn.commit()
            return result.rowcount
        except Exception:
            conn.rollback()
            raise


def remove(uid: str, server_id: str, key: str) -> None:
    if not AVATAR_RE.fullmatch(str(key)):
        return
    _schema()
    with _connection() as conn:
        try:
            conn.execute(_sql('DELETE FROM profile_avatar_photos WHERE uid=? AND server_id=? AND avatar_key=?'),
                         (str(uid), str(server_id).upper(), key))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
