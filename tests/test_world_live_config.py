import tempfile
import unittest
from pathlib import Path

from gxb2 import local_config, world_live_config, events


class WorldLiveConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_state_root = world_live_config.STATE_ROOT
        self.old_local_override = local_config.OVERRIDE_PATH
        world_live_config.STATE_ROOT = Path(self.tmp.name) / "worlds"
        local_config.OVERRIDE_PATH = Path(self.tmp.name) / "local_config.json"

    def tearDown(self):
        world_live_config.STATE_ROOT = self.old_state_root
        local_config.OVERRIDE_PATH = self.old_local_override
        self.tmp.cleanup()

    def test_worlds_are_isolated_and_economy_is_scaled(self):
        cfg = world_live_config.get("S1")
        cfg["shop"]["price_multiplier"] = 0.5
        cfg["shop"]["disabled_shop_ids"] = [7]
        cfg["event_shop"]["price_multiplier"] = 2
        cfg["event_rewards"]["multiplier"] = 3
        cfg["summon_rate"]["star_multiplier"]["5"] = 2
        world_live_config.save("S1", cfg)

        self.assertAlmostEqual(world_live_config.get("S1")["shop"]["price_multiplier"], 0.5)
        self.assertEqual(world_live_config.get("S2")["shop"]["price_multiplier"], 1.0)
        self.assertFalse(world_live_config.shop_enabled("S1", 7))
        self.assertTrue(world_live_config.shop_enabled("S2", 7))
        self.assertEqual(world_live_config.shop_cost(101, "S1"), 51)
        self.assertEqual(world_live_config.event_shop_cost(100, "S1"), 200)
        self.assertEqual(world_live_config.event_reward(10, "S1"), 30)

        row = {"weight": 100, "item": "50001#1"}
        partner = {"50001": {"max_star": 5}}
        self.assertEqual(world_live_config.summon_weight(row, partner, "S1"), 200)
        self.assertEqual(world_live_config.summon_weight(row, partner, "S2"), 100)

    def test_event_toggle_blocks_claim_on_only_one_world(self):
        cfg = world_live_config.get("S1")
        cfg["event_rewards"]["checkin_enabled"] = False
        cfg["event_rewards"]["sevenday_enabled"] = False
        world_live_config.save("S1", cfg)

        state = {"server_id": "S1", "items": {}}
        with self.assertRaises(ValueError):
            events.action(state, {"action": "checkin"}, now=1700000000)
        with self.assertRaises(ValueError):
            events.action(state, {"action": "sevenday"}, now=1700000000)

        other = {"server_id": "S2", "items": {}}
        result = events.action(other, {"action": "checkin"}, now=1700000000)
        self.assertTrue(result["awards"])

    def test_reset_returns_defaults(self):
        cfg = world_live_config.get("S9")
        cfg["event_rewards"]["multiplier"] = 4
        world_live_config.save("S9", cfg)
        self.assertEqual(world_live_config.get("S9")["event_rewards"]["multiplier"], 4)
        reset = world_live_config.reset("S9")
        self.assertEqual(reset["event_rewards"]["multiplier"], 1.0)

    def test_cached_world_config_is_detached_and_invalidates_after_save(self):
        cfg = world_live_config.get("S8")
        self.assertEqual(world_live_config.shop_cost(100, "S8"), 100)
        cfg["shop"]["price_multiplier"] = 50
        self.assertEqual(world_live_config.shop_cost(100, "S8"), 100)
        world_live_config.save("S8", cfg)
        self.assertEqual(world_live_config.shop_cost(100, "S8"), 5000)


if __name__ == "__main__":
    unittest.main()
