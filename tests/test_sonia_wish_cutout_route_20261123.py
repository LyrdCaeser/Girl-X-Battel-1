"""Only the dedicated Sonia Wish cutout may be added to the Chaos asset route."""
import unittest
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

class SoniaWishCutoutRouteTests(unittest.TestCase):
    def test_exact_webp_whitelist_and_transparent_asset(self):
        code=(ROOT/'server.py').read_text()
        self.assertIn("if candidate.name == 'lyr_sonia_wish_cutout.webp':",code)
        self.assertIn("mime = 'image/webp'",code)
        self.assertIn("candidate.is_relative_to(folder.resolve()) and candidate.is_file()",code)
        with Image.open(ROOT/'web/assets/chaos/lyr_sonia_wish_cutout.webp') as im:
            self.assertEqual(im.size,(1152,1536))
            self.assertEqual(im.mode,'RGBA')
            self.assertEqual(im.getpixel((0,0))[3],0)
            self.assertEqual(im.getpixel((490,390))[3],255)

if __name__=='__main__':unittest.main()
