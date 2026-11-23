import json
import unittest
from collections import Counter
from pathlib import Path

from gxb2 import chaos_summon, summon_rates


ROOT = Path(__file__).resolve().parents[1]


class SummonRateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dropbox = json.loads((ROOT / 'data/dropbox.json').read_text())
        cls.partners = json.loads((ROOT / 'data/partner.json').read_text())

    def pool(self, dropbox_id, rows=None, multiplier=None):
        rows = rows or [
            row for row in self.dropbox.values()
            if int(row.get('dropbox_id') or 0) == dropbox_id
            and str(row.get('item', '')).split('#')[0] in self.partners
        ]
        multiplier = multiplier or (lambda row: int(row['weight']))
        return summon_rates.balanced_pool(
            rows, self.partners, dropbox_id, multiplier
        )

    def tier_totals(self, rows):
        totals = Counter()
        for row in rows:
            star = summon_rates.native_star(row, self.partners)
            totals[star] += int(row['_local_weight'])
        return dict(totals)

    def test_all_capsules_have_exact_fixed_tier_budgets(self):
        for dropbox_id, expected in summon_rates.TIER_BUDGETS.items():
            with self.subTest(dropbox_id=dropbox_id):
                pool = self.pool(dropbox_id)
                self.assertEqual(self.tier_totals(pool), expected)
                self.assertEqual(
                    sum(row['_local_weight'] for row in pool),
                    summon_rates.WEIGHT_TOTAL,
                )

    def test_new_rare_girl_redistributes_instead_of_inflating_tier(self):
        rows = [
            row for row in self.dropbox.values()
            if int(row.get('dropbox_id') or 0) == 10002
            and str(row.get('item', '')).split('#')[0] in self.partners
        ]
        clone = dict(next(
            row for row in rows
            if summon_rates.native_star(row, self.partners) == 5
        ))
        clone['id'] = 99999999
        rows.append(clone)
        totals = self.tier_totals(self.pool(10002, rows))
        self.assertEqual(totals[5], 15_000)
        self.assertEqual(sum(totals.values()), 1_000_000)

    def test_admin_multiplier_applies_after_fixed_budget(self):
        def doubled_five_star(row):
            weight = int(row['weight'])
            if summon_rates.native_star(row, self.partners) == 5:
                return weight * 2
            return weight
        totals = self.tier_totals(self.pool(10002, multiplier=doubled_five_star))
        self.assertEqual(totals, {3: 795_000, 4: 190_000, 5: 30_000})


class ChaosSummonRateTests(unittest.TestCase):
    def state(self, tickets=100):
        return {
            'items': {str(chaos_summon.TICKET_ID): tickets},
            'partners': [],
            'next_partner_id': 1,
        }

    def test_featured_hit_uses_half_percent_and_resets_pity(self):
        state = self.state(1)
        new = chaos_summon.summon(state, 27, lambda: 33001, rng=lambda _: 0)
        self.assertEqual(new[0]['table_id'], chaos_summon.PARTNER_ID)
        self.assertEqual(state['chaos_summon']['times'], 0)
        self.assertEqual(state['chaos_summon']['total'], 1)

    def test_first_pity_120_then_150_and_offbanner_five_star(self):
        state=self.state(270)
        no_rare=lambda:33001
        is_five=lambda tid: tid==51017
        calls=[0]
        def first(bound):
            calls[0]+=1
            return 0 if calls[0]==120 else bound-1
        for _ in range(12):
            result=chaos_summon.summon(
                state,29,no_rare,rng=first,
                offbanner_draw=lambda:51017,is_five_star=is_five)
        self.assertEqual(result[-1]['table_id'],chaos_summon.PARTNER_ID)
        self.assertEqual(state['chaos_summon']['times'],0)
        self.assertEqual(chaos_summon.snapshot(state)['guarantee'],150)
        for _ in range(15):
            result=chaos_summon.summon(
                state,29,no_rare,rng=lambda bound:bound-1,
                offbanner_draw=lambda:51017,is_five_star=is_five)
        self.assertEqual(result[-1]['table_id'],chaos_summon.PARTNER_ID)
        self.assertEqual(state['chaos_summon']['cycles'],2)
        self.assertEqual(state['chaos_summon']['times'],0)
        self.assertEqual(state['chaos_summon']['sonia_times'],0)
        self.assertEqual(chaos_summon.snapshot(state)['hard_guaranteed_hit_percent'],100.0)

    def test_natural_five_star_resets_cycle(self):
        state=self.state(1)
        result=chaos_summon.summon(
            state,27,lambda:51017,rng=lambda n:n-1,
            is_five_star=lambda tid:tid==51017)
        self.assertEqual(result[0]['table_id'],51017)
        self.assertEqual(state['chaos_summon']['times'],0)
        self.assertEqual(chaos_summon.snapshot(state)['guarantee'],150)

    def test_legacy_pity_preserved_after_update(self):
        state=self.state(1)
        state['chaos_summon']={'times':82,'total':115}
        self.assertEqual(chaos_summon.snapshot(state)['guarantee'],150)
        self.assertEqual(chaos_summon.snapshot(state)['times'],82)

    def test_insufficient_ticket_does_not_mutate_progress(self):
        state = self.state(0)
        with self.assertRaises(ValueError):
            chaos_summon.summon(state, 27, lambda: 33001)
        self.assertNotIn('chaos_summon', state)


if __name__ == '__main__':
    unittest.main()
