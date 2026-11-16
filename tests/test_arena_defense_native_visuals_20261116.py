"""Arena and Cross Server defenses use the same original native card as attack."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class DefenseVisuals(unittest.TestCase):
    def test_defense_and_attack_use_identical_native_card_renderer(self):
        js=(ROOT/'web/arena-online-native.js').read_text()
        native=js.split("function nativeCardStars(hero,extraClass=''){",1)[1].split('function drawAttack(',1)[0]
        self.assertIn("GirlUI.stars(n,'card')",native)
        self.assertNotIn('ar-native-total-stars',native)
        defense=js.split('function drawDefense(win,button){',1)[1].split('function drawTeams(',1)[0]
        attack=js.split('function drawAttack(win,button){',1)[1].split('function drawDefense(',1)[0]
        for area in (defense,attack):
            self.assertIn("slot.append(nativeCardStars(hero,",area)
            self.assertIn('b.append(nativeCardStars(hero,',area)
            self.assertNotIn("const meta=el('span','ar-defense-meta')",area)
            self.assertNotIn('ar-defense-slot-stars',area)
            self.assertNotIn("slot.append(el('span','ar-defense-slot-stars'",area)
        self.assertNotIn("slot.append(el('small','',String(pos)))",defense)
        self.assertIn("b.title=(hero.name||'Nữ Thần')",defense)

    def test_all_shared_arena_defense_modes_persist_without_pve_mutation(self):
        js=(ROOT/'web/arena-online-native.js').read_text()
        self.assertIn("['arena','cross','arena3v3']",js)
        self.assertIn("panel=mode==='arena3v3'?'teams':'defense'",js)
        self.assertIn("const r=await post('/api/pvp/defense',{formation})",js)
        css=(ROOT/'web/arena3v3.css').read_text()
        self.assertIn('.ar-defense-candidate:has(.ar-native-stars)',css)
        self.assertNotIn('.ar-defense-slot-stars{',css)
        html=(ROOT/'web/index.html').read_text()
        self.assertIn('/arena-online-native.js?v=20261116-defense-native-r7',html)
        self.assertIn('/arena3v3.css?v=20261116-defense-native-r6',html)

if __name__=='__main__':unittest.main()
