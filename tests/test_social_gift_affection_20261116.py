"""Offline regression for friends gifts on historical Neon-like profiles.

No player DB connection. Mocks a transactional database and verifies that
missing social_affection never leaks KeyError and that rollback is atomic.
"""
import copy
import json
import unittest
from unittest.mock import patch
from gxb2 import live_service as svc


class FakeResult:
    def __init__(self, row):self.row=row
    def fetchone(self):return self.row


class FakeTransactionDB:
    backend='sqlite'
    def __init__(self, sender, receiver):
        self.states={'a':copy.deepcopy(sender),'b':copy.deepcopy(receiver)}
        self.staged=None
        self.inserts=0
        self.commits=0
        self.rollbacks=0
        self.closed=False

    def execute(self,sql,args=()):
        op=sql.strip().upper()
        if op.startswith('BEGIN'):
            self.staged=copy.deepcopy(self.states)
            return FakeResult(None)
        if op.startswith('SELECT DATA FROM PLAYER_PROFILES'):
            return FakeResult({'data':json.dumps(self.staged[args[0]])})
        if op.startswith('SELECT COALESCE') or op.startswith('SELECT COUNT'):
            return FakeResult({'n':0})
        if op.startswith('UPDATE PLAYER_PROFILES'):
            self.staged[args[-2]]=json.loads(args[0])
            return FakeResult(None)
        if op.startswith('INSERT INTO SOCIAL_ITEM_GIFTS'):
            self.inserts+=1
            return FakeResult(None)
        raise AssertionError('Unexpected SQL: '+sql[:100])

    def commit(self):
        self.states=copy.deepcopy(self.staged)
        self.commits+=1
        self.staged=None

    def rollback(self):
        self.staged=None
        self.rollbacks+=1

    def close(self):
        self.closed=True


class GiftRegressionTest(unittest.TestCase):
    def setUp(self):
        self.db=FakeTransactionDB({'items':{'300':5}},
                                  {'items':{'300':2}})
        self.patches=[
            patch.object(svc,'_db',return_value=self.db),
            patch.object(svc,'_ensure_social_tables',return_value=None),
            patch.object(svc,'_are_friends',return_value=True),
            patch.object(svc,'_audit',return_value=None),
            patch.object(svc,'social_gift_meta',return_value={
                'id':'300','name':'Hộp Cơm','kind':'item','points':10,
                'quality':2,'icon':'icon_300','max_quantity':None,
                'affection_divisor':1
            }),
        ]
        for p in self.patches:p.start()

    def tearDown(self):
        for p in reversed(self.patches):p.stop()

    def test_old_profiles_with_missing_affection_gift_success_and_same_credit(self):
        result=svc.friend_gift('a','S1','b','300',2)
        self.assertTrue(result['ok'])
        self.assertEqual(result['affection_gained'],20)
        self.assertEqual(result['affection'],20)
        self.assertEqual(self.db.states['a']['items']['300'],3)
        self.assertEqual(self.db.states['b']['items']['300'],4)
        self.assertEqual(self.db.states['a']['social_affection']['b'],20)
        self.assertEqual(self.db.states['b']['social_affection']['a'],20)
        self.assertEqual(self.db.commits,1)
        self.assertEqual(self.db.rollbacks,0)
        self.assertTrue(self.db.closed)

    def test_null_affection_in_legacy_profiles_normalized(self):
        self.db.states['a']['social_affection']=None
        self.db.states['b']['social_affection']=None
        svc.friend_gift('a','S1','b','300',1)
        self.assertEqual(self.db.states['a']['social_affection']['b'],10)
        self.assertEqual(self.db.states['b']['social_affection']['a'],10)

    def test_insufficient_items_rolls_back_without_partial_transfer(self):
        original=copy.deepcopy(self.db.states)
        with self.assertRaisesRegex(ValueError,'Không đủ vật phẩm'):
            svc.friend_gift('a','S1','b','300',9)
        self.assertEqual(self.db.states,original)
        self.assertEqual(self.db.commits,0)
        self.assertEqual(self.db.rollbacks,1)

    def test_existing_affection_increments_instead_of_resetting(self):
        self.db.states['a']['social_affection']={'b':17}
        self.db.states['b']['social_affection']={'a':17}
        r=svc.friend_gift('a','S1','b','300',1)
        self.assertEqual(r['affection'],27)
        self.assertEqual(self.db.states['b']['social_affection']['a'],27)


if __name__=='__main__':
    unittest.main()
