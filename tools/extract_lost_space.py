"""Lost Space Zone (activity 292, ActivityLostSpaceMapWindow; capture 2026-09-29-fb/62): zones (activity_lost_space_awards:
award, export_step, treasure_step, if_treasure), boxes (activity_lost_space_boxes, groups 1-3), events and lasers (+ texts),
radar purchase (misc activity_lost_space_buy_cost / _buy_limit), texts and sprites.
Output data/lost_space.json + web/assets/lost-space/. Sources in ~/Downloads are read only."""
import json, re, shutil, sqlite3
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
SPR = Path.home() / 'Downloads/Decompiled'
CUT = SPR / 'Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/lost-space'; OUT.mkdir(parents=True, exist_ok=True)


def lua_table(path):
    text = path.read_text(encoding='utf-8-sig')
    keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', text.split('table.keys = {', 1)[1].split('}', 1)[0])}
    rows = {}
    for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\}', text.split('table.rows = {', 1)[1], re.S):
        vals = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p) for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
        rows[m.group(1)] = {k: vals[i] for k, i in keys.items() if i < len(vals)}
    return rows


misc = (T / 'misc.lua').read_text(encoding='utf-8-sig')
g = lambda k: re.search(r'\t' + k + r' = \{\s*"' + k + r'",\s*"([^"]*)"', misc).group(1)
db = sqlite3.connect(DEC / 'data/en_en.db')
out = {'awards': lua_table(T / 'activity_lost_space_awards.lua'), 'boxes': lua_table(T / 'activity_lost_space_boxes.lua'),
       'events': lua_table(T / 'activity_lost_space_event.lua'), 'skills': lua_table(T / 'activity_lost_space_skill.lua'),
       'event_text': {str(r[0]): {'name': r[1], 'icon': r[2], 'desc': r[3]} for r in db.execute('select * from activity_lost_space_event_text_en_en')},
       'skill_text': {str(r[0]): {'name': r[1], 'icon': r[3], 'desc': r[4]} for r in db.execute('select * from activity_lost_space_skill_text_en_en')},
       'buy_cost': g('activity_lost_space_buy_cost'), 'buy_limit': int(g('activity_lost_space_buy_limit')),
       'text': dict(db.execute("select name, translation from translation_en_en where name like 'ACTIVITY_LOST_SPACE%'"))}
(ROOT / 'data/lost_space.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
n = 0
for p in list(CUT.glob('activity_lost_space*.png')) + [CUT / f'{x}.png' for x in ('icon_349', 'icon_350', 'icon_355', 'icon_356', 'btn_tips', 'btn_award')]:
    if p.stem.endswith(('_de_de', '_fr_fr', '_ja_jp', '_ko_kr', '_zh_tw')) or not p.exists() or 'giftbag' in p.stem: continue
    shutil.copy2(p, OUT / p.name); n += 1
Image.open(SPR / 'Images (backgrounds)/scenes/activity_lost_space_bg_banner.png').convert('RGB').save(OUT / 'activity_lost_space_bg_banner.webp', 'WEBP', quality=82)
Image.open(SPR / 'Images (other)/common_ui_texture/activity_lost_space_bg_di.png').convert('RGBA').save(OUT / 'activity_lost_space_bg_di.webp', 'WEBP', quality=85)
print(len(out['awards']), 'zones,', len(out['boxes']), 'boxes,', n + 2, 'sprites')
