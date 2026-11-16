"""Arena attack cards show the original exact-star assets, including 10–25★."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class FormationStars(unittest.TestCase):
    def test_original_star_assets_exist_and_source_preserves_star_values(self):
        for item in ('partner_star_red.png','partner_star_yellow.png',
                     'potentiality_card_star.png','potentiality_card_star_max.png'):
            self.assertTrue((ROOT/'web/assets/girl-ui'/item).is_file(),item)
        source=(ROOT/'web/girl-ui.js').read_text()
        self.assertIn("function stars(n,kind='card')",source)
        self.assertIn("n>10",source)
        self.assertIn("n>=15?'_max'",source)

    def test_attack_slots_and_roster_show_exact_backend_star_count(self):
        source=(ROOT/'web/arena-online-native.js').read_text()
        section=source.split('function nativeCardStars(hero',1)[1].split('function drawDefense(',1)[0]
        self.assertIn("GirlUI.stars(n,'card')",section)
        self.assertNotIn("ar-native-total-stars",section)
        self.assertIn("slot.append(nativeCardStars(hero,'ar-attack-slot-stars'))",section)
        self.assertIn("b.append(nativeCardStars(hero,'ar-attack-candidate-stars'))",section)
        self.assertNotIn("slot.append(el('span','ar-defense-slot-stars',String(hero.stars||0)+'★'))",section)
        self.assertEqual(section.count("nativeCardStars(hero,'ar-attack"),2)
        self.assertIn("const n=Number(hero?.stars)||0",section)

    def test_cards_keep_star_overlay_visible_in_portrait(self):
        css=(ROOT/'web/arena3v3.css').read_text()
        self.assertIn('/* The attack formation reuses original card-star assets',css)
        self.assertIn('.ar-defense-candidate .ar-native-stars',css)
        self.assertIn('position:absolute;left:0;right:0;bottom:0;z-index:8;',css)
        self.assertIn('.gu-star',css)
        self.assertIn('.gu-emblem',css)
        html=(ROOT/'web/index.html').read_text()
        self.assertIn('src="/arena-online-native.js?v=20261116-',html)
        self.assertIn('/arena3v3.css?v=20261116-clean-stars-r5',html)


if __name__=='__main__': unittest.main()
