"""GXB3 Sonia: native Elite Skills, real original book costs, isolated account."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from gxb2.engine import Engine, TABLES, EXSKILL

class SoniaEliteTests(unittest.TestCase):
    def test_metadata_and_five_ranks(self):
        hero=TABLES['partner']['758001']
        self.assertEqual(hero['ex_skill'],1)
        self.assertEqual(hero['group'],8)
        self.assertEqual(hero['max_star'],10)
        self.assertEqual(EXSKILL['max'],5)
        self.assertEqual(EXSKILL['cost']['1'],'198#400|199#100')
        self.assertEqual(len(EXSKILL['cost']),5)

    def test_real_native_upgrade_and_books_on_isolated_account(self):
        with TemporaryDirectory(prefix='gxb3-sonia-elite-') as t:
            e=Engine(Path(t)/'only-qa.sqlite3')
            try:
                state=e._load()
                sonia=dict(state['partners'][0],table_id=758001,partner_id=880001,
                           awake=15,grade=6,lv=666,ex_skills=[0,0,0,0])
                state['partners'].append(sonia)
                state['items']['198']=10000000
                state['items']['199']=10000000
                before=(state['items']['198'],state['items']['199'])
                e._dispatch('UPGRADE_PARTNER_EX_SKILL',
                    {'partner_id':880001,'index':1},state)
                self.assertEqual(sonia['ex_skills'],[1,0,0,0])
                self.assertEqual(state['items']['198'],before[0]-400)
                self.assertEqual(state['items']['199'],before[1]-100)
                e._dispatch('UPGRADE_PARTNER_EX_SKILL',
                    {'partner_id':880001,'index':2},state)
                self.assertEqual(sonia['ex_skills'],[1,1,0,0])
                self.assertEqual(state['items']['198'],before[0]-800)
                self.assertEqual(state['items']['199'],before[1]-200)
                for idx in range(1,5):
                    while sonia['ex_skills'][idx-1]<5:
                        e._dispatch('UPGRADE_PARTNER_EX_SKILL',
                            {'partner_id':880001,'index':idx},state)
                self.assertEqual(sonia['ex_skills'],[5,5,5,5])
                with self.assertRaises(Exception):
                    e._dispatch('UPGRADE_PARTNER_EX_SKILL',
                        {'partner_id':880001,'index':1},state)
            finally:
                e.close()

    def test_all_four_elite_slots_survive_native_25_star_battles(self):
        from gxb2.battle import simulate, ONLINE_BATTLE_ID, normalize_online_seed
        with TemporaryDirectory(prefix='gxb3-sonia-elite-luajit-') as t:
            e=Engine(Path(t)/'qa.sqlite3')
            try:
                starter=dict(e.pvp_team_snapshot()['team'][0])
            finally:
                e.close()
            for slot in range(4):
                ranks=[0,0,0,0]
                ranks[slot]=5
                sonia=dict(starter, table_id=758001, lv=666, grade=6,
                           awake=15, ex_skills=ranks, initMp=100)
                enemies=[dict(starter,table_id=41001,pos=i+1,
                              gm_bonus={'hp':100000}) for i in range(5)]
                result=simulate([sonia],enemies,ONLINE_BATTLE_ID,
                                normalize_online_seed(45678),max_round=3)
                self.assertIn(result['isWin'],(0,1))
                self.assertTrue(result['frames'])
                if slot==0:
                    self.assertIn(758001015,
                        [f.get('skill_id') for f in result['frames']])

if __name__=='__main__':unittest.main()
