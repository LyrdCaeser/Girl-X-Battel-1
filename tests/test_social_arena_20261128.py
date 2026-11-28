import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from gxb2 import social_arena as a, database, live_service
from gxb2.engine import Engine
from gxb2.battle import ONLINE_BATTLE_ID

class TournamentTests(unittest.TestCase):
    def setUp(self):
        self.assertFalse(database.is_postgres(),'Only isolated SQLite tests')
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        path=Path(self.temp.name)/'live.sqlite'
        p=patch.object(live_service,'_db',lambda:database.connect(path,'live'))
        p.start();self.addCleanup(p.stop)
        self.engine=Engine(Path(self.temp.name)/'engine.sqlite')
        self.addCleanup(self.engine.close)
        self.snap=self.engine.pvp_team_snapshot()
        self.now=a.START+60
    def join(self,uid,now=None):
        return a.join(uid,uid,{**self.snap,'uid':uid,'server_id':'S5'},world='S5',now=self.now if now is None else now)
    def ready(self,uids):
        ids=[self.join(u) for u in uids]
        self.assertEqual(ids[:3],[None]*3)
        mid=ids[3]
        for u in uids:a.accept(u,mid,now=self.now+1)
        self.assertEqual(len(a.status(uids[0],now=self.now+2)['match']['formations']),4)
        with self.assertRaises(ValueError):a.begin(uids[0],mid,now=self.now+5)
        for u in uids:a.begin(u,mid,now=self.now+6)
        return mid
    def test_real_engine_two_rounds_and_idempotent_settlement(self):
        users=['P1','P2','P3','P4']
        mid=self.ready(users)
        with self.assertRaises(ValueError):a.resolve('intruder',mid,ONLINE_BATTLE_ID,now=self.now+7)
        self.assertEqual(a.resolve(users[0],mid,ONLINE_BATTLE_ID,now=self.now+7),'finished')
        reports=[a.replay(uids,mid,i) for i,uids in enumerate(users[:2])]
        self.assertTrue(all(r['frames'] and 0<int(r['total_round'])<=20 for r in reports))
        score=a.match_points(reports)
        first=a.status(users[0],now=self.now+8)
        self.assertEqual(first['history'][0]['score'],score)
        for u in users:
            self.assertEqual(a.resolve(u,mid,ONLINE_BATTLE_ID,now=self.now+9),'finished')
        self.assertEqual(first['board'],a.status(users[0],now=self.now+10)['board'])
        self.assertEqual(sum(p['points'] for p in first['board']),400)
        with self.assertRaises(ValueError):a.replay('intruder',mid,0)
    def test_filter_and_expire(self):
        with self.assertRaises(ValueError):self.join('P1',a.START-1)
        with self.assertRaises(ValueError):a.join('P1','x',self.snap,world='S1',now=self.now)
        with self.assertRaises(ValueError):a.join('P1','x',self.snap,world='S5',admin=True,now=self.now)
        with self.assertRaises(ValueError):a.validate_snapshot({'uid':'P1','server_id':'S5','team':[{'table_id':758001,'pos':1}]},'P1')
        self.join('P1')
        self.assertFalse(a.status('P1',now=self.now+a.QUEUE_TTL+1)['queued'])
    def test_score_draw_and_elimination(self):
        def report(h1,h2):return {'total_round':20,'end_status':[{'pos':1,'hp':h1},{'pos':7,'hp':h2}]}
        win=report(100,0);draw=report(5,5);loss=report(0,100)
        self.assertEqual(a.match_points([win,draw]),[2,1])
        self.assertEqual(a.match_points([draw,draw]),[2,2])
        self.assertEqual(a.match_points([loss,loss]),[0,2])
        users=['P1','P2','P3','P4']
        mid=self.ready(users)
        with a.transaction() as (state,db):
            m=state['matches'][mid]
            losers=m['uids'][2:]
            for u in losers:state['players'][u]['points']=20
        with patch.object(a,'simulate_pair',return_value=win):
            a.resolve(users[0],mid,ONLINE_BATTLE_ID,now=self.now+7)
        for u in losers:
            self.assertEqual(a.status(u,now=self.now+8)['me']['points'],0)
            with self.assertRaises(ValueError):self.join(u)
    def test_referee_and_atomic_reward(self):
        users=['P1','P2','P3','P4']
        mid=self.ready(users)
        with self.assertRaises(PermissionError):a.referee('close',authorized=False)
        with self.assertRaises(ValueError):a.referee('finalize',authorized=True,now=self.now+7)
        report={'total_round':20,'end_status':[{'pos':1,'hp':100},{'pos':7,'hp':0}]}
        with patch.object(a,'simulate_pair',return_value=report):
            a.resolve(users[0],mid,ONLINE_BATTLE_ID,now=self.now+7)
        final=a.referee('finalize',authorized=True,now=a.END)['final']
        self.assertEqual(len(final),4)
        uid=final[0]['uid']
        live_service.register_player(uid,'S1','Winner')
        with self.assertRaises(PermissionError):a.award(1,'S1',{'1':123},'Test','',authorized=False)
        with self.assertRaises(ValueError):a.award(1,'S5',{'1':123},'Test','',authorized=True)
        first=a.award(1,'S1',{'1':123},'Test','',authorized=True)
        second=a.award(1,'S1',{'1':123},'Test','',authorized=True)
        self.assertFalse(first['already_sent'])
        self.assertEqual(first['mail_id'],second['mail_id'])
        self.assertTrue(second['already_sent'])
        db=live_service._db()
        try:
            row=db.execute('SELECT uid,server_id,attachments FROM mail WHERE id=?',(first['mail_id'],)).fetchone()
            self.assertEqual(row['uid'],uid)
            self.assertEqual(row['server_id'],'S1')
        finally:db.close()
