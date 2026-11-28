"""Real 10★ Lyr Sonia awakening requires Sonia art in the empty material slot."""
import unittest
from pathlib import Path

from PIL import Image
from gxb2.engine import TABLES, Engine


class SoniaAwakeRequiredImageTest(unittest.TestCase):
    def test_11_star_recipe_uses_lyr_sonia_copy(self):
        entry=TABLES['partner']['758001']
        self.assertEqual(int(entry['max_star']),10)
        self.assertEqual(int(entry['group']),8)
        self.assertEqual(str(entry['awake_material']).split('|')[0], '758001')
        img=Path(__file__).resolve().parents[1] / 'web/assets/cards/partner_card_758001.png'
        with Image.open(img) as actual:
            self.assertGreater(actual.width, 0)
            self.assertGreater(actual.height, 0)

    def test_frontend_shows_required_card_before_selection(self):
        root=Path(__file__).resolve().parents[1]
        js=(root/'web/girl-ui.js').read_text()
        self.assertIn("const exact=Number(code)>0&&Number(code)%1000!==999;",js)
        self.assertIn("materialSlotPreview(pic,hero,r,'normal',i,g,Number(code));",js)
        self.assertIn("pic.classList.add('lb-preview');",js)
        self.assertIn("c.append(pic,el('small','',(g?1:0)+'/1'))",js)
        # No client-side material auto-selection or server recipe change.
        self.assertIn("c.onclick=()=>chooseMaterial(hero,r,'normal',i,close)",js)
        # The static cards index omits this special girl. The card resolver
        # must not show an unrelated generic partner-avatar instead.
        self.assertIn("cardIds.has(tid)||Number(tid)===758001",js)


if __name__ == '__main__':
    unittest.main()
