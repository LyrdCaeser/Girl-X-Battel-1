"""Diploma low-tier is earned alongside original 10★ Diploma sources.
Existing point-event array indices and original wish claims remain intact.
Uses only temporary, in-memory states; never connects to player/Neon data.
"""
import copy
import json
import unittest
from pathlib import Path

from gxb2 import point_events, wish

ROOT = Path(__file__).resolve().parents[1]
OLD_DIPLOMA = '47'
NEW_DIPLOMA = '47001'


class SharedDiplomaSourceTests(unittest.TestCase):

    def test_wish_old_rows_remain_unchanged_with_new_independent_rows(self):
        originals = [(5, 300), (11, 800), (17, 1300), (23, 1800)]
        for i, (old_id, old_threshold) in enumerate(originals, start=26):
            old = wish.D['rows'][str(old_id)]
            new = wish.D['rows'][str(i)]
            self.assertEqual(old['awards'], '47#5|209#20')
            self.assertEqual(old['limit'], old_threshold)
            self.assertEqual(new['awards'], '47001#5')
            self.assertEqual(new['limit'], int(old_threshold * 0.85))
            self.assertEqual(new['type'], 0)
            self.assertLess(new['limit'], old_threshold)
        self.assertEqual(len(wish.D['rows']), 29)

    def test_wish_old_claim_does_not_claim_new_reward(self):
        state = {'items': {}, 'wish': {
            'select':0,'times':0,'total':300, 'claimed':{'5':1},'free_at':0
        }}
        s=wish.snapshot(state, now=0)
        self.assertNotIn(5,s['can_claim'])
        self.assertIn(26,s['can_claim'])
        got=wish.action(state,{'action':'claim','id':26})['got']
        self.assertEqual(got,{NEW_DIPLOMA:5})
        self.assertEqual(state['items'].get(OLD_DIPLOMA,0),0)
        self.assertEqual(state['wish']['claimed']['5'],1)
        self.assertEqual(state['wish']['claimed']['26'],1)
        with self.assertRaises(wish.WishError):
            wish.action(state,{'action':'claim','id':26})

    def test_wish_new_award_first_then_old_award_later(self):
        state={'items':{},'wish':{
            'select':0,'times':0,'total':255,'claimed':{},'free_at':0
        }}
        self.assertIn(26,wish.snapshot(state,0)['can_claim'])
        self.assertNotIn(5,wish.snapshot(state,0)['can_claim'])
        wish.action(state,{'action':'claim','id':26})
        self.assertEqual(state['items'][NEW_DIPLOMA],5)
        state['wish']['total']=300
        wish.action(state,{'action':'claim','id':5})
        self.assertEqual(state['items'][NEW_DIPLOMA],5)
        self.assertEqual(state['items'][OLD_DIPLOMA],5)

    def test_point_event_existing_rows_and_indices_are_unchanged(self):
        tiers=point_events.CONFIG['13']['table']
        self.assertEqual(len(tiers),7)
        self.assertEqual(tiers[3],{'point':300,'awards':'47#5|20#5|329#20|358#10'})
        self.assertEqual(tiers[-1],{'point':255,'awards':'47001#5'})

    def test_capsule_points_255_awards_low_before_300_high(self):
        state={'items':{}}
        now=1780000000
        point_events.add(state,'advanced',26,now=now) # 26*10 = 260
        self.assertEqual(state['items'][NEW_DIPLOMA],5)
        self.assertEqual(state['items'].get(OLD_DIPLOMA,0),0)
        point_events.add(state,'advanced',4,now=now) # 300
        self.assertEqual(state['items'][NEW_DIPLOMA],5)
        self.assertEqual(state['items'][OLD_DIPLOMA],5)

    def test_existing_point_claim_index_three_preserved(self):
        now=1780000000
        period=point_events.clock.week(now)
        state={'items':{},'point_events':{'13':{
            'period':period,'point':300,'rounds':0,
            'got':[0,1,2,3],
        }}}
        before=copy.deepcopy(state)
        shown=point_events.snapshot(state,now)['13']
        self.assertEqual(state,before)
        points=[row['point'] for row in shown['tiers']]
        self.assertEqual(points,[50,100,200,255,300,400,500])
        got_by_threshold={r['point']:r['got'] for r in shown['tiers']}
        self.assertTrue(got_by_threshold[300])
        self.assertFalse(got_by_threshold[255])
        point_events.add(state,'advanced',1,now=now)
        self.assertEqual(state['items'][NEW_DIPLOMA],5)
        self.assertEqual(state['items'].get(OLD_DIPLOMA,0),0)
        self.assertIn(3,state['point_events']['13']['got'])
        self.assertIn(6,state['point_events']['13']['got'])

    def test_other_point_sources_unchanged(self):
        for aid in ('16','20'):
            self.assertFalse(any('47001#' in row['awards'] for row in point_events.CONFIG[aid]['table']))

    def test_existing_diploma_rebirth_item_catalog_unchanged(self):
        import subprocess
        old = json.loads(subprocess.check_output(['git','show','HEAD:web/assets/items-catalog.json'],cwd=ROOT))
        new=json.loads((ROOT/'web/assets/items-catalog.json').read_text())
        self.assertEqual(old['47'], new['47'])
        self.assertEqual(new['47001']['icon'],new['47']['icon'])


if __name__ == '__main__':
    unittest.main()
