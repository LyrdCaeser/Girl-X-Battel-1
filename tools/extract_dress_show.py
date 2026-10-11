"""Outfit Showcase (models/DressShow.lua, DressShowWindow; capture 2026-09-29-fb/40): 4 booths (show_window) of 15 slots
(show_window_slot: row type 1-3 = Courage / Charisma / Knowledge booth, unlock chain + condition, placement requirement
add_type/add_num), daily rewards by booth score (show_window_award, rating misc show_window_point_rank) and the Showcase
Store (show_window_shop2 / shop3, Rare Tag 314 / Metal Tag 315, weekly refresh). Output data/dress_show.json +
web/assets/dress-show/. Sources in ~/Downloads are read only."""
import json, re, shutil, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/dress-show'; OUT.mkdir(parents=True, exist_ok=True)


def lua_table(path):
    text = path.read_text(encoding='utf-8-sig')
    keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', text.split('table.keys = {', 1)[1].split('}', 1)[0])}
    rows = {}
    for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\}', text.split('table.rows = {', 1)[1], re.S):
        vals = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p) for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
        rows[m.group(1)] = {k: vals[i] for k, i in keys.items() if i < len(vals)}
    return rows


db = sqlite3.connect(DEC / 'data/en_en.db')
misc = (T / 'misc.lua').read_text(encoding='utf-8-sig')
g = lambda k: re.search(r'\t' + k + r' = \{\s*"' + k + r'",\s*"([^"]*)"', misc).group(1)
tx = lambda t: {str(r[0]): r[1] for r in db.execute(f'select * from {t}')}
out = {'windows': lua_table(T / 'show_window.lua'), 'slots': lua_table(T / 'show_window_slot.lua'), 'awards': lua_table(T / 'show_window_award.lua'),
       'shop1': lua_table(T / 'show_window_shop1.lua'),  # skill buffs: skill, num battles, max_time stacks, func_id, cost, buy_time, item_icon
       'shop1_text': {str(r[0]): [r[1], r[2], r[3]] for r in db.execute('select id, name, desc1, desc2 from show_window_shop1_text_en_en')},
       'shop2': lua_table(T / 'show_window_shop2.lua'), 'shop3': lua_table(T / 'show_window_shop3.lua'),
       'rank': [int(x) for x in g('show_window_point_rank').split('|')], 'refresh': int(g('show_window_shop_refresh')),
       'unlock_text': {str(r[1]): [r[2], r[3]] for r in db.execute('select * from show_window_slot_unlock_text_en_en')},
       'add_text': {f'{r[1]}:{r[2]}': r[3] for r in db.execute('select * from show_window_slot_add_text_en_en')},
       'text': dict(db.execute("select name, translation from translation_en_en where name like 'SHOW_WINDOW_TEXT%'"))}
(ROOT / 'data/dress_show.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
n = 0
for p in CUT.glob('dress_show_*.png'):
    if p.stem.endswith(('_de_de', '_fr_fr', '_ja_jp', '_ko_kr', '_zh_tw')): continue
    shutil.copy2(p, OUT / p.name); n += 1
from PIL import Image
SCENES = Path.home() / 'Downloads/Decompiled/Images (backgrounds)/scenes'
for name in ('dress_show_entrance_bg', 'dress_show_main_bg'):  # 1024x2048 textures shown at 1000x1559
    Image.open(SCENES / f'{name}.png').convert('RGB').resize((1000, 1559), Image.LANCZOS).save(OUT / f'{name}.webp', 'WEBP', quality=82)
for name in ('shop', 'memory_list_lock', 'help_2', 'lock_icon', 'altar_add_bg', 'partner_detail_arrow', 'alert_icon', '9gongge16'):
    shutil.copy2(CUT / f'{name}.png', OUT / f'{name}.png')
for name in ('icon_314', 'icon_315'):
    if (CUT / f'{name}.png').exists(): shutil.copy2(CUT / f'{name}.png', OUT / f'{name}.png')
print(len(out['slots']), 'slots,', len(out['awards']), 'award tiers,', n, 'sprites', out['rank'])
