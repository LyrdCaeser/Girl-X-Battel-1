"""Tree of Chimes (ChimeMainWindow / ChimeDetailWindow / ChimeDebrisBackpackWindow / ChimePokedexWindow; Shrine models): the ten
Chimes (chime: base attrs, 4 buffs with limit / cost, unlock shards, quality, sort, Spine), Chimelight cost per level by quality
(chime_lv_cost), shard transfer to Chime Chips (chime_decompose), texts (chime_text, CHIME_*), the tree Spine yushenmu_main, the
Chime Spines fengling_* and the charge / unlock effects, and the window sprites.
Output data/chimes.json + web/assets/chimes/ + web/assets/spine/<name>/. Sources in ~/Downloads are read only."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from spine36 import decode
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
SPR = Path.home() / 'Downloads/Decompiled'
CUT = SPR / 'Sprites (atlases, cut)'
ANIM = SPR / 'Animation (Misc)/Misc/chime'
OUT = ROOT / 'web/assets/chimes'; OUT.mkdir(parents=True, exist_ok=True)


def lua_table(path):
    text = path.read_text(encoding='utf-8-sig')
    keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', text.split('table.keys = {', 1)[1].split('}', 1)[0])}
    rows = {}
    for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\}', text.split('table.rows = {', 1)[1], re.S):
        vals = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p) for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
        rows[m.group(1)] = {k: vals[i] for k, i in keys.items() if i < len(vals)}
    return rows


db = sqlite3.connect(DEC / 'data/en_en.db')
out = {'chimes': lua_table(T / 'chime.lua'), 'lv_cost': lua_table(T / 'chime_lv_cost.lua'), 'decompose': lua_table(T / 'chime_decompose.lua'),
       'names': {str(r[0]): {'name': r[1], 'buffs': [r[2], r[3], r[4], r[5]]} for r in db.execute('select * from chime_text_en_en')},
       'items': {str(r[0]): r[1] for r in db.execute('select id, name from item_text_en_en where id in (325,326,373,982001,983001,984001,985001,986001) or (id between 984001 and 986010)')},
       'text': dict(db.execute("select name, translation from translation_en_en where name like 'CHIME\\_%' escape '\\'"))}
(ROOT / 'data/chimes.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
spines = ['yushenmu_main', 'chime_levelup', 'chime_unlock', 'chime_skill'] + sorted({r['resource'] for r in out['chimes'].values()})
for name in spines:
    src = next((d for d in ANIM.iterdir() if d.is_dir() and (d.name == name or any(d.glob(name + '.skel')))), None)
    if not src: print('missing spine', name); continue
    dst = ROOT / 'web/assets/spine' / name; dst.mkdir(parents=True, exist_ok=True)
    (dst / 'model.json').write_text(json.dumps(decode((src / f'{name}.skel').read_bytes()), separators=(',', ':')))
    atlas = (src / f'{name}.atlas').read_text()
    for page in re.findall(r'^([^\r\n]+\.png)\r?$', atlas, re.M): shutil.copy2(src / page, dst / page)
    (dst / 'model.atlas').write_text(atlas)
n = 0
for p in list(CUT.glob('chime_*.png')) + list(CUT.glob('fengling_*.png')) + [CUT / f'{x}.png' for x in ('icon_325', 'icon_326', 'icon_373', 'icon_tj', 'icon_sp', 'lock', 'alert_icon', 'help_2')]:
    if p.stem.endswith(('_de_de', '_fr_fr', '_ja_jp', '_ko_kr', '_zh_tw', '_zh_cn')) or not p.exists(): continue
    shutil.copy2(p, OUT / p.name); n += 1
print(len(out['chimes']), 'chimes,', len(out['lv_cost']), 'levels,', len(spines), 'spines,', n, 'sprites')
# ChimeMainWindow background (chime_bg_ysm, the purple tree), the cord of each row (layerItem bg, chime_bg_ysm_x) and the
# ChimeDetailWindow frames (chime_web: tc / tc1 / spd / spd1)
from PIL import Image
_bg = Image.open(SPR / 'Images (backgrounds)/scenes/chime_bg_ysm.png').convert('RGB')  # 1024² texture, picture in the middle
_bg.crop(_bg.convert('L').point(lambda v: 255 if v > 12 else 0).getbbox()).save(OUT / 'chime_bg_ysm.webp', 'WEBP', quality=84)
for name in ('chime_bg_ysm_x', 'chime_bg_ysm_tc', 'chime_bg_ysm_tc1', 'chime_bg_ysm_spd', 'chime_bg_ysm_spd1'):
    shutil.copy2(DEC / f'unity/Assets/hotres/textures/chime_web/{name}.png', OUT / f'{name}.png')
