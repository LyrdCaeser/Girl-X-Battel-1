from __future__ import annotations

import sys
import webbrowser

GAME_URL = "https://gxb3-production.onrender.com"


def main() -> int:
    try:
        import webview
    except Exception:
        webbrowser.open(GAME_URL)
        return 0

    try:
        webview.create_window(
            "GXB 3",
            GAME_URL,
            width=1280,
            height=800,
            min_size=(960, 600),
            resizable=True,
            text_select=False,
            confirm_close=True,
        )
        webview.start(gui="edgechromium", private_mode=False)
        return 0
    except Exception:
        # Keep the release usable even if WebView2 is unavailable/corrupted.
        webbrowser.open(GAME_URL)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
