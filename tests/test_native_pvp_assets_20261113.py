"""Release asset gate: native sprites must exist; LFS pointers are not images."""
import tempfile
import unittest
from pathlib import Path
from tools.verify_native_pvp_assets import ROOT, inspect_image, verify, PNG


class NativePvPAssetTests(unittest.TestCase):
    def test_repository_manifest_has_original_assets_or_valid_lfs_metadata(self):
        stats=verify(ROOT)
        self.assertGreaterEqual(sum(stats.values()),30)

    def test_release_strict_rejects_pointer_and_invalid_binary(self):
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/'asset.png'
            file.write_text('version https://git-lfs.github.com/spec/v1\n'
                            'oid sha256:'+('a'*64)+'\nsize 12345\n')
            self.assertEqual(inspect_image(file,strict=False),'lfs')
            with self.assertRaisesRegex(ValueError,'Git LFS'):
                inspect_image(file,strict=True)
            file.write_bytes(PNG+b'bad')
            with self.assertRaisesRegex(ValueError,'header'):
                inspect_image(file,strict=True)


if __name__=='__main__':
    unittest.main()
