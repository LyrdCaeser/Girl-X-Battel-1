#!/usr/bin/env python3
"""Audit absolute frontend URLs and separate static assets from gameplay/API routes."""
from __future__ import annotations
import argparse
import collections
import re
from pathlib import Path

URL = re.compile(r'''["'`](/[^"'`\s<>]+)''')
STATIC_EXT = re.compile(r"\.(?:js|css|json|png|jpg|jpeg|webp|gif|svg|mp3|ogg|wav|m4a|aac|atlas)(?:$|[?#])", re.I)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", type=Path, default=Path("web"))
    args = ap.parse_args()
    counts = collections.Counter()
    unique = collections.defaultdict(set)
    files = 0
    for path in args.root.rglob("*"):
        if path.suffix.lower() not in {".html", ".js", ".css"}:
            continue
        files += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in URL.finditer(text):
            value = match.group(1).split("?", 1)[0].split("#", 1)[0]
            if value.startswith("/api/") or value == "/health" or value.startswith("/local-log"):
                category = "gameplay-or-api"
            elif value.startswith("/assets/") or value.startswith("/localization/"):
                category = "cdn-static"
            elif STATIC_EXT.search(value):
                category = "root-static"
            else:
                category = "other"
            counts[category] += 1
            unique[category].add(value)
    print(f"scanned_files={files}")
    for category in ("cdn-static", "root-static", "gameplay-or-api", "other"):
        print(f"{category}_references={counts[category]}")
        print(f"{category}_unique={len(unique[category])}")
    if unique["gameplay-or-api"] & unique["cdn-static"]:
        raise SystemExit("a path was classified as both gameplay/API and CDN static")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
