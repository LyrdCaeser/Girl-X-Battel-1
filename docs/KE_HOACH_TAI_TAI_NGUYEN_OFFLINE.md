# Kế hoạch triển khai tải và giữ tài nguyên game offline

**Nhánh:** `feature/offline-mode`


**Trạng thái:** Quyết định sản phẩm đã chốt là Android chơi offline thật sự. Launcher có resource dashboard, signed downloader, background worker và local asset resolver. Builder streaming và workflow GitHub Actions hydrate LFS/build web packs đã được thêm; workflow chưa chạy/publish. Remote branch hiện có LuaJIT JNI bridge cho battle/attrs cùng APK debug, nhưng chưa nối vào local API/frontend và chưa có local profile/state/save hoàn chỉnh.
**Mục tiêu người dùng:** Game Android phải chơi được offline; Internet chỉ tùy chọn để tải/cập nhật resource pack, còn shell, API/engine và save chạy local.

Quyết định kiến trúc và cổng nghiệm thu được ghi tại [`QUYET_DINH_ANDROID_OFFLINE.vi.md`](./QUYET_DINH_ANDROID_OFFLINE.vi.md). Kế hoạch resource bên dưới là tổng quan; trình tự triển khai downloader/kho local cụ thể nằm trong [`KE_HOACH_ASSET_DOWNLOADER_ANDROID.vi.md`](./KE_HOACH_ASSET_DOWNLOADER_ANDROID.vi.md). Riêng việc tải tài nguyên **không** đáp ứng mục tiêu gameplay offline.

## 1. Hiện trạng trong nhánh

Android hiện mở resource dashboard trước và có lựa chọn chơi online tách biệt; Windows/iOS vẫn là launcher online. Android local shell chỉ phục vụ file thuộc manifest đã ký và không fallback CDN. JNI bridge LuaJIT mới cung cấp đường gọi battle/attrs native riêng; API/auth, campaign state, economy/action routing và save chưa chạy local qua frontend.

Web client yêu cầu ảnh, âm thanh, Spine, JSON và dữ liệu theo đường dẫn `/assets/...`; nhiều màn hình chỉ tải tài nguyên khi người chơi mở màn đó. Android có `OfflineResourceManager`, WebView local handler và manifest/pack builder, nhưng chưa có allowlist release review hoặc origin/CDN phát hành.

Kiểm kê pointer-aware trên working copy hiện tại (LFS size lấy từ metadata pointer; payload thật chưa hydrate trong sandbox):

- `web/assets`: **31.506 file**, **5.025.069.633 byte** (khoảng **4,680 GiB**), gồm **29.299 LFS object** với **4.011.852.022 byte** payload khai báo.
- Toàn bộ `web/` (source + vendor + assets): **31.667 file**, **5.028.767.826 byte** (khoảng **4,683 GiB**); đây là root allowlist của pipeline.
- `data`: **1.258 file**, **74.833.722 byte** (khoảng **71,37 MiB**).
- `runtime`: **3.599 file**, **89.040.410 byte** (khoảng **84,91 MiB**).
- Tổng `web` + `data` + `runtime`: **5.192.641.958 byte** (khoảng **4,836 GiB**); con số chưa phản ánh ZIP compression hoặc phần nào thực sự cần cho gameplay Android.

LFS pointer metadata cho biết byte count dự kiến, không chứng minh payload đã được tải đúng; workflow phải checkout `lfs: true`, từ chối pointer còn sót và đo lại byte/hash trên payload thật. Kích thước pack tải được sẽ do CI report sau khi nén. `runtime`/`data` còn có thể cần cho gameplay nhưng không thuộc web asset pack bước đầu.

## 2. Kết quả mong muốn và ranh giới phạm vi

Người dùng có thể chọn **Tải/cập nhật tài nguyên offline**. App cho biết dung lượng tổng, dung lượng còn thiếu, gói còn chờ tải và yêu cầu Wi-Fi/sạc nếu cần. Tải có thể tạm dừng/tiếp tục sau khi thoát app hoặc mất mạng. Sau khi xác minh xong, app giữ phiên bản trong bộ lưu trữ riêng và dùng cùng local shell/API/engine khi mở game; khởi chạy gameplay không được chờ server hoặc tải lại asset từ production.

Bộ tài nguyên được giữ trong thư mục dữ liệu ứng dụng bền vững. Nó phải tồn tại qua khởi động lại thiết bị và cập nhật app tương thích; bị xóa khi người dùng chọn xóa dữ liệu ứng dụng hoặc gỡ game. Không thể cam kết giữ khi người dùng chủ động xóa dữ liệu/gỡ app hoặc hệ điều hành xóa dữ liệu ứng dụng theo chính sách nền tảng.

Việc tải asset chỉ là một lớp của tính năng. Để đáp ứng quyết định sản phẩm, còn phải đưa HTML/JS vào local app/resource store, cung cấp API/engine và save cục bộ, bỏ yêu cầu đăng nhập online cho hồ sơ offline, và chặn/đánh dấu các tính năng online-only. Không quảng bá “chơi offline hoàn toàn” trước khi campaign/save và các luồng single-player đã công bố qua kiểm thử airplane mode trên thiết bị thật.

Asset công khai và save riêng tư cũng là hai loại dữ liệu khác nhau. Nếu dùng AWS, phân phối resource pack qua CDN/bucket asset riêng; không đặt resource pack public trong bucket private chứa save người chơi, và tuyệt đối không để AWS secret trong app.

## 3. Kiến trúc đề xuất

### 3.1 Manifest phát hành

CI tạo một manifest bất biến cho mỗi release tài nguyên, ví dụ `resources-v1.<build-id>.json`. Manifest gồm `manifest_version`, `resource_version`, `build_id`, `minimum_app_version`, `created_at`, tổng byte tải/giải nén và danh sách gói. Mỗi file trong manifest có đường dẫn tương đối chuẩn hóa, byte length, SHA-256, MIME type, pack ID và nhãn `core|full|optional`.

Các nhóm nội dung được lập chỉ mục gồm:

- Shell chạy game: HTML, CSS, JavaScript và vendor runtime cần thiết.
- Game assets: `web/assets` và các file dữ liệu phục vụ client.
- Data/config: những JSON/Lua/data file thật sự cần khi chạy local.
- Runtime theo nền tảng: binary/runtime cần thiết để chạy local engine; không đưa binary Windows vào gói Android/iOS.

Danh sách phải được tạo từ allowlist thư mục/file đã duyệt, không đóng gói `.git`, cache build, file test, tool trích xuất hoặc dữ liệu developer. Không đưa path tuyệt đối, secret, save, log hay thông tin cá nhân vào manifest. Generator phải phát hiện symlink/path traversal và từ chối đường dẫn ngoài root resource.

### 3.2 Gói chia phần, tải tiếp tục được

Không gửi 31 nghìn file thành từng HTTP request riêng lẻ. CI gom file thành các archive theo nhóm tài nguyên và kích thước tối đa đã cấu hình (mốc thử nghiệm: 32–64 MiB/gói), rồi ghi checksum SHA-256 cho archive và từng file. Tổ chức theo nhóm tương đối ổn định (`core`, `ui`, `audio`, `spine`, `characters`, `events`, v.v.) để release mới chỉ cần thay gói có nội dung thay đổi.

Manifest liệt kê URI/version/hash/size của từng gói. Downloader tải gói theo HTTP range/resume nếu origin hỗ trợ; nếu không, retry gói hiện tại từ đầu, không phải tải lại toàn bộ bộ tài nguyên. Tải song song có giới hạn (mốc ban đầu 2–4 gói) để không làm quá tải thiết bị/mạng. Tên gói chứa content hash để cache/update không ghi đè nhầm phiên bản.

Tạo hai profile phát hành nhưng chỉ coi profile **full** là “đã tải trọn bộ”:

- `core`: shell và resource tối thiểu để mở, đăng nhập/hiển thị màn đầu.
- `full`: toàn bộ resource được tham chiếu trong manifest và các runtime/data được xác định là cần thiết cho chức năng offline.

Nếu người dùng chọn tải full, app phải báo rõ tổng dung lượng và không đánh dấu full hoàn thành cho tới khi tất cả gói bắt buộc đã xác minh.

### 3.3 Nguồn tải và phát hành

Bản đầu có thể phục vụ gói từ HTTPS server phát hành hiện tại. Khi chuyển sang AWS, dùng bucket/prefix asset riêng cùng CloudFront hoặc CDN tương đương: bucket không public trực tiếp, CDN đọc qua quyền origin, gói và manifest theo URL version bất biến. Resource pack là nội dung phát hành, không phải dữ liệu người dùng; không cần presigned URL theo từng người dùng nếu mô hình cấp phép không yêu cầu.

Phiên bản trong URL không ghi đè, ví dụ `/offline-resources/<resource-version>/<pack-sha256>.zip`. Builder hiện hỗ trợ deterministic pack, SHA-256 và Ed25519-signed envelope; Android pin public key và từ chối manifest unsigned. HTTPS và hash bảo vệ đường truyền/toàn vẹn file; chữ ký manifest bảo vệ tính xác thực nguồn phát hành. Chưa có release publisher hoặc URL manifest dùng thật.

## 4. Lưu trữ bền vững trên thiết bị

### Android

- Dùng `context.getExternalFilesDir(null)` làm thư mục mẹ app-specific; đường dẫn thường có dạng `Android/data/<applicationId>/files/`. Tạo hai thư mục con `data/` và `obb/` ngay bên dưới. Với project hiện tại `applicationId` là `com.quangho.goddess.battle`, không phải `com.garena.kgvn`; Android không cho app này ghi vào thư mục package của Liên Quân.
- Lưu manifest, metadata, shell/code và resource nhỏ trong `data/`; lưu asset nhị phân/media lớn và pack đang tải trong `obb/`. `obb/` ở đây là thư mục app-specific do game quản lý, không phải định dạng Google Play Expansion OBB; thư mục Expansion OBB chính thức nằm ở vị trí khác.
- Không dùng `cacheDir`, Downloads công khai hoặc WebView HTTP cache làm kho chính; app-specific external files không cần quyền đọc/ghi bộ nhớ dùng chung. Nếu `getExternalFilesDir(null)` trả `null`, caller có thể fallback sang `context.getFilesDir()` nhưng vẫn giữ layout con `data/` và `obb/`.
- Lưu phiên bản đã xác minh theo content hash. Lưu manifest hiện hành riêng trong `data/`, đổi con trỏ active atomic sau khi toàn bộ gói bắt buộc đạt kiểm tra.
- Tải nền có thông báo tiến độ và trạng thái tiếp tục/tạm dừng; giới hạn mạng di động theo lựa chọn người dùng. Sau khi app bị kill, khôi phục danh sách gói từ state bền vững và tiếp tục từ byte/chunk đã có sau khi xác minh lại.
- Dùng WebView local asset mapping an toàn (ví dụ HTTPS-like app-assets origin) thay vì mở tùy tiện `file://`. Chặn đường dẫn traversal, chỉ phục vụ file trong root release đã xác minh.

### iOS

- Lưu gói đã cài vào `Application Support/OfflineResources/<resource-version>/`; không dùng `Caches` làm kho duy nhất vì cache có thể bị hệ điều hành dọn.
- Dùng background `URLSession` cho tác vụ tải dài; khi hoàn tất, chuyển file tạm vào thư mục phiên bản sau khi kiểm hash. Lưu state đủ để khôi phục khi app được hệ thống đánh thức lại.
- Phục vụ web resource từ local origin/handler an toàn do app kiểm soát. Không dựa vào `WKWebView` cache hiện tại; xử lý rõ CORS/origin và đường dẫn API local ở chế độ offline.
- Kiểm tra thực tế hạn mức dung lượng, background download và khởi động offline trên thiết bị iOS được hỗ trợ; không coi simulator là nghiệm thu thay cho thiết bị thật.

### Bản desktop

Các script khởi động trong repo hiện chạy `server.py` từ thư mục source, nên bản clone đầy đủ đã có asset tại chỗ. Release desktop cần đóng gói đúng allowlist resource, kiểm tra đủ file ở cài đặt đầu tiên và không gọi pip/install/network để có thể chạy thực sự offline sau khi đã cài. Bản desktop không nên buộc tải lại asset đã nằm sẵn trong package.

## 5. Luồng trải nghiệm và cập nhật

1. Khi mở mục **Tài nguyên offline**, client lấy manifest mới nhất qua HTTPS và kiểm tra chữ ký (nếu bật).
2. Client so manifest với version cục bộ, tính tổng byte còn thiếu và dung lượng trống cần thiết. Với lần tải web asset đầu, thông báo khoảng 4,68 GiB uncompressed hoặc số đo pack thực tế trong manifest; yêu cầu người dùng xác nhận.
3. Tải từng pack vào staging; lưu tiến độ và retry với backoff. Cho phép dừng/resume. Không thay thư mục `current` trong lúc đang tải.
4. Kiểm tra checksum của từng pack, giải nén an toàn, kiểm tra kích thước/file count/path, sau đó kiểm SHA-256 của từng file theo manifest.
5. Chạy self-test tài nguyên tối thiểu (HTML entry point, bảng catalog, một ảnh, một file Spine/audio đại diện). Nếu lỗi, đánh dấu pack lỗi và giữ phiên bản hiện tại.
6. Khi mọi pack bắt buộc đã hợp lệ, cập nhật manifest/con trỏ hiện hành atomic. Hiển thị “Đã tải đủ — có thể mở tài nguyên offline”.
7. Khi có release mới, chỉ tải pack hash mới. Giữ bản hiện hành cho tới khi bản mới hoàn toàn hợp lệ; sau khi đổi thành công và app không còn dùng bản cũ, xóa file hash không còn tham chiếu để thu hồi dung lượng.
8. Xóa tài nguyên chủ động phải là thao tác riêng trong Settings, hiển thị dung lượng sẽ giải phóng và xác nhận. Xóa cache tạm/log không được xóa resource pack hiện hành.

### Cập nhật và dung lượng

Do web assets hiện khoảng 4,68 GiB raw, cập nhật staging kiểu “giữ hai bản đầy đủ” có thể cần thêm nhiều GiB trống nếu asset thay đổi diện rộng. Không yêu cầu tải lại object có cùng hash. Kiểm tra dung lượng trước khi tải; khi thiếu, dừng an toàn và nêu dung lượng cần giải phóng. Ưu tiên lưu object theo content hash để các release chia sẻ dữ liệu không trùng.

Manifest phải chứa `minimum_app_version` và version schema. Nếu bản app không hiểu định dạng mới, giữ resource version đang hoạt động và yêu cầu cập nhật app. Không tự xóa resource đã cài chỉ vì server tạm thời không truy cập được.

## 6. Những phần cần làm trong codebase

1. `tools/build_offline_resource_manifest.py`: đã hỗ trợ streaming files, ZIP bounded deterministic, SHA-256, signed envelope, tracked-root allowlist và phát hiện pointer chưa hydrate. `tools/offline_resources_allowlist.json` chọn toàn bộ file Git-tracked dưới `web/`.
2. `.github/workflows/offline-resource-pack.yml`: checkout bật Git LFS, verify hydration, build đủ web tree khi `web/**`/`.gitattributes` đổi; chạy thủ công sau khi sửa builder/allowlist. Artifact nhiều GiB chỉ upload theo lựa chọn manual 1 ngày. Nếu chưa cấu hình `OFFLINE_RESOURCE_BASE_URL`/`OFFLINE_MANIFEST_SIGNING_KEY_PEM`, build dùng URL placeholder/unsigned development-only; workflow không tự publish lên CDN.
3. `server.py` hoặc service phân phối: endpoint manifest/version và tải pack có Range/ETag nếu chưa dùng CDN. Đặt cache policy riêng cho URL bất biến; không để `Cache-Control: no-store` ngăn CDN giữ immutable pack.
4. Android: manager/Worker/resume/progress/verify/extract/local WebView mapping, origin-restricted WebMessageListener và fail-closed local API router (`GET /api/offline/health`; gameplay routes 501), cùng JNI LuaJIT battle/attrs bridge đã có trong nhánh; còn cần device test, state/action/save provider, frontend adapter và hardening.
5. iOS: resource manager native, background URLSession, verify/extract an toàn và local WebView resource handler.
6. Web client: config `online|offline`, asset base URL, không hard-code remote origin trong offline mode; các endpoint dữ liệu phải được xử lý bởi local API hoặc được nêu rõ là tính năng cần mạng.
7. Desktop packaging: tạo bản phát hành có đủ resource/runtime; tách dependency cài đặt khỏi khởi động để không cần mạng khi chạy offline.
8. Settings UI: dung lượng tổng/còn thiếu, version hiện cài, nút tải/tạm dừng/tiếp tục/xóa, lỗi và thời điểm cập nhật.

## 7. Lộ trình theo giai đoạn

### Giai đoạn 0 — Chốt kiến trúc và ngân sách

- Chốt nền tảng ưu tiên, định nghĩa “trọn bộ” chính xác, danh sách file offline cần thiết và giới hạn dung lượng tối đa.
- Chốt việc mobile có thực sự chạy local game engine hay chỉ cung cấp resource offline. Tách quyết định này khỏi việc tải asset.
- Phân tích các route `/assets/...` theo repo để tìm file tham chiếu động, file Spine phụ thuộc atlas/texture, âm thanh và fallback assets.
- Tạo báo cáo license/provenance cho nội dung sẽ phát hành lại; loại file không được phép phân phối.

**Đầu ra:** allowlist resource, phân loại core/full, budget kích thước, tiêu chí nghiệm thu và quyết định local serving cho Android/iOS.

### Giai đoạn 1 — Manifest và pack build

- Viết generator xác định, có thể chạy lại cho ra cùng manifest/hash với cùng source.
- Sinh pack chia phần, manifest, hash, optional chữ ký và báo cáo dung lượng/compression.
- Thêm CI test kiểm tra link asset, file tham chiếu không tồn tại, giới hạn pack, archive path traversal và sự nhất quán giữa manifest với artifact.

**Hoàn tất khi:** artifact build tái lập được; manifest bao phủ 100% file thuộc scope full; CI báo thiếu file hoặc sai hash là fail.

### Giai đoạn 2 — Downloader và kho bền vững

- Triển khai downloader Android/iOS: tải nền, pause/resume, retry, giới hạn concurrency, kiểm dung lượng trống, hash validation và cài đặt atomic.
- Lưu resource trong thư mục bền vững app-private; phân biệt staging/current/old version; thực hiện cleanup an toàn.
- Làm Settings UI và telemetry không chứa dữ liệu người dùng/URL nhạy cảm.

**Hoàn tất khi:** tải bị ngắt rồi tiếp tục được; app kill/reboot vẫn tiếp tục; file hash sai bị từ chối; phiên bản đang dùng không bị thay thế bởi download lỗi.

### Giai đoạn 3 — Local asset serving và offline entry

- Dẫn URL tài nguyên web sang thư mục resource đã cài; tắt tải mạng cho asset khi `offline mode` đang bật.
- Tạo trang chẩn đoán cho file thiếu/version sai; không âm thầm fallback sang server khi người dùng đang kiểm thử offline.
- Tích hợp local HTML/JS cùng cách phục vụ API local. Nếu local API/gameplay chưa sẵn sàng, thông báo chính xác phần UI/resource có thể xem offline và phần nào cần mạng.

**Hoàn tất khi:** bật airplane mode sau khi cài full resources vẫn khởi chạy được local shell và truy cập được mọi asset đã khai báo; network log không cho thấy request tải asset từ production.

### Giai đoạn 4 — Cập nhật, rollback và phát hành

- Bổ sung phát hiện manifest mới, tải delta theo content hash, giữ phiên bản cũ khi update lỗi và rollback khi self-test fail.
- Thử trên thiết bị dung lượng thấp, mạng yếu, Wi-Fi chuyển sang mobile, app bị kill, hết pin, thiết bị reboot, cập nhật app và gỡ/cài lại.
- Kiểm tra behavior xóa dữ liệu/gỡ app đúng kỳ vọng của Android/iOS; tài liệu người dùng nói rõ gỡ app sẽ xóa bản resource cục bộ.
- Phát hành beta có feature flag, theo dõi tỷ lệ tải thành công, thời gian tải, dung lượng trung vị, checksum failure, resume failure và lỗi khởi chạy offline.

## 8. Kiểm thử và tiêu chí nghiệm thu chung

- **Manifest:** hash khớp cho tất cả file; phát hiện resource thiếu, đường dẫn sai, case-sensitive mismatch, symlink và file ngoài allowlist.
- **Tải:** retry sau timeout, mất mạng, app kill và reboot; không tải lại pack hash đã có; tiến độ không bị báo 100% trước khi xác minh/cài đặt.
- **Toàn vẹn:** sửa một byte trong pack/file khiến install fail; archive có `../` hoặc file vượt giới hạn bị chặn; chữ ký sai bị từ chối.
- **Dung lượng:** thiếu dung lượng trước tải hoặc lúc giải nén không làm mất bản đang dùng; cleanup chỉ xóa hash không còn được version nào tham chiếu.
- **Offline:** xóa cache WebView/HTTP cache và bật airplane mode vẫn đọc resource từ Application Support/filesDir; kiểm tra khởi động sau force-stop.
- **Vòng đời:** cập nhật app giữ resource tương thích; nâng resource đổi version atomic; chọn xóa dữ liệu/gỡ app xóa resource theo hành vi hệ điều hành; tải lại sau cài mới.
- **Hiệu năng:** đo lần tải đầu trên mạng thực, CPU/bộ nhớ khi giải nén, tiêu thụ pin, số file và thời gian lookup; hiện có 31.506 asset, gần 4,68 GiB raw, nên cần kiểm thử batch/background trên thiết bị.
- **Gameplay:** kiểm thử riêng đăng nhập, API, state/save, thời gian, battle/runtime và các thao tác game trong airplane mode. Asset được cache thành công không được dùng làm bằng chứng rằng gameplay offline đã hoàn tất.

### Điều kiện bật nhãn “Đã tải trọn bộ”

Chỉ hiển thị trạng thái này khi manifest release hợp lệ, tất cả pack bắt buộc đã tải và xác minh, mọi file đã được cài trong kho bền vững, self-test đạt, và app có thể đọc chúng sau khi tắt mạng/force-stop. Không dùng WebView cache hoặc “đã từng mở màn đó” làm điều kiện.

## 9. Rủi ro và quyết định cần chốt

- **Dung lượng cao:** full web asset hiện khoảng 4,68 GiB raw. Cần xác nhận thiết bị mục tiêu có đủ dung lượng và quyền phân phối; tối ưu có chủ đích trước khi bỏ asset hoặc giảm chất lượng.
- **Tải full không bằng gameplay offline:** phụ thuộc API/gameplay/server state. Đây là blocker sản phẩm riêng, cần đồng bộ với thiết kế save offline trong [`offline-s3-sync-workflow.vi.md`](./offline-s3-sync-workflow.vi.md).
- **Tài nguyên động/lazy-loaded:** đường dẫn tạo trong JS hoặc file Spine có thể thiếu khỏi manifest tĩnh. Cần scan code + runtime crawl/test UI để kiểm tra coverage.
- **Gói update quá lớn:** chọn shard theo category/hash và đo tỷ lệ thay đổi giữa hai release; điều chỉnh kích thước pack từ số liệu CI.
- **Phân phối nội dung:** xác minh quyền phân phối asset trong APK/resource pack/CDN trước khi public; bucket/CDN configuration không thay thế quyền tác giả.
- **Xóa app/data:** “vĩnh viễn” có nghĩa là giữ cho tới khi hệ điều hành xóa vùng dữ liệu ứng dụng hoặc người dùng gỡ app; không phải giữ xuyên qua uninstall.

## 10. Thứ tự việc nên làm tiếp theo

1. Chạy `.github/workflows/offline-resource-pack.yml` để hydrate/paket web assets thật; cấu hình signing key/CDN origin trước khi xem manifest là release dùng được.
2. Build sạch APK và kiểm thử trên Android thật: download/resume/integrity/storage, local WebView và airplane mode.
3. Bổ sung local API + persistent save/profile, rồi nối JNI battle bridge với state/action contracts.
4. Chuyển frontend sang local provider, khóa network fallback và kiểm campaign/summon/inventory/formation/reward.
5. Hoàn tất debug/release reproducibility, smoke tests và nghiệm thu offline end-to-end.

**Chưa được workflow này làm:** publish pack ra CDN/bucket, ký production manifest nếu secret chưa được cấu hình, hoặc đóng gói runtime/API/save Android. Artifact upload lớn cần bật thủ công và có thể bị giới hạn quota Actions.
