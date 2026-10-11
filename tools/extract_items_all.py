"""Complete the item catalogue and icons. extract_inventory_assets.py only kept the items shown in the Bag (show_in_bag = 1)
and the icons found in two atlases; rewards, costs and event items outside the Bag had no name or picture. This adds every
row of item*.lua to web/assets/items-catalog.json (category 0 = not a Bag item, so the Bag tabs are unchanged) and copies
each missing icon from the cut sprites into web/assets/item-icons (+ item-icons.json). Sources are read only."""
import json, re, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
T = Path.home() / 'Downloads/Decomp files/lua/data/tables'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets'


def lua_table(path):
    t = path.read_text(encoding='utf-8-sig')
    if 'table.keys = {' not in t: return {}
    keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', t.split('table.keys = {', 1)[1].split('}', 1)[0])}
    rows = {}
    for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\n\s*\}', t, re.S):
        v = [json.loads(p) if p.startswith('"') else p for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
        rows[m.group(1)] = {k: v[i] for k, i in keys.items() if i < len(v)}
    return rows


items, text = {}, {}
for f in sorted(T.glob('item[0-9]*.lua')): items.update(lua_table(f))
for f in sorted((T / 'en_en').glob('item_text_en_en*.lua')): text.update(lua_table(f))
catalog = json.loads((OUT / 'items-catalog.json').read_text()); before = len(catalog)
num = lambda v: int(float(v)) if re.fullmatch(r'-?\d+(\.\d+)?', str(v or '')) else 0
for iid, row in items.items():
    if iid in catalog or not row.get('icon'): continue
    name = text.get(iid, {}).get('name')
    if not name or str(name) == '-1': continue
    catalog[iid] = {'id': int(iid), 'name': name, 'description': text.get(iid, {}).get('desc') or '', 'icon': str(row['icon']),
                    'quality': num(row.get('qlt')), 'category': 0, 'type': num(row.get('type'))}
have = set(json.loads((OUT / 'item-icons.json').read_text())); added = 0
for row in catalog.values():
    ic = row.get('icon')
    if ic and ic not in have and (CUT / f'{ic}.png').exists():
        shutil.copyfile(CUT / f'{ic}.png', OUT / 'item-icons' / f'{ic}.png'); have.add(ic); added += 1
(OUT / 'items-catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, separators=(',', ':')))
(OUT / 'item-icons.json').write_text(json.dumps(sorted(have)))
missing = sorted({r['icon'] for r in catalog.values() if r.get('icon') and r['icon'] not in have})
print(before, '→', len(catalog), 'items;', added, 'icons added;', len(have), 'icons;', len(missing), 'still missing', missing[:8])
