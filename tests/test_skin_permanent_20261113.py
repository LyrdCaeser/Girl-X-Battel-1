"""Permanent account-wide costume entitlements, including old saves and new copies.

Pure in-memory player states; never reads/writes any production or Neon database.
"""
import unittest
from unittest.mock import patch

from gxb2 import equipment, skins


class PermanentSkinOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skin_id, cls.skin = next((sid, row) for sid, row in skins.SKINS.items()
                                      if row.get('partners'))
        cls.partner_table = cls.skin['partners'][0]

    def hero(self, uid, wearing=0, table_id=None):
        slots = [0] * 7
        slots[6] = wearing
        return {'partner_id':uid, 'table_id':table_id or self.partner_table, 'equips':slots,
                'show_skin':1, 'stars':5, 'lv':1}

    def test_legacy_bag_item_unlocks_every_existing_and_future_copy(self):
        sid = self.skin_id
        first, second = self.hero(101), self.hero(102)
        state = {'items':{str(sid):1}, 'partners':[first,second]}
        for uid in (101,102):
            skins.action(state, {'action':'equip','partner_id':uid,'skin':sid})
        self.assertEqual(first['equips'][6],sid)
        self.assertEqual(second['equips'][6],sid)
        self.assertEqual(state['items'][str(sid)],1)  # no per-instance consumption
        skins.action(state, {'action':'unequip','partner_id':101})
        self.assertEqual(first['equips'][6],0)
        self.assertEqual(second['equips'][6],sid)
        later = self.hero(103)
        state['partners'].append(later)
        skins.action(state, {'action':'equip','partner_id':103,'skin':sid})
        self.assertEqual(later['equips'][6],sid)
        self.assertEqual(skins.snapshot(state)['owned'][str(sid)],1)

    def test_legacy_worn_only_costume_survives_unequip_and_removal(self):
        sid = self.skin_id
        legacy = self.hero(201,wearing=sid)
        state = {'items':{},'partners':[legacy,self.hero(202)]}
        skins.action(state, {'action':'unequip','partner_id':201})
        self.assertEqual(legacy['equips'][6],0)
        self.assertIn(sid,state['skins']['collected'])
        skins.action(state, {'action':'equip','partner_id':202,'skin':sid})
        self.assertEqual(state['partners'][1]['equips'][6],sid)

    def test_consuming_goddess_does_not_duplicate_permanent_skin_items(self):
        sid = self.skin_id
        legacy = self.hero(301,wearing=sid)
        state={'items':{},'partners':[legacy]}
        with patch('gxb2.souls.release',return_value=None):
            equipment.release(state,legacy)
        self.assertEqual(legacy['equips'][6],0)
        self.assertNotIn(str(sid),state['items'])
        self.assertIn(sid,state['skins']['collected'])
        state['partners'].append(self.hero(302))
        skins.action(state, {'action':'equip','partner_id':302,'skin':sid})
        self.assertEqual(state['partners'][1]['equips'][6],sid)

    def test_unowned_skin_cannot_be_equipped_or_used_by_other_goddess(self):
        sid=self.skin_id
        state={'items':{},'partners':[self.hero(401)]}
        with self.assertRaisesRegex(ValueError,'chưa mở khóa'):
            skins.action(state,{'action':'equip','partner_id':401,'skin':sid})
        different=next((x for x in skins.SKINS.values()
                        if x.get('partners') and self.partner_table not in x.get('partners')))
        other_table=different['partners'][0]
        state['partners'].append(self.hero(402,table_id=other_table))
        state['items'][str(sid)]=1
        with self.assertRaisesRegex(ValueError,'không thuộc'):
            skins.action(state,{'action':'equip','partner_id':402,'skin':sid})


if __name__ == '__main__':
    unittest.main()
