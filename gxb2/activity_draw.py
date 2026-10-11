"""Draw-with-a-token minigames (LOCAL-061): Goldfish Scooper 317, Seaside Fishing 245, Spin the Wheel 286, Easter Egg Factory 290,
Childhood Memories 298, Lucky Dips 260, Jungle Exploration 234 and Ring Toss 283, all on one engine.

Original (data/activity_draw.json, tools/extract_activity_draw.py): the token and the cost of a draw (misc activity_*_cost), the
prizes (a weighted table or dropboxes), the per-draw stock of Spin the Wheel (`num`), the Fishing golden-fish chance
(activity_fish_extra_pro over 10000), the Lucky Dips big prizes (1 % each) and its pity bar (misc luckyboxes_pointmax 100, +2 per
draw), the milestone awards (`complete` / `point`) and the token packs sold for gems (goldfish, Childhood, Ring Toss) with their limits.

Local (LOCAL-061): the server counted the milestones; here every draw adds 1 to the event counter (one unit per draw) and each
milestone is claimed once. The token normally came from the event's tasks and login gifts: `DAILY_DRAWS` draws' worth of the first
token is given once per local day. Easter Egg Factory's two tokens draw from two dropboxes; Ring Toss picks one of four dropboxes
by weight. Jungle Exploration only rebuilds area 1 of its milestones. Wish Upon a Chime: the two Cranes draw the two dropbox types and every 20 Gilded Cranes guarantee a Shard of Reflections; the Chimes themselves (equipment) aren't rebuilt, they stay as items.
"""
from __future__ import annotations
import json, secrets
from pathlib import Path
from . import clock

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/activity_draw.json').read_text())
EVENTS = {int(k): v for k, v in D['events'].items()}


def spent(state, item):
    """Tokens of `item` consumed in every draw event (for the tasks that ask to consume an event currency)."""
    return sum(int((s.get('spent') or {}).get(str(item), 0)) for s in (state.get('act_draw') or {}).values())
DAILY_DRAWS = 10
MAX_TIMES = 10


class DrawError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def has(eid):
    return int(eid) in EVENTS


def data(state, eid):
    root = state.setdefault('act_draw', {})
    s = root.get(str(eid))
    if not s:
        s = root[str(eid)] = {'draws': 0, 'claimed': [], 'bought': 0, 'stock': {}, 'pity': 0, 'token_day': '', 'last': []}
    return s


def add(state, got):
    for k, n in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + n


def merge(a, b):
    for k, n in b.items(): a[k] = a.get(k, 0) + n


def pick(rows, rng, weights=None):
    weights = weights or [int(r['weight']) for r in rows]
    total = sum(weights)
    n = rng(total)
    for r, w in zip(rows, weights):
        n -= w
        if n < 0: return r
    return rows[-1]


def draw_one(ev, s, mi, rng):
    """One draw of mode `mi`: returns the awards {item: n}."""
    mode = ev['modes'][mi]; got = dict(pairs(mode['always']))
    s['pity'] = int(s.get('pity', 0))
    if ev.get('big') and ev.get('pity'):
        s['pity'] += ev['pity']['add']
        roll = rng(10000) / 10000
        if s['pity'] >= ev['pity']['max'] or roll < sum(b['rate'] for b in ev['big']):
            big = pick(ev['big'], rng, [max(1, int(b['rate'] * 10000)) for b in ev['big']]); s['pity'] = 0
            merge(got, pairs(big['awards'])); return got, True
    if ev.get('bonus') and rng(10000) < int(ev['bonus']['chance']):
        merge(got, pairs(pick(ev['bonus']['prizes'], rng)['awards'])); return got, True
    groups = mode['groups']; gi = pick(groups, rng, [g['weight'] for g in groups]) if len(groups) > 1 else groups[0]
    gi = groups.index(gi) if not isinstance(gi, int) else gi
    prizes = groups[gi]['prizes']; key = f'{mi}:{gi}'
    if any('stock' in p for p in prizes):
        left = s['stock'].setdefault(key, [p.get('stock', 1) for p in prizes])
        if not any(left): left[:] = [p.get('stock', 1) for p in prizes]
        i = pick(prizes, rng, [w if left[j] > 0 else 0 for j, w in enumerate(int(p['weight']) for p in prizes)])
        left[prizes.index(i)] -= 1
    else:
        i = pick(prizes, rng)
    merge(got, pairs(i['awards']))
    return got, False


def snapshot(state, now):
    view = json.loads(json.dumps(state)); out = {}
    for eid, ev in EVENTS.items():
        s = data(view, eid)
        out[str(eid)] = {'draws': s['draws'], 'claimed': s['claimed'], 'bought': s['bought'], 'pity': s['pity'], 'last': s['last'], 'guar': int(s.get('guar', 0)),
                         'daily_ready': s['token_day'] != clock.day(now), 'daily': daily_of(eid),
                         'tokens': {k: int(view['items'].get(k, 0)) for m in ev['modes'] for k in pairs(m['cost'])}}
    return out


def daily_of(eid):
    cost = pairs(EVENTS[int(eid)]['modes'][0]['cost'])
    return {k: n * DAILY_DRAWS for k, n in cost.items()}


def action(state, request, now, rng=secrets.randbelow):
    eid = int(request.get('event', 0))
    if not has(eid): raise DrawError('Evento sin sorteo')
    ev = EVENTS[eid]; s = data(state, eid); act = request.get('action')
    if act == 'draw':
        mi = int(request.get('mode', 0)); times = int(request.get('times', 1))
        if not 0 <= mi < len(ev['modes']) or not 1 <= times <= MAX_TIMES: raise DrawError('Sorteo no válido')
        cost = {k: n * times for k, n in pairs(ev['modes'][mi]['cost']).items()}
        for k, n in cost.items():
            if int(state['items'].get(k, 0)) < n: raise DrawError('Faltan fichas')
        for k, n in cost.items(): state['items'][k] = int(state['items'].get(k, 0)) - n
        got, specials = {}, 0
        for _ in range(times):
            g, special = draw_one(ev, s, mi, rng); merge(got, g); specials += special
        sp = s.setdefault('spent', {})
        for k, n in cost.items(): sp[k] = int(sp.get(k, 0)) + n
        gu = ev.get('guarantee')
        if gu and gu['mode'] == mi:      # e.g. a Shard of Reflections for every 20 Gilded Cranes consumed
            s['guar'] = int(s.get('guar', 0)) + times
            while s['guar'] >= gu['every']: s['guar'] -= gu['every']; merge(got, pairs(gu['awards'])); specials += 1
        add(state, got); s['draws'] += times; s['last'] = [[k, n] for k, n in got.items()]
        return {'got': got, 'special': specials}
    if act == 'claim':
        i = int(request.get('index', -1)); ms = ev.get('milestones') or []
        if not 0 <= i < len(ms): raise DrawError('Hito no disponible')
        if i in s['claimed']: raise DrawError('Hito ya reclamado')
        if s['draws'] < ms[i]['need']: raise DrawError('Aún no llegas')
        got = pairs(ms[i]['awards']); add(state, got); s['claimed'].append(i)
        return {'got': got}
    if act == 'buy':
        buy = ev.get('buy')
        if not buy: raise DrawError('Este evento no vende fichas')
        if s['bought'] >= int(buy['limit']): raise DrawError('Límite de compras alcanzado')
        cost = pairs(buy['cost'])
        for k, n in cost.items():
            if int(state['items'].get(k, 0)) < n: raise DrawError('Faltan recursos')
        for k, n in cost.items(): state['items'][k] = int(state['items'].get(k, 0)) - n
        got = pairs(buy['get']); add(state, got); s['bought'] += 1
        return {'got': got}
    if act == 'daily':
        if s['token_day'] == clock.day(now): raise DrawError('Ya recibiste las fichas de hoy')
        got = daily_of(eid); add(state, got); s['token_day'] = clock.day(now)
        return {'got': got}
    if act == 'open':
        return {}
    raise DrawError('Acción no disponible')
