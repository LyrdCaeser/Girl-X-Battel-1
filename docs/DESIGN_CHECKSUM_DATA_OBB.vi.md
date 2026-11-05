# Thiết kế kiểm tra tính toàn vẹn cho tài nguyên `data/` và `obb/`

**Dự án/nhánh:** Girl-X-Battel-1 · `feature/offline-mode`

**Phạm vi:** Android resource downloader và kho tài nguyên app-specific `files/data/`, `files/obb/`

**Trạng thái:** Đặc tả thiết kế; chưa triển khai xác minh chữ ký manifest hoặc kiểm tra định kỳ đầy đủ.

## 1. Mục tiêu bảo vệ

Cơ chế phải phát hiện được tải thiếu byte, dữ liệu thay đổi trên đường truyền, pack hỏng, file hỏng khi giải nén, ghi dở do app/thiết bị dừng, file bị sửa sau khi cài và manifest bị thay bằng manifest không thuộc bản phát hành chính thức. Lỗi ở `data/` và `obb/` phải được xử lý giống nhau về độ tin cậy; khác biệt thư mục chỉ là nơi lưu file, không làm thay đổi thuật toán hash.

Thiết kế tách hai câu hỏi:

1. **Integrity:** bytes đang có có khớp chính xác với bytes mà manifest mô tả không?
2. **Authenticity:** manifest và các hash trong đó có thực sự do nhà phát hành phát hành không?

SHA-256 trả lời câu hỏi thứ nhất. Chỉ hash trong manifest chưa ký không trả lời được câu hỏi thứ hai, vì người thay được cả file lẫn manifest có thể tính lại hash.

## 2. Layout và phân loại lưu trữ

Với `applicationId` hiện tại `com.quangho.goddess.battle`, app truyền `context.getExternalFilesDir(null)` cho manager; layout tương ứng là:

```text
Android/data/com.quangho.goddess.battle/files/
├── data/
│   ├── manifests/<resource-version>.json
│   ├── active-version
│   └── objects/<prefix>/<sha256>.blob       # shell, config, JSON/Lua và file nhỏ
└── obb/
    ├── staging/<resource-version>/<pack>.zip.part
    └── objects/<prefix>/<sha256>.blob       # ảnh, âm thanh, Spine và asset lớn
```

`obb/` tại đây là thư mục app-specific theo layout game; không phải Google Play Expansion OBB. `data/` và `obb/` đều có vòng đời theo dữ liệu ứng dụng; kiểm tra hash không thể giữ file sau khi người dùng xóa dữ liệu hoặc gỡ app.

Cùng một file/hash phải được đặt theo một quy tắc xác định. Implementation hiện phân loại dựa trên đuôi phổ biến và ngưỡng kích thước 1 MiB. **Trước khi phát hành resource pack**, nên chuyển quy tắc này thành metadata `storage_class: "data" | "obb"` trong manifest đã ký. Như vậy thay đổi thuật toán phân loại ở app mới không làm client đặt nhầm object vào thư mục khác. Mọi file phải thuộc đúng một pack; đường dẫn logic trong manifest vẫn giữ nguyên, resolver tra hash để mở từ một trong hai vùng.

## 3. Thuật toán và chuỗi tin cậy

Dùng **SHA-256** cho pack và từng file. Không dùng MD5/SHA-1; CRC32 có sẵn trong ZIP chỉ dùng phát hiện lỗi ZIP thông thường, không thay thế SHA-256.

```text
Manifest bytes --chữ ký nhà phát hành--> manifest đáng tin cậy
     │
     ├── pack.size_bytes + SHA256(pack ZIP bytes)
     │        └── từng entry: path + size_bytes + SHA256(file bytes)
     │                  └── object lưu theo hash trong data/ hoặc obb/
     └── resource_version/build_id/platform/application_id
```

Mỗi phép kiểm tra dùng cả **kích thước** và **SHA-256**. Kích thước phát hiện file thiếu/thừa nhanh; SHA-256 xác nhận nội dung chính xác. Không coi ETag, tên file, timestamp, CRC ZIP hoặc HTTP 200 là bằng chứng integrity.

### 3.1 Manifest phát hành

Manifest hiện tại v1 đã có `size_bytes` và `sha256` cho pack cùng danh sách file có `path`, `size_bytes`, `sha256`. Phiên bản tiếp theo cần bổ sung:

- `application_id`, `platform`, `resource_version`, `build_id`, `manifest_version`, `minimum_app_version`.
- Mỗi file: `path`, `storage_class` (`data`/`obb`), `size_bytes`, `sha256`, `pack_id`.
- Mỗi pack: `id`, URL HTTPS bất biến, `size_bytes`, `sha256`, danh sách file thuộc pack.
- Báo cáo `total_download_bytes`, `total_unpacked_bytes`, số file/gói để UI kiểm dung lượng.

CI tính hash trên **bytes đúng như sẽ được phát hành**, sắp xếp entry ổn định, từ chối path tuyệt đối/`..`, file ngoài allowlist, path trùng, pack thiếu file và cùng hash nhưng size mâu thuẫn. Bản manifest được ký bằng private key chỉ nằm trong CI/release environment; app pin public key. Dùng thuật toán chữ ký chuẩn qua thư viện/provider đã được kiểm tra tương thích `minSdk 26` (không tự viết crypto). Ký chính xác bytes UTF-8 của manifest hoặc dùng quy tắc canonical JSON được thống nhất; không parse rồi serialize lại tùy tiện trước khi verify chữ ký. Có `key_id` và quy trình xoay key: bản app mới tin key mới, manifest chuyển tiếp được ký bởi key hiện tại; không chấp nhận key lạ tự khai báo trong manifest.

Chỉ sau khi chữ ký hợp lệ mới tin các hash, URL, version và storage class. Sau đó parser vẫn phải kiểm schema, host allowlist, path, giới hạn kích thước, số file/pack và URL HTTPS.

## 4. Luồng tải, giải nén và kích hoạt

### 4.1 Xác minh manifest

1. Tải manifest qua HTTPS từ host trong allowlist.
2. Giới hạn byte đọc trước khi parse để tránh manifest phình bất thường.
3. Xác minh chữ ký trên bytes gốc; từ chối chữ ký sai/thiếu, key không được pin, `application_id`/platform không khớp hoặc schema không hỗ trợ.
4. Parse và kiểm tra mọi hash theo dạng 64 ký tự hex, mọi size trong giới hạn, không có path trùng/path traversal và mỗi file chỉ được ánh xạ duy nhất.

### 4.2 Tải pack có resume

1. Lưu pack tạm ở `obb/staging/<resource-version>/<pack-id>.zip.part`.
2. Nếu mạng ngắt, giữ `.part` và trạng thái byte hiện có. File `.part` **không bao giờ** được xem là đã xác minh hoặc mở cho game dùng.
3. Khi tiếp tục, gửi `Range: bytes=<offset>-`. Nếu server trả `206`, kiểm tra `Content-Range` bắt đầu đúng offset và tổng size bằng manifest. Nếu server bỏ qua Range và trả `200`, ghi đè từ byte 0; nếu trả `416`, xóa part và tải lại từ đầu một lần.
4. Sau khi tải đủ, kiểm tra đúng `size_bytes` và `SHA256(zip bytes)` theo manifest. Sai một trong hai: không giải nén; xóa/quarantine pack tạm, ghi mã lỗi và tải lại pack từ nguồn tin cậy.
5. Không dùng ETag thay hash; có thể dùng ETag làm tối ưu resume/cache nhưng hash vẫn là điều kiện quyết định.

### 4.3 Giải nén và ghi object

1. Chỉ giải nén sau khi pack ZIP đã được xác minh đầy đủ.
2. So từng ZIP entry với allowlist file trong pack: reject entry thừa, trùng, thiếu, path traversal, đường dẫn tuyệt đối/backslash, entry vượt size đã khai báo hoặc tổng byte giải nén vượt giới hạn.
3. Đọc từng entry theo stream, tính SHA-256 và byte count trên đúng bytes giải nén. CRC của ZIP là lớp phụ; SHA-256 từng file mới là tiêu chuẩn.
4. Ghi vào file tạm trong cùng filesystem với object đích (`data/objects/...` hoặc `obb/objects/...`), flush/fsync, xác minh xong rồi atomic rename sang `<sha256>.blob`. Không tạo output path trực tiếp từ tên trong ZIP; chỉ lấy `ResourceFile` đã được manifest xác minh.
5. Nếu object cùng hash đã tồn tại, trước khi reuse phải kiểm tra ít nhất size và SHA-256. Object hỏng được thay bằng object tạm đã xác minh, không ghi đè in-place.
6. Các object mới có thể nằm trong kho trước khi release active; resolver không được phục vụ chúng cho tới khi manifest của release hoàn tất.

### 4.4 Kích hoạt atomic

Sau khi mọi pack và mọi file bắt buộc đã qua hash:

1. Lưu manifest đã xác minh vào `data/manifests/<version>.json` bằng temp file + fsync + atomic rename.
2. Ghi `active-version.tmp`, fsync rồi atomic rename thành `active-version`.
3. Resolver chỉ đọc release được trỏ bởi `active-version`; nếu app/process dừng trước bước 2, release cũ vẫn hoạt động.
4. Không xóa object release cũ khi đổi con trỏ. Garbage collection chỉ được xóa hash không còn được manifest active/rollback/download nào tham chiếu.

## 5. Kiểm tra sau cài đặt và khi dùng offline

`resolveResourceFile()` hiện kiểm tra file tồn tại và size; `verifyVersion()` hiện hash lại tất cả object. Cần giữ khác biệt rõ giữa hai kiểu kiểm tra:

- **Quick startup check:** xác minh chữ ký manifest đã lưu, active pointer hợp lệ, version tương thích và các file core tồn tại/đúng size. Nếu thiếu core file, không báo “đã tải trọn bộ”.
- **Install-time check:** luôn SHA-256 toàn bộ pack và từng file (bắt buộc, đồng bộ trước activation).
- **First-use check:** hash lại object lần đầu dùng trong mỗi process trước khi cấp cho WebView/game; cache trạng thái chỉ trong RAM theo `{release, sha256, size}`. File JS/config/JSON nhỏ có thể rehash mỗi lần app mở; asset lớn hash trước lần đầu sử dụng trong process.
- **Deep audit:** chạy `verifyVersion()` theo yêu cầu người dùng hoặc tác vụ nền có giới hạn pin/mạng. Có thể kiểm toàn bộ 31.506+ file/970 MiB theo batch; hiển thị tiến độ và không chặn màn hình khởi động lâu.

Không coi mtime là bằng chứng hash. Nếu file được phân phối trực tiếp từ app-specific external storage, tránh TOCTOU: ưu tiên API mở stream/descriptor từ object đã xác minh; nếu dùng path cho WebView, hash ngay trước khi cấp file và giới hạn việc app khác sửa vùng lưu trữ. Bản ghi “đã xác minh” lưu trên thiết bị chỉ là cache hiệu năng, không thay thế chữ ký manifest hoặc hash lại khi cần.

## 6. Phát hiện hỏng, sửa chữa và fallback

Khi integrity fail, manager trả lỗi phân loại (`MANIFEST_SIGNATURE_INVALID`, `PACK_HASH_MISMATCH`, `FILE_HASH_MISMATCH`, `MISSING_OBJECT`, `SIZE_MISMATCH`, `ZIP_PATH_REJECTED`, `INSUFFICIENT_STORAGE`, `RESUME_RANGE_INVALID`). Log chỉ ghi version, pack ID/hash prefix, path logic cần thiết và error code; không ghi token/presigned query hoặc dữ liệu save.

- Đánh dấu object sai là **corrupt**; tuyệt đối không trả object đó cho game, dù file có đúng tên hash.
- Tìm pack chứa file hỏng từ manifest đã ký; chỉ tải lại pack đó nếu có mạng. Không tải lại toàn bộ 1 GiB.
- Nếu offline, giữ lỗi ở trạng thái cần sửa và dùng bản trước chỉ khi bản trước đã được cài + xác minh đầy đủ + tương thích. Nếu không có bản tốt, hiển thị “Tài nguyên bị hỏng/thiếu — cần kết nối để sửa”; không fallback âm thầm sang server online.
- Với pack resume bị hash sai, xóa part và thử lại từ đầu theo retry có giới hạn/backoff. Sau số lần vượt giới hạn, dừng và cho người dùng thử lại.
- `active-version` không đổi cho tới khi repair/update đủ điều kiện activation.

## 7. Phân biệt hỏng dữ liệu với nội dung độc hại

Checksum SHA-256 chứng minh bytes khớp với manifest, không chứng minh asset có nội dung an toàn hoặc có quyền phân phối. Chữ ký manifest xác nhận nguồn phát hành nhưng không thay kiểm tra license, parser an toàn, URL host allowlist, sandbox path hoặc CSP. Không thực thi Lua/binary từ resource pack nếu runtime chưa có sandbox và policy riêng.

## 8. Kiểm thử bắt buộc

1. Pack/file chuẩn và đúng size/hash trong cả `data` lẫn `obb`.
2. Sửa 1 byte, truncate, append byte, size đúng nhưng hash sai; mỗi trường hợp phải bị phát hiện.
3. ZIP CRC sai, SHA pack sai, entry thiếu/thừa/trùng, path `../`, absolute path, backslash, zip bomb và entry dài hơn size manifest.
4. Manifest bị sửa 1 byte, chữ ký sai, `key_id` lạ, app ID/platform sai, hash sai format, version/schema không hỗ trợ.
5. Range resume chuẩn; server trả 200 thay 206; 416; Content-Range sai; đổi pack giữa hai lần tiếp tục; part đã đủ size nhưng sai hash.
6. Crash/force-stop trong lúc tải, giải nén, ghi manifest và đổi active pointer; sau khởi động không được coi bản dở là active.
7. Object đã cache nhưng bị thay đổi; object share giữa hai release; repair không xóa hash còn được release rollback tham chiếu.
8. Kiểm layout route: JSON/JS nhỏ ở `data/`, media/lớn ở `obb/`, manifest storage class khớp vị trí, resolver từ chối file ngoài manifest.
9. Benchmark deep audit trên thiết bị thật với full resource khoảng 970 MiB; đo pin, thời gian, peak storage và khả năng resume.

## 9. Điều kiện nghiệm thu

- Tất cả pack và file được hash bằng SHA-256; không có trạng thái “installed/active” trước khi mọi hash bắt buộc khớp.
- Manifest được verify bằng public key nhà phát hành đã pin trước khi tin URL/hash/storage class.
- `data/` và `obb/` có cùng tiêu chuẩn integrity, mapping trong manifest nhất quán và không phụ thuộc WebView cache.
- Tệp lỗi không bao giờ được mở; có thể sửa theo pack mà không tải lại resource không đổi.
- Tắt mạng sau khi full install vẫn đọc được file đã xác minh; file thiếu/hỏng được báo chính xác và không giả vờ hoàn tất.
- Update/crash không phá release đang hoạt động; rollback chỉ dùng release được xác minh.

## 10. Trạng thái implementation hiện tại và các bước tiếp theo

`OfflineResourceManager.java` hiện đã có SHA-256 cho ZIP pack và từng file giải nén; so kích thước, resume `.part`, giới hạn HTTPS host, kiểm đường dẫn ZIP, lưu object content-addressed vào `data/` hoặc `obb/`, và chuyển manifest active sau khi gói thành công. `verifyVersion()` hash lại toàn bộ object; `resolveResourceFile()` hiện mới kiểm tra tồn tại/kích thước.

Các khoảng trống cần làm trước phát hành: (1) chữ ký manifest/key rotation; (2) `storage_class` được ký thay cho heuristic đuôi/size; (3) xác minh manifest đã lưu khi startup; (4) first-use/deep-audit và repair per-pack; (5) test mạng Range và crash/restart; (6) kết nối manager vào worker/UI. Đây là thiết kế kiểm soát toàn vẹn, chưa phải tuyên bố các hạng mục đó đã được code.
