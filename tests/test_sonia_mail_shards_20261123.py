"""Lyr Sonia mail and shard claim regression, local fake players only.

No production database access, no change to any player's 500 stored fragments.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2 import database, live_service, gm_catalog, sonia_festival, chaos_summon
from gxb2.engine import DEBRIS, TABLES

ROOT=Path(__file__).resolve().parents[1]

class SoniaMailShardTests(unittest.TestCase):
    def test_canonical_shard_not_separate_goddess(self):
        shard=DEBRIS[sonia_festival.SHARD]
        self.assertEqual(shard['name'],'Mảnh Lyr Sonia')
        self.assertEqual(shard['type'],3)
        self.assertEqual(shard['group'],8)
        self.assertEqual(shard['partner_cost'],'758001#100')
        self.assertEqual(int(shard['summon_id']),10260)
        self.assertEqual(TABLES['summon']['10260']['cost'],'940061#100')
        self.assertEqual(chaos_summon.PARTNER_ID,758001)

    def test_gm_catalog_stays_single_source_of_shard_without_duplicates(self):
        catalog=gm_catalog.catalog()
        special=[s for s in catalog['shards'] if int(s['id'])==940061]
        self.assertEqual(len(special),1)
        self.assertEqual(special[0]['girl_id'],758001)
        self.assertEqual(special[0]['required'],100)
        self.assertTrue(special[0]['image'].startswith('/assets/'))
        self.assertEqual(sum(1 for x in catalog['items'] if x['id']==940061),0)
        self.assertEqual(gm_catalog.validate_gift({'940061':500}),{'940061':500})
        self.assertTrue((ROOT/'web/assets/item-icons/partner_avatar_758001.png').is_file())

    def test_mail_claim_500_only_once_and_retains_exact_item_id(self):
        with tempfile.TemporaryDirectory(prefix='gxb3-sonia-shard-mail-') as directory:
            tmp=Path(directory)/'test-mail.sqlite3'
            original=database.connect
            with patch.object(live_service,'_db',lambda:original(tmp,'live')):
                live_service.register_player('SONIA-ADMIN','S1','Admin')
                live_service.register_player('SONIA-USER','S1','Player')
                mail=live_service.send_mail(
                    'SONIA-USER','S1','Player','Quà từ Admin','',
                    gm_catalog.validate_gift({'940061':500}),'TEST')
                inbox=live_service.mailbox('SONIA-USER','S1')
                self.assertEqual(len(inbox),1)
                self.assertEqual(inbox[0]['attachments']['940061'],500)
                received=live_service.claim_mail(mail['id'],'SONIA-USER','S1')
                self.assertEqual(received,{'940061':500})
                with self.assertRaises(ValueError):
                    live_service.claim_mail(mail['id'],'SONIA-USER','S1')
                inbox=live_service.mailbox('SONIA-USER','S1')
                self.assertEqual(inbox[0]['status'],'claimed')
                self.assertEqual(inbox[0]['attachments']['940061'],500)

if __name__=='__main__':
    unittest.main()
