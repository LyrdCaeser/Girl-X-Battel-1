#!/usr/bin/env python3
"""Fail-closed checks for the Android offline release signing boundary."""
import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path


def required(value: str, name: str) -> str:
    if not value:
        raise SystemExit(f"missing required value: {name}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keystore", required=True)
    parser.add_argument("--store-password", required=True)
    parser.add_argument("--alias", required=True)
    parser.add_argument("--public-key-b64", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--apk", required=True)
    parser.add_argument("--apksigner", required=True)
    args = parser.parse_args()

    keystore = Path(args.keystore)
    manifest = Path(args.manifest)
    apk = Path(args.apk)
    for path, label in ((keystore, "keystore"), (manifest, "signed manifest"), (apk, "APK")):
        if not path.is_file() or path.stat().st_size == 0:
            raise SystemExit(f"{label} is missing or empty: {path}")

    try:
        public_key = base64.b64decode(args.public_key_b64, validate=True)
    except Exception as exc:
        raise SystemExit(f"public key is not valid base64: {exc}")
    if len(public_key) != 32:
        raise SystemExit(f"Ed25519 public key must be 32 bytes, got {len(public_key)}")

    keytool = subprocess.run(
        ["keytool", "-list", "-v", "-keystore", str(keystore), "-storepass", args.store_password],
        text=True, capture_output=True, check=False,
    )
    if keytool.returncode != 0:
        raise SystemExit("keystore cannot be opened with the supplied password")
    if "Entry type: PrivateKeyEntry" not in keytool.stdout:
        raise SystemExit("keystore does not contain a private signing key")
    if f"Alias name: {args.alias}" not in keytool.stdout:
        raise SystemExit(f"keystore alias not found: {args.alias}")

    envelope = json.loads(manifest.read_text(encoding="utf-8"))
    if set(envelope) != {"payload_b64", "signature_b64"}:
        raise SystemExit("manifest must be a signed envelope, not an unsigned payload")
    payload = base64.b64decode(envelope["payload_b64"], validate=True)
    signature = base64.b64decode(envelope["signature_b64"], validate=True)
    if len(signature) != 64:
        raise SystemExit("manifest signature must be 64 bytes")
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        Ed25519PublicKey.from_public_bytes(public_key).verify(signature, payload)
    except Exception as exc:
        raise SystemExit(f"manifest signature verification failed: {exc}")
    signed_payload = json.loads(payload.decode("utf-8"))
    for field in ("manifest_version", "resource_version", "packs"):
        if field not in signed_payload:
            raise SystemExit(f"signed manifest missing field: {field}")

    signer = subprocess.run(
        [args.apksigner, "verify", "--verbose", "--print-certs", str(apk)],
        text=True, capture_output=True, check=False,
    )
    output = signer.stdout + signer.stderr
    if signer.returncode != 0:
        raise SystemExit("apksigner rejected the release APK")
    if "Android Debug" in output or "CN=Android Debug" in output:
        raise SystemExit("release APK is signed with the Android debug certificate")
    print("Android release gate passed: private keystore, non-debug APK signer, pinned public key, and signed manifest verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
