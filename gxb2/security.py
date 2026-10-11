from __future__ import annotations

import os
import threading
import time
from collections import defaultdict, deque
from urllib.parse import urlparse


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def normalized_origin(value: str) -> str:
    value = str(value or "").strip().rstrip("/")
    if not value:
        return ""
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("GXB3_PUBLIC_ORIGIN phải là URL http/https hợp lệ")
    return f"{parsed.scheme}://{parsed.netloc}"


def validate_production_config(*, http_host: str, public_origin: str, admin_key: str, database_url: str) -> list[str]:
    production = env_bool("GXB3_PRODUCTION", False)
    public_bind = str(http_host or "") not in ("127.0.0.1", "localhost", "::1")
    warnings: list[str] = []
    if not production:
        if public_bind:
            warnings.append("HTTP đang bind public nhưng GXB3_PRODUCTION chưa bật.")
        return warnings

    origin = normalized_origin(public_origin)
    if not origin or not origin.startswith("https://"):
        raise RuntimeError("Production yêu cầu GXB3_PUBLIC_ORIGIN dùng HTTPS.")
    if len(str(admin_key or "")) < 24:
        raise RuntimeError("Production yêu cầu GXB3_ADMIN_KEY ngẫu nhiên, tối thiểu 24 ký tự.")
    if not (str(database_url or "").startswith("postgresql://") or str(database_url or "").startswith("postgres://")):
        raise RuntimeError("Production yêu cầu PostgreSQL qua GXB3_DATABASE_URL/DATABASE_URL.")
    if not public_bind:
        warnings.append("Production đang bind localhost; chỉ hợp lệ khi reverse proxy chạy cùng máy/container.")
    return warnings


class FixedWindowRateLimiter:
    """Small in-process limiter. Production multi-instance should also rate-limit at proxy/Redis."""

    def __init__(self):
        self._lock = threading.RLock()
        self._events: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    def allow(self, bucket: str, key: str, *, limit: int, window: int, now: float | None = None) -> tuple[bool, int]:
        now = float(time.time() if now is None else now)
        limit = max(1, int(limit))
        window = max(1, int(window))
        ident = (str(bucket), str(key))
        cutoff = now - window
        with self._lock:
            q = self._events[ident]
            while q and q[0] <= cutoff:
                q.popleft()
            if len(q) >= limit:
                retry = max(1, int(window - (now - q[0])))
                return False, retry
            q.append(now)
            if not q:
                self._events.pop(ident, None)
            return True, 0

    def clear(self):
        with self._lock:
            self._events.clear()


DEFAULT_LIMITS = {
    "auth_register": (5, 600),
    "auth_login": (12, 300),
    "auth_reset": (5, 900),
    "recovery_rotate": (4, 3600),
    "order_create": (6, 600),
    "guild_chat": (30, 60),
    "pvp_queue": (20, 60),
    "battle": (12, 60),
    "admin": (60, 60),
}
