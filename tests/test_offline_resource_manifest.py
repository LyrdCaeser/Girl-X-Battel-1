import base64
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.build_offline_resource_manifest import BuildError, build, read_allowlist


class OfflineResourceManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "images").mkdir()
        (self.source / "images/a.bin").write_bytes(b"image-data" * 20)
        (self.source / "config.json").write_text('{"ok":true}', encoding="utf-8")

    def output(self, label):
        return self.root / label

    def test_deterministic_packs_and_manifest(self):
        allow = ["config.json", "images/a.bin"]
        first = build(self.source, allow, self.output("one"), "r7", "https://cdn.example/assets", 10000)
        second = build(self.source, allow, self.output("two"), "r7", "https://cdn.example/assets", 10000)
        self.assertEqual(first, second)
        self.assertEqual((self.output("one") / "manifest.json").read_bytes(),
                         (self.output("two") / "manifest.json").read_bytes())
        pack = first["packs"][0]
        archive_path = self.output("one") / f"pack-{pack['sha256']}.zip"
        blob = archive_path.read_bytes()
        self.assertEqual(hashlib.sha256(blob).hexdigest(), pack["sha256"])
        self.assertEqual(pack["size_bytes"], len(blob))
        self.assertEqual(pack["url"], f"https://cdn.example/assets/r7/pack-{pack['sha256']}.zip")
        self.assertEqual(first["manifest_version"], 1)
        self.assertEqual(first["resource_version"], "r7")
        with zipfile.ZipFile(archive_path) as archive:
            self.assertEqual(archive.namelist(), ["config.json", "images/a.bin"])
            for entry in pack["files"]:
                content = archive.read(entry["path"])
                self.assertEqual(entry["size_bytes"], len(content))
                self.assertEqual(entry["sha256"], hashlib.sha256(content).hexdigest())
                self.assertEqual(archive.getinfo(entry["path"]).date_time, (1980, 1, 1, 0, 0, 0))
        self.assertTrue((self.output("one") / "UNSIGNED_DEV_ONLY.txt").exists())

    def test_text_and_json_allowlists(self):
        text = self.root / "allow.txt"
        text.write_text("# assets\nimages/a.bin\nconfig.json\n", encoding="utf-8")
        self.assertEqual(read_allowlist(text), ["config.json", "images/a.bin"])
        jsonfile = self.root / "allow.json"
        jsonfile.write_text('{"files":["images/a.bin"]}', encoding="utf-8")
        self.assertEqual(read_allowlist(jsonfile), ["images/a.bin"])

    def test_traversal_rejected(self):
        for path in ("../secret", "/absolute", "images/../config.json", "a\\b"):
            with self.subTest(path=path), self.assertRaises(BuildError):
                build(self.source, [path], self.output("bad"), "r1", "https://cdn.example", 10000)

    def test_rejects_unsafe_resource_versions_and_base_urls(self):
        for version in ("../r1", "has space", "x" * 81, ""):
            with self.subTest(version=version), self.assertRaises(BuildError):
                build(self.source, ["config.json"], self.output("bad"), version, "https://cdn.example", 10000)
        for base_url in ("http://cdn.example", "https://user@cdn.example", "https:///missing-host", "https://cdn.example/?token=x"):
            with self.subTest(base_url=base_url), self.assertRaises(BuildError):
                build(self.source, ["config.json"], self.output("bad"), "r1", base_url, 10000)
        self.assertFalse(self.output("bad").exists())

    def test_symlink_rejected(self):
        outside = self.root / "outside"
        outside.write_text("secret", encoding="utf-8")
        (self.source / "linked").symlink_to(outside)
        with self.assertRaisesRegex(BuildError, "symlinks"):
            build(self.source, ["linked"], self.output("bad"), "r1", "https://cdn.example", 10000)

    def test_unresolved_lfs_pointer_rejected(self):
        (self.source / "pointer").write_bytes(
            b"version https://git-lfs.github.com/spec/v1\noid sha256:" + b"a" * 64 + b"\nsize 999\n")
        with self.assertRaisesRegex(BuildError, "LFS"):
            build(self.source, ["pointer"], self.output("bad"), "r1", "https://cdn.example", 10000)

    def test_pack_limit_and_no_partial_output(self):
        with self.assertRaises(BuildError):
            build(self.source, ["images/a.bin"], self.output("bad"), "r1", "https://cdn.example", 10)
        self.assertFalse(self.output("bad").exists())

    def test_signed_envelope_if_cryptography_available(self):
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
            from cryptography.hazmat.primitives import serialization
        except ImportError:
            self.skipTest("optional cryptography package unavailable")
        key = Ed25519PrivateKey.generate()
        key_path = self.root / "key.pem"
        key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM,
                                               serialization.PrivateFormat.PKCS8,
                                               serialization.NoEncryption()))
        result = build(self.source, ["config.json"], self.output("signed"), "r2",
                       "https://cdn.example", 10000, key_path)
        envelope = json.loads((self.output("signed") / "manifest.json").read_text("utf-8"))
        payload = base64.b64decode(envelope["payload_b64"])
        signature = base64.b64decode(envelope["signature_b64"])
        self.assertEqual(payload, json.dumps(result, ensure_ascii=False, sort_keys=True,
                                            separators=(",", ":")).encode("utf-8"))
        key.public_key().verify(signature, payload)
        self.assertFalse((self.output("signed") / "UNSIGNED_DEV_ONLY.txt").exists())


if __name__ == "__main__":
    unittest.main()
