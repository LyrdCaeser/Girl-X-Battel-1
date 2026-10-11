"""Jigsaw and Puppet Parade with original tables and durable local progression.

LOCAL-070: archived events stay open without the original server calendar. Jigsaw
gets 3 daily energy; Puppet gets 40 daily puppets, replacing server event drops.
Rewards go directly to the bag; milestone claims are explicit and exactly once.
"""
import copy
import json
from pathlib import Path
from . import clock

D = json.loads((Path(__file__).resolve().parents[1] / 'data/puzzle_events.json').read_text())
PICS = D['activity_jigsaw_pic']
JIGSAW_DAILY = 3
PUPPET_DAILY = 40
PUPPET_ITEM = D['misc']['activity_puppet_item']


class PuzzleError(ValueError):
    pass


def integer(value, low, high):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise PuzzleError('Cantidad o posición inválida')
    return value


def pairs(text):
    out = {}
    for part in str(text).split('|'):
        key, amount = part.split('#')
        out[key] = out.get(key, 0) + int(amount)
    return out


def grant(state, awards):
    for key, amount in awards.items():
        state['items'][key] = int(state['items'].get(key, 0)) + amount


def initial():
    return {'opened': False, 'pictures': {}, 'done': [], 'jigsaw_claimed': [], 'buys': 0,
            'jigsaw_day': '', 'puppet_day': '', 'puppet_claimed': []}


def read(state):
    data = initial()
    data.update(copy.deepcopy(state.get('puzzle_events') or {}))
    return data


def board(data, picture):
    return list(data['pictures'].get(picture, [int(n) for n in PICS[picture]['picture'].split('|')]))


def snapshot(state, now):
    data = read(state)
    day = clock.day(now)
    next_buy = D['activity_jigsaw_buy'].get(str(data['buys'] + 1))
    count = len(data['done'])
    puppets = int(state['items'].get(PUPPET_ITEM, 0))
    return {'jigsaw': {'energy': int(state['items'].get('40', 0)), 'opened': data['opened'], 'done': data['done'],
                       'boards': {key: board(data, key) for key in PICS}, 'buys': data['buys'],
                       'next_buy': next_buy, 'daily': JIGSAW_DAILY, 'daily_ready': day > data['jigsaw_day'],
                       'tiers': [{'id': int(key), **row, 'claimed': int(key) in data['jigsaw_claimed'], 'ready': count >= row['complete']}
                                 for key, row in D['activity_jigsaw_award'].items()]},
            'puppet': {'amount': puppets, 'item': PUPPET_ITEM, 'daily': PUPPET_DAILY,
                       'daily_ready': day > data['puppet_day'],
                       'tiers': [{'id': int(key), **row, 'claimed': int(key) in data['puppet_claimed'], 'ready': puppets >= row['point']}
                                 for key, row in D['activity_puppet_award'].items()]}}


def action(state, request, now):
    # Validate the full action on a copy: failures leave even initialization untouched.
    work = copy.deepcopy(state)
    data = read(work)
    act = request.get('action')
    got = {}
    if act == 'open':
        if not data['opened']:
            data['opened'] = True
            got = pairs(D['misc']['activity_jigsaw_energy_init'])
    elif act in ('jigsaw_daily', 'puppet_daily'):
        prefix = 'jigsaw' if act == 'jigsaw_daily' else 'puppet'
        day = clock.day(now)
        if day <= data[prefix + '_day']:
            raise PuzzleError('Ya recogiste el suministro de hoy')
        data[prefix + '_day'] = day
        got = {'40': JIGSAW_DAILY} if prefix == 'jigsaw' else {PUPPET_ITEM: PUPPET_DAILY}
    elif act == 'buy':
        num = integer(request.get('num', 1), 1, 50)
        limit = int(D['misc']['activity_jigsaw_buy_limit'])
        if data['buys'] + num > limit:
            raise PuzzleError('Límite de compra de energía alcanzado')
        costs, rewards = {}, {}
        for index in range(data['buys'] + 1, data['buys'] + num + 1):
            row = D['activity_jigsaw_buy'][str(index)]
            for key, amount in pairs(row['cost']).items():
                costs[key] = costs.get(key, 0) + amount
            for key, amount in pairs(row['item']).items():
                rewards[key] = rewards.get(key, 0) + amount
        if any(int(work['items'].get(key, 0)) < amount for key, amount in costs.items()):
            raise PuzzleError('Faltan gemas')
        for key, amount in costs.items():
            work['items'][key] -= amount
        data['buys'] += num
        got = rewards
    elif act == 'swap':
        picture = str(integer(request.get('picture'), 1, len(PICS)))
        a, b = integer(request.get('a'), 1, 9), integer(request.get('b'), 1, 9)
        if a == b:
            raise PuzzleError('Elige dos piezas distintas')
        if int(picture) in data['done']:
            raise PuzzleError('Esta ilustración ya está completa')
        cost = pairs(D['misc']['activity_jigsaw_use_cost'])
        if any(int(work['items'].get(key, 0)) < amount for key, amount in cost.items()):
            raise PuzzleError('No tienes suficiente energía')
        pieces = board(data, picture)
        pieces[a - 1], pieces[b - 1] = pieces[b - 1], pieces[a - 1]
        for key, amount in cost.items():
            work['items'][key] -= amount
        data['pictures'][picture] = pieces
        if pieces == list(range(1, 10)):
            data['done'].append(int(picture))
            got = pairs(PICS[picture]['awards'])
    elif act in ('jigsaw_claim', 'puppet_claim'):
        is_jigsaw = act == 'jigsaw_claim'
        rows = D['activity_jigsaw_award' if is_jigsaw else 'activity_puppet_award']
        rid = integer(request.get('id'), 1, len(rows))
        claimed = data['jigsaw_claimed' if is_jigsaw else 'puppet_claimed']
        if rid in claimed:
            raise PuzzleError('Premio ya recogido')
        row = rows[str(rid)]
        progress = len(data['done']) if is_jigsaw else int(work['items'].get(PUPPET_ITEM, 0))
        if progress < row['complete' if is_jigsaw else 'point']:
            raise PuzzleError('Todavía no has alcanzado este hito')
        claimed.append(rid)
        got = pairs(row['awards'])
    else:
        raise PuzzleError('Acción no disponible')
    grant(work, got)
    work['puzzle_events'] = data
    state.clear()
    state.update(work)
    return {'got': got}
