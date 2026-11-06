#!/usr/bin/env bash
# Publish a signed offline resource release: immutable packs first, manifest last.
# Required: AWS_REGION RESOURCE_BUCKET RESOURCE_PREFIX RESOURCE_VERSION VERSION_DIR
# Optional: DISTRIBUTION_ID CLOUDFRONT_DOMAIN DRY_RUN=1 ALLOW_EXISTING_VERSION=1
set -euo pipefail

: "${AWS_REGION:?Set AWS_REGION, for example ap-southeast-1}"
: "${RESOURCE_BUCKET:?Set RESOURCE_BUCKET}"
: "${RESOURCE_PREFIX:?Set RESOURCE_PREFIX, for example offline-resources}"
: "${RESOURCE_VERSION:?Set RESOURCE_VERSION, for example web-4ab86d79}"
: "${VERSION_DIR:?Set VERSION_DIR to the built release directory}"

command -v aws >/dev/null || { echo "aws CLI is required" >&2; exit 1; }
command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 1; }
[[ -d "$VERSION_DIR" ]] || { echo "VERSION_DIR does not exist: $VERSION_DIR" >&2; exit 1; }
[[ -s "$VERSION_DIR/manifest.json" ]] || { echo "manifest.json is missing or empty" >&2; exit 1; }

export AWS_PAGER=""
aws sts get-caller-identity >/dev/null
aws s3api head-bucket --bucket "$RESOURCE_BUCKET" >/dev/null

VERSION_KEY="$RESOURCE_PREFIX/$RESOURCE_VERSION"
MANIFEST_KEY="$RESOURCE_PREFIX/manifest.json"
VERSION_MANIFEST_KEY="$VERSION_KEY/manifest.json"

# Validate the signed envelope, pack names, pack hashes, and CloudFront URLs before upload.
python3 - "$VERSION_DIR" "${CLOUDFRONT_DOMAIN:-}" <<'PY'
import base64
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
cloudfront = sys.argv[2].strip()
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
if manifest.get("resource_version") != root.name and root.name != "":
    # VERSION_DIR can be an arbitrary local name, so this is informational only.
    pass
packs = manifest.get("packs")
if not isinstance(packs, list) or not packs:
    raise SystemExit("manifest contains no packs")
seen = set()
for pack in packs:
    name = Path(pack["url"].split("/")[-1]).name
    if not name.startswith("pack-") or not name.endswith(".zip"):
        raise SystemExit(f"invalid pack URL/name: {name}")
    expected = pack["sha256"]
    if name != f"pack-{expected}.zip":
        raise SystemExit(f"pack filename does not match manifest hash: {name}")
    if name in seen:
        raise SystemExit(f"duplicate pack: {name}")
    seen.add(name)
    path = root / name
    if not path.is_file():
        raise SystemExit(f"pack missing from VERSION_DIR: {path}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected:
        raise SystemExit(f"pack hash mismatch: {name}: {digest} != {expected}")
    if cloudfront and not pack["url"].startswith("https://" + cloudfront + "/"):
        raise SystemExit(f"pack URL is not on CLOUDFRONT_DOMAIN: {pack['url']}")
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
fi
