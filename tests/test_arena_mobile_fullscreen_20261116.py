"""The original Arena backdrop fills portrait screens; PC styles stay unchanged."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class MobileArena(unittest.TestCase):
    def test_mobile_stage_extends_beyond_1280_fixed_units(self):
        css=(ROOT/'web/arena.css').read_text()
        marker='@media(max-width:720px){'
        self.assertIn(marker,css)
        scoped=css.split('/* Mobile portrait 20:9+:',1)[1].split('/* Original ArenaWindow frame',1)[0]
        for statement in (
            'html.gxb-mobile #app-frame .arena-view',
            'height:100%;min-height:100%;overflow:hidden;',
            'height:100%;min-height:calc(1280 * var(--u));',
            'left:0!important;top:0!important;width:100%!important;height:100%!important;',
            'object-fit:cover;object-position:center center;',
            'bottom:0!important;'
        ):
            self.assertIn(statement,scoped)
        self.assertEqual(scoped.count(marker),1)

    def test_original_background_and_versioned_styles(self):
        arena=(ROOT/'web/arena-online-native.js').read_text()
        self.assertIn("A(mode==='arena3v3'?'arena_3v3_scene':'arena_scene')",arena)
        html=(ROOT/'web/index.html').read_text()
        self.assertIn('href="/arena.css?v=20261116-',html)

if __name__=='__main__':unittest.main()
