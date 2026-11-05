# Thiết kế luồng đồng bộ save offline với AWS S3

**Trạng thái:** Đề xuất thiết kế — chưa phải mô tả tính năng đã triển khai
**Phạm vi:** Sao lưu và khôi phục save game giữa các thiết bị iOS/Android; không đồng bộ asset game trong luồng này.

## 1. Hiện trạng và quyết định thiết kế

Migration [`0001_offline_accounts_devices_sync.sql`](../migrations/0001_offline_accounts_devices_sync.sql) định nghĩa metadata tài khoản, thiết bị và trạng thái đồng bộ. Comment trong migration nói rõ save có thẩm quyền và asset vẫn ở thiết bị; schema không chứa payload save. Hiện chưa có luồng ứng dụng ghi/đọc S3.

Ngoài ra, client iOS và Android hiện là các vỏ WKWebView/WebView trỏ tới máy chủ online, chưa phải client offline có kho save cục bộ hoàn chỉnh. Xem [`GXB3App.swift`](../clients/ios/GXB3App.swift) và [`MainActivity.java`](../clients/android/app/src/main/java/com/gxb3/game/MainActivity.java). Vì vậy, thiết kế này là mục tiêu cần triển khai; không giả định chỉ cần bật bucket là sync hoạt động.

Thiết kế chọn các nguyên tắc sau:

- Bản save cục bộ tiếp tục là nguồn dữ liệu có thẩm quyền khi thiết bị offline. S3 giữ các snapshot để backup/khôi phục và chuyển save giữa thiết bị, không thay thế gameplay backend hiện tại.
- Backend xác thực người chơi, thiết bị và quyền truy cập; backend cấp quyền truyền object có thời hạn. Ứng dụng không chứa AWS access key/secret key.
- Bucket là private. Save được tải trực tiếp giữa thiết bị và S3 bằng presigned URL ngắn hạn, tránh đưa payload lớn qua API.
- Một revision cloud hiện hành được xác định theo **tài khoản + stream**, không theo thiết bị. Metadata riêng từng thiết bị vẫn được giữ để ghi nhận revision cục bộ và lần sync cuối.
- Không tự hợp nhất nội dung save game. Nếu hai bản cùng xuất phát từ một revision cloud cũ, giữ cả hai và yêu cầu người chơi chọn bản cần khôi phục/đẩy lên.

## 2. Thành phần

1. **Client offline:** Có kho save bền vững trên thiết bị, tạo `installation_id` ngẫu nhiên cho mỗi lần cài đặt, theo dõi `local_revision`, checksum và hàng đợi sync. Không dùng IMEI, advertising ID hay định danh phần cứng làm khóa thiết bị.
2. **Sync API:** Các endpoint có xác thực phiên người dùng. API kiểm tra tài khoản còn hoạt động, thiết bị chưa bị thu hồi, giới hạn kích thước/version/schema và trạng thái stream trước khi tạo quyền S3.
3. **PostgreSQL riêng cho offline:** Áp dụng schema vào database dành riêng cho bản offline (`gxb2_offline` theo comment migration), không áp dụng migration này lên database của dự án Online. PostgreSQL là nơi giữ metadata, upload session, revision cloud và tham chiếu tới object.
4. **S3 private bucket:** Chứa byte của các snapshot save. Bật Block Public Access, versioning, mã hóa mặc định, TLS-only policy và lifecycle dọn multipart upload chưa hoàn tất. S3 Versioning cho phép giữ và khôi phục các phiên bản object; mỗi lần ghi cùng key tạo version mới khi bật versioning. [4]
5. **AWS IAM role:** Gắn vào workload chạy backend (ví dụ task/container role). Cấp quyền tối thiểu theo bucket/prefix và thao tác cần dùng. Không cấp quyền liệt kê bucket hoặc credential dài hạn cho ứng dụng di động.

## 3. Điều chỉnh metadata cần có

Schema hiện có gồm `accounts`, `devices`, `sync_metadata`. `sync_metadata` có `UNIQUE (account_id, device_id, stream_key)`, nên nó biểu diễn trạng thái của từng thiết bị. Để nhiều thiết bị cùng đọc/ghi một đầu cloud chung, cần thêm bảng cấp tài khoản và bảng snapshot bất biến.

### `sync_heads` — đầu cloud theo tài khoản

Một hàng cho mỗi `(account_id, stream_key)`, gồm `cloud_revision`, `current_snapshot_id`, `updated_at`, trạng thái tombstone nếu người dùng xóa cloud save, và lock/version phục vụ cập nhật đồng thời. Tạo hàng đầu tiên khi tài khoản bật backup lần đầu.

### `sync_snapshots` — lịch sử các snapshot đã xác nhận

Một hàng cho mỗi revision đã commit, tối thiểu gồm:

- `snapshot_id`, `account_id`, `stream_key`, `cloud_revision`;
- `source_device_id`, `local_revision`, `base_cloud_revision`, `mutation_id`;
- `object_key`, `s3_version_id`, `checksum_sha256`, `size_bytes`, `save_schema_version`;
- `created_at`, và trạng thái xóa/khôi phục nếu cần.

Đặt unique constraint cho `(account_id, stream_key, cloud_revision)` và idempotency key `(account_id, mutation_id)`. `object_key` chỉ do server sinh, không nhận tùy ý từ client. Key không chứa username/email; ví dụ `offline-saves/<account-uuid>/<stream>/<upload-uuid>`.

### `sync_uploads` — phiên upload tạm

Lưu `upload_id`, tài khoản, thiết bị, stream, key do server sinh, revision gốc dự kiến, checksum/kích thước mong đợi, thời điểm hết hạn và trạng thái `pending|completed|conflict|expired`. Hàng pending bị bỏ dở sẽ được dọn định kỳ. Có thể gộp bảng này với snapshot nếu trạng thái và unique constraint vẫn phân biệt được upload chưa commit với snapshot đã công bố.

Giữ `sync_metadata` hiện có cho trạng thái từng thiết bị: `local_revision`, `acknowledged_local_revision`, `sync_status`, `last_sync_at`, `last_error_code`. Sau khi thiết bị đồng bộ xong, cập nhật metadata của thiết bị đó; không dùng hàng của một thiết bị làm head chung của cả tài khoản.

## 4. Luồng sync

### A. Đăng ký thiết bị và lấy trạng thái cloud

1. Người chơi đăng nhập bằng tài khoản hiện có.
2. Client gửi `installation_id`, platform, app version và `save_schema_version` tới `POST /api/offline-sync/v1/devices/register`.
3. Backend lấy `account_id` từ session đã xác thực; không tin `account_id` do client gửi. Backend tạo/cập nhật thiết bị và trả `device_id` cùng trạng thái thu hồi.
4. Client gọi `GET /api/offline-sync/v1/streams/game-save/head`.
5. Backend trả `cloud_revision`, checksum, schema version, kích thước snapshot gần nhất và trạng thái tombstone; không trả AWS credentials.
6. Nếu checksum và revision của bản local tương ứng head cloud, đánh dấu đã sync. Nếu chưa có head, hiển thị tùy chọn bật backup/tạo snapshot đầu tiên. Nếu local và cloud khác nhau, chuyển sang upload hoặc restore dựa trên revision gốc; không tự ghi đè.

### B. Upload snapshot mới

1. Client chụp save ổn định, serialize theo định dạng/version xác định, nén nếu cần, rồi tính SHA-256 trên **đúng byte sẽ upload**. Ghi file tạm và giữ bản local hiện hành cho tới khi server xác nhận commit.
2. Client gọi `POST /api/offline-sync/v1/uploads` với `stream_key`, `local_revision`, `base_cloud_revision`, `save_schema_version`, `size_bytes`, `checksum_sha256` và `mutation_id` UUID dùng để retry idempotent.
3. Backend kiểm tra quyền, giới hạn kích thước/schema, thiết bị active và `base_cloud_revision` so với cloud head hiện tại. Nếu đã lỗi thời, trả `409 Conflict` kèm head hiện tại trước khi bắt đầu tải lên.
4. Nếu hợp lệ, backend tạo `sync_uploads` pending, key riêng không đoán được, rồi cấp presigned `PUT` hết hạn ngắn (mặc định đề xuất 5 phút) cho đúng object key và checksum. URL là bearer token: ai có URL đều dùng được trong thời gian còn hiệu lực, nên không đưa URL vào log/analytics. AWS cho phép dùng presigned URL để upload mà không cấp credential AWS cho bên upload; cùng URL có thể được dùng lại trước khi hết hạn và upload lại cùng key sẽ thay object hiện hành. [1]
5. Client upload trực tiếp lên S3 bằng đúng HTTP method, headers và checksum đã ký. SigV4 hỗ trợ SHA-256 checksum; S3 tự kiểm tra checksum upload và từ chối nếu dữ liệu không khớp. [1] [2]
6. Client gọi `POST /api/offline-sync/v1/uploads/{upload_id}/complete`. Backend tự đọc metadata S3 (không tin checksum/version do client tự khai), xác nhận kích thước, SHA-256 và version ID. Bucket versioning bật giúp backend pin đúng `s3_version_id`; nếu presigned URL bị dùng lại sau đó, snapshot đã commit vẫn trỏ tới version đã xác nhận. Mọi download luôn chỉ định version ID đó.
7. Backend mở transaction PostgreSQL và khóa `sync_heads` của tài khoản/stream. Kiểm tra lại `base_cloud_revision`. Nếu vẫn bằng head hiện tại, tạo revision kế tiếp, insert `sync_snapshots`, cập nhật `sync_heads.current_snapshot_id/cloud_revision`, đánh dấu upload complete, rồi commit trong cùng transaction.
8. Nếu một thiết bị khác đã thắng cuộc đua và head tăng, không công bố object của upload hiện tại. Đánh dấu conflict, giữ local save, trả `409`; object không được tham chiếu sẽ được janitor dọn sau thời hạn an toàn.
9. Client chỉ cập nhật `acknowledged_local_revision` và báo “đã backup” khi nhận xác nhận commit. Nếu mất kết nối sau bước 7, retry với `mutation_id` cũ để API trả kết quả đã commit thay vì tạo revision lặp.

Conditional requests của S3 có thể bổ sung điều kiện để tránh tạo/ghi object khi precondition không còn đúng; tuy nhiên, kiểm soát revision cloud vẫn phải được thực hiện nguyên tử trong transaction PostgreSQL vì S3 và PostgreSQL không có một transaction chung. [3]

### C. Tải/khôi phục snapshot

1. Client gọi `GET /api/offline-sync/v1/streams/game-save/snapshots/{cloud_revision}/download-url`.
2. Backend xác thực account/device, kiểm tra snapshot thuộc đúng account + stream và cấp presigned `GET` ngắn hạn cho đúng `object_key` **và `s3_version_id`**.
3. Client tải vào file tạm, xác minh SHA-256 bằng giá trị metadata, kiểm tra schema/version và parse trước khi áp dụng.
4. Client tạo backup cục bộ của save hiện tại, rồi thay thế bằng thao tác atomic (ghi file tạm, flush, rename). Nếu kiểm tra hoặc rename lỗi, giữ save hiện tại và báo lỗi khôi phục.
5. Client gọi API ghi nhận restore/sync để cập nhật `sync_metadata`. Khôi phục revision cũ không xóa lịch sử cloud; nếu người chơi tiếp tục chơi và muốn upload, client tạo snapshot mới với `base_cloud_revision` bằng head hiện tại sau khi người chơi xác nhận.

### D. Xử lý xung đột

Trả `409 Conflict` nếu `base_cloud_revision` khác head tại thời điểm hoàn tất. Client giữ cả hai bản và cung cấp lựa chọn rõ ràng: tải bản cloud, giữ bản local rồi tạo snapshot mới dựa trên head hiện tại, hoặc lưu bản local thành bản khôi phục riêng trước khi thay thế. Không tự merge inventory, tiền tệ, nhiệm vụ hoặc giao dịch game.

Nếu retry cùng `mutation_id`, API trả lại kết quả của lần xử lý trước. Nếu người dùng xóa save cloud, tạo tombstone trong PostgreSQL trước; không xóa object ngay khi nhận yêu cầu. Có thể áp dụng thời gian khôi phục (ví dụ 30 ngày), sau đó tác vụ backend xóa các version/object theo policy. Yêu cầu xóa tài khoản cần có luồng purge metadata và object độc lập, có audit và kiểm tra kết quả.

## 5. API đề xuất

- `POST /api/offline-sync/v1/devices/register` — đăng ký hoặc nhận lại device hiện tại.
- `POST /api/offline-sync/v1/devices/{device_id}/revoke` — thu hồi thiết bị; chặn cấp URL mới.
- `GET /api/offline-sync/v1/streams/{stream_key}/head` — lấy revision cloud hiện hành.
- `POST /api/offline-sync/v1/uploads` — tạo upload session và presigned PUT.
- `POST /api/offline-sync/v1/uploads/{upload_id}/complete` — xác minh object và commit revision.
- `GET /api/offline-sync/v1/streams/{stream_key}/snapshots/{revision}/download-url` — cấp presigned GET cho version cụ thể.
- `POST /api/offline-sync/v1/streams/{stream_key}/restore` — ghi nhận khôi phục và cập nhật metadata thiết bị.
- `DELETE /api/offline-sync/v1/streams/{stream_key}` — đặt tombstone, không xóa vật lý ngay.

Mọi API cần xác thực session, rate-limit theo account/device, giới hạn payload và idempotency cho thao tác tạo/commit. Endpoint quản trị xóa object không được cung cấp cho client.

## 6. Cấu hình và bảo mật S3

- Tạo bucket riêng theo môi trường, ví dụ `gxb2-offline-saves-prod`; không dùng chung bucket public chứa static assets.
- Bật S3 Block Public Access toàn bucket và tài khoản; cấm ACL public. Yêu cầu HTTPS/TLS bằng bucket policy. Mã hóa mặc định SSE-S3 là lớp bảo vệ at-rest cơ bản của S3; dùng SSE-KMS nếu cần kiểm soát khóa/audit cụ thể hơn, tính cả quyền KMS và chi phí tương ứng. SSE mã hóa object data nhưng không mã hóa metadata của object. [5]
- Bật versioning. PostgreSQL phải lưu `s3_version_id` cho từng snapshot, và tải đúng version đã xác minh; không dựa vào ETag như checksum tổng quát.
- Chỉ backend tạo presigned URL từ IAM role có quyền tối thiểu trên prefix save. URL chỉ cấp quyền cho một method, một key và headers đã định; thời hạn ngắn hơn thời hạn credential IAM. URL phải được coi như bí mật bearer và không ghi vào access log.
- Nếu client chạy trong WebView/browser, cấu hình CORS chỉ cho origin ứng dụng và method/header thực sự cần (PUT/GET/HEAD, checksum/content-type phù hợp); CORS không thay thế xác thực/policy bucket.
- Cấu hình lifecycle `AbortIncompleteMultipartUpload` (đề xuất sau 7 ngày) để dọn parts upload dở. AWS khuyến nghị lifecycle rule này để hạn chế chi phí; rule xóa các part chưa hoàn tất, không xóa object hoàn tất. [6]
- Đặt lifecycle/retention cho noncurrent versions và orphan object sau khi chốt yêu cầu khôi phục. Versioning làm tăng dung lượng vì mỗi version được tính như một object riêng; không xóa noncurrent version quá sớm nếu còn trong thời gian khôi phục. [4]
- Không bật multipart upload ở giai đoạn đầu nếu save nhỏ. Nếu cần hỗ trợ file lớn, thêm API initiate/sign-per-part/complete/abort, lưu upload ID, kiểm tra checksum từng phần và áp dụng lifecycle dọn upload dang dở.

## 7. Định dạng snapshot và giới hạn

Định dạng snapshot cần có `format`, `save_schema_version`, `game_version`, `local_revision` và payload save. Không đưa email, username, access token hay session cookie vào object/key. Quy định rõ canonical serialization hoặc checksum tính trên byte đã nén; cùng một quy tắc phải áp dụng ở upload và restore.

Đề xuất khởi đầu giới hạn save 10 MiB (giá trị cấu hình được), một stream `game-save`, và giữ 20 snapshot gần nhất hoặc theo hạn lưu được thống nhất. Đây là giới hạn sản phẩm ban đầu, không phải giới hạn tối đa của S3. Nếu file vượt giới hạn, từ chối rõ ràng thay vì âm thầm bỏ trường save.

Static assets không thuộc luồng này: chúng nên tiếp tục được đóng gói/cache riêng. Nếu sau này chuyển assets lên S3/CDN, thiết kế phân phối asset cần bucket/prefix, cache policy và kiểm tra toàn vẹn riêng; không trộn quyền public của assets với quyền riêng tư của save.

## 8. Lỗi, dọn rác và quan sát

Do upload S3 và commit PostgreSQL không thể nguyên tử cùng nhau, quy trình phải chấp nhận object mồ côi: upload pending quá hạn được đánh dấu expired; tác vụ định kỳ đối chiếu session/snapshot với object/version; chỉ xóa khi object không được metadata tham chiếu và đã qua grace period. Retry complete phải idempotent.

Ghi log `account_id` nội bộ, `device_id`, `upload_id`, `mutation_id`, revision, kích thước, latency, kết quả và mã lỗi. Không log URL ký, query string, save payload hoặc secret. Theo dõi tỷ lệ upload/restore lỗi, xung đột, object mồ côi, checksum mismatch, số lần retry và chi phí dung lượng/request. Báo người dùng phân biệt lỗi mạng, hết hạn URL, xung đột, save/schema không tương thích và lỗi lưu trữ.

## 9. Kế hoạch triển khai

1. **Chốt nền offline:** Hoàn thiện kho save cục bộ bền vững và định dạng/version save. Làm rõ khác biệt giữa client offline mới và các vỏ WebView online hiện tại.
2. **Tách database và schema:** Tạo database offline riêng; bổ sung migrations cho `sync_heads`, `sync_snapshots`, `sync_uploads`; không chạy migration offline lên Online.
3. **Tạo hạ tầng S3:** Bucket private theo môi trường, versioning, block public access, encryption, IAM role/policy, CORS tối thiểu và lifecycle multipart.
4. **Xây sync service/API:** Đăng ký/thu hồi thiết bị, head, upload init/complete, download/restore, idempotency, giới hạn dung lượng và cơ chế orphan cleanup.
5. **Tích hợp client:** Backup/restore có xác nhận người dùng, upload từ file snapshot, checksum verification, atomic local restore và UX xử lý conflict.
6. **Kiểm thử:** Unit test cho revision/CAS/idempotency; contract test S3 mock hoặc môi trường tương thích; staging test với bucket AWS thật; kiểm thử hai thiết bị upload cùng base revision, URL hết hạn/replay, checksum sai, revoke device, mạng đứt giữa upload và complete, khôi phục version cũ và xóa/tombstone.
7. **Phát hành có kiểm soát:** Bật backup theo feature flag, giới hạn tài khoản thử nghiệm, đo lỗi/chi phí trước khi mở rộng. Không bật tự động thay thế save local trên lần sync đầu.

### Điều kiện nghiệm thu

- Thiết bị mới có thể khôi phục snapshot cloud đúng tài khoản và đúng revision.
- Backend không cấp URL cho tài khoản/thiết bị không hợp lệ; không có AWS secret trong app hoặc response API.
- Checksum sai không được commit thành cloud head.
- Hai thiết bị cùng upload từ một base revision chỉ có tối đa một snapshot thắng; thiết bị còn lại nhận conflict và không mất save local.
- Retry cùng mutation không tạo revision trùng.
- Restore ghi file local an toàn và có thể quay lại bản cũ khi lỗi.
- Snapshot đã commit tải đúng `s3_version_id` kể cả khi object key có version mới hơn.
- Bucket không public; lifecycle, backup/retention và quy trình purge đã được kiểm tra ở staging.

## References

[1]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html "Download and upload objects with presigned URLs"
[2]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity-upload.html "Checking object integrity for data uploads in Amazon S3"
[3]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-requests.html "Add preconditions to S3 operations with conditional requests"
[4]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html "Retaining multiple versions of objects with S3 Versioning"
[5]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingServerSideEncryption.html "Using server-side encryption with Amazon S3 managed keys"
[6]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpu-abort-incomplete-mpu-lifecycle-config.html "Configuring a bucket lifecycle configuration to delete incomplete multipart uploads"
