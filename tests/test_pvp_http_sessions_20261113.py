"""Two real HTTP sessions + original LuaJIT combat against isolated SQLite.

No production credentials, player profiles, or network services are used.
All game state, authentication, live matches, and cookies stay in a temp dir.
"""
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2 import auth, database, live_service, player_engines
from gxb2.engine import Engine
from server import make_servers


class PvPHttpSessionTests(unittest.TestCase):
    def setUp(self):
        if database.POSTGRES:
            self.skipTest('Never use production PostgreSQL for isolated HTTP tests')
        self.tmp=tempfile.TemporaryDirectory(prefix='gxb3-http-two-sessions-')
        self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name)
        social_cache=patch.object(live_service,'_social_schema_ready',set())
        social_cache.start();self.addCleanup(social_cache.stop)
        connect=database.connect
        for module, path, kind in ((auth,root/'test_auth.sqlite3','auth'),
                                   (live_service,root/'test_live.sqlite3','live')):
            patcher=patch.object(module,'_db',lambda p=path,k=kind: connect(p,k))
            patcher.start();self.addCleanup(patcher.stop)
        names=patch.object(player_engines,'ROOT',root)
        names.start();self.addCleanup(names.stop)
        self.game=Engine(root/'test_developer.sqlite3')
        self.pool=player_engines.PlayerEnginePool()
        self.http,self.tcp=make_servers(self.game,0,0,player_engines=self.pool,trust_proxy=False)
        self.thread=threading.Thread(target=self.http.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.cleanup_http)
        self.port=self.http.server_port
        self.tokens=[]
        for index in range(3):
            status,payload,headers=self.request('POST','/api/auth/register',{
                'username':f'HttpTestPlayer{index}','password':'ExamplePassword123A',
                'character_name':f'PvP Tester {index}','server_id':'S1'})
            self.assertEqual(status,200,payload)
            self.tokens.append(headers['set-cookie'].split(';',1)[0])

    def cleanup_http(self):
        self.http.shutdown();self.http.server_close();self.tcp.server_close()
        self.thread.join(timeout=5)
        self.pool.close();self.game.close()

    def request(self,method,path,body=None,user=None):
        headers={}
        if body is not None: headers['Content-Type']='application/json'
        if user is not None: headers['Cookie']=self.tokens[user]
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=30)
        try:
            conn.request(method,path,None if body is None else json.dumps(body),headers)
            resp=conn.getresponse();raw=resp.read()
            return resp.status,json.loads(raw),dict((k.lower(),v) for k,v in resp.getheaders())
        finally:
            conn.close()

    def call(self,method,path,body=None,user=0):
        status,payload,_=self.request(method,path,body,user)
        self.assertEqual(status,200,f'{method} {path}: HTTP {status}: {payload}')
        return payload

    def test_ios_exclusive_gateway(self):
        from gxb2 import ios_web
        iphone='Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148'
        android='Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/130 Mobile Safari/537.36'
        def req(method,path,ua=iphone,body=None,cookie='',origin=None):
            headers={'User-Agent':ua}
            if body is not None:headers['Content-Type']='application/json'
            if cookie:headers['Cookie']=cookie
            if origin:headers['Origin']=origin
            conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=20)
            try:
                conn.request(method,path,None if body is None else json.dumps(body),headers)
                res=conn.getresponse()
                return res.status,res.read(),{k.lower():v for k,v in res.getheaders()}
            finally:conn.close()
        self.assertEqual(req('GET','/ios-gateway/',android)[0],403)
        self.assertEqual(req('GET','/ios-gateway/api/auth/me',android)[0],403)
        code,body,h=req('GET','/ios-gateway/')
        self.assertEqual(code,200);self.assertIn(b'ios-manifest.webmanifest',body)
        self.assertEqual(h['cache-control'],'no-store')
        self.assertEqual(req('GET','/ios-gateway/play')[0],302)
        self.assertEqual(req('GET','/ios-gateway/api/state')[0],403)
        self.assertEqual(req('POST','/ios-gateway/ios-launch',body={'standalone':False,'touch':5},origin=ios_web.ORIGIN)[0],403)
        self.assertEqual(req('POST','/ios-gateway/ios-launch',body={'standalone':True,'touch':5},origin='https://wrong.example')[0],403)
        code,body,h=req('POST','/ios-gateway/ios-launch',body={'standalone':True,'touch':5},origin=ios_web.ORIGIN)
        self.assertEqual(code,200)
        cookie=h['set-cookie'].split(';',1)[0]
        self.assertIn('HttpOnly',h['set-cookie']);self.assertIn('Secure',h['set-cookie'])
        code,body,h=req('GET','/ios-gateway/play',cookie=cookie)
        self.assertEqual(code,200);self.assertIn(b'viewport-fit=cover',body);self.assertIn(b'/ios-launch.js',body)
        self.assertIn('microphone=(self)',h['permissions-policy'])
        self.assertEqual(req('GET','/ios-gateway/play',android,cookie=cookie)[0],403)
        self.assertEqual(req('GET','/ios-gateway/app.js',cookie=cookie)[0],200)
        self.assertEqual(req('GET','/ios-gateway/api/state',cookie=cookie)[0],401)
        cookie+='; '+self.tokens[0]
        code,body,h=req('GET','/ios-gateway/api/state',cookie=cookie)
        self.assertEqual(code,200);self.assertEqual(json.loads(body)['server_id'],'S1')
        self.assertEqual(req('POST','/ios-gateway/api/pvp/live-status',body={},cookie=cookie,origin=ios_web.ORIGIN)[0],200)
        self.assertEqual(req('POST','/api/pvp/live-status',body={},cookie=self.tokens[0],origin=ios_web.ORIGIN)[0],403)
        self.assertEqual(req('GET','/',android)[0],200)

    def ready_match(self,mode):
        status=self.call('GET',f'/api/pvp/status?mode={mode}',user=0)
        rival=next(row for row in status['candidates'] if row['character_name']=='PvP Tester 1')
        selected=self.call('POST','/api/pvp/challenge',{
            'mode':mode,'target_uid':rival['uid'],'target_server':rival['server_id']},0)
        match=selected['match']
        self.assertEqual(match['status'],'invited')
        mid=match['id']
        self.assertEqual(self.call('POST','/api/pvp/live-status',{},1)['matches'][0]['id'],mid)
        self.assertFalse(self.call('POST','/api/pvp/live-status',{},2)['matches'])
        self.assertNotEqual(self.request('POST','/api/pvp/match/invite',{'match_id':mid,'action':'accept'},0)[0],200)
        self.call('POST','/api/pvp/match/heartbeat',{'match_id':mid,'ready':True},0)
        self.assertEqual(self.call('POST','/api/pvp/match/heartbeat',{'match_id':mid,'ready':True},1)['match']['status'],'invited')
        self.assertNotEqual(self.request('POST','/api/pvp/match/comms',{'match_id':mid,'kind':'text','text':'no'},0)[0],200)
        self.call('POST','/api/pvp/match/invite',{'match_id':mid,'action':'accept'},1)
        self.call('POST','/api/pvp/match/heartbeat',{'match_id':mid,'ready':True},0)
        self.assertEqual(self.call('POST','/api/pvp/match/heartbeat',{'match_id':mid,'ready':True},1)['match']['status'],'active')
        self.assertEqual(self.call('GET',f'/api/pvp/status?mode={mode}',user=1)['pvp']['match']['id'],mid)
        return mid

    def test_world_rankings_authenticated_saved_data_and_isolation(self):
        states=[self.call('GET','/api/state',user=i) for i in (0,1)]
        uids=[st['uid'] for st in states]
        guild=live_service.create_world_guild(uids[0],'S1',states[0]['name'],'Rank HTTP','',0)
        live_service.apply_world_guild(uids[1],'S1',states[1]['name'],guild['id'],0)
        live_service.review_guild_application(uids[0],'S1',uids[1],True)
        db=live_service._db()
        try:
            live_service._ensure_social_tables(db)
            for i,uid in enumerate(uids):
                player=live_service.player(uid,'S1')
                engine=self.pool.get(uid,'S1',player['character_name'])
                saved=engine._load()
                saved['max_stage']=1+i
                saved['tower']={'max_stage':10+i}
                db.execute("INSERT INTO player_profiles(uid,server_id,data,updated_at) VALUES(?,?,?,?) ON CONFLICT(uid,server_id) DO UPDATE SET data=excluded.data",
                           (uid,'S1',json.dumps(saved),1))
            db.commit()
        finally:db.close()
        self.assertEqual(self.request('GET','/api/world-rankings')[0],401)
        for mode in ('power','level','campaign','tower','guild'):
            board=self.call('GET','/api/world-rankings?mode='+mode+'&server_id=S5',user=0)
            self.assertEqual(board['server_id'],'S1')
            self.assertEqual(board['total'],1 if mode=='guild' else 2)
            self.assertTrue(all('uid' not in r and 'data' not in r for r in board['ranking']))
            if mode!='guild': self.assertTrue(all(r['guild_name']=='Rank HTTP' for r in board['ranking']))
            if mode=='campaign': self.assertEqual(board['ranking'][0]['score'],2)
            if mode=='tower': self.assertEqual(board['ranking'][0]['score'],11)
            if mode=='guild': self.assertEqual(board['ranking'][0]['member_count'],2)
        for group in range(1,9):
            board=self.call('GET','/api/world-rankings?mode=faction&group='+str(group))
            self.assertEqual(board['group'],group)
            self.assertTrue(all(r['server_id']=='S1' for r in board['ranking']))
        self.assertEqual(self.request('GET','/api/world-rankings?mode=faction&group=9',user=0)[0],400)
        # Progress changes are visible without a leaderboard cache reset.
        db=live_service._db()
        try:
            r=db.execute('SELECT data FROM player_profiles WHERE uid=? AND server_id=?',(uids[0],'S1')).fetchone()
            saved=json.loads(r['data']);saved['tower']['max_stage']=100
            db.execute('UPDATE player_profiles SET data=? WHERE uid=? AND server_id=?',(json.dumps(saved),uids[0],'S1'));db.commit()
        finally:db.close()
        board=self.call('GET','/api/world-rankings?mode=tower')
        self.assertEqual(board['ranking'][0]['score'],100)
        self.assertEqual(board['my_rank'],1)
        live_service.leave_world_guild(uids[1],'S1')
        board=self.call('GET','/api/world-rankings?mode=power')
        self.assertEqual([r['guild_name'] for r in board['ranking'] if not r['me']],[''])
        self.assertEqual([r['guild_name'] for r in board['ranking'] if r['me']],['Rank HTTP'])

    def test_cross_world_rankings_include_only_public_worlds(self):
        from gxb2 import world_rankings
        st=self.call('GET','/api/state',user=0)
        uid=st['uid']
        saved=self.pool.get(uid,'S1',st['name'])._load()
        for world in ('S2','S3','S4','S5'):
            live_service.create_world(world,'Rank QA '+world)
            live_service.register_player(uid,world,'Rank QA '+world)
        db=live_service._db()
        try:
            live_service._ensure_social_tables(db)
            for world in ('S1','S2','S3','S4','S5'):
                db.execute("INSERT INTO player_profiles(uid,server_id,data,updated_at) VALUES(?,?,?,?) ON CONFLICT(uid,server_id) DO UPDATE SET data=excluded.data",(uid,world,json.dumps(saved),1))
            db.commit()
        finally:db.close()
        live_service.create_world_guild(uid,'S2','Rank QA S2','Rank S2 Only','',0)
        self.assertEqual(self.request('GET','/api/world-rankings?mode=cross')[0],401)
        board=self.call('GET','/api/world-rankings?mode=cross&server_id=S5')
        self.assertEqual(board['worlds'],['S1','S2','S3'])
        self.assertEqual(board['scope'],'cross')
        self.assertEqual(board['total'],3)
        self.assertEqual({r['server_id'] for r in board['ranking']},{'S1','S2','S3'})
        self.assertEqual([r['server_id'] for r in board['ranking'] if r['me']],['S1'])
        self.assertTrue(all(r['score']==r['power'] for r in board['ranking']))
        self.assertEqual({r['server_id']:r['guild_name'] for r in board['ranking']},{'S1':'','S2':'Rank S2 Only','S3':''})
        self.assertEqual(board['my_rank'],next(r['rank'] for r in board['ranking'] if r['me']))
        for world in ('S1','S2','S3','S4','S5'):
            local=world_rankings.ranking(world,uid)
            self.assertEqual(local['scope'],'local')
            self.assertEqual(local['total'],1)
            self.assertEqual(local['ranking'][0]['server_id'],world)
            if world in ('S4','S5'):
                with self.assertRaises(ValueError):world_rankings.ranking(world,uid,'cross')
            else:
                cross=world_rankings.ranking(world,uid,'cross')
                self.assertEqual([r['server_id'] for r in cross['ranking'] if r['me']],[world])
                self.assertEqual([(r['server_id'],r['score'],r['rank']) for r in cross['ranking']],[(r['server_id'],r['score'],r['rank']) for r in board['ranking']])

    def test_authenticated_guild_presence(self):
        first=self.call('GET','/api/state',user=0)
        second=self.call('GET','/api/state',user=1)
        guild=live_service.create_world_guild(first['uid'],'S1',first['name'],'Presence HTTP','',0)
        live_service.apply_world_guild(second['uid'],'S1',second['name'],guild['id'],0)
        live_service.review_guild_application(first['uid'],'S1',second['uid'],True)
        db=live_service._db()
        try:
            db.execute('UPDATE presence SET last_seen=1 WHERE server_id=?',('S1',))
            db.commit()
        finally:db.close()
        self.assertEqual(self.request('GET','/api/presence/heartbeat')[0],401)
        self.assertEqual(self.request('GET','/api/world-guild/members')[0],401)
        members=self.call('GET','/api/world-guild/members',user=0)['members']
        self.assertEqual([m['online'] for m in members],[True,False])
        self.assertEqual([m['level'] for m in members],[first['level'],second['level']])
        self.call('GET','/api/presence/heartbeat',user=1)
        members=self.call('GET','/api/world-guild/members',user=0)['members']
        self.assertTrue(all(m['online'] for m in members))
        self.assertEqual(self.call('GET','/api/world-guild/members',user=2)['members'],[])

    def test_friend_duel_same_world_no_rank_or_ticket_cost(self):
        from gxb2 import s5_test as s
        from datetime import datetime
        live_service.create_world('S5',s.NAME)
        phase=s.schedule(datetime(2026,11,28,6,30,tzinfo=s.TZ).timestamp())
        with patch.object(s,'schedule',return_value=phase):
            for world in ('S1','S5'):
                if world=='S5':
                    for i in (0,1):
                        self.call('POST','/api/auth/create-character',{'server_id':'S5','character_name':'Friend QA '+str(i)},i)
                states=[self.call('GET','/api/state',user=i) for i in (0,1)]
                uid_a,uid_b=[st['uid'] for st in states]
                # SQLite fixtures have separate engine/live stores; mirror the
                # profiles as the production PostgreSQL adapter normally does.
                db=live_service._db()
                try:
                    live_service._ensure_social_tables(db)
                    for uid in (uid_a,uid_b):
                        player=live_service.player(uid,world)
                        engine=self.pool.get(uid,world,player['character_name'])
                        db.execute("INSERT INTO player_profiles(uid,server_id,data,updated_at) VALUES(?,?,?,?) ON CONFLICT(uid,server_id) DO UPDATE SET data=excluded.data",
                                   (uid,world,json.dumps(engine._load()),1))
                    db.commit()
                finally:db.close()

                self.assertNotEqual(self.request('POST','/api/friends/duel',{'target_uid':uid_b},0)[0],200)
                self.call('POST','/api/friends/action',{'action':'request','target_uid':uid_b},0)
                self.call('POST','/api/friends/action',{'action':'accept','target_uid':uid_a},1)
                for i,target in ((0,uid_b),(1,uid_a)):
                    out=self.call('POST','/api/friends/duel',{'target_uid':target},i)
                    self.assertTrue(out['report']['frames'])
                    self.assertTrue(out['report']['display_units'])
                    self.assertTrue(out['report']['map_asset'])
                for i in (0,1):
                    after=self.call('GET','/api/state',user=i)
                    self.assertEqual(after['items'],states[i]['items'])
                    self.assertEqual(after['formation'],states[i]['formation'])
                self.assertFalse(self.call('POST','/api/pvp/live-status',{},0)['matches'])
                self.assertNotEqual(self.request('POST','/api/friends/duel',{'target_uid':uid_a},0)[0],200)

    def test_decline_cancel_expire_invites(self):
        rival=next(row for row in self.call('GET','/api/pvp/status?mode=arena',user=0)['candidates'] if row['character_name']=='PvP Tester 1')
        req={'mode':'arena','target_uid':rival['uid'],'target_server':rival['server_id']}
        m=self.call('POST','/api/pvp/challenge',req,0)['match']
        self.assertEqual(self.call('POST','/api/pvp/match/invite',{'match_id':m['id'],'action':'decline'},1)['match']['status'],'declined')
        self.assertNotEqual(self.request('POST','/api/pvp/match/invite',{'match_id':m['id'],'action':'accept'},1)[0],200)
        self.assertEqual(self.call('GET','/api/pvp/status?mode=arena',user=0)['pvp']['status'],'idle')
        m=self.call('POST','/api/pvp/challenge',req,0)['match']
        self.assertEqual(self.call('POST','/api/pvp/match/invite',{'match_id':m['id'],'action':'cancel'},0)['match']['status'],'cancelled')
        m=self.call('POST','/api/pvp/challenge',req,0)['match']
        db=live_service._db()
        db.execute('UPDATE pvp_matches SET created_at=1 WHERE id=?',(m['id'],));db.commit();db.close()
        self.assertNotEqual(self.request('POST','/api/pvp/match/invite',{'match_id':m['id'],'action':'accept'},1)[0],200)
        self.assertFalse(any(x['id']==m['id'] for x in self.call('POST','/api/pvp/live-status',{},1)['matches']))

    def test_http_auth_cookies_real_pvp_and_replay_access(self):
        status,data,_=self.request('GET','/api/pvp/status?mode=arena')
        self.assertEqual(status,401,data)
        match_id=self.ready_match('arena')
        formation=self.call('GET','/api/state',user=0)['formation']
        result=self.call('POST','/api/pvp/match/battle',{'match_id':match_id,'formation':formation},0)
        self.assertEqual(result['result']['status'],'finished')
        self.assertEqual(self.call('POST','/api/pvp/live-status',{},1)['matches'][0]['status'],'finished')
        msg=self.call('POST','/api/pvp/match/comms',{'match_id':match_id,'kind':'text','text':'Xin chào'},0)
        received=self.call('POST','/api/pvp/match/comms',{'match_id':match_id,'kind':'poll'},1)
        self.assertEqual(received['events'][0]['text'],'Xin chào')
        audio=self.call('POST','/api/pvp/match/comms',{'match_id':match_id,'kind':'audio','mime':'audio/webm;codecs=opus','audio':'GkXfow=='},1)
        received=self.call('POST','/api/pvp/match/comms',{'match_id':match_id,'kind':'poll','after':msg['after']},0)
        self.assertEqual(received['events'][0]['audio'],'GkXfow==')
        self.assertNotEqual(self.request('POST','/api/pvp/match/comms',{'match_id':match_id},2)[0],200)
        replays=[self.call('POST','/api/pvp/match/replay',{'match_id':match_id},i) for i in (0,1)]
        self.assertEqual(replays[0]['play_at'],replays[1]['play_at'])
        views=[r['report'] for r in replays]
        self.assertTrue(views[0]['frames'])
        self.assertEqual(views[0]['isWin'],1-views[1]['isWin'])
        self.assertEqual(len(views[0]['frames']),len(views[1]['frames']))
        self.assertTrue(all(1<=row['pos']<=12 for row in views[0]['display_units']))
        unauthorized=self.request('POST','/api/pvp/match/replay',{'match_id':match_id},2)
        self.assertNotEqual(unauthorized[0],200,'third player cannot fetch full combat frames')
        # Replays must not consume currencies or re-award match rewards.
        before=self.call('POST','/api/pvp/match/result',{'match_id':match_id},0)['result']
        after=self.call('POST','/api/pvp/match/result',{'match_id':match_id},0)['result']
        self.assertEqual(before['rating_delta_a'],after['rating_delta_a'])

    def test_online_arena_and_guild_rosters_expose_only_public_avatar_ids(self):
        # Registration is NOT an arena result. Create a real authoritative
        # 1v1 before checking public leaderboard avatars.
        initial=self.call('GET','/api/pvp/status?mode=arena',user=0)['rating_board']
        self.assertEqual(len(initial),3)
        self.assertTrue(all(p['rank_basis']=='power' for p in initial))
        self.ready_match('arena')
        match=self.call('GET','/api/pvp/status?mode=arena',user=0)['pvp']['match']
        self.call('POST','/api/pvp/match/battle',{'match_id':match['id'],'formation':self.call('GET','/api/state',user=0)['formation']},0)
        board=self.call('GET','/api/pvp/status?mode=arena',user=0)['rating_board']
        self.assertEqual(len(board),3)
        self.assertTrue(all(p['matches']>0 for p in board[:2]))
        self.assertEqual(board[2]['matches'],0)
        for player in board:
            self.assertEqual(player['avatar'],'head_1001')  # clean SQLite fallback
            self.assertTrue(set(player).isdisjoint({'data','items','email','password_hash','salt'}))
        made=self.call('POST','/api/world-guild/action',
                       {'action':'create','name':'HTTP Public Avatar Guild','notice':'QA isolated'},0)
        gid=made['guild']['id']
        self.call('POST','/api/world-guild/manage',{'action':'apply','guild_id':gid},1)
        first=self.call('GET','/api/world-guild',user=0)
        pending=first.get('applications') or []
        self.assertEqual(len(pending),1)
        self.call('POST','/api/world-guild/manage',
                  {'action':'review','target_uid':pending[0]['uid'],'approve':True},0)
        own=self.call('GET','/api/world-guild',user=0)
        other=self.call('GET','/api/world-guild',user=1)
        for payload in (own,other):
            members=payload['guild']['members']
            self.assertEqual(len(members),2)
            for member in members:
                self.assertEqual(member['avatar'],'head_1001')
                self.assertTrue(set(member).isdisjoint({'data','items','email','password_hash','salt'}))

    def test_shared_wifi_rate_limits_each_verified_account_separately(self):
        # All three HTTP sessions connect from localhost, like players on one NAT.
        # Malformed match IDs trigger a normal 400, without reading other saves.
        req={'match_id':'not-a-real-match','round':0}
        for _ in range(12):
            status,payload,_=self.request('POST','/api/pvp/arena3v3/replay',req,0)
            self.assertEqual(status,400,payload)
        status,denied,_=self.request('POST','/api/pvp/arena3v3/replay',req,0)
        self.assertEqual(status,429,denied)
        self.assertEqual(denied.get('error'),'RATE_LIMITED')
        status,other,_=self.request('POST','/api/pvp/arena3v3/replay',req,1)
        self.assertEqual(status,400,other)
        status,third,_=self.request('POST','/api/pvp/arena3v3/replay',req,2)
        self.assertEqual(status,400,third)

    def test_http_arena3v3_rounds_and_private_replays(self):
        for idx in (0,1):
            fresh=self.call('GET','/api/pvp/status?mode=arena3v3',user=idx)
            self.assertGreaterEqual(int(fresh['arena3v3']['tickets']),3)
            state=self.call('GET','/api/state',user=idx)
            self.assertGreaterEqual(len(state['roster']),3)
            self.assertTrue(state['arena3v3_info']['online_only'])
            self.assertEqual(state['arena3v3_info']['board'],[])
            self.assertEqual(state['arena3v3_info']['enemies'],[])
            self.assertIsNone(state['arena3v3_info']['rank'])
            self.assertEqual(state['arena3v3_info']['tickets'],fresh['arena3v3']['tickets'])
            teams=[[{'partner_id':int(h['partner_id']),'pos':1}]
                   for h in state['roster'][:3]]
            self.call('POST','/api/pvp/arena3v3/teams',{'teams':teams},idx)
        match_id=self.ready_match('arena3v3')
        for idx in (0,1):
            self.call('POST','/api/pvp/arena3v3/pay',{'match_id':match_id},idx)
        for round_index in range(3):
            resolved=self.call('POST','/api/pvp/arena3v3/round',
                               {'match_id':match_id,'expected_round':round_index},0)
            self.assertTrue(resolved.get('round_report'),'every played round uses LuaJIT')
            a=self.call('POST','/api/pvp/arena3v3/replay',{'match_id':match_id,'round':round_index},0)['report']
            b=self.call('POST','/api/pvp/arena3v3/replay',{'match_id':match_id,'round':round_index},1)['report']
            self.assertTrue(a['frames'])
            self.assertEqual(a['isWin'],1-b['isWin'])
            bad=self.request('POST','/api/pvp/arena3v3/replay',{'match_id':match_id,'round':round_index},2)
            self.assertNotEqual(bad[0],200)
            if resolved.get('result'):
                self.assertEqual(resolved['result']['status'],'finished')
                break
        duplicate=self.call('POST','/api/pvp/arena3v3/round',
                            {'match_id':match_id,'expected_round':0},1)
        self.assertEqual(duplicate['result']['status'],'finished')
        replay=self.call('POST','/api/pvp/arena3v3/replay',{'match_id':match_id,'round':0},1)
        self.assertTrue(replay['report']['frames'])


    def test_keepalive_cookie_change_never_reuses_previous_account(self):
        # BaseHTTPRequestHandler serves multiple HTTP/1.1 requests on the same
        # handler object. Changing the Cookie must therefore re-resolve auth,
        # never reuse the previous request's cached player engine.
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=30)
        try:
            seen=[]
            for user in (0,1,0):
                conn.request('GET','/api/state',headers={'Cookie':self.tokens[user]})
                response=conn.getresponse()
                payload=json.loads(response.read())
                self.assertEqual(response.status,200,payload)
                seen.append((payload['uid'],payload['name']))
            self.assertNotEqual(seen[0],seen[1])
            self.assertEqual(seen[0],seen[2])
        finally:
            conn.close()


if __name__=='__main__':
    unittest.main()
