"""Soul Land battle/shield regression, entirely in-memory; no Neon writes."""
import json
import unittest
from pathlib import Path
from gxb2 import soul_land
from gxb2.engine import new_state, TABLES, Engine
from gxb2.souls import catalog
from gxb2.battle import simulate


class SoulLandCombatLoadingTests(unittest.TestCase):
    def test_fast_catalog_preserves_every_used_source_table(self):
        source = catalog()
        slim = {k: source[k] for k in
                ('land', 'land_shop', 'god_text', 'icons', 'names')}
        original_bytes = len(json.dumps(source,ensure_ascii=False).encode('utf8'))
        slim_bytes = len(json.dumps(slim,ensure_ascii=False).encode('utf8'))
        self.assertLess(slim_bytes, original_bytes * .5)
        self.assertEqual(len(slim['land']),150)
        self.assertTrue(slim['god_text'])
        self.assertIn('421',slim['icons'])

    def test_sonia_shield_expiry_heal_has_native_array_normalization(self):
        code = (Path(__file__).resolve().parents[1] /
                'runtime/lua/lib/battle/LyrSoniaPatch.lua').read_text()
        self.assertIn('[1758011]=true', code)
        self.assertIn('type(self.finalNumArray_)',code)
        self.assertIn('self.finalNumArray_ = {tonumber(self.finalNumArray_) or 0}',code)

    def test_three_forts_battle_with_two_elite_sonias(self):
        for f in (1,2,3):
            with self.subTest(fort=f):
                s=new_state()
                starter=dict(s['partners'][0])
                s['partners'] = [
                    dict(starter,partner_id=1,table_id=758001,lv=134,
                         grade=6,awake=15,ex_skills=[0,0,0,0],pos=1),
                    dict(starter,partner_id=2,table_id=758001,lv=666,
                         grade=6,awake=15,ex_skills=[5,5,5,5],pos=2)]
                s['formation']=[{'partner_id':1,'pos':1},
                                {'partner_id':2,'pos':2}]
                s['items']['421']=4
                soul_land.data(s,1795370000)
                before_tickets=s['items']['421']
                stage=soul_land.first_stage(f)
                def combat(battle_id,god_skills):
                    battle=TABLES['battle'][str(battle_id)]
                    enemies=[dict(table_id=int(t),pos=int(p),isMonster=True)
                        for t,p in zip(str(battle['monsters']).split('|'),
                                       str(battle['stands']).split('|'))]
                    result=Engine._simulate(s,
                        [{**p,'pos':i+1} for i,p in enumerate(s['partners'])],
                        enemies,battle_id,4444,None,battle_type=soul_land.BATTLE_TYPE,
                        god_skills=god_skills)
                    self.assertIn(result['isWin'],(0,1))
                    self.assertTrue(result['frames'])
                    return result
                result=soul_land.action(s,{'action':'fight','stage':stage},
                                        now=1795370000,fight=combat)
                self.assertIsInstance(result['win'],bool)
                self.assertGreaterEqual(s['items']['421'],before_tickets-1)
                if not result['win']:
                    self.assertEqual(s['items']['421'],before_tickets)

if __name__=='__main__':
    unittest.main()
