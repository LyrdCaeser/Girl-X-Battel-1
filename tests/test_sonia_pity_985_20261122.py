"""Sonia has 99.2%/0.8% early featured chance, with a 100% hard stop at 150."""
import unittest
from gxb2 import chaos_summon


class Pity992Tests(unittest.TestCase):
    def draw(self,roll):
        state={'items':{'940060':1},'partners':[],'next_partner_id':1,
               'chaos_summon':{'times':119,'total':119,'cycles':0}}
        new=chaos_summon.summon(
            state,27,lambda:33001,rng=lambda n:roll,
            offbanner_draw=lambda:51017,
            is_five_star=lambda tid:tid==51017)
        return state,new[0]['table_id']

    def test_exact_probability_and_boundaries(self):
        self.assertEqual(chaos_summon.GUARANTEE_HIT_BASIS_POINTS,9920)
        for roll in (0,300,9919):
            state,target=self.draw(roll)
            self.assertEqual(target,758001)
            self.assertEqual(state['chaos_summon']['times'],0)
            self.assertEqual(state['chaos_summon']['cycles'],1)
        for roll in (9920,9975,9999):
            state,target=self.draw(roll)
            self.assertEqual(target,51017)
            self.assertEqual(state['chaos_summon']['times'],0)
            self.assertEqual(state['chaos_summon']['cycles'],1)

    def test_client_percentages(self):
        s=chaos_summon.snapshot({'items':{},'partners':[]})
        self.assertEqual(s['guaranteed_hit_percent'],99.2)
        self.assertEqual(s['guaranteed_miss_percent'],0.8)
        self.assertEqual(s['first_guarantee'],120)
        self.assertEqual(s['repeat_guarantee'],150)
        self.assertEqual(s['hard_guaranteed_hit_percent'],100.0)


if __name__=='__main__':
    unittest.main()
