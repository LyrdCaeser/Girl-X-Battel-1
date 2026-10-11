"""Wish Capsule (activity 140; capture 2026-09-29-fb/47): the draw-count rewards (activity_wish_gacha: limit, awards,
type 1 = repeatable), the Wish Girls and odds (misc wish_gacha_*), texts WISH_GACHA_* and sprites. The draws themselves
are summon ids 22-26 (summon.json, dropbox 10008). Output data/wish.json + web/assets/wish/. Sources are read only."""
import json, re, shutil, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
SPR = Path.home() / 'Downloads/Decompiled'
CUT = SPR / 'Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/wish'; OUT.mkdir(parents=True, exist_ok=True)


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
partner = json.loads((ROOT / 'data/partner.json').read_text())
db = sqlite3.connect(DEC / 'data/en_en.db')
out = {'rows': lua_table(T / 'activity_wish_gacha.lua'),
       'partners': [int(x) for x in g('wish_gacha_partners').split('|') if x in partner],
       'odds': {k: int(g('wish_gacha_' + k)) for k in ('weight_ini_total', 'weight_ini_get', 'weight_add', 'weight_add_num', 'guarantee', 'weight_special_start', 'weight_special_add')},
       'text': dict(db.execute("select name, translation from translation_en_en where name like 'WISH_GACHA%'"))}
(ROOT / 'data/wish.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
n = 0
for p in list(CUT.glob('wish_capsule_*.png')) + [CUT / 'activity_wish_gacha.png', CUT / 'summon_record_wish_icon.png', CUT / 'wish_up_tips.png']:
    if p.stem.endswith(('_de_de', '_fr_fr', '_ja_jp', '_ko_kr', '_zh_tw', '_zh_cn')): continue
    shutil.copy2(p, OUT / p.name); n += 1
for name in ('wish_capsule_detail_logo_en_en', 'activity_wish_capsule_logo_en_en'):
    shutil.copy2(SPR / 'Images (other)/activity_text' / f'{name}.png', OUT / f'{name}.png'); n += 1
print(len(out['rows']), 'reward rows,', len(out['partners']), 'wish girls,', n, 'sprites', out['odds'])
