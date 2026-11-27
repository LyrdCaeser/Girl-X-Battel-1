import unittest
from datetime import datetime
from collections import Counter
from unittest.mock import patch
from gxb2 import s5_test as s5, goddess_gifts
from gxb2.engine import Engine, new_state, player_level, TABLES, TOWER

class S5CoreTests(unittest.TestCase):
    def state(self,uid='GB3-111111111'):
        state=new_state(1795740000)
        state.update(uid=uid,server_id='S5')
        return state

    def test_schedule(self):
        for day in (23,28):
            for h,m,expected in [(5,59,'locked'),(6,0,'open'),(8,59,'open'),(9,0,'locked'),
                                 (19,59,'locked'),(20,0,'open'),(22,59,'open'),(23,0,'locked')]:
                now=datetime(2026,11,day,h,m,tzinfo=s5.TZ)
                self.assertEqual(s5.schedule(now.timestamp())['phase'],expected)
        for day in (24,25,26,27,29):
            for hour in (7,21):
                self.assertEqual(s5.schedule(datetime(2026,11,day,hour,tzinfo=s5.TZ).timestamp())['phase'],'locked')

    def test_welcome(self):
        state=self.state()
        out=s5.grant_welcome(state,1795740000)
        self.assertEqual(out['wish_count'],104)
        self.assertEqual(player_level(state),400)
        self.assertEqual(state['max_stage'],530)
        self.assertEqual(state['tower']['max_stage'],len(TOWER))
        self.assertEqual(state['s5_welcome']['skin_choices'],10)
        for p in state['partners'][-104:]:
            self.assertEqual(p['lv'],1)
            self.assertEqual(p['awake'],0)
            self.assertEqual(p['equips'],[0]*7)
            self.assertNotEqual(p['table_id'],s5.SONIA)
        with self.assertRaises(ValueError):s5.grant_welcome(state,1795740000)
        for world in ('S1','S2','S3','S4'):
            another=self.state();another['server_id']=world
            before=dict(another['items'])
            with self.assertRaises(ValueError):s5.grant_welcome(another,1795740000)
            self.assertEqual(another['items'],before)

    def test_sonia_scope(self):
        self.assertNotIn(s5.SONIA,s5.roster('GB3-111111111'))
        self.assertIn(s5.SONIA,s5.roster(s5.MONTHANH_UID))
        with patch.dict('os.environ',{'GXB3_OWNER_UID':'owner-fixture'}):
            self.assertIn(s5.SONIA,s5.roster('owner-fixture'))
        with self.assertRaises(ValueError):s5.awakening_plan('GB3-111111111',s5.SONIA,0)

    def test_every_native_recipe(self):
        e=Engine.__new__(Engine)
        for uid in ('GB3-111111111',s5.MONTHANH_UID):
            for tid in s5.roster(uid):
                for a in range(15):
                    plan=s5.awakening_plan(uid,tid,a)
                    recipe=s5._recipe(tid,a)
                    if recipe.get('awake25'):
                        copies=plan['materials'][:recipe['copies']]
                        fodder=plan['materials'][recipe['copies']:]
                        self.assertEqual(len(fodder),recipe['sacrifices'])
                        for t,aw in copies:
                            self.assertTrue(e.awake25_same_character(TABLES['partner'][str(tid)],TABLES['partner'][str(t)]))
                            self.assertIn(int(TABLES['partner'][str(t)]['max_star'])+aw,(9,10))
                        for t,aw in fodder:
                            self.assertTrue(e.awake25_valid_goddess(TABLES['partner'][str(t)]))
                            self.assertIn(int(TABLES['partner'][str(t)]['max_star'])+aw,range(8,16))
                    else:
                        owned={i:{'table_id':t,'awake':aw} for i,(t,aw) in enumerate(plan['materials'],1)}
                        self.assertEqual(len(e.match_materials(owned,list(owned),recipe['material'],recipe['group'])),len(owned))

    def test_kit_and_skin_choices(self):
        state=self.state();s5.grant_welcome(state,1795740000)
        tid=next(iter(s5.roster(state['uid'])))
        pid=state['s5_welcome']['hosts'][str(tid)]
        out=s5.grant_kit(state,pid)
        self.assertEqual(out['to_star'],11)
        self.assertEqual(next(p for p in state['partners'] if p['partner_id']==pid)['awake'],0)
        with self.assertRaises(ValueError):s5.grant_kit(state,pid)
        catalog=s5.skin_catalog(state['uid'])
        with self.assertRaises(ValueError):s5.choose_skins(state,list(catalog[:11]))
        result=s5.choose_skins(state,list(catalog[:10]))
        self.assertEqual(result['remaining'],0)
        with self.assertRaises(ValueError):s5.choose_skins(state,[catalog[10]])

if __name__=='__main__':unittest.main()
