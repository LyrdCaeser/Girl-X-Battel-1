"""Yume Collection (CollectionWindow / CollectionShopWindow, models/Collection.lua).

collection.lua: every collectable (type 1 skin, 2 anima gear, 3 avatar, 4 frame, 5 furniture, 6 background, 7 story item,
8 emoji, 9 outfit) with its item_id and collect points (awards / new_awards 123#n). shop_collection1 (Rare Store: once
ever) and shop_collection2 (Common Store: limits refresh every Monday): item, cost, collection_point gate, buy_time.
misc collection_point_level (500|1500|2500) gives the three stages. Output data/collection.json. Sources read only."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
T = Path.home() / 'Downloads/Decomp files/lua/data/tables'


def lua_table(path):
    text = path.read_text(encoding='utf-8-sig')
    keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', text.split('table.keys = {', 1)[1].split('}', 1)[0])}
    rows = {}
    for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\n\s*\}', text, re.S):
        vals = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p) for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
        rows[m.group(1)] = {k: vals[i] for k, i in keys.items() if i < len(vals)}
    return rows


rows = []
for r in lua_table(T / 'collection.lua').values():
    m = re.search(r'(?:^|\|)123#(\d+)', str(r.get('new_awards') or '') + '|' + str(r.get('awards') or ''))  # skins: new_awards is 377#n, the points are in awards
    rows.append([int(r['id']), int(r['type']), int(r['item_id'] or 0) or int(r.get('dress_id') or 0), int(m.group(1)) if m else 0])  # outfits: dress_id
shops = {}
for n in (1, 2):
    shops[str(n)] = [{'id': int(r['id']), 'item': r['item'], 'cost': r['cost'], 'point': int(r['collection_point']), 'limit': int(r['buy_time'])}
                     for r in sorted(lua_table(T / f'shop_collection{n}.lua').values(), key=lambda r: int(r['id']))]
import sqlite3
DB = sqlite3.connect(Path.home() / 'Downloads/Decomp files/data/en_en.db')
WEB = ROOT / 'web'
def icon(item):
    """Where the page finds each store item: frames / avatars in assets/profile, furniture in the Dorm assets."""
    iid = int(item.split('#')[0])
    for rel in (f'assets/profile/frame_{iid}.png', f'assets/profile/head_{iid - 20000000}.png' if iid > 20000000 else '',
                f'assets/original-ui/house-dress/img_{iid}.png'):
        if rel and (WEB / rel).exists(): return '/' + rel
    return ''
for rows_ in shops.values():
    for r in rows_:
        iid = int(r['item'].split('#')[0])
        row = DB.execute('select name from item_text_en_en where id = ?', (iid,)).fetchone()
        r['name'] = row[0] if row else ''; r['icon'] = icon(r['item'])
misc = (T / 'misc.lua').read_text(encoding='utf-8-sig')
levels = [int(x) for x in re.search(r'\tcollection_point_level = \{\s*"collection_point_level",\s*"([^"]*)"', misc).group(1).split('|')]
(ROOT / 'data/collection.json').write_text(json.dumps({'rows': rows, 'shops': shops, 'levels': levels}, separators=(',', ':')))
print(len(rows), 'collectables,', {k: len(v) for k, v in shops.items()}, 'levels', levels)
