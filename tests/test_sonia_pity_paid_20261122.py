"""Only synthetic accounts and isolated receipts; never write to Neon."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2 import chaos_summon, sonia_festival as festival, live_service
from gxb2.engine import Engine


class ReceiptAndPityTests(unittest.TestCase):
    def test_sonia_pity_120_then_150_with_real_offbanner_five_star(self):
        state={'items':{'940060':270},'partners':[],'next_partner_id':1}
        first=lambda bound:0 if bound==100 else bound-1
        for _ in range(12):
            chaos_summon.summon(state,29,lambda:33001,rng=first,
                                offbanner_draw=lambda:51017,
                                is_five_star=lambda tid:tid==51017)
        self.assertEqual(state['partners'][-1]['table_id'],758001)
        self.assertEqual(chaos_summon.snapshot(state)['guarantee'],150)
        for _ in range(15):
            chaos_summon.summon(state,29,lambda:33001,
                                rng=lambda bound:bound-1,
                                offbanner_draw=lambda:51017,
                                is_five_star=lambda tid:tid==51017)
        self.assertEqual(state['partners'][-1]['table_id'],51017)
        self.assertEqual(state['chaos_summon']['cycles'],2)
        self.assertEqual(state['chaos_summon']['times'],0)
        self.assertEqual(state['items']['940060'],0)

    def test_pity_probability_is_95_hit_5_off(self):
        for hit_expected,roll in ((True,0),(True,94),(False,95),(False,99)):
            state={'items':{'940060':1},'partners':[],'next_partner_id':1,
                   'chaos_summon':{'times':119,'total':119,'cycles':0}}
            chaos_summon.summon(state,27,lambda:33001,
                                rng=lambda n:roll if n==100 else n-1,
                                offbanner_draw=lambda:51017,
                                is_five_star=lambda tid:tid==51017)
            self.assertEqual(state['partners'][0]['table_id']==758001,hit_expected)
            self.assertEqual(state['chaos_summon']['times'],0)
            self.assertEqual(state['chaos_summon']['cycles'],1)

    def test_pity_not_mutated_when_ticket_missing(self):
        state={'items':{'940060':0},'partners':[],'next_partner_id':1}
        with self.assertRaises(ValueError):
            chaos_summon.summon(state,27,lambda:33001)
        self.assertNotIn('chaos_summon',state)

    def test_exact_paid_tiers_total_350_and_no_double_claim(self):
        state={'items':{'940060':0},'partners':[]}
        self.assertEqual(sum(t[5] for t in festival.TASKS),120)
        with self.assertRaises(ValueError):
            festival.action(state,{'action':'sonia_paid_claim','tier':1},
                            now=festival.START+30,paid_vnd=0)
        total=0
        for index in range(1,9):
            before=state['items']['940060']
            response=festival.action(
                state,{'action':'sonia_paid_claim','tier':index},
                now=festival.START+30,paid_vnd=2_400_000)
            total+=response['awards']['940060']
            self.assertEqual(total,festival.PAID_TIERS[index-1][1])
            self.assertGreater(state['items']['940060'],before)
            with self.assertRaises(ValueError):
                festival.action(state,{'action':'sonia_paid_claim','tier':index},
                                now=festival.START+30,paid_vnd=2_400_000)
        self.assertEqual(total,350)
        self.assertEqual(festival.snapshot(state,festival.START+30,paid_vnd=2_400_000)
                         ['paid_ticket_cap'],350)
        with self.assertRaises(ValueError):
            festival.action(state,{'action':'sonia_paid_claim','tier':8},
                            now=festival.ENDS['missions'],paid_vnd=2_400_000)

    def test_paid_orders_must_be_approved_and_receipt_fixed_by_uid_world(self):
        with tempfile.TemporaryDirectory(prefix='sonia-paid-qa-') as folder:
            path=Path(folder)/'receipts.sqlite3'
            db=sqlite3.connect(path)
            db.execute('CREATE TABLE orders(id TEXT,uid TEXT,server_id TEXT,status TEXT,reviewed_at BIGINT,package TEXT,price_label TEXT)')
            start=festival.START
            rows=[
                ('1','USER-A','S1','approved',start+100,'GEMS_250','30.000 VNĐ'),
                ('2','USER-A','S1','approved',start+200,'GEMS_500','60.000 VNĐ'),
                ('3','USER-A','S1','approved',start+300,'GEMS_5000','600.000 VNĐ'),
                ('4','USER-A','S1','pending',start+300,'GEMS_5000','600.000 VNĐ'),
                ('5','USER-B','S1','approved',start+300,'GEMS_5000','600.000 VNĐ'),
                ('6','USER-A','S2','approved',start+300,'GEMS_5000','600.000 VNĐ'),
                ('7','USER-A','S1','approved',start-5,'GEMS_5000','600.000 VNĐ'),
                ('8','USER-A','S1','approved',start+600,'CUSTOM','2.400.000 VNĐ'),
                ('9','USER-A','S1','approved',start+600,'GEMS_250','5 VNĐ'),
            ]
            db.executemany('INSERT INTO orders VALUES(?,?,?,?,?,?,?)',rows)
            db.commit();db.close()

            def local_db():
                c=sqlite3.connect(path)
                c.row_factory=sqlite3.Row
                return c
            with patch.object(live_service,'_db',local_db):
                paid=live_service.approved_sonia_spend('USER-A','S1',start,festival.ENDS['missions'])
                self.assertEqual(paid,690_000)
                self.assertEqual(live_service.approved_sonia_spend('USER-A','S2',start,festival.ENDS['missions']),600_000)
                self.assertEqual(live_service.approved_sonia_spend('USER-B','S1',start,festival.ENDS['missions']),600_000)
                self.assertEqual(live_service.approved_sonia_spend('USER-X','S1',start,festival.ENDS['missions']),0)
        s=festival.snapshot({'items':{},'partners':[]},festival.START+500,paid_vnd=paid)
        self.assertEqual([x['id'] for x in s['paid_missions'] if x['can']],[1,2,3,4,5])
        self.assertEqual(sum(x['tickets'] for x in s['paid_missions'] if x['can']),150)

    def test_actual_server_pool_probabilities_are_normalized(self):
        engine=Engine.__new__(Engine)
        odds=engine.summon_odds('S1')
        self.assertEqual(set(odds),{'regular','advanced','wish'})
        for key,entry in odds.items():
            self.assertAlmostEqual(sum(x['probability'] for x in entry['stars']),100,places=8)
            self.assertAlmostEqual(sum(x['probability'] for x in entry['girls']),100,places=8)
            self.assertTrue(all(x['probability']>=0 for x in entry['girls']))
        bystar={x['star']:x['probability'] for x in odds['advanced']['stars']}
        self.assertAlmostEqual(bystar[5],1.5,places=6)


if __name__=='__main__':
    unittest.main()
