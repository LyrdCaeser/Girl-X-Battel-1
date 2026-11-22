"""Lyr Sonia presentation assets must originate from the approved full illustration."""
import json
import unittest
from pathlib import Path

from PIL import Image, ImageChops, ImageOps
from gxb2 import chaos_summon, engine

ROOT = Path(__file__).resolve().parents[1]


class SoniaVisualUnificationTests(unittest.TestCase):
    def test_chaos_registration_gives_display_name_without_changing_faction(self):
        t = {'partner': {}, 'names': {}, 'summon': {}}
        chaos_summon.register(t)
        self.assertEqual(t['names']['758001'], 'Lyr Sonia')
        self.assertEqual(t['partner']['758001']['group'], 8)
        self.assertEqual(engine.TABLES['names']['758001'], 'Lyr Sonia')
        self.assertEqual(engine.TABLES['partner']['758001']['group'], 8)

    def test_card_and_character_derive_from_approved_art(self):
        base = Image.open(ROOT / 'web/assets/pictures/758001.webp').convert('RGB')
        self.assertEqual(base.size, (1152, 1536))
        expected = ImageOps.fit(base.crop((64, 105, 880, 1203)), (520, 700),
                                method=Image.Resampling.LANCZOS)
        for path in ('web/assets/cards/partner_card_758001.png',
                     'web/assets/characters/758001.png'):
            actual = Image.open(ROOT / path).convert('RGB')
            self.assertEqual(actual.size, (520, 700))
            self.assertIsNone(ImageChops.difference(expected, actual).getbbox(), path)

    def test_avatar_and_skin_faction_icon(self):
        with Image.open(ROOT / 'web/assets/avatar-hd/portraits/758001.webp') as portrait:
            self.assertEqual(portrait.size, (160, 160))
        icon = Image.open(ROOT / 'web/assets/factions/8.png').convert('RGBA')
        skin = Image.open(ROOT / 'web/assets/skins/ui/img_group8.png').convert('RGBA')
        self.assertEqual(skin.size, (46, 46))
        self.assertIsNone(ImageChops.difference(icon.resize((46, 46),
                            Image.Resampling.LANCZOS), skin).getbbox())
        avatars = json.loads((ROOT / 'web/assets/avatars.json').read_text())
        self.assertEqual(avatars['758001']['group'], 8)
        self.assertIn('v=20261122-sonia-art-r1', avatars['758001']['src'])

    def test_client_uses_name_and_fresh_assets(self):
        app = (ROOT / 'web/app.js').read_text()
        skins = (ROOT / 'web/skins.js').read_text()
        html = (ROOT / 'web/index.html').read_text()
        css = (ROOT / 'web/girl-ui.css').read_text()
        self.assertIn("Number(hero.table_id)===758001?'Lyr Sonia':hero.name", app)
        self.assertIn("Number(imageId)===758001&&!hasSkinCard&&!hasSkinPicture", app)
        self.assertIn("s.base&&Number(hero.table_id)===758001", skins)
        self.assertIn('girl-card[data-group="8"] .girl-faction.faction-8', css)
        # The app/portrait sheet version advances when later Sonia-only
        # visual fixes ship; the skins script remains on the unified release.
        for file, version in (
            ('app.js', '20261122-sonia-poison-real-r9'),
            ('skins.js', '20261122-sonia-cosmos-outfit-r2'),
            ('girl-ui.css', '20261122-sonia-mobile-fullbleed-r2'),
        ):
            self.assertIn('/' + file + '?v=' + version, html)


if __name__ == '__main__':
    unittest.main()
