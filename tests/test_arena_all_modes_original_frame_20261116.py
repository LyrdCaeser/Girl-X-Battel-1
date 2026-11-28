import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class AllArenasFrameTest(unittest.TestCase):
    def test_shared_original_frame_on_ranking_and_owner_card(self):
        css=(ROOT/'web/arena.css').read_text()
        self.assertIn('.arena-view .ar-rank,\n.arena-view .ar-detail{',css)
        self.assertIn("border-image-source:url('/assets/arena/arena_bg.png')",css)
        self.assertIn('border-image-slice:30 fill',css)
        self.assertTrue((ROOT/'web/assets/arena/arena_bg.png').is_file())
    def test_shared_renderer_covers_all_three_modes(self):
        js=(ROOT/'web/arena-online-native.js').read_text()
        self.assertIn("['arena','cross','arena3v3']",js)
        self.assertIn("stage.append(center(el('div','ar-detail')",js)
        self.assertIn("const rank=center(el('div','ar-rank')",js)
        self.assertIn("mode==='cross'?",js)
        html=(ROOT/'web/index.html').read_text()
        self.assertIn('rel="stylesheet" href="/arena.css?v=20261116-',html)
if __name__=='__main__':unittest.main()
