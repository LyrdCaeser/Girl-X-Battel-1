"""3v3 portraits must fill the card without distorting artwork or native star images."""
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class TeamPortraits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css=(ROOT/'web/arena3v3.css').read_text()
        cls.js=(ROOT/'web/arena-online-native.js').read_text()
        cls.html=(ROOT/'web/index.html').read_text()
    def test_slots_and_candidates_scale_only_the_portrait_image(self):
        css=self.css
        for container in ('.a3-slot','.a3-cand'):
            self.assertIn(container+'>.portrait{display:block;width:100%!important;height:100%!important',css)
            self.assertIn(container+'>.portrait>.portrait-image{display:block;width:100%!important;height:100%!important;object-fit:contain!important;object-position:center center!important}',css)
        self.assertNotIn('.a3-slot img,.a3-slot canvas{width:100%;height:100%;object-fit:cover}',css)
        self.assertNotIn('.a3-cand img{width:100%;height:100%;object-fit:cover}',css)
        self.assertNotIn('.a3-cand>*:first-child{width:100%;height:100%;object-fit:cover',css)
    def test_stars_are_not_stretched_or_hidden(self):
        css=self.css
        self.assertIn('.a3-win .a3-slot .ar-native-stars',css)
        self.assertIn('.a3-win .a3-cand .ar-native-stars',css)
        self.assertIn('object-fit:contain!important;flex:none;',css)
        self.assertIn('.a3-win .a3-slot .ar-native-stars .gu-emblem',css)
        self.assertIn('.a3-win .a3-cand .ar-native-stars .gu-star',css)
        self.assertIn("slot.append(nativeCardStars(hero,'a3-slot-native-stars'))",self.js)
        self.assertIn("b.append(nativeCardStars(hero,'a3-candidate-native-stars'))",self.js)
        self.assertNotIn('ar-native-total-stars',self.js)
    def test_3v3_has_three_independent_teams_and_new_css_revision(self):
        self.assertIn("teams.forEach((team,i)=>",self.js)
        self.assertIn("post('/api/pvp/arena3v3/teams',{teams})",self.js)
        self.assertIn('/arena3v3.css?v=20261116-portrait-contained-r8',self.html)
        self.assertNotIn('/arena3v3.css?v=20261116-defense3v3-r7',self.html)

if __name__=='__main__':unittest.main()
