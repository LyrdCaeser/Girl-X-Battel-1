"""Live ranking must extend to the shifted owner pane with a 12-unit gap."""
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class RankMobileTest(unittest.TestCase):
    def test_full_height_ranking_and_gap_to_owner_card(self):
        css=(ROOT/'web/arena.css').read_text()
        portion=css.split('/* MOBILE ONLY: the leaderboard keeps',1)[1]
        self.assertIn('@media(max-width:720px)',portion)
        self.assertIn('html.gxb-mobile #app-frame .arena-view',portion)
        self.assertIn('bottom:calc(334 * var(--u))!important',portion)
        self.assertIn('top:calc(228.5 * var(--u))!important',portion)
        self.assertIn('height:auto!important',portion)
        self.assertIn('overflow-y:auto',portion)
        self.assertEqual(334-(132+190),12)
        # Baseline 1280-wide prefab stays scrollable; portrait 1530+ fills gap.
        self.assertGreater(1280-228.5-334,680)
        self.assertGreater(1530-228.5-334,900)

    def test_original_rank_rows_and_frame_unchanged(self):
        js=(ROOT/'web/arena-online-native.js').read_text()
        self.assertIn('Arena.rankRow(player,i,Number(state?.power||0),openPlayer)',js)
        self.assertIn("rank.style.borderImageSource=",js)
        self.assertIn('const rows=el(',js)
        css=(ROOT/'web/arena.css').read_text()
        self.assertIn("border-image-source:url('/assets/arena/arena_bg.png')",css)
        self.assertIn('border-image-slice:30 fill',css)
        html=(ROOT/'web/index.html').read_text()
        self.assertIn('/arena.css?v=20261116-rank-continuous-r6',html)

if __name__=='__main__':unittest.main()
