#!/usr/bin/env python3
"""Build deterministic, bounded ZIP packs and a manifest for allowlisted resources."""
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
import subprocess
import tempfile
import urllib.parse
import zipfile

LFS_PREFIX = b"version https://git-lfs.github.com/spec/v1\n"
ZIP_TIME = (1980, 1, 1, 0, 0, 0)
CHUNK_SIZE = 1024 * 1024
MAX_MANIFEST_BYTES = 8 * 1024 * 1024
MAX_PACKS = 512
MAX_FILES = 100_000
MAX_PACK_BYTES = 256 * 1024 * 1024
MAX_FILE_BYTES = 512 * 1024 * 1024
MAX_TOTAL_FILE_BYTES = 8 * 1024 * 1024 * 1024


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


def read_allowlist(filename: Path, repository_root: Path | None = None) -> list[str]:
    """Read explicit file paths or expand explicit roots using Git's tracked-file index."""
    try:
        text = filename.read_text(encoding="utf-8")
    except OSError as exc:
        raise BuildError(f"cannot read allowlist {filename}: {exc}") from exc
    if filename.suffix.lower() == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise BuildError(f"invalid JSON allowlist: {exc}") from exc
        if isinstance(data, dict) and "files" in data:
            paths = data["files"]
        elif isinstance(data, dict) and "tracked_roots" in data:
            roots = data["tracked_roots"]
            if not isinstance(roots, list) or not roots:
                raise BuildError("tracked_roots must be a non-empty array")
            roots = [_validate_path(root).rstrip("/") for root in roots]
            root = (repository_root or filename.resolve().parent.parent).resolve()
            try:
                result = subprocess.run(
                    ["git", "-C", str(root), "ls-files", "-z"],
                    check=True, capture_output=True,
                )
            except (OSError, subprocess.CalledProcessError) as exc:
                raise BuildError(f"cannot enumerate Git-tracked resource files: {exc}") from exc
            tracked = result.stdout.decode("utf-8", errors="strict").split("\0")
            paths = sorted(
                path for path in tracked if path
                and any(path.startswith(f"{tracked_root}/") for tracked_root in roots)
            )
            if not paths:
                raise BuildError("tracked_roots matched no Git-tracked files")
        else:
            paths = data if isinstance(data, list) else None
        if not isinstance(paths, list):
            raise BuildError("JSON allowlist must contain 'files' or non-empty 'tracked_roots'")
    else:
        paths = [line.strip() for line in text.splitlines()
                 if line.strip() and not line.lstrip().startswith("#")]
    validated = [_validate_path(item) for item in paths]
    if len(set(validated)) != len(validated):
        raise BuildError("allowlist contains duplicate paths")
    return sorted(validated)


def _resolve_source(root: Path, relative: str) -> Path:
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
    return resolved


def _hash_source(path: Path, relative: str) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        first = source.read(len(LFS_PREFIX))
        if first.startswith(LFS_PREFIX):
            raise BuildError(f"unresolved Git LFS pointer: {relative}")
        digest.update(first)
        size += len(first)
        while True:
            chunk = source.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    return size, digest.hexdigest()


def _zip_group(members: list[dict], archive_path: Path) -> tuple[int, str]:
    """Stream source files into a deterministic archive and return archive size/hash."""
    with archive_path.open("wb") as target:
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9, allowZip64=True) as archive:
            for member in members:
                info = zipfile.ZipInfo(member["path"], ZIP_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                digest = hashlib.sha256()
                size = 0
                with member["source"].open("rb") as source, archive.open(info, "w") as entry:
                    first = source.read(len(LFS_PREFIX))
                    if first.startswith(LFS_PREFIX):
                        raise BuildError(f"unresolved Git LFS pointer: {member['path']}")
                    if first:
                        digest.update(first)
                        size += len(first)
                        entry.write(first)
                    while True:
                        chunk = source.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        digest.update(chunk)
                        size += len(chunk)
                        entry.write(chunk)
                if size != member["size_bytes"] or digest.hexdigest() != member["sha256"]:
                    raise BuildError(f"resource changed while packaging: {member['path']}")
    digest = hashlib.sha256()
    size = 0
    with archive_path.open("rb") as archive:
        while True:
            chunk = archive.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    return size, digest.hexdigest()


def build(source_root: Path, allowlist: list[str], output: Path, resource_version: str,
          base_url: str, max_pack_size: int, private_key: Path | None = None) -> dict:
    allowlist = [_validate_path(path) for path in allowlist]
    if len(set(allowlist)) != len(allowlist):
        raise BuildError("allowlist contains duplicate paths")
    if len(allowlist) > MAX_FILES:
        raise BuildError(f"file count exceeds Android limit ({MAX_FILES})")
    if max_pack_size <= 0 or max_pack_size > MAX_PACK_BYTES:
        raise BuildError(f"max pack size must be between 1 and {MAX_PACK_BYTES} bytes")
    parsed = urllib.parse.urlsplit(base_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise BuildError("base URL must be an HTTPS URL without query or fragment")
    if not isinstance(resource_version, str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,80}", resource_version):
        raise BuildError("resource version must match [A-Za-z0-9._-]{1,80}")

    root = source_root.resolve(strict=True)
    resources = []
    total_source_bytes = 0
    for relative in sorted(allowlist):
        source = _resolve_source(root, relative)
        size, digest = _hash_source(source, relative)
        if size > MAX_FILE_BYTES:
            raise BuildError(f"resource exceeds Android per-file limit ({MAX_FILE_BYTES}): {relative}")
        total_source_bytes += size
        if total_source_bytes > MAX_TOTAL_FILE_BYTES:
            raise BuildError(f"resource set exceeds Android total size limit ({MAX_TOTAL_FILE_BYTES} bytes)")
        resources.append({"path": relative, "source": source,
                          "size_bytes": size, "sha256": digest})
    if not resources:
        raise BuildError("allowlist must contain at least one file")

    output = output.absolute()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise BuildError("output directory must be absent or empty; refusing to overwrite existing data")
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output.name}.tmp-", dir=output.parent))
    try:
        packs = []
        temporary_counter = 0

        def emit_group(members: list[dict]) -> None:
            nonlocal temporary_counter
            temporary_counter += 1
            temporary = stage / f".pack-{temporary_counter:05d}.tmp"
            packed_size, digest = _zip_group(members, temporary)
            if packed_size > max_pack_size:
                temporary.unlink(missing_ok=True)
                if len(members) == 1:
                    raise BuildError(
                        f"resource cannot fit in a pack: {members[0]['path']} "
                        f"({packed_size} bytes > {max_pack_size})"
                    )
                middle = len(members) // 2
                emit_group(members[:middle])
                emit_group(members[middle:])
                return
            pack_name = f"pack-{digest}.zip"
            os.replace(temporary, stage / pack_name)
            packs.append({
                "id": digest,
                "url": f"{base_url.rstrip('/')}/{urllib.parse.quote(resource_version, safe='')}/{pack_name}",
                "size_bytes": packed_size,
                "sha256": digest,
                "files": [{"path": member["path"], "size_bytes": member["size_bytes"],
                           "sha256": member["sha256"]} for member in members],
            })

        current: list[dict] = []
        current_uncompressed = 0
        for member in resources:
            if current and current_uncompressed + member["size_bytes"] > max_pack_size:
                emit_group(current)
                current = []
                current_uncompressed = 0
            current.append(member)
            current_uncompressed += member["size_bytes"]
            if member["size_bytes"] > max_pack_size:
                emit_group(current)
                current = []
                current_uncompressed = 0
        if current:
            emit_group(current)
        if len(packs) > MAX_PACKS:
            raise BuildError(f"pack count exceeds Android limit ({MAX_PACKS})")

        manifest = {"manifest_version": 1, "resource_version": resource_version, "packs": packs}
        payload = json.dumps(manifest, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8")
        if private_key is not None:
            try:
                from cryptography.hazmat.primitives import serialization
                from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
                key = serialization.load_pem_private_key(private_key.read_bytes(), password=None)
                if not isinstance(key, Ed25519PrivateKey):
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
            envelope_bytes = (json.dumps(envelope, ensure_ascii=False, sort_keys=True,
                                         separators=(",", ":")) + "\n").encode("utf-8")
            if len(envelope_bytes) > MAX_MANIFEST_BYTES:
                raise BuildError(f"signed manifest exceeds Android limit ({MAX_MANIFEST_BYTES} bytes)")
            (stage / "manifest.json").write_bytes(envelope_bytes)
        else:
            manifest_bytes = payload + b"\n"
            if len(manifest_bytes) > MAX_MANIFEST_BYTES:
                raise BuildError(f"manifest exceeds Android limit ({MAX_MANIFEST_BYTES} bytes)")
            (stage / "manifest.json").write_bytes(manifest_bytes)
            (stage / "UNSIGNED_DEV_ONLY.txt").write_text(
                "UNSIGNED DEVELOPMENT OUTPUT — not suitable for production distribution.\n",
                encoding="utf-8")

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
    parser.add_argument("--allowlist", required=True, type=Path,
                        help="JSON files/tracked_roots or text file of relative paths")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--resource-version", required=True)
    parser.add_argument("--base-url", required=True, help="HTTPS base URL")
    parser.add_argument("--max-pack-size", type=int, default=50 * 1024 * 1024,
                        help="maximum ZIP bytes (default: 50 MiB)")
    parser.add_argument("--private-key", type=Path,
                        help="optional Ed25519 PEM private key for signed manifest envelope")
    args = parser.parse_args(argv)
    try:
        allowlist = read_allowlist(args.allowlist, args.source_root)
        manifest = build(args.source_root, allowlist, args.output_dir,
                         args.resource_version, args.base_url, args.max_pack_size, args.private_key)
    except (BuildError, OSError) as exc:
        parser.error(str(exc))
    file_count = sum(len(pack["files"]) for pack in manifest["packs"])
    total_bytes = sum(file["size_bytes"] for pack in manifest["packs"] for file in pack["files"])
    print(f"Built {len(manifest['packs'])} pack(s), {file_count} file(s), "
          f"{total_bytes} source bytes and manifest in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
