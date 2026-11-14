"""Restore exact archived 6★ awakening recipes, including Lord Dracula.

These tests only read static partner tables. They never access player data.
"""
import unittest
from gxb2 import engine


class NativeSixStarAwakenTests(unittest.TestCase):
    def setUp(self):
        self.reader=object.__new__(engine.Engine)

    def test_lord_dracula_native_7_8_9_10_star_materials_and_costs(self):
        row=engine.TABLES['partner']['651024']
        self.assertEqual(int(row['max_star']), 6)
        original_mats=str(row['awake_material']).split('|')
        original_costs=str(row['stone_material']).split('|')
        expected_target=int(engine.TABLES['partner']['51017']['star_10'])
        self.assertEqual(expected_target, 751017)
        for level in range(4):
            recipe=self.reader.awake_recipe({'table_id':651024,'awake':level})
            self.assertIsNotNone(recipe)
            self.assertEqual(recipe['kind'],'awake')
            self.assertEqual(recipe['star'],7+level)
            self.assertEqual(recipe['material'],[int(x) for x in original_mats[level].split('#')])
            self.assertEqual(recipe['cost'],{str(k):v for k,v in engine.item_pairs(original_costs[level]).items()})
            self.assertEqual(recipe['target'],751017)
        self.assertIsNone(self.reader.awake_recipe({'table_id':651024,'awake':4}))

    def test_native_six_star_without_original_materials_stays_unavailable(self):
        missing=next(int(k) for k,row in engine.TABLES['partner'].items()
                     if int(row.get('max_star') or 0)==6 and not str(row.get('awake_material') or '').strip())
        self.assertIsNone(self.reader.awake_recipe({'table_id':missing,'awake':0}))

    def test_ten_star_original_awakening_remains_unmodified(self):
        recipe=self.reader.awake_recipe({'table_id':751017,'awake':0})
        self.assertEqual(recipe['kind'],'awake')
        self.assertEqual(recipe['star'],11)
        self.assertEqual(recipe['material'],[int(x) for x in engine.TABLES['partner']['751017']['awake_material'].split('|')[0].split('#')])


if __name__ == '__main__':
    unittest.main()
