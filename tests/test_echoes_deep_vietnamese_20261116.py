"""Verify complete text catalogue and unchanged Echoes engine mechanics."""
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class EchoesCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads(subprocess.check_output(['git','show','HEAD:data/echoes.json'],cwd=ROOT))
        cls.new=json.loads((ROOT/'data/echoes.json').read_text())

    def test_gameplay_rules_unchanged(self):
        old,new=self.old,self.new
        self.assertEqual(set(old),set(new))
        for key in old:
            if key in ('text','tec_text','ach_text','card_text','world_text'):
                continue
            self.assertEqual(old[key],new[key],key)
        self.assertEqual(set(old['card_text']),set(new['card_text']))

    def test_all_card_descriptions_vietnamese_and_goddess_names_untouched(self):
        for key,card in self.new['card_text'].items():
            self.assertRegex(card['desc'],r'[À-ỹ]',key)
            original=self.old['card_text'][key]['name']
            prefix=original.split(' · ')[0]
            if prefix in ('Luna','Blowie','Angel','Fenrir','Raphael','Teresa','Bud Elf',
                          'Vera','Caitlyn','Boxer','Nobunaga','Diana','Sakura','Hottie',
                          'Robbie','Yuri','Skye','Hermes','Blair','Librarian','Mika'):
                self.assertEqual(card['name'],original,key)

    def test_every_achievement_technology_and_help_translated(self):
        for key,s in self.new['ach_text'].items():
            self.assertRegex(s,r'[À-ỹ]',key)
        for key,r in self.new['tec_text'].items():
            self.assertRegex(r['name'],r'[À-ỹ]',key)
            self.assertRegex(r['desc'],r'[À-ỹ]',key)
            if r['unlock']:
                self.assertRegex(r['unlock'],r'[À-ỹ]',key)
        for key,s in self.new['text'].items():
            if s not in ('Xanh Lam','Cam'):
                self.assertRegex(s,r'[À-ỹ]',key)
        for key,s in self.new['world_text'].items():
            self.assertRegex(s['name'],r'[À-ỹ]',key)
            self.assertRegex(s['desc'],r'[À-ỹ]',key)


if __name__=='__main__':unittest.main()
