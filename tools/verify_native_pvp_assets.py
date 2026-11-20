#!/usr/bin/env python3
"""Verify original Arena/Guild sprites; strict mode rejects Git LFS pointers.

Run in release worktree AFTER Git LFS hydration and BEFORE deploying/restarting:
    python3 tools/verify_native_pvp_assets.py --strict

Default mode supports GitHub Actions' LFS pointer checkout by validating metadata
and names without mistaking pointer text for a rendered PNG.
"""
from __future__ import annotations

import argparse
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ('web/assets/arena', 'web/assets/guild', 'web/assets/sprite')
SINGLES = (
    'web/assets/menus/arena-cross.png',
    'web/assets/original-ui/battle_hp_bar_bg_new.png',
    'web/assets/original-ui/battle_hp_bar1.png',
)
PNG = b'\x89PNG\r\n\x1a\n'
POINTER = b'version https://git-lfs.github.com/spec/v1\n'
HASH = re.compile(r'^oid sha256:([a-f0-9]{64})$', re.M)
SIZE = re.compile(r'^size ([1-9][0-9]*)$', re.M)


def inspect_image(path: Path, *, strict: bool) -> str:
    if not path.is_file():
        raise ValueError(f'Thiếu tài nguyên: {path}')
    with path.open('rb') as stream:
        head = stream.read(512)
    if head.startswith(PNG):
        if len(head) < 24 or head[12:16] != b'IHDR':
            raise ValueError(f'PNG bị lỗi header: {path}')
        width, height = struct.unpack('>II', head[16:24])
        if not 1 <= width <= 16384 or not 1 <= height <= 16384:
            raise ValueError(f'PNG kích thước bất thường: {path}')
        return 'png'
    if head.startswith(POINTER):
        metadata = head.decode('ascii', 'strict')
        if not HASH.search(metadata) or not SIZE.search(metadata):
            raise ValueError(f'Con trỏ Git LFS không hợp lệ: {path}')
        if strict:
            raise ValueError(f'Git LFS chưa tải PNG gốc: {path}')
        return 'lfs'
    raise ValueError(f'Tài nguyên không phải PNG hay Git LFS: {path}')


def verify(root: Path, *, strict=False) -> dict[str, int]:
    files = []
    for folder in GROUPS:
        base = root / folder
        if not base.is_dir():
            raise ValueError(f'Thiếu thư mục sprite gốc: {base}')
        files.extend(sorted(base.rglob('*.png')))
    files.extend(root / single for single in SINGLES)
    if len(files) < 30:
        raise ValueError('Thiếu tập tài nguyên Arena/Bang Hội gốc')
    count = {'png': 0, 'lfs': 0}
    for file in files:
        count[inspect_image(file, strict=strict)] += 1
    return count


def main():
    parser = argparse.ArgumentParser(description='Kiểm tra hình Arena/Guild gốc GXB3')
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--strict', action='store_true', help='Bắt buộc ảnh thật; chặn Git LFS pointers khi release')
    args = parser.parse_args()
    try:
        stats = verify(args.root, strict=args.strict)
    except (ValueError, OSError, UnicodeError) as exc:
        parser.exit(2, f'FAIL | {exc}\n')
    print('PASS | Arena/Guild original assets:', stats['png'], 'PNG,', stats['lfs'], 'Git LFS pointers')
    if stats['lfs'] and not args.strict:
        print('NOTICE | Checkout này cần git lfs pull trước khi làm bản phát hành.')


if __name__ == '__main__':
    main()
