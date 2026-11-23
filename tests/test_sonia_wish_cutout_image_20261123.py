"""The Sonia Wish-only image has real alpha; other Sonia art is unchanged."""
from pathlib import Path
import unittest
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
CUTOUT=ROOT/'web/assets/chaos/lyr_sonia_wish_cutout.webp'
SOURCE=ROOT/'web/assets/pictures/758001.webp'

class SoniaWishCutout(unittest.TestCase):
    def test_transparent_character_art_on_exact_original_canvas(self):
        with Image.open(SOURCE) as src:
            original=src.copy()
        with Image.open(CUTOUT) as cut:
            wish=cut.copy()
        self.assertEqual(original.size,(1152,1536))
        self.assertEqual(original.mode,'RGB','Original art is not replaced')
        self.assertEqual(wish.mode,'RGBA')
        self.assertEqual(wish.size,original.size)
        alpha=wish.getchannel('A')
        hist=alpha.histogram()
        self.assertGreater(sum(hist[:6]),350_000,'Background must not remain as a rectangle')
        self.assertGreater(sum(hist[250:]),350_000,'Skin, face and dress must remain opaque')
        self.assertEqual(alpha.getpixel((0,0)),0)
        self.assertEqual(alpha.getpixel((1151,0)),0)
        self.assertEqual(alpha.getpixel((490,390)),255)
        self.assertEqual(alpha.getpixel((650,550)),255)
        self.assertEqual(alpha.getpixel((720,1000)),255)
    def test_approved_cosmos_icons_exist_unchanged(self):
        for name in ('lyr_sonia_tag_cosmos.png','lyr_sonia_tag_cosmos_max.png'):
            p=CUTOUT.parent/name
            im=Image.open(p)
            self.assertEqual(im.mode,'RGBA')
            self.assertIsNotNone(im.getchannel('A').getbbox())

if __name__=='__main__':
    unittest.main()
