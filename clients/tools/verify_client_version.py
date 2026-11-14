"""Fail release builds when any of the four client formats drift in version."""
from __future__ import annotations

import json
import plistlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION = "2.6.4"
VERSION_CODE = "200366"

def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("RELEASE VERSION CHECK FAILED: " + message)

android = (ROOT / "clients/android/app/build.gradle").read_text(encoding="utf-8")
require(re.search(rf"versionCode\s+{VERSION_CODE}\b", android) is not None, "Android versionCode")
require(re.search(rf'versionName\s+"{re.escape(VERSION)}"', android) is not None, "Android versionName")

with (ROOT / "clients/ios/Info.plist").open("rb") as stream:
    ios = plistlib.load(stream)
require(ios.get("CFBundleShortVersionString") == VERSION, "iOS CFBundleShortVersionString")
require(str(ios.get("CFBundleVersion")) == VERSION_CODE, "iOS CFBundleVersion")

windows = (ROOT / "clients/windows/version_info.txt").read_text(encoding="utf-8")
require(f"filevers=(2, 6, 4, 0)" in windows, "Windows file version")
require(f"prodvers=(2, 6, 4, 0)" in windows, "Windows product version")
require(f"ProductVersion', '{VERSION}'" in windows, "Windows ProductVersion metadata")

launcher = (ROOT / "clients/windows/gxb3_launcher.py").read_text(encoding="utf-8")
require("GXB3-Windows/2.6.4" in launcher and "v=2.6.4" in launcher, "Windows cache-busting URL/User-Agent")

app = (ROOT / "clients/ios/GXB3App.swift").read_text(encoding="utf-8")
require("v=2.6.4" in app and "2.6.4" in app, "iOS app shell cache bust/version")

webclip = (ROOT / "clients/ios/make_webclip.py").read_text(encoding="utf-8")
require("2.6.4" in webclip and "NuThanChienDau-GXB3-iOS-2.6.4.mobileconfig" in webclip and "v=2.6.4" in webclip, "iOS Web Clip version/cache bust")

# Every source avatar URL must resolve to a committed 3x WebP asset.
catalog = json.loads((ROOT / "web/assets/avatars.json").read_text(encoding="utf-8"))
avatar_entries = [entry for entry in catalog.values() if entry.get("src")]
require(len(avatar_entries) >= 600, "avatar catalog unexpectedly incomplete")
for entry in avatar_entries:
    src = str(entry["src"]).split("?", 1)[0]
    require(src.startswith("/assets/avatar-hd/portraits/") and src.endswith(".webp"), f"non-HD avatar source: {src}")
    require((ROOT / "web" / src.removeprefix("/" )).is_file(), f"missing avatar asset: {src}")
require(len(list((ROOT / "web/assets/avatar-hd/profile").glob("head_*.webp"))) >= 80, "profile avatar HD set incomplete")
require(len(list((ROOT / "web/assets/avatar-hd/profile").glob("partner_avatar_*.webp"))) >= 700, "profile Goddess avatar HD set incomplete")

workflow = (ROOT / ".github/workflows/gxb3-clients.yml").read_text(encoding="utf-8")
require("2.6.4" in workflow and "200366" in workflow, "Build workflow version labels")
require("publish-release:" in workflow and "tag=\"v2.6.4\"" in workflow, "Versioned production release publishing")

print(f"PASS: Android, Windows, iOS IPA and iOS Web Clip use Version Name {VERSION} / VersionCode {VERSION_CODE}; HD portrait assets are present.")
