import tempfile
import unittest
from pathlib import Path

from gxb2 import live_service, topup
from gxb2.engine import Engine, GameError


class PvPArena3v3Tests(unittest.TestCase):
    def setUp(self):
        self.old_db = live_service.DB_PATH
        self.old_topup = topup.OVERRIDE_PATH
        self.tmp = tempfile.TemporaryDirectory(prefix='gxb3-pvp-3v3-')
        root = Path(self.tmp.name)
        live_service.DB_PATH = root / 'live.sqlite3'
        topup.OVERRIDE_PATH = root / 'topup.json'
        live_service.register_player('A3V3-A', 'S1', 'Alpha')
        live_service.register_player('A3V3-B', 'S1', 'Beta')

    def tearDown(self):
        live_service.DB_PATH = self.old_db
        topup.OVERRIDE_PATH = self.old_topup
        self.tmp.cleanup()

    def _match(self):
        first = live_service.enqueue_pvp('A3V3-A', 'S1', 'Alpha', 'arena3v3', 18000)
        self.assertEqual(first['status'], 'waiting')
        second = live_service.enqueue_pvp('A3V3-B', 'S1', 'Beta', 'arena3v3', 17500)
        self.assertEqual(second['status'], 'matched')
        match = second['match']
        self.assertEqual(match['mode'], 'arena3v3')
        self.assertEqual(match['server_a'], 'S1')
        self.assertEqual(match['server_b'], 'S1')
        live_service.heartbeat_pvp_match(match['id'], 'A3V3-A', True)
        ready = live_service.heartbeat_pvp_match(match['id'], 'A3V3-B', True)
        self.assertEqual(ready['match']['status'], 'active')
        return match

    def _engine(self, uid, tickets=10):
        path = Path(self.tmp.name) / f'{uid}.sqlite3'
        engine = Engine(path)
        state = engine._load()
        state['uid'] = uid
        state['server_id'] = 'S1'
        state['items']['34'] = tickets
        engine._save_profile(state)
        engine.db.commit()
        return engine

    def _pay_both(self, match):
        a = self._engine('A3V3-A')
        b = self._engine('A3V3-B')
        try:
            paid_a = a.pay_pvp_arena3v3_ticket(match['id'], 'A3V3-A')
            paid_b = b.pay_pvp_arena3v3_ticket(match['id'], 'A3V3-B')
            self.assertTrue(paid_a['series']['paid'])
            self.assertTrue(paid_b['series']['paid'])
            self.assertTrue(paid_b['series']['all_paid'])
            return a, b
        except Exception:
            a.close(); b.close()
            raise

    def test_matchmaking_is_real_same_server_and_creates_series(self):
        match = self._match()
        series = live_service.pvp_arena3v3_series_status(match['id'], 'A3V3-A')
        self.assertEqual(series['next_round'], 0)
        self.assertFalse(series['paid'])
        self.assertFalse(series['all_paid'])
        self.assertEqual(series['wins_a'], 0)
        self.assertEqual(series['wins_b'], 0)

    def test_ticket_payment_is_atomic_and_idempotent_for_each_real_player(self):
        match = self._match()
        a = self._engine('A3V3-A', tickets=8)
        try:
            first = a.pay_pvp_arena3v3_ticket(match['id'], 'A3V3-A')
            self.assertEqual(first['tickets_left'], 5)
            second = a.pay_pvp_arena3v3_ticket(match['id'], 'A3V3-A')
            self.assertEqual(second['tickets_left'], 5)
            self.assertTrue(second['series']['paid'])
            self.assertEqual(a.snapshot()['items']['34'], 5)
        finally:
            a.close()

    def test_best_of_three_stops_after_two_wins_and_duplicate_round_cannot_score_twice(self):
        match = self._match()
        a, b = self._pay_both(match)
        try:
            report_a = {'isWin': 1, 'total_round': 15, 'total_harm': 100000}
            first = live_service.record_pvp_arena3v3_round(
                match['id'], 'A3V3-A', 0, 'A3V3-A', report_a)
            self.assertEqual(first['series']['wins_a'], 1)
            self.assertEqual(first['series']['next_round'], 1)

            duplicate = live_service.record_pvp_arena3v3_round(
                match['id'], 'A3V3-B', 0, 'A3V3-B', {'isWin': 0, 'total_round': 15})
            self.assertTrue(duplicate['already_resolved'])
            self.assertEqual(duplicate['series']['next_round'], 1)
            self.assertEqual(duplicate['series']['wins_b'], 0)

            second = live_service.record_pvp_arena3v3_round(
                match['id'], 'A3V3-B', 1, 'A3V3-A', report_a)
            self.assertTrue(second['series']['complete'])
            self.assertEqual(second['series']['winner_uid'], 'A3V3-A')
            self.assertEqual(len(second['series']['rounds']), 2)
            self.assertEqual(second['series']['wins_a'], 2)

            final_report = {
                'isWin': 1, 'total_round': 2, 'series': second['series'],
                'arena3v3': {'sweep': True, 'player_rewards': {
                    'A3V3-A': {'cards':[{'1':11250},{'2':15},{'16':8}], 'pick':0, 'reward':{'1':11250}},
                    'A3V3-B': {'cards':[{'1':11250},{'2':15},{'16':8}], 'pick':1, 'reward':{'2':15}},
                }},
            }
            result = live_service.finish_authoritative_pvp(
                match['id'], 'A3V3-B', {'uid':'A3V3-A','server_id':'S1','name':'Alpha','team':[]},
                {'uid':'A3V3-B','server_id':'S1','name':'Beta','team':[]}, final_report)
            self.assertEqual(result['winner_uid'], 'A3V3-A')
            base_delta = live_service._elo_delta(1000, 1000, True)
            self.assertEqual(result['rating_delta_a'], int(round(base_delta * 1.25)))
            rating = live_service.pvp_rating('A3V3-A', 'S1', 'arena3v3')
            self.assertEqual(rating['wins'], 1)
            self.assertEqual(rating['matches'], 1)
            self.assertGreater(rating['rating'], 1000)
            self.assertEqual(live_service.mailbox('A3V3-A','S1')[-1]['attachments'], {'1':11250})
            self.assertEqual(live_service.mailbox('A3V3-B','S1')[-1]['attachments'], {'2':15})
            stored_a=live_service.pvp_match_result(match['id'],'A3V3-A')['battle_report']['series']
            stored_b=live_service.pvp_match_result(match['id'],'A3V3-B')['battle_report']['series']
            self.assertEqual(stored_a,stored_b)
            self.assertEqual(stored_a['rounds'][0]['winner_uid'],'A3V3-A')
            self.assertNotIn('won_by_me',stored_a['rounds'][0])
            history=live_service.pvp_history('A3V3-A',10)[0]
            self.assertEqual(history['arena3v3_wins_a'],2)
            self.assertEqual(history['arena3v3_wins_b'],0)
            # A duplicate finalize cannot create another reward mail or rating increment.
            again=live_service.finish_authoritative_pvp(
                match['id'],'A3V3-A',{'uid':'A3V3-A','server_id':'S1','name':'Alpha','team':[]},
                {'uid':'A3V3-B','server_id':'S1','name':'Beta','team':[]},final_report)
            self.assertEqual(again['rating_delta_a'],result['rating_delta_a'])
            self.assertEqual(len(live_service.mailbox('A3V3-A','S1')),1)
            self.assertEqual(live_service.pvp_rating('A3V3-A','S1','arena3v3')['matches'],1)
        finally:
            a.close(); b.close()

    def test_third_round_is_used_only_after_split_score(self):
        match = self._match()
        a, b = self._pay_both(match)
        try:
            one = live_service.record_pvp_arena3v3_round(
                match['id'], 'A3V3-A', 0, 'A3V3-A', {'isWin':1,'total_round':15})
            two = live_service.record_pvp_arena3v3_round(
                match['id'], 'A3V3-B', 1, 'A3V3-B', {'isWin':0,'total_round':15})
            self.assertFalse(two['series']['complete'])
            self.assertEqual((two['series']['wins_a'], two['series']['wins_b']), (1,1))
            three = live_service.record_pvp_arena3v3_round(
                match['id'], 'A3V3-A', 2, 'A3V3-B', {'isWin':0,'total_round':15})
            self.assertTrue(three['series']['complete'])
            self.assertEqual(three['series']['winner_uid'], 'A3V3-B')
            self.assertEqual(len(three['series']['rounds']), 3)
        finally:
            a.close(); b.close()

    def test_round_requires_both_ticket_payments_and_rejects_non_participants(self):
        match = self._match()
        with self.assertRaisesRegex(ValueError, 'không thuộc trận'):
            live_service.record_pvp_arena3v3_round(
                match['id'], 'INTRUDER', 0, 'A3V3-A', {'isWin': 1, 'total_round': 15})
        with self.assertRaisesRegex(ValueError, 'Cả hai người chơi'):
            live_service.record_pvp_arena3v3_round(
                match['id'], 'A3V3-A', 0, 'A3V3-A', {'isWin': 1, 'total_round': 15})
        a = self._engine('A3V3-A')
        try:
            a.pay_pvp_arena3v3_ticket(match['id'], 'A3V3-A')
            with self.assertRaisesRegex(ValueError, 'Cả hai người chơi'):
                live_service.record_pvp_arena3v3_round(
                    match['id'], 'A3V3-A', 0, 'A3V3-A', {'isWin': 1, 'total_round': 15})
        finally:
            a.close()

    def test_arena3v3_api_uses_server_snapshots_and_simulation_not_client_winner(self):
        source = (Path(__file__).resolve().parents[1] / 'server.py').read_text(encoding='utf-8')
        start = source.index("if path == '/api/pvp/arena3v3/round':")
        end = source.index("if path == '/api/pvp/match/battle':", start)
        route = source[start:end]
        self.assertIn('pvp_arena3v3_snapshot()', route)
        self.assertIn('simulate_battle(', route)
        self.assertIn('record_pvp_arena3v3_round(', route)
        self.assertNotIn("data.get('winner_uid')", route)
        self.assertNotIn("data.get('report')", route)
        self.assertNotIn("data.get('team_a')", route)
        self.assertNotIn("data.get('team_b')", route)

    def test_original_luajit_round_replay_is_persisted_for_exact_participants(self):
        match=self._match()
        a,b=self._pay_both(match)
        try:
            report={
                'isWin':1,'total_round':4,'total_harm':221,
                'frames':[{'pos':1,'round':1,'skill_id':4100100,'targets':[7],
                           'buffs':[{'pos':7,'f_pos':1,'hp':30}],
                           'eps':[{'pos':1,'ep':100},{'pos':14,'ep':5}]}],
                'teamA':[{'pos':1,'table_id':41001,'level':25}],
                'teamB':[{'pos':1,'table_id':41002,'level':25}],
                'hp':[{'pos':1,'hp':100},{'pos':7,'hp':30}],
                'hurts':[{'pos':7,'hurt':300}],
                'petA':{'pet_id':9},'petB':{'pet_id':10},
            }
            stored=live_service.record_pvp_arena3v3_round(
                match['id'],'A3V3-A',0,'A3V3-A',report)
            self.assertFalse(stored['already_resolved'])
            replay_a=live_service.pvp_arena3v3_round_replay(match['id'],'A3V3-A',0)
            replay_b=live_service.pvp_arena3v3_round_replay(match['id'],'A3V3-B',0)
            self.assertEqual(replay_a['isWin'],1)
            self.assertEqual(replay_b['isWin'],0)
            self.assertEqual(replay_b['frames'][0]['pos'],7)
            self.assertEqual(replay_b['frames'][0]['targets'],[1])
            self.assertEqual(replay_b['frames'][0]['eps'][1]['pos'],13)
            self.assertEqual(replay_b['petA']['pet_id'],10)
            self.assertEqual([u['pos'] for u in replay_b['display_units']],[7,1])
            public=live_service.pvp_arena3v3_series_status(match['id'],'A3V3-A')
            self.assertNotIn('replay_z',str(public))
            self.assertNotIn('replay_z',str(live_service.pvp_history('A3V3-A')))
            self.assertEqual(report['frames'][0]['pos'],1)
            with self.assertRaisesRegex(ValueError,'không thuộc'):
                live_service.pvp_arena3v3_round_replay(match['id'],'INTRUDER',0)
            with self.assertRaisesRegex(ValueError,'chưa'):
                live_service.pvp_arena3v3_round_replay(match['id'],'A3V3-A',1)
            duplicate=live_service.record_pvp_arena3v3_round(
                match['id'],'A3V3-A',0,'A3V3-B',{'isWin':0,'total_round':2})
            self.assertTrue(duplicate['already_resolved'])
            self.assertEqual(live_service.pvp_arena3v3_round_replay(match['id'],'A3V3-A',0),replay_a)
        finally:
            a.close(); b.close()

    def test_historical_summary_only_round_never_returns_fake_battle_frames(self):
        match=self._match()
        a,b=self._pay_both(match)
        try:
            live_service.record_pvp_arena3v3_round(
                match['id'],'A3V3-A',0,'A3V3-A',{'isWin':1,'total_round':15})
            with self.assertRaisesRegex(ValueError,'chưa lưu'):
                live_service.pvp_arena3v3_round_replay(match['id'],'A3V3-A',0)
        finally:
            a.close(); b.close()

    def test_team_saves_are_owned_unique_and_persisted(self):
        engine = self._engine('A3V3-A')
        try:
            state = engine._load()
            ids = [int(x['partner_id']) for x in state['partners'][:3]]
            self.assertEqual(len(ids), 3)
            teams = [[{'partner_id': pid, 'pos': 1}] for pid in ids]
            saved = engine.save_pvp_arena3v3_teams(teams)
            self.assertEqual(saved['team_count'], 3)
            self.assertEqual(sum(len(x) for x in engine.pvp_arena3v3_teams()), 3)
            with self.assertRaises(GameError):
                engine.save_pvp_arena3v3_teams([[{'partner_id':ids[0],'pos':1}],
                                                [{'partner_id':ids[0],'pos':1}],
                                                [{'partner_id':ids[2],'pos':1}]])
            self.assertEqual(sum(len(x) for x in engine.pvp_arena3v3_teams()), 3)
        finally:
            engine.close()

    def test_first_open_awards_original_ticket_once_without_robot_roster(self):
        engine = self._engine('A3V3-A', tickets=0)
        try:
            first = engine.ensure_pvp_arena3v3()
            amount = int(first['tickets'])
            self.assertGreaterEqual(amount, 1)
            state = engine._load()
            self.assertEqual(state['arena3v3']['teams'], [])
            second = engine.ensure_pvp_arena3v3()
            self.assertEqual(second['tickets'], amount)
            self.assertNotIn('rivals', engine._load()['arena3v3'])
        finally:
            engine.close()

    def test_active_series_blocks_switching_to_another_pvp_mode(self):
        match = self._match()
        status_3v3 = live_service.pvp_status('A3V3-A', 'S1', 'arena3v3')
        self.assertEqual(status_3v3['status'], 'matched')
        self.assertEqual(status_3v3['match']['id'], match['id'])
        self.assertEqual(live_service.pvp_status('A3V3-A', 'S1', 'team')['status'], 'idle')
        with self.assertRaisesRegex(ValueError, 'trận PvP ở chế độ khác'):
            live_service.enqueue_pvp('A3V3-A', 'S1', 'Alpha', 'team', 18000)

    def test_player_has_only_one_waiting_pvp_mode(self):
        first = live_service.enqueue_pvp('A3V3-A', 'S1', 'Alpha', 'arena', 18000)
        self.assertEqual(first['status'], 'waiting')
        second = live_service.enqueue_pvp('A3V3-A', 'S1', 'Alpha', 'arena3v3', 18000)
        self.assertEqual(second['status'], 'waiting')
        db = live_service._db()
        try:
            rows = db.execute("SELECT mode FROM pvp_queue WHERE uid=? AND server_id=? AND status='waiting'",
                              ('A3V3-A', 'S1')).fetchall()
            self.assertEqual([row['mode'] for row in rows], ['arena3v3'])
        finally:
            db.close()

    def test_15_day_server_season_ranking_and_native_rank_reward(self):
        from gxb2 import arena3v3
        db=live_service._db()
        import time
        now=int(time.time())
        db.execute("UPDATE worlds SET created_at=? WHERE server_id='S1'",(now-31*86400,))
        db.commit(); db.close()
        current=live_service.pvp_season_id('arena3v3','S1',now)
        previous=live_service.previous_pvp_season_id('arena3v3','S1',now)
        self.assertNotEqual(current,previous)
        db=live_service._db()
        db.execute("""INSERT INTO pvp_ratings(uid,server_id,mode,season_id,rating,wins,losses,matches,updated_at)
                      VALUES(?,?,?,?,?,?,?,?,?)""",('A3V3-A','S1','arena3v3',previous,1810,8,1,9,now-10))
        db.execute("""INSERT INTO pvp_ratings(uid,server_id,mode,season_id,rating,wins,losses,matches,updated_at)
                      VALUES(?,?,?,?,?,?,?,?,?)""",('A3V3-B','S1','arena3v3',previous,1500,5,4,9,now-9))
        db.commit(); db.close()
        board=live_service.pvp_rating_board('arena3v3',season_id=previous,server_id='S1')
        self.assertEqual(board[0]['uid'],'A3V3-A')
        status=live_service.pvp_season_claim_status('A3V3-A','S1','arena3v3')
        self.assertEqual(status['season_id'],previous)
        self.assertEqual(status['rank'],1)
        self.assertEqual(status['reward'],arena3v3.arena.pairs(arena3v3.rank_award(1)['season_awards']))
        claimed=live_service.claim_pvp_season_reward('A3V3-A','S1','Alpha','arena3v3')
        self.assertTrue(claimed['eligible'])
        self.assertEqual(live_service.mailbox('A3V3-A','S1')[-1]['attachments'],status['reward'])
        with self.assertRaisesRegex(ValueError,'đã nhận'):
            live_service.claim_pvp_season_reward('A3V3-A','S1','Alpha','arena3v3')


if __name__ == '__main__':
    unittest.main()
