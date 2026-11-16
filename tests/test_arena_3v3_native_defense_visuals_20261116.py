"""Three-team arena keeps independent teams but the same Goddess cards and stars."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class Arena3v3Visuals(unittest.TestCase):
    def test_three_team_defense_slots_and_roster_have_original_stars(self):
        js=(ROOT/'web/arena-online-native.js').read_text()
        team=js.split('function drawTeams(win,button){',1)[1].split('function currentMode()',1)[0]
        self.assertIn("win.append(el('h3','','Bố Trận 3 Đội'))",team)
        self.assertIn("for(let pos=1;pos<=6;pos++)",team)
        self.assertIn("img(A('arena_3v3_t'+(i+1)),'a3-badge')",team)
        self.assertIn("slot.append(nativeCardStars(hero,'a3-slot-native-stars'))",team)
        self.assertIn("b.append(nativeCardStars(hero,'a3-candidate-native-stars'))",team)
        self.assertNotIn("b.append(el('small','',hero.name",team)
        self.assertNotIn('ar-native-total-stars',team)
        self.assertIn("b.title=(hero.name||'Nữ Thần')",team)

    def test_css_keeps_small_original_emblems_visible(self):
        css=(ROOT/'web/arena3v3.css').read_text()
        for selector in (
            '.a3-win .a3-slot .ar-native-stars',
            '.a3-win .a3-cand .ar-native-stars',
            '.a3-win .a3-slot .ar-native-stars .gu-star',
            '.a3-win .a3-cand .ar-native-stars .gu-emblem',
        ):
            self.assertIn(selector,css)
        self.assertIn('object-fit:contain!important',css)
        self.assertIn('position:absolute;bottom:0;left:0;right:0;z-index:8',css)
        html=(ROOT/'web/index.html').read_text()
        self.assertIn('/arena-online-native.js?v=20261116-defense3v3-r8',html)
        self.assertIn('/arena3v3.css?v=20261116-defense3v3-r7',html)

    def test_saves_are_separate_from_one_vs_one_defense(self):
        js=(ROOT/'web/arena-online-native.js').read_text()
        self.assertIn("post('/api/pvp/arena3v3/teams',{teams})",js)
        self.assertIn("post('/api/pvp/defense',{formation})",js)
        self.assertIn("panel=mode==='arena3v3'?'teams':'defense'",js)
        backend=(ROOT/'gxb2/engine.py').read_text()
        self.assertIn("state.setdefault('arena3v3', {})['teams'] = clean",backend)
        self.assertIn("state['pvp_defense'] = clean",backend)

if __name__=='__main__': unittest.main()
