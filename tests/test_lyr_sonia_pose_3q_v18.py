"""QA-only: approved Lyr Sonia three-quarter-right battle stance contracts."""
from pathlib import Path
import hashlib
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
POSE = ROOT / "docs/lyr-sonia/pose_3q_v18"
SPEC = ROOT / "docs/lyr-sonia/character-v1.json"
SHA_WEBP = "7a1a336b75238d0116fe3410d285fb7c2d5f4d526c8caed1a33f08529da01a8e"


class ThreeQuarterRightBattleStanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads((POSE / "model.json").read_text(encoding="utf8"))
        cls.spec = json.loads(SPEC.read_text(encoding="utf8"))

    def test_attachment_is_approved_three_quarter_right_not_front(self):
        m = self.model
        self.assertEqual(m["skeleton"]["spine"], "3.6.37")
        self.assertEqual(m["slots"][0]["name"], "combat_stance")
        self.assertEqual(m["slots"][0]["attachment"], "three_quarter_right")
        self.assertEqual(list(m["skins"]["default"]["combat_stance"]), ["three_quarter_right"])
        self.assertIn("front_right_45", self.spec["character"]["visual"]["directions"])

    def test_texture_and_atlas_match(self):
        p = POSE / "lyr_sonia_battle_3q_right.webp"
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), SHA_WEBP)
        atlas = (POSE / "model.atlas").read_text(encoding="utf8")
        self.assertIn("lyr_sonia_battle_3q_right.webp", atlas)
        self.assertIn("three_quarter_right", atlas)
        self.assertIn("size: 234,398", atlas)

    def test_no_fake_gameplay_animations_or_movement(self):
        m = self.model
        self.assertEqual(set(m["animations"]), {"battle_idle", "battle_pose_approved"})
        self.assertNotIn("attack", m["animations"])
        self.assertNotIn("skill", m["animations"])
        self.assertNotIn("move", m["animations"])
        self.assertNotIn("run", m["animations"])
        self.assertTrue(self.spec["combat"]["formation_position_fixed"])
        self.assertFalse(self.spec["integration"]["enabled"])

    def test_static_pose_not_misrepresented_as_rig(self):
        m = self.model
        self.assertEqual(len(m["bones"]), 2)
        self.assertEqual(len(m["slots"]), 1)
        idle = m["animations"]["battle_idle"]
        self.assertEqual(
            [f["angle"] for f in idle["bones"]["combat_anchor"]["rotate"]],
            [0, 0],
        )


if __name__ == "__main__":
    unittest.main()
