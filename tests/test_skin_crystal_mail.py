"""Crystal Skin purchase must deliver exactly one pending mail inside the player transaction."""
import json
import sqlite3
import threading
import unittest
from unittest.mock import patch
from gxb2 import engine


class FakeAtomicPlayerDB:
    def __init__(self):
        self.raw=sqlite3.connect(":memory:")
        self.raw.row_factory=sqlite3.Row
        self.raw.execute("""CREATE TABLE mail (
            id TEXT PRIMARY KEY,uid TEXT,server_id TEXT,character_name TEXT,
            title TEXT,body TEXT,attachments TEXT,status TEXT,
            created_at BIGINT,operator TEXT
        )""")
        self.raw.commit()
    def execute(self, query, args=()):
        return self.raw.execute(query,args)
    def commit(self):
        self.raw.commit()
    def rollback(self):
        self.raw.rollback()
    def borrowed_live_transaction(self):
        return self
    def count_mail(self):
        return self.raw.execute("SELECT COUNT(*) FROM mail").fetchone()[0]


class CrystalMailTests(unittest.TestCase):
    def setUp(self):
        self.db=FakeAtomicPlayerDB()
        self.addCleanup(self.db.raw.close)
        self.game=object.__new__(engine.Engine)
        self.game.lock=threading.RLock()
        self.game.db=self.db
        self.state={'uid':'USER-5','server_id':'S1','name':'Nữ Thần', 'items':{'2':500,'7003':0}}
        self.game._load=lambda: self.state
        self.game._save_profile=lambda state:None
        self.game.snapshot=lambda:self.state
        def paid_action(state, req):
            state['items']['2']-=100
            state['items']['7003']+=1
            return {'got':{'7003':1},'purchase':{'price':100,'currency':'crystal'}}
        self.patches=[
            patch.object(engine,'ScopedPostgresPlayerDB',FakeAtomicPlayerDB),
            patch.object(engine.skins,'action',side_effect=paid_action),
            patch('gxb2.skin_store.is_wedding',return_value=False),
            patch.object(engine.live_service,'_audit',return_value=None),
        ]
        for p in self.patches:
            p.start();self.addCleanup(p.stop)

    def test_crystal_debit_delivers_one_mail_and_not_inventory(self):
        result=self.game.skins_action({'action':'buy','skin':7003,'payment':'crystal'})
        self.assertEqual(self.state['items']['2'],400)
        self.assertEqual(self.state['items']['7003'],0)
        self.assertEqual(result['delivery'],'mail')
        self.assertEqual(result['got'],{})
        self.assertEqual(self.db.count_mail(),1)
        row=self.db.execute("SELECT * FROM mail").fetchone()
        self.assertEqual(row['status'],'pending')
        self.assertEqual(row['uid'],'USER-5')
        self.assertEqual(row['server_id'],'S1')
        self.assertEqual(json.loads(row['attachments']),{'7003':1})

    def test_failed_save_rolls_back_delivery(self):
        self.game._save_profile=lambda _: (_ for _ in ()).throw(RuntimeError('simulated save failure'))
        with self.assertRaisesRegex(RuntimeError,'save failure'):
            self.game.skins_action({'action':'buy','skin':7003,'payment':'crystal'})
        self.assertEqual(self.db.count_mail(),0)


if __name__ == '__main__':
    unittest.main()
