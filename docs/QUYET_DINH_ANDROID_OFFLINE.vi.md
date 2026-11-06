# Quyết định kiến trúc: Android chơi offline

**Dự án:** Girl-X-Battel-1
**Nhánh:** `feature/offline-mode`
**Trạng thái:** Đã chốt phạm vi; triển khai theo từng giai đoạn
**Ngày:** 2026-11-05

## Quyết định sản phẩm

Bản Android offline phải mở và chơi được mà không cần kết nối máy chủ game. Internet chỉ là tùy chọn để tải/cập nhật resource pack; sau khi gói đã tải và xác minh, game phải dùng mã giao diện, engine/API và save cục bộ. Không hiển thị hoặc chờ thông báo “đang khởi động máy chủ”. Không âm thầm fallback sang production khi chạy offline.

Đây là mục tiêu gameplay offline thực sự, không phải chỉ tải ảnh/âm thanh hoặc dùng cache WebView. Tài khoản online, thanh toán, PvP, guild/chat và đồng bộ cloud là tính năng online riêng; chúng không được chặn chế độ chơi cục bộ. Save cục bộ là nguồn có thẩm quyền khi offline. Đồng bộ cloud, nếu triển khai sau này, là tùy chọn và không thay thế save local.

## Hiện trạng đã kiểm tra

- Splash tự chờ `readyz` đã được thay bằng resource dashboard; nút vào bản online là lựa chọn riêng, không còn tự chờ server khi mở app.
- Android hiện có dashboard resource, signed Ed25519 manifest với public key pin, content-addressed store, unique WorkManager foreground download, strict `WebViewAssetLoader`, và origin-restricted `WebMessageListener` trên `https://gxb3.local/`. Local JSON router có health/readiness; gameplay routes chủ động trả 501, chưa giả lập kết quả. URL/allowlist/key cấu hình qua Gradle properties; mặc định nút tải vẫn tắt.
- Web client hiện đăng nhập trước khi vào game; API helper gửi yêu cầu về server và chưa được nối sang WebMessage RPC. Có 111 chuỗi đường dẫn `/api/...` trong JS (bao gồm prefix động); server có khoảng 164 nhánh API chính xác và 9 nhánh `startswith`. Campaign/summon/inventory/formation chưa chạy qua local provider.
- Engine baseline vẫn là Python server; Android đã có LuaJIT JNI bridge thực thi `battle_host.lua` ở mode battle/attrs, nhưng bridge chưa được nối vào state/action của web client và không cung cấp save/game economy.
- APK debug mới đã được commit trên remote (`artifacts/android/Girl-X-Battel-1-debug.apk`, khoảng 33,8 MiB); native runtime link cho `arm64-v8a` và `armeabi-v7a` đã được ghi nhận trong README native. Cần clean rebuild lặp lại và smoke test trên thiết bị trước khi gọi là reproducible/đạt offline.
- Checkout sandbox chưa có LFS object cache, nên builder cục bộ từ chối build từ pointer; workflow CI mới chưa chạy và chưa publish resource pack/CDN. Inventory pointer-aware ghi nhận `web/assets` 31.506 file, 5.025.069.633 byte (~4,680 GiB), trong đó 29.299 LFS pointer khai báo 4.011.852.022 byte; workflow sẽ xác minh payload thật khi chạy.

## Phạm vi đầu tiên: local single-player

1. Chế độ **Chơi offline** dùng hồ sơ khách cục bộ riêng, khởi tạo save bền vững và không yêu cầu tài khoản/server.
2. Boot, catalog thiết yếu, campaign, chọn đội hình, chiến đấu, nhận thưởng và lưu/đọc tiến trình chạy local. Bắt đầu bằng một lát dọc campaign có thể kiểm thử đầu-cuối; mở rộng các hệ thống single-player theo danh sách endpoint/dependency đã kiểm kê.
3. Asset/code có phiên bản, manifest được xác thực, pack tải lại được sau khi gián đoạn và được lưu trong app-private storage. Cho phép vào game khi không có mạng nếu resource cục bộ tương thích và hợp lệ.
4. Mạng chỉ được dùng bởi luồng tải/cập nhật có chủ đích. Trong chế độ offline, request không được hỗ trợ phải báo tính năng cần mạng; không chuyển request gameplay sang server production.
5. Online-only (đăng nhập tài khoản, thanh toán, PvP, guild/chat, leaderboard và cloud sync) được ẩn hoặc đánh dấu rõ cần mạng. Không được xóa hay ghi đè save offline khi các tính năng này tắt.

## Ranh giới kiến trúc bắt buộc

- Tách API client thành provider có chế độ rõ ràng: `online` và `offline-local`; lựa chọn offline không dựa vào lỗi mạng tự động.
- Local state/save dùng schema/version riêng có migration, ghi nguyên tử và khôi phục an toàn. Không dùng `localStorage` làm nguồn save gameplay có thẩm quyền.
- Chọn local engine/API sau một proof-of-concept trên Android: so sánh adapter native cho endpoint cốt lõi với nhúng CPython. Không port toàn bộ backend hoặc đưa PostgreSQL/credential production vào APK một cách mặc định. Engine chiến đấu phải giữ logic xác thực gameplay hiện hành hoặc được kiểm chứng tương đương; không tạo chiến thắng/phần thưởng chỉ từ giao diện.
- Game UI và resource phải đọc từ origin/file root do app kiểm soát, với đường dẫn allowlist. Lỗi thiếu asset/offline không được fallback ngầm sang CDN/production.
- Tách nội dung tài nguyên công khai khỏi save người chơi; không nhúng secret AWS hoặc token phát hành trong APK.

## Các giai đoạn và cổng nghiệm thu

### A. Resource release và local shell

Hydrate/kiểm tra LFS; định nghĩa allowlist và kích thước thực; sinh manifest bất biến, checksum và các pack; xuất bản URL HTTPS versioned; tích hợp downloader Android, tiến độ/resume/cancel, xác minh và cài đặt atomic. Phục vụ web shell từ local origin an toàn.

**Cổng:** cài gói, force-stop, bật airplane mode, mở lại app và tải được màn shell cùng toàn bộ resource core đã khai báo; log không có request đến game server/production.

### B. Local profile/save và API proof-of-concept

Chọn, triển khai và benchmark phương án engine local trên thiết bị Android thật. Đưa một lát dọc campaign vào API local và save bền vững. Xác định phần nào của engine hiện dùng SQLite, LuaJIT/native runtime, thư mục `HOME` hoặc dịch vụ production; không coi chạy `server.py` trên desktop là bằng chứng chạy được trên Android.

**Cổng:** khởi tạo guest profile, chơi một stage, nhận reward, force-stop/reopen và giữ đúng tiến trình trong airplane mode; save migration/backup không làm hỏng dữ liệu.

### C. Mở rộng single-player và loại trừ online-only

Lập ma trận endpoint theo màn hình; chuyển các hệ thống single-player đã cam kết sang local provider; vô hiệu hóa có chủ đích các tính năng online-only. Thêm tests cho state transition, chiến đấu, reward, lỗi/mất dung lượng và update resource.

**Cổng:** coverage của các luồng single-player thuộc phạm vi đã công bố; request production không xuất hiện trong network log khi offline; online-only được thông báo chính xác.

### D. Phát hành thử

Build và kiểm thử trên thiết bị Android thật với tài nguyên đầy đủ, tải dở/resume, update, airplane mode, reboot/force-stop, storage thấp và gỡ/cài lại. Tách debug keystore khỏi phát hành chính thức.

**Cổng phát hành:** không tuyên bố “chơi offline đầy đủ” trước khi các cổng A–D đạt trên device build tương ứng.

## Việc chưa được coi là hoàn thành

Đã tích hợp dashboard, signed downloader Worker, streaming pack builder, full-web tracked-root allowlist, workflow CI bật Git LFS, LuaJIT JNI battle/attrs bridge và APK debug trên remote. Vẫn chưa chạy CI hydrate/build hoặc publish resource release/CDN; local API/state/action/save chưa hoàn chỉnh và chưa có smoke test offline trên thiết bị hay clean reproducibility verification. Không được quảng bá APK hiện tại là game offline. Tiếp theo chạy workflow sau khi cấu hình signing/CDN, kiểm tra build trên thiết bị, rồi nối JNI bridge vào local API/save/frontend. Kế hoạch chi tiết nằm ở [`KE_HOACH_ASSET_DOWNLOADER_ANDROID.vi.md`](./KE_HOACH_ASSET_DOWNLOADER_ANDROID.vi.md), kế hoạch tổng thể tài nguyên ở [`KE_HOACH_TAI_TAI_NGUYEN_OFFLINE.md`](./KE_HOACH_TAI_TAI_NGUYEN_OFFLINE.md), và thiết kế save/sync cloud riêng ở [`offline-s3-sync-workflow.vi.md`](./offline-s3-sync-workflow.vi.md).
