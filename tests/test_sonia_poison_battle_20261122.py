"""Read-only synthetic GXB3 original LuaJIT fight with five enemy positions."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from gxb2.engine import Engine
from gxb2.battle import simulate, ONLINE_BATTLE_ID, normalize_online_seed

class SoniaPoisonBattleTest(unittest.TestCase):
    def test_five_target_native_lua_report(self):
        with TemporaryDirectory(prefix='gxb3-sonia-poison-qa-') as d:
            e=Engine(Path(d)/'qa.sqlite3')
            try:
                starter=dict(e.pvp_team_snapshot()['team'][0])
                allies=[dict(starter,table_id=758001,initMp=100)]
                enemies=[dict(starter,table_id=42001,pos=i+1) for i in range(5)]
                r=simulate(allies,enemies,ONLINE_BATTLE_ID,
                           normalize_online_seed(12345),max_round=2)
                self.assertIn(r['isWin'],(0,1))
                sonia_frames=[f for f in r['frames'] if f.get('pos')==1]
                self.assertIn(75800101,{f['skill_id'] for f in sonia_frames})
                skill_effects=[b for f in sonia_frames if f['skill_id']==75800101
                               for b in f.get('buffs',[]) if isinstance(b,dict)]
                self.assertTrue(any(b.get('table_id')==1758018 for b in skill_effects),
                                'Original Lua must execute the new knife hit')
                hits=[int(b['pos']) for b in skill_effects
                      if b.get('table_id')==1758018]
                self.assertLessEqual(len(hits),5)
                self.assertEqual(len(hits),len(set(hits)))
                self.assertTrue(all(7<=p<=11 for p in hits))
                shields=[b for b in skill_effects if b.get('name')=='hpShield' and
                         b.get('buffOn')==5]
                self.assertTrue(shields,'Sonia must generate native shield updates')
                self.assertGreater(shields[0].get('shield',0),0)
                self.assertGreater(shields[0].get('shieldCost',0),0)
                # An actual surviving enemy demonstrates real damage-over-time
                # values, five distinct hits and genuine buff expiration.
                survivors=[dict(starter,table_id=42001,pos=i+1,
                                gm_bonus={'hp':7000}) for i in range(5)]
                longer=simulate(allies,survivors,ONLINE_BATTLE_ID,
                                normalize_online_seed(45678),max_round=5)
                first_active=next(f for f in longer['frames']
                                  if f['pos']==1 and f['skill_id']==75800101)
                first_hits=[b for b in first_active.get('buffs',[])
                            if b.get('table_id')==1758018]
                self.assertEqual(len(first_hits),5,
                                 'Exactly five poison knives must hit separate enemies')
                self.assertEqual(len({b['pos'] for b in first_hits}),5)
                initial_poison=[b for b in first_active.get('buffs',[])
                                if b.get('table_id')==1758019 and b.get('buffOn')==0]
                self.assertEqual(len(initial_poison),5)
                ticks=[(f,b) for f in longer['frames']
                       for b in (f.get('buffs',[]) or [])
                       if isinstance(b,dict) and
                       b.get('table_id')==1758019 and b.get('buffOn')==2]
                self.assertTrue(ticks,'Actual Lua poison damage must tick in later rounds')
                self.assertTrue(all(b['value']<0 for _,b in ticks))
                self.assertTrue(all(b['f_pos']==1 for _,b in ticks))
            finally:
                e.close()

if __name__=='__main__':
    unittest.main()
