"""Beach Treasure Hunt (activity 309, ActivitySandSearch / ActivitySandMission / ActivitySandShop): the sandcastle
(activity_sand_gamble: 32×10, 10×50, 5×100 point shells + Water Ball / Hermit Crab / Water Valve), round rewards
(activity_sand_award: 160 / 320 / 640 points per round), Midsummer Task (activity_sand_mission + texts) and the Ocean Coin
Exchange (activity_sand_shop). Output data/ev_sand.json + web/assets/ev-sand/. Sources in ~/Downloads are read only."""
import json, re, shutil, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/ev-sand'; OUT.mkdir(parents=True, exist_ok=True)


def lua_table(path):
    text = path.read_text(encoding='utf-8-sig')
    keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', text.split('table.keys = {', 1)[1].split('}', 1)[0])}
    rows = {}
    for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\}', text.split('table.rows = {', 1)[1], re.S):
        vals = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p) for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
        rows[m.group(1)] = {k: vals[i] for k, i in keys.items() if i < len(vals)}
    return rows


db = sqlite3.connect(DEC / 'data/en_en.db')
tr = dict(db.execute("select name, translation from translation_en_en where name like 'ACTIVITY_SAND%'"))
mission_text = {str(r[0]): r[1] for r in db.execute('select * from activity_sand_mission_text_en_en')}
shop = lua_table(T / 'activity_sand_shop.lua')
ids = sorted({p.split('#')[0] for r in shop.values() for p in str(r['awards']).split('|') if '#' in p} | {'390', '391'})
names = {str(r[0]): r[1] for r in db.execute('select id, name from item_text_en_en where id in (%s)' % ','.join(ids))}
out = {'gamble': lua_table(T / 'activity_sand_gamble.lua'), 'award': lua_table(T / 'activity_sand_award.lua'), 'mission': lua_table(T / 'activity_sand_mission.lua'),
       'shop': shop, 'mission_text': mission_text, 'text': tr, 'names': names}
(ROOT / 'data/ev_sand.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
n = 0
for p in CUT.glob('activity_sand_*.png'):
    if p.stem.endswith(('_de_de', '_fr_fr', '_ja_jp', '_ko_kr', '_zh_tw')): continue
    shutil.copy2(p, OUT / p.name); n += 1
for name in ('icon_390', 'icon_391'):
    if (CUT / f'{name}.png').exists(): shutil.copy2(CUT / f'{name}.png', OUT / f'{name}.png')
print(len(out['award']), 'rounds,', len(shop), 'shop rows,', len(out['mission']), 'missions,', n, 'sprites')
from PIL import Image
TEX = DEC / 'unity/Assets/hotres/textures'
for src in [TEX / 'common_ui_texture_web/activity_sand_search_bg.png', TEX / 'common_ui_texture_web/activity_sand_search_bg2.png', TEX / 'scenes_web/activity_sand_mission_bg.png']:
    Image.open(src).convert('RGBA').save(OUT / (src.stem + '.webp'), 'WEBP', quality=85)
