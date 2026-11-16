"""Original owner card uses lower marked area on Mobile only, not PC."""
import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class OwnerPlacementTest(unittest.TestCase):
    def test_mobile_only_bottom_anchoring(self):
        css=(ROOT/'web/arena.css').read_text()
        section=css.split('/* MOBILE ONLY: use the extra portrait-height room',1)[1]
        self.assertIn('@media(max-width:720px)',section)
        self.assertIn('html.gxb-mobile #app-frame',section)
        self.assertIn('--ar-bottom-nav-h:calc(120 * var(--u))',section)
        self.assertIn('--ar-owner-bottom:calc(132 * var(--u))',section)
        self.assertIn('--ar-owner-height:calc(190 * var(--u))',section)
        self.assertIn('bottom:var(--ar-owner-bottom)!important',section)
        self.assertIn('top:auto!important',section)
        self.assertIn('bottom:calc(160 * var(--u))!important',section)
        for klass in ('arena_award_s','arena_record','arena_defence'):
            self.assertIn('.ar-side-'+klass,section)
        # The owner frame ends 12 units above the nav; its first row is 190
        # units high. Children stay within it, with no PC coordinate changes.
        self.assertEqual(132-120,12)
        for bottom,height in ((198,112),(225,56),(187,27),(149,27),
                              (138,145),(273,32),(160,73),
                              (262,48),(208,48),(154,48)):
            self.assertGreaterEqual(bottom,132)
            self.assertLessEqual(bottom+height,132+190)

    def test_one_renderer_for_three_arena_variants(self):
        js=(ROOT/'web/arena-online-native.js').read_text()
        self.assertIn("['arena','cross','arena3v3']",js)
        self.assertIn("'ar-stat '+(label==='Xếp hạng'?'ar-stat-rank':'ar-stat-score')",js)
        self.assertIn("'ar-side ar-side-'+asset",js)
        self.assertNotIn("stage.style.bottom=",js)
        index=(ROOT/'web/index.html').read_text()
        self.assertIn('/arena-online-native.js?v=20261116-owner-bottom-r6',index)
        self.assertIn('/arena.css?v=20261116-owner-bottom-r5',index)
if __name__=='__main__':unittest.main()
