"""Global regressions from real Android screenshots: never fake ranks/stars.

Isolated SQLite for rankings; no writes to player Neon/Production state.
"""
from pathlib import Path
import tempfile
import unittest

from gxb2 import live_service, protocol

ROOT = Path(__file__).resolve().parents[1]


class SystemicVisualDataRegressions(unittest.TestCase):
    def test_25_star_formation_uses_shared_original_star_renderer(self):
        source=(ROOT/'web/campaign-flow.js').read_text()
        self.assertIn("GirlUI.stars(star,'card')",source)
        self.assertNotIn('Math.min(4,star-5)',source)
        self.assertIn("st.setAttribute('aria-label',star+'★')",source)
        self.assertIn('.cf-stars .gu-stars .gu-emblem',
                      (ROOT/'web/campaign-flow.css').read_text())
        self.assertIn('potentiality_card_star', (ROOT/'web/girl-ui.js').read_text())

    def test_awaken_tab_shows_original_materials_not_only_redirect(self):
        source=(ROOT/'web/girl-ui.js').read_text()
        self.assertIn("el('div','lb-inline-materials')",source)
        self.assertIn('r.material||[]',source)
        self.assertIn('materialsReady(r,picked)',source)
        self.assertIn("go.onclick=()=>limitBreak(hero)",source)

    def test_oversized_original_luajit_damage_does_not_rollback_wire_encoding(self):
        # Exact overflow pictured at 4-2: this exceeds protobuf int32, but
        # is a legitimate 64-bit LuaJIT battle damage accumulator.
        damage=3_192_954_487
        payload=protocol.defaults('battle_data');payload['total_harm']=damage
        encoded=protocol.encode('battle_data',payload)
        message=protocol.decode('battle_data',encoded)
        self.assertEqual(payload['total_harm'],damage,'Full authority report must stay exact')
        self.assertEqual(message['total_harm'],2**31-1,
                         'Only legacy protobuf wire value is capped')
        regular=protocol.defaults('battle_data');regular['total_harm']=500_200
        self.assertEqual(protocol.decode('battle_data',protocol.encode('battle_data',regular))['total_harm'],500_200)
        for bad in (-1,2.1,True):
            with self.assertRaises(ValueError):
                protocol.encode('battle_data',{**regular,'total_harm':bad})

    def test_rankings_only_have_actual_authoritative_fights_and_keep_modes_separate(self):
        if getattr(live_service.database,'POSTGRES',False):
            self.skipTest('Do not run temporary fixtures on Neon')
        with tempfile.TemporaryDirectory(prefix='gxb3-real-pvp-rank-') as dirpath:
            before=live_service.DB_PATH
            live_service.DB_PATH=Path(dirpath)/'live.sqlite3'
            try:
                for uid in ('P11','P22','P33'):
                    live_service.register_player(uid,'S1',uid)
                self.assertEqual(live_service.pvp_rating_board('arena',server_id='S1'),[])
                self.assertEqual(live_service.pvp_rating_board('arena3v3',server_id='S1'),[])
                # A queue entry or an unplayed registered account does not
                # prove performance. No fabricated #1..N with 1000 Elo.
                live_service.enqueue_pvp('P11','S1','P11','arena',1200)
                self.assertEqual(live_service.pvp_rating_board('arena',server_id='S1'),[])
                matched=live_service.enqueue_pvp('P22','S1','P22','arena',1300)
                result=live_service.finish_authoritative_pvp(matched['match']['id'],'P11',
                    {'uid':'P11','server_id':'S1','name':'P11','power':1200,'team':[]},
                    {'uid':'P22','server_id':'S1','name':'P22','power':1300,'team':[]},
                    {'isWin':1,'frames':[],'total_round':1})
                self.assertEqual(result['status'],'finished')
                board=live_service.pvp_rating_board('arena',server_id='S1')
                self.assertEqual([r['uid'] for r in board],['P11','P22'])
                self.assertTrue(all(r['matches']==1 for r in board))
                self.assertEqual([r['rank'] for r in board],[1,2])
                self.assertEqual(live_service.pvp_rating_board('arena3v3',server_id='S1'),[])
                self.assertEqual(live_service.pvp_rating_board('cross',server_id=None),[])
            finally:
                live_service.DB_PATH=before

    def test_all_153_archived_4_to_5_and_5_to_6_recipes_keep_real_source(self):
        from gxb2.engine import TABLES, COMPOSE_BY_SOURCE
        rows=TABLES['partner']
        self.assertEqual(len(rows),647)
        counts={4:0,5:0}
        for tid,recipe in COMPOSE_BY_SOURCE.items():
            self.assertIn(str(tid),rows)
            star=int(rows[str(tid)].get('max_star') or 0)
            self.assertIn(star,(4,5))
            self.assertEqual(recipe['source'],tid)
            self.assertIn(str(recipe['target']),rows)
            self.assertTrue(recipe['material'])
            counts[star]+=1
        # Other 5-star forms can be the terminal result of evolving a 4-star
        # Goddess or an archived material template. Do not invent recipes.
        self.assertEqual(counts,{4:38,5:115})
        self.assertEqual(len(COMPOSE_BY_SOURCE),153)

    def test_mobile_battle_hp_anchors_use_full_width_not_legacy_46_percent(self):
        css=(ROOT/'web/mobile-native.css').read_text(encoding='utf-8')
        self.assertIn('html.gxb-mobile #app-frame .battlefield>.units',css)
        self.assertIn('width:100%!important;max-width:none!important',css)
        self.assertIn('position:absolute!important;inset:0!important',css)
        index=(ROOT/'web/index.html').read_text(encoding='utf-8')
        for filename in ('mobile-native.css','arena.js','arena.css','arena-online-native.js'):
            self.assertIn(filename+'?v=20261114-systemic-r1',index)
        for filename in ('campaign-flow.js','campaign-flow.css','girl-ui.js','girl-ui.css'):
            self.assertIn(filename+'?v=20261114-player-fix-r2',index)

    def test_arena_rank_list_uses_actual_profile_photo_for_own_account(self):
        arena=(ROOT/'web/arena.js').read_text()
        native=(ROOT/'web/arena-online-native.js').read_text()
        self.assertIn('state?.profile?.avatar||p.avatar',arena)
        self.assertIn("profileAsset(state?.profile?.avatar||'head_1001')",native)
        self.assertIn("'Chưa đấu'",native)
        self.assertNotIn('state.roster[0].table_id,100',native)

if __name__ == '__main__':
    unittest.main()
