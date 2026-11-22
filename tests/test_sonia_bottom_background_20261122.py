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
        self.assertIn('html.gxb-mobile #app-frame #girl-detail-view.gs-zoom.sonia-continuation-scene > .detail-scene', css)
        self.assertIn("background-image:url('/assets/chaos/lyr_sonia_zoom_bedding_floor.png')!important;", css)
        self.assertIn('background-size:100% auto!important;', css)
        self.assertIn('background-position:center top!important;', css)
        self.assertIn('.gs-zoom.sonia-continuation-scene .detail-art-wrap', css)
        self.assertIn("classList.toggle('sonia-continuation-scene',Number(hero.table_id)===758001&&Number(imageId)===758001)", app)
        self.assertNotIn("classList.toggle('sonia-continuation-scene',Number(hero.table_id)===758001&&src==", app)
        # A missing group-8 college background must not revert to flat blue.
        self.assertFalse((ROOT/'web/assets/scenes/college_scene8.png').exists())
        self.assertIn('background-color:#dec6df!important;', css)
        self.assertIn('/girl-ui.css?v=20261122-sonia-elite-r4', html)
        self.assertIn('/app.js?v=20261122-sonia-elite-vfx-r11', html)


if __name__ == '__main__':
    unittest.main()
