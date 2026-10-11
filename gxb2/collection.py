"""Yume Collection points and Collection Store (CollectionWindow / CollectionShopWindow, models/Collection.lua) offline.

Recovered from the client (data/collection.json, tools/extract_collection.py):
- collection.lua lists every collectable by type (1 skin, 2 antique, 3 avatar, 4 frame, 5 furniture, 6 background,
  7 story item, 8 emoji, 9 outfit) with its item and its collect points (123#n); the points of everything collected add up.
- Collection Store: Rare Store (shop_collection1) and Common Store (shop_collection2); each row needs
  collection_point Collect Points (stages misc collection_point_level 500 / 1500 / 2500), costs gold or gems and can be
  bought buy_time times. Rare limits never refresh; Common limits refresh every Monday (COLLECTION_SHOP_HELP).

LOCAL decisions (DESIGN_DECISIONS.md LOCAL-068): the server kept the list of collected ids. Here an id counts as
collected when its item is owned: skins through skins.collected (bag, worn or once owned), antiques in the bag or equipped, outfits through the Outfit pieces, and every other type through the bag. Weeks follow the local clock (LOCAL-057).
"""
from __future__ import annotations
import json
from pathlib import Path
from . import clock

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/collection.json').read_text())
ROWS = DATA['rows']            # [id, type, item_id, points]
SHOPS = {int(k): v for k, v in DATA['shops'].items()}
LEVELS = DATA['levels']
RARE, COMMON = 1, 2
# CollectionWindow entrances: type(s) of collection.lua each one counts
NODES = {'skin': [1], 'frame': [3, 4], 'soul': [2], 'story': [7], 'furniture': [5], 'face': [8], 'bg': [6]}


class CollectionError(ValueError):
    pass


def pair(text):
    k, n = str(text).split('#')[:2]
    return k, int(n)


def owned_ids(state):
    """collection.lua ids you have collected."""
    items = state.get('items', {})
    have = lambda k: int(items.get(str(k), 0)) > 0
    try:
        from . import skins
        skin_got = skins.collected(state)
    except Exception:
        skin_got = set()
    gear = {int(r.get('table_id', 0)) for r in ((state.get('souls') or {}).get('items') or {}).values()}
    worn = {int(x) for p in state.get('partners', []) for x in (p.get('equips') or []) if str(x).isdigit() and int(x)}
    outfit = set()
    for did, piece in ((state.get('dress') or {}).get('owned') or {}).items():
        outfit.add(int(did))
    out = set()
    for cid, typ, item, _ in ROWS:
        if typ == 1: ok = item in skin_got or have(item)
        elif typ == 2: ok = item in gear or item in worn or have(item)  # Antiques: in the bag or equipped
        elif typ == 9: ok = item in outfit or have(item)
        else: ok = have(item)
        if ok: out.add(cid)
    return out


def points(state, got=None):
    got = owned_ids(state) if got is None else got
    return sum(p for cid, _, _, p in ROWS if cid in got)


def saved(state, now):
    s = state.setdefault('collection_shop', {'rare': {}, 'common': {}, 'week': ''})
    wk = clock.week(now)
    if s.get('week') != wk:
        s['week'] = wk; s['common'] = {}
    return s


def snapshot(state, now=None):
    import copy
    view = copy.deepcopy(state)
    got = owned_ids(view)
    s = saved(view, clock.epoch(now))
    by_type = {}
    for cid, typ, _, _ in ROWS:
        t = by_type.setdefault(str(typ), [0, 0]); t[1] += 1
        if cid in got: t[0] += 1
    nodes = {k: [sum(by_type.get(str(t), [0, 0])[0] for t in ts), sum(by_type.get(str(t), [0, 0])[1] for t in ts)] for k, ts in NODES.items()}
    shops = {}
    for kind, rows in SHOPS.items():
        bought = s['rare' if kind == RARE else 'common']
        shops[str(kind)] = [{**r, 'bought': int(bought.get(str(r['id']), 0))} for r in rows]
    return {'points': points(view, got), 'levels': LEVELS, 'by_type': by_type, 'nodes': nodes, 'shops': shops,
            'week_end': clock.week_end(s['week']), 'got': sorted(got)}


def action(state, request, now=None):
    now = clock.epoch(now)
    if request.get('action') != 'buy':
        raise CollectionError('Acción de Collection Store desconocida')
    kind = int(request.get('shop') or 0); rid = int(request.get('id') or 0)
    row = next((r for r in SHOPS.get(kind, []) if r['id'] == rid), None)
    if not row:
        raise CollectionError('Artículo desconocido')
    s = saved(state, now)
    have = points(state)
    if have < row['point']:
        raise CollectionError(f"Unlock after acquiring {row['point']} Collection Points")
    bought = s['rare' if kind == RARE else 'common']
    if row['limit'] >= 0 and int(bought.get(str(rid), 0)) >= row['limit']:
        raise CollectionError('Sold out')
    ck, cn = pair(row['cost'])
    if int(state['items'].get(ck, 0)) < cn:
        raise CollectionError('Not enough ' + ('Gems' if ck == '2' else 'Gold'))
    state['items'][ck] = int(state['items'][ck]) - cn
    ik, inn = pair(row['item'])
    state['items'][ik] = int(state['items'].get(ik, 0)) + inn
    bought[str(rid)] = int(bought.get(str(rid), 0)) + 1
    return {'got': {ik: inn}}
