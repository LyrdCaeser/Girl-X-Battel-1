"""Ranking uses current-season real player progress, never artificial entries."""
import json
import unittest
from unittest.mock import patch
from gxb2 import live_service, house_exam


class DB:
    def __init__(self,rows): self.rows=rows;self.closed=False
    def execute(self,query,args):
        assert "p.status='active'" in query
        assert args==('S1',)
        return self
    def fetchall(self):return self.rows
    def close(self):self.closed=True


class RankingTest(unittest.TestCase):
    def test_real_season_separated_and_progress_per_house(self):
        first=house_exam.FIRST[1]
        ordered=[int(r['id']) for r in house_exam.FORTS[1]]
        def row(uid,season,score,current):
            return {'uid':uid,'character_name':'User '+uid,'level':25,'power':200,
                    'data':json.dumps({'house_exam':{
                        'season':season,'score':score,'current':{'1':current}},
                        'profile':{'avatar':'head_1001'}})}
        db=DB([row('a',123,500,ordered[2]),row('b',123,1000,ordered[1]),
               row('c',122,9000,-1),row('empty',123,0,first)])
        with patch.object(live_service,'_db',return_value=db):
            total=live_service.house_exam_ranking('S1',123,'a',0)
        self.assertEqual([x['uid'] for x in total],['b','a'])
        with patch.object(live_service,'_db',return_value=db):
            ghost=live_service.house_exam_ranking('S1',123,'a',1)
        self.assertEqual([x['uid'] for x in ghost],['a','b'])
        self.assertEqual([x['progress'] for x in ghost],[2,1])
        self.assertTrue(ghost[0]['me'])
        self.assertTrue(db.closed)
        self.assertEqual([x['character_name'] for x in ghost],['User a','User b'])

    def test_bad_faction_rejected(self):
        with self.assertRaisesRegex(ValueError,'Hệ thi đấu'):
            live_service.house_exam_ranking('S1',123,'a',7)


if __name__=='__main__':unittest.main()
