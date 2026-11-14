#!/usr/bin/env python3
"""Root-console recovery of one existing GXB3 account after lost password + recovery code.

No web endpoint. No account creation. Exact owner UID + username + configured owner
email must match the active Neon account. Changes only auth credentials, recovery
code, and that account's sessions; gameplay data is never touched.
"""
from __future__ import annotations
import getpass
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_UID = "GXB3-00000001"
TARGET_USERNAME = "Admin"
KEYS = ("DATABASE_URL", "GXB3_DATABASE_URL", "GXB3_OWNER_UID", "GXB3_OWNER_EMAIL")


def load_service_environment(service="gxb3"):
    result = subprocess.run(
        ["systemctl", "show", "--property=MainPID", "--value", service],
        capture_output=True, text=True, check=True, timeout=10,
    )
    value = result.stdout.strip()
    if not value.isdigit() or int(value) <= 1:
        raise RuntimeError("Không xác định được tiến trình GXB3 đang chạy")
    pid = int(value)
    raw = (Path("/proc") / str(pid) / "environ").read_bytes()
    found = {}
    for item in raw.split(b"\0"):
        if b"=" not in item:
            continue
        k, v = item.split(b"=", 1)
        name = k.decode("ascii", "replace")
        if name in KEYS:
            found[name] = v.decode("utf-8")
    if not (found.get("GXB3_DATABASE_URL") or found.get("DATABASE_URL")):
        raise RuntimeError("Không đọc được Neon URL từ tiến trình game")
    if found.get("GXB3_OWNER_UID") != TARGET_UID:
        raise RuntimeError("Cấu hình chủ sở hữu VPS không khớp UID yêu cầu")
    if not found.get("GXB3_OWNER_EMAIL"):
        raise RuntimeError("Thiếu email chủ sở hữu đã cấu hình trên VPS")
    for key in KEYS:
        if key in found:
            os.environ[key] = found[key]
        else:
            os.environ.pop(key, None)
    return pid


def reset_existing_owner_account(password, recovery_code):
    from gxb2 import auth, database
    password = auth._clean_password(password)
    if not database.is_postgres():
        raise RuntimeError("Chỉ cho phép thao tác trên Neon PostgreSQL")
    expected_email = os.environ["GXB3_OWNER_EMAIL"].strip().casefold()
    if os.environ.get("GXB3_OWNER_UID") != TARGET_UID or not expected_email:
        raise RuntimeError("Thiếu định danh chủ sở hữu hợp lệ")
    salt = secrets.token_bytes(16)
    password_hash = auth._hash_password(password, salt)
    code_hash = auth._recovery_hash(recovery_code)
    now = int(time.time())
    db = auth._db()
    try:
        db.execute("BEGIN IMMEDIATE")
        rows = db.execute(
            """SELECT id,uid,username,email,status FROM accounts
               WHERE uid=? AND lower(username)=lower(?) AND lower(trim(email))=?""",
            (TARGET_UID, TARGET_USERNAME, expected_email),
        ).fetchall()
        if len(rows) != 1 or rows[0]["status"] != "active":
            raise RuntimeError("Không xác minh được duy nhất tài khoản SUPER GM trên Neon")
        account_id = int(rows[0]["id"])
        db.execute(
            "UPDATE accounts SET password_hash=?,salt=? WHERE id=? AND uid=?",
            (password_hash, salt.hex(), account_id, TARGET_UID),
        )
        if db.backend == "postgres":
            db.execute(
                """INSERT INTO recovery_codes(account_id,code_hash,created_at,used_at)
                   VALUES(?,?,?,0) ON CONFLICT(account_id) DO UPDATE SET
                   code_hash=excluded.code_hash,created_at=excluded.created_at,used_at=0""",
                (account_id, code_hash, now),
            )
        else:
            auth._save_recovery(db, account_id, code_hash, now, 0)
        db.execute("DELETE FROM sessions WHERE account_id=?", (account_id,))
        db.commit()
        return {"uid": TARGET_UID, "username": TARGET_USERNAME}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    if os.name != "posix" or not hasattr(os, "geteuid") or os.geteuid() != 0:
        raise RuntimeError("Chỉ chạy bằng root trên VPS")
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise RuntimeError("Cần terminal tương tác; không chạy qua API, pipe hoặc cron")
    os.chdir(ROOT)
    pid = load_service_environment()
    sys.path.insert(0, str(ROOT))
    from gxb2 import database
    if not database.is_postgres():
        raise RuntimeError("Cấu hình hiện tại không trỏ tới Neon PostgreSQL")
    print("\n=== KHÔI PHỤC TÀI KHOẢN GXB3 ĐÃ TỒN TẠI ===")
    print("Dịch vụ PID:", pid)
    print("Tài khoản đích:", TARGET_UID, "|", TARGET_USERNAME)
    print("Email chủ sở hữu được đối chiếu trực tiếp trong Neon; không hiển thị.")
    print("Chỉ cập nhật mật khẩu + mã khôi phục + thu hồi phiên đăng nhập.")
    print("Không sửa UID, nhân vật, bang hội, thư, vật phẩm, Crystal, VNĐ.")
    if input("Gõ RESET ADMIN để xác nhận đúng tài khoản: ").strip() != "RESET ADMIN":
        print("Đã hủy, không thay đổi dữ liệu.")
        return 1
    password = getpass.getpass("Mật khẩu mới (ẩn): ")
    confirm = getpass.getpass("Nhập lại mật khẩu mới (ẩn): ")
    if password != confirm:
        raise ValueError("Hai mật khẩu không khớp; không thay đổi dữ liệu")
    from gxb2 import auth
    auth._clean_password(password)
    recovery = auth._new_recovery_code()
    if input("Gõ XAC NHAN RESET để ghi vào Neon: ").strip() != "XAC NHAN RESET":
        print("Đã hủy, không thay đổi dữ liệu.")
        return 1
    result = reset_existing_owner_account(password, recovery)
    password = confirm = ""
    print("\nTHÀNH CÔNG:", result["uid"], result["username"])
    print("Mã khôi phục mới (chỉ hiển thị lần này):", recovery)
    print("Lưu mã ở nơi an toàn. Tất cả phiên cũ đã bị thu hồi.")
    print("Đăng nhập lại bằng mật khẩu mới. Dữ liệu game được giữ nguyên.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print("DỪNG AN TOÀN:", exc, file=sys.stderr)
        sys.exit(1)
