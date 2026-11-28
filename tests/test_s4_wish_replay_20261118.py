"""Read-only S4 Wish replay security and inventory tests: no production DB."""
import inspect
import json
import unittest
from gxb2 import s4_exclusive, goddess_gifts
from gxb2.engine import new_state
from server import HTTPHandler

class S4WishReplayTests(unittest.TestCase):
    def test_replay_requires_claimed_s4_not_s1(self):
        state=new_state()
        state['server_id']='S1'
        with self.assertRaisesRegex(ValueError,'S4'):
            s4_exclusive.replay_payload(state)
        state['server_id']='S4'
        with self.assertRaisesRegex(ValueError,'Chưa nhận'):
            s4_exclusive.replay_payload(state)

    def test_replay_gift_non_mutating_and_exact_items(self):
        s=new_state()
        s.update({'uid':'TEST-FAKE-REPLAY-UID','server_id':'S4'})
        result=s4_exclusive.grant_bundle(s,1,lambda *a,**kw:666)
        before=json.dumps(s,sort_keys=True)
        replay=s4_exclusive.replay_payload(s)
        self.assertEqual(before,json.dumps(s,sort_keys=True),'Replay must never save/grant again')
        self.assertEqual(len(replay['goddesses']),104)
        self.assertEqual(replay['skin_count'],324)
        self.assertTrue(replay['replay'])
        self.assertFalse(replay['granted'])
        self.assertEqual(replay['catalog_total'],104)
        self.assertEqual(replay['skin_catalog_total'],324)
        self.assertEqual(set(replay['skin_ids']),set(result['skin_ids']))
        self.assertEqual(len(replay['skin_details']),324)
        self.assertTrue(all(isinstance(x['partners'],list) for x in replay['skin_details']))
        self.assertEqual(len({p['table_id'] for p in replay['goddesses']}),104)

    def test_replay_shows_exact_current_inventory_not_all_catalog(self):
        s=new_state()
        s['server_id']='S4';s['s4_exclusive_claimed']=True
        s['partners']=[]
        valid=s4_exclusive._source_goddesses()
        for tid in valid[:2]:
            s['partners'].append({'table_id':tid,'awake':15})
        s['partners'].append({'table_id':valid[2],'awake':14})
        s['skins']={'collected':list(s4_exclusive._skin_ids(valid)[:3])}
        before=json.dumps(s,sort_keys=True)
        p=s4_exclusive.replay_payload(s)
        self.assertEqual(before,json.dumps(s,sort_keys=True),
                         'Even old profiles must not mutate on replay')
        self.assertEqual(p['wish_count'],2)
        self.assertEqual(p['skin_count'],3)

    def test_route_is_authenticated_and_read_only(self):
        source=inspect.getsource(HTTPHandler.do_GET)
        auth_marker=source.index("if path.startswith('/api/') and not self.require_auth()")
        marker=source.index("if path == '/api/s4/wish/replay':")
        self.assertGreater(marker,auth_marker)
        route=source[marker:source.index("if path == '/api/state':",marker)]
        self.assertIn("account']['server_id'] != 'S4'",route)
        self.assertIn('self.engine.s4_wish_replay()',route)
        self.assertIn("Cache-Control': 'no-store'",route)
        self.assertNotIn('grant_bundle',route)

if __name__=='__main__':
    unittest.main()
