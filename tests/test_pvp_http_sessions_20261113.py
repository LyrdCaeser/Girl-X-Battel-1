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

    def ready_match(self,mode):
        for idx in (0,1):
            self.call('POST','/api/pvp/queue',{'action':'join','mode':mode},idx)
        status=self.call('GET',f'/api/pvp/status?mode={mode}',user=0)
        match=status['pvp']['match']
        for idx in (0,1):
            self.call('POST','/api/pvp/match/heartbeat',{'match_id':match['id'],'ready':True},idx)
        return match['id']

    def test_http_auth_cookies_real_pvp_and_replay_access(self):
        status,data,_=self.request('GET','/api/pvp/status?mode=arena')
        self.assertEqual(status,401,data)
        match_id=self.ready_match('arena')
        result=self.call('POST','/api/pvp/match/battle',{'match_id':match_id},0)
        self.assertEqual(result['result']['status'],'finished')
        views=[self.call('POST','/api/pvp/match/replay',{'match_id':match_id},i)['report'] for i in (0,1)]
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


if __name__=='__main__':
    unittest.main()
