"""Each Sonia skill is a recolored copy of one genuine goddess Spine 3.6.37 FX.

Never modify the source girl's clips, rig, animation frames, combat damage,
or the server game state. Check actually copied pixel data, not just filenames.
"""
from pathlib import Path
import json
import unittest
from PIL import Image, ImageChops, ImageStat

ROOT=Path(__file__).resolve().parents[1]
FX=ROOT/'web/assets/battle-fx'
MAPPING={
    'sonia_chaos_orb':'monika_hurt02',
    'sonia_chaos_siphon':'yixienamei_hurt01',
    'sonia_chaos_guard':'lianhua_hurt02',
    'sonia_chaos_collapse':'aboluo_hurt01'
}
SKILLS={
    '75800101':'sonia_chaos_orb',
    '75800102':'sonia_chaos_siphon',
    '75800103':'sonia_chaos_guard',
    '75800104':'sonia_chaos_collapse'
}

class SoniaCopiesTest(unittest.TestCase):
    def test_four_distinct_goddesses_one_skill_each(self):
        self.assertEqual(len(MAPPING),4)
        self.assertEqual(len(set(MAPPING.values())),4)
        src=(ROOT/'web/battle-animation.js').read_text()
        for skill,res in SKILLS.items():
            self.assertIn('case '+skill+':',src)
            self.assertIn("at('"+res+"',",src)
        self.assertIn('75800100:{impact:',src)
        self.assertNotIn('SoniaBattleVFX',src)
        self.assertNotIn("if(!fxLite)at(",src)
        self.assertIn("['lianhua_hurt01','sonia_chaos_orb','sonia_chaos_siphon',",src)
        html=(ROOT/'web/index.html').read_text()
        self.assertIn('/battle-animation.js?v=20261122-sonia-motion-passivefx-r5',html)
        self.assertNotIn('/sonia-battle-vfx.js',html)

    def test_rigs_are_exact_original_spine_3_6_37(self):
        for copied,original in MAPPING.items():
            with self.subTest(copied=copied):
                dst=FX/copied;src=FX/original
                self.assertEqual((dst/'model.json').read_bytes(),(src/'model.json').read_bytes())
                self.assertEqual((dst/'model.atlas').read_bytes(),(src/'model.atlas').read_bytes())
                rig=json.loads((dst/'model.json').read_text())
                self.assertEqual(rig['skeleton']['spine'],'3.6.37')
                self.assertIn('texiao01',rig['animations'])
                if copied=='sonia_chaos_guard':
                    self.assertIn('texiao02',rig['animations'])

                originals=sorted(src.glob('*.webp'))
                self.assertGreater(len(originals),0)
                self.assertEqual([x.name for x in originals],[x.name for x in sorted(dst.glob('*.webp'))])
                for page in originals:
                    self.assertIn(page.name,(dst/'model.atlas').read_text())

    def test_recolored_pages_preserve_alpha_and_are_visibly_different(self):
        for copied,original in MAPPING.items():
            for original_page in (FX/original).glob('*.webp'):
                with self.subTest(original=original_page.name,copied=copied):
                    with Image.open(original_page) as source,Image.open(FX/copied/original_page.name) as target:
                        a=source.convert('RGBA');b=target.convert('RGBA')
                    self.assertEqual(a.size,b.size)
                    self.assertEqual(a.getchannel('A').tobytes(),b.getchannel('A').tobytes())
                    diff=ImageChops.difference(a.convert('RGB'),b.convert('RGB'))
                    mean=sum(ImageStat.Stat(diff).mean)/3
                    self.assertGreater(mean,3)
                    self.assertLess(mean,75)

if __name__=='__main__':
    unittest.main()
