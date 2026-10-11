"""Generic event kit (LOCAL-059): exchange shops and mission boards shared by many limited events.

Data comes from data/activity_kit.json (tools/extract_activity_kit.py): per activity id an optional exchange shop
(`cost` -> `award`, `limit` per row) and an optional mission board. What is original and what is local:

* Original: rows, costs, awards, limits and the mission texts/amounts/awards.
* Local: the server counted the actions during the event. Progress is the increase of our own counters
  (`missions.counts`, `missions.totals`) since the event was first opened; the counter each mission needs is derived from
  its text (COUNTERS). Missions about purchases with real money, gem spending, a specific girl, friends or other systems
  we don't have are listed as `tracked: false` and cannot be claimed.
* Local: the event currency normally dropped from the event's own minigame. Until that minigame exists, an event whose
  missions don't pay its shop currency gives a small daily supply (`SUPPLY_DAYS` days of the median price) once per local day.
* A shop `limit` of 0 means unlimited; missions with `limit` N can be claimed N times (each needs `need` more progress).
"""
from __future__ import annotations
import json, re
from pathlib import Path
from . import clock, vip, activity_draw, local_config

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/activity_kit.json').read_text())
EVENTS = {int(k): v for k, v in D['events'].items()}
SUPPLY_DAYS = 10
UNLOCK_BY_SPENT = {330}   # Palace Vaults: bigger vaults open after spending Pirate Coins (activity_pirate_shop_awards.unlock)
NO_SUPPLY = {64, 330}    # the event's own minigame pays its currency
BASIC = {'1', '2', '3'}

# (regex on the mission text, counter key). First match wins; None = counted from the other missions of the board.
COUNTERS = [
    (r'complete all (the )?other|complete all (daily|weekly|tasks)', 'others'),
    (r'daily login|log in \d+ days', 'login'),
    (r'slot machine', 'gamble'),
    (r'bff capsule', None),
    (r'adv(anced|\.)? capsule', 'advanced'),
    (r'\b(enroll|seals?)\b', 'enroll'),
    (r'internship', 'tavern3'),
    (r'junior varsity|league tickets?', 'arena'),
    (r'battles? in tests', 'tower'),
    (r'daily quiz', 'quiz'),
    (r'\bforge\b', 'forge'),
    (r'echoes of time', 'echoes_obs'),
    (r'alchemy', 'midas'),
    (r'auto-battle loot', 'idle'),
    (r'space radars?', 'radar'),
    (r'vip exp', 'vip_exp'),
    (r'jade cranes?', 'spent:385'),
    (r'gilded cranes?', 'spent:386'),
    (r'acquire (a|1) 5-star girl|obtain a 5-star girl', 'star5'),
]


class KitError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def counter_for(text):
    t = re.sub(r'\[[^\]]*\]', '', str(text)).lower()
    for pattern, key in COUNTERS:
        if re.search(pattern, t): return key
    return None


def has(eid):
    return int(eid) in EVENTS


def ev_of(eid):
    if not has(eid): raise KitError('Evento sin motor genérico')
    return EVENTS[int(eid)]


def read_counter(state, key):
    """Cumulative counters: missions.record() adds every action to missions.totals (counts is the daily copy)."""
    if key == 'vip_exp': return vip.exp(state)
    if key.startswith('spent:'): return activity_draw.spent(state, key.split(':')[1])
    return int(((state.get('missions') or {}).get('totals') or {}).get(key, 0))


ALL_KEYS = sorted({k for _, k in COUNTERS if k and k != 'others'})  # vip_exp included: baseline via read_counter


def snapshot_counters(state):
    return {k: read_counter(state, k) for k in ALL_KEYS}


def data(state, eid, now):
    """Saved state of one event; the first call fixes the counter baseline."""
    root = state.setdefault('act_kit', {})
    s = root.get(str(eid))
    if not s:
        s = root[str(eid)] = {'base': snapshot_counters(state), 'claimed': {}, 'bought': {}, 'supply_day': '', 'spent': {}}
    return s


def median(values):
    v = sorted(values); return v[len(v) // 2] if v else 0


def currency_of(eid):
    """The event's own currency: the non-basic item most rows of its shop cost (>= 60 % of them)."""
    rows = EVENTS[int(eid)].get('shop') or []
    count = {}
    for r in rows:
        for k in pairs(r['cost']):
            if k not in BASIC: count[k] = count.get(k, 0) + 1
    if not count: return None
    k = max(count, key=count.get)
    return k if count[k] >= 0.6 * len(rows) else None


def supply_of(eid):
    """Daily supply for events whose own missions don't pay the shop currency: {item: amount}."""
    ev = EVENTS[int(eid)]; cur = currency_of(eid)
    if not cur or int(eid) in NO_SUPPLY: return {}
    if any(cur in pairs(m['award']) for m in ev.get('missions') or []): return {}
    prices = [pairs(r['cost'])[cur] for r in ev['shop'] if cur in pairs(r['cost'])]
    return {cur: max(1, -(-median(prices) // SUPPLY_DAYS))}


def clean(text):
    return re.sub(r'\[/?c\]|\[[0-9a-fA-F]{6}\]|\[-\]', '', str(text))


def mission_view(state, s, m, others_done=0):
    counter = counter_for(m['text']); need = int(m['need']); limit = int(m['limit']) or 1
    if counter == 'others': have = others_done
    elif counter: have = max(0, read_counter(state, counter) - int(s['base'].get(counter, 0)))
    else: have = 0
    done = int(s['claimed'].get(str(m['id']), 0))
    return {'id': m['id'], 'text': clean(m['text']).replace('{1}', str(need)).replace('{2}', '') or 'Mission %d' % m['id'],
            'need': need, 'have': min(have, need * limit), 'limit': limit, 'award': m['award'], 'tracked': counter is not None,
            'claimed': done, 'can': counter is not None and min(limit, have // need if need else 0) > done}


def missions_of(state, eid, s):
    rows = EVENTS[int(eid)].get('missions') or []
    out = [mission_view(state, s, m) if counter_for(m['text']) != 'others' else None for m in rows]
    finished = sum(1 for v in out if v and v['claimed'] >= v['limit'])
    return [v or mission_view(state, s, m, finished) for v, m in zip(out, rows)]


def snapshot(state, now):
    view = json.loads(json.dumps(state)); out = {}
    for eid, ev in EVENTS.items():
        s = data(view, eid, now)
        out[str(eid)] = {'started': str(eid) in (state.get('act_kit') or {}), 'bought': s['bought'], 'missions': missions_of(view, eid, s) if ev.get('missions') else [],
                         'supply': supply_of(eid) if s.get('supply_day') != clock.day(now) else {},
                         'items': {k: int(view['items'].get(k, 0)) for r in (ev.get('shop') or []) for k in pairs(r['cost'])}, 'currency': currency_of(eid),
                         'spent': int(s['spent'].get(currency_of(eid) or '', 0)), 'unlock_by_spent': eid in UNLOCK_BY_SPENT}
    return out


def add(state, got):
    for k, n in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + n


def action(state, request, now):
    eid = int(request.get('event', 0)); ev = ev_of(eid); s = data(state, eid, now); act = request.get('action')
    if act == 'buy':
        rid = int(request.get('id', 0)); times = int(request.get('times', 1))
        row = next((r for r in ev.get('shop') or [] if r['id'] == rid), None)
        if not row or times < 1 or times > 999: raise KitError('Artículo no disponible')
        bought = int(s['bought'].get(str(rid), 0))
        if row['limit'] and bought + times > row['limit']: raise KitError('Límite de compras alcanzado')
        if eid in UNLOCK_BY_SPENT and row.get('unlock', 0) > int(s['spent'].get(currency_of(eid) or '', 0)): raise KitError('Bóveda bloqueada')
        cost = {k: local_config.shop_cost(n) * times for k, n in pairs(row['cost']).items()}
        for k, n in cost.items():
            if int(state['items'].get(k, 0)) < n: raise KitError('Faltan recursos')
        for k, n in cost.items():
            state['items'][k] = int(state['items'].get(k, 0)) - n; s['spent'][k] = int(s['spent'].get(k, 0)) + n
        got = {k: n * times for k, n in pairs(row['award']).items()}
        add(state, got); s['bought'][str(rid)] = bought + times
        return {'got': got}
    if act == 'claim':
        mid = int(request.get('id', 0)); views = missions_of(state, eid, s)
        v = next((x for x in views if x['id'] == mid), None)
        if not v or not v['tracked']: raise KitError('Misión no disponible')
        times = min(v['limit'], v['have'] // v['need']) - v['claimed']
        if times <= 0: raise KitError('Misión sin completar')
        got = {k: n * times for k, n in pairs(v['award']).items()}
        add(state, got); s['claimed'][str(mid)] = v['claimed'] + times
        return {'got': got}
    if act == 'supply':
        if s.get('supply_day') == clock.day(now): raise KitError('Ya recibiste el suministro de hoy')
        got = supply_of(eid)
        if not got: raise KitError('Este evento no tiene suministro')
        add(state, got); s['supply_day'] = clock.day(now)
        return {'got': got}
    if act == 'open':
        return {}
    raise KitError('Acción no disponible')
