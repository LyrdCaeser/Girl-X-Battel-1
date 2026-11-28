"""Isolated authorization and seat accounting; no Production DB or SFU mutation."""
import json,base64,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from gxb2 import database,live_service,social_bar as b,social_arena as a,social_voice as v

class VoiceTests(unittest.TestCase):
    def setUp(self):
        self.assertFalse(database.is_postgres())
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        p=Path(tmp.name)/'voice.sqlite'
        for obj,name,value in [(live_service,'_db',lambda:database.connect(p,'live')),(v,'_leases',{}),(v,'enabled',lambda:True),(v,'_start',lambda:None),(v,'_credentials',lambda:{'key':'qa-key','secret':'qa-secret'}),(b,'enabled',lambda:True),(a,'enabled',lambda:True)]:
            mock=patch.object(obj,name,value);mock.start();self.addCleanup(mock.stop)
        self.calls=[]
        def rpc(method,room,**kw):
            self.calls.append((method,room,kw));return {'ok':True}
        mock=patch.object(v,'rpc',rpc);mock.start();self.addCleanup(mock.stop)
    def join(self,i,room='public:CROSS',world='S1'):
        uid='P'+str(i);b.enter(uid,world,uid,room)
        return v.join('bar',room,uid,world,uid)
    def ctl(self,i,lease,action,room='public:CROSS',world='S1'):
        return v.control('bar',room,'P'+str(i),world,lease,action)
    def test_eight_seats_and_listener_only_tokens(self):
        leases=[]
        for i in range(9):
            j=self.join(i)
            claim=json.loads(base64.urlsafe_b64decode(j['token'].split('.')[1]+'==='))
            self.assertFalse(claim['video']['canPublish'])
            self.assertEqual(claim['video']['canPublishSources'],['microphone'])
            leases.append(j['lease'])
        for i in range(8):
            self.assertTrue(self.ctl(i,leases[i],'mic_on')['mic'])
        with self.assertRaises(ValueError):self.ctl(8,leases[8],'mic_on')
        self.assertFalse(self.ctl(0,leases[0],'mic_off')['mic'])
        self.assertTrue(self.ctl(8,leases[8],'mic_on')['mic'])
        with self.assertRaises(ValueError):self.ctl(0,leases[8],'mic_on')
        self.ctl(8,leases[8],'leave')
        self.assertEqual(sum(l['mic'] for l in v._leases.values()),7)
    def test_room_scope_kick_and_mic_revocation(self):
        with self.assertRaises(ValueError):v.join('bar','public:S1','U','S2','U')
        j=self.join(0);self.ctl(0,j['lease'],'mic_on')
        b.action('P0','S1','public:CROSS','mic',target='P0',admin=True)
        r=self.ctl(0,j['lease'],'heartbeat');self.assertFalse(r['mic'])
        self.assertTrue(any(m=='UpdateParticipant' and not kw['permission']['canPublish'] for m,room,kw in self.calls))
        b.leave('P0','S1','public:CROSS')
        with self.assertRaises(ValueError):self.ctl(0,j['lease'],'heartbeat')
        self.assertFalse(v._leases)
    def test_arena_exact_match_membership(self):
        with a.transaction() as (st,db):
            st['matches']['test']={'uids':['P0','P1','P2','P3'],'status':'preview'}
        with self.assertRaises(ValueError):v.join('arena','test','P0','S1','P0')
        with self.assertRaises(ValueError):v.join('arena','test','OUT','S5','OUT')
        r=v.join('arena','test','P0','S5','P0')
        self.assertTrue(v.control('arena','test','P0','S5',r['lease'],'mic_on')['mic'])
        with a.transaction() as (st,db):st['matches']['test']['status']='finished'
        with self.assertRaises(ValueError):v.control('arena','test','P0','S5',r['lease'],'heartbeat')
    def test_lease_expiration_and_retry(self):
        j=self.join(0);self.ctl(0,j['lease'],'mic_on')
        k,l=next(iter(v._leases.items()));l['expires']=0
        with patch.object(v,'rpc',side_effect=ValueError('QA failure')):
            v._reap();self.assertIn(k,v._leases)
        v._reap();self.assertNotIn(k,v._leases)
