"""Keep recovered original currency rewards while closing unintended grants."""
import json
import tempfile
import unittest
from pathlib import Path

from gxb2 import campaign, events, local_config, world_live_config
from gxb2.engine import Engine

ROOT=Path(__file__).resolve().parents[1]


class OriginalEconomyGuardTests(unittest.TestCase):
    def test_new_player_has_no_free_gems_or_excess_resources(self):
        with tempfile.TemporaryDirectory(prefix='gxb3-economy-qa-') as folder:
            engine=Engine(Path(folder)/'account.sqlite3',developer=False)
            try:
                state=engine._load()
                defaults=local_config.starting_resources()
                for key in ('1','2','9','33','36'):
                    self.assertEqual(int(state['items'].get(key,0)),int(defaults.get(key,0)))
                self.assertEqual(int(state['items'].get('2',0)),0)
                self.assertEqual(int(state['items'].get('36',0)),10)
            finally:
                engine.close()

    def test_recovered_original_7_day_reward_did_not_get_changed(self):
        source=json.loads((ROOT/'data/recovered/tables/activity_sevendays_awards.json').read_text())
        recovered={int(k):row[1] for k,row in source['rows'].items()}
        active={int(day):row['award'] for day,row in events.SEVENDAY.items()}
        self.assertEqual(recovered,active)
        self.assertEqual(sum(events.pairs(v).get('36',0) for v in active.values()),100)

    def test_recovered_original_monthly_gems_unchanged(self):
        source=json.loads((ROOT/'data/recovered/tables/activity_login.json').read_text())
        saved={int(k):row[1] for k,row in source['rows'].items()}
        actual={day:row['award'] for day,row in events.LOGIN.items()}
        for day in range(1,31):
            self.assertEqual(actual[day],saved[day])
        self.assertEqual(sum(events.pairs(actual[d]).get('2',0) for d in range(1,31)),3100)

    def test_no_summon_or_event_multiplier_above_original_on_production(self):
        self.assertEqual(local_config.get()['rewards']['multiplier'],1.0)
        self.assertEqual(local_config.get()['summon_rate']['star_multiplier']['5'],1.0)
        for sid in ('S1','S2','S3','S4'):
            current=world_live_config.get(sid)
            self.assertEqual(current['event_rewards']['multiplier'],1.0)
            self.assertEqual(current['summon_rate']['star_multiplier']['5'],1.0)

    def test_idle_collection_does_not_award_twice_same_time(self):
        now=1_795_280_000
        state={'max_stage':1,'current_stage':1,
               'items':{'1':0,'3':0,'9':0},'vip':0,
               'hang':{'since':now-3600,'drop_since':now-3600}}
        got=campaign.collect(state,now=now)
        self.assertTrue(got)
        before=state['items'].copy()
        with self.assertRaises(ValueError):
            campaign.collect(state,now=now)
        self.assertEqual(before,state['items'])


if __name__=='__main__':
    unittest.main()
