import json
import re
import unittest
from gxb2 import dress

class OutfitVietnamese(unittest.TestCase):
    def test_all_outfit_effects_have_translation(self):
        catalog=dress.catalog()
        self.assertEqual(len(catalog['skill_text']),348)
        self.assertEqual(set(catalog['skill_text']),set(dress.DATA['skill_text']))
        for id,text in catalog['skill_text'].items():
            with self.subTest(id=id):
                self.assertTrue(text.strip())
                self.assertNotRegex(text,r'^(Has |Receive |Obtain |Increase |Adds |Campaign Loot|Courage |Crystal )')

    def test_46_outfit_set_names_localized(self):
        catalog=dress.catalog()
        self.assertEqual(len(dress.VI['group_names']),46)
        for id,text in dress.VI['group_names'].items():
            self.assertEqual(catalog['groups'][id]['name'],text)
        self.assertEqual(catalog['slots']['4']['name'],'Mũ')
        self.assertEqual(catalog['slots']['5']['name'],'Phụ Kiện')

    def test_223_shard_names_and_four_currency_names(self):
        names=dress.catalog()['shard_names']
        self.assertGreaterEqual(sum(v!=dress.DATA['shard_names'][k] for k,v in names.items()),223)
        self.assertEqual(names['32001'],'Tula') # Goddess name is immutable.
        self.assertEqual(dress.catalog()['item_names']['258'],'Nút Thường')

    def test_source_counts_and_numerics_unchanged(self):
        source=dress.DATA['skill_text'];vi=dress.VI['skill_text']
        self.assertEqual(set(vi),set(source))
        # Common percent values must carry through in each localized effect.
        for id,text in source.items():
            src_pct=re.findall(r'\d+(?:\.\d+)?%',text)
            dest_pct=re.findall(r'\d+(?:\.\d+)?%',vi[id])
            self.assertEqual(src_pct,dest_pct, 'numeric percent mismatch for '+id)

if __name__=='__main__':unittest.main()
