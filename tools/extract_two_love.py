"""Matching Pairs (activity 331, Activity2LoveWindow; capture 2026-09-29-fb/88): cards (activity_2love_awards), Recharge
Task (activity_2love_mission), cost (misc activity_2love_random_cost), texts and sprites.
Output data/two_love.json + web/assets/two-love/. Sources in ~/Downloads are read only."""
import json, re, shutil, sqlite3
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
SPR = Path.home() / 'Downloads/Decompiled'
CUT = SPR / 'Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/two-love'; OUT.mkdir(parents=True, exist_ok=True)


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
out = {'awards': lua_table(T / 'activity_2love_awards.lua'), 'missions': lua_table(T / 'activity_2love_mission.lua'), 'cost': g('activity_2love_random_cost'),
       'text': dict(db.execute("select name, translation from translation_en_en where name like 'ACTIVITY_2LOVE%'"))}
(ROOT / 'data/two_love.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
n = 0
for p in list(CUT.glob('activity_2love*.png')) + [CUT / 'icon_427.png', CUT / 'check_white_btn.png']:
    if p.stem.endswith(('_de_de', '_fr_fr', '_ja_jp', '_ko_kr', '_zh_tw')) or not p.exists(): continue
    shutil.copy2(p, OUT / p.name); n += 1
Image.open(SPR / 'Images (other)/activity_2love/activity_2love_bg.png').convert('RGBA').resize((1024, 1390), Image.LANCZOS).save(OUT / 'activity_2love_bg.webp', 'WEBP', quality=85)
print(len(out['awards']), 'cards,', len(out['missions']), 'missions,', n + 1, 'sprites')
