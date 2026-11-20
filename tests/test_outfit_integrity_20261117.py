"""Outfit regression tests with disposable in-memory game states only."""
import copy
import unittest

from gxb2 import dress, dress_show


def sample():
    return {'items': {'1': 999999999, '2': 100000, '258': 20, '259': 20,
                      '260': 30000, '261': 30000}}


class OutfitIntegrity(unittest.TestCase):
    def test_original_catalogue_availability(self):
        out = dress.catalog()['pieces']
        self.assertEqual(len(out), 288)
        valid = [int(k) for k, v in out.items() if v['available']]
        self.assertEqual(len(valid), 242)
        self.assertFalse(out['101231']['available'])
        self.assertTrue(out['101230']['available'])
        self.assertEqual(len(out['101001']['styles']), 2)

    def test_saved_variant_is_persistent_after_snapshot(self):
        state = sample()
        a = [1000102, 1000201, 1000301, 0, 0]
        dress.action(state, {'action':'save', 'styles':a}, 2000000000)
        self.assertEqual(state['dress']['equipped'], a)
        self.assertEqual(state['dress']['style']['101001'], 1000102)
        fresh = dress.snapshot(state, 2000000001)
        self.assertEqual(fresh['style']['101001'], 1000102)
        self.assertEqual(fresh['equipped'], a)

    def test_snapshot_skips_unknown_record_without_modifying_player(self):
        state = sample()
        dress.saved(state)['owned']['9999999'] = 5
        old = copy.deepcopy(state)
        result = dress.snapshot(state,2000000000)
        self.assertEqual(state,old)
        self.assertNotIn(9999999,[p['dress'] for p in result['owned']])

    def test_incomplete_owned_piece_does_not_break_profile(self):
        state = sample()
        dress.saved(state)['owned']['101231'] = 1
        old = copy.deepcopy(state)
        result = dress.snapshot(state,2000000000)
        row = next(x for x in result['owned'] if x['dress'] == 101231)
        self.assertIsNone(row['cost'])
        self.assertEqual(state,old)

    def test_outfit_showcase_with_unknown_legacy_piece(self):
        state = sample()
        dress.saved(state)
        # A legacy/invalid Outfit reference must not make the Showcase fail.
        slot = next(iter(dress_show.SLOTS))
        state['dress_show'] = {'slots': {slot:9999999}}
        before = copy.deepcopy(state)
        snapshot = dress_show.snapshot(state, 2000000000)
        self.assertEqual(len(snapshot['booths']),4)
        self.assertEqual(state,before)

    def test_no_shard_conversion_never_loses_duplicate(self):
        state = sample()
        dress.saved(state)
        original = copy.deepcopy(state)
        with self.assertRaisesRegex(ValueError,'chưa có mảnh'):
            dress.grant(state,3100001)
        self.assertEqual(state,original)

    def test_one_free_draw_then_payment(self):
        state = sample()
        t = 2000000000
        before = state['items']['258']
        first=dress.action(state,{'action':'summon','kind':1,'count':1},t,seed=21)
        self.assertEqual(len(first['results']),1)
        self.assertEqual(state['items']['258'],before)
        second=dress.action(state,{'action':'summon','kind':1,'count':1},t+1,seed=22)
        self.assertEqual(len(second['results']),1)
        self.assertEqual(state['items']['258'],before-1)
        self.assertEqual(dress.snapshot(state,t+1)['draws'],2)

    def test_ten_draws_charge_ten_once(self):
        state=sample()
        before=state['items']['259']
        result=dress.action(state,{'action':'summon','kind':2,'count':10},2000000000,seed=12)
        self.assertEqual(len(result['results']),10)
        self.assertEqual(state['items']['259'],before-10)
        self.assertEqual(dress.snapshot(state,2000000000)['draws'],10)

    def test_upgrade_spends_required_materials_only(self):
        candidate=next(did for did in dress.PIECES
                       if dress.complete_piece(did)
                       and dress.ITEMS[dress.item_of(did,1)].get('next_id'))
        state=sample()
        d=dress.saved(state)
        d['owned'][str(candidate)] = 1
        costs=dress.upgrade_cost(d,candidate)
        self.assertTrue(costs)
        for key,n in costs.items():
            item_key=str(dress.COMMON[int(key[3:])-1]) if key.startswith('qlt') else str(key)
            state['items'][item_key]=n+100
        before=copy.deepcopy(state['items'])
        result=dress.action(state,{'action':'upgrade','dress':candidate},2000000000)
        self.assertEqual(result['star'],2)
        for key,n in costs.items():
            item_key=str(dress.COMMON[int(key[3:])-1]) if key.startswith('qlt') else str(key)
            self.assertEqual(state['items'][item_key],before[item_key]-n)

if __name__ == '__main__':
    unittest.main()
