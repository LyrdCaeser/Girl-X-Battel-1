"""One-time discounted Sonia clock roulette with server-authoritative price.
Only synthetic profiles, or isolated temporary SQLite, no production accounts.
"""
import copy
import tempfile
import unittest
from pathlib import Path
from gxb2 import sonia_festival as f
from gxb2.engine import Engine

NOW=f.START+10800


def player(gems=10000,spins=None):
    state={'items':{'2':gems,'940061':0},'partners':[]}
    if spins is not None:state['sonia_festival']={'spins':spins}
    return state


class ClockDiscountTests(unittest.TestCase):

    def test_prices_and_range_1_to_100_from_server(self):
        self.assertEqual(f.SPIN_COST,{1:1200,5:5800})
        self.assertEqual(f.DISCOUNT_MIN,1)
        self.assertEqual(f.DISCOUNT_MAX,100)
        for draw,percent in ((0,1),(1,2),(32,33),(49,50),(98,99),(99,100)):
            with self.subTest(draw=draw):
                s=player()
                offer=f.action(s,{'action':'sonia_discount_draw'},NOW,rng=lambda max_:draw)
                self.assertEqual(offer['discount_percent'],percent)
                wheel=f.snapshot(s,NOW)['wheel']
                self.assertFalse(wheel['first_discount']['needs_draw'])
                self.assertEqual(wheel['first_discount']['percent'],percent)
                for count,base in f.SPIN_COST.items():
                    self.assertEqual(wheel['first_discount']['prices'][str(count)],
                                     base*(100-percent)//100)
                    self.assertGreaterEqual(wheel['first_discount']['prices'][str(count)],0)
        self.assertEqual(f.snapshot(player(),NOW)['wheel']['first_discount']['prices'],
                         {'1':1200,'5':5800})

    def test_welcome_is_zero_cost_never_spends_diamonds_or_adds_spins(self):
        s=player(0)
        before=copy.deepcopy(s)
        offer=f.action(s,{'action':'sonia_discount_draw'},NOW,rng=lambda max_:99)
        self.assertEqual(offer,{'awards':{},'discount_percent':100})
        self.assertEqual(s['items'],before['items'])
        self.assertEqual(f.snapshot(s,NOW)['wheel']['spins'],0)
        result=f.action(s,{'action':'sonia_spin','count':5},NOW,rng=lambda max_:9999)
        self.assertEqual(result['cost'],0)
        self.assertEqual(result['discount_percent'],100)
        self.assertEqual(len(result['draws']),5)
        self.assertEqual(s['items']['2'],0)
        self.assertEqual(s['sonia_festival']['spins'],5)
        self.assertTrue(s['sonia_festival']['clock_discount_used'])
        self.assertFalse(f.snapshot(s,NOW)['wheel']['first_discount']['eligible'])
        with self.assertRaisesRegex(ValueError,'đã được sử dụng'):
            f.action(s,{'action':'sonia_discount_draw'},NOW,rng=lambda max_:0)

    def test_reopening_cannot_re_roll_existing_coupon(self):
        s=player()
        attempts=[25,99]
        def random(max_):
            return attempts.pop(0)
        first=f.action(s,{'action':'sonia_discount_draw'},NOW,rng=random)
        second=f.action(s,{'action':'sonia_discount_draw'},NOW,rng=random)
        self.assertEqual(first,second)
        self.assertEqual(attempts,[99])
        self.assertEqual(f.snapshot(s,NOW)['wheel']['first_discount']['percent'],26)
        self.assertEqual(f.snapshot(s,NOW)['wheel']['first_discount']['prices']['1'],888)

    def test_invalid_discount_rng_never_mutates_player(self):
        s=player()
        old=copy.deepcopy(s)
        for n in (-1,100,105):
            with self.assertRaisesRegex(ValueError,'chưa quay đúng'):
                f.action(s,{'action':'sonia_discount_draw'},NOW,rng=lambda max_:n)
            self.assertEqual(s,old)

    def test_no_prize_spin_without_claiming_first_discount(self):
        s=player()
        old=copy.deepcopy(s)
        with self.assertRaisesRegex(ValueError,'ưu đãi'):
            f.action(s,{'action':'sonia_spin','count':1},NOW,rng=lambda max_:0)
        self.assertEqual(s,old)

    def test_discount_one_time_for_x1_then_x5_returns_to_full_price(self):
        s=player(10000)
        f.action(s,{'action':'sonia_discount_draw'},NOW,rng=lambda max_:49)
        one=f.action(s,{'action':'sonia_spin','count':1},NOW,rng=lambda max_:9999)
        self.assertEqual(one['cost'],600)
        self.assertEqual(s['items']['2'],9400)
        self.assertFalse(f.snapshot(s,NOW)['wheel']['first_discount']['eligible'])
        five=f.action(s,{'action':'sonia_spin','count':5},NOW,rng=lambda max_:9999)
        self.assertEqual(five['cost'],5800)
        self.assertEqual(five['discount_percent'],0)
        self.assertEqual(s['items']['2'],3600)
        self.assertEqual(s['sonia_festival']['spins'],6)

    def test_discount_one_time_x5_consumes_once_not_per_each_reward(self):
        s=player(20000)
        f.action(s,{'action':'sonia_discount_draw'},NOW,rng=lambda max_:29)
        five=f.action(s,{'action':'sonia_spin','count':5},NOW,rng=lambda max_:0)
        self.assertEqual(five['cost'],4060)
        self.assertEqual(len(five['draws']),5)
        self.assertEqual(s['sonia_festival']['spins'],5)
        self.assertEqual(s['items']['2'],15940)
        one=f.action(s,{'action':'sonia_spin','count':1},NOW,rng=lambda max_:9999)
        self.assertEqual(one['cost'],1200)

    def test_insufficient_gems_does_not_consume_coupon(self):
        s=player(0)
        f.action(s,{'action':'sonia_discount_draw'},NOW,rng=lambda max_:49)
        before=copy.deepcopy(s)
        with self.assertRaisesRegex(ValueError,'Không đủ Kim Cương'):
            f.action(s,{'action':'sonia_spin','count':1},NOW,rng=lambda max_:9999)
        self.assertEqual(s,before)
        self.assertFalse(s['sonia_festival']['clock_discount_used'])
        self.assertTrue(f.snapshot(s,NOW)['wheel']['first_discount']['eligible'])

    def test_previous_spinners_do_not_receive_retroactive_offer(self):
        for spins in (1,30,199,200):
            with self.subTest(spins=spins):
                s=player(9000,spins)
                original=copy.deepcopy(s)
                wheel=f.snapshot(s,NOW)['wheel']
                self.assertFalse(wheel['first_discount']['eligible'])
                self.assertFalse(wheel['first_discount']['needs_draw'])
                self.assertEqual(s,original)
                with self.assertRaisesRegex(ValueError,'đã được sử dụng'):
                    f.action(s,{'action':'sonia_discount_draw'},NOW,rng=lambda max_:99)
                self.assertEqual(s,original)

    def test_old_players_can_continue_normal_rate(self):
        s=player(10000,30)
        res=f.action(s,{'action':'sonia_spin','count':1},NOW,rng=lambda max_:9999)
        self.assertEqual(res['cost'],1200)
        self.assertEqual(s['sonia_festival']['spins'],31)

    def test_no_double_first_purchase_and_zero_discount_after_expiry(self):
        s=player(7000)
        f.action(s,{'action':'sonia_discount_draw'},NOW,rng=lambda max_:0)
        f.action(s,{'action':'sonia_spin','count':1},NOW,rng=lambda max_:0)
        before=copy.deepcopy(s)
        with self.assertRaisesRegex(ValueError,'đã được sử dụng'):
            f.action(s,{'action':'sonia_discount_draw'},NOW,rng=lambda max_:99)
        self.assertEqual(s,before)
        with self.assertRaisesRegex(ValueError,'đã kết thúc'):
            f.action(s,{'action':'sonia_spin','count':1},f.ENDS['shards'],rng=lambda max_:0)
        self.assertEqual(s,before)

    def test_discount_does_not_bypass_season_cap(self):
        s=player(9999,spins=200)
        original=copy.deepcopy(s)
        with self.assertRaisesRegex(ValueError,'đạt số lượt'):
            f.action(s,{'action':'sonia_spin','count':1},NOW,rng=lambda max_:9999)
        self.assertEqual(s,original)

    def test_real_engine_persists_discount_in_transaction(self):
        with tempfile.TemporaryDirectory(prefix='gxb3-sonia-discount-') as d:
            engine=Engine(Path(d)/'profile.sqlite3')
            try:
                # Engine snapshot time is current real day (Nov 23, 2026);
                # patch only the time method to the festival test window.
                engine.now=lambda:NOW
                state=engine._load()
                state['sonia_festival']={'spins':0}
                state['items']['2']=10000
                engine._save_profile(state);engine.db.commit()
                welcome=engine.events_action({'action':'sonia_discount_draw'})
                pct=welcome['discount_percent']
                self.assertTrue(1<=pct<=100)
                again=engine.events_action({'action':'sonia_discount_draw'})
                self.assertEqual(again['discount_percent'],pct)
                price=welcome['state']['sonia_festival_info']['wheel']['first_discount']['prices']['1']
                result=engine.events_action({'action':'sonia_spin','count':1})
                self.assertEqual(result['cost'],price)
                self.assertEqual(result['state']['sonia_festival_info']['wheel']['spins'],1)
                self.assertTrue(result['state']['sonia_festival']['clock_discount_used'])
                with self.assertRaisesRegex(ValueError,'đã được sử dụng'):
                    engine.events_action({'action':'sonia_discount_draw'})
                snap=engine.snapshot()
                self.assertEqual(snap['sonia_festival_info']['wheel']['spins'],1)
                self.assertEqual(snap['items']['2'],10000-price)
            finally:
                engine.close()


if __name__=='__main__':
    unittest.main()
