"""Mobile Sonia artwork should extend vertically without scaling the character."""
import unittest
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]


class SoniaBottomBackgroundTests(unittest.TestCase):
    def test_approved_detail_art_matches_extension_at_seam(self):
        with Image.open(ROOT / 'web/assets/characters/758001.png') as original:
            source = original.convert('RGB')
        with Image.open(ROOT / 'web/assets/chaos/lyr_sonia_bottom_extend.png') as extension:
            continuation = extension.convert('RGB')
        self.assertEqual(source.size, (520, 700))
        self.assertEqual(continuation.size, (520, 850))
        seam = source.crop((0, 699, 520, 700))
        follow = continuation.crop((0, 0, 520, 1))
        # WebP compression may introduce a few RGB units at the joint.
        average = ImageStat.Stat(ImageChops.difference(seam, follow)).mean
        self.assertLess(max(average), 14, average)

    def test_mobile_only_and_sonia_only(self):
        css = (ROOT / 'web/girl-ui.css').read_text()
        app = (ROOT / 'web/app.js').read_text()
        html = (ROOT / 'web/index.html').read_text()
        self.assertIn('html.gxb-mobile #app-frame #girl-detail-view > .detail-scene > .sonia-bottom-fill', css)
        self.assertIn('top:134.615cqw;', css)
        self.assertIn('height:calc(100% - 134.615cqw);', css)
        self.assertIn("sheetScene.querySelector('.sonia-bottom-fill')", app)
        self.assertIn("Number(hero.table_id)===758001&&Number(imageId)===758001", app)
        self.assertIn("extension.src='/assets/chaos/lyr_sonia_bottom_extend.png'", app)
        self.assertIn('else extension?.remove();', app)
        self.assertIn('/girl-ui.css?v=20261122-sonia-bottom-dom-r2', html)
        self.assertIn('/app.js?v=20261122-sonia-purple-nametag-r3', html)


if __name__ == '__main__':
    unittest.main()
