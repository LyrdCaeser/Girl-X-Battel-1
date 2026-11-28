import copy,unittest
from gxb2 import engine, vip

def mkstate(paid=0, pts=1000, used=False):
 return {'items':{'12':pts},'partners':[{'partner_id':1,'table_id':51004}],
         'vip_paid_exp':paid,'egg_starter_used':used,'next_partner_id':2,'server_id':'S1'}

def draw(st):
 e=engine.Engine.__new__(engine.Engine)
 e.now=lambda:1763388000
 e.summon_pool=lambda *args:([{'item':'51004#1','weight':100}],100)
 e.summon_info=lambda state:{}
 e.backpack=lambda state:{}
 e.slot_info=lambda state:{}
 e._dispatch('SUMMON',{'summon_id':9,'times':1},st)
 return st

class EggVIP3(unittest.TestCase):
 def test_original_starter_has_1000_points_and_requires_vip3(self):
  from gxb2.local_config import _FALLBACK
  self.assertEqual(_FALLBACK['starting_resources']['12'],1000)
  self.assertEqual(engine.TABLES['summon']['9']['vip_need'],3)
  self.assertEqual(engine.TABLES['summon']['9']['cost'],'12#1000')
 def test_first_claim_before_vip3_consumes_existing_points(self):
  st=draw(mkstate())
  self.assertEqual(st['items']['12'],0)
  self.assertTrue(st['egg_starter_used'])
  self.assertEqual(len(st['partners']),2)
 def test_second_claim_denied_below_vip3_even_with_refilled_points(self):
  st=mkstate(0,2000,True);before=copy.deepcopy(st)
  with self.assertRaisesRegex(engine.GameError,'VIP 3'):draw(st)
  self.assertEqual(st,before)
 def test_vip3_can_redeem_earned_points(self):
  paid=next(x['need_exp'] for x in vip.LEVELS if int(x['level'])==3)
  st=draw(mkstate(paid,2000,True))
  self.assertEqual(st['items']['12'],1000)
  self.assertEqual(len(st['partners']),2)
 def test_unauthorized_fake_vip_level_rejected(self):
  st=mkstate(0,1000,True);st['vip_level']=25;old=copy.deepcopy(st)
  with self.assertRaisesRegex(engine.GameError,'VIP 3'):draw(st)
  self.assertEqual(st,old)
 def test_no_points_no_free_claim(self):
  st=mkstate(0,0,False);old=copy.deepcopy(st)
  with self.assertRaisesRegex(engine.GameError,'VIP 3'):draw(st)
  self.assertEqual(st,old)
 def test_starter_entitlement_not_double_paid(self):
  st=mkstate(0,1500,False)
  draw(st);self.assertEqual(st['items']['12'],500)
  self.assertEqual(st['next_partner_id'],3)
if __name__=='__main__':unittest.main()
