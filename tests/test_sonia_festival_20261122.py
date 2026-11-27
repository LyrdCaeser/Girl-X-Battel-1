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
        self.assertEqual(sum(t[5] for t in f.TASKS),120)
        self.assertEqual(f.SPIN_COST,{1:1200,5:5800})
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
        # The complimentary welcome dial grants a 1% coupon, which applies
        # to the very first prize purchase only (5 spins here).
        offer=f.action(state,{'action':'sonia_discount_draw'},f.START+1,rng=lambda bound:0)
        self.assertEqual(offer['discount_percent'],1)
        r=f.action(state,{'action':'sonia_spin','count':5},f.START+1,rng=lambda bound:0)
        self.assertEqual(r['cost'],5742)
        self.assertEqual(r['discount_percent'],1)
        self.assertEqual(r['awards'],{f.SHARD:10})
        self.assertEqual(state['items']['2'],494_258)
        self.assertEqual(state['items'][f.SHARD],10)
        r=f.action(state,{'action':'sonia_spin','count':1},f.START+1,rng=lambda bound:9999)
        self.assertEqual(r['cost'],1200)
        self.assertEqual(r['discount_percent'],0)
        self.assertEqual(r['awards'],{'1':12000})
        self.assertEqual(state['items']['2'],493_058)
        self.assertEqual(f.snapshot(state,f.START+2)['wheel']['spins'],6)
        state['sonia_festival']['spins']=196
        before=deepcopy(state)
        with self.assertRaises(ValueError):
            f.action(state,{'action':'sonia_spin','count':5},f.START+3)
        self.assertEqual(before,state)
        with self.assertRaises(ValueError):
            f.action(state,{'action':'sonia_spin','count':5},f.ENDS['shards'])
        for bad in (2,3,4,6,10,'5',True,100):
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
        self.assertEqual(res['awards'],{'940060':5})
        with self.assertRaises(ValueError):
            f.action(state,{'action':'sonia_mission_claim','id':'victory40'},f.START+33)
        f.record(state,'victory',500,f.START+8*86400)
        with self.assertRaises(ValueError):
            f.action(state,{'action':'sonia_mission_claim','id':'victory120'},f.START+14*86400)
        self.assertEqual(state['items']['940060'],5)

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

    def test_tower_phases_and_legacy_cap(self):
        state=profile()
        start=f.TOWER_START;week=f.TOWER_WEEK
        def claim(key,now):
            return f.action(state,{'action':'sonia_mission_claim','id':key},now)
        def rows(now):
            return {m['id']:m for m in f.snapshot(state,now)['missions']}
        f.record_tower_clear(state,1,start-1)
        f.record(state,'tower_clear',1000,start)
        self.assertEqual(rows(start)['tower100']['progress'],0)
        self.assertNotIn('arena30',rows(start))
        for floor in range(1,101):
            f.record_tower_clear(state,floor,start+1)
        f.record_tower_clear(state,100,start+2)
        self.assertEqual(rows(start+2)['tower100']['progress'],100)
        self.assertTrue(rows(start+2)['tower100']['can'])
        self.assertFalse(rows(start+2)['tower200']['can'])
        with self.assertRaises(ValueError):claim('tower200',start+2)
        self.assertEqual(claim('tower100',start+3)['awards'],{f.TICKET:3})
        with self.assertRaises(ValueError):claim('tower100',start+4)
        for floor in range(101,201):
            f.record_tower_clear(state,floor,start+week)
        self.assertEqual(claim('tower200',start+week)['awards'],{f.TICKET:5})
        for floor in range(201,301):
            f.record_tower_clear(state,floor,start+2*week)
        self.assertEqual(claim('tower300',start+2*week)['awards'],{f.TICKET:7})
        self.assertEqual(state['items'][f.TICKET],15)
        f.record_tower_clear(state,301,start+3*week)
        self.assertEqual(rows(start+3*week)['tower300']['progress'],300)
        missed=profile()
        f.record_tower_clear(missed,1,start)
        missed['sonia_festival']['progress']['tower_clear']=300
        with self.assertRaises(ValueError):
            f.action(missed,{'action':'sonia_mission_claim','id':'tower100'},start+week)
        old=profile()
        old['sonia_festival']={'mission_claimed':['arena30'],'progress':{'tower_clear':300}}
        for i,key in enumerate(f.TOWER_IDS):
            now=start+i*week
            row=next(m for m in f.snapshot(old,now)['missions'] if m['id']==key)
            self.assertTrue(row['legacy_covered']);self.assertFalse(row['can'])
            with self.assertRaises(ValueError):
                f.action(old,{'action':'sonia_mission_claim','id':key},now)
        self.assertEqual(old['items'][f.TICKET],0)
        self.assertLessEqual(start+3*week,f.ENDS['missions'])

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
        self.assertEqual(got['awards'],{f.TICKET:15})
        self.assertEqual(state['items'][f.TICKET],15)


if __name__=='__main__':
    unittest.main()
