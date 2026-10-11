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
- player gameplay profiles
- player battle history
- online presence
- leaderboard

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
- Gameplay save per-world đã có PostgreSQL shared storage theo UID + Server; transaction gameplay khóa row profile bằng `FOR UPDATE` để tránh hai instance ghi đè cùng lúc.
- Redis/session/rate-limit khi chạy nhiều instance.
- HTTPS/reverse proxy.
- backup/restore.
- metrics/logging có redaction.
- CSRF strategy nếu bổ sung cross-site frontend.
- centralized audit và payment reconciliation.


## Online presence / Leaderboard foundation

Khi player snapshot được cập nhật, server ghi:
- online presence theo UID + Server
- level
- team power
- timestamp

API authenticated:
- `GET /api/world/online?server_id=S1`
- `GET /api/leaderboard?server_id=S1&limit=100`

SUPER GM Dashboard hiển thị số người online hiện tại. Đây là nền dùng chung cho leaderboard, matchmaking, guild online state và PvP ở chặng sau.


## Shared Guild / PvP foundation

### Shared Guild theo Server

Guild online mới dùng database chung, tách khỏi guild NPC/local cũ.

- Một nhân vật chỉ thuộc một Guild trong một Server.
- Guild có leader, member list, notice, level/exp và capacity.
- UI Guild ở thanh điều hướng mở Shared Guild Hub.
- Có tạo Guild, xem danh sách Guild, tham gia và rời/giải tán.
- Member power/last_seen được lưu trên shared database.

### Matchmaking PvP

Các mode hiện có ở matchmaking layer:

- `arena`: cùng Server.
- `team`: cùng Server.
- `cross`: cho phép ghép khác Server.

Queue ưu tiên combat power gần nhất rồi thời gian chờ.

Khi tìm được đối thủ, hệ thống tạo match ID dạng `PVP-...` và một seed chung. Mỗi client gửi heartbeat/ready state; khi cả hai peer còn online và ready, match session chuyển sang `active`.

Các endpoint chính:

- `GET /api/pvp/status?mode=arena`
- `POST /api/pvp/queue`
- `POST /api/pvp/match/heartbeat`
- `POST /api/pvp/match/session`

Online Hub polling heartbeat khoảng 2.5 giây khi màn PvP đang mở.

**Chưa coi đây là battle-result authority cuối cùng.** Matchmaking/session/peer synchronization đã có; bước kế tiếp là server-authoritative combat snapshot/result validation để không tin kết quả do client tự gửi.


## Server-authoritative PvP combat

PvP không nhận trường `winner` hoặc kết quả chiến đấu từ client.

Luồng hiện tại:

1. Matchmaking tạo match ID + deterministic seed.
2. Cả hai peer gửi heartbeat/ready.
3. Chỉ khi session có đủ hai peer ready thì endpoint battle mới chạy.
4. Server tải save thật của `player_a` và `player_b` theo UID + Server.
5. Server lấy formation + hero data trực tiếp từ save.
6. Lua battle engine chạy ở server bằng seed của match.
7. `isWin` từ battle report quyết định winner.
8. Server ghi snapshots, battle report, winner và rating delta vào `pvp_matches`.
9. Nếu hai client cùng yêu cầu xử lý, kết quả đã hoàn tất được reuse thay vì client ghi đè.

Endpoint:
- `POST /api/pvp/match/battle`
- `POST /api/pvp/match/result`

### PvP Season / Rating

Season ID hiện dùng tháng UTC dạng `YYYY-MM`.

Mỗi mode có rating riêng:
- arena
- team
- cross

Rating khởi đầu: 1000. Sau trận authoritative, ELO K=32 cập nhật:
- rating
- wins
- losses
- matches

Online Hub hiển thị rating hiện tại, W/L, lịch sử trận và top mùa.

### Giới hạn hiện tại

Combat result đã là server-authoritative. Battle adapter hiện truyền team, Pet, Guild Skills và Chime bonus cho cả A/B. Tuy nhiên vẫn cần runtime test bằng LuaJIT thực tế để xác nhận toàn bộ bonus phía B được original battle bytecode áp dụng đúng như phía A trước khi coi PvP balance là final.


## Guild management / Guild War

Shared Guild hiện hỗ trợ quyền:

- `leader`
- `deputy`
- `member`

Luồng vào Guild dùng **Application**; API direct join cũ đã được đổi thành tạo đơn để không bypass duyệt.

Leader:
- duyệt/từ chối đơn
- bổ nhiệm/hạ Deputy
- kick member/deputy
- chuyển Leader
- sửa notice
- gửi Guild Mail
- tạo Guild War

Deputy:
- duyệt/từ chối đơn
- kick member thường
- sửa notice
- gửi Guild Mail
- tạo Guild War

Guild Chat:
- member/Deputy/Leader gửi tin nhắn tối đa 280 ký tự
- chat lưu shared DB theo guild_id
- UI tải 100 tin gần nhất

Guild Mail:
- Leader/Deputy gửi thông báo đến toàn bộ thành viên
- mỗi thành viên nhận một mail cá nhân trong mailbox
- audit log ghi sender, guild và số recipient

Guild Ranking:
- xếp theo tổng Power thành viên, sau đó level/exp

Guild War:
- Leader/Deputy thách đấu Guild cùng Server.
- tạo war ID `GW-...`.
- combat server-authoritative giữa member hai Guild.
- score A/B, battle history, Contribution, Guild EXP/Level.
- tự settlement khi hết thời gian và gửi reward qua mailbox.

## PvP season rewards

Reward tier nằm trong `data/pvp_season_rewards.json`.

- Mỗi mode có bảng tier riêng.
- Season hiện tại theo UTC `YYYY-MM`.
- Người chơi chỉ claim **mùa trước**.
- Phải có ít nhất 1 trận trong mùa.
- Claim được ghi vào `pvp_season_claims`, chống nhận lặp.
- Reward được gửi qua mailbox để player tự nhận.
- Online Hub hiển thị eligibility, reward và trạng thái claimed.


## Guild War combat / progression

Guild War hiện có combat server-authoritative:

1. Member mở một Guild War đang `active`.
2. Chọn thành viên Guild đối phương.
3. Server xác minh attacker/defender thuộc đúng hai Guild.
4. Server tải save thật của cả hai UID trong cùng Server.
5. Battle engine chạy server-side với team + Pet + Guild Skills + Chime bonus A/B.
6. Server ghi battle report và cộng score vào Guild thắng lượt.
7. Thành viên hai phía nhận Contribution; hai Guild nhận EXP.
8. Guild Level tự tăng theo EXP, mặc định 5.000 EXP/level, tối đa level 20.

Một attacker chỉ được đánh cùng một defender một lần trong cùng Guild War. Score/reward/progression cấu hình tại `data/guild_online_config.json`.

Khi `ends_at` tới:
- maintenance loop chuyển war sang `finished`;
- xác định winner theo score A/B;
- reward winner/loser/draw được gửi qua mailbox;
- `guild_war_claims` bảo đảm settlement idempotent, không phát quà lặp.

Background maintenance chạy mỗi 30 giây và đồng thời dọn PvP queue/session cũ.

## Realtime SSE transport

Online Hub không còn phụ thuộc polling PvP 2,5 giây làm transport chính.

Authenticated endpoint:

```text
GET /api/events/stream?mode=arena
Content-Type: text/event-stream
```

Server gửi event `snapshot` chứa:
- server time
- online count
- PvP session/status
- Guild summary
- Guild War state

Browser dùng `EventSource`, tự reconnect khi stream được rotate. Server giữ mỗi stream khoảng 40 giây để tránh connection sống vô hạn trên transport hiện tại. Nếu browser không hỗ trợ EventSource thì UI fallback polling 5 giây.

Reverse proxy production phải tắt buffering cho SSE. App đã gửi `X-Accel-Buffering: no`.

Với tải lớn hoặc realtime battle input tốc độ cao, bước scale tiếp theo vẫn nên chuyển transport sang ASGI/WebSocket + Redis pub/sub. SSE hiện phù hợp cho state/event updates của Online Hub, Guild và matchmaking; battle simulation vẫn chạy server-authoritative theo request.
