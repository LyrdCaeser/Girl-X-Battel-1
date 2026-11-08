#!/usr/bin/env python3
"""Compare tracked resources on main and offline branches without hydrating payloads.

This deliberately compares Git tree paths/blob IDs. Git LFS payload hydration is a
separate release step; an LFS pointer is never reported as a playable asset.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from pathlib import PurePosixPath

AUDIO_EXTENSIONS = {".mp3", ".ogg", ".wav", ".m4a", ".aac", ".flac"}
RESOURCE_ROOTS = ("web/assets/", "data/", "runtime/")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True)


def tree(ref: str) -> dict[str, str]:
    rows = git("ls-tree", "-r", ref, "--", *RESOURCE_ROOTS).splitlines()
    result: dict[str, str] = {}
    for row in rows:
        mode, kind, blob, path = row.split(None, 3)
        if kind == "blob":
            result[path] = blob
    return result


def group(path: str) -> str:
    parts = PurePosixPath(path).parts
    if len(parts) >= 3 and parts[0] == "web" and parts[1] == "assets":
        return f"web/assets/{parts[2]}"
    return parts[0]


def is_lfs(ref: str, path: str) -> bool:
    try:
        prefix = git("show", f"{ref}:{path}")[:44]
    except subprocess.CalledProcessError:
        return False
    return prefix.startswith("version https://git-lfs.github.com/spec/v1")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main", default="origin/main")
    parser.add_argument("--offline", default="feature/offline-mode")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    main_tree, offline_tree = tree(args.main), tree(args.offline)
    missing = sorted(set(main_tree) - set(offline_tree))
    extra = sorted(set(offline_tree) - set(main_tree))
    changed = sorted(path for path in set(main_tree) & set(offline_tree) if main_tree[path] != offline_tree[path])
    audio = sorted(path for path in main_tree if PurePosixPath(path).suffix.lower() in AUDIO_EXTENSIONS)
    report = {
        "main": args.main,
        "offline": args.offline,
        "main_resource_files": len(main_tree),
        "offline_resource_files": len(offline_tree),
        "missing_from_offline": missing,
        "offline_only": extra,
        "changed_blob_paths": changed,
        "audio_files_on_main": len(audio),
        "audio_missing_from_offline": [path for path in audio if path not in offline_tree],
        "audio_changed": [path for path in audio if path in offline_tree and main_tree[path] != offline_tree[path]],
        "lfs_audio_pointers_on_main": sum(is_lfs(args.main, path) for path in audio),
        "groups": {},
    }
    groups = sorted(set(group(path) for path in main_tree | offline_tree))
    for name in groups:
        m = {p for p in main_tree if group(p) == name}
        o = {p for p in offline_tree if group(p) == name}
        report["groups"][name] = {
            "main": len(m), "offline": len(o), "missing": len(m - o),
            "changed": sum(1 for p in m & o if main_tree[p] != offline_tree[p]),
        }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    print(f"main={args.main} files={len(main_tree)}")
    print(f"offline={args.offline} files={len(offline_tree)}")
    print(f"missing={len(missing)} changed={len(changed)} offline_only={len(extra)}")
    print(f"audio={len(audio)} audio_missing={len(report['audio_missing_from_offline'])} audio_changed={len(report['audio_changed'])}")
    print(f"main_lfs_audio_pointers={report['lfs_audio_pointers_on_main']}")
    for name, values in report["groups"].items():
        print(f"{name}: main={values['main']} offline={values['offline']} missing={values['missing']} changed={values['changed']}")
    if missing:
        print("\nMissing paths:")
        print("\n".join(missing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
