"""Excursion → Explore adventure (ExploreAdventureWindow.lua) on the travel_* tables.

Recovered from the client: explore level rows (slots, chest-grade rates, enemy level, battles, upgrade gate
`update_box_limit`), chest types (open time, rewards, dropboxes, gem price), event list with its costs,
bread price/limits (misc.travel_buy / travel_buy_time_limit) and the help text (10 bread per exploration,
elite after wins, chests wait or open with gems, full slots block new chests, max level 10).

LOCAL decisions (server logic not in the client, see DESIGN_DECISIONS.md):
- travel_event.value sums to exactly 10000 over the non-elite events, so it is used as the event weight.
- The elite enemy (event 2) replaces the roll after `travel_strong_enemy_condition[0]` (5) common wins.
- reward_box_type 2 rolls the chest grade twice and keeps the higher; 0 gives the event dropbox (Food Truck).
- update_box_limit "g#n|..." = chests of grade g opened at the current level needed to upgrade.
"""
from __future__ import annotations
import json, secrets, time
from . import clock
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/home_systems.json').read_text())
LEVELS = {int(r['grade']): r for r in DATA['travel_explore']}
BOXES = {int(r['id']): r for r in DATA['travel_box']}
EVENTS = {int(r['id']): r for r in DATA['travel_event']}
MISC = DATA['misc']
DROP = {}
for _r in json.loads((Path(__file__).resolve().parents[1] / 'data/dropbox.json').read_text()).values():
    DROP.setdefault(int(_r['dropbox_id']), []).append(_r)
BREAD = '203'
ELITE_AFTER = int(str(MISC.get('travel_strong_enemy_condition', '5|2')).split('|')[0])


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[k] = out.get(k, 0) + int(n)
    return out


def weighted(text, rng):
    opts = [(int(k), int(v)) for k, v in pairs(text).items()]
    roll = rng(sum(w for _, w in opts))
    for k, w in opts:
        roll -= w
        if roll < 0:
            return k
    return opts[-1][0]


def dropbox(box_id, rng):
    rows = [r for r in DROP.get(int(box_id), []) if int(r['weight']) > 0]
    if not rows:
        return {}
    roll = rng(sum(int(r['weight']) for r in rows))
    for r in rows:
        roll -= int(r['weight'])
        if roll < 0:
            parts = str(r['item']).split('#')
            if parts[0] in ('0', ''):
                return {}
            low = int(parts[1]); high = int(parts[2]) if len(parts) > 2 else low
            return {parts[0]: low + (rng(high - low + 1) if high > low else 0)}
    return {}


def saved(state, now):
    home = state.setdefault('home_systems', {})
    travel = home.setdefault('travel', {})
    ex = travel.setdefault('explore', {})
    ex.setdefault('lv', 1); ex.setdefault('wins', 0); ex.setdefault('chests', []); ex.setdefault('opened', {})
    ex.setdefault('event', None); ex.setdefault('bought', {'day': '', 'count': 0}); ex.setdefault('log', [])
    return ex


def day(now):
    return clock.day(now)


def buy_limit(state):
    limits = [int(x) for x in str(MISC['travel_buy_time_limit']).split('|')]
    vip = int(state.get('vip', 0) or 0)
    return limits[min(vip, len(limits) - 1)]


def _box_detail():
    """ExploreBoxDetailWindow: fixed award1 (100%) and dropbox_id1's items with weight / total weight."""
    out = {}
    for bid, row in BOXES.items():
        rows = [r for r in DROP.get(int(row['dropbox_id1'] or 0), []) if int(r['weight']) > 0]
        total = sum(int(r['weight']) for r in rows) or 1
        rand = [[str(r['item']), round(int(r['weight']) * 100 / total, 2)] for r in rows if str(r['item']).split('#')[0] not in ('0', '')]
        out[str(bid)] = {'fixed': pairs(row['award1']), 'random': rand, 'time': int(row['time_consume'])}
    return out


BOX_DETAIL = _box_detail()


def snapshot(state, now=None):
    now = int(time.time()) if now is None else now
    ex = ((state.get('home_systems') or {}).get('travel') or {}).get('explore') or {'lv': 1, 'wins': 0, 'chests': [], 'opened': {}, 'event': None, 'bought': {'day': '', 'count': 0}}
    row = LEVELS[ex['lv']]
    need = pairs(row['update_box_limit'])
    bought = ex['bought']['count'] if ex['bought']['day'] == day(now) else 0
    chests = [{**c, 'ready': now >= c['ready_at'], 'left': max(0, c['ready_at'] - now),
               'gems': pairs(BOXES[c['box']]['pay_consume']).get('2', 0)} for c in ex['chests']]
    return {'lv': ex['lv'], 'max_lv': max(LEVELS), 'slots': int(row['slot']), 'enemy_lv': int(row['enemy_lv']),
            'rates': pairs(row['reward_box_rate']), 'next_rates': pairs(LEVELS[ex['lv'] + 1]['reward_box_rate']) if ex['lv'] + 1 in LEVELS else {},
            'next_slots': int(LEVELS[ex['lv'] + 1]['slot']) if ex['lv'] + 1 in LEVELS else 0,
            'next_enemy_lv': int(LEVELS[ex['lv'] + 1]['enemy_lv']) if ex['lv'] + 1 in LEVELS else 0,
            'upgrade_need': need, 'opened': ex['opened'], 'can_upgrade': ex['lv'] < max(LEVELS) and all(int(ex['opened'].get(str(g), 0)) >= n for g, n in need.items()),
            'chests': chests, 'event': ex['event'], 'wins': ex['wins'], 'bread': int(state['items'].get(BREAD, 0)),
            'cost': pairs(MISC['travel_event_consume']), 'buy': pairs(MISC['travel_buy']), 'bought': bought, 'buy_limit': buy_limit(state),
            'log': ex.get('log', [])[:8], 'box_detail': BOX_DETAIL}


def chest_grade(ex, rng, twice=False):
    rates = LEVELS[ex['lv']]['reward_box_rate']
    g = weighted(rates, rng)
    return max(g, weighted(rates, rng)) if twice else g


def add_chest(ex, box, now):
    ex['chests'].append({'id': (max([c['id'] for c in ex['chests']] or [0]) + 1), 'box': box, 'ready_at': now + int(BOXES[box]['time_consume'])})


def charge(state, cost):
    if any(int(state['items'].get(k, 0)) < n for k, n in cost.items()):
        raise ValueError('Faltan recursos')
    for k, n in cost.items():
        state['items'][k] = int(state['items'].get(k, 0)) - n


def grant(state, items):
    for k, n in items.items():
        state['items'][k] = int(state['items'].get(k, 0)) + n


def action(state, request, now=None, rng=secrets.randbelow, fight=None):
    """fight(battle_id) -> (win: bool, battle_record_id) runs the original battle engine (injected by Engine)."""
    now = int(time.time()) if now is None else now
    ex = saved(state, now)
    kind = request.get('action')
    result = {}
    slots = int(LEVELS[ex['lv']]['slot'])
    if kind == 'go':
        if ex['event'] and not ex['event'].get('done'):
            raise ValueError('Resuelve primero el encuentro actual')
        ex['event'] = None
        if len(ex['chests']) >= slots:
            raise ValueError('Las ranuras de cofre están llenas: abre alguno antes de explorar')
        charge(state, pairs(MISC['travel_event_consume']))
        from . import growth_diary
        growth_diary.record(state,'growth_explore')
        if ex['wins'] >= ELITE_AFTER:
            eid = 2
        else:
            eid = weighted('|'.join(f"{i}#{r['value']}" for i, r in EVENTS.items() if r['value']), rng)
        ev = EVENTS[eid]
        ex['event'] = {'id': eid, 'type': int(ev['type']), 'map': int(ev['map'] or 1), 'text': ev['text'],
                       'model': ev['model'], 'consume': ev['consume'] if int(ev['type']) == 3 or eid == 8 else ''}
        if int(ev['type']) == 2 and eid != 8:
            # Wild chest / Food Truck: resolved on the spot.
            got = {}
            if ev['reward_box_type'] == '0':
                got = dropbox(ev['dropbox_ids'].split('|')[min(ex['lv'], 10) - 1], rng)
                grant(state, got)
            else:
                add_chest(ex, chest_grade(ex, rng, ev['reward_box_type'] == '2'), now)
            ex['event']['done'] = True; ex['event']['got'] = got
        result['event'] = ex['event']
    elif kind == 'resolve':
        ev = ex['event']
        if not ev or ev.get('done'):
            ex['event'] = None
            return result
        row = EVENTS[ev['id']]
        if request.get('skip'):
            ex['event'] = None
            return result
        if ev['type'] == 1:
            lv = LEVELS[ex['lv']]
            battle_id = weighted(lv['battle_id2' if ev['id'] == 2 else 'battle_id1'], rng)
            win, record = fight(battle_id) if fight else (True, None)
            result.update(win=win, battle=record)
            if win:
                if ev['id'] == 2:
                    ex['wins'] = 0
                else:
                    ex['wins'] += 1
                add_chest(ex, chest_grade(ex, rng, row['reward_box_type'] == '2'), now)
                got = dropbox(row['dropbox_ids'].split('|')[min(ex['lv'], 10) - 1], rng) if row['dropbox_ids'] else {}
                grant(state, got); result['got'] = got
        else:
            charge(state, pairs(ev.get('consume')))
            add_chest(ex, chest_grade(ex, rng, row['reward_box_type'] == '2'), now)
        ex['log'].insert(0, {'at': now, 'event': ev['id'], 'win': result.get('win', True)})
        ex['log'] = ex['log'][:20]
        ex['event'] = None
    elif kind == 'open':
        cid = int(request.get('id', 0))
        chest = next((c for c in ex['chests'] if c['id'] == cid), None)
        if not chest:
            raise ValueError('Cofre inexistente')
        box = BOXES[chest['box']]
        if now < chest['ready_at']:
            if not request.get('pay'):
                raise ValueError('El cofre todavía se está abriendo')
            charge(state, pairs(box['pay_consume']))
        got = pairs(box['award1'])
        for key in ('dropbox_id1', 'dropbox_id2'):
            if box[key]:
                for k, n in dropbox(box[key], rng).items():
                    got[k] = got.get(k, 0) + n
        grant(state, got)
        ex['chests'] = [c for c in ex['chests'] if c['id'] != cid]
        ex['opened'][str(chest['box'])] = int(ex['opened'].get(str(chest['box']), 0)) + 1
        from . import growth_diary
        growth_diary.record(state,'growth_chests')
        result['got'] = got
    elif kind == 'open_ready':
        got = {}
        for c in [c for c in ex['chests'] if now >= c['ready_at']]:
            r = action(state, {'action': 'open', 'id': c['id']}, now, rng, fight)
            for k, n in r['got'].items():
                got[k] = got.get(k, 0) + n
        if not got:
            raise ValueError('Ningún cofre está listo')
        result['got'] = got
    elif kind == 'upgrade':
        snap = snapshot(state, now)
        if not snap['can_upgrade']:
            raise ValueError('Abre más cofres de los grados indicados para subir de nivel')
        ex['lv'] += 1; ex['opened'] = {}
    elif kind == 'buy_bread':
        count = int(request.get('count', 1))
        if count < 1:
            raise ValueError('Cantidad inválida')
        if ex['bought']['day'] != day(now):
            ex['bought'] = {'day': day(now), 'count': 0}
        if ex['bought']['count'] + count > buy_limit(state):
            raise ValueError('Límite diario de compras alcanzado')
        buy = pairs(MISC['travel_buy'])
        charge(state, {k: n * count for k, n in buy.items() if k != BREAD})
        grant(state, {BREAD: buy[BREAD] * count}); ex['bought']['count'] += count
    else:
        raise ValueError('Acción de exploración no disponible')
    return result
