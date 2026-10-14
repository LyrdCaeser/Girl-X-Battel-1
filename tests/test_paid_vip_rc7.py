"""Paid-only VIP EXP must be delivered from verified, single-claim player mail.

Tests are read-only and never touch production Neon or VPS.
"""
import json
import unittest
from pathlib import Path
from gxb2 import vip, topup, gm_catalog

ROOT = Path(__file__).resolve().parents[1]

class PaidVipRC7Tests(unittest.TestCase):
    def test_gameplay_progress_does_not_grant_vip(self):
        progressed = {
            'max_stage': 300, 'items': {'3': 99999999},
            'missions': {'totals': {'popularity': 999999, 'login': 500}},
            'guild_lab': {'levels': {'1': 20}},
        }
        self.assertEqual(vip.exp(progressed), 0)
        self.assertEqual(vip.info(progressed)['level'], 0)
        self.assertEqual(vip.info(progressed)['sources'], {'paid': 0})

    def test_receipt_is_not_inventory_item_and_increases_level_only_once(self):
        state = {'items': {'1': 100}, 'vip_paid_exp': 340}
        attachments = {vip.VIP_EXP_REWARD_ID: 50, '2': 10}
        self.assertEqual(vip.claim_reward(state, attachments), 50)
        self.assertNotIn(vip.VIP_EXP_REWARD_ID, attachments)
        self.assertEqual(state['vip_paid_exp'], 390)
        self.assertEqual(state['vip_level'], vip.level_for(390))
        self.assertEqual(vip.claim_reward(state, attachments), 0)
        self.assertEqual(state['vip_paid_exp'], 390)

    def test_game_original_vip_tiers_preserved(self):
        self.assertEqual(vip.MAX_LEVEL, len(vip.LEVELS)-1)
        self.assertEqual(vip.level_for(0), 0)
        self.assertGreater(vip.level_for(700), vip.level_for(0))

    def test_gm_only_receipt_id_and_pack_validation(self):
        self.assertIn(vip.VIP_EXP_REWARD_ID, gm_catalog.allowed_gift_ids())
        self.assertEqual(gm_catalog.validate_gift({vip.VIP_EXP_REWARD_ID: 100}),
                         {vip.VIP_EXP_REWARD_ID: 100})
        cfg = topup.get()
        ids = {p['id'] for p in cfg['packages']}
        self.assertTrue({'CUSTOM', 'MONTHLY_GIFT','WEEKLY_GIFT','MONTHLY_CARD','WEEKLY_CARD'} <= ids)
        example = topup.validate({'packages':[{
            'id':'VIP_TEST','name':'Thử','price_label':'QTV xác nhận giá',
            'reward':{vip.VIP_EXP_REWARD_ID:150},'manual_reward':False
        }]})
        self.assertEqual(example['packages'][0]['reward'][vip.VIP_EXP_REWARD_ID],150)

    def test_paid_package_amounts_match_archived_game_records(self):
        giftbag=json.loads((ROOT/'data/recovered/tables/giftbag.json').read_text(encoding='utf-8'))
        idx=giftbag['keys']['vip_exp']-1
        pairs={'MONTHLY_CARD':1,'WEEKLY_CARD':3,'GEMS_250':4,'GEMS_500':5,
               'GEMS_1000':6,'GEMS_2500':7,'GEMS_5000':8}
        for package_id,original_id in pairs.items():
            with self.subTest(package_id=package_id):
                configured=topup.package(package_id)
                self.assertEqual(configured['reward'][vip.VIP_EXP_REWARD_ID],
                                 giftbag['rows'][str(original_id)][idx])
        public=topup.public_catalog()['packages']
        self.assertIn('vip_exp',public[0])
        self.assertIn('instant_gems',public[0])

    def test_original_recharge_event_is_real_storefront(self):
        events=(ROOT/'web/events.js').read_text(encoding='utf-8')
        home=(ROOT/'web/app.js').read_text(encoding='utf-8')
        self.assertIn("[2,3,6,24,39,40,184].includes(Number(selected))",events)
        self.assertIn("publicGemPacks.filter",events)
        self.assertIn("GxbPayment?.open(p.id,p.name)",events)
        self.assertIn("EventsHub.openOriginalEvent(184,'home')",home)

    def test_real_original_store_and_mail_ui(self):
        home=(ROOT/'web/home-menus.js').read_text(encoding='utf-8')
        events=(ROOT/'web/events.js').read_text(encoding='utf-8')
        admin=(ROOT/'web/admin.js').read_text(encoding='utf-8')
        self.assertIn("EventsHub.openOriginalEvent(o.event",home)
        self.assertIn("GxbPayment?.open(packages[a.id]",events)
        self.assertIn("gm-topup-vip-exp",admin)
        self.assertIn("'999999991'",home)

if __name__ == '__main__':
    unittest.main()
