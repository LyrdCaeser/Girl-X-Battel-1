"""Sonia keeps Chaos faction while using authentic purple Cosmos star sprites."""
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'web/assets'


class SoniaCosmosStarTests(unittest.TestCase):
    def test_winged_nametag_preserves_original_wings(self):
        purple_count = 0
        for source, generated, width in (
            ('potentiality_nametag_star.png', 'lyr_sonia_tag_cosmos.png', 135),
            ('potentiality_nametag_star_max.png', 'lyr_sonia_tag_cosmos_max.png', 169),
        ):
            with Image.open(ASSETS/'girl-ui'/source) as original, Image.open(ASSETS/'chaos'/generated) as output:
                before=original.convert('RGBA'); after=output.convert('RGBA')
            self.assertEqual(before.size,(width,51))
            self.assertEqual(after.size,before.size)
            left=(width-43)//2
            self.assertEqual(before.crop((0,0,left,51)).tobytes(),
                             after.crop((0,0,left,51)).tobytes())
            self.assertEqual(before.crop((left+43,0,width,51)).tobytes(),
                             after.crop((left+43,0,width,51)).tobytes())
            self.assertNotEqual(before.tobytes(),after.tobytes())
            purples=sum(
                1 for r,g,b,a in after.crop((left,3,left+43,46)).get_flattened_data()
                if a>200 and b>g*1.4 and r>g*1.2)
            self.assertGreater(purples,190)
            purple_count+=purples
        self.assertGreater(purple_count,500)

    def test_character_only_styling_and_correct_versions(self):
        app=(ROOT/'web/app.js').read_text()
        skins=(ROOT/'web/skins.js').read_text()
        css=(ROOT/'web/skins.css').read_text()
        html=(ROOT/'web/index.html').read_text()
        self.assertIn('Number(hero.table_id)===758001&&Number(hero.stars)>=10',app)
        self.assertIn("lyr_sonia_tag_cosmos'+(Number(hero.stars)>=15?'_max':'')",app)
        self.assertIn('s.base&&Number(hero.table_id)===758001&&Number(hero.stars)>=10',skins)
        self.assertIn("star_orange_group_7",skins)
        self.assertIn("potentiality_card_star_group_7",skins)
        self.assertIn("badge.append(mark);c.append(badge)",skins)
        self.assertIn('.sk-name.sk-cosmos-star',css)
        self.assertIn('/app.js?v=20261122-sonia-scene-fallback-r4',html)
        self.assertIn('/skins.js?v=20261122-sonia-cosmos-outfit-r2',html)
        self.assertIn('/skins.css?v=20261122-sonia-cosmos-outfit-r2',html)


if __name__=='__main__':
    unittest.main()
