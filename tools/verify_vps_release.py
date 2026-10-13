#!/usr/bin/env python3
"""Read-only online production smoke test. Never reads passwords or modifies Neon."""
from __future__ import annotations
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PUBLIC = os.environ.get("GXB3_TEST_ORIGIN", "https://180-93-111-99.sslip.io").rstrip("/")
LOCAL = "http://127.0.0.1:9080"
FAILS = 0


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
    check("Game entry links lobby script", PUBLIC + "/",
          assertion=lambda _, data: b"/lobby-dialogue.js" in data)
    print("=== RESULT:", "PASS" if not FAILS else f"FAILED ({FAILS})", "===")
    sys.exit(bool(FAILS))


if __name__ == "__main__":
    main()
