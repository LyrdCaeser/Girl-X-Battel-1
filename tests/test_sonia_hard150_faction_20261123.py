"""Lyr Sonia 0.8% pre-guarantee deviation + absolute 150-draw guarantee.
Isolated synthetic profiles only; no live player or Neon writes.
"""
import unittest
from gxb2 import chaos_summon as s


class SoniaHardGuaranteeTests(unittest.TestCase):
    def player(self, draws=150, progress=None):
        data={'items':{str(s.TICKET_ID):draws},'partners':[],'next_partner_id':1}
        if progress is not None:
            data['chaos_summon']=progress
        return data

    @staticmethod
    def always_miss(bound):
        return bound-1

    def draw(self, state, n=1, rng=None, fallback=None):
        results=[]
        for _ in range(n):
            results+=s.summon(state,27,fallback or (lambda:33001),
                              rng=rng or self.always_miss,
                              offbanner_draw=lambda:51017,
                              is_five_star=lambda id:int(id)==51017)
        return results

    def test_120_soft_pity_9920_threshold_and_persist_miss(self):
        for roll in (0,9919,9920,9999):
            state=self.player(31,{'times':119,'total':119,'cycles':0})
            results=self.draw(state,rng=lambda bound:roll)
            expected=s.PARTNER_ID if roll<9920 else 51017
            self.assertEqual(results[0]['table_id'],expected)
            self.assertEqual(state['chaos_summon']['times'],0)
            if expected==51017:
                self.assertEqual(s.snapshot(state)['times'],120)
                self.assertEqual(s.snapshot(state)['remaining'],30)
                self.assertTrue(s.snapshot(state)['first_soft_used'])
                self.assertEqual(self.draw(state,30)[-1]['table_id'],s.PARTNER_ID)
            else:
                self.assertEqual(s.snapshot(state)['times'],0)

    def test_150_hard_always_sonia_even_with_unlucky_rng(self):
        state=self.player(151,{'times':149,'total':149,'cycles':5,
                               'sonia_times':149,'sonia_cycles':0,'first_soft_used':True})
        out=self.draw(state,1,rng=self.always_miss)
        self.assertEqual(out[0]['table_id'],758001)
        self.assertEqual(state['chaos_summon']['sonia_times'],0)
        self.assertEqual(state['items'][str(s.TICKET_ID)],150)

    def test_5star_fallback_does_not_erase_hard_pity(self):
        state=self.player(150)
        for x in range(149):
            fallback=(lambda:51017) if x%3==2 else (lambda:33001)
            out=self.draw(state,1,fallback=fallback)
            self.assertNotEqual(out[-1]['table_id'],s.PARTNER_ID)
        self.assertEqual(s.snapshot(state)['times'],149)
        self.assertEqual(s.snapshot(state)['remaining'],1)
        self.assertEqual(self.draw(state,1)[-1]['table_id'],s.PARTNER_ID)
        self.assertEqual(s.snapshot(state)['times'],0)
        self.assertEqual(state['items'][str(s.TICKET_ID)],0)

    def test_x5_and_x10_cross_150_without_double_reward(self):
        for batch in (28,29):
            count=s.SUMMON_COUNTS[batch]
            state=self.player(count,{'times':149,'total':149,'cycles':1,
                                     'sonia_times':149,'sonia_cycles':1,'first_soft_used':True})
            new=s.summon(state,batch,lambda:33001,rng=self.always_miss,
                         offbanner_draw=lambda:51017,
                         is_five_star=lambda id:int(id)==51017)
            self.assertEqual(len(new),count)
            self.assertEqual(new[0]['table_id'],s.PARTNER_ID)
            self.assertEqual(sum(p['table_id']==s.PARTNER_ID for p in new),1)
            self.assertEqual(s.snapshot(state)['times'],count-1)
            self.assertEqual(s.snapshot(state)['remaining'],150-(count-1))
            self.assertEqual(state['items'][str(s.TICKET_ID)],0)

    def test_pre_guarantee_featured_deviation_exactly_8_per_1000(self):
        # When the 0.5% featured branch has been selected: 99.2% Sonia,
        # 0.8% other 5★. At the hard stop no deviation is allowed.
        for featured_roll in (9919,9920):
            state=self.player(1,{'times':1,'total':1,'cycles':1,
                                 'sonia_times':1,'sonia_cycles':1,'first_soft_used':True})
            calls=iter([0,featured_roll])
            result=self.draw(state,rng=lambda bound:next(calls))[0]
            self.assertEqual(result['table_id'],
                             s.PARTNER_ID if featured_roll==9919 else 51017)
            if result['table_id']!=s.PARTNER_ID:
                self.assertEqual(s.snapshot(state)['times'],2)

    def test_legacy_progress_and_display(self):
        state=self.player(10,{'times':82,'total':115})
        snap=s.snapshot(state)
        self.assertEqual(snap['times'],82)
        self.assertEqual(snap['guarantee'],150)
        self.assertEqual(snap['remaining'],68)
        self.assertEqual(snap['hard_guaranteed_hit_percent'],100.0)
        self.assertEqual(snap['guaranteed_hit_percent'],99.2)
        self.assertEqual(snap['guaranteed_miss_percent'],0.8)
        self.assertEqual(snap['first_guarantee'],120)

    def test_insufficient_tickets_keep_original_account_unchanged(self):
        state=self.player(0)
        with self.assertRaisesRegex(ValueError,'Không đủ'):
            self.draw(state)
        self.assertNotIn('chaos_summon',state)
        self.assertEqual(state['partners'],[])


if __name__=='__main__':
    unittest.main()
