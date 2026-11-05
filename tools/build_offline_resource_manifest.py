#!/usr/bin/env python3
"""Build deterministic ZIP packs and a manifest for explicitly allowlisted resources."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import tempfile
import urllib.parse
import zipfile

LFS_PREFIX = b"version https://git-lfs.github.com/spec/v1\n"
ZIP_TIME = (1980, 1, 1, 0, 0, 0)


class BuildError(ValueError):
    """Invalid input or an artifact that cannot be safely built."""


def _validate_path(raw: str) -> str:
    if not isinstance(raw, str) or not raw or "\\" in raw or "\x00" in raw:
        raise BuildError(f"invalid resource path: {raw!r}")
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in ("", ".", "..") for part in raw.split("/")):
        raise BuildError(f"resource path must be normalized and relative: {raw!r}")
    if path.as_posix() != raw:
        raise BuildError(f"resource path must be normalized: {raw!r}")
    return raw


def read_allowlist(filename: Path) -> list[str]:
    text = filename.read_text(encoding="utf-8")
    if filename.suffix.lower() == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise BuildError(f"invalid JSON allowlist: {exc}") from exc
        paths = data.get("files") if isinstance(data, dict) else data
        if not isinstance(paths, list):
            raise BuildError("JSON allowlist must be an array or an object with a 'files' array")
    else:
        paths = [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    validated = [_validate_path(item) for item in paths]
    if len(set(validated)) != len(validated):
        raise BuildError("allowlist contains duplicate paths")
    return sorted(validated)


def _read_source(root: Path, relative: str) -> bytes:
    candidate = root
    for part in relative.split("/"):
        candidate = candidate / part
        if candidate.is_symlink():
            raise BuildError(f"symlinks are not allowed: {relative}")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise BuildError(f"resource missing or outside source root: {relative}") from exc
    if not resolved.is_file():
        raise BuildError(f"resource is not a regular file: {relative}")
    data = resolved.read_bytes()
    if data.startswith(LFS_PREFIX):
        raise BuildError(f"unresolved Git LFS pointer: {relative}")
    return data


def _zip_bytes(files: list[tuple[str, bytes]]) -> bytes:
    import io
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, content in files:
            info = zipfile.ZipInfo(name, ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.flag_bits = 0
            archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return buffer.getvalue()


def build(source_root: Path, allowlist: list[str], output: Path, resource_version: str,
          base_url: str, max_pack_size: int, private_key: Path | None = None) -> dict:
    allowlist = [_validate_path(path) for path in allowlist]
    if len(set(allowlist)) != len(allowlist):
        raise BuildError("allowlist contains duplicate paths")
    if max_pack_size <= 0:
        raise BuildError("max pack size must be a positive number of bytes")
    parsed = urllib.parse.urlsplit(base_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise BuildError("base URL must be an HTTPS URL without query or fragment")
    if not isinstance(resource_version, str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,80}", resource_version):
        raise BuildError("resource version must match [A-Za-z0-9._-]{1,80}")
    resources = [(path, _read_source(source_root, path)) for path in sorted(allowlist)]
    if not resources:
        raise BuildError("allowlist must contain at least one file")

    # Greedily find groups whose actual deterministic ZIP size fits the configured cap.
    groups: list[tuple[list[tuple[str, bytes]], bytes]] = []
    current: list[tuple[str, bytes]] = []
    for item in resources:
        candidate = current + [item]
        packed = _zip_bytes(candidate)
        if len(packed) > max_pack_size:
            if not current:
                raise BuildError(f"resource cannot fit in a pack: {item[0]} ({len(packed)} bytes > {max_pack_size})")
            groups.append((current, _zip_bytes(current)))
            current = [item]
            packed = _zip_bytes(current)
            if len(packed) > max_pack_size:
                raise BuildError(f"resource cannot fit in a pack: {item[0]} ({len(packed)} bytes > {max_pack_size})")
        else:
            current = candidate
    if current:
        groups.append((current, _zip_bytes(current)))

    output = output.absolute()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise BuildError("output directory must be absent or empty; refusing to overwrite existing data")
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output.name}.tmp-", dir=output.parent))
    try:
        packs = []
        for members, blob in groups:
            digest = hashlib.sha256(blob).hexdigest()
            pack_name = f"pack-{digest}.zip"
            (stage / pack_name).write_bytes(blob)
            packs.append({
                "id": digest,
                "url": f"{base_url.rstrip('/')}/{urllib.parse.quote(resource_version, safe='')}/{pack_name}",
                "size_bytes": len(blob),
                "sha256": digest,
                "files": [{"path": path, "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                          for path, data in members],
            })
        manifest = {"manifest_version": 1, "resource_version": resource_version, "packs": packs}
        payload = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if private_key is not None:
            try:
                from cryptography.hazmat.primitives import serialization
                key = serialization.load_pem_private_key(private_key.read_bytes(), password=None)
                if key.__class__.__name__ != "Ed25519PrivateKey":
                    raise BuildError("private key must be an Ed25519 PEM key")
                signature = key.sign(payload)
            except BuildError:
                raise
            except ImportError as exc:
                raise BuildError("signing requires the optional 'cryptography' package") from exc
            except Exception as exc:
                raise BuildError(f"unable to load/sign with Ed25519 private key: {exc}") from exc
            envelope = {"payload_b64": base64.b64encode(payload).decode("ascii"),
                        "signature_b64": base64.b64encode(signature).decode("ascii")}
            (stage / "manifest.json").write_text(json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        else:
            (stage / "manifest.json").write_bytes(payload + b"\n")
            (stage / "UNSIGNED_DEV_ONLY.txt").write_text(
                "UNSIGNED DEVELOPMENT OUTPUT — not suitable for production distribution.\n", encoding="utf-8")
        if output.exists():
            output.rmdir()
        os.replace(stage, output)
        return manifest
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path.cwd())
    parser.add_argument("--allowlist", required=True, type=Path, help=".json array/object or text file, one relative path per line")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--resource-version", required=True)
    parser.add_argument("--base-url", required=True, help="HTTPS base URL")
    parser.add_argument("--max-pack-size", type=int, default=50 * 1024 * 1024, help="maximum ZIP bytes (default: 50 MiB)")
    parser.add_argument("--private-key", type=Path, help="optional Ed25519 PEM private key for signed manifest envelope")
    args = parser.parse_args(argv)
    try:
        manifest = build(args.source_root, read_allowlist(args.allowlist), args.output_dir,
                         args.resource_version, args.base_url, args.max_pack_size, args.private_key)
    except (BuildError, OSError) as exc:
        parser.error(str(exc))
    print(f"Built {len(manifest['packs'])} pack(s) and manifest in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
