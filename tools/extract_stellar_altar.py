"""Stellar Altar (StarryAltarWindow, starry_altar): the House Cosmos summon. Rows 1/3 are the regular Surprise /
Accumulate modes (Star Token 358), 2 the Limited Star Token row (396). Art: starry_altar_bg, logo, mode panels, shards.
Output data/stellar_altar.json + web/assets/stellar/. Sources in ~/Downloads are read only."""
import json, re, shutil
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
TEX = DEC / 'unity/Assets/hotres/textures'
OUT = ROOT / 'web/assets/stellar'; OUT.mkdir(parents=True, exist_ok=True)
text = (T / 'starry_altar.lua').read_text(encoding='utf-8-sig')
keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', text.split('table.keys = {', 1)[1].split('}', 1)[0])}
rows = {}
for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\}', text.split('table.rows = {', 1)[1], re.S):
    vals = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p) for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
    rows[m.group(1)] = {k: vals[i] for k, i in keys.items() if i < len(vals)}
(ROOT / 'data/stellar_altar.json').write_text(json.dumps(rows, separators=(',', ':')))
Image.open(TEX / 'scenes_big_web/starry_altar_bg.png').convert('RGB').save(OUT / 'starry_altar_bg.webp', 'WEBP', quality=84)
for f in ['starry_bg_jlxz_1', 'starry_bg_jlxz_2', 'starry_bg_jlxz_group_1', 'starry_bg_jlxz_group_2', 'starry_bg_jlxz_group_3']:
    Image.open(TEX / f'common_ui_texture_web/{f}.png').convert('RGBA').save(OUT / f'{f}.webp', 'WEBP', quality=86)
for n in ['starry_altar_en_en', 'starry_act_bg', 'starry_bg_d', 'starry_star_img_1', 'starry_star_img_2', 'starry_star_img_3', 'right_starry_altar_icon_h5', 'icon_358', 'icon_940059']:
    if (CUT / f'{n}.png').exists(): shutil.copy2(CUT / f'{n}.png', OUT / f'{n}.png')
print(sorted(rows), sorted(p.name for p in OUT.iterdir()))
