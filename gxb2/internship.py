"""Internship (models/Tavern.lua, TavernWindow, TavernDetailWindow, TAVERN_WINDOW_TIPS) offline.

Recovered from the client:
- Quests of 1-7 stars (pub_mission): partner_num Girls for mission_time seconds; one of them must have at least
  partner_star stars and, for every condition (pub_mission_condition: a faction or a class), a different Girl of that
  faction/class (TavernMultimissionWindow:checkCanStartMission). Each Girl does one Internship at a time.
- Reward: award_dropbox_id, drawn when the quest appears (the list shows it) and paid on completion. Speed up with speedup_cost; refresh the quests not started nor locked for
  pub_mission_refresh_cost each; lock / unlock; cancel a running quest.
- A daily amount of new quests (vip.pub_mission_num: 5 at VIP 0) drawn with weight; Internship Scrolls (24) and
  Advanced Scrolls (25) add one quest with pub_scroll star odds. At most pub_mission_max quests at once.

LOCAL decisions (DESIGN_DECISIONS.md LOCAL-033):
- The daily quests arrive at 00:00 UTC (the server day); VIP stays 0 until VIP exists offline.
- Each quest gets need_num conditions chosen at random from its list, and a random name from random_names.
- The Internship daily task counts completed quests.
"""
from __future__ import annotations
import json, secrets, time
from . import clock
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/internship.json').read_text())
MISSIONS = {int(r['id']): r for r in DATA['missions']}
CONDITIONS = {int(k): v for k, v in DATA['conditions'].items()}
SCROLLS = {int(r['id']): r for r in DATA['scrolls']}
BOX: dict[int, list] = {}
for _r in DATA['dropbox']:
    BOX.setdefault(int(_r['dropbox_id']), []).append(_r)
MAX = int(DATA['misc']['pub_mission_max'])


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[k] = out.get(k, 0) + int(float(n))
    return out


def ids(text):
    return [int(x) for x in str(text or '').split('|') if x]


def day(now):
    return clock.day(now)


def weighted(options, weight, rng):
    total = sum(max(0, int(weight(o))) for o in options)
    if total <= 0:
        return None
    x = rng(total)
    for o in options:
        x -= max(0, int(weight(o)))
        if x < 0:
            return o
    return options[-1]


def new_mission(h, star_id, rng):
    row = MISSIONS[star_id]
    pool = ids(row['conditions'])
    conds = []
    for _ in range(min(int(row['need_num']), len(pool))):
        conds.append(pool.pop(rng(len(pool))))
    names = ids(row['random_names'])
    m = {'id': h['next_id'], 'table_id': star_id, 'name': names[rng(len(names))] if names else 0, 'conditions': sorted(conds),
         'locked': False, 'partners': [], 'end': 0}
    m['award'] = roll(row['award_dropbox_id'], rng)  # TavernWindow shows the reward before the quest starts
    h['next_id'] += 1
    h['missions'].append(m)
    return m


def daily(state):
    return int(DATA['vip_daily'].get(str(int(state.get('vip', 0))), DATA['vip_daily'].get('0', 5)))


def saved(state, now, rng=secrets.randbelow):
    h = state.setdefault('internship', {'day': '', 'missions': [], 'next_id': 1})
    if h['day'] != day(now):
        h['day'] = day(now)
        for _ in range(daily(state)):
            if len(h['missions']) >= MAX:
                break
            row = weighted(list(MISSIONS.values()), lambda r: r['weight'], rng)
            new_mission(h, int(row['id']), rng)
    for m in h['missions']:  # quests saved before the reward was drawn up front
        if 'award' not in m: m['award'] = roll(MISSIONS[m['table_id']]['award_dropbox_id'], rng)
    return h


def busy(h):
    return {p for m in h['missions'] for p in m['partners']}


def stars(state, pid):
    from .engine import TABLES
    p = next(x for x in state['partners'] if x['partner_id'] == pid)
    row = TABLES['partner'].get(str(p['table_id']), {})
    return int(row.get('max_star') or 0) + int(p.get('awake', 0)), int(row.get('group') or 0), int(row.get('job') or 0)


def fits(state, m, pids):
    """Star requirement plus one distinct Girl per faction/class condition (bipartite matching)."""
    row = MISSIONS[m['table_id']]
    info = {p: stars(state, p) for p in pids}
    needs = []
    if int(row['partner_star']) > 0:
        needs.append(lambda s, g, j, v=int(row['partner_star']): s >= v)
    for c in m['conditions']:
        cond = CONDITIONS[c]
        if int(cond['group']) > 0:
            needs.append(lambda s, g, j, v=int(cond['group']): g == v)
        if int(cond['job']) > 0:
            needs.append(lambda s, g, j, v=int(cond['job']): j == v)
    match = {}

    def assign(i, seen):
        for p in pids:
            if p in seen or not needs[i](*info[p]):
                continue
            seen.add(p)
            if p not in match or assign(match[p], seen):
                match[p] = i
                return True
        return False
    return all(assign(i, set()) for i in range(len(needs)))


def roll(box, rng):
    opt = weighted(BOX.get(int(box), []), lambda o: o['weight'], rng)
    if not opt:
        return {}
    k, lo, *hi = str(opt['item']).split('#')
    lo = int(lo); hi = int(hi[0]) if hi else lo
    return {k: lo + (rng(hi - lo + 1) if hi > lo else 0)}


def snapshot(state, now=None):
    import copy
    now = int(time.time()) if now is None else now
    view = copy.deepcopy(state)
    h = view.get('internship') or {'day': '', 'missions': [], 'next_id': 1}  # read-only: the day's quests are drawn by 'open'
    out = []
    for m in h['missions']:
        row = MISSIONS[m['table_id']]
        out.append({**m, 'star': int(row['star']), 'time': int(row['mission_time']), 'partner_num': int(row['partner_num']),
                    'partner_star': int(row['partner_star']), 'speedup': pairs(row['speedup_cost']),
                    'title': DATA['names'].get(str(m['name']), f"Internship {m['id']}"),
                    'conds': [{'group': int(CONDITIONS[c]['group']), 'job': int(CONDITIONS[c]['job'])} for c in m['conditions']],
                    'state': 'idle' if not m['end'] else ('done' if now >= m['end'] else 'running')})
    order = {'done': 0, 'running': 1, 'idle': 2}
    out.sort(key=lambda m: (order[m['state']], -m['star'], m['id']))
    items = view.get('items', {})
    fresh = state.get('internship', {}).get('day') != day(now)
    return {'missions': out, 'busy': sorted(busy(h)), 'refresh_cost': pairs(DATA['misc']['pub_mission_refresh_cost']),
            'scrolls': {'24': int(items.get('24', 0)), '25': int(items.get('25', 0))}, 'daily': daily(state), 'max': MAX,
            'next_day': (now // 86400 + 1) * 86400, 'pending_daily': fresh}


def pay(items, cost):
    cost = {k: n for k, n in cost.items() if k != '0' and n > 0}  # '0#0' = free (1-3★ speed-up)
    for k, n in cost.items():
        if int(items.get(k, 0)) < n:
            raise ValueError('Faltan ' + ('gemas' if k == '2' else f'objetos {k}'))
    for k, n in cost.items():
        items[k] = int(items[k]) - n


def action(state, request, now=None, rng=secrets.randbelow):
    now = int(time.time()) if now is None else now
    h = saved(state, now, rng)
    items = state['items']
    kind = request.get('action')
    result = {}
    if kind == 'open':
        return result
    if kind == 'scroll':
        sid = int(request.get('index', 1))
        if sid not in SCROLLS:
            raise ValueError('Pergamino no válido')
        if len(h['missions']) >= MAX:
            raise ValueError(DATA['text'].get('PUB_MISSION_LIMIT_TIPS', 'Too many Internship quests'))
        pay(items, pairs(SCROLLS[sid]['cost']))
        rates = [(int(k), int(v)) for k, v in (x.split('#') for x in str(SCROLLS[sid]['rate']).split('|'))]
        star = weighted(rates, lambda r: r[1], rng)[0]
        result['mission'] = new_mission(h, star, rng)['id']
        return result
    if kind == 'refresh':
        todo = [m for m in h['missions'] if not m['end'] and not m['locked']]
        if not todo:
            raise ValueError('No hay encargos para refrescar')
        cost = {k: n * len(todo) for k, n in pairs(DATA['misc']['pub_mission_refresh_cost']).items()}
        pay(items, cost)
        for m in todo:
            h['missions'].remove(m)
            row = weighted(list(MISSIONS.values()), lambda r: r['weight'], rng)
            new_mission(h, int(row['id']), rng)
        result['refreshed'] = len(todo)
        return result
    m = next((x for x in h['missions'] if x['id'] == int(request.get('mission', 0))), None)
    if not m:
        raise ValueError('Encargo no disponible')
    row = MISSIONS[m['table_id']]
    if kind == 'lock':
        m['locked'] = not m['locked']
    elif kind == 'start':
        if m['end']:
            raise ValueError('Ese encargo ya está en marcha')
        pids = [int(p) for p in request.get('partners') or []]
        owned = {p['partner_id'] for p in state['partners']}
        if len(pids) != int(row['partner_num']) or len(set(pids)) != len(pids) or any(p not in owned for p in pids):
            raise ValueError(f"Este encargo necesita {row['partner_num']} chicas")
        if set(pids) & busy(h):
            raise ValueError('Cada chica solo puede hacer una prácticas a la vez')
        if not fits(state, m, pids):
            raise ValueError('Las chicas no cumplen las condiciones del encargo')
        m['partners'] = pids
        m['end'] = now + int(row['mission_time'])
    elif kind == 'cancel':
        if not m['end'] or now >= m['end']:
            raise ValueError('Solo se cancela un encargo en marcha')
        m['partners'] = []; m['end'] = 0
    elif kind == 'speed':
        if not m['end'] or now >= m['end']:
            raise ValueError('Ese encargo no está en marcha')
        pay(items, pairs(row['speedup_cost']))
        m['end'] = now
    elif kind == 'complete':
        if not m['end'] or now < m['end']:
            raise ValueError('Aún no ha terminado')
        got = m.get('award') or roll(row['award_dropbox_id'], rng)
        for k, n in got.items():
            items[k] = int(items.get(k, 0)) + n
        h['missions'].remove(m)
        result.update(got=got, star=int(row['star']))
    else:
        raise ValueError('Acción de Internship no disponible')
    return result
