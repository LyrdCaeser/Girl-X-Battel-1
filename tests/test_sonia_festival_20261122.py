"""Production-safe, synthetic-state only tests of Lyr Sonia seasonal events."""
from copy import deepcopy
from pathlib import Path
import unittest

from gxb2 import sonia_festival as f, goddess_gifts, gm_catalog
from gxb2.engine import TABLES, DEBRIS, Engine

ROOT=Path(__file__).resolve().parents[1]


def profile():
    return {'items':{'2':500_000,'940061':0,'940060':0},
            'partners':[{'partner_id':1,'table_id':758001,'awake':0}],
            'server_id':'S1'}


class SoniaFestivalTests(unittest.TestCase):
    def test_window_lengths_and_total_limits(self):
        self.assertEqual(f.ENDS['stars']-f.START,15*86400)
        self.assertEqual(f.ENDS['shards']-f.START,7*86400)
        self.assertEqual(f.ENDS['missions']-f.START,30*86400)
        self.assertEqual(sorted(f.STAR_REWARDS),list(range(11,26)))
        self.assertEqual(sum(r[0] for r in f.WHEEL),10_000)
        self.assertEqual(sum(t[5] for t in f.TASKS),12)
        self.assertEqual(f.SPIN_COST,{5:2000,10:9500})
        self.assertNotIn(f.TICKET,set().union(*(d.keys() for _,d,_ in f.WHEEL)))
        self.assertNotIn(f.GEMS,set().union(*(d.keys() for _,d,_ in f.WHEEL)))

    def test_snapshot_does_not_mutate_player(self):
        state=profile()
        before=deepcopy(state)
        snap=f.snapshot(state,f.START+1)
        self.assertEqual(state,before)
        self.assertEqual(snap['stars'][0]['star'],11)
        self.assertFalse(snap['stars'][0]['can'])
        self.assertEqual(snap['highest_owned_star'],10)

    def test_awake_claim_is_real_action_only_and_once(self):
        state=profile()
        with self.assertRaises(ValueError):
            f.action(state,{'action':'sonia_star_claim','star':11},f.START+1)
        self.assertEqual(state['items']['1'] if '1' in state['items'] else 0,0)
        f.record_sonia_star(state,11,f.START+2)
        self.assertTrue(f.snapshot(state,f.START+3)['stars'][0]['can'])
        out=f.action(state,{'action':'sonia_star_claim','star':11},f.START+3)
        self.assertEqual(out['awards'],f.STAR_REWARDS[11])
        before=deepcopy(state)
        with self.assertRaises(ValueError):
            f.action(state,{'action':'sonia_star_claim','star':11},f.START+4)
        self.assertEqual(state,before)
        with self.assertRaises(ValueError):
            f.action(state,{'action':'sonia_star_claim','star':25},f.START+4)
        self.assertEqual(state,before)
        with self.assertRaises(ValueError):
            f.action(state,{'action':'sonia_star_claim','star':11},f.ENDS['stars'])

    def test_one_high_star_upgrade_cannot_claim_unearned_lower_tiers(self):
        player=profile()
        player['partners'][0]['awake']=14  # Starting at 24★
        f.record_sonia_star(player,25,f.START+5,prior=24)
        unlocked=[x['star'] for x in f.snapshot(player,f.START+5)['stars'] if x['can']]
        self.assertEqual(unlocked,[25])
        with self.assertRaises(ValueError):
            f.action(player,{'action':'sonia_star_claim','star':11},f.START+6)
        reward=f.action(player,{'action':'sonia_star_claim','star':25},f.START+6)
        self.assertEqual(reward['awards'],f.STAR_REWARDS[25])

    def test_spin_prices_odds_and_hard_cap(self):
        state=profile()
        r=f.action(state,{'action':'sonia_spin','count':5},f.START+1,rng=lambda bound:0)
        self.assertEqual(r['cost'],2000)
        self.assertEqual(r['awards'],{f.SHARD:10})
        self.assertEqual(state['items']['2'],498_000)
        self.assertEqual(state['items'][f.SHARD],10)
        r=f.action(state,{'action':'sonia_spin','count':10},f.START+1,rng=lambda bound:9999)
        self.assertEqual(r['cost'],9500)
        self.assertEqual(r['awards'],{'1':120000})
        self.assertEqual(state['items']['2'],488_500)
        self.assertEqual(f.snapshot(state,f.START+2)['wheel']['spins'],15)
        state['sonia_festival']['spins']=196
        before=deepcopy(state)
        with self.assertRaises(ValueError):
            f.action(state,{'action':'sonia_spin','count':5},f.START+3)
        self.assertEqual(before,state)
        with self.assertRaises(ValueError):
            f.action(state,{'action':'sonia_spin','count':5},f.ENDS['shards'])
        for bad in (1,2,4,6,'5',True,100):
            with self.assertRaises(ValueError):
                f.action(state,{'action':'sonia_spin','count':bad},f.START+1)

    def test_mission_requires_real_counter_and_deadline(self):
        state=profile()
        f.record(state,'victory',39,f.START+20)
        with self.assertRaises(ValueError):
            f.action(state,{'action':'sonia_mission_claim','id':'victory40'},f.START+22)
        f.record(state,'victory',1,f.START+30)
        self.assertTrue(next(t for t in f.snapshot(state,f.START+31)['missions']
                             if t['id']=='victory40')['can'])
        res=f.action(state,{'action':'sonia_mission_claim','id':'victory40'},f.START+32)
        self.assertEqual(res['awards'],{'940060':1})
        with self.assertRaises(ValueError):
            f.action(state,{'action':'sonia_mission_claim','id':'victory40'},f.START+33)
        f.record(state,'victory',500,f.START+8*86400)
        with self.assertRaises(ValueError):
            f.action(state,{'action':'sonia_mission_claim','id':'victory120'},f.START+14*86400)
        self.assertEqual(state['items']['940060'],1)

    def test_gm_gifts_shards_and_redemption_are_connected(self):
        catalog=[g for g in goddess_gifts.catalog() if g['id']==f.SONIA]
        self.assertEqual(len(catalog),1)
        self.assertEqual(catalog[0]['group'],8)
        self.assertEqual(catalog[0]['stars'],list(range(10,26)))
        for stars in (10,11,15,16,25):
            c=goddess_gifts.validate({'girl_id':f.SONIA,'stars':stars,'level':1})
            self.assertEqual(c['awake'],stars-10)
        shards=[g for g in gm_catalog.catalog()['shards'] if g['girl_id']==f.SONIA]
        self.assertEqual(len(shards),1)
        self.assertEqual(shards[0]['required'],100)
        self.assertIn(f.SHARD,gm_catalog.allowed_gift_ids())
        self.assertEqual(DEBRIS[f.SHARD]['partner_cost'],'758001#100')
        self.assertEqual(TABLES['summon']['10260']['cost'],'940061#100')
        table,total=Engine.__new__(Engine).summon_pool(990061,'S1')
        self.assertEqual(len(table),1)
        self.assertEqual(table[0]['item'],'758001#1')
        self.assertGreater(total,0)
        self.assertTrue((ROOT/'web/assets/item-icons/partner_avatar_758001.png').is_file())
        import json
        public_icons=json.loads((ROOT/'web/assets/item-icons.json').read_text())
        self.assertIn('partner_avatar_758001',public_icons)

    def test_no_hidden_rewards_from_invalid_actions(self):
        state=profile()
        before=deepcopy(state)
        with self.assertRaises(ValueError):
            f.action(state,{'action':'sonia_infinite_tickets'},f.START+100)
        self.assertEqual(state,before)
        f.record(state,'advanced',150,f.START+15*86400)
        task=next(t for t in f.snapshot(state,f.START+15*86400)['missions'] if t['id']=='advanced150')
        self.assertTrue(task['can'])
        got=f.action(state,{'action':'sonia_mission_claim','id':'advanced150'},f.START+15*86400)
        self.assertEqual(got['awards'],{f.TICKET:2})
        self.assertEqual(state['items'][f.TICKET],2)


if __name__=='__main__':
    unittest.main()
