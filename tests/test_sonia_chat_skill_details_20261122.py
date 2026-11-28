"""No-Neon verification of Sonia's original Station and all-goddess skill catalog."""
import json
import unittest
from pathlib import Path
from gxb2 import relations

ROOT = Path(__file__).resolve().parents[1]

class SoniaStationAndSkillTests(unittest.TestCase):
    def test_station_is_real_and_original_catalog_unchanged(self):
        base = json.loads((ROOT/'web/assets/station/station.json').read_text())
        self.assertEqual(len(base['girls']), 143)
        sonia = relations.STATION['girls']['858001']
        self.assertEqual(sonia['ids'], [758001])
        self.assertEqual(sonia['name'], 'Lyr Sonia')
        self.assertEqual(len(sonia['skills']), 4)
        self.assertEqual(len(relations.STATION['girls']), 144)
        self.assertEqual(sonia['lineups'], [None,None,None])
        self.assertFalse(any(sonia['points']))
        self.assertTrue(all(s['desc'] for s in sonia['skills']))
        self.assertEqual(sonia['skills'][0]['id'], 75800101)

    def test_sonia_discuss_state_and_messages(self):
        state={'partners':[{'partner_id':'sonia-qa','table_id':758001}], 'station':{}}
        def req(action,**kwargs):
            return relations.station_action(state,{'action':action,'id':'858001',**kwargs})
        self.assertEqual(req('station')['likes'], 0)
        msg='Sonia, ta muốn cùng nàng khám phá các vì sao!'
        self.assertEqual(req('station_comment',text=msg)['station']['comments'][0]['text'],msg)
        self.assertEqual(req('station')['hot'], [])
        self.assertEqual(req('station_like')['likes'], 1)
        self.assertEqual(req('station')['station']['comments'][0]['text'],msg)
        self.assertEqual(req('station_delete',index=0)['station']['comments'], [])

    def test_all_original_goddesses_have_clickable_text_entries(self):
        details=json.loads((ROOT/'web/assets/girl-details.json').read_text())
        descriptions=json.loads((ROOT/'web/assets/skills/skill-descriptions.json').read_text())['skills']
        total=0
        for goddess in details.values():
            for skill in goddess.get('skills',[]):
                total+=1
                self.assertIn(str(skill['id']),descriptions)
        self.assertEqual(len(details), 647)
        self.assertGreater(total,2000)
        self.assertGreater(len(descriptions),1750)
        self.assertIn('Nymphaea',descriptions['75301901']['text'])
        self.assertEqual(descriptions['75301901']['lang'],'vi')
        self.assertIn('180%',descriptions['4100101']['text'])

    def test_sonia_original_icon_and_three_level_descriptions(self):
        chaos=json.loads((ROOT/'web/assets/chaos/lyr_sonia.json').read_text())
        self.assertEqual(len(chaos['skills']),4)
        for skill in chaos['skills']:
            self.assertEqual(len(skill['levels']),3)
            self.assertTrue(all(len(x)>30 for x in skill['levels']))
            self.assertTrue((ROOT/'web/assets/skills'/f'skill_icon_{skill["id"]}.png').is_file())

if __name__=='__main__':unittest.main()
