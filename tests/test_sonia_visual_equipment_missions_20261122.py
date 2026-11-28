"""Regression coverage for Sonia's native art, equipping, shards and 30-day challenges."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from gxb2 import chaos_summon, equipment, sonia_festival as festival

ROOT=Path(__file__).resolve().parents[1]


class SoniaVisualAndGameplayTests(unittest.TestCase):
    def test_native_sonia_portrait_for_animated_wish(self):
        pictures=json.loads((ROOT/'data/pictures.json').read_text())
        positions=json.loads((ROOT/'data/partner_pictures.json').read_text())
        self.assertIn(758001,pictures)
        self.assertIn('758001',positions)
        self.assertGreater(positions['758001']['summon_static_scale'],0.2)
        self.assertLess(positions['758001']['summon_static_scale'],0.8)
        self.assertTrue((ROOT/'web/assets/pictures/758001.webp').is_file())
        frontend=(ROOT/'web/summon-anim.js').read_text()
        self.assertIn('pics.add(758001)',frontend)
        self.assertIn("summon_static_scale:0.47",frontend)

    def test_sonia_job_in_equipment_catalog(self):
        self.assertEqual(equipment.job_of({'table_id':758001}),2)
        self.assertEqual(equipment.PARTNERS['758001']['name'],'Lyr Sonia')

    def test_equips_sonia_with_compatible_gear_and_removes_it(self):
        eligible=next((int(key) for key,row in equipment.EQUIP.items()
                      if int(row.get('job') or 0)==2 and int(row.get('pos') or 0)==1),None)
        self.assertIsNotNone(eligible)
        state={'items':{str(eligible):1},'partners':[{
            'partner_id':91,'table_id':758001,'lv':1,'grade':0,'awake':5,'equips':[0]*7
        }]}
        equipment.action(state,{'action':'equip','partner_id':91,'item_id':eligible})
        self.assertEqual(state['partners'][0]['equips'][0],eligible)
        self.assertEqual(int(state['items'].get(str(eligible),0)),0)
        equipment.action(state,{'action':'unequip','partner_id':91,'slot':1})
        self.assertEqual(state['partners'][0]['equips'][0],0)
        self.assertEqual(state['items'][str(eligible)],1)
        equipment.action(state,{'action':'equip_all','partner_id':91})
        self.assertEqual(state['partners'][0]['equips'][0],eligible)

    def test_awaken_rewards_are_shards_not_full_goddesses(self):
        for star,row in festival.STAR_REWARDS.items():
            self.assertNotIn('758001',row)
            self.assertNotIn(festival.TICKET,row)
        self.assertEqual(festival.STAR_REWARDS[25][festival.SHARD],25)
        self.assertNotIn('10',festival.STAR_REWARDS[25])
        fragment=json.loads((ROOT/'data/debris.json').read_text())['940061']
        self.assertEqual(fragment['partner_cost'],'758001#100')
        self.assertEqual(fragment['type'],3)

    def test_free_ticket_cap_and_checkin20_not_arena100(self):
        self.assertEqual(sum(task[5] for task in festival.TASKS),120)
        names={task[0] for task in festival.TASKS}
        self.assertIn('checkin20',names)
        self.assertNotIn('arena100',names)
        self.assertEqual(next(x for x in festival.TASKS if x[0]=='checkin20')[3],20)
        self.assertEqual(next(x for x in festival.TASKS if x[0]=='checkin20')[5],20)

    def test_daily_checkins_count_distinct_days_only(self):
        state={'items':{festival.TICKET:0},'partners':[]}
        first=festival.START+3600
        for day in range(20):
            at=first+day*86400
            festival.record_daily_checkin(state,at)
            festival.record_daily_checkin(state,at)
        self.assertEqual(state['sonia_festival']['progress']['daily_checkin'],20)
        self.assertEqual(len(state['sonia_festival']['checked_days']),20)
        awarded=festival.action(state,{'action':'sonia_mission_claim','id':'checkin20'},now=first+20*86400)
        self.assertEqual(awarded['awards'][festival.TICKET],20)
        with self.assertRaises(ValueError):
            festival.action(state,{'action':'sonia_mission_claim','id':'checkin20'},now=first+20*86400)
        self.assertEqual(state['items'][festival.TICKET],20)

    def test_event_ui_uses_distinct_ticket_shard_and_lunch_icons(self):
        script=(ROOT/'web/events.js').read_text()
        for name in ('Mảnh Sonia','Vé Sonia','Hộp cơm'):
            self.assertIn(name,script)
        self.assertIn('/assets/item-icons/icon_10.png',script)
        self.assertIn('sf-reward-name',script)
        for fn in ('icon_10.png','partner_avatar_758001.png'):
            self.assertTrue((ROOT/'web/assets/item-icons'/fn).is_file())


if __name__=='__main__':
    unittest.main()
