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
            self.assertEqual(six, int(TABLES['partner'][str(tid)]['max_star'] >= 6))
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
        with self.assertRaisesRegex(GameError, 'trao đổi'):
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
        ids = [self.add(651001) for _ in range(6)]
        before = len(self.state['partners'])
        with self.assertRaises(GameError):
            self.engine._dispatch('DECOMPOSE_PARTNERS', {'partner_ids': ids}, self.state)
        self.assertEqual(len(self.state['partners']), before)


    def test_specials_obey_native_daily_quota(self):
        from gxb2 import clock
        ids = [self.add(tid) for tid in (661001,761001,757001,757002,757003)]
        self.state['altar'] = {'day': clock.day(self.engine.now()), 'six': 5}
        expected, quota = self.engine.altar_returns(self.state, ids)
        self.assertTrue(expected)
        self.assertEqual(quota, 5)
        with self.assertRaisesRegex(GameError, 'Mỗi ngày'):
            self.engine._dispatch('DECOMPOSE_PARTNERS', {'partner_ids': ids}, self.state)
        self.assertEqual(self.state['altar']['six'], 5)
        self.state['altar']['six'] = 0
        self.engine._dispatch('DECOMPOSE_PARTNERS', {'partner_ids': ids}, self.state)
        self.assertEqual(self.state['altar']['six'], 5)

    def test_verified_admin_unlimited_daily_but_preserves_safety(self):
        from unittest.mock import patch
        from gxb2 import s5_test, clock
        uid='owner-test'
        self.engine.identity=(uid,'S5')
        self.state.update(uid=uid,server_id='S5')
        self.state['altar']={'day':clock.day(self.engine.now()),'six':5}
        with patch.object(s5_test,'verified_owner',side_effect=lambda x:x==uid):
            for world in ('S1','S2','S3','S4','S5'):
                self.engine.identity=(uid,world)
                self.state['server_id']=world
                ids=[self.add(651001) for _ in range(12)]
                self.assertTrue(self.engine.altar_unlimited(self.state))
                with patch.object(self.engine,'_load',return_value=self.state):
                    preview=self.engine.altar_preview({'partner_ids':ids})
                    self.assertTrue(preview['unlimited'])
                    self.assertIsNone(preview['six_left'])
                self.engine._dispatch('DECOMPOSE_PARTNERS',{'partner_ids':ids},self.state)
                self.assertTrue(set(ids).isdisjoint(x['partner_id'] for x in self.state['partners']))
            self.assertEqual(self.state['altar']['six'],65)
            locked=self.add(651001,flags=[1])
            with self.assertRaises(GameError):
                self.engine._dispatch('DECOMPOSE_PARTNERS',{'partner_ids':[locked]},self.state)
            ids=[self.add(651001) for _ in range(13)]
            with self.assertRaises(GameError):
                self.engine._dispatch('DECOMPOSE_PARTNERS',{'partner_ids':ids},self.state)
            self.engine.identity=('ordinary','S5')
            self.assertFalse(self.engine.altar_unlimited(self.state))
            self.state['uid']='ordinary'
            with self.assertRaises(GameError):
                self.engine._dispatch('DECOMPOSE_PARTNERS',{'partner_ids':ids[:1],'admin':True},self.state)
            self.engine.identity=None
            self.state['uid']=uid
            self.assertFalse(self.engine.altar_unlimited(self.state))

    def test_regular_six_star_remains_limited_after_five(self):
        from gxb2 import clock
        regular = self.add(651001)
        self.state['altar'] = {'day': clock.day(self.engine.now()), 'six': 5}
        count = len(self.state['partners'])
        with self.assertRaisesRegex(GameError, 'Mỗi ngày'):
            self.engine._dispatch(
                'DECOMPOSE_PARTNERS', {'partner_ids': [regular]}, self.state)
        self.assertEqual(count, len(self.state['partners']))

    def test_mixed_batch_counts_all_six_star(self):
        from gxb2 import clock
        ids = [self.add(tid) for tid in (561001,661001,757001,651001)]
        reward, quota = self.engine.altar_returns(self.state, ids)
        self.assertTrue(reward)
        self.assertEqual(quota, 3)
        self.state['altar'] = {'day': clock.day(self.engine.now()), 'six': 3}
        with self.assertRaises(GameError):
            self.engine._dispatch('DECOMPOSE_PARTNERS', {'partner_ids': ids}, self.state)
        self.state['altar']['six'] = 2
        self.engine._dispatch('DECOMPOSE_PARTNERS', {'partner_ids': ids}, self.state)
        self.assertEqual(self.state['altar']['six'], 5)

if __name__ == '__main__':
    unittest.main()
