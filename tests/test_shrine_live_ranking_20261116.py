"""Real ranking reads active player profiles, never fabricated leaderboard rows."""
import json
import unittest
from unittest.mock import patch
from gxb2 import live_service,shrine


class FakeDB:
    def __init__(self, rows): self.rows=rows;self.closed=False
    def execute(self, query, args):
        assert "p.status='active'" in query
        assert args==('S1',)
        return self
    def fetchall(self): return self.rows
    def close(self):self.closed=True


class ShrineOnlineRankingTest(unittest.TestCase):
    def test_real_profiles_sorted_by_season_score(self):
        def row(uid, name, n, scores, power=100):
            return {'uid':uid,'character_name':name,'level':10,'power':power,
                    'data':json.dumps({'shrine':{'season':{'n':n,'scores':scores}},
                                       'profile':{'avatar':'head_1001','frame':'frame_8007'}})}
        db=FakeDB([row('u1','A',10,{'1':300}),row('u2','B',10,{'1':100,'2':500}),
                   row('u3','Old',9,{'1':9999}),row('u4','Empty',10,{})])
        with patch.object(live_service,'_db',return_value=db):
            result=live_service.shrine_ranking('S1',10,current_uid='u2')
        self.assertTrue(db.closed)
        self.assertEqual([r['uid'] for r in result],['u2','u1'])
        self.assertEqual([r['score'] for r in result],[600,300])
        self.assertEqual([r['rank'] for r in result],[1,2])
        self.assertTrue(result[0]['me'])
        self.assertFalse(result[1]['me'])

    def test_original_unlock_does_not_bypass_tower_floor(self):
        state={'tower':{'max_stage':3},'partners':[
            {'table_id':751001,'awake':0}]}
        floor,has10,unlocked=shrine.unlock_state(state)
        self.assertEqual(floor,3)
        self.assertTrue(has10)
        self.assertFalse(unlocked)


if __name__=='__main__':unittest.main()
