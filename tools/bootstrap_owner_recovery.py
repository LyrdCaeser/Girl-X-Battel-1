#!/usr/bin/env python3
"""First-time SUPER GM Authenticator bootstrap from local VPS root console.

This is NOT a web endpoint or a password bypass for remote users. It requires
physical/SSH root terminal access to the existing GXB3 systemd service and the
live PostgreSQL backend. It changes only the dedicated owner-security tables;
NEVER alters game accounts, player profiles, currencies, sessions, or mail.
"""
from __future__ import annotations

import base64
import getpass
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYS_TO_COPY = (
    "DATABASE_URL", "GXB3_DATABASE_URL",
    "GXB3_ADMIN_KEY", "GXB3_GIFTCODE_PANEL_KEY", "GXB3_GM_ACTION_KEY",
    "GXB3_OWNER_UID", "GXB3_OWNER_EMAIL",
)


def load_running_service_environment(service="gxb3"):
    """Import only required values from *running* root-owned systemd service.

    Never display or write secrets. Do not trust shell-provided DATABASE_URL:
    it might silently point to a different database. The server process's
    environment is the authoritative deployment configuration.
    """
    result = subprocess.run(
        ["systemctl", "show", "--property=MainPID", "--value", service],
        capture_output=True, text=True, check=True, timeout=10,
    )
    if not result.stdout.strip().isdigit():
        raise RuntimeError("Không xác định được tiến trình GXB 3 đang chạy")
    pid = int(result.stdout.strip())
    if pid <= 1:
        raise RuntimeError("Dịch vụ GXB 3 chưa chạy; không thay đổi dữ liệu")
    target = Path("/proc") / str(pid) / "environ"
    data = target.read_bytes()
    environment = {}
    for part in data.split(b"\x00"):
        if b"=" not in part:
            continue
        key, value = part.split(b"=", 1)
        label = key.decode("ascii", "replace")
        if label in KEYS_TO_COPY:
            environment[label] = value.decode("utf-8")
    if not (environment.get("GXB3_DATABASE_URL") or environment.get("DATABASE_URL")):
        raise RuntimeError("Không thấy cấu hình Neon trong tiến trình server; dừng an toàn")
    for name in ("GXB3_ADMIN_KEY", "GXB3_GIFTCODE_PANEL_KEY", "GXB3_GM_ACTION_KEY"):
        if name not in environment:
            raise RuntimeError("Không đọc được cấu hình khóa server; không tự tạo hoặc xóa khóa")
    for name in KEYS_TO_COPY:
        if name in environment:
            os.environ[name] = environment[name]
        else:
            os.environ.pop(name, None)
    # _master() requires stable original 3 VPS secrets even after key overrides.
    return pid


def _canonical_owner():
    return (
        os.environ.get("GXB3_OWNER_UID", "GXB3-00000001").strip(),
        os.environ.get("GXB3_OWNER_EMAIL",
                       "trieuquangholuxury@gmail.com").strip().casefold(),
    )


def validate_owner_record(db, uid, email):
    """Require exactly the same canonical active owner identity as server.py."""
    if not uid or not email:
        raise RuntimeError("VPS chưa xác định chủ tài khoản")
    row = db.execute(
        """SELECT id FROM accounts WHERE uid=? AND LOWER(TRIM(email))=?
           AND status='active'""", (uid, email),
    ).fetchall()
    if len(row) != 1:
        raise RuntimeError("Không tìm thấy duy nhất tài khoản SUPER GM hợp lệ trên Neon")
    return row[0]["id"]


def assert_unenrolled(db, uid, recovery):
    row = recovery._read(db, locked=True)
    if row is not None:
        if str(row["owner_uid"]) != uid:
            raise RuntimeError("Bảng bảo mật thuộc chủ tài khoản khác; dừng an toàn")
        if int(row["enrolled"]) != 0:
            raise RuntimeError("Authenticator đã liên kết; không được ghi đè từ công cụ ban đầu")


def apply_first_time_recovery(nonce, counter, new_keys):
    """Commit only owner_security + three hashed override keys + backup hashes."""
    from gxb2 import owner_recovery as recovery

    recovery._master()
    new_keys = recovery._validate_new_keys(new_keys)
    owner_uid, owner_email = _canonical_owner()
    db = recovery._db()
    try:
        db.execute("BEGIN IMMEDIATE")
        validate_owner_record(db, owner_uid, owner_email)
        assert_unenrolled(db, owner_uid, recovery)
        now = int(time.time())
        db.execute(
            """INSERT INTO owner_security(
                id, owner_uid, nonce, enrolled, pending_nonce,
                pending_session, pending_at, last_counter, version,
                failures, blocked_until, updated_at
             ) VALUES (1, ?, ?, 1, '', '', 0, ?, 1, 0, 0, ?)
             ON CONFLICT(id) DO UPDATE SET
                nonce=excluded.nonce, enrolled=1, pending_nonce='',
                pending_session='', pending_at=0, last_counter=excluded.last_counter,
                version=owner_security.version+1, failures=0,
                blocked_until=0, updated_at=excluded.updated_at""",
            (owner_uid, nonce, int(counter), now),
        )
        for name in recovery.KEY_FIELDS:
            salt, digest = recovery._hash_key(new_keys[name])
            db.execute(
                """INSERT INTO owner_key_overrides(key_name,salt,key_hash)
                    VALUES (?,?,?) ON CONFLICT(key_name) DO UPDATE
                    SET salt=excluded.salt,key_hash=excluded.key_hash""",
                (name, salt, digest),
            )
        backups = recovery._new_backups(db)
        recovery._event(db, owner_uid, "owner.root.bootstrap.first_time")
        db.commit()
        return backups
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _ask_new_keys(recovery):
    labels = {
        "admin": "Khóa quản trị GXB 3",
        "panel": "Khóa bảo vệ trang chủ",
        "gm": "Khóa hành động QTV",
    }
    while True:
        keys = {}
        for name in recovery.KEY_FIELDS:
            first = getpass.getpass(f"{labels[name]} MỚI (ẩn): ")
            second = getpass.getpass("Nhập lại khóa (ẩn): ")
            if first != second:
                raise ValueError("Hai lần nhập khóa không trùng; chưa thay đổi dữ liệu")
            keys[name] = first
        return recovery._validate_new_keys(keys)


def main():
    if os.name != "posix" or not hasattr(os, "geteuid") or os.geteuid() != 0:
        raise RuntimeError("Chỉ chạy trên VPS qua terminal root (UID 0)")
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise RuntimeError("Phải dùng terminal tương tác; không chạy qua cron/API/pipe")
    os.chdir(ROOT)
    pid = load_running_service_environment()
    sys.path.insert(0, str(ROOT))
    from gxb2 import database, owner_recovery as recovery
    if not database.is_postgres():
        raise RuntimeError("Chỉ cho phép khôi phục trên Neon PostgreSQL đã cấu hình")
    recovery._master()
    uid, email = _canonical_owner()
    db = recovery._db()
    try:
        validate_owner_record(db, uid, email)
        assert_unenrolled(db, uid, recovery)
    finally:
        db.close()

    print("\n=== GXB 3: BOOTSTRAP AUTHENTICATOR BẰNG ROOT VPS ===")
    print("Đã xác minh dịch vụ gxb3 PID", pid, "và chủ SUPER GM trên Neon.")
    print("KHÔNG thay đổi tài khoản, nhân vật, vật phẩm hoặc tiến trình game.")
    print("Chỉ chạy khi Authenticator CHƯA được liên kết.")
    if input("Gõ KHOI PHUC để tiếp tục: ").strip() != "KHOI PHUC":
        print("Đã hủy an toàn.")
        return 1

    keys = _ask_new_keys(recovery)
    nonce = secrets.token_urlsafe(32)
    seed = base64.b32encode(recovery._secret(nonce)).decode().rstrip("=")
    print("\n=== GOOGLE AUTHENTICATOR ===")
    print("1) Điện thoại: Google Authenticator > (+) > Nhập khóa thiết lập.")
    print("2) Tên tài khoản: Goddess Battle 3 - SUPER GM")
    print("3) Loại mã: Theo thời gian (TOTP).")
    print("4) KHÓA THIẾT LẬP (chỉ nhập vào điện thoại, KHÔNG gửi chat):")
    print(seed)
    print("\nBước này chưa ghi khóa nào vào cơ sở dữ liệu.")
    start = time.monotonic()
    counter = None
    for attempt in range(3):
        if time.monotonic() - start > 600:
            raise RuntimeError("Quá 10 phút; chưa thay đổi dữ liệu, hãy chạy lại")
        code = input("Nhập mã 6 số đang hiện trong ứng dụng: ").strip()
        counter = recovery._counter(nonce, code, -1)
        if counter is not None:
            break
        print("Mã chưa đúng hoặc hết hạn. Hãy kiểm tra đồng hồ trên điện thoại.")
    if counter is None:
        raise RuntimeError("Không xác minh được mã; chưa thay đổi dữ liệu")
    if input("Gõ XAC NHAN để lưu liên kết và thay cả 3 khóa: ").strip() != "XAC NHAN":
        print("Đã hủy; chưa thay đổi dữ liệu.")
        return 1

    backups = apply_first_time_recovery(nonce, counter, keys)
    keys.clear()
    print("\n=== THÀNH CÔNG: AUTHENTICATOR ĐÃ LIÊN KẾT ===")
    print("3 khóa quản trị MỚI đã có hiệu lực; khóa cũ bị vô hiệu hóa.")
    print("8 mã dự phòng (MỖI MÃ MỘT LẦN — chỉ in tại terminal này):")
    for item in backups:
        print(item)
    print("Lưu vào trình quản lý mật khẩu; KHÔNG chụp/gửi terminal có mã dự phòng.")
    print("Không cần restart dịch vụ. Dữ liệu game không bị thay đổi.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print("DỪNG AN TOÀN:", exc, file=sys.stderr)
        sys.exit(1)
