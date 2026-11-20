# GXB 3 · Release Checklist

Nhánh phát hành hiện tại: `snez-vietnamese`.

## Gate bắt buộc trước public release

- [ ] GitHub Actions của HEAD xanh.
- [ ] `GXB3_PRODUCTION=1`.
- [ ] `GXB3_PUBLIC_ORIGIN` là HTTPS thật.
- [ ] `GXB3_ADMIN_KEY` là secret ngẫu nhiên >= 24 ký tự, không dùng key dev cũ.
- [ ] PostgreSQL production đã bật và migration/backup đã kiểm tra.
- [ ] Reverse proxy HTTPS hoạt động; không expose legacy TCP 9081 ra Internet.
- [ ] `GXB3_TRUST_PROXY=1` chỉ khi proxy là trusted hop.
- [ ] `python tools/production_preflight.py` PASS trên chính máy/container phát hành.
- [ ] `python3 tools/verify_native_pvp_assets.py --strict` PASS **trước khi restart hoặc chuyển traffic**; phải là PNG thật, không phải Git LFS pointer. Khi cần: `git lfs pull` rồi kiểm tra lại.
- [ ] Battle runtime PASS bằng LuaJIT tương thích của target; không chấp nhận CI skip làm bằng chứng runtime.
- [ ] `GET /healthz` trả 200.
- [ ] `GET /readyz` trả 200 và `ready:true`.
- [ ] `python tools/release_smoke.py --base-url https://...` PASS; nếu có smoke account thì login/auth/leaderboard/guild/logout đều PASS.
- [ ] Backup PostgreSQL thử restore được vào DB test.
- [ ] Test ít nhất 2 account thật: Register → Login → Guild → PvP → Mail → restart → dữ liệu còn nguyên.
- [ ] Test Guild War hai Guild thật và reward settlement sau khi hết thời gian.
- [ ] Test đơn nạp: tạo order → SUPER GM duyệt → mail reward → claim đúng một lần.
- [ ] Kiểm tra rate-limit bằng login sai/repeat request; không có endpoint nhạy cảm bypass.
- [ ] Không có secret thật nằm trong Git repository hoặc browser JS.

## Private beta

Có thể mở private beta nhóm nhỏ sau khi:
- CI xanh;
- HTTPS + PostgreSQL + secret admin đúng;
- production preflight PASS;
- backup có bản đầu tiên.

## Public đông người

Trước khi scale lớn nên chuyển transport từ `ThreadingHTTPServer` sang ASGI và dùng Redis/shared rate-limit/pub-sub. Domain/storage layer PostgreSQL hiện tại có thể giữ lại.
