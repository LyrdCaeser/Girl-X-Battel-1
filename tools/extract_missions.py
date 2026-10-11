"""Daily tasks and trophies data (daily_mission, achievement, achievement_type + English texts) and window art."""
import json, shutil, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/missions'; OUT.mkdir(parents=True, exist_ok=True)
d = sqlite3.connect(DEC / 'data/data.db'); en = sqlite3.connect(DEC / 'data/en_en.db')
dt = dict(en.execute('select id, mission_des from daily_mission_text_en_en')) if 'mission_des' in [x[0] for x in en.execute('select * from daily_mission_text_en_en limit 1').description] else dict(en.execute('select * from daily_mission_text_en_en'))
at = dict(en.execute('select id, desc from achievement_text_en_en'))
daily = [{'id': r[0], 'complete_value': r[2], 'award': r[3], 'coefficient': r[4], 'lv_limit': r[5], 'go_window': r[6], 'rank': r[8], 'text': dt.get(r[0], '')}
         for r in d.execute('select * from daily_mission')]
ach = [{'id': int(r[0]), 'next': r[2], 'complete_value': r[3], 'award': r[4]} for r in d.execute('select * from achievement')]
types = [{'id': int(r[0]), 'start': int(r[1]), 'end': int(r[2]), 'text': at.get(r[0], '')} for r in d.execute('select * from achievement_type') if at.get(r[0])]
(ROOT / 'data/missions.json').write_text(json.dumps({'daily': daily, 'achievements': ach, 'types': types}, ensure_ascii=False))
for n in ('mission_bg', 'mission_item_bg', 'mission_icon', 'achievement_icon', 'daily_mission_icon', 'btn_get', 'progress_bar_bg', 'progress_bar_thumb',
          'activity_bar_bg', 'activity_bar_thumb', 'icon_check', 'blue_btn_65_65', 'white_btn_65_65', 'nav_btn_blue_left', 'nav_btn_blue_right',
          'nav_btn_white_left', 'nav_btn_white_right', 'right_mission_icon_v3_h5', 'left_task_icon_v3_h5', 'left_mission_icon', 'main_mission_icon'):
    if (CUT / f'{n}.png').exists():
        shutil.copyfile(CUT / f'{n}.png', OUT / f'{n}.png')
print(len(daily), 'daily;', len(ach), 'trophy steps;', len(types), 'trophy types;', len(list(OUT.glob('*'))), 'sprites')
