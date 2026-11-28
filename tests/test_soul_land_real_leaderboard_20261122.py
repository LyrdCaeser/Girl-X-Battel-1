"""Soul Land leaderboards contain verified saved players; never bots.

Synthetic read-only SQLite fixtures only. No real Neon/user mutation.
"""
import json
import sqlite3
import unittest
from unittest.mock import patch
from gxb2 import live_service, bots


class FakeDB:
    backend = 'sqlite'
    def __init__(self):
        self.conn=sqlite3.connect(':memory:')
        self.conn.row_factory=sqlite3.Row
        self.conn.execute('CREATE TABLE players(uid TEXT,server_id TEXT,character_name TEXT,status TEXT)')
        self.conn.execute('CREATE TABLE player_profiles(uid TEXT,server_id TEXT,data TEXT)')
        self.conn.execute('CREATE TABLE leaderboard(uid TEXT,server_id TEXT,level INT,power INT)')
    def add(self, uid, server, name, status, cleared, power=0, avatar='head_1001'):
        self.conn.execute('INSERT INTO players VALUES(?,?,?,?)',(uid,server,name,status))
        profile={'profile':{'avatar':avatar}}
        if cleared is not None:
            profile['soul_land']={'cleared':cleared}
        self.conn.execute('INSERT INTO player_profiles VALUES(?,?,?)',
                          (uid,server,json.dumps(profile)))
        self.conn.execute('INSERT INTO leaderboard VALUES(?,?,?,?)',
                          (uid,server,320,power))
    def execute(self, sql, params=()):
        return self.conn.execute(sql, params)
    def close(self):
        # No-op so the fixture can be reused between requests.
        pass


class RealSoulLandLeaderboardTests(unittest.TestCase):
    def setUp(self):
        self.db=FakeDB()
        self.db.add('a','S1','Bé Anh','active',{'1':1009,'2':2002},power=100,
                    avatar='head_1234')  # 9 + 2 = 11
        self.db.add('b','S1','Chiến Binh','active',{'1':1011},power=200)  # 11
        self.db.add('bot','S1','Bot giả','banned',{'1':1050},power=100000)
        self.db.add('other','S2','Máy Chủ Khác','active',{'1':1050},power=100000)
        self.db.add('new','S1','Chưa Chơi','active',{})
        self.db.add('bad','S1','Dữ liệu hỏng','active',{'1':9000,'2':2010})  # only valid fort 2 counts
        self.db.add('zero','S1','Chưa Mở','active',None)

    def tearDown(self):
        self.db.conn.close()

    def test_real_players_only_with_exact_stage_counts(self):
        with patch.object(live_service,'_db',return_value=self.db):
            rows=live_service.soul_land_ranking('s1','a')
        self.assertEqual([r['character_name'] for r in rows],
                         ['Chiến Binh','Bé Anh','Dữ liệu hỏng'])
        self.assertEqual([r['score'] for r in rows],[11,11,10])
        self.assertEqual([r['rank'] for r in rows],[1,2,3])
        self.assertEqual([r['me'] for r in rows],[False,True,False])
        self.assertEqual([r['server_id'] for r in rows],['S1']*3)
        self.assertEqual(rows[1]['avatar'],'head_1234')
        self.assertNotIn('uid', rows[0])
        self.assertNotIn('power', rows[0])
        self.assertTrue(all('bot' not in r for r in rows))

    def test_emptiness_limit_and_fort_bounds(self):
        with patch.object(live_service,'_db',return_value=self.db):
            self.assertEqual(len(live_service.soul_land_ranking('S1','a',limit=1)),1)
            self.assertEqual([r['score'] for r in live_service.soul_land_ranking('S2')],[50])
            self.assertEqual(live_service.soul_land_ranking('S3'),[])

    def test_legacy_snapshot_no_fake_soul_land_ranking(self):
        state={'name':'Player','level':300,'soul_land_info':{
            'forts':[{'first':1001,'cleared':1004}]}}
        snap=bots.snapshot(state,300,1796000000)
        self.assertNotIn('soul_land',snap['ranks'])
        self.assertIn('shrine',snap['ranks'])
        self.assertIn('tower',snap['ranks'])

if __name__=='__main__':unittest.main()
