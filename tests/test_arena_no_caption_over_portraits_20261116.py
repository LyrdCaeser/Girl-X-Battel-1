"""Prevent duplicate star labels and top-of-portrait captions in Arena."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class ArenaPortraits(unittest.TestCase):
    def test_attack_list_has_only_original_images_and_original_star_badges(self):
        js=(ROOT/'web/arena-online-native.js').read_text()
        attack=js.split('function drawAttack(win,button){',1)[1].split('function drawDefense(win,button){',1)[0]
        self.assertIn("b.append(nativeCardStars(hero,'ar-attack-candidate-stars'))",attack)
        self.assertIn("slot.append(nativeCardStars(hero,'ar-attack-slot-stars'))",attack)
        self.assertNotIn("const meta=el('span','ar-defense-meta')",attack)
        self.assertNotIn("b.append(meta)",attack)
        # Name and level remain available through the HTML button tooltip.
        self.assertIn("b.title=(hero.name||'Nữ Thần')",attack)

    def test_no_extra_total_star_text_on_picture(self):
        js=(ROOT/'web/arena-online-native.js').read_text()
        native=js.split("function nativeCardStars(hero,extraClass=''){",1)[1].split("function drawAttack(",1)[0]
        self.assertIn("GirlUI.stars(n,'card')",native)
        self.assertNotIn('ar-native-total-stars',native)
        css=(ROOT/'web/arena3v3.css').read_text()
        self.assertNotIn('.ar-native-total-stars{',css)
        self.assertNotIn('>.ar-defense-meta{',css)
        self.assertIn('.ar-defense-candidate .ar-native-stars',css)

if __name__=='__main__':unittest.main()
