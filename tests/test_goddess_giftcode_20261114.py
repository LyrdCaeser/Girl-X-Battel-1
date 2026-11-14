"""SUPER GM Goddess Gift: original shapes, audited 30-day giftcodes, atomic claims.

ALL writes use isolated temporary SQLite. Never touch Neon/Production.
"""
import copy
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from gxb2 import database, live_service, giftcodes, goddess_gifts
from gxb2.engine import Engine
from gxb2.battle import attributes


class GoddessGiftcodeTests(unittest.TestCase):
    def setUp(self):
        if database.POSTGRES:self.skipTest('Isolated SQLite ONLY, never Production Neon')
        self.temp=tempfile.TemporaryDirectory(prefix='gxb3-goddess-gift-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        path=self.root/'live.sqlite3'
        original=database.connect
        p=patch.object(live_service,'_db',lambda:original(path,'live'))
        p.start();self.addCleanup(p.stop)
        old=giftcodes._READY
        giftcodes._READY=False
        self.addCleanup(setattr,giftcodes,'_READY',old)
        self.names=['GMTEST-USER-A','GMTEST-USER-B','GMTEST-USER-C']
        for i,uid in enumerate(self.names):
            live_service.register_player(uid,'S1',f'Test Player {i}')
        self.games={}
        for uid in self.names:
            game=Engine(self.root/f'{uid}.sqlite3')
            with game.lock:
                game.db.execute('BEGIN IMMEDIATE')
                state=game._load()
                state['uid']=uid;state['server_id']='S1'
                game._save_profile(state);game.db.commit()
            self.games[uid]=game
            self.addCleanup(game.close)

    def config(self,**changes):
        c={'girl_id':51017,'stars':15,'level':250,
           'stats':{'hp':1200,'atk':310,'arm':125,'spd':4},
           'max_stellar':True,'max_red6':True}
        c.update(changes)
        return c

    def test_validated_complete_gift_from_redeem_to_claim_mail_exact_uid(self):
        issued=giftcodes.create_goddess(self.config(),'SUPER-GM-TEST')
        self.assertTrue(issued['unlimited'])
        self.assertEqual(issued['max_uses'],0)
        self.assertIsNone(issued['remaining'])
        self.assertTrue(30*86400-15<=issued['expires_at']-int(time.time())<=30*86400+5)
        self.assertEqual(issued['rewards']['__gxb3_goddess__']['table_id'],751017)
        for i,uid in enumerate(self.names):
            got=giftcodes.redeem(issued['code'],uid,'S1')
            self.assertTrue(got['ok'])
            mailid=got['mail_id']
            self.assertEqual(len(live_service.mailbox(uid,'S1')),1)
            if i==0:
                before=self.games[uid].snapshot()
                data=self.games[uid].claim_live_mail(mailid)
                self.assertEqual(data['goddess']['stars'],15)
                after=data['state']
                self.assertEqual(before['items'],after['items'])
                self.assertEqual(len(after['roster']),len(before['roster'])+1)
                new=next(g for g in after['roster'] if g['partner_id']==data['goddess']['partner_id'])
                self.assertEqual(new['table_id'],751017)
                self.assertEqual(new['stars'],15)
                self.assertEqual(new['lv'],250)
                self.assertEqual(new['equips'][:4],[1999,2999,3999,4999])
                self.assertEqual(len(new['star_origin']),10)
                self.assertEqual(new['gm_bonus'],{'hp':1200,'atk':310,'arm':125,'spd':4})
                self.assertEqual(live_service.mailbox(uid,'S1')[0]['status'],'claimed')
                with self.assertRaises(ValueError):self.games[uid].claim_live_mail(mailid)
            with self.assertRaisesRegex(ValueError,'đã sử dụng'):
                giftcodes.redeem(issued['code'],uid,'S1')
        codes=giftcodes.list_codes()
        self.assertEqual(codes[0]['used_count'],3)
        self.assertEqual(codes[0]['remaining'],None)
        self.assertEqual(len(giftcodes.redemptions(issued['code'])),3)
        # Neither users B/C nor a stranger receive automatic characters until
        # they explicitly claim the mailed reward on their own account.
        self.assertEqual(len(self.games[self.names[1]].snapshot()['roster']),len(self.games[self.names[2]].snapshot()['roster']))

    def test_full_25_star_666_level_cannot_exceed_native_cap(self):
        valid=self.config(girl_id=757001,stars=25,level=666,stats={},max_red6=True,max_stellar=True)
        c=goddess_gifts.validate(valid)
        self.assertEqual(c['stars'],25)
        self.assertEqual(c['table_id'],757001)
        self.assertEqual(c['awake'],15)
        with self.assertRaisesRegex(ValueError,'giới hạn'):
            goddess_gifts.validate(self.config(girl_id=41001,stars=4,level=666,max_stellar=False))
        with self.assertRaisesRegex(ValueError,'Lõi'):
            goddess_gifts.validate(self.config(girl_id=41001,stars=5,level=1,max_stellar=True,max_red6=False))
        with self.assertRaises(ValueError):
            goddess_gifts.validate(self.config(girl_id=541001,stars=6,level=1,max_stellar=False))
        with self.assertRaises(ValueError):
            goddess_gifts.validate(self.config(girl_id=757001,stars=5,level=1,max_stellar=False))
        with self.assertRaises(ValueError):
            goddess_gifts.validate(self.config(girl_id=51017,stars=25,level=667))

    def test_gm_flat_stats_feed_actual_original_luajit(self):
        # Use a 10-star native hero to keep the original engine fast.
        base={'partner_id':10,'table_id':751017,'lv':250,'grade':10,'awake':0,
              'pos':1,'equips':[0]*7,'show_skin':1}
        stronger={**base,'gm_bonus':{'hp':1200,'atk':310,'arm':125,'spd':4}}
        original=attributes([base])['10']
        gifted=attributes([stronger])['10']
        for k,expected in [('hp',1200),('atk',310),('arm',125),('spd',4)]:
            self.assertEqual(gifted[k]-original[k],expected,(k,original,gifted))
        self.assertGreater(gifted['power'],original['power'])

    def test_cosmic_25_star_full_stellar_red6_claim_and_luajit_attributes(self):
        spec={'girl_id':757001,'stars':25,'level':666,'stats':{'hp':880,'atk':160,'arm':70,'spd':2},
              'max_stellar':True,'max_red6':True}
        created=giftcodes.create_goddess(spec,'SUPER-GM-TEST')
        redeemer=self.names[2]
        claim=giftcodes.redeem(created['code'],redeemer,'S1')
        out=self.games[redeemer].claim_live_mail(claim['mail_id'])
        hero=next(g for g in out['state']['roster'] if g['partner_id']==out['goddess']['partner_id'])
        self.assertEqual(hero['stars'],25)
        self.assertEqual(hero['lv'],666)
        self.assertEqual(hero['equips'][:4],[1999,2999,3999,4999])
        self.assertEqual(hero['awake'],15)
        self.assertEqual(len(hero['star_origin']),10)
        self.assertTrue(all(v>0 for v in hero['star_origin']))
        self.assertEqual(hero['gm_bonus']['hp'],880)
        original_attr=attributes([hero])[str(hero['partner_id'])]
        self.assertGreater(original_attr['power'],0)
        self.assertEqual(live_service.mailbox(redeemer,'S1')[0]['status'],'claimed')

    def test_normal_giftcodes_existing_limits_unchanged_and_expiration(self):
        simple=giftcodes.create({'title':'Normal','message':'Normal','rewards':{'1':10},'max_uses':1},'SUPER-GM-TEST')
        self.assertFalse(simple['unlimited'])
        self.assertEqual(simple['remaining'],1)
        giftcodes.redeem(simple['code'],self.names[0],'S1')
        with self.assertRaisesRegex(ValueError,'hết lượt'):
            giftcodes.redeem(simple['code'],self.names[1],'S1')
        special=giftcodes.create_goddess(self.config(level=1),'SUPER-GM-TEST')
        db=live_service._db()
        try:
            db.execute('UPDATE giftcodes SET expires_at=? WHERE code=?',(int(time.time())-1,special['code']))
            db.commit()
        finally:db.close()
        with self.assertRaisesRegex(ValueError,'hết hạn'):
            giftcodes.redeem(special['code'],self.names[2],'S1')

    def test_invalid_gm_payload_no_issuance(self):
        with self.assertRaises(ValueError):
            giftcodes.create_goddess(self.config(stats={'hp':-100}),'TEST')
        with self.assertRaises(ValueError):
            giftcodes.create_goddess(self.config(stats={'atk':float('nan')}),'TEST')
        with self.assertRaises(ValueError):
            giftcodes.create_goddess(self.config(stars=26),'TEST')
        with self.assertRaises(ValueError):
            giftcodes.create_goddess(self.config(girl_id=9999999),'TEST')
        with self.assertRaises(ValueError):
            giftcodes.create_goddess(self.config(max_red6='true'),'TEST')
        self.assertEqual(len(giftcodes.list_codes()),0)


if __name__=='__main__': unittest.main()
