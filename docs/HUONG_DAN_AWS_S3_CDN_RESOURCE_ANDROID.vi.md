# Hướng dẫn cấu hình AWS S3 + CloudFront cho Android resource pack

**Dự án:** Girl-X-Battel-1
**Nhánh:** `feature/offline-mode`
**Phạm vi:** phân phối resource pack công khai qua S3 private bucket + CloudFront OAC để Android tải, kiểm tra hash và lưu local.

> Tài liệu này chỉ cấu hình **static resource pack**. Nó không triển khai local API, engine chiến đấu, save gameplay hoặc đồng bộ save. Luồng save S3 là một hệ thống khác và phải dùng bucket private/presigned URL riêng.

## 1. Kiến trúc sau khi cấu hình

```text
Git checkout đã hydrate LFS
        |
        v
build_offline_resource_manifest.py
        |
        |  ZIP pack + manifest.json ký Ed25519
        v
S3 bucket private
s3://BUCKET/offline-resources/
        |
        |  CloudFront Origin Access Control (OAC)
        v
https://DISTRIBUTION.cloudfront.net/offline-resources/manifest.json
        |
        v
Android OfflineResourceDownloadWorker
        |
        v
Xác minh chữ ký + SHA-256 + cài atomic vào app-private storage
```

URL public của Android chỉ là URL CloudFront. Không đưa `s3://`, AWS access key, secret key hoặc credential IAM vào APK.

## 2. Chuẩn bị biến môi trường

Thực hiện trên máy release/CI có AWS CLI đã đăng nhập bằng IAM role hoặc profile có quyền tạo bucket, CloudFront và upload artifact.

```bash
export AWS_REGION=ap-southeast-1
export AWS_ACCOUNT_ID="123456789012"
export RESOURCE_BUCKET="gxb3-offline-resources-prod"
export RESOURCE_PREFIX="offline-resources"
export RESOURCE_VERSION="2026.11.05.1"
export CLOUDFRONT_DOMAIN="dxxxxxxxxxxxx.cloudfront.net"
```

Không commit các biến chứa secret. Kiểm tra identity:

```bash
aws sts get-caller-identity
aws configure get region
```

Tên bucket S3 phải duy nhất trên toàn AWS. Nên dùng bucket riêng theo môi trường, ví dụ `gxb3-offline-resources-staging` và `gxb3-offline-resources-prod`.

## 3. Tạo S3 bucket private

```bash
aws s3api create-bucket \
  --bucket "$RESOURCE_BUCKET" \
  --region "$AWS_REGION" \
  --create-bucket-configuration LocationConstraint="$AWS_REGION"

aws s3api put-public-access-block \
  --bucket "$RESOURCE_BUCKET" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

aws s3api put-bucket-versioning \
  --bucket "$RESOURCE_BUCKET" \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket "$RESOURCE_BUCKET" \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}
    }]
  }'
```

S3 static resource là nội dung phát hành, không phải save người chơi. Không đặt save snapshot vào bucket này.

### Bucket policy sau khi tạo CloudFront

Sau khi có CloudFront distribution và biết `DISTRIBUTION_ID`, đặt policy chỉ cho CloudFront đọc object. Thay các placeholder trước khi chạy:

```bash
export DISTRIBUTION_ID="E1234567890ABC"
cat > /tmp/resource-bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontReadOnly",
      "Effect": "Allow",
      "Principal": {"Service": "cloudfront.amazonaws.com"},
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$RESOURCE_BUCKET/$RESOURCE_PREFIX/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::$AWS_ACCOUNT_ID:distribution/$DISTRIBUTION_ID"
        }
      }
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket "$RESOURCE_BUCKET" \
  --policy file:///tmp/resource-bucket-policy.json
```

Không bật public-read ACL/policy. CloudFront OAC mới là principal được phép đọc.

## 4. Tạo khóa ký manifest Ed25519

Manifest được ký ở CI/release machine; Android chỉ nhúng **raw public key Base64**.

```bash
mkdir -p .secrets
openssl genpkey -algorithm Ed25519 \
  -out .secrets/offline-manifest-signing-key.pem
chmod 600 .secrets/offline-manifest-signing-key.pem

# SubjectPublicKeyInfo DER của Ed25519 dài 44 byte; 32 byte cuối là raw public key.
openssl pkey \
  -in .secrets/offline-manifest-signing-key.pem \
  -pubout -outform DER \
  | tail -c 32 \
  | base64 -w0 > .secrets/offline-manifest-public-key.b64
printf '\n'
wc -c .secrets/offline-manifest-public-key.b64
```

Kết quả phải là chuỗi Base64 dài 44 ký tự, giải mã được thành 32 byte:

```bash
python3 - <<'PY'
import base64
from pathlib import Path
value = Path('.secrets/offline-manifest-public-key.b64').read_text().strip()
raw = base64.b64decode(value, validate=True)
assert len(raw) == 32, len(raw)
print('Ed25519 raw public key: 32 bytes')
PY
```

- Private key: lưu trong secret store của CI/HSM, không commit.
- Public key: có thể đưa vào secret/protected variable của build Android.
- Khi rotate key, cần phát hành APK pin public key mới và có chính sách chuyển tiếp; không thay key trên CDN mà không phát hành app tương thích.

## 5. Hydrate LFS và tạo allowlist

Builder của repository cố ý từ chối file Git LFS pointer chưa được hydrate. Trên checkout release:

```bash
git lfs install
git lfs pull
```

Tạo allowlist đã được review, ví dụ `release/offline-allowlist.txt`:

```text
web/index.html
web/style.css
web/app.js
web/campaign-map.js
web/campaign-ui.js
web/battle-animation.js
web/assets/home-bg.png
web/assets/home-icons.png
data/stage.json
data/models.json
```

Đây chỉ là ví dụ nhỏ. Không dùng toàn bộ repository một cách mù quáng. Allowlist thực tế phải bao phủ đúng shell, data và assets của phạm vi gameplay đã kiểm thử; loại `.git`, logs, saves, secrets, test artifacts và tool files.

Kiểm tra file có thật và không còn pointer:

```bash
while IFS= read -r path; do
  test -f "$path" || { echo "missing: $path" >&2; exit 1; }
  ! grep -q '^version https://git-lfs.github.com/spec/v1$' "$path" \
    || { echo "unresolved LFS pointer: $path" >&2; exit 1; }
done < release/offline-allowlist.txt
```

## 6. Build pack và signed manifest

Cài dependency ký manifest trên release machine:

```bash
python3 -m venv .venv-release
.venv-release/bin/pip install 'cryptography>=41'
```

`tools/build_offline_resource_manifest.py` yêu cầu output directory mới hoặc rỗng. Base URL phải là HTTPS, không có query/fragment:

```bash
rm -rf release/offline-resources/$RESOURCE_VERSION

.venv-release/bin/python tools/build_offline_resource_manifest.py \
  --source-root . \
  --allowlist release/offline-allowlist.txt \
  --output-dir release/offline-resources/$RESOURCE_VERSION \
  --resource-version "$RESOURCE_VERSION" \
  --base-url "https://$CLOUDFRONT_DOMAIN/$RESOURCE_PREFIX" \
  --max-pack-size $((100 * 1024 * 1024)) \
  --private-key .secrets/offline-manifest-signing-key.pem
```

Output gồm:

```text
release/offline-resources/<version>/
  manifest.json
  pack-<sha256>.zip
  pack-<sha256>.zip
  ...
```

Manifest sẽ chứa URL pack dạng:

```text
https://DISTRIBUTION.cloudfront.net/offline-resources/<version>/pack-<sha256>.zip
```

Đây là lý do `--base-url` phải trỏ tới prefix CloudFront, không phải URL S3.

Kiểm tra nhanh manifest không phải unsigned dev output:

```bash
test ! -e release/offline-resources/$RESOURCE_VERSION/UNSIGNED_DEV_ONLY.txt
python3 - <<'PY'
import base64, json
from pathlib import Path
p = Path('release/offline-resources')
manifest = next(p.glob('*/manifest.json'))
data = json.loads(manifest.read_text())
assert set(data) == {'payload_b64', 'signature_b64'}
json.loads(base64.b64decode(data['payload_b64']))
base64.b64decode(data['signature_b64'])
print('signed envelope: OK')
PY
```

## 7. Tạo CloudFront distribution với OAC

Tạo distribution bằng AWS Console là cách ít lỗi hơn:

1. CloudFront → **Create distribution**.
2. Origin domain: chọn S3 bucket bằng REST origin, không chọn S3 website endpoint.
3. Origin access: tạo/chọn **Origin Access Control (OAC)**, signing behavior `Sign requests`.
4. Viewer protocol policy: `Redirect HTTP to HTTPS`.
5. Allowed methods: `GET, HEAD`.
6. Cache policy: `CachingOptimized` hoặc policy riêng chỉ cache theo path, không cache theo query string.
7. Không bật public bucket access.
8. Hoàn tất distribution, lấy `Distribution domain name` và `Distribution ID`.
9. Cập nhật bucket policy ở bước 3.

Có thể giới hạn behavior chỉ cho prefix `/offline-resources/*`. Không cần CloudFront Function, Lambda@Edge hoặc signed URL cho resource pack nếu manifest đã ký và pack có tên content hash. Nếu cần giới hạn người tải, đó là bài toán license/auth riêng; không nhúng AWS credential vào client.

## 8. Upload artifact lên S3

Upload pack trước, manifest sau. Các pack có URL version + SHA-256 nên dùng cache dài và immutable:

```bash
VERSION_DIR="release/offline-resources/$RESOURCE_VERSION"

aws s3 cp "$VERSION_DIR/" "s3://$RESOURCE_BUCKET/$RESOURCE_PREFIX/$RESOURCE_VERSION/" \
  --recursive \
  --exclude 'manifest.json' \
  --content-type application/zip \
  --cache-control 'public,max-age=31536000,immutable'

aws s3 cp "$VERSION_DIR/manifest.json" \
  "s3://$RESOURCE_BUCKET/$RESOURCE_PREFIX/manifest.json" \
  --content-type application/json \
  --cache-control 'no-cache,no-store,must-revalidate'
```

Nếu muốn giữ manifest theo version để rollback/audit, upload thêm bản bất biến:

```bash
aws s3 cp "$VERSION_DIR/manifest.json" \
  "s3://$RESOURCE_BUCKET/$RESOURCE_PREFIX/manifests/$RESOURCE_VERSION.json" \
  --content-type application/json \
  --cache-control 'public,max-age=31536000,immutable'
```

Không ghi đè pack cùng tên hash. Nếu release mới thay đổi file, phải tạo `RESOURCE_VERSION` mới; không sửa object pack đã phát hành.

### Dùng publisher script có kiểm tra trước khi upload

Repository có [`tools/publish_offline_resource_s3.sh`](../tools/publish_offline_resource_s3.sh). Script kiểm tra AWS identity, bucket, signed manifest, toàn bộ SHA-256 pack và từ chối ghi đè version immutable. Nó upload pack trước, manifest versioned tiếp theo và stable `manifest.json` sau cùng. `DISTRIBUTION_ID` là tùy chọn; nếu có, script chỉ invalidation stable manifest.

```bash
chmod +x tools/publish_offline_resource_s3.sh
export AWS_REGION=ap-southeast-1
export RESOURCE_BUCKET=gxb3-offline-resources-prod
export RESOURCE_PREFIX=offline-resources
export RESOURCE_VERSION=web-4ab86d79
export VERSION_DIR=/path/to/offline-resource-release
export CLOUDFRONT_DOMAIN=dxxxxxxxxxxxx.cloudfront.net
export DISTRIBUTION_ID=E1234567890ABC

# Kiểm tra lệnh, chưa upload:
DRY_RUN=1 tools/publish_offline_resource_s3.sh

# Upload thật sau khi xem toàn bộ lệnh dry-run:
tools/publish_offline_resource_s3.sh
```

Script cố ý dừng nếu `s3://$RESOURCE_BUCKET/$RESOURCE_PREFIX/$RESOURCE_VERSION/manifest.json` đã tồn tại. Hãy tạo `RESOURCE_VERSION` mới cho release mới; chỉ dùng `ALLOW_EXISTING_VERSION=1` cho tình huống khôi phục đã được review.

## 9. Kiểm tra CloudFront trước khi build APK

```bash
export MANIFEST_URL="https://$CLOUDFRONT_DOMAIN/$RESOURCE_PREFIX/manifest.json"

curl -fsSI "$MANIFEST_URL"
curl -fsS "$MANIFEST_URL" -o /tmp/manifest.json
```

Kiểm tra các URL trong payload đã trỏ đúng CloudFront:

```bash
python3 - <<'PY'
import base64, json, sys
m = json.load(open('/tmp/manifest.json'))
payload = json.loads(base64.b64decode(m['payload_b64']))
for pack in payload['packs']:
    assert pack['url'].startswith('https://'), pack['url']
    print(pack['url'])
PY
```

Kiểm tra một pack có thể tải và kích thước/hash đúng:

```bash
curl -fL "$PACK_URL" -o /tmp/pack.zip
sha256sum /tmp/pack.zip
unzip -t /tmp/pack.zip
```

Nếu CloudFront trả `403`, kiểm tra lần lượt: OAC đã gắn đúng origin chưa, bucket policy có đúng distribution ARN không, object có nằm dưới prefix được policy cho phép không, và bucket public access block có đang bật không.

## 10. Build Android với manifest URL và public key

Đọc public key:

```bash
export OFFLINE_PUBLIC_KEY_B64="$(cat .secrets/offline-manifest-public-key.b64)"
export OFFLINE_TRUSTED_HOSTS="$CLOUDFRONT_DOMAIN"
```

Build bằng đúng Gradle properties mà `clients/android/app/build.gradle` đang đọc:

```bash
gradle -p clients/android \
  -PgxbOfflineManifestUrl="$MANIFEST_URL" \
  -PgxbOfflineTrustedHosts="$OFFLINE_TRUSTED_HOSTS" \
  -PgxbOfflineManifestPublicKeyB64="$OFFLINE_PUBLIC_KEY_B64" \
  :app:assembleDebug
```

BuildConfig Android sẽ nhận:

```text
OFFLINE_RESOURCE_MANIFEST_URL     = https://<cloudfront>/offline-resources/manifest.json
OFFLINE_RESOURCE_TRUSTED_HOSTS    = <cloudfront-host>
OFFLINE_RESOURCE_PUBLIC_KEY_B64   = <raw-ed25519-public-key-base64>
```

Nếu pack URL dùng nhiều host, liệt kê tất cả host bằng dấu phẩy:

```bash
-PgxbOfflineTrustedHosts="dxxxxxxxxxxxx.cloudfront.net,assets.example.com"
```

Không dùng `*` cho trusted hosts.

## 11. Cache và update policy

- `manifest.json`: `no-cache` để app nhìn thấy version mới.
- Pack content-hash: `max-age=31536000, immutable`.
- Khi phát hành version mới, upload pack mới dưới prefix version mới.
- Không invalidation toàn bộ CloudFront; chỉ invalidation `/offline-resources/manifest.json` nếu cần cập nhật ngay lập tức.
- Android tải pack mới vào staging, xác minh xong mới activate; nếu lỗi phải giữ release active cũ.
- Giữ lại ít nhất một release trước để rollback và áp dụng lifecycle/cleanup sau khi đã xác nhận không còn được tham chiếu.

Invalidate manifest khi cần:

```bash
aws cloudfront create-invalidation \
  --distribution-id "$DISTRIBUTION_ID" \
  --paths "/$RESOURCE_PREFIX/manifest.json"
```

## 12. CI/CD tối thiểu

CI cần có các secret/protected variables sau:

```text
OFFLINE_MANIFEST_SIGNING_KEY_PEM   # private Ed25519 key, chỉ job release đọc
AWS_ROLE_ARN                        # ưu tiên OIDC assume-role, không dùng access key dài hạn
RESOURCE_BUCKET
CLOUDFRONT_DOMAIN
OFFLINE_PUBLIC_KEY_B64              # có thể public nhưng nên quản lý bằng config release
```

Pipeline đề xuất:

1. Checkout với LFS và fail nếu còn pointer.
2. Đọc allowlist đã review.
3. Chạy unit tests của manifest builder.
4. Build deterministic pack + signed manifest.
5. Verify signature/hash bằng một verifier độc lập.
6. Upload pack versioned lên S3.
7. Upload manifest sau cùng.
8. Kiểm tra GET qua CloudFront.
9. Chỉ sau khi smoke test pass mới cập nhật Android build config/release.

Dùng GitHub Actions OIDC hoặc IAM role của CI để tránh lưu `AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY` dài hạn trong repository.

## 13. Phân biệt resource S3 với save S3

Không dùng chung bucket/prefix/quyền giữa hai loại dữ liệu:

| Loại | Bucket | Quyền client | CDN |
|---|---|---|---|
| Resource pack | Bucket riêng, có thể đọc qua CloudFront OAC | Chỉ HTTPS GET resource đã ký manifest | CloudFront |
| Save snapshot | Bucket private riêng | Presigned PUT/GET do backend cấp sau khi xác thực | Không public CDN |

Ứng dụng Android không được chứa AWS access key/secret. Save sync phải đi qua backend xác thực, presigned URL ngắn hạn, checksum, versioning và cơ chế conflict; việc bật bucket S3 resource không làm save sync hoạt động.

## 14. Giới hạn hiện tại của nhánh

Cấu hình thành công S3 + CloudFront sẽ làm được:

- Android tải manifest/pack qua CDN.
- Xác minh chữ ký Ed25519 và SHA-256.
- Lưu resource vào app-private storage.
- Mở lại resource đã cài khi không có mạng.
- Tự chuyển sang local shell khi server online không truy cập được.

Nó **chưa tự biến APK thành game offline đầy đủ**. Nhánh vẫn cần local API, engine chiến đấu và save gameplay Android trước khi có thể tuyên bố người chơi chơi campaign offline hoàn chỉnh.
