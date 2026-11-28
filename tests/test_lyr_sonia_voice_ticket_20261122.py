import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LyrSoniaVoiceTicketTests(unittest.TestCase):
    def test_ticket_uses_lyr_sonia_name_everywhere(self):
        chaos = (ROOT / 'gxb2/chaos_summon.py').read_text()
        gm = (ROOT / 'gxb2/gm_catalog.py').read_text()
        banner = json.loads((ROOT / 'web/assets/chaos/lyr_sonia.json').read_text())
        self.assertNotIn('Vé Syrcotte', chaos + gm + json.dumps(banner, ensure_ascii=False))
        self.assertIn('Vé Lyr Sonia', chaos)
        self.assertIn('Vé Lyr Sonia', gm)
        self.assertEqual(banner['ticket']['name'], 'Vé Lyr Sonia')

    def test_voice_pack_covers_every_original_dialogue_type(self):
        pack = json.loads((ROOT / 'web/assets/chaos/lyr_sonia_voice.json').read_text())
        self.assertEqual(pack['id'], 758001)
        self.assertEqual(pack['voice']['lang'], 'vi-VN')
        self.assertEqual({int(row['type']) for row in pack['dialogs']}, set(range(1, 32)))
        self.assertGreaterEqual(len(pack['dialogs']), 40)
        for row in pack['dialogs']:
            self.assertTrue(row['text'].strip())
            self.assertTrue(row['sound'].startswith('tts:758001'))

    def test_frontend_keeps_sonia_utterance_alive(self):
        source = (ROOT / 'web/dates.js').read_text()
        self.assertIn("lyr_sonia_voice.json?v=20261122-r1", source)
        self.assertIn("utterance=new SpeechSynthesisUtterance(bubble)", source)
        self.assertIn("utterance.lang='vi-VN'", source)
        self.assertIn('playGirlVoiceByType', source)


if __name__ == '__main__':
    unittest.main()
