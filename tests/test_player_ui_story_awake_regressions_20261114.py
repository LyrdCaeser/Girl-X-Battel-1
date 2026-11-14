"""Regressions for player-facing stars, story playback and manual awakening."""
from pathlib import Path
import tempfile
import unittest

from gxb2 import engine

ROOT = Path(__file__).resolve().parents[1]


class PlayerUiStoryAwakeRegressions(unittest.TestCase):
    def test_formation_emblem_stays_inside_goddess_card(self):
        css=(ROOT/'web/campaign-flow.css').read_text(encoding='utf-8')
        self.assertIn('width:20px!important;height:14px!important',css)
        self.assertIn('font-size:8px',css)
        girl_css=(ROOT/'web/girl-ui.css').read_text(encoding='utf-8')
        self.assertIn('height:22px;max-width:66px',girl_css)

    def test_story_memory_mask_is_an_effect_not_an_opaque_picture(self):
        js=(ROOT/'web/story.js').read_text(encoding='utf-8')
        css=(ROOT/'web/story.css').read_text(encoding='utf-8')
        self.assertIn("const memory=L.cg==='memory_mask'",js)
        self.assertIn("if(L.cg&&!memory)",js)
        self.assertIn('.sp-cg.memory::before',css)
        self.assertIn('opacity:.16',css)

    def test_story_auto_waits_for_voice_and_reading(self):
        js=(ROOT/'web/story.js').read_text(encoding='utf-8')
        self.assertIn("addEventListener('ended',done",js)
        self.assertIn('autoGate.read',js)
        self.assertIn('autoGate.voice',js)
        self.assertNotIn('timer=setTimeout(next,800)',js)

    def test_awake_materials_are_chosen_by_player_not_first_match(self):
        js=(ROOT/'web/girl-ui.js').read_text(encoding='utf-8')
        self.assertIn('function chooseMaterial(',js)
        self.assertIn('Chạm từng ô để tự chọn Nữ Thần',js)
        self.assertIn("c.onclick=()=>chooseMaterial(hero,r,'normal',i,close)",js)
        self.assertIn("addGroup('Nữ Thần cùng tên'",js)
        self.assertNotIn('const g=pool[0]',js)

    def test_player_ui_has_no_internal_awake_or_bag_wording(self):
        sources='\n'.join((ROOT/p).read_text(encoding='utf-8') for p in (
            'web/girl-ui.js','web/app.js','web/game-assistant.js','web/events.js',
            'web/settings-menu.js','web/shops.js','web/home-menus.js','web/guild-lab.js',
            'web/skins.js','gxb2/bag_use.py'))
        for phrase in ('dữ liệu gốc','bảng gốc','tài nguyên thật','hình thái gốc',
                       'chức năng gốc trên máy chủ','dữ liệu nhà phát triển',
                       'dữ liệu máy chủ','Gói nguyên bản','Summons saved in your local save'):
            self.assertNotIn(phrase,sources)

    def test_compose_snapshot_has_numeric_target_level_cap(self):
        with tempfile.TemporaryDirectory(prefix='gxb3-compose-cap-') as folder:
            game=engine.Engine(Path(folder)/'state.sqlite3')
            try:
                game.db.execute('BEGIN IMMEDIATE')
                state=game._load()
                state['partners']=[{'partner_id':1234,'table_id':41001,'lv':1,'grade':0,
                                    'awake':0,'equips':[],'pos':0,'show_skin':1}]
                state['next_partner_id']=1235
                game._save_profile(state);game.db.commit()
                hero=next(x for x in game.snapshot()['roster'] if x['partner_id']==1234)
                recipe=hero['next_awake']
                self.assertEqual(recipe['kind'],'compose')
                target=engine.TABLES['partner'][str(recipe['target'])]
                self.assertEqual(recipe['target_level_cap'],int(target['max_lv']))
            finally:
                game.close()


if __name__ == '__main__':
    unittest.main()
