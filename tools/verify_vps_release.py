#!/usr/bin/env python3
"""Read-only online production smoke test. Never reads passwords or modifies Neon."""
from __future__ import annotations
import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PUBLIC = os.environ.get("GXB3_TEST_ORIGIN", "https://180-93-111-99.sslip.io").rstrip("/")
LOCAL = "http://127.0.0.1:9080"
FAILS = 0


def wait_ready(label, origin, require_postgres=False, timeout=120, interval=3):
    """Wait for the actual HTTP listener and production preflight; read-only.

    Never treat systemd 'active' as sufficient and never test public endpoints
    before the reverse proxy upstream is ready.
    """
    deadline = time.monotonic() + max(0, timeout)
    attempt = 0
    while True:
        attempt += 1
        try:
            req = Request(origin + "/readyz", headers={"User-Agent": "GXB3-release-check/1.0"})
            with urlopen(req, timeout=4) as resp:
                payload = json.loads(resp.read(8192))
                ok = resp.status == 200 and payload.get("ready") is True
                if require_postgres:
                    ok = ok and payload.get("database") == "postgres"
                if ok:
                    print(f"READY | {label} | HTTP 200 | attempt {attempt}", flush=True)
                    return True
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, TypeError, AttributeError):
            pass
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            print(f"FAIL | {label} did not become ready within {timeout}s", flush=True)
            return False
        if attempt == 1 or attempt % 5 == 0:
            print(f"WAIT | {label} | attempt {attempt} | waiting for /readyz", flush=True)
        time.sleep(min(max(0.01, interval), remaining))


def check(label, url, expected_http=200, assertion=None, headers=None):
    global FAILS
    try:
        req = Request(url, headers={"User-Agent": "GXB3-release-check/1.0", **(headers or {})})
        try:
            with urlopen(req, timeout=20) as resp:
                code, data = resp.status, resp.read(256000)
        except HTTPError as exc:
            code, data = exc.code, exc.read(10000)
        obj = json.loads(data) if data.lstrip().startswith(b"{") else None
        ok = code == expected_http and (assertion is None or assertion(obj, data))
        print(("PASS" if ok else "FAIL") + f" | {label} | HTTP {code}")
        if not ok:
            FAILS += 1
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        FAILS += 1
        print(f"FAIL | {label} | {type(exc).__name__} (no credentials displayed)")


def main():
    print("=== GXB 3 REAL VPS READ-ONLY RELEASE CHECK ===", flush=True)
    startup_timeout = max(0, int(os.environ.get("GXB3_READY_TIMEOUT", "120")))
    if not wait_ready("Local GXB 3", LOCAL, require_postgres=True, timeout=startup_timeout):
        print("=== RESULT: FAILED (server startup not ready; check journalctl -u gxb3) ===")
        sys.exit(1)
    if not wait_ready("Public HTTPS", PUBLIC, timeout=startup_timeout):
        print("=== RESULT: FAILED (HTTPS upstream not ready; inspect proxy and service) ===")
        sys.exit(1)
    check("Local health", LOCAL + "/healthz", assertion=lambda x, _: bool(x and x.get("ok")))
    check("Local readiness", LOCAL + "/readyz", assertion=lambda x, _: bool(x and x.get("ready") and x.get("database") == "postgres"))
    check("Internet HTTPS health", PUBLIC + "/healthz", assertion=lambda x, _: bool(x and x.get("ok")))
    check("Internet HTTPS readiness", PUBLIC + "/readyz", assertion=lambda x, _: bool(x and x.get("ready")))
    check("Anonymous identity has no GM", PUBLIC + "/api/auth/me",
          assertion=lambda x, _: bool(x and not x.get("authenticated") and not x.get("is_super_gm")))
    check("Anonymous blocked from GM", PUBLIC + "/api/admin/dashboard", expected_http=401)
    check("Anonymous blocked from guild", PUBLIC + "/api/world-guild", expected_http=401)
    check("Fake legacy key cannot bypass GM", PUBLIC + "/api/admin/dashboard",
          expected_http=401, headers={"X-GXB2-Admin-Key": "legacy-key-must-not-work"})
    check("Lobby speech served", PUBLIC + "/lobby-dialogue.js",
          assertion=lambda _, data: b"LobbyDialogue" in data)
    check("Lobby dialogue CSS served", PUBLIC + "/lobby-dialogue.css",
          assertion=lambda _, data: b"#dev-open" in data and b"#gxb3-lobby-speech" not in data)
    check("Mobile native CSS served", PUBLIC + "/mobile-native.css",
          assertion=lambda _, data: len(data) > 100)
    check("Mobile layout CSS served", PUBLIC + "/mobile-layout.css",
          assertion=lambda _, data: len(data) > 100)
    check("Game entry links lobby script", PUBLIC + "/",
          assertion=lambda _, data: b"/lobby-dialogue.js" in data)
    # Public/CDN asset paths must serve actual PNG data, not a Git LFS pointer
    # accidentally published as an image or a redirect to a broken placeholder.
    png = b"\x89PNG\r\n\x1a\n"
    for label, path in (
        ("Arena original scene", "/assets/arena/arena_scene.png"),
        ("Arena 3v3 original scene", "/assets/arena/arena_3v3_scene.png"),
        ("Guild original office scene", "/assets/sprite/guild_bg03.png"),
        ("Battle original HP bar", "/assets/original-ui/battle_hp_bar1.png"),
    ):
        check(label, PUBLIC + path, assertion=lambda _, data: data.startswith(png))
    print("=== RESULT:", "PASS" if not FAILS else f"FAILED ({FAILS})", "===")
    sys.exit(bool(FAILS))


if __name__ == "__main__":
    main()
