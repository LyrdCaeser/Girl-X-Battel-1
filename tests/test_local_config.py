import json
import tempfile
import unittest
from pathlib import Path

from gxb2 import local_config


class LocalConfigTests(unittest.TestCase):
    def setUp(self):
        self.old_override = local_config.OVERRIDE_PATH
        self.tmp = tempfile.TemporaryDirectory()
        local_config.OVERRIDE_PATH = Path(self.tmp.name) / "local_config.json"

    def tearDown(self):
        local_config.OVERRIDE_PATH = self.old_override
        self.tmp.cleanup()

    def test_save_and_reset(self):
        cfg = local_config.get()
        cfg["shop"]["price_multiplier"] = 0.5
        cfg["rewards"]["multiplier"] = 2
        saved = local_config.save(cfg)
        self.assertEqual(saved["shop"]["price_multiplier"], 0.5)
        self.assertEqual(local_config.shop_cost(101), 51)
        self.assertEqual(local_config.scale_reward(25), 50)
        reset = local_config.reset()
        self.assertEqual(reset["shop"]["price_multiplier"], 1.0)

    def test_starting_resources_are_normalized(self):
        cfg = local_config.get()
        cfg["starting_resources"] = {1: 123, "2": 456}
        saved = local_config.save(cfg)
        self.assertEqual(saved["starting_resources"], {"1": 123, "2": 456})

    def test_summon_weight_uses_star_multiplier(self):
        cfg = local_config.get()
        cfg["summon_rate"]["star_multiplier"]["5"] = 3
        local_config.save(cfg)
        row = {"weight": 100, "item": "50001#1"}
        partner = {"50001": {"max_star": 5}}
        self.assertEqual(local_config.summon_weight(row, partner), 300)

    def test_invalid_multiplier_is_rejected(self):
        cfg = local_config.get()
        cfg["rewards"]["multiplier"] = -1
        with self.assertRaises(ValueError):
            local_config.save(cfg)


if __name__ == "__main__":
    unittest.main()
