#!/usr/bin/env bash
# Publish a signed offline resource release: immutable packs first, manifest last.
# Required: AWS_REGION RESOURCE_BUCKET RESOURCE_PREFIX RESOURCE_VERSION VERSION_DIR
# Optional: DISTRIBUTION_ID CLOUDFRONT_DOMAIN ONLINE_ASSET_DIR ONLINE_ASSET_PREFIX DRY_RUN=1 ALLOW_EXISTING_VERSION=1
set -euo pipefail

: "${AWS_REGION:?Set AWS_REGION, for example ap-southeast-1}"
: "${RESOURCE_BUCKET:?Set RESOURCE_BUCKET}"
: "${RESOURCE_PREFIX:?Set RESOURCE_PREFIX, for example offline-resources}"
: "${RESOURCE_VERSION:?Set RESOURCE_VERSION, for example web-<full-commit-sha>}"
: "${VERSION_DIR:?Set VERSION_DIR to the built release directory}"

command -v aws >/dev/null || { echo "aws CLI is required" >&2; exit 1; }
command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 1; }
[[ -d "$VERSION_DIR" ]] || { echo "VERSION_DIR does not exist: $VERSION_DIR" >&2; exit 1; }
[[ -s "$VERSION_DIR/manifest.json" ]] || { echo "manifest.json is missing or empty" >&2; exit 1; }
if [[ -n "${ONLINE_ASSET_DIR:-}" ]]; then
  [[ -d "$ONLINE_ASSET_DIR" ]] || { echo "ONLINE_ASSET_DIR does not exist: $ONLINE_ASSET_DIR" >&2; exit 1; }
  : "${ONLINE_ASSET_PREFIX:=online-assets}"
fi

export AWS_PAGER=""
aws sts get-caller-identity >/dev/null
aws s3api head-bucket --bucket "$RESOURCE_BUCKET" >/dev/null

VERSION_KEY="$RESOURCE_PREFIX/$RESOURCE_VERSION"
MANIFEST_KEY="$RESOURCE_PREFIX/manifest.json"
VERSION_MANIFEST_KEY="$VERSION_KEY/manifest.json"
ONLINE_VERSION_KEY="${ONLINE_ASSET_PREFIX:-online-assets}/$RESOURCE_VERSION"

# Validate the signed envelope, release version, pack names/hashes, and CloudFront URLs before upload.
EXPECTED_RESOURCE_VERSION="$RESOURCE_VERSION" RESOURCE_PREFIX="$RESOURCE_PREFIX" \
python3 - "$VERSION_DIR" "${CLOUDFRONT_DOMAIN:-}" <<'PY'
import base64
import hashlib
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

root = Path(sys.argv[1]).resolve()
cloudfront = sys.argv[2].strip()
expected_version = os.environ["EXPECTED_RESOURCE_VERSION"]
resource_prefix = os.environ["RESOURCE_PREFIX"].strip("/")
envelope = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
if set(envelope) != {"payload_b64", "signature_b64"}:
    raise SystemExit("manifest must be a signed envelope: payload_b64 + signature_b64")
try:
    payload = base64.b64decode(envelope["payload_b64"], validate=True)
    signature = base64.b64decode(envelope["signature_b64"], validate=True)
except Exception as exc:
    raise SystemExit(f"invalid manifest base64: {exc}")
if len(signature) != 64:
    raise SystemExit("manifest signature must be 64 bytes")
manifest = json.loads(payload.decode("utf-8"))
if manifest.get("resource_version") != expected_version:
    raise SystemExit(
        f"manifest resource_version mismatch: {manifest.get('resource_version')!r} != {expected_version!r}"
    )
packs = manifest.get("packs")
if not isinstance(packs, list) or not packs:
    raise SystemExit("manifest contains no packs")
seen = set()
for pack in packs:
    parsed = urlsplit(pack["url"])
    name = Path(parsed.path).name
    if not name.startswith("pack-") or not name.endswith(".zip"):
        raise SystemExit(f"invalid pack URL/name: {name}")
    expected = pack["sha256"]
    if name != f"pack-{expected}.zip":
        raise SystemExit(f"pack filename does not match manifest hash: {name}")
    expected_path = f"/{resource_prefix}/{expected_version}/{name}"
    if parsed.scheme != "https" or parsed.path != expected_path or parsed.query or parsed.fragment:
        raise SystemExit(f"pack URL does not match release prefix/version: {pack['url']}")
    if cloudfront and parsed.netloc.lower() != cloudfront.lower():
        raise SystemExit(f"pack URL is not on CLOUDFRONT_DOMAIN: {pack['url']}")
    if name in seen:
        raise SystemExit(f"duplicate pack: {name}")
    seen.add(name)
    path = root / name
    if not path.is_file():
        raise SystemExit(f"pack missing from VERSION_DIR: {path}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected:
        raise SystemExit(f"pack hash mismatch: {name}: {digest} != {expected}")
print(f"Validated signed envelope, {len(packs)} pack(s), and SHA-256 hashes")
PY

run() {
  if [[ "${DRY_RUN:-0}" == "1" ]]; then
    printf '+ '
    printf '%q ' "$@"
    printf '\n'
  else
    "$@"
  fi
}

# A versioned release must never be overwritten after publication.
if [[ "${ALLOW_EXISTING_VERSION:-0}" != "1" ]] && aws s3api head-object --bucket "$RESOURCE_BUCKET" --key "$VERSION_MANIFEST_KEY" >/dev/null 2>&1; then
  echo "Refusing to overwrite existing immutable release: s3://$RESOURCE_BUCKET/$VERSION_MANIFEST_KEY" >&2
  echo "Use a new RESOURCE_VERSION. ALLOW_EXISTING_VERSION=1 is reserved for recovery." >&2
  exit 1
fi
if [[ -n "${ONLINE_ASSET_DIR:-}" ]] && [[ "${ALLOW_EXISTING_VERSION:-0}" != "1" ]] && aws s3api head-object --bucket "$RESOURCE_BUCKET" --key "$ONLINE_VERSION_KEY/RESOURCE_VERSION" >/dev/null 2>&1; then
  echo "Refusing to overwrite existing immutable Online asset release: s3://$RESOURCE_BUCKET/$ONLINE_VERSION_KEY/" >&2
  exit 1
fi

shopt -s nullglob
packs=("$VERSION_DIR"/pack-*.zip)
((${#packs[@]} > 0)) || { echo "No pack-*.zip files found" >&2; exit 1; }

echo "Uploading ${#packs[@]} immutable pack(s) to s3://$RESOURCE_BUCKET/$VERSION_KEY/"
for pack in "${packs[@]}"; do
  run aws s3 cp "$pack" "s3://$RESOURCE_BUCKET/$VERSION_KEY/$(basename "$pack")" \
    --region "$AWS_REGION" \
    --content-type application/zip \
    --cache-control 'public,max-age=31536000,immutable' \
    --only-show-errors
 done

if [[ -n "${ONLINE_ASSET_DIR:-}" ]]; then
  echo "Uploading Online asset tree to s3://$RESOURCE_BUCKET/$ONLINE_VERSION_KEY/"
  run aws s3 sync "$ONLINE_ASSET_DIR/" "s3://$RESOURCE_BUCKET/$ONLINE_VERSION_KEY/" \
    --region "$AWS_REGION" \
    --cache-control 'public,max-age=31536000,immutable' \
    --exclude 'RESOURCE_VERSION' \
    --only-show-errors
  run aws s3 cp "$ONLINE_ASSET_DIR/RESOURCE_VERSION" "s3://$RESOURCE_BUCKET/$ONLINE_VERSION_KEY/RESOURCE_VERSION" \
    --region "$AWS_REGION" \
    --content-type text/plain \
    --cache-control 'public,max-age=31536000,immutable' \
    --only-show-errors
fi

# Versioned manifest supports rollback/audit; stable manifest is uploaded last so clients
# cannot observe a new pointer before all immutable packs exist.
echo "Uploading versioned manifest"
run aws s3 cp "$VERSION_DIR/manifest.json" "s3://$RESOURCE_BUCKET/$VERSION_MANIFEST_KEY" \
  --region "$AWS_REGION" \
  --content-type application/json \
  --cache-control 'public,max-age=31536000,immutable' \
  --only-show-errors

echo "Publishing stable manifest last"
run aws s3 cp "$VERSION_DIR/manifest.json" "s3://$RESOURCE_BUCKET/$MANIFEST_KEY" \
  --region "$AWS_REGION" \
  --content-type application/json \
  --cache-control 'no-cache,no-store,must-revalidate' \
  --only-show-errors

if [[ -n "${DISTRIBUTION_ID:-}" ]]; then
  echo "Invalidating CloudFront manifest only"
  run aws cloudfront create-invalidation \
    --distribution-id "$DISTRIBUTION_ID" \
    --paths "/$MANIFEST_KEY" \
    --region "$AWS_REGION" \
    --no-cli-pager
fi

echo "Published: s3://$RESOURCE_BUCKET/$MANIFEST_KEY"
if [[ -n "${CLOUDFRONT_DOMAIN:-}" ]]; then
  echo "Manifest URL: https://$CLOUDFRONT_DOMAIN/$MANIFEST_KEY"
  if [[ -n "${ONLINE_ASSET_DIR:-}" ]]; then
    echo "Online asset base URL: https://$CLOUDFRONT_DOMAIN/$ONLINE_VERSION_KEY/"
  fi
fi
