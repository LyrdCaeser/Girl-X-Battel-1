"""Anima saved sets use owned serial gear IDs, with atomic validation and no consumptions."""
import copy
import unittest
from gxb2 import souls

class SavedPlans(unittest.TestCase):
    def setUp(self):
        self.hero = {'partner_id':101,'lv':250,'souls':[0]*5}
        self.other = {'partner_id':102,'lv':250,'souls':[0]*5}
        self.state={'items':{},'partners':[self.hero,self.other]}
        self.art=int(sorted(souls.E1)[0])
        self.stones={int(r['pos']):int(t) for t,r in sorted(souls.E2.items())}
        self.assertTrue(all(i in self.stones for i in range(2,6)))
        self.sids=[int(souls.new_soul(self.state,self.art))]
        self.sids += [int(souls.new_soul(self.state,self.stones[i])) for i in range(2,6)]
        self.bag=self.state['souls']['items']
        for sid in self.sids:
            self.bag[str(sid)]['owner']=101
        self.hero['souls']=self.sids[:]
        souls.sync(self.state,self.hero)
    def run_action(self,name,**params):
        return souls.action(self.state,{'action':name,'partner_id':101,'plan':1,**params})
    def test_save_restore_and_delete_without_consumption(self):
        before_items=copy.deepcopy(self.bag)
        self.run_action('plan_save')
        self.assertEqual(souls.snapshot(self.state)['plans']['101']['1'],self.sids)
        souls.action(self.state,{'action':'unequip','partner_id':101})
        self.assertEqual(self.hero['souls'],[0]*5)
        self.run_action('plan_apply')
        self.assertEqual(self.hero['souls'],self.sids)
        self.assertTrue(all(r['owner']==101 for r in self.bag.values()))
        self.assertEqual(self.state['items'],{})
        self.assertEqual(set(self.bag),set(before_items))
        self.assertEqual([r['table_id'] for r in self.bag.values()],
                         [r['table_id'] for r in before_items.values()])
        self.assertTrue(self.hero['soul_infos'])
        self.run_action('plan_delete')
        self.assertEqual(souls.snapshot(self.state)['plans'],{})
        with self.assertRaisesRegex(souls.SoulError,'chưa được lưu'):
            self.run_action('plan_apply')
    def test_rejects_gear_equipped_elsewhere_without_any_state_change(self):
        self.run_action('plan_save')
        souls.action(self.state,{'action':'unequip','partner_id':101})
        self.bag[str(self.sids[0])]['owner']=102
        self.other['souls']=[self.sids[0],0,0,0,0]
        before=copy.deepcopy(self.state)
        with self.assertRaisesRegex(souls.SoulError,'Nữ Thần khác'):
            self.run_action('plan_apply')
        self.assertEqual(self.state,before)
    def test_rejects_missing_gear_and_bad_slots_without_mutation(self):
        self.run_action('plan_save')
        souls.action(self.state,{'action':'unequip','partner_id':101})
        del self.bag[str(self.sids[1])]
        before=copy.deepcopy(self.state)
        with self.assertRaisesRegex(souls.SoulError,'không còn'):
            self.run_action('plan_apply')
        self.assertEqual(self.state,before)
        with self.assertRaisesRegex(souls.SoulError,'từ 1 đến 3'):
            self.run_action('plan_save',plan=4)
    def test_cannot_save_empty_equipment_or_silently_grant_items(self):
        souls.action(self.state,{'action':'unequip','partner_id':101})
        before=copy.deepcopy(self.state)
        with self.assertRaisesRegex(souls.SoulError,'ít nhất'):
            self.run_action('plan_save')
        self.assertEqual(self.state['items'],before['items'])
        self.assertEqual(self.hero['souls'],[0]*5)
    def test_snapshot_without_plan_keeps_old_save_compatible(self):
        state={'souls':{'items':{},'next':1,'exp':0},'items':{},'partners':[]}
        self.assertEqual(souls.snapshot(state)['plans'],{})

if __name__=='__main__':unittest.main()
