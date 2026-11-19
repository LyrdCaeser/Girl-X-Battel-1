"""S4 owner-only GM gifts; all writes are isolated SQLite test fixtures."""
import inspect
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2 import database, live_service, giftcodes, s4_trial_gm_gifts as gifts
from gxb2 import s4_exclusive, s4_trial, wish, goddess_gifts, skins, dress
from gxb2.engine import Engine
from server import HTTPHandler


class S4TrialGMGiftsTests(unittest.TestCase):
    def setUp(self):
        if database.is_postgres():
            self.skipTest('Do not write test mails into production Neon')
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base=Path(temp.name)
        old=live_service.DB_PATH
        live_service.DB_PATH=self.base/'live.sqlite3'
        self.addCleanup(setattr,live_service,'DB_PATH',old)
        for sid,name in [('S1','Thường 1'),('S2','Thường 2'),('S4','Độc Quyền')]:
            if sid!='S1':
                live_service.create_world(sid,name)
        live_service.register_player('GM-GIFT-UID','S1','Người Thử')
        live_service.register_player('OTHER-UID','S1','Người Khác')
        self.request_id='ecabafef'+'11'*12

    def issue(self,hours,**opts):
        return gifts.issue('GM-GIFT-UID','S1','Người Thử',hours,
                           opts.pop('request_id',self.request_id),
                           'SUPER-GM',**opts)

    def activate_test_key(self, sent, hours):
        self.assertIsNotNone(sent['key_mail_id'])
        source=Engine(self.base/'s1-player.sqlite3',
                      identity=('GM-GIFT-UID','S1'))
        self.addCleanup(source.close)
        source.bind_identity('GM-GIFT-UID','S1','Người Thử')
        source.claim_live_mail(sent['key_mail_id'])
        # Read the isolated S1 test profile, never the real VPS player paths.
        scope=patch.object(s4_trial,'_all_other_profiles',side_effect=
            lambda uid:[json.dumps(source._load())] if uid=='GM-GIFT-UID' else [])
        scope.start();self.addCleanup(scope.stop)
        activation=source.use_bag_item(str(990050+hours//24))
        self.assertEqual(activation['s4_trial']['hours'],hours)
        self.assertEqual(activation['state']['items'][str(990050+hours//24)],0)
        self.assertEqual(s4_exclusive.access_mode('GM-GIFT-UID'),'trial')
        return source

    def test_24_wish_goddesses_are_exact_native_roster(self):
        ids=gifts.wish_goddesses()
        self.assertEqual(len(ids),24)
        self.assertEqual(len(set(ids)),24)
        self.assertEqual(ids,tuple(goddess_gifts.resolve(x,25)[0]
                                   for x in wish.D['partners']))
        self.assertTrue(set(ids).issubset(set(s4_exclusive._source_goddesses())))

    def test_all_five_tier_packages_and_native_skins_and_outfits(self):
        for hours in (24,48,72,96,120):
            with self.subTest(hours=hours):
                p=gifts.package(hours)
                self.assertEqual(p['hours'],hours)
                self.assertEqual(p['key_item_id'],str(990050+hours//24))
                self.assertEqual(len(p['wish_goddesses']),24)
                self.assertEqual(p['goddess_count'],48 if hours>=96 else 24)
                self.assertEqual(p['random_count'],24 if hours>=96 else 0)
                self.assertEqual(len(p['skin_ids']),24 if hours>=96 else 0)
                self.assertEqual(len(p['outfit_sets']),10 if hours>=96 else 0)
        wish_sources=set(wish.D['partners'])
        wish_can=set(gifts.wish_goddesses())
        for skin_id in gifts.wish_skins():
            row=skins.SKINS[skin_id]
            self.assertTrue(row['model'])
            self.assertTrue(set(row['partners'])&(wish_sources|wish_can))
        pieces=gifts.outfit_pieces()
        self.assertEqual(len(pieces),50)
        self.assertEqual(len(set(pieces)),50)
        for did in pieces:
            self.assertTrue(dress.complete_piece(did))
            self.assertEqual(dress.max_star(did),6)
        with self.assertRaises(ValueError):
            gifts.package(12)

    def test_gm_action_generates_two_uid_scoped_mails_even_without_s4_character(self):
        self.assertIsNone(live_service.player('GM-GIFT-UID','S4'))
        sent=self.issue(96)
        self.assertTrue(sent['sent'])
        self.assertEqual(sent['goddess_count'],48)
        self.assertEqual(sent['skin_count'],24)
        self.assertEqual(sent['outfit_set_count'],10)
        source=live_service.mailbox('GM-GIFT-UID','S1')
        target=live_service.mailbox('GM-GIFT-UID','S4')
        self.assertEqual(len(source),1)
        self.assertEqual(len(target),1)
        self.assertEqual(source[0]['attachments'],{'990054':1})
        self.assertEqual(source[0]['operator'],gifts.OPERATOR)
        self.assertEqual(target[0]['operator'],gifts.OPERATOR)
        mark=target[0]['attachments'][gifts.MARKER]
        self.assertEqual(mark['hours'],96)
        self.assertEqual(mark['wish_goddesses'],list(gifts.wish_goddesses()))
        self.assertEqual(len(mark['extra_goddesses']),24)
        self.assertEqual(len(set(mark['extra_goddesses'])),24)
        self.assertFalse(set(mark['extra_goddesses'])&set(mark['wish_goddesses']))
        self.assertTrue(set(mark['extra_goddesses']).issubset(
            set(s4_exclusive._source_goddesses())))
        self.assertEqual(len(mark['skin_ids']),24)
        self.assertEqual(len(mark['outfit_sets']),10)
        self.assertEqual(live_service.mailbox('OTHER-UID','S1'),[])
        self.assertEqual(live_service.mailbox('OTHER-UID','S4'),[])

    def test_locked_until_activation_and_gift_only_option(self):
        result=self.issue(24,send_key=False)
        self.assertIsNone(result['key_mail_id'])
        self.assertEqual(live_service.mailbox('GM-GIFT-UID','S1'),[])
        self.assertEqual(len(live_service.mailbox('GM-GIFT-UID','S4')),1)
        self.assertEqual(gifts.ready_mails('GM-GIFT-UID'),[])
        with self.assertRaisesRegex(ValueError,'không kèm chìa'):
            self.issue(24,send_key=True)
        self.assertEqual(len(live_service.mailbox('GM-GIFT-UID','S4')),1)

    def test_idempotent_retry_does_not_issue_double_mail_or_reroll(self):
        first=self.issue(120)
        marker=live_service.mailbox('GM-GIFT-UID','S4')[0]['attachments'][gifts.MARKER]
        again=self.issue(120)
        self.assertTrue(again['already_sent'])
        self.assertEqual(first['gift_mail_id'],again['gift_mail_id'])
        self.assertEqual(len(live_service.mailbox('GM-GIFT-UID','S1')),1)
        self.assertEqual(len(live_service.mailbox('GM-GIFT-UID','S4')),1)
        self.assertEqual(live_service.mailbox('GM-GIFT-UID','S4')[0]['attachments'][gifts.MARKER],marker)
        with self.assertRaisesRegex(ValueError,'thời hạn khác'):
            self.issue(96)

    def test_rejects_forged_uid_server_name_and_nonhex_nonce(self):
        failures=[
            ('OTHER-UID','S1','Người Thử',24,self.request_id),
            ('GM-GIFT-UID','S4','Người Thử',24,self.request_id),
            ('GM-GIFT-UID','S1','Sai Tên',24,self.request_id),
            ('GM-GIFT-UID','S2','Người Thử',24,self.request_id),
            ('GM-GIFT-UID','S1','Người Thử',24,'not-valid'),
        ]
        for uid,server,name,hours,req in failures:
            with self.subTest(uid=uid,server=server,name=name,req=req):
                with self.assertRaises(ValueError):
                    gifts.issue(uid,server,name,hours,req,'SUPER GM')
        self.assertEqual(live_service.mailbox('GM-GIFT-UID','S1'),[])
        self.assertEqual(live_service.mailbox('GM-GIFT-UID','S4'),[])

    def test_claim_24_wish_bundle_full_integration_with_original_engine(self):
        sent=self.issue(24)
        self.assertEqual(len(live_service.mailbox('GM-GIFT-UID','S4')),1)
        self.activate_test_key(sent,24)
        live_service.register_player('GM-GIFT-UID','S4','Nhân Vật Mới')
        engine=Engine(self.base/'s4-player.sqlite3',
                      identity=('GM-GIFT-UID','S4'))
        self.addCleanup(engine.close)
        engine.bind_identity('GM-GIFT-UID','S4','Nhân Vật Mới')
        self.assertEqual(live_service.mailbox('GM-GIFT-UID','S4')[0]['status'],'claimed')
        with self.assertRaisesRegex(ValueError,'đã được nhận'):
            engine.claim_live_mail(sent['gift_mail_id'])
        saved=engine._load()
        girls=[p for p in saved['partners']
               if int(p.get('table_id') or 0) in gifts.wish_goddesses()
               and int(p.get('awake') or 0)==15]
        self.assertEqual(len(girls),24)
        self.assertTrue(all(p['lv']==1 and p['equips']==[0]*7 for p in girls))
        self.assertFalse(saved.get('s4_exclusive_claimed'))
        self.assertTrue(saved['s4_trial_reward_claimed'])
        self.assertEqual(s4_exclusive.replay_payload(saved)['wish_count'],24)
        with self.assertRaises(ValueError):
            engine.claim_live_mail(sent['gift_mail_id'])

    def test_claim_96_premium_bundle_48_heroes_24_skins_10_outfits(self):
        sent=self.issue(96)
        self.activate_test_key(sent,96)
        live_service.register_player('GM-GIFT-UID','S4','Nhân Vật Mới')
        engine=Engine(self.base/'s4-player.sqlite3',
                      identity=('GM-GIFT-UID','S4'))
        self.addCleanup(engine.close)
        engine.bind_identity('GM-GIFT-UID','S4','Nhân Vật Mới')
        self.assertEqual(live_service.mailbox('GM-GIFT-UID','S4')[0]['status'],'claimed')
        saved=engine._load()
        girls=[p for p in saved['partners'] if int(p.get('awake') or 0)==15]
        self.assertEqual(len(girls),48)
        self.assertEqual(len(set(p['table_id'] for p in girls)),48)
        self.assertEqual(len(set(gifts.wish_skins())&
                             set(saved['skins']['collected'])),24)
        owned=saved['dress']['owned']
        for did in gifts.outfit_pieces():
            self.assertEqual(owned[str(did)],6)
        self.assertEqual(len([x for x in gifts.outfit_pieces() if saved['dress']['owned'].get(str(x))==6]),50)
        self.assertFalse(saved.get('s4_exclusive_claimed'))
        replay=s4_exclusive.replay_payload(saved)
        self.assertEqual(replay['wish_count'],48)
        self.assertEqual(replay['skin_count'],24)

    def test_regular_gm_key_automatically_generates_matching_s4_reward(self):
        from gxb2 import s4_trial_gm_gifts as gifts
        key_mail=live_service.send_mail(
            'GM-GIFT-UID','S1','Người Thử','GM S4','Chìa thử',
            {'990055':1},'SUPER_GM')
        source=Engine(self.base/'direct-source.sqlite3',
                      identity=('GM-GIFT-UID','S1'))
        self.addCleanup(source.close)
        source.bind_identity('GM-GIFT-UID','S1','Người Thử')
        source.claim_live_mail(key_mail['id'])
        patcher=patch.object(s4_trial,'_all_other_profiles',
            side_effect=lambda uid:[json.dumps(source._load())])
        patcher.start();self.addCleanup(patcher.stop)
        key=source.use_bag_item('990055')['s4_trial']
        self.assertEqual(key['hours'],120)
        self.assertEqual(key['gift_status'],'auto_on_s4_entry')
        pending=live_service.mailbox('GM-GIFT-UID','S4')
        self.assertEqual(len(pending),1)
        self.assertEqual(pending[0]['attachments'][gifts.MARKER]['hours'],120)
        self.assertEqual(len(gifts.ready_mails('GM-GIFT-UID')),1)
        live_service.register_player('GM-GIFT-UID','S4','Nhân Vật Mới')
        target=Engine(self.base/'direct-s4.sqlite3',
                      identity=('GM-GIFT-UID','S4'))
        self.addCleanup(target.close)
        target.bind_identity('GM-GIFT-UID','S4','Nhân Vật Mới')
        self.assertEqual(live_service.mailbox('GM-GIFT-UID','S4')[0]['status'],'claimed')
        self.assertEqual(len([x for x in target._load()['partners']
                              if int(x.get('awake') or 0)==15]),48)
        target.bind_identity('GM-GIFT-UID','S4','Nhân Vật Mới')
        self.assertEqual(len([x for x in target._load()['partners']
                              if int(x.get('awake') or 0)==15]),48)

    def test_private_trial_giftcode_redemption_requires_exact_uid_and_activation(self):
        previous=giftcodes._READY
        giftcodes._READY=False
        self.addCleanup(setattr,giftcodes,'_READY',previous)
        created=giftcodes.create_s4_trial_key(
            'GM-GIFT-UID','S1','Người Thử',72,'SUPER-GM',days=15)
        self.assertEqual(created['hours'],72)
        with self.assertRaisesRegex(ValueError,'UID khác'):
            giftcodes.redeem(created['code'],'OTHER-UID','S1')
        redeemed=giftcodes.redeem(created['code'],'GM-GIFT-UID','S1')
        with self.assertRaisesRegex(ValueError,'đã sử dụng'):
            giftcodes.redeem(created['code'],'GM-GIFT-UID','S1')
        self.assertEqual(live_service.mailbox('GM-GIFT-UID','S4'),[])
        source=Engine(self.base/'giftcode-source.sqlite3',
                      identity=('GM-GIFT-UID','S1'))
        self.addCleanup(source.close)
        source.bind_identity('GM-GIFT-UID','S1','Người Thử')
        source.claim_live_mail(redeemed['mail_id'])
        patcher=patch.object(s4_trial,'_all_other_profiles',
            side_effect=lambda uid:[json.dumps(source._load())])
        patcher.start();self.addCleanup(patcher.stop)
        result=source.use_bag_item('990053')
        self.assertEqual(result['s4_trial']['hours'],72)
        self.assertEqual(len(live_service.mailbox('GM-GIFT-UID','S4')),1)

    def test_forged_marker_cannot_use_normal_gm_mail(self):
        self.issue(96,send_key=False)
        real=live_service.mailbox('GM-GIFT-UID','S4')[0]
        fake=live_service.send_mail('GM-GIFT-UID','S1','Người Thử',
            'Normal GM','Normal item',{'990051':1},'SUPER_GM')
        live_service.register_player('GM-GIFT-UID','S4','Nhân Vật Mới')
        db=live_service._db()
        try:
            db.execute(
              """INSERT INTO mail(id,uid,server_id,character_name,title,body,
                  attachments,status,created_at,operator)
                 VALUES(?,?,?,?,?,?,?,'claimed',?,?)""",
              ('S4TRYG-FAKE','GM-GIFT-UID','S4','Nhân Vật Mới',
               'Forged','Forged',json.dumps(real['attachments']),int(time.time()),
               'SUPER_GM'))
            db.commit()
        finally:db.close()
        state={'uid':'GM-GIFT-UID','server_id':'S4'}
        with self.assertRaisesRegex(ValueError,'không do SUPER GM'):
            gifts.grant(state,real['attachments'][gifts.MARKER],
                        lambda *a,**kw:666,'S4TRYG-FAKE',None)

    def test_owner_only_api_has_two_factor_and_no_client_reward_ids(self):
        source=inspect.getsource(HTTPHandler.do_POST)
        pos=source.index("if path == '/api/admin/s4/trial/send'")
        area=source[pos:source.index("if path == '/api/admin/s4/giftcode/create'",pos)]
        self.assertIn('self.gm_key_authorized()',area)
        self.assertIn('self.admin_authorized()',area)
        self.assertIn('self.rate_limit_player',area)
        self.assertNotIn("data.get('reward')",area)
        self.assertNotIn("data.get('goddess_ids')",area)


if __name__=='__main__':
    unittest.main()
