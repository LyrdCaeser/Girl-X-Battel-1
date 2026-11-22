"""Mobile Sonia artwork should extend vertically without scaling the character."""
import unittest
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]


class SoniaBottomBackgroundTests(unittest.TestCase):
    def test_approved_detail_art_matches_extension_at_seam(self):
        with Image.open(ROOT / 'web/assets/characters/758001.png') as original:
            source = original.convert('RGB')
        with Image.open(ROOT / 'web/assets/chaos/lyr_sonia_bottom_extend.webp') as extension:
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
        self.assertIn('html.gxb-mobile #app-frame #girl-detail-view.sonia-background-extend>.detail-scene::before', css)
        self.assertIn('top:calc(100cqw * 700 / 520 - 1px);', css)
        self.assertIn('background:url(\'/assets/chaos/lyr_sonia_bottom_extend.webp\')', css)
        self.assertIn("classList.toggle('sonia-background-extend',Number(imageId)===758001&&src==='/assets/characters/758001.png')", app)
        self.assertIn('/girl-ui.css?v=20261122-sonia-bottom-fill-r1', html)
        self.assertIn('/app.js?v=20261122-sonia-bottom-fill-r1', html)


if __name__ == '__main__':
    unittest.main()
