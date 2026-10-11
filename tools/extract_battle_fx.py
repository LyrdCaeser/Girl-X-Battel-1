"""Battle skill effects (fx*.lua + skill*.lua fx1 / fx_hurt1-3): the Spine effects played on the targets of a skill ("hurt",
fx type 2) and the area / cast effects at a fixed point of the field (type 1). A skill lists "base#skin1#skin2…" groups of
"a|b" fx ids; the base group is used. Each referenced skeleton (hero_web/<girl>/<res>, RGB + Alpha textures) becomes
web/assets/battle-fx/<res>/ (model.json, model.atlas, png) and web/assets/battle-fx/skills.json maps
skill id → {"h": [[res, anim, scale, layer, position]…], "c": [[res, anim, scale, layer, x, y, aoe]…]}.
Type 3 (summoned units) and projectiles' flight are not reproduced. Sources are read only.  Usage: [--dry]"""
import json, re, sys
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from spine36 import decode
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
SP = DEC / 'unity/Assets/hotres/spine'
OUT = ROOT / 'web/assets/battle-fx'; OUT.mkdir(parents=True, exist_ok=True)


def lua_table(path):
    t = path.read_text(encoding='utf-8-sig')
    if 'table.keys = {' not in t: return {}
    keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', t.split('table.keys = {', 1)[1].split('}', 1)[0])}
    rows = {}
    for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\n\s*\}', t, re.S):
        v = [p.strip('"') for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
        rows[m.group(1)] = {k: v[i] for k, i in keys.items() if i < len(v)}
    return rows


fx, skills = {}, {}
for f in sorted(T.glob('fx[0-9]*.lua')): fx.update(lua_table(f))
for f in sorted(T.glob('skill[0-9]*.lua')): skills.update(lua_table(f))
skel = {}
for base in (SP / 'hero', SP / 'hero_web'):
    for p in base.rglob('*.skel.bytes'): skel[p.name[:-len('.skel.bytes')]] = p
num = lambda v, d=0: float(v) if re.fullmatch(r'-?\d+(\.\d+)?', str(v or '')) else d
out, used = {}, set()
for sid, r in skills.items():
    hurt, cast = [], []
    for col in ('fx_hurt1', 'fx_hurt2', 'fx_hurt3', 'fx1'):
        group = str(r.get(col) or '').split('#')[0]
        for fid in group.split('|'):
            row = fx.get(fid)
            if not row or row.get('res_name') not in skel: continue
            t = row.get('type')
            if t == '2' or (col != 'fx1' and t == '1' and not row.get('is_aoe')):
                e = [row['res_name'], row.get('texiao_name') or '', num(row.get('scale'), 1), int(num(row.get('layer'))), int(num(row.get('position')))]
                if e not in hurt: hurt.append(e)
            elif t == '1':
                e = [row['res_name'], row.get('texiao_name') or '', num(row.get('scale'), 1), int(num(row.get('layer'))), num(row.get('x'), 360), num(row.get('y'), 640), int(num(row.get('is_aoe')))]
                if e not in cast: cast.append(e)
            else: continue
            used.add(row['res_name'])
    if hurt or cast: out[sid] = {k: v for k, v in (('h', hurt), ('c', cast)) if v}
print(len(out), 'skills with effects,', len(used), 'skeletons,', round(sum(sum(f.stat().st_size for f in skel[n].parent.glob('*.png')) for n in used) / 1e6), 'MB of source textures')
if '--dry' in sys.argv: sys.exit()
done = fail = 0
only = [a.split('=')[1] for a in sys.argv if a.startswith('--only=')]
for n in (only or sorted(used)):
    folder = OUT / n
    if (folder / 'model.json').exists(): continue
    try:
        src = skel[n]; folder.mkdir(exist_ok=True)
        atlas = src.with_name(n + '.atlas.txt').read_text()
        for page in re.findall(r'^([^\r\n]+\.png)\r?$', atlas, re.M):
            rgb = src.parent / (Path(page).stem + '_RGB.png'); alpha = src.parent / (Path(page).stem + '_Alpha.png')
            im = Image.open(rgb).convert('RGBA')
            if alpha.exists(): im.putalpha(Image.open(alpha).convert('RGB').getchannel('R'))
            im.save(folder / (Path(page).stem + '.webp'), 'WEBP', quality=88, method=4)
            atlas = atlas.replace(page, Path(page).stem + '.webp')
        (folder / 'model.atlas').write_text(atlas)
        (folder / 'model.json').write_text(json.dumps(decode(src.read_bytes()), separators=(',', ':')))
        done += 1
    except Exception as e:
        fail += 1; used.discard(n); print('FAIL', n, e)
if only: sys.exit()
for sid in list(out):
    for k in list(out[sid]):
        out[sid][k] = [e for e in out[sid][k] if e[0] in used]
        if not out[sid][k]: del out[sid][k]
    if not out[sid]: del out[sid]
(OUT / 'skills.json').write_text(json.dumps(out, separators=(',', ':')))
print('converted', done, 'failed', fail, '→', len(out), 'skills')
