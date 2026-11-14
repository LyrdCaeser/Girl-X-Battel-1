"""REAL HTTP, auth cookies, 2FA and original Goddess catalog, SQLite-only."""
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from gxb2 import auth, database, giftcodes, live_service, owner_recovery, player_engines
from gxb2.engine import Engine
from server import HTTPHandler, make_servers


class GmGoddessHTTPTests(unittest.TestCase):
    def setUp(self):
        if database.POSTGRES:self.skipTest('Isolated SQLite only')
        temp=tempfile.TemporaryDirectory(prefix='gxb3-gm-realhttp-')
        self.addCleanup(temp.cleanup)
        root=Path(temp.name)
        source=database.connect
        for module,path,kind in ((auth,root/'auth.sqlite3','auth'),
                                 (live_service,root/'live.sqlite3','live')):
            ctx=patch.object(module,'_db',lambda p=path,k=kind: source(p,k))
            ctx.start();self.addCleanup(ctx.stop)
        self.owner_uid=None
        original_auth=HTTPHandler.is_super_gm
        ctx=patch.object(HTTPHandler,'is_super_gm',lambda handler:
            bool(handler.auth_context() and handler.auth_context()['account']['uid']==self.owner_uid))
        ctx.start();self.addCleanup(ctx.stop)
        ctx=patch.object(owner_recovery,'verify_key',lambda name,key: name=='gm' and key=='QA_ACTION_KEY_32_CHARS_DONT_SHARE')
        ctx.start();self.addCleanup(ctx.stop)
        old=giftcodes._READY
        giftcodes._READY=False;self.addCleanup(setattr,giftcodes,'_READY',old)
        ctx=patch.object(player_engines,'ROOT',root);ctx.start();self.addCleanup(ctx.stop)
        self.game=Engine(root/'dev.sqlite3')
        self.pool=player_engines.PlayerEnginePool()
        self.http,self.tcp=make_servers(self.game,0,0,player_engines=self.pool,trust_proxy=False)
        self.thread=threading.Thread(target=self.http.serve_forever,daemon=True);self.thread.start()
        self.addCleanup(self.cleanup)
        self.port=self.http.server_port
        self.cookies=[]
        for i in range(2):
            code,payload,headers=self.call('POST','/api/auth/register',{
                'username':'GiftGMHttp'+str(i),'password':'ExamplePassword123A',
                'character_name':'GM HTTP '+str(i),'server_id':'S1'})
            self.assertEqual(code,200,payload)
            self.cookies.append(headers['set-cookie'].split(';',1)[0])
            if i==0:self.owner_uid=payload['account']['uid']

    def cleanup(self):
        self.http.shutdown();self.http.server_close();self.tcp.server_close()
        self.thread.join(timeout=6);self.pool.close();self.game.close()

    def call(self,method,path,payload=None,user=None,key=None):
        headers={}
        if payload is not None:headers['Content-Type']='application/json'
        if user is not None:headers['Cookie']=self.cookies[user]
        if key:headers['X-GXB3-GM-Key']=key
        c=http.client.HTTPConnection('127.0.0.1',self.port,timeout=30)
        try:
            c.request(method,path,body=None if payload is None else json.dumps(payload),headers=headers)
            r=c.getresponse();body=json.loads(r.read());return r.status,body,{k.lower():v for k,v in r.getheaders()}
        finally:c.close()

    def test_owner_only_catalog_and_2fa_creating_thirty_day_unlimited_code(self):
        self.assertEqual(self.call('GET','/api/admin/goddess-gift/catalog')[0],401)
        self.assertEqual(self.call('GET','/api/admin/goddess-gift/catalog',user=1)[0],403)
        code,body,_=self.call('GET','/api/admin/goddess-gift/catalog',user=0)
        self.assertEqual(code,200,body)
        self.assertEqual(len(body['goddesses']),446)
        self.assertEqual({x['group'] for x in body['goddesses']},set(range(1,8)))
        config={'girl_id':51017,'stars':15,'level':250,'stats':{'hp':10},'max_stellar':True,'max_red6':True}
        self.assertEqual(self.call('POST','/api/admin/goddess-gift/create',config)[0],401)
        self.assertEqual(self.call('POST','/api/admin/goddess-gift/create',config,user=1,key='QA_ACTION_KEY_32_CHARS_DONT_SHARE')[0],403)
        self.assertEqual(self.call('POST','/api/admin/goddess-gift/create',config,user=0)[0],403)
        self.assertEqual(self.call('POST','/api/admin/goddess-gift/create',config,user=0,key='wrong')[0],403)
        code,data,_=self.call('POST','/api/admin/goddess-gift/create',config,user=0,key='QA_ACTION_KEY_32_CHARS_DONT_SHARE')
        self.assertEqual(code,200,data)
        self.assertEqual(data['max_uses'],0)
        self.assertTrue(data['unlimited'])
        self.assertTrue(data['code'].startswith('GXB3-'))
        self.assertEqual(data['rewards']['__gxb3_goddess__']['table_id'],751017)
        self.assertEqual(len(giftcodes.list_codes()),1)
        self.assertEqual(self.call('GET','/api/admin/goddess-gift/catalog',user=1)[0],403)


if __name__=='__main__':unittest.main()
