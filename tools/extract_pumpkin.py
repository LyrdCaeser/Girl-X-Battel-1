"""Halloween Pumpkin Patch (activity 150, ActivityHalloweenPumpkinField; capture 2026-09-29-fb/78): the 10 pumpkins' reward
rows and the round rewards (activity_halloween_award: rows 1-10 per pumpkin with weights, rows with times >= 1 are the round
rewards), the Pumpkin Dagger (182) purchase (misc halloween_buy / halloween_limit), texts and sprites.
Output data/pumpkin.json + web/assets/pumpkin/. Sources in ~/Downloads are read only."""
import json, re, shutil, sqlite3
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
SPR = Path.home() / 'Downloads/Decompiled'
CUT = SPR / 'Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/pumpkin'; OUT.mkdir(parents=True, exist_ok=True)


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
rows = lua_table(T / 'activity_halloween_award.lua')
db = sqlite3.connect(DEC / 'data/en_en.db')
out = {'pumpkins': [rows[str(i)] for i in range(1, 11)], 'rounds': [r for k, r in sorted(rows.items(), key=lambda x: int(x[0])) if int(r['times'] or 0) >= 1],
       'buy': g('halloween_buy'), 'limit': int(g('halloween_limit')),
       'text': dict(db.execute("select name, translation from translation_en_en where name like 'ACTIVITY_HALLOWEEN\\_%' escape '\\' and name not like 'ACTIVITY_HALLOWEEN2022%'"))}
(ROOT / 'data/pumpkin.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
n = 0
for p in list(CUT.glob('halloween_*.png')) + [CUT / 'icon_182.png', CUT / 'blue_btn_65_65.png']:
    if p.stem.endswith(('_de_de', '_fr_fr', '_ja_jp', '_ko_kr', '_zh_tw')): continue
    shutil.copy2(p, OUT / p.name); n += 1
im = Image.open(SPR / 'Images (backgrounds)/scenes/halloween_cut_bg.png').convert('RGB')
im.crop(im.convert('L').point(lambda v: 255 if v > 8 else 0).getbbox()).save(OUT / 'halloween_cut_bg.webp', 'WEBP', quality=84)
shutil.copy2(SPR / 'Images (other)/activity_text/halloween_name_en_en.png', OUT / 'halloween_name_en_en.png')
print(len(out['rounds']), 'rounds,', n + 2, 'sprites', out['buy'], out['limit'])
