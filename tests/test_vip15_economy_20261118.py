"""VIP15 pricing and compatibility checks; no production player writes."""
import json
import unittest
from pathlib import Path
from gxb2 import topup, vip

ROOT=Path(__file__).resolve().parents[1]
PACKS={
 'GEMS_250':(250,30000),
 'GEMS_500':(500,60000),
 'GEMS_1000':(1000,120000),
 'GEMS_2500':(2500,300000),
 'GEMS_5000':(5000,600000),
}
class VIP15PricingTests(unittest.TestCase):
    def test_vip_tiers_remain_unchanged(self):
        self.assertEqual(next(r['need_exp'] for r in vip.LEVELS if r['level']==15),3100000)
        self.assertEqual(vip.level_for(3099999),14)
        self.assertEqual(vip.level_for(3100000),15)

    def test_price_and_diamond_quantity_preserved(self):
        for pid,(gems,vnd) in PACKS.items():
            with self.subTest(pid=pid):
                p=topup.package(pid)
                self.assertEqual(p['reward']['2'],gems)
                self.assertEqual(p['price_label'],f'{vnd:,}'.replace(',','.')+' VNĐ')
                self.assertFalse(p['manual_reward'])
                self.assertTrue(p['enabled'])

    def test_gem_packs_have_balanced_uniform_vip_exp_rate(self):
        for pid,(gems,price) in PACKS.items():
            with self.subTest(pid=pid):
                p=topup.package(pid)
                self.assertEqual(p['reward'][vip.VIP_EXP_REWARD_ID],gems*25)
                self.assertEqual(price*6250,p['reward'][vip.VIP_EXP_REWARD_ID]*30000)
                self.assertLessEqual(p['reward'][vip.VIP_EXP_REWARD_ID],
                                     vip.MAX_VIP_EXP_REWARD)

    def test_vip15_total_cost_is_not_cheap_and_not_372_million(self):
        required=next(r['need_exp'] for r in vip.LEVELS if r['level']==15)
        unit_exp=topup.package('GEMS_250')['reward'][vip.VIP_EXP_REWARD_ID]
        minimum_packs=(required+unit_exp-1)//unit_exp
        self.assertEqual(minimum_packs,496)
        self.assertEqual(minimum_packs*30000,14880000)
        major_exp=topup.package('GEMS_5000')['reward'][vip.VIP_EXP_REWARD_ID]
        major_packs=(required+major_exp-1)//major_exp
        self.assertEqual(major_packs,25)
        self.assertEqual(major_packs*600000,15000000)
        self.assertEqual(vip.level_for(24*major_exp),14)
        self.assertEqual(vip.level_for(25*major_exp),15)

    def test_monthly_and_custom_rewards_preserved(self):
        previous=json.loads((ROOT/'data/recovered/tables/giftbag.json').read_text())
        col=previous['keys']['vip_exp']-1
        self.assertEqual(topup.package('MONTHLY_CARD')['reward'][vip.VIP_EXP_REWARD_ID],
                         int(previous['rows']['1'][col]))
        self.assertEqual(topup.package('WEEKLY_CARD')['reward'][vip.VIP_EXP_REWARD_ID],
                         int(previous['rows']['3'][col]))
        for pid in ('CUSTOM','WEEKLY_GIFT','MONTHLY_GIFT'):
            self.assertTrue(topup.package(pid)['manual_reward'])

    def test_preexisting_orders_keep_their_original_snapshotted_vip_exp(self):
        # Pending paid orders made before this economy change must not
        # silently receive a different contract at GM approval.
        from unittest.mock import patch
        import tempfile
        from gxb2 import database, live_service
        with tempfile.TemporaryDirectory() as tmp:
            real_connect=database.connect
            with patch.object(live_service,'_db',
                              side_effect=lambda:real_connect(
                                  Path(tmp)/'test-only-topup.sqlite3','live')):
                # S1 is created by the isolated live SQLite bootstrap.
                live_service.register_player('TEST-PRICING-UID','S1','Người Thử')
                old_package={
                    'id':'GEMS_250','name':'Gói 250 Kim Cương',
                    'price_label':'Liên hệ Zalo để xác nhận giá',
                    'reward':{'2':250,vip.VIP_EXP_REWARD_ID:250},
                    'enabled':True,'manual_reward':False
                }
                with patch.object(topup,'package',return_value=old_package):
                    before=live_service.create_order(
                        'TEST-PRICING-UID','S1','Người Thử','GEMS_250')
                self.assertEqual(before['reward'][vip.VIP_EXP_REWARD_ID],250)
                now=live_service.create_order(
                    'TEST-PRICING-UID','S1','Người Thử','GEMS_250')
                self.assertEqual(now['reward'][vip.VIP_EXP_REWARD_ID],6250)
                approved=live_service.review_order(before['id'],True,
                                                   reviewer='TEST GM')
                self.assertEqual(approved['reward'][vip.VIP_EXP_REWARD_ID],250)
                mail=next(x for x in live_service.mailbox('TEST-PRICING-UID','S1')
                          if x['operator']=='TEST GM')
                self.assertEqual(mail['attachments'][vip.VIP_EXP_REWARD_ID],250)
                self.assertEqual(mail['attachments']['2'],250)
                self.assertEqual(live_service.order(now['id'])['status'],'pending')

    def test_public_catalog_has_consistent_display_price_and_exp(self):
        public={p['id']:p for p in topup.public_catalog()['packages']}
        for pid,(gems,vnd) in PACKS.items():
            x=public[pid]
            self.assertEqual(x['instant_gems'],gems)
            self.assertEqual(x['vip_exp'],gems*25)
            self.assertEqual(x['price_label'],f'{vnd:,}'.replace(',','.')+' VNĐ')

if __name__=='__main__':
    unittest.main()
