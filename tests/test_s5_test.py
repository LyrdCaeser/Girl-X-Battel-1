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

    def test_owner_early_card(self):
        from gxb2 import auth,live_service
        from tempfile import TemporaryDirectory
        from pathlib import Path
        with TemporaryDirectory() as td,patch.object(auth,'DB_PATH',Path(td)/'auth.sqlite3'),patch.object(live_service,'DB_PATH',Path(td)/'live.sqlite3'):
            db=auth._db()
            db.execute("INSERT INTO accounts(uid,username,email,password_hash,salt,status,created_at,last_login) VALUES(?,?,?,?,?,?,?,?)",
                       ('owner-fixture','ownerqa','owner@example.test','hash','salt','active',1,1))
            db.commit();db.close()
            live_service.register_player('owner-fixture','S1','Owner QA')
            closed=datetime(2026,11,27,12,tzinfo=s5.TZ).timestamp()
            with patch.dict('os.environ',{'GXB3_OWNER_UID':'owner-fixture','GXB3_OWNER_EMAIL':'owner@example.test'}):
                self.assertFalse(s5.early_access('owner-fixture'))
                with self.assertRaises(ValueError):s5.ensure_open('S5',closed,uid='owner-fixture')
                with self.assertRaises(ValueError):s5.issue_early_card(s5.MONTHANH_UID)
                self.assertTrue(s5.issue_early_card('owner-fixture')['issued'])
                self.assertFalse(s5.issue_early_card('owner-fixture')['issued'])
                self.assertFalse(s5.early_access('owner-fixture'))
                live_service.claim_mail(s5.early_mail_id('owner-fixture'),'owner-fixture','S1')
                self.assertTrue(s5.early_access('owner-fixture'))
                self.assertTrue(s5.access_cycle(closed,'owner-fixture')['access_allowed'])
                self.assertEqual(s5.access_cycle(closed,'owner-fixture')['phase'],'locked')
                s5.ensure_open('S5',closed,uid='owner-fixture')
                for uid in (None,s5.MONTHANH_UID,'regular'):
                    self.assertFalse(s5.access_cycle(closed,uid)['access_allowed'])
                    with self.assertRaises(ValueError):s5.ensure_open('S5',closed,uid=uid)
                with patch.dict('os.environ',{'GXB3_OWNER_EMAIL':'different@example.test'}):
                    self.assertFalse(s5.early_access('owner-fixture'))

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

    def test_advanced_reward_all_native_goddesses(self):
        from gxb2 import equipment,souls
        for uid in ('ordinary',s5.MONTHANH_UID):
            st=self.state(uid);s5.grant_welcome(st,1795740000)
            hosts=[p for p in st['partners'] if st['s5_welcome']['hosts'].get(str(p['table_id']))==p['partner_id']]
            for p in hosts:
                pid=p['partner_id']
                self.assertEqual(p['lv'],1)
                plan=s5.advanced_plan(p)
                before=list(p['equips'])
                result=s5.grant_advanced(st,pid)
                self.assertEqual(p['lv'],1)
                self.assertEqual(souls.snapshot(st)['open_lv'],1)
                self.assertEqual(p['souls'],result['souls'])
                self.assertEqual(p['equips'][:4],before[:4])
                self.assertEqual(p['ex_skills'],[plan['elite_max']]*4)
                self.assertEqual(p['equips'][4:6],[plan['treasure'],plan['antique']])
                self.assertEqual(equipment.EQUIP[plan['treasure']]['item_lv'],max(equipment.TIERS))
                self.assertFalse(equipment.EQUIP[plan['antique']].get('artifact_next'))
                records=[souls.store(st)['items'][str(i)] for i in p['souls']]
                self.assertEqual(len(records),5)
                self.assertEqual({souls.E2[str(r['table_id'])]['group'] for r in records[1:]}, {souls.E2[str(plan['souls'][1])]['group']})
                for r in records:
                    self.assertEqual(r['lv'],souls.max_lv(r))
                    self.assertEqual(souls.star(r),6)
                    self.assertEqual(r['owner'],pid)
                self.assertEqual(p['soul_infos'],souls.infos(st,p))
                with self.assertRaises(ValueError):s5.grant_advanced(st,pid)
            self.assertEqual(len(st['s5_welcome']['advanced_claimed']),len(hosts))
            st['server_id']='S1'
            self.assertEqual(souls.snapshot(st)['open_lv'],souls.OPEN_LV)
            with self.assertRaises(ValueError):souls.action(st,{'action':'equip','partner_id':hosts[0]['partner_id'],'soul_id':hosts[0]['souls'][0]})
            with self.assertRaises(ValueError):s5.grant_advanced(st,hosts[0]['partner_id'])

    def test_job_gear_reward_once_for_existing_character(self):
        from gxb2 import equipment
        state=self.state()
        s5.grant_welcome(state,1795740000)
        jobs=set()
        for host in list(state['partners']):
            if state['s5_welcome']['hosts'].get(str(host['table_id']))!=host['partner_id']:
                continue
            job=equipment.job_of(host)
            jobs.add(job)
            before=dict(state['items'])
            original=list(host['equips'])
            out=s5.grant_gear(state,host['partner_id'])
            self.assertEqual(out['job'],job)
            self.assertEqual(len(out['gear']),4)
            self.assertEqual({equipment.EQUIP[i]['pos'] for i in out['gear']},{1,2,3,4})
            for item in out['gear']:
                self.assertEqual(equipment.EQUIP[item]['job'],job)
                self.assertEqual(equipment.EQUIP[item]['item_lv'],25)
                self.assertEqual(state['items'][str(item)],before.get(str(item),0)+1)
            self.assertEqual(host['equips'],original)
            with self.assertRaises(ValueError):s5.grant_gear(state,host['partner_id'])
        self.assertEqual(jobs,{1,2,3,4,5})
        state['server_id']='S1'
        with self.assertRaises(ValueError):s5.grant_gear(state,host['partner_id'])
        s5.allow_skin_gift('S5','S5')
        for pair in [('S1','S5'),('S5','S1'),('S5','S4')]:
            with self.assertRaises(ValueError):s5.allow_skin_gift(*pair)

    def test_isolation_rules(self):
        for route in ('/api/giftskin/crystal',
                      '/api/giftcode/redeem','/api/order/create',
                      '/api/guild-war/battle'):
            self.assertFalse(s5.restrict_route(route))
        for route in ('/api/friends/duel','/api/pvp/status','/api/pvp/challenge','/api/events/stream',
                      '/api/friends/gift','/api/friends/marriage','/api/profile/photo/upload','/api/profile/photo/delete'):
            self.assertFalse(s5.restrict_route(route))
        state=self.state()
        state['partners'].append({'table_id':s5.SONIA})
        with self.assertRaises(ValueError):s5.enforce_roster(state)
        state['server_id']='S1';s5.enforce_roster(state)
        from gxb2 import live_service,auth
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as td, patch.object(live_service,'DB_PATH',Path(td)/'live.sqlite3'):
            live_service.create_world('S2','Second')
            live_service.create_world('S5',s5.NAME)
            for uid,world in [('A','S1'),('B','S2'),('C','S5')]:
                live_service.register_player(uid,world,uid+' Test')
            self.assertNotIn('C',[p['uid'] for p in live_service.pvp_candidates('A','S1','cross')])
            self.assertNotIn('C',[p['uid'] for p in live_service.pvp_rating_board('cross')])
            with self.assertRaises(ValueError):live_service.challenge_pvp('A','S1','Alpha','cross','C','S5')
            with self.assertRaises(ValueError):live_service.enqueue_pvp('C','S5','Charlie','cross')
            with self.assertRaises(ValueError):auth.verify_gift_recipient('GB3-123456789','Charlie','S5')

    def test_s5_local_pvp_and_character_scope(self):
        from gxb2 import live_service as ls
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as td,patch.object(ls,'DB_PATH',Path(td)/'live.sqlite3'):
            ls.create_world('S5',s5.NAME)
            for uid,world in [('A','S1'),('B','S1'),('A','S5'),('B','S5'),('C','S5')]:
                ls.register_player(uid,world,uid+' '+world)
            ordinary=ls.challenge_pvp('A','S1','A S1','arena','B','S1')['match']
            self.assertEqual(ls.pvp_status('A','S5','arena')['status'],'idle')
            for mode in ('arena','arena3v3'):
                board=ls.pvp_rating_board(mode,server_id='S5')
                self.assertEqual({p['uid'] for p in board},{'A','B','C'})
                self.assertTrue(all(p['server_id']=='S5' for p in board))
                self.assertEqual({p['uid'] for p in ls.pvp_candidates('A','S5',mode)},{'B','C'})
                match=ls.challenge_pvp('A','S5','A S5',mode,'B','S5')['match']
                self.assertEqual(match['mode'],mode)
                self.assertNotEqual(match['id'],ordinary['id'])
                self.assertEqual(ls.pvp_status('A','S5',mode)['match']['id'],match['id'])
                ls.require_pvp_match_world(match['id'],'A','S5')
                ls.require_pvp_match_world(match['id'],'B','S5')
                with self.assertRaises(ValueError):ls.require_pvp_match_world(match['id'],'A','S1')
                with self.assertRaises(ValueError):ls.require_pvp_match_world(match['id'],'C','S5')
                with self.assertRaises(ValueError):ls.require_pvp_match_world(ordinary['id'],'A','S5')
                if mode=='arena':
                    ls.finish_authoritative_pvp(match['id'],'A',{'uid':'A','server_id':'S5'}, {'uid':'B','server_id':'S5'}, {'isWin':1})
                else:
                    from gxb2 import arena3v3
                    # A native reward item selected by the original reward table.
                    item=str(arena3v3.DATA['dropbox'][0]['item']).split('#')[0]
                    report={'isWin':1,'arena3v3':{'player_rewards':{u:{'reward':{item:1}} for u in ('A','B')}}}
                    ls.finish_authoritative_pvp(match['id'],'A',{'uid':'A','server_id':'S5'},{'uid':'B','server_id':'S5'},report)
                    self.assertTrue(ls.mailbox('A','S5'))
                    self.assertFalse(ls.mailbox('A','S1'))
                self.assertEqual(ls.pvp_rating('A','S5',mode)['matches'],1)
                self.assertEqual(ls.pvp_rating('A','S1',mode)['matches'],0)
            self.assertEqual(len(ls.pvp_history('A',20,'S5')),2)
            self.assertEqual(len(ls.pvp_history('A',20,'S1')),1)
            self.assertEqual(ls.pvp_status('A','S1','arena')['match']['id'],ordinary['id'])
            with self.assertRaises(ValueError):ls.pvp_candidates('A','S5','cross')
            with self.assertRaises(ValueError):ls.challenge_pvp('A','S5','A S5','cross','B','S1')
            with self.assertRaises(ValueError):ls.challenge_pvp('A','S1','A S1','cross','C','S5')

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
