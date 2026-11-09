# Kiểm tra khả năng truy cập CDN tài nguyên offline

**Kiểm tra ban đầu:** 2026-11-09 05:55 (+07:00)
**Kiểm tra sau sửa:** 2026-11-09 06:26 (+07:00)
**CDN:** `d22ubllklhmcic.cloudfront.net`

## Phát hiện ban đầu

- GET `https://d22ubllklhmcic.cloudfront.net/offline-resources/manifest.json`: **200 OK**, 6.429.298 byte, `application/json`.
- Manifest cũ có `resource_version=web-ec1f31f32725`, **97 packs**, **31.667 file**.
- GET với `Range: bytes=0-0` tới pack mẫu trả **403 AccessDenied** từ Amazon S3, `X-Cache: Error from cloudfront`.

Pack mẫu cũ: `https://d22ubllklhmcic.cloudfront.net/offline-resources/web-ec1f31f32725/pack-969203c147a72ad54e18265130ae9480aa6d37a0658d95ebb38d11da0e8a7188.zip`

Nguyên nhân cụ thể trong cấu hình workflow là manifest cũ dùng `web-${GITHUB_SHA:0:12}`, trong khi upload dùng `web-${{ github.sha }}` (SHA đầy đủ). Vì vậy manifest trỏ tới prefix khác nơi publisher lưu các pack. Đây là lỗi version-path khớp với 403; trước khi republish vẫn cần xét khả năng còn vấn đề bucket policy/OAC nếu lỗi tiếp tục.

## Sửa và kết quả publish

- Commit pipeline `f9ff576d09008e445c2cdce31607f86fb21a8960` dùng chung `RESOURCE_VERSION=web-${{ github.sha }}` cho manifest và upload.
- `tools/publish_offline_resource_s3.sh` từ chối sai version/prefix/URL trước khi upload; mock DRY_RUN đã xác nhận mismatch bị chặn trước `aws s3 cp`.
- GitHub Actions run [42533667739](https://github.com/LyrdCaeser/Girl-X-Battel-1/actions/runs/42533667739) chạy trên `feature/offline-mode` và hoàn tất **success** sau 17m34s, gồm hydrate Git LFS, build, OIDC và S3/CloudFront publish.
- Manifest mới trả **200 OK**, 6.432.958 byte; `resource_version=web-f9ff576d09008e445c2cdce31607f86fb21a8960`, 97 packs và 31.667 file.
- Gửi `Range: bytes=0-0` song song tới mọi URL pack: **97/97 trả HTTP 206**, không có lỗi; toàn bộ URL ở đúng HTTPS CloudFront host và version prefix.

## Android release gate

`android-offline-release-gate.yml` đã được sửa cục bộ để lấy manifest thật, xác minh chữ ký Ed25519, kiểm tra từng pack trước khi build, truyền manifest URL/trusted host/public key vào Gradle, và chỉ cấp secrets cho những step cần dùng. Phần này cùng guest/campaign Android changes sẽ được đẩy ở giai đoạn 2 sau khi đạt kiểm tra CDN.

**Trạng thái AWS/CDN:** publish S3 và invalidation đã chạy trong run nêu trên; không có thay đổi bucket policy hoặc OAC. Chưa chạy Android production gate ở thời điểm cập nhật báo cáo này.
