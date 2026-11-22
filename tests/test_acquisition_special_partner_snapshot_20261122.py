import unittest

from gxb2 import acquisition


class AcquisitionSpecialPartnerTests(unittest.TestCase):
    def test_special_summon_is_not_eligible_for_original_replacement(self):
        self.assertNotIn('758001', acquisition.PARTNERS)
        self.assertFalse(acquisition.eligible({'partner_id': 42, 'table_id': 758001, 'awake': 0}))
        self.assertFalse(acquisition.eligible({'partner_id': 43, 'table_id': 999999999, 'awake': 0}))

    def test_snapshot_keeps_loading_when_special_summon_is_owned(self):
        state = {
            'items': {'3': 0},
            'partners': [
                {'partner_id': 42, 'table_id': 758001, 'awake': 0},
                {'partner_id': 43, 'table_id': 41001, 'awake': 0},
            ],
        }
        payload = acquisition.snapshot(state, now=1700000000, developer=True)
        self.assertEqual([p['partner_id'] for p in payload['eligible']], [43])
        self.assertIn('slots', payload)
        self.assertEqual(len(state['partners']), 2)


if __name__ == '__main__':
    unittest.main()
