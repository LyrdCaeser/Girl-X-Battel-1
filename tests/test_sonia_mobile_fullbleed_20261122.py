"""Reproduce/fix Sonia portrait's 75%-width, 279-unit top gap on Mobile."""
import json
import math
import re
import unittest
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
RULE=r'''html\.gxb-mobile #app-frame #girl-detail-view\.sonia-continuation-scene:not\(\.gs-zoom\) #detail-art\.gu-native\[src\$="/758001\.webp"\]\{([^}]+)\}'''

class SoniaMobileFullBleedTest(unittest.TestCase):
    def setUp(self):
        self.css=(ROOT/'web/girl-ui.css').read_text()
        self.html=(ROOT/'web/index.html').read_text()
        self.pic=json.loads((ROOT/'data/partner_pictures.json').read_text())['758001']
        with Image.open(ROOT/'web/assets/pictures/758001.webp') as image:
            self.original_size=image.size

    def test_exact_native_art_aspect_uses_960x1280_sheet(self):
        self.assertEqual(self.original_size,(1152,1536))
        # Portrait fills 1280 design units from y=0; crop only 120
        # units at each lateral edge of a 720-unit original sheet.
        source_width,source_height=self.original_size
        rendered_width=960
        rendered_height=rendered_width*source_height/source_width
        self.assertAlmostEqual(rendered_height,1280)
        self.assertAlmostEqual(640-rendered_height/2,0)
        self.assertGreaterEqual(rendered_width,720)
        self.assertAlmostEqual((rendered_width-720)/2,120)

    def test_css_uses_mobile_only_and_never_rescales_pc_or_zoom(self):
        match=re.search(RULE,self.css)
        self.assertIsNotNone(match,'missing Sonia-only mobile non-zoom rule')
        body=match.group(1)
        for token in ('width:calc(960 * var(--u))!important',
                      'height:auto!important','max-width:none!important',
                      'left:calc(360 * var(--u))!important',
                      'top:calc(640 * var(--u))!important',
                      'transform:translate(-50%,-50%)!important'):
            self.assertIn(token,body)
        self.assertIn('#girl-detail-view.gs-zoom.sonia-continuation-scene > .detail-scene{',self.css)
        self.assertIn('lyr_sonia_zoom_bedding_floor.png',self.css)
        self.assertEqual(self.pic['scale'],.47,'leave original Wish metadata unchanged')
        self.assertEqual(self.pic['summon_static_scale'],.47)
        self.assertIn('/girl-ui.css?v=20261122-sonia-mobile-fullbleed-r2',self.html)
        self.assertIn('/girl-ui.js?v=20261122-awake-material-image-r1',self.html)

    def test_original_mobile_failure_reproduced_before_override(self):
        source_width,source_height=self.original_size
        displayed_width=source_width*self.pic['scale']
        displayed_height=source_height*self.pic['scale']
        self.assertGreater((720-displayed_width)/2,85)
        self.assertGreater(640-displayed_height/2,270)

if __name__=='__main__':
    unittest.main()
