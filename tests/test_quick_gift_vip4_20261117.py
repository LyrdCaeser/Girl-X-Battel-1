import copy,unittest
from gxb2 import relations,vip

LOVE=1000013
NEUTRAL=1000001
BAD=1000010
def state(vip_exp=3150, love=0, vow=0):
 return {'vip_paid_exp':vip_exp,'items':{str(LOVE):8,str(NEUTRAL):40,str(BAD):10},
         'partners':[{'partner_id':'g1','table_id':51017,'love_point':love,'is_vowed':vow}]}
def quick(s):
 return relations.action(s,{'action':'gift_quick','partner_id':'g1'})

class VIPQuickGift(unittest.TestCase):
 def test_gate_is_server_verified_from_paid_exp(self):
  s=state(3149);s['vip_level']=25
  old=copy.deepcopy(s)
  with self.assertRaisesRegex(ValueError,'VIP 4'):quick(s)
  self.assertEqual(s,old)
  self.assertEqual(vip.level_for(3150),4)
 def test_favourites_then_neutral_and_no_disliked(self):
  s=state()
  r=quick(s)
  self.assertEqual(r['delta'],8*40+40*20)
  self.assertEqual(r['used'],{str(LOVE):8,str(NEUTRAL):40})
  self.assertEqual(s['items'][str(BAD)],10)
  self.assertEqual(s['partners'][0]['love_point'],1120)
 def test_uses_only_one_gift_needed_near_cap(self):
  s=state(love=9990)
  r=quick(s)
  self.assertEqual(r['delta'],10)
  self.assertEqual(r['used'],{str(LOVE):1})
  self.assertEqual(s['items'][str(LOVE)],7)
  self.assertEqual(s['partners'][0]['love_point'],10000)
 def test_no_extra_consumption_at_maximum(self):
  s=state(love=10000);old=copy.deepcopy(s)
  with self.assertRaisesRegex(ValueError,'giới hạn'):quick(s)
  self.assertEqual(old,s)
 def test_vow_cap_12000(self):
  s=state(love=11980,vow=1)
  self.assertEqual(quick(s)['delta'],20)
  self.assertEqual(s['partners'][0]['love_point'],12000)
 def test_disliked_gifts_not_consumed(self):
  s=state(love=0);s['items']={str(BAD):200}
  with self.assertRaisesRegex(ValueError,'Không có quà'):quick(s)
  self.assertEqual(s['items'][str(BAD)],200)
 def test_vip4_normal_gifts_not_debug_items(self):
  s=state(love=0);s['items']={str(NEUTRAL):3,'1':9999999,'2':100000}
  r=quick(s)
  self.assertEqual(r['used'],{str(NEUTRAL):3})
  self.assertEqual(s['items']['1'],9999999)
if __name__=='__main__':unittest.main()
