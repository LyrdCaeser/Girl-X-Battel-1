"""Zoom image uses natural bedding extension as one canvas (no mirrored legs)."""
from pathlib import Path
from PIL import Image, ImageStat, ImageChops
import unittest

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'web/assets'


class SoniaZoomCanvasTests(unittest.TestCase):
    def test_top_is_approved_character_image_without_distortion(self):
        with Image.open(ASSETS/'chaos/lyr_sonia_zoom_bedding_floor.png') as f:
            tall=f.convert('RGB')
        with Image.open(ASSETS/'characters/758001.png') as f:
            card=f.convert('RGB')
        self.assertEqual(tall.size,(520,1190))
        self.assertEqual(card.size,(520,700))
        self.assertEqual(tall.crop((0,0,520,700)).tobytes(),card.tobytes())

    def test_missing_lower_bedding_taken_from_original_art(self):
        with Image.open(ASSETS/'chaos/lyr_sonia_zoom_bedding_floor.png') as f:
            tall=f.convert('RGB')
        with Image.open(ASSETS/'pictures/758001.webp') as f:
            full=f.convert('RGB')
        true_lower=full.crop((64,1203,880,1536)).resize((520,213),Image.Resampling.LANCZOS)
        self.assertEqual(tall.crop((0,700,520,770)).tobytes(),
                         true_lower.crop((0,0,520,70)).tobytes())
        # No hard horizontal jump in the generated continuation.
        for y in (700,770,850,913,954,1070):
            left=tall.crop((0,y-2,520,y-1))
            right=tall.crop((0,y,520,y+1))
            means=ImageStat.Stat(ImageChops.difference(left,right)).mean
            self.assertLess(max(means),17,(y,means))

    def test_only_mobile_zoom_replaces_art_not_normal_sheet(self):
        css=(ROOT/'web/girl-ui.css').read_text()
        html=(ROOT/'web/index.html').read_text()
        self.assertIn('#girl-detail-view.gs-zoom.sonia-continuation-scene > .detail-scene',css)
        self.assertIn('background-size:100% auto!important;',css)
        self.assertIn('background-position:center top!important;',css)
        self.assertIn('gs-zoom.sonia-continuation-scene .detail-art-wrap{',css)
        self.assertIn('opacity:0!important;',css)
        self.assertIn('/girl-ui.css?v=20261122-all-skill-details-r3',html)


if __name__=='__main__':
    unittest.main()
