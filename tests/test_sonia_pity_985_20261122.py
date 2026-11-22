"""Sonia's pity is exactly 98.5% hit / 1.5% offbanner, not 100% or 95%."""
import unittest
from gxb2 import chaos_summon


class Pity985Tests(unittest.TestCase):
    def draw(self,roll):
        state={'items':{'940060':1},'partners':[],'next_partner_id':1,
               'chaos_summon':{'times':119,'total':119,'cycles':0}}
        new=chaos_summon.summon(
            state,27,lambda:33001,rng=lambda n:roll,
            offbanner_draw=lambda:51017,
            is_five_star=lambda tid:tid==51017)
        return state,new[0]['table_id']

    def test_exact_probability_and_boundaries(self):
        self.assertEqual(chaos_summon.GUARANTEE_HIT_BASIS_POINTS,9850)
        for roll in (0,300,9849):
            state,target=self.draw(roll)
            self.assertEqual(target,758001)
            self.assertEqual(state['chaos_summon']['times'],0)
            self.assertEqual(state['chaos_summon']['cycles'],1)
        for roll in (9850,9875,9999):
            state,target=self.draw(roll)
            self.assertEqual(target,51017)
            self.assertEqual(state['chaos_summon']['times'],0)
            self.assertEqual(state['chaos_summon']['cycles'],1)

    def test_client_percentages(self):
        s=chaos_summon.snapshot({'items':{},'partners':[]})
        self.assertEqual(s['guaranteed_hit_percent'],98.5)
        self.assertEqual(s['guaranteed_miss_percent'],1.5)
        self.assertEqual(s['first_guarantee'],120)
        self.assertEqual(s['repeat_guarantee'],150)


if __name__=='__main__':
    unittest.main()
