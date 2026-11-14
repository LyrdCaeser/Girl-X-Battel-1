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

MAX_UPLOAD_BYTES = 3 * 1024 * 1024
MAX_PIXELS = 12_000_000
MAX_STORED_BYTES = 240 * 1024
OUTPUT_SIZE = 320
AVATAR_RE = re.compile(r"custom_[0-9a-f]{32}\Z")
LOCAL_DB = Path(os.environ.get('GXB3_PROFILE_PHOTOS_SQLITE', str(Path(__file__).resolve().parents[1] / 'state' / 'profile-photos.sqlite3')))
_ready = set()
_lock = threading.RLock()


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


def store(uid: str, server_id: str, webp: bytes) -> str:
    _schema()
    key = 'custom_' + secrets.token_hex(16)
    assert AVATAR_RE.fullmatch(key)
    with _connection() as conn:
        try:
            conn.execute(_sql('INSERT INTO profile_avatar_photos(avatar_key,uid,server_id,picture,updated_at) VALUES(?,?,?,?,?)'),
                         (key, str(uid), str(server_id).upper(), webp, int(time.time())))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    return key


def read(key: str) -> bytes | None:
    if not AVATAR_RE.fullmatch(str(key)):
        return None
    _schema()
    with _connection() as conn:
        cur = conn.execute(_sql('SELECT picture FROM profile_avatar_photos WHERE avatar_key=?'), (key,))
        row = cur.fetchone()
        return bytes(row['picture'] if database.POSTGRES else row[0]) if row else None


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
