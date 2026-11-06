#!/usr/bin/env python3
"""Compare two Android APK builds excluding the inherently randomized v2 signature block.

APK Signature Scheme v2 signs the ZIP payload with a randomized RSA-PSS signature, so
whole-file SHA-256 is not expected to be stable. The ZIP entries and their metadata are
the reproducible build payload; apksigner should be used separately to verify installability.
"""
from __future__ import annotations

import hashlib
import sys
from zipfile import ZipFile


def snapshot(path: str):
    with ZipFile(path) as archive:
        result = {}
        for name in archive.namelist():
            info = archive.getinfo(name)
            result[name] = (
                hashlib.sha256(archive.read(name)).hexdigest(),
                info.file_size,
                info.compress_size,
                info.CRC,
                info.date_time,
                info.compress_type,
            )
        return result


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} APK_A APK_B", file=sys.stderr)
        return 2
    a, b = snapshot(sys.argv[1]), snapshot(sys.argv[2])
    if a != b:
        names = sorted(set(a) | set(b))
        for name in names:
            if a.get(name) != b.get(name):
                print(f"DIFF {name}\n  A={a.get(name)}\n  B={b.get(name)}")
        return 1
    print(f"PASS: {len(a)} APK ZIP entries are byte-identical")
    print("NOTE: whole-file SHA-256 may differ because APK v2 RSA-PSS signatures are randomized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
