# GXB 3 · Production / Public Server Notes

> Trạng thái: nền tảng multi-user đang được chuyển từ bản Local sang server nhiều tài khoản. Tài liệu này mô tả cách chạy lớp HTTP hiện tại sau reverse proxy; chưa thay thế cho một production framework chuyên dụng.

## Bind HTTP

Mặc định server chỉ lắng nghe localhost:

```powershell
python server.py --http-host 127.0.0.1 --http-port 9080
```

Khi đặt sau reverse proxy trên VPS/container:

```powershell
$env:GXB3_HOST="0.0.0.0"
$env:PORT="9080"
$env:GXB3_PUBLIC_ORIGIN="https://game.example.com"
python server.py
```

Legacy TCP battle socket vẫn chỉ bind `127.0.0.1`; không được expose trực tiếp ra Internet.

## Database backend

Mặc định dev/local vẫn dùng SQLite:

- Account DB: `state/auth.sqlite3`
- Live service DB: `state/live_service.sqlite3`

Production có thể bật PostgreSQL cho **Auth + Live Service** bằng một biến:

```powershell
$env:GXB3_DATABASE_URL="postgresql://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require"
```

Có thể dùng `DATABASE_URL` thay cho `GXB3_DATABASE_URL`. Khi biến này tồn tại, app tự chuyển Auth, Session, World, Player Registry, GM Mail, Orders và Audit sang PostgreSQL với connection pool.

Pool mặc định:

```text
GXB3_DB_POOL_MIN=1
GXB3_DB_POOL_MAX=12
```

Player gameplay save hiện vẫn nằm riêng tại `state/players/<UID>/<SERVER>.sqlite3`; đây là lớp tiếp theo cần chuyển khỏi local disk khi triển khai nhiều instance.

### Chuyển dữ liệu SQLite hiện có sang PostgreSQL

Kiểm tra trước:

```powershell
python tools/migrate_sqlite_to_postgres.py --database-url "$env:GXB3_DATABASE_URL" --dry-run
```

Migration:

```powershell
python tools/migrate_sqlite_to_postgres.py --database-url "$env:GXB3_DATABASE_URL"
```

Script migrate:
- accounts
- sessions
- recovery codes
- login attempts
- worlds
- players
- GM mail
- orders
- audit log

Sau khi kiểm tra dữ liệu PostgreSQL đầy đủ mới đặt `GXB3_DATABASE_URL` cho server production.

## Auth
- Player save: `state/players/<UID>/<SERVER>.sqlite3`
- Mật khẩu: PBKDF2-HMAC-SHA256 + salt riêng.
- Session cookie: `HttpOnly; SameSite=Lax`; khi reverse proxy gửi `X-Forwarded-Proto: https`, cookie có thêm `Secure`.
- Session TTL mặc định: 30 ngày.
- Người chơi có thể xem và thu hồi từng phiên.
- SUPER GM có thể xem metadata phiên và thu hồi toàn bộ phiên của tài khoản.

## Recovery

Khi đăng ký, người chơi được cấp một **mã khôi phục** chỉ hiển thị ở bước tạo tài khoản. Hệ thống chỉ lưu SHA-256 của mã.

- Quên mật khẩu cần: username + mã khôi phục + mật khẩu mới.
- Reset thành công thu hồi toàn bộ session cũ.
- Mã khôi phục chỉ dùng một lần.
- Người chơi đang đăng nhập có thể tạo mã khôi phục mới; mã cũ lập tức mất hiệu lực.

Không có luồng "gửi lại mã bằng username" vì điều đó sẽ cho phép người khác chiếm tài khoản nếu chỉ biết tên đăng nhập.

## World policy

SUPER GM có thể đặt riêng cho từng server:

- `status`: `online`, `maintenance`, `closed`
- `registration_open`: cho phép/tắt đăng ký account mới vào server.
- `character_creation_open`: cho phép/tắt tạo nhân vật mới ở server.
- `message`: thông báo/lý do hiển thị khi policy chặn thao tác.

## Reverse proxy

Production public nên dùng HTTPS tại Nginx/Caddy/Cloudflare/Render proxy và forward đến HTTP process nội bộ. Không expose file SQLite hoặc thư mục `state/`.

Các header ứng dụng đang gửi:
- Content-Security-Policy
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy

## Trước khi mở public đông người

HTTP server hiện tại vẫn dựa trên Python `ThreadingHTTPServer`. Nó phù hợp cho dev/private beta nhỏ nhưng chưa phải kiến trúc cuối cho tải lớn.

Trước public scale cần chuyển lớp transport sang production ASGI/WSGI service, thêm:
- PostgreSQL cho account/live-service: **đã có adapter + connection pool + migration utility**.
- Gameplay save per-world vẫn cần chuyển khỏi SQLite local disk để chạy nhiều instance stateless.
- Redis/session/rate-limit khi chạy nhiều instance.
- HTTPS/reverse proxy.
- backup/restore.
- metrics/logging có redaction.
- CSRF strategy nếu bổ sung cross-site frontend.
- centralized audit và payment reconciliation.
