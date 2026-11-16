"""Safe, offline Altar retirement checks; never accesses production Neon."""
import tempfile
import unittest
from pathlib import Path

from gxb2.engine import Engine, GameError, RETURN, TABLES, item_pairs


def girl(pid, tid, **extra):
    return {
        'partner_id': pid, 'table_id': tid, 'lv': 1, 'grade': 0,
        'awake': 0, 'equips': [], 'pos': 0, 'show_skin': 1,
        **extra,
    }


class AltarDollsCosmosTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.engine = Engine(Path(self.tmp.name) / 'offline.sqlite3')
        self.state = self.engine._load()

    def tearDown(self):
        self.engine.close()
        self.tmp.cleanup()

    def add(self, tid, **extra):
        pid = max(x['partner_id'] for x in self.state['partners']) + 1
        self.state['partners'].append(girl(pid, tid, **extra))
        return pid

    def test_all_native_dolls_use_their_own_decompose_table(self):
        self.assertEqual(len(RETURN['puppets']), 18)
        for tid in RETURN['puppets']:
            pid = self.add(tid)
            rewards, six = self.engine.altar_returns(self.state, [pid])
            expected = {str(k): v for k, v in item_pairs(TABLES['partner'][str(tid)]['decompose']).items()}
            self.assertEqual(rewards, expected, tid)
            self.assertEqual(six, int(int(TABLES['partner'][str(tid)]['max_star']) >= 6))
            self.state['partners'].pop()

    def test_three_playable_cosmos_girls_use_existing_native_10star_recipe(self):
        native = {str(k): v for k, v in item_pairs(TABLES['partner']['751001']['decompose']).items()}
        self.assertTrue(native)
        for tid in (757001, 757002, 757003):
            pid = self.add(tid)
            rewards, six = self.engine.altar_returns(self.state, [pid])
            self.assertEqual(rewards, native)
            self.assertEqual(six, 1)
            self.state['partners'].pop()

    def test_nonplayable_cosmos_npc_is_not_deletable(self):
        pid = self.add(2000031)
        with self.assertRaisesRegex(GameError, 'không hợp lệ'):
            self.engine.altar_returns(self.state, [pid])

    def test_locked_girls_stay_protected(self):
        for tid in (561001, 757001):
            pid = self.add(tid, flags=[1])
            with self.assertRaises(GameError):
                self.engine.altar_returns(self.state, [pid])
            self.state['partners'].pop()

    def test_pending_exchange_and_last_girl_stay_protected(self):
        pid = self.add(757001)
        self.state['exchange'] = {'partner_id': pid}
        with self.assertRaisesRegex(GameError, 'intercambio'):
            self.engine.altar_returns(self.state, [pid])
        self.state['exchange'] = {}
        self.state['partners'] = [self.state['partners'][-1]]
        with self.assertRaises(GameError):
            self.engine.altar_returns(self.state, [pid])

    def test_real_dispatch_changes_only_selected_roster_and_uses_reward_preview(self):
        d, c = self.add(561001), self.add(757001)
        self.state['formation'].append({'partner_id': c, 'pos': 6})
        self.state['campaign_hang'] = [{'partner_id': d, 'pos': 1}]
        preview, six = self.engine.altar_returns(self.state, [d, c])
        before = {k: int(self.state['items'].get(k, 0)) for k in preview}
        packets, _ = self.engine._dispatch('DECOMPOSE_PARTNERS', {'partner_ids': [d, c]}, self.state)
        self.assertTrue(packets)
        self.assertEqual(self.state['last_decompose'], preview)
        self.assertEqual(self.state['altar']['six'], six)
        for key, number in preview.items():
            self.assertEqual(self.state['items'][key], before[key] + number)
        self.assertFalse({d, c}.intersection(x['partner_id'] for x in self.state['partners']))
        self.assertFalse({d, c}.intersection(x['partner_id'] for x in self.state['formation']))
        self.assertFalse({d, c}.intersection(x['partner_id'] for x in self.state['campaign_hang']))

    def test_six_star_daily_cap_still_rejects_six_in_one_action(self):
        ids = [self.add(tid) for tid in RETURN['puppets'][6:12]]
        before = len(self.state['partners'])
        with self.assertRaises(GameError):
            self.engine._dispatch('DECOMPOSE_PARTNERS', {'partner_ids': ids}, self.state)
        self.assertEqual(len(self.state['partners']), before)


if __name__ == '__main__':
    unittest.main()
