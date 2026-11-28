"""Read-only contract validation for Lyr Sonia; no imports into the game runtime."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "docs/lyr-sonia/character-v1.json"
PARTNERS = ROOT / "data/partner.json"
FX = ROOT / "web/assets/battle-fx/skills.json"


class LyrSoniaBlueprintContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
        cls.partners = json.loads(PARTNERS.read_text(encoding="utf-8"))
        cls.original_fx = json.loads(FX.read_text(encoding="utf-8"))

    def test_unreleased_by_default(self):
        self.assertEqual(self.spec["status"], "QA_ONLY_NOT_IN_GAME")
        self.assertFalse(self.spec["integration"]["enabled"])
        for field in ("create_player_items", "mutate_neon", "migrate_existing_data"):
            self.assertFalse(self.spec["integration"][field])

    def test_chaos_is_new_eighth_faction_and_mage_job_is_native(self):
        char = self.spec["character"]
        self.assertEqual((char["faction"]["id"], char["faction"]["name"]), (8, "Hệ Hỗn Độn"))
        self.assertEqual((char["job"]["id"], char["job"]["name"]), (3, "Pháp Sư"))
        occupied = {int(v.get("group", -1)) for v in self.partners.values() if isinstance(v, dict)}
        self.assertTrue(set(range(1, 8)).issubset(occupied))
        self.assertNotIn(8, occupied, "Faction 8 already occupied: inspect before any integration")
        self.assertEqual(int(self.partners["753019"]["job"]), 3)

    def test_exactly_one_active_and_three_passive_skills(self):
        slots = self.spec["skills"]["slots"]
        self.assertEqual([s["slot"] for s in slots], ["active", "passive_1", "passive_2", "passive_3"])
        self.assertEqual([s["field"] for s in slots],
                         ["act_skill_id", "pas_skill1_id", "pas_skill2_id", "pas_skill3_id"])
        for s in slots:
            self.assertIsNone(s["id"], "Do not invent production skill IDs")
            self.assertIn(s["field"], self.partners["753019"])
        self.assertFalse(self.spec["skills"]["mechanics_approved"])
        self.assertTrue(all(s["effects"] is None for s in slots[1:]))

    def test_original_vfx_sources_are_referenced_not_copied_to_gameplay(self):
        fx_ids = ("75301901", "75500701", "75201701")
        fx_names = self.spec["skills"]["slots"][0]["source_fx"]
        self.assertEqual(fx_names, ["lianhua_hurt02", "yixienamei_hurt02", "monika_hurt03"])
        for skill_id, expected in zip(fx_ids, fx_names):
            self.assertIn(skill_id, self.original_fx)
            content = json.dumps(self.original_fx[skill_id], ensure_ascii=False)
            self.assertIn(expected, content)

    def test_stationary_combat_six_real_directions_and_dead_disappears(self):
        combat = self.spec["combat"]
        self.assertTrue(combat["formation_position_fixed"])
        self.assertEqual(combat["allowed_clips"], ["idle", "attack", "skill", "hurt", "dead"])
        self.assertEqual(combat["forbid_clips_in_combat"], ["move", "run"])
        self.assertTrue(combat["facing"]["use_direction_art"])
        self.assertTrue(combat["facing"]["mirror_only_not_equivalent_to_turning"])
        self.assertEqual(len(self.spec["character"]["visual"]["directions"]), 6)
        self.assertEqual(combat["death"]["after_animation"], "remove_from_battlefield")
        self.assertFalse(combat["death"]["leave_corpse"])
        self.assertEqual(self.spec["character"]["visual"]["spine_version"], "3.6.37")

if __name__ == "__main__":
    unittest.main()
