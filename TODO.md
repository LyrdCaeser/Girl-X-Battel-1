# TODO — Hoàn thiện Android offline-mode

Phạm vi chuẩn: [`docs/QUYET_DINH_ANDROID_OFFLINE.vi.md`](docs/QUYET_DINH_ANDROID_OFFLINE.vi.md). Mục tiêu là bản Android mở và chơi được không cần máy chủ game; internet chỉ dùng cho thao tác tải/cập nhật tài nguyên do người chơi chủ động chọn. Offline save là nguồn dữ liệu có thẩm quyền; không tự fallback sang production. Pipeline tài nguyên đã được đẩy ở commit `f9ff576d`; các thay đổi Android còn lại đang chờ giai đoạn 2.

## A. Release tài nguyên và local shell — đang làm dở

- [~] Tạo release tài nguyên bất biến từ allowlist đã duyệt; hydrate và xác minh toàn bộ Git LFS payload thật; sinh manifest có version, byte size, SHA-256 và chữ ký Ed25519; xuất bản HTTPS versioned manifest/packs và cấu hình URL, trusted hosts, pinned public key vào đúng APK build. Đã sửa lệch short/full SHA, publisher fail-closed, workflow pack thành công ở run [42533667739](https://github.com/LyrdCaeser/Girl-X-Battel-1/actions/runs/42533667739), version `web-f9ff576d09008e445c2cdce31607f86fb21a8960`; manifest HTTP 200 và 97/97 URL trả HTTP 206. Cấu hình Android release gate đã có trong working tree nhưng chưa đẩy.
- [~] App báo dung lượng cần tải, tiến độ/gói đang tải, cho phép hủy và tiếp tục sau mất mạng/thoát app; chỉ kích hoạt release sau khi toàn bộ resource bắt buộc đã được kiểm tra. Worker/WorkManager có progress theo byte/gói, cancel, staging `.part`, HTTP Range resume, storage reserve và activate nguyên tử; chưa có live test tải toàn pack trên thiết bị, UI chưa hiển thị estimate dung lượng trước khi xác nhận.
- [ ] Cài gói, force-stop, bật airplane mode, mở lại app và tải được local shell cùng toàn bộ resource core đã khai báo; log không có request đến game server/production.

## B. Hồ sơ khách, local save/API và campaign vertical slice — đang làm dở

- [~] Chế độ **Chơi offline** dùng hồ sơ khách cục bộ riêng, khởi tạo save bền vững và không yêu cầu tài khoản/server; UI khởi động game phải dùng API local, không chờ đăng nhập online. Đã có guest UI/local API/session bền vững và logout; 31 JVM tests cùng `node --check web/auth.js` đạt. Còn thiếu smoke-test WebView/airplane mode trên thiết bị.
- [ ] Boot, catalog thiết yếu, campaign, chọn đội hình, chiến đấu, nhận thưởng và lưu/đọc tiến trình chạy local. Bắt đầu bằng một lát dọc campaign có thể kiểm thử đầu-cuối; dùng battle engine có thật, không tạo chiến thắng/phần thưởng chỉ từ giao diện.
- [ ] Chọn và kiểm chứng phương án engine local trên thiết bị Android; nối engine LuaJIT/native vào state/action/save/frontend hoặc chứng minh phương án tương đương. Không đưa PostgreSQL, credential production hay secret phát hành vào APK.
- [ ] Khởi tạo guest profile, chơi một stage, nhận reward, force-stop/reopen và giữ đúng tiến trình trong airplane mode; save migration/backup không làm hỏng dữ liệu.

## C. Mở rộng single-player, tài nguyên và ranh giới online — chưa hoàn tất

- [ ] Lập ma trận endpoint theo màn hình; chuyển các hệ thống single-player đã cam kết sang local provider; asset/code có version và manifest xác thực; không dùng `localStorage` làm nguồn save gameplay có thẩm quyền.
- [ ] Mạng chỉ được dùng bởi luồng tải/cập nhật có chủ đích. Trong offline, request không được hỗ trợ phải báo tính năng cần mạng; tuyệt đối không chuyển request gameplay sang production.
- [ ] Tài khoản online, thanh toán, PvP, guild/chat và cloud sync không chặn chế độ chơi cục bộ; online-only được ẩn hoặc đánh dấu cần mạng; không xóa/ghi đè save offline khi các tính năng này tắt.
- [ ] Bổ sung coverage cho các luồng single-player thuộc phạm vi đã công bố, state transition, chiến đấu, reward, lỗi/mất dung lượng và resource update; xác minh network log offline không có request production.

## D. Phát hành thử trên thiết bị — chưa bắt đầu

- [ ] Build/rebuild sạch và kiểm thử trên thiết bị Android thật với resource đầy đủ, tải dở/resume, update, airplane mode, reboot/force-stop, storage thấp và gỡ/cài lại; tách debug keystore khỏi production release.
- [ ] Chỉ tuyên bố “chơi offline đầy đủ” khi các cổng A–D đều đạt trên đúng device build tương ứng.

## Mốc làm ngay

- [~] Thêm luồng **Chơi offline với tư cách Khách** qua local API; guest/session được lưu bền vững, có logout đúng cách, không phụ thuộc tài khoản hoặc server; giữ nguyên luồng local account hiện có. Đã thêm UI guest, route guest/logout và test persistence; cần xác nhận flow WebView trên thiết bị.
- [~] Kiểm thử settlement campaign: chỉ battle runner quyết định win/first-clear/reward, save và battle report còn sau reload; contract test dùng runner giả định và 31/31 unit tests qua. Còn phải thực thi LuaJIT JNI thật trên Android rồi kiểm thử catalog → formation → battle → reward → save trong airplane mode.
