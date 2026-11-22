"""Closed Events must not mint currencies, shards or tickets.

Synthetic player state only. S4 special window intentionally keeps all events
open. No migration, player balance changes or real orders.
"""
import copy
import time
import unittest

from gxb2 import point_events, activity_kit, activity_draw, game_calendar


class ClosedEventEconomyTests(unittest.TestCase):
    def setUp(self):
        self.now=int(time.time())
        self.state={'items':{'1':0,'2':500_000,'36':50},
                    'server_id':'S1','partners':[]}
        self.source=list(activity_draw.EVENTS)
        self.closed_points=[i for i in (13,16,20) if not game_calendar.is_open(i,self.now)]
        self.open_points=[i for i in (13,16,20) if game_calendar.is_open(i,self.now)]
        self.closed_kits=[i for i in activity_kit.EVENTS if not game_calendar.is_open(i,self.now)]
        self.closed_draws=[i for i in activity_draw.EVENTS if not game_calendar.is_open(i,self.now)]

    def test_no_reward_or_mutation_for_closed_point_events(self):
        self.assertTrue(self.closed_points)
        for aid in self.closed_points:
            cfg=point_events.CONFIG[str(aid)]
            source=cfg['source']
            before=copy.deepcopy(self.state)
            got=point_events.add(self.state,source,20_000,self.now)
            self.assertEqual(got,{})
            self.assertEqual(self.state,before)

    def test_closed_kit_cannot_grant_daily_supply_or_buy(self):
        self.assertTrue(self.closed_kits)
        for eid in self.closed_kits[:6]:
            before=copy.deepcopy(self.state)
            with self.assertRaises(activity_kit.KitError):
                activity_kit.action(self.state,{'event':eid,'action':'supply'},self.now)
            self.assertEqual(self.state,before)

    def test_closed_draw_cannot_grant_ten_free_pulls(self):
        self.assertTrue(self.closed_draws)
        for eid in self.closed_draws[:6]:
            before=copy.deepcopy(self.state)
            with self.assertRaises(activity_draw.DrawError):
                activity_draw.action(self.state,{'event':eid,'action':'daily'},self.now)
            self.assertEqual(self.state,before)

    def test_snapshots_hide_closed_claim_buttons(self):
        kit=activity_kit.snapshot(self.state,self.now)
        draw=activity_draw.snapshot(self.state,self.now)
        points=point_events.snapshot(self.state,self.now)
        self.assertTrue(all(not kit[str(i)]['open'] and not kit[str(i)]['supply']
                            for i in self.closed_kits))
        self.assertTrue(all(not draw[str(i)]['open'] and not draw[str(i)]['daily_ready']
                            for i in self.closed_draws))
        self.assertTrue(all(not points[str(i)]['open'] for i in self.closed_points))

    def test_s4_keeps_special_all_events_open(self):
        s=copy.deepcopy(self.state);s['server_id']='S4'
        kit=activity_kit.snapshot(s,self.now)
        draw=activity_draw.snapshot(s,self.now)
        points=point_events.snapshot(s,self.now)
        self.assertTrue(all(row['open'] for row in kit.values()))
        self.assertTrue(all(row['open'] for row in draw.values()))
        self.assertTrue(all(row['open'] for row in points.values()))


if __name__=='__main__':
    unittest.main()
