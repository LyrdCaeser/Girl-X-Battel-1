# Quyết định kiến trúc: Android chơi offline

**Dự án:** Girl-X-Battel-1
**Nhánh:** `feature/offline-mode`
**Trạng thái:** Đã chốt phạm vi; triển khai theo từng giai đoạn
**Ngày:** 2026-11-05

## Quyết định sản phẩm

Bản Android offline phải mở và chơi được mà không cần kết nối máy chủ game. Internet chỉ là tùy chọn để tải/cập nhật resource pack; sau khi gói đã tải và xác minh, game phải dùng mã giao diện, engine/API và save cục bộ. Không hiển thị hoặc chờ thông báo “đang khởi động máy chủ”. Không âm thầm fallback sang production khi chạy offline.

Đây là mục tiêu gameplay offline thực sự, không phải chỉ tải ảnh/âm thanh hoặc dùng cache WebView. Tài khoản online, thanh toán, PvP, guild/chat và đồng bộ cloud là tính năng online riêng; chúng không được chặn chế độ chơi cục bộ. Save cục bộ là nguồn có thẩm quyền khi offline. Đồng bộ cloud, nếu triển khai sau này, là tùy chọn và không thay thế save local.

## Hiện trạng đã kiểm tra

- `clients/android/.../MainActivity.java` chờ `https://180-93-111-99.sslip.io/readyz`, rồi tải game từ origin đó. Đây là nguyên nhân splash trong ảnh vẫn nói đang khởi động server.
- Android hiện có dashboard resource, signed Ed25519 manifest với public key pin, content-addressed store, unique WorkManager foreground download, và `WebViewAssetLoader` strict local resolver trên `https://gxb3.local/`. URL/allowlist/key cấu hình qua Gradle properties; mặc định nút tải vẫn tắt. Preview local chỉ là shell/assets, chưa có API/game engine/save.
- Web client hiện đăng nhập trước khi vào game; API helper gửi yêu cầu về server. Có 111 chuỗi đường dẫn `/api/...` trong JS (bao gồm prefix động); server có khoảng 164 nhánh API so sánh chính xác và 9 nhánh `startswith`.
- Chiến đấu và thay đổi trạng thái gameplay được xử lý bởi server engine. Chỉ bỏ bước đăng nhập hoặc cache asset không làm cho campaign/save hoạt động offline.
- APK debug đang có chỉ khoảng 310 KiB và không chứa game web/backend. Web assets đã từng được kiểm kê khoảng 970 MiB, nhưng cần hydrate/kiểm tra Git LFS trước khi tin số liệu hoặc đóng gói; checkout có thể chứa file LFS pointer.
- Engine hiện tại nằm trong Python server và gọi LuaJIT/native runtime để giữ đúng logic chiến đấu; không có Android local runtime/provider tương ứng trong dự án. Port/đóng gói engine sang Android là phần cốt lõi còn lại, không thể thay bằng cách bỏ auth hoặc trả kết quả chiến thắng giả.
- Môi trường kiểm tra chưa có Android SDK/Gradle/adb nên không thể xác nhận build APK tại sandbox. Hàng chục nghìn asset trong checkout vẫn là Git LFS pointers và không có LFS object cache, vì vậy chưa thể tạo pack thật hoặc nghiệm thu airplane mode.

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

Đã tích hợp khung dashboard, signed downloader Worker, pack builder và resolver local; vẫn chưa có release tài nguyên thật, build/device verification hoặc local API/gameplay/save. Không được quảng bá APK hiện tại là game offline. Trước tiên cần hydrate Git LFS, cấu hình HTTPS publisher + public-key pin, build/kiểm thử Android; song song làm proof-of-concept port engine chiến đấu sang Android. Kế hoạch chi tiết nằm ở [`KE_HOACH_ASSET_DOWNLOADER_ANDROID.vi.md`](./KE_HOACH_ASSET_DOWNLOADER_ANDROID.vi.md), kế hoạch tổng thể tài nguyên ở [`KE_HOACH_TAI_TAI_NGUYEN_OFFLINE.md`](./KE_HOACH_TAI_TAI_NGUYEN_OFFLINE.md), và thiết kế save/sync cloud riêng ở [`offline-s3-sync-workflow.vi.md`](./offline-s3-sync-workflow.vi.md).
