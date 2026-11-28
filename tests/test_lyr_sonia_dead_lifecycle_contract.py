"""Read-only contract checks for Lyr Sonia's Dead behavior in original GXB 3 engine."""
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "web" / "battle-animation.js"
DOC = ROOT / "docs" / "lyr-sonia" / "dead-sequence-v3.md"

class LyrSoniaDeathContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = ENGINE.read_text(encoding="utf-8")
        cls.doc = DOC.read_text(encoding="utf-8")

    def test_original_engine_single_death_and_revive(self):
        for fragment in ("deadPositions.add(pos)", "if(deadPositions.has(pos))return",
                         "kind==='revive'", "deadPositions.delete(pos)"):
            self.assertIn(fragment, self.engine)

    def test_original_engine_hides_corpse_and_has_completion_fallback(self):
        for fragment in ("figure.state.setAnimation(0,death,false)",
                         "figure.visible=false", "figure.state.addListener(finish)",
                         "setTimeout(", "deathTokens.get(pos)===token"):
            self.assertIn(fragment, self.engine)

    def test_qa_scope_explicit(self):
        for fragment in ("CHƯA ĐẠT", "1,155", "1,55", "2,5 giây", "không thay đổi gameplay"):
            self.assertIn(fragment, self.doc)
        self.assertIn("bóng kép", self.doc)
        self.assertIn("¾ phải", self.doc)

if __name__ == "__main__":
    unittest.main()
