"""Shopping Street stores (ShopMapWindow / MarketWindow / ShopWindow, models/Shop.lua) on shop_config.

Recovered from the client: store list, currencies (economy_show), per-slot buy limits (slot_buy_time, -1 = no
limit), refresh cost (refresh_cost), level gates (limit_level), Market = shop_black_new slots whose dropbox rows
carry item + cost, Market buys once per slot (MarketItem left_times = 1) and refreshes when the day ends
(MarketWindow: 86400 - serverTime % 86400). Girls Store / Artifact Store order by table rank and filter by group.

LOCAL decisions (server logic missing, see DESIGN_DECISIONS.md LOCAL-026):
- Days end at local midnight (the client used the server's UTC day).
- Guild Store limits also reset daily; its paid refresh (4#20000) resets them immediately.
- Transfer (shop 2 / shop_hero) had a server-generated inventory (all table rows are 0#0): not rebuilt.
- Lucky Store (shop 3) keeps its own implementation in acquisition.py (Slots window).
"""
from __future__ import annotations
import json, time
from . import clock, local_config
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/shops.json').read_text())
SHOPS = {int(k): v for k, v in DATA['shops'].items()}
BOX = {}
for _r in DATA['dropbox'].values():
    BOX.setdefault(int(_r['dropbox_id']), []).append(_r)
EXCHANGE_TABS = sorted((s for s in SHOPS.values() if s.get('type') == 2), key=lambda s: int(s.get('rank') or 99))
DAILY = {7, 6}


def pair(text):
    p = str(text or '0#0').split('#')
    return [int(p[0]), int(p[1]) if len(p) > 1 else 0]


def day(now):
    return clock.day(now)


def limits(sid):
    return [int(x) for x in str(SHOPS[sid].get('slot_buy_time') or '').split('|') if x not in ('',)]


def goods(sid):
    shop = SHOPS[sid]
    rows = DATA['tables'][shop['excel_table']]
    lim = limits(sid)
    out = []
    for i, r in enumerate(rows):
        if sid == 7:
            box = BOX.get(int(r['dropbox_id']), [{}])[0]
            item, cost, cap = pair(box.get('item')), pair(box.get('cost')), 1
            cost[1] = local_config.shop_cost(cost[1])
        else:
            item, cost = pair(r.get('item')), pair(r.get('cost'))
            cost[1] = local_config.shop_cost(cost[1])
            cap = lim[i] if i < len(lim) else -1
        if item[0] <= 0 or cost[0] <= 0:
            continue
        out.append({'index': i + 1, 'item': item, 'cost': cost, 'limit': cap, 'rank': int(r.get('rank') or 0), 'group': int(r.get('group') or 0)})
    if sid in (11, 17):
        out.sort(key=lambda g: (g['rank'], g['index']))
    return out


def saved(state, sid, now):
    boards = state.setdefault('shop_boards', {})
    b = boards.setdefault(str(sid), {'day': day(now), 'bought': {}})
    if sid in DAILY and b['day'] != day(now):
        b.update(day=day(now), bought={})
    return b


def level_ok(sid, level):
    lv = int(SHOPS[sid].get('limit_level') or -1)
    return lv <= 0 or level >= lv


def snapshot(state, level, now=None):
    now = int(time.time()) if now is None else now
    out = {}
    for sid, shop in SHOPS.items():
        if sid == 3:
            continue
        b = (state.get('shop_boards') or {}).get(str(sid)) or {}
        bought = b.get('bought', {}) if (sid not in DAILY or b.get('day') == day(now)) else {}
        out[sid] = {'id': sid, 'open': level_ok(sid, level), 'limit_level': shop.get('limit_level'), 'available': sid != 2,
                    'goods': [{**g, 'bought': int(bought.get(str(g['index']), 0))} for g in goods(sid)] if sid != 2 else [],
                    'refresh_at': (int(time.mktime(time.strptime(day(now), '%Y-%m-%d'))) + 86400) if sid in DAILY else 0}
    return out


def action(state, request, level, now=None):
    now = int(time.time()) if now is None else now
    sid = int(request.get('shop', 0))
    if sid not in SHOPS or sid in (2, 3):
        raise ValueError('Tienda no disponible')
    if not level_ok(sid, level):
        raise ValueError(f"Se desbloquea al nivel {SHOPS[sid]['limit_level']}")
    b = saved(state, sid, now)
    items = state['items']
    kind = request.get('action')
    if kind == 'buy':
        idx = int(request.get('index', 0)); num = max(1, int(request.get('num', 1)))
        g = next((x for x in goods(sid) if x['index'] == idx), None)
        if not g:
            raise ValueError('Artículo inexistente')
        have = int(b['bought'].get(str(idx), 0))
        if g['limit'] >= 0 and have + num > g['limit']:
            raise ValueError('Ya comprado')
        cid, cn = str(g['cost'][0]), g['cost'][1] * num
        if int(items.get(cid, 0)) < cn:
            raise ValueError('Faltan recursos')
        items[cid] = int(items.get(cid, 0)) - cn
        iid, n = str(g['item'][0]), g['item'][1] * num
        items[iid] = int(items.get(iid, 0)) + n
        b['bought'][str(idx)] = have + num
        return {'got': {iid: n}}
    if kind == 'refresh':
        shop = SHOPS[sid]
        if not int(shop.get('is_refresh') or 0) or not shop.get('refresh_cost'):
            raise ValueError('Esta tienda no se puede refrescar')
        cid, cn = pair(shop['refresh_cost']); cn = local_config.shop_cost(cn)
        if int(items.get(str(cid), 0)) < cn:
            raise ValueError('Faltan recursos')
        items[str(cid)] = int(items.get(str(cid), 0)) - cn
        b['bought'] = {}
        return {}
    raise ValueError('Acción de tienda no disponible')
