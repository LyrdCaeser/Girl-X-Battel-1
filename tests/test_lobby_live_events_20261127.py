import unittest
from gxb2 import game_calendar as c, sonia_festival as s

class LobbyLiveEventsTests(unittest.TestCase):
    def test_calendar_is_authoritative_in_all_worlds(self):
        for world in ('S1','S2','S3','S4','S5'):
            for now in (s.START-1,s.START,s.ENDS['shards']-1,s.ENDS['shards'],s.ENDS['stars'],s.ENDS['missions']):
                with self.subTest(world=world,now=now):
                    r=c.lobby_snapshot(world,now)
                    self.assertEqual(r['server_id'],world)
                    self.assertEqual(len({e['key'] for e in r['events']}),len(r['events']))
                    self.assertTrue(all(e['start']<=now<e['end'] for e in r['events']))
                    self.assertEqual({e['festival'] for e in r['events'] if 'festival' in e},{k for k in s.ENDS if s.active(now,k)})
                    self.assertNotIn(167,{e.get('id') for e in r['events']})
                    if world=='S4':
                        self.assertTrue({e['id'] for e in r['events'] if 'id' in e}<=set(r['calendar']['featured_today']['ids']))
                    else:
                        self.assertTrue({e['id'] for e in r['events'] if 'id' in e}<= {e['id'] for e in r['calendar']['events']})
    def test_expiry_replaces_shortcut(self):
        end=s.ENDS['shards']
        before=c.lobby_snapshot('S1',end-1)['events'][:6]
        after=c.lobby_snapshot('S1',end)['events'][:6]
        self.assertIn('sonia:shards',{e['key'] for e in before})
        self.assertNotIn('sonia:shards',{e['key'] for e in after})
        self.assertEqual(len(after),6)
        self.assertTrue({e['key'] for e in after}-{e['key'] for e in before})
    def test_week_rotation(self):
        now=s.START+3*86400
        end=c.periods(now)['week']['end']
        a=c.lobby_snapshot('S1',end-1)
        b=c.lobby_snapshot('S1',end)
        self.assertNotEqual({e['key'] for e in a['events']},{e['key'] for e in b['events']})
