"""SQLite-only S4 Wish GM code grants; production Neon never used."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2 import database, live_service, giftcodes, s4_exclusive
from gxb2.engine import Engine

class S4GMGiftcodeTests(unittest.TestCase):
    def setUp(self):
        if database.is_postgres():
            self.skipTest('SQLite-only tests')
        td=tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.base=Path(td.name)
        raw=database.connect
        self.stub=patch.object(live_service,'_db',lambda:raw(self.base/'gm_gift.sqlite3','live'))
        self.stub.start()
        self.addCleanup(self.stub.stop)
        old=giftcodes._READY
        giftcodes._READY=False
        self.addCleanup(setattr,giftcodes,'_READY',old)
        live_service.create_world('S4',s4_exclusive.NAME)
        live_service.register_player('USER-A','S4','Người A')
        live_service.register_player('USER-B','S4','Người B')
        live_service.register_player('USER-A','S1','Người A gốc')
        self.guard=patch.multiple(s4_exclusive,ensure_vip15=lambda uid,server_id:3100000,
                                  ensure_key_claimed=lambda uid,server_id:True,
                                  permanent_access=lambda uid:True,
                                  ensure_access=lambda uid,server_id:'permanent')
        self.guard.start()
        self.addCleanup(self.guard.stop)

    def test_create_redemption_s4_only_once_per_uid(self):
        created=giftcodes.create_s4_exclusive('GM',code='S4WISH-TEST',max_uses=0,days=30)
        self.assertEqual(created['server_id'],'S4')
        self.assertEqual(created['rewards'],{s4_exclusive.KEY:2})
        self.assertEqual(created['effect'],'s4_wish_bundle')
        self.assertTrue(created['unlimited'])
        with self.assertRaisesRegex(ValueError,'không áp dụng|dành cho S4'):
            giftcodes.redeem(created['code'],'USER-A','S1')
        self.assertFalse(live_service.mailbox('USER-A','S1'))
        result=giftcodes.redeem(created['code'],'USER-A','S4')
        self.assertTrue(result['ok'])
        rows=live_service.mailbox('USER-A','S4')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['attachments'],{s4_exclusive.KEY:2})
        with self.assertRaisesRegex(ValueError,'đã sử dụng'):
            giftcodes.redeem(created['code'],'USER-A','S4')
        self.assertEqual(len(live_service.mailbox('USER-A','S4')),1)

    def test_after_original_welcome_claim_can_use_new_gm_code(self):
        engine=Engine(self.base/'state_A.sqlite3',identity=('USER-A','S4'))
        self.addCleanup(engine.close)
        engine.bind_identity('USER-A','S4','Người A')
        state=engine._load()
        state['s4_exclusive_claimed']=True
        engine._save_profile(state)
        engine.db.commit()
        created=giftcodes.create_s4_exclusive('GM')
        giftcodes.redeem(created['code'],'USER-A','S4')
        code_mail=next(m for m in live_service.mailbox('USER-A','S4') if m['attachments']=={s4_exclusive.KEY:2})
        result=engine.claim_live_mail(code_mail['id'])
        self.assertEqual(result['s4_rewards']['wish_count'],104)
        self.assertEqual(result['s4_rewards']['skin_count'],324)
        self.assertEqual(len(engine._load()['partners']),len(state['partners'])+104)
        with self.assertRaisesRegex(ValueError,'được nhận'):
            engine.claim_live_mail(code_mail['id'])

    def test_gm_code_does_not_consume_original_welcome(self):
        from gxb2.engine import new_state
        state=new_state()
        state['server_id']='S4'
        self.assertFalse(state.get('s4_exclusive_claimed'))
        result=s4_exclusive.grant_bundle(state,2,lambda *args,**kw:666)
        self.assertEqual(result['wish_count'],104)
        self.assertFalse(state.get('s4_exclusive_claimed'))
        original=s4_exclusive.grant_bundle(state,1,lambda *args,**kw:666)
        self.assertEqual(original['wish_count'],0)
        self.assertTrue(state['s4_exclusive_claimed'])

    def test_vip_and_key_both_required(self):
        created=giftcodes.create_s4_exclusive('GM')
        with patch.object(s4_exclusive,'ensure_vip15',side_effect=ValueError('VIP 15')):
            with self.assertRaisesRegex(ValueError,'VIP 15'):
                giftcodes.redeem(created['code'],'USER-A','S4')
        with patch.object(s4_exclusive,'ensure_key_claimed',side_effect=ValueError('Chìa Khóa')):
            with self.assertRaisesRegex(ValueError,'Chìa Khóa'):
                giftcodes.redeem(created['code'],'USER-A','S4')
        self.assertEqual(giftcodes.list_codes()[0]['used_count'],0)
        self.assertEqual(live_service.mailbox('USER-A','S4'),[])

    def test_global_max_use_cap_and_revoke(self):
        c=giftcodes.create_s4_exclusive('GM',max_uses=1,days=3)
        giftcodes.redeem(c['code'],'USER-A','S4')
        with self.assertRaisesRegex(ValueError,'hết lượt'):
            giftcodes.redeem(c['code'],'USER-B','S4')
        d=giftcodes.create_s4_exclusive('GM')
        giftcodes.revoke(d['code'],'GM')
        with self.assertRaisesRegex(ValueError,'đã bị khóa'):
            giftcodes.redeem(d['code'],'USER-B','S4')

if __name__=='__main__':
    unittest.main()
