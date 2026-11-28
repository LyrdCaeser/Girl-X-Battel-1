"""Safe S4 GM trial key tests: no Neon writes, no production credentials."""
import inspect
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2 import s4_trial, s4_exclusive, gm_catalog, live_service, auth, bag_use
from gxb2.engine import Engine, GameError
from server import HTTPHandler


class TrialKeyTests(unittest.TestCase):
    def setUp(self):
        old=s4_exclusive._s4_epoch
        s4_exclusive._s4_epoch=1000
        self.addCleanup(setattr,s4_exclusive,'_s4_epoch',old)

    def test_five_distinct_duration_items_and_gm_catalog(self):
        self.assertEqual(s4_trial.KEY_HOURS,{
            '990051':24,'990052':48,'990053':72,'990054':96,'990055':120})
        items={str(x['id']):x for x in gm_catalog.catalog()['items']}
        for sid,hours in s4_trial.KEY_HOURS.items():
            with self.subTest(sid=sid):
                self.assertEqual(bag_use.describe(sid)['hours'],hours)
                self.assertEqual(bag_use.describe(sid)['kind'],'s4_trial')
                self.assertIn('Chìa Khóa S4 Dùng Thử',items[sid]['name'])
                self.assertEqual(items[sid]['image'],'/s4-exclusive-key.svg')
                self.assertEqual(gm_catalog.validate_gift({sid:1}),{sid:1})
                self.assertIsNone(live_service.social_gift_meta(sid))
        self.assertNotIn('990004',gm_catalog.allowed_gift_ids())
        self.assertFalse(bag_use.describe('990004')['usable'])

    def test_open_hours_exclude_global_s4_lock(self):
        base=1000
        for hours in (24,48,72,96,120):
            with self.subTest(hours=hours):
                exp=s4_trial.trial_end_at(base,hours)
                self.assertEqual(s4_trial.open_seconds_between(base,exp),hours*3600)
                expected=base+hours*3600+(48*3600 if hours>72 else 0)
                self.assertEqual(exp,expected)
        # Activated with 1 open hour left: time pauses for whole 48h rest.
        start=base+71*3600
        end=s4_trial.trial_end_at(start,24)
        self.assertEqual(end,base+(72+48+23)*3600)
        self.assertEqual(s4_trial.open_seconds_between(
            base+73*3600,end),23*3600)
        self.assertEqual(s4_trial.open_seconds_between(
            base+119*3600,end),23*3600)

    def test_activate_consumes_exactly_one_key_and_prevents_reactivation(self):
        state={'uid':'UID-TRIAL','server_id':'S1',
               'items':{'990052':2,'990053':1}}
        with patch.object(s4_trial,'_all_other_profiles',return_value=[]), \
             patch.object(s4_exclusive,'permanent_access',return_value=False):
            info=s4_trial.activate(state,'990052',now=1000)
            self.assertEqual(info['hours'],48)
            self.assertEqual(info['remaining_seconds'],48*3600)
            self.assertEqual(state['items']['990052'],1)
            self.assertEqual(s4_trial.status('UID-TRIAL',now=1000,state=state)['remaining_seconds'],48*3600)
            with self.assertRaisesRegex(ValueError,'đang hoạt động'):
                s4_trial.activate(state,'990053',now=1001)
            self.assertEqual(state['items']['990053'],1)
            future=s4_trial.activate(state,'990053',now=info['expires_at']+1)
            self.assertEqual(future['hours'],72)
            self.assertEqual(state['items']['990053'],0)

    def test_rejects_bad_world_forged_id_permanent_and_locked(self):
        with patch.object(s4_trial,'_all_other_profiles',return_value=[]), \
             patch.object(s4_exclusive,'permanent_access',return_value=False):
            for state in [
                {'uid':'U','server_id':'S4','items':{'990051':1}},
                {'uid':'','server_id':'S1','items':{'990051':1}},
                {'uid':'U','server_id':'S2','items':{}}
            ]:
                with self.assertRaises(ValueError):
                    s4_trial.activate(state,'990051',now=1000)
            with self.assertRaises(ValueError):
                s4_trial.activate({'uid':'U','server_id':'S1','items':{'990004':1}},'990004',1000)
            state={'uid':'U','server_id':'S1','items':{'990051':1}}
            with self.assertRaisesRegex(ValueError,'48 giờ'):
                s4_trial.activate(state,'990051',now=1000+72*3600+1)
            self.assertEqual(state['items']['990051'],1)
        with patch.object(s4_trial,'_all_other_profiles',return_value=[]), \
             patch.object(s4_exclusive,'permanent_access',return_value=True):
            state={'uid':'U','server_id':'S1','items':{'990051':1}}
            with self.assertRaisesRegex(ValueError,'vĩnh viễn'):
                s4_trial.activate(state,'990051',now=1000)
            self.assertEqual(state['items']['990051'],1)

    def test_uid_cross_server_entitlement_persists_and_expires(self):
        raw=[
            json.dumps({'uid':'OTHER','server_id':'S1','s4_trial_expires_at':999999999}),
            json.dumps({'uid':'U','server_id':'S4','s4_trial_expires_at':999999999}),
            json.dumps({'uid':'U','server_id':'S99','s4_trial_expires_at':1000+24*3600}),
        ]
        with patch.object(s4_trial,'_all_other_profiles',return_value=raw), \
             patch.object(s4_exclusive,'permanent_access',return_value=False):
            self.assertTrue(s4_trial.status('U',now=1000)['active'])
            self.assertEqual(s4_exclusive.ensure_access('U','S4',now=1000),'trial')
            self.assertTrue(s4_trial.status('U',now=1000+24*3600-1)['active'])
            self.assertFalse(s4_trial.status('U',now=1000+24*3600)['active'])
            with self.assertRaisesRegex(ValueError,'Dùng Thử'):
                s4_exclusive.ensure_access('U','S4',now=1000+24*3600)
        with patch.object(s4_exclusive,'permanent_access',return_value=True):
            self.assertEqual(s4_exclusive.ensure_access('U','S4',now=1000+2000000),
                             'permanent')

    def test_engine_inventory_use_transactional_and_once_only(self):
        with tempfile.TemporaryDirectory() as temp:
            engine=Engine(Path(temp)/'player.sqlite3',identity=('UID-TEMP','S1'))
            self.addCleanup(engine.close)
            engine.bind_identity('UID-TEMP','S1','Nhân vật thử')
            state=engine._load()
            state['items']['990055']=1
            engine._save_profile(state);engine.db.commit()
            with patch.object(s4_trial,'_all_other_profiles',return_value=[]),\
                 patch.object(s4_exclusive,'permanent_access',return_value=False):
                response=engine.use_bag_item('990055')
                self.assertEqual(response['used'],{'item_id':990055,'count':1})
                self.assertEqual(response['s4_trial']['hours'],120)
                self.assertEqual(response['state']['items']['990055'],0)
                with self.assertRaisesRegex(GameError,'Không có Chìa'):
                    engine.use_bag_item('990055')
                with self.assertRaisesRegex(GameError,'chỉ được dùng một'):
                    engine.use_bag_item('990055',count=2)
            self.assertEqual(engine._load()['s4_trial_key_hours'],120)

    def test_gm_mail_claim_grants_exact_item_only_on_target_server(self):
        with tempfile.TemporaryDirectory() as temp:
            original=live_service.DB_PATH
            live_service.DB_PATH=Path(temp)/'s4-gm-live.sqlite3'
            try:
                live_service.register_player('GM-KEY-RECIPIENT','S1','Người Chơi')
                live_service.register_player('OTHER','S1','Người Khác')
                engine=Engine(Path(temp)/'S1-player.sqlite3',
                              identity=('GM-KEY-RECIPIENT','S1'))
                engine.bind_identity('GM-KEY-RECIPIENT','S1','Người Chơi')
                try:
                    keys={str(s):1 for s in range(990051,990056)}
                    validated=gm_catalog.validate_gift(keys)
                    receipt=live_service.send_mail(
                        'GM-KEY-RECIPIENT','S1','Người Chơi','Quà thử S4',
                        'Cảm ơn đã ủng hộ GXB 3',validated,'SUPER_GM')
                    self.assertEqual(live_service.mailbox('OTHER','S1'),[])
                    self.assertEqual(live_service.mailbox('GM-KEY-RECIPIENT','S4'),[])
                    response=engine.claim_live_mail(receipt['id'])
                    for key in s4_trial.KEY_IDS:
                        self.assertEqual(response['state']['items'][key],1)
                    with self.assertRaises(ValueError):
                        engine.claim_live_mail(receipt['id'])
                finally:
                    engine.close()
            finally:
                live_service.DB_PATH=original

    def test_actual_session_trial_create_expiry_and_safe_switch(self):
        from datetime import datetime
        import time
        with tempfile.TemporaryDirectory() as temp:
            old_auth,old_live=auth.DB_PATH,live_service.DB_PATH
            old_epoch=s4_exclusive._s4_epoch
            auth.DB_PATH=Path(temp)/'auth.sqlite3'
            live_service.DB_PATH=Path(temp)/'live.sqlite3'
            s4_exclusive._s4_epoch=None
            try:
                live_service.create_world('S4',s4_exclusive.NAME)
                created=auth.register('Trial_Account01','VerySecurePass123',
                                      'Nhân Vật S1','S1')
                uid=created['account']['uid']
                expiry=int(time.time())+3600
                raw={'uid':uid,'server_id':'S1','s4_trial_expires_at':expiry}
                with patch.object(s4_trial,'_all_other_profiles',
                                  side_effect=lambda _: [json.dumps(raw)]), \
                     patch.object(s4_exclusive,'permanent_access',return_value=False):
                    ctx=auth.create_character(created['token'],'S4','Nhân Vật Thử')
                    self.assertEqual(ctx['account']['server_id'],'S4')
                    self.assertFalse(ctx['s4_access_expired'])
                    self.assertEqual(live_service.mailbox(uid,'S4'),[],
                                     'Trial members must never get VIP15 Wish gifts')
                    raw['s4_trial_expires_at']=int(time.time())-1
                    expired=auth.session(created['token'])
                    self.assertTrue(expired['s4_access_expired'])
                    with self.assertRaisesRegex(ValueError,'Dùng Thử'):
                        auth.login('Trial_Account01','VerySecurePass123','S4')
                    safe=auth.switch_server(created['token'],'S1')
                    self.assertEqual(safe['account']['server_id'],'S1')
                    self.assertFalse(safe['s4_access_expired'])
                    self.assertEqual(live_service.mailbox(uid,'S4'),[])
            finally:
                auth.DB_PATH=old_auth
                live_service.DB_PATH=old_live
                s4_exclusive._s4_epoch=old_epoch

    def test_trial_does_not_grant_vip_wish_bundle(self):
        # S4 welcome still requires permanent access, not merely a trial.
        source=inspect.getsource(auth.login)
        self.assertIn('s4_exclusive.permanent_access(row["uid"])',source)
        source=inspect.getsource(auth.create_character)
        self.assertIn('s4_exclusive.permanent_access(uid)',source)
        from gxb2.engine import Engine as E
        source=inspect.getsource(E.snapshot)
        self.assertIn("s4_exclusive.permanent_access(state['uid'])",source)
        self.assertIn('s4_exclusive.ensure_welcome',source)

    def test_api_returns_423_for_expired_trial_not_s1(self):
        from unittest.mock import Mock
        handler=object.__new__(HTTPHandler)
        handler.send=Mock()
        handler.auth_context=lambda:{'account':{'uid':'U','server_id':'S4'},
                                      's4_access_expired':True}
        with patch.object(s4_exclusive,'cycle',
                          return_value={'server_id':'S4','phase':'open'}):
            self.assertIsNone(HTTPHandler.require_auth(handler))
        self.assertEqual(handler.send.call_args.args[0],423)
        self.assertEqual(handler.send.call_args.args[1]['code'],
                         'S4_TRIAL_EXPIRED')
        handler.send.reset_mock()
        normal={'account':{'uid':'U','server_id':'S1'},
                's4_access_expired':False}
        handler.auth_context=lambda:normal
        self.assertIs(HTTPHandler.require_auth(handler),normal)
        handler.send.assert_not_called()

    def test_gm_mail_only_into_normal_worlds_and_uid_lock(self):
        server_source=inspect.getsource(HTTPHandler.do_POST)
        start=server_source.index("if path == '/api/admin/mail/send':")
        end=server_source.index("if path == '/api/admin/order/review':",start)
        section=server_source[start:end]
        self.assertIn("any(item in s4_trial.KEY_IDS for item in gift)",section)
        self.assertIn("str(data.get('server_id') or '').upper()=='S4'",section)
        self.assertIn('self.gm_key_authorized()',section)
        engine=inspect.getsource(Engine.use_bag_item)
        self.assertIn('pg_advisory_xact_lock',engine)
        self.assertIn('s4_trial.activate(state,item_id)',engine)

    def test_expired_session_redirects_but_does_not_grant_gameplay(self):
        text=inspect.getsource(HTTPHandler.require_auth)
        self.assertIn("ctx.get('s4_access_expired')",text)
        self.assertIn('S4_TRIAL_EXPIRED',text)
        method=inspect.getsource(auth.session)
        self.assertIn('s4_access_expired = True',method)
        self.assertNotIn('except ValueError: return None',method)
        sse=inspect.getsource(HTTPHandler.send_sse)
        self.assertIn('s4_trial_expired',sse)

if __name__=='__main__':
    unittest.main()
