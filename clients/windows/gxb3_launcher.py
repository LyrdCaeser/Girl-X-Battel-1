from __future__ import annotations

import json
import threading
import time
import urllib.request
import webbrowser

GAME_URL = "https://180-93-111-99.sslip.io"
READY_URL = GAME_URL + "/readyz"

LOADING_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body{margin:0;width:100%;height:100%;background:#090b12;color:#fff;font-family:Segoe UI,Arial,sans-serif}
.wrap{height:100%;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:18px}
.logo{font-size:42px;font-weight:800;letter-spacing:3px}
.sub{color:#b9c1d9;font-size:15px}
.spinner{width:44px;height:44px;border:4px solid #252b3d;border-top-color:#8f5cff;border-radius:50%;animation:s 1s linear infinite}
@keyframes s{to{transform:rotate(360deg)}}
</style></head><body><div class="wrap">
<div class="logo">Nữ Thần Chiến Đấu - GXB 3</div><div class="spinner"></div>
<div class="sub">Đang khởi động máy chủ và chuẩn bị trò chơi...</div>
</div></body></html>"""

ERROR_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body{margin:0;width:100%;height:100%;background:#090b12;color:#fff;font-family:Segoe UI,Arial,sans-serif}
.wrap{height:100%;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:14px;text-align:center}
h1{margin:0}.sub{color:#b9c1d9;max-width:520px;line-height:1.6}
</style></head><body><div class="wrap"><h1>Nữ Thần Chiến Đấu - GXB 3</h1>
<div class="sub">Không thể kết nối máy chủ. Kiểm tra mạng rồi mở lại trò chơi.</div>
</div></body></html>"""


def server_ready() -> bool:
    request = urllib.request.Request(
        READY_URL,
        headers={"User-Agent": "GXB3-Windows/1.0", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.status != 200:
                return False
            body = response.read(65536).decode("utf-8", "replace")
            payload = json.loads(body)
            return payload.get("ready") is True
    except Exception:
        return False


def wake_and_open(window) -> None:
    deadline = time.monotonic() + 150
    while time.monotonic() < deadline:
        if server_ready():
            window.load_url(GAME_URL)
            return
        time.sleep(3)
    window.load_html(ERROR_HTML)


def main() -> int:
    try:
        import webview
    except Exception:
        deadline = time.monotonic() + 150
        while time.monotonic() < deadline:
            if server_ready():
                break
            time.sleep(3)
        webbrowser.open(GAME_URL)
        return 0

    try:
        window = webview.create_window(
            "Nữ Thần Chiến Đấu - GXB 3 · ALPHA RC7",
            html=LOADING_HTML,
            width=1280,
            height=800,
            min_size=(960, 600),
            resizable=True,
            text_select=False,
            confirm_close=True,
        )

        def on_started() -> None:
            threading.Thread(target=wake_and_open, args=(window,), daemon=True).start()

        webview.start(on_started, gui="edgechromium", private_mode=False)
        return 0
    except Exception:
        webbrowser.open(GAME_URL)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
