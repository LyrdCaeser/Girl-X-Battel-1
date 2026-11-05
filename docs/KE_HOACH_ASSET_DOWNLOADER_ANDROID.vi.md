# Kế hoạch triển khai Android Asset Downloader và kho tài nguyên local

**Dự án:** Girl-X-Battel-1
**Nhánh:** `feature/offline-mode`
**Trạng thái:** Nền downloader đã có signed-manifest verifier, deterministic pack builder, WorkManager worker và strict local asset resolver; chưa có resource release thật hoặc local game API/engine/save
**Phạm vi tài liệu:** tải, xác minh, cài đặt, lưu giữ, cập nhật và phục vụ game assets/code tĩnh trên Android.

> Downloader và kho asset là nền tảng bắt buộc, nhưng tự chúng không cung cấp API/game engine/save. Muốn chơi offline đầy đủ, phần local gameplay phải được lập trình và nghiệm thu riêng theo [`QUYET_DINH_ANDROID_OFFLINE.vi.md`](./QUYET_DINH_ANDROID_OFFLINE.vi.md).

## 1. Mục tiêu và nguyên tắc

Sau khi người chơi chủ động tải xong một resource release hợp lệ, ứng dụng có thể đọc toàn bộ tài nguyên đã công bố từ bộ nhớ app-private khi không có mạng. Tải lại cùng release không tải lại các object đã có hash hợp lệ. Mất mạng, Android dừng process, app bị force-stop hoặc hết dung lượng không được làm mất resource release đang hoạt động.

Các nguyên tắc bắt buộc:

- Không yêu cầu Internet để mở lại tài nguyên đã cài hợp lệ; không tải asset ngầm từ production khi chế độ offline đang chạy.
- Chỉ manifest đã xác thực, URL HTTPS trong allowlist và đường dẫn nằm trong manifest mới được cài/đọc.
- Chỉ chuyển release sang `active` sau khi tất cả gói bắt buộc, file, self-test và metadata đã được xác minh.
- Không xóa release active trong thao tác cập nhật hoặc dọn rác. Dọn theo hash/refcount, không dựa riêng vào tên file hoặc version string.
- Chỉ hiện trạng thái **Đã sẵn sàng offline** sau khi kiểm tra lại release trên đĩa; không dựa vào việc từng tải xong hoặc WebView cache.
- Tải resource không được đưa cloud save, tài khoản, token cá nhân hay AWS secret vào manifest/pack.

## 2. Hiện trạng đã biết và blocker đầu vào

- Android đã có [`OfflineResourceManager.java`](../clients/android/app/src/main/java/com/quangho/goddess/battle/offline/OfflineResourceManager.java): chỉ nhận signed manifest Ed25519 với public key pin trong APK, URL HTTPS host allowlist, resume byte-range, SHA-256 pack/file, kiểm ZIP path, content-addressed store và activation nguyên tử. Unit tests bao gồm signature hợp lệ/sai/tampered.
- `MainActivity` khởi chạy unique foreground [`OfflineResourceDownloadWorker.java`](../clients/android/app/src/main/java/com/quangho/goddess/battle/offline/OfflineResourceDownloadWorker.java), quan sát tiến độ/result qua WorkManager, và tách nút chơi online. [`OfflineWebViewPathHandler.java`](../clients/android/app/src/main/java/com/quangho/goddess/battle/offline/OfflineWebViewPathHandler.java) chỉ phục vụ file thuộc manifest active; local shell không fallback mạng.
- [`tools/build_offline_resource_manifest.py`](../tools/build_offline_resource_manifest.py) tạo deterministic ZIP/hash và signed envelope khi có private Ed25519 PEM. Gradle properties cấu hình URL, allowlist và public key; mặc định nút tải vẫn tắt. Chưa có manifest/pack phát hành, CI publisher hoặc game API local.
- Checkout hiện có hàng chục nghìn file LFS pointer và không có LFS object cache; builder sẽ từ chối pointer. Không thể tạo resource release đầy đủ trong checkout này cho tới khi hydrate LFS.
- `web/assets` chứa khoảng hàng chục nghìn file; tải/xác minh mỗi file và scan đồng bộ trên UI thread là không phù hợp. Phải đo CPU, bộ nhớ, số inode/file và thời gian trên thiết bị tầm thấp.

## 3. Kiến trúc đích

### 3.1 Luồng phát hành

`Source đã hydrate LFS → allowlist → inventory/manifest → chia pack bất biến → hash/sign manifest → CI kiểm tra → artifact versioned → HTTPS/CDN`

### 3.2 Luồng cài đặt trên thiết bị

`Người chơi chọn Tải/Cập nhật → kiểm tra mạng/dung lượng → tải manifest và xác thực chữ ký → tính object còn thiếu → tải pack vào staging có thể resume → kiểm SHA-256 pack → giải nén an toàn → kiểm SHA-256 từng file → self-test → ghi metadata atomically → chuyển active release → khởi động local resource origin`

Mỗi giai đoạn có trạng thái bền vững để process có thể chết bất kỳ lúc nào mà không làm đổi release đang chạy. Lỗi manifest/signature/hash/path/dung lượng phải giữ nguyên release active, dừng cài và cung cấp thông báo có thể xử lý.

### 3.3 Manifest phát hành

Tiến hóa manifest v1 hiện tại thành schema versioned có tối thiểu:

- `manifest_version`, `resource_version`, `build_id`, `created_at`, `minimum_app_version`, `total_download_bytes`, `total_installed_bytes`.
- Danh sách `packs`: `id`, URL HTTPS bất biến chứa version + hash, `size_bytes`, `sha256`, thứ tự/nhãn `core|full|optional`, danh sách file thuộc pack.
- Metadata file: `path` tương đối chuẩn hóa, `size_bytes`, `sha256`, MIME type, loại storage và flags nếu cần.
- Danh sách entrypoint/self-test và metadata tương thích schema.
- Chữ ký Ed25519 tách khỏi payload ký hoặc theo định dạng canonical rõ ràng; app pin public key. Private key chỉ nằm trong CI secret/HSM được giới hạn; không đóng gói private key/token trong APK.

URL, host và redirect cuối cùng phải kiểm qua allowlist. Release đã phát hành không được ghi đè cùng version/hash; bản mới dùng version/URL mới. Chỉ HTTPS + SHA-256 không thay thế chữ ký manifest.

### 3.4 Phân gói

Chia resource thành:

- **Core:** HTML/CSS/JS shell, thư viện runtime tĩnh, catalog/bootstrap bắt buộc để khởi chạy local shell.
- **Full:** asset được khai báo dùng bởi các màn chơi offline thuộc phạm vi; mọi file bắt buộc phải có trong manifest.
- **Optional:** gói dung lượng lớn/voice/skin/event media chỉ khi gameplay đã hỗ trợ thiếu gói và UI báo rõ.

Giới hạn pack không vượt giới hạn hiện có của downloader (256 MiB mỗi pack); target mềm 100–200 MiB để retry không quá tốn và không giữ file tải dở quá lớn. Điều chỉnh sau khi đo mạng/thiết bị. Tránh tạo một ZIP khổng lồ khoảng 1 GiB. Dùng hash để chia sẻ object chung giữa các release.

### 3.5 Bộ nhớ local và trạng thái

Root ưu tiên `getExternalFilesDir(null)`; nếu null thì dùng `getFilesDir()`. Không xin quyền storage dùng chung. Không dùng `cacheDir`, Downloads công khai hoặc cache HTTP của WebView làm nơi lưu duy nhất.

Cấu trúc dự kiến (cần đối chiếu implementation hiện có trước khi khóa tên chính thức):

```text
<app-private-root>/
  data/
    manifests/<resource-version>.json
    versions/<resource-version>.json
    active-version
    download-state.json
    install.lock
    objects/<sha256>
  obb/
    objects/<sha256>
    staging/<pack-sha256>.part
    staging/<pack-sha256>.zip
```

`obb/` ở đây chỉ là thư mục app-specific, không phải Google Play Expansion OBB. Object lớn có thể ở `obb/`, metadata và object nhỏ ở `data/`. Bản thân manifest xác định path đích; ZIP entry không được tự quyết định đường dẫn giải nén. Object chỉ được ghi sau xác minh và qua rename/atomic move.

Manifest của mỗi release liệt kê hash cần dùng. Garbage collector tính tập object được tham chiếu bởi `active` và các release đang giữ để rollback; chỉ xóa object không còn được tham chiếu, không phải staging active, và chưa bị reader sử dụng. Không xóa release cũ cho tới khi release mới active, self-test đạt và không còn WebView đang đọc release cũ.

Kiểm tra dung lượng trước tải và trước giải nén: download bytes còn thiếu + staging + installed bytes mới + reserve. Tài liệu thiết kế hiện đặt reserve 32 MiB; hiệu chỉnh sau benchmark thực tế. Nếu thiếu, báo số cần trống và giữ nguyên active release. Có thao tác xóa tài nguyên rõ ràng, hiển thị dung lượng giải phóng và xác nhận; không tự xóa full pack trong cleanup nền.

## 4. Các work package

### WP0 — Kiểm kê, LFS và chính sách phát hành

1. CI checkout/fetch LFS đúng cách; thêm kiểm tra fail nếu file ảnh/media vẫn là LFS pointer (`version https://git-lfs.github.com/spec/v1`) hoặc file byte-size bất thường.
2. Tạo inventory reproducible: đường dẫn, size, MIME, LFS state, owner/source/license, tham chiếu từ web/data/runtime; ghi nhận file bị loại.
3. Xác định allowlist core/full/optional bằng tham chiếu code, không lấy nguyên toàn bộ repository; chặn symlink, path traversal, file dev/test/log/secret/save.
4. Ghi rõ quyền phân phối lại ảnh/âm thanh/nội dung trước khi phát hành pack public.

**Đầu ra:** báo cáo kích thước thật, allowlist reviewable và CI guard LFS.

### WP1 — Builder manifest/pack xác định

1. Viết `tools/build_offline_resource_manifest.py` với `--check`, `--output`, `--max-pack-bytes`, `--resource-version`.
2. Sinh cùng output/hash khi cùng input/options; sort path ổn định, chuẩn hóa metadata và timestamp ZIP (không chứa mtime hiện tại).
3. Chia pack theo nhóm/kích thước; tạo SHA-256 pack + từng file; tránh file lặp theo hash; xuất báo cáo tổng tải/cài và danh sách thiếu/trùng.
4. Reject path tuyệt đối, `..`, symlink, Unicode/path conflict/case collision, LFS pointer, file ngoài root/allowlist và tổng vượt giới hạn.
5. Thêm tests fixtures nhỏ cho reproducibility, archive traversal, file bị đổi, LFS pointer, giới hạn pack và manifest coverage.

**Đầu ra:** manifest + pack local tái lập được, chưa tự động publish.

### WP2 — Xác thực manifest và kiểm soát an toàn

1. Chốt format canonical Ed25519 phù hợp với Java/Android và generator Python; thêm vector test ký/xác minh liên ngôn ngữ.
2. Thêm verifier trước khi tin bất kỳ URL/path/hash nào; public key pin trong app và key rotation có `key_id`/overlap policy.
3. Hardening redirect/host validation, HTTPS, timeout, giới hạn kích thước, ZIP bomb/path, duplicate entries, MIME/path map, cancellation và atomic state.
4. Bổ sung test kiểm tra signature sai/thiếu, unknown key, URL host sai, path traversal và không làm đổi active version khi lỗi.

**Đầu ra:** manifest không thể bị thay thế âm thầm chỉ bằng cách đổi checksum trong cùng file.

### WP3 — Android download orchestration/UI

1. Tích hợp manager qua repository/service riêng; Activity không tự làm network, unzip hoặc hash trên main thread.
2. Dùng WorkManager unique work có constraint mạng (Wi-Fi-only nếu người dùng chọn), tiến độ notification và retry backoff; tác vụ dài chuyển foreground theo yêu cầu Android. Quyền notification/API level và policy foreground service cần xác minh trong build/thiết bị.
3. Lưu job state/version/pack/checkpoint bền vững. Sau process death, khởi động lại phải kiểm `.part`, xác minh lại byte range/ETag/expected total rồi tiếp tục; không tin state UI còn RAM.
4. UI hiển thị version hiện tại, total/remaining bytes, số pack, progress thực, Wi-Fi/mobile data, dung lượng trống, pause/resume/cancel/retry và lỗi chi tiết. Không báo 100% trước verify/install/activation.
5. Nút **Mở game** chỉ active khi core/full resource đúng phạm vi được cài, verify và self-test; mở lại app offline đọc active metadata tại chỗ, không gọi `/readyz`.
6. Xóa/cập nhật có confirmation và cleanup riêng; tránh race với download/install/WebView reader bằng lock/state machine.

**Đầu ra:** người dùng bắt đầu tải có chủ đích; download sống qua đóng Activity/restart; lỗi không làm hỏng active release.

### WP4 — Local resource origin và WebView routing

1. Bundled shell nhỏ hoặc entrypoint core được cài ở local root; assets lớn nằm ở app-private store.
2. Dùng `WebViewAssetLoader` hoặc `WebViewClient`/handler giới hạn tương đương để ánh xạ origin HTTPS-like riêng sang allowlisted release, không dùng `file://` và không expose đường dẫn filesystem.
3. Chỉ resolve URL asset qua manifest active; validate normalized relative path, MIME, range cho media nếu cần; `404` chẩn đoán file/version thiếu thay vì fallback production.
4. Xử lý CORS, CSP, secure origin, cookies/storage namespace, service-worker policy và thay release khi WebView đóng/reopen.
5. Chặn tuyệt đối request game API đến production khi `offline-local`; API local là một work package riêng, không giả lập trả thành công từ asset handler.

**Đầu ra:** web shell đọc được asset đã cài bằng airplane mode; network trace không có request production cho shell/asset.

### WP5 — Versioning, cập nhật và garbage collection

1. Giữ `active` và metadata theo version; resource version mới staging riêng, activation atomic sau self-test.
2. Chỉ tải pack/hash còn thiếu; hash object được chia sẻ giữa release; retry/resume không tải lại bytes đã hợp lệ.
3. Nếu update lỗi/thiếu dung lượng/hash mismatch, giữ version trước chạy được và hiển thị update lỗi; có rollback được kiểm thử.
4. GC tham chiếu dựa trên active + retained rollback releases + lock/readers; chạy sau activation và có thể dry-run/báo bytes trước xóa.
5. Có chính sách giữ mặc định: active + một release gần nhất để rollback (điều chỉnh theo dung lượng), staging cũ được dọn chỉ khi không có job đang chạy.

**Đầu ra:** nâng resource không làm mất bản đang chơi; dọn chỉ giải phóng dữ liệu chắc chắn không được tham chiếu.

### WP6 — CI/release và telemetry tối thiểu

1. Workflow riêng chạy hydrate/validate LFS, builder/tests, verify manifest/signature/hash và upload artifacts.
2. Không public tự động theo mọi push; publish versioned release chỉ từ workflow/tag được duyệt. Bật immutable/no-overwrite/cache policy phù hợp cho CDN.
3. Không đưa secret phát hành vào repository/artifact/APK/log. Nếu chưa có CDN, artifact CI chỉ là artifact thử nghiệm, không phải URL downloader production.
4. Telemetry opt-in hoặc local diagnostics: version app/resource, elapsed time, bytes, pack ID/hash prefix, error category; không ghi save, token, signed URL hay danh tính tài khoản.

**Đầu ra:** artifact tái lập, kiểm được checksum, có nguồn phân phối và policy cache/version rõ ràng.

## 5. Test matrix bắt buộc

| Nhóm | Ca thử | Kết quả yêu cầu |
|---|---|---|
| Manifest | chữ ký sai/thiếu, version schema mới, host lạ, URL redirect sang host khác | Từ chối trước khi cài; active version giữ nguyên |
| Pack integrity | hash pack/file sai, ZIP entry trùng hoặc `../`, size/file count vượt giới hạn | Dừng an toàn; không ghi ra ngoài root; không activation |
| LFS/release | file LFS pointer còn sót, file nguồn đổi sau inventory | CI fail; không tạo release sai |
| Resume | mất mạng, timeout, đóng Activity, force-stop, reboot rồi tiếp tục | Xác minh partial/range rồi tiếp tục; không báo complete sớm |
| Storage | thiếu dung lượng trước tải, lúc tải, khi extract | Báo bytes cần giải phóng; giữ active release và save |
| Lifecycle | app update, resource update lỗi, rollback, xóa resource | Version tương thích còn dùng; chỉ xóa sau xác nhận và refcount |
| WebView | tắt mạng, xóa HTTP/WebView cache, mở shell/assets, range media | Local resolver trả đúng resource; không gọi production |
| Hiệu năng | thiết bị Android RAM/dung lượng thấp, nhiều file nhỏ, pack lớn | UI không block/ANR; RAM/CPU/thời gian đo được; có giới hạn hợp lý |

## 6. Trình tự và cổng quyết định

1. **Gate 0 — dữ liệu đúng:** xác nhận LFS hydrate + allowlist + kích thước/license. Không đóng pack trước gate này.
2. **Gate 1 — pipeline:** builder deterministic, manifest/pack/checksum, tests pass; phát hành nội bộ artifact thử nghiệm.
3. **Gate 2 — downloader:** tích hợp UI/WorkManager/resume/storage checks; hoàn thành Android unit/instrumentation tests.
4. **Gate 3 — local resolver:** WebView đọc shell + assets đã cài, force-stop/airplane-mode vẫn truy cập được; không có production request cho resource.
5. **Gate 4 — update/rollback:** version mới, pack lỗi, thiếu dung lượng và GC giữ đúng active release.
6. **Gate 5 — device beta:** thử trên thiết bị thật và kiểm chứng quyền phát hành nội dung; chỉ lúc này mới đánh dấu downloader beta-ready.

Không đưa công khai lời hứa “chơi offline đầy đủ” tại Gate 5 nếu local API/engine/save chưa qua các cổng trong quyết định Android offline.

## 7. Các quyết định kỹ thuật cần khóa trước khi code

- Danh sách resource `core/full/optional` và dung lượng mục tiêu sau LFS hydration.
- Host phát hành/CDN, immutable URL, redirect/cache policy; ai có quyền publish release.
- Quy ước canonical serialization/chữ ký manifest và key rotation.
- Tương thích version app/resource và chính sách giữ release rollback.
- Quyền/phạm vi nội dung game được phép đóng gói và tải xuống lại.
- Tương thích local URL/origin với WebView API, CORS, CSP, cookie và cấu trúc route game.
- Tối thiểu Android/API level và thiết bị thật dùng làm benchmark.

## 8. Không thuộc phạm vi Asset Downloader

Downloader không thay thế login, API gameplay, chiến đấu, economy, campaign state, save engine hoặc local profile. Không được đánh dấu các chức năng này “offline” chỉ vì asset đã có trên máy. Phần local API/save và chế độ offline của frontend phải có thiết kế, code, test và cổng nghiệm thu riêng.
