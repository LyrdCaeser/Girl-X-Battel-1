"""Verify gameplay is identical and every challenge story is Vietnamese."""
import json,re,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class HeroChallengeVi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads(subprocess.check_output(
            ['git','show','HEAD:data/hero_challenge.json'],cwd=ROOT))
        cls.new=json.loads((ROOT/'data/hero_challenge.json').read_text())

    def test_gameplay_unchanged(self):
        for k in self.old:
            if k in ('stage_text','buff_text','text'):continue
            self.assertEqual(self.old[k],self.new[k],k)
        self.assertEqual(set(self.old['stage_text']),set(self.new['stage_text']))
        for k,r in self.old['stage_text'].items():
            for field in r:
                if field not in ('fort','name','desc'):
                    self.assertEqual(r[field],self.new['stage_text'][k][field])
        self.assertEqual(set(self.old['buff_text']),set(self.new['buff_text']))
        self.assertEqual(set(self.old['text']),set(self.new['text']))

    def test_all_stage_names_descriptions_and_original_goddess_names(self):
        heroes={'Phoenix','Linky','Iron Fist','Hottie','KongMing','Aquaris',
                'Hexa','Valeera','Turin','Esau & Jacob','Ithil','Krystal'}
        found=set()
        for key,r in self.new['stage_text'].items():
            self.assertRegex(r['desc'],r'[À-ỹ]',key)
            self.assertTrue(r['name'].strip(),key)
            original_hero=self.old['stage_text'][key]['fort'].split('·')[0].strip()
            # Older localizations may have translated some names already.
            local={'Phượng Hoàng':'Phoenix','Thiết Quyền':'Iron Fist',
                   'Khổng Minh':'KongMing','Mỹ Nhân':'Hottie'}
            original_hero=local.get(original_hero,original_hero)
            self.assertEqual(r['fort'].split(' · ')[0],original_hero,key)
            found.add(original_hero)
        self.assertEqual(found,heroes)

    def test_all_buff_and_help_descriptions_vietnamese(self):
        for k,r in self.new['buff_text'].items():
            self.assertRegex(r['name'],r'[À-ỹ]',k)
            self.assertRegex(r['desc'],r'[À-ỹ]',k)
        for k,s in self.new['text'].items():
            self.assertRegex(s,r'[À-ỹ]',k)
        js=(ROOT/'web/hero-challenge.js').read_text()
        self.assertIn("cls:'hc-help-modal'",js)
        self.assertNotIn("'Please choose your reward'",js)
        self.assertNotIn('({1:"Girl"',js)

if __name__=='__main__':unittest.main()
