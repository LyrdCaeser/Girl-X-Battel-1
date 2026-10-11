"""Jackpot of Fortune (activity 64, ActivityJackPotMachine; capture 2026-09-29-fb/3).

Original (data/jackpot.json): Jackpot Energy (item 57): 15 at the start, +1 every 4 h (misc activity_jackpot_energy_cd/add) while
below 20 (activity_jackpot_energy_limit). A spin costs bet x 5 energy (activity_jackpot_draw 57#5, bets 1|2|5|10) and pays the
combination it lands on x bet: 27 reel combinations of three heads with their weight (three alike 8/7/6, two alike 5/4/3, all
different nothing), in Basic (item 58, Jackpot Coin) or Super (item 305; opens after 40 spins). Super energy spent fills the
progress awards (activity_jackpot_award). Coins convert 58#1 -> 305#1 (activity_jackpot_transfer). The exchange shop is served by
gxb2/activity_kit.py (event 64).

Local (LOCAL-062): the server picked the combination; here it is a weighted pick, and the spin counter for the Super unlock
is our own (1 per spin, whatever the bet). The paid Privilege Card that unlocked Super at once isn't sold. Always available.
"""
from __future__ import annotations
import json, secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/jackpot.json').read_text())
M = D['misc']
ENERGY, COIN, SUPER_COIN = '57', '58', '305'
CD, ADD, LIMIT = int(M['activity_jackpot_energy_cd']), int(M['activity_jackpot_energy_add']), int(M['activity_jackpot_energy_limit'])
BETS = [int(x) for x in str(M['activity_jackpot_energy_bet_num']).split('|')]
BASE_COST = int(str(M['activity_jackpot_draw']).split('#')[1])
UNLOCK = int(M['activity_jackpot_unlock'])


class JackpotError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def data(state, now):
    s = state.get('jackpot')
    if not s:
        s = state['jackpot'] = {'energy_at': now, 'spins': 0, 'senior': 0, 'claimed': [], 'pos': [1, 1, 1]}
        add = pairs(M['activity_jackpot_energy_initial']); state['items'][ENERGY] = int(state['items'].get(ENERGY, 0)) + add[ENERGY]
    energy = int(state['items'].get(ENERGY, 0))
    if energy >= LIMIT: s['energy_at'] = now
    elif now > s['energy_at']:
        gain = (now - s['energy_at']) // CD * ADD
        if gain: state['items'][ENERGY] = energy + min(gain, LIMIT - energy); s['energy_at'] += (now - s['energy_at']) // CD * CD
        if int(state['items'][ENERGY]) >= LIMIT: s['energy_at'] = now
    return s


def snapshot(state, now):
    view = json.loads(json.dumps(state)); s = data(view, now)
    return {'energy': int(view['items'].get(ENERGY, 0)), 'limit': LIMIT, 'next_at': s['energy_at'] + CD if int(view['items'].get(ENERGY, 0)) < LIMIT else 0,
            'spins': s['spins'], 'unlock': UNLOCK, 'super_open': s['spins'] >= UNLOCK, 'senior': s['senior'], 'claimed': s['claimed'], 'pos': s['pos'], 'started': 'jackpot' in state,
            'coin': int(view['items'].get(COIN, 0)), 'super_coin': int(view['items'].get(SUPER_COIN, 0)), 'bets': BETS, 'base_cost': BASE_COST}


def add(state, got):
    for k, n in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + n


def action(state, request, now, rng=secrets.randbelow):
    s = data(state, now); act = request.get('action')
    if act == 'spin':
        mode = request.get('mode', 'basic'); bet = int(request.get('bet', 1))
        if mode not in ('basic', 'super') or bet not in BETS: raise JackpotError('Tirada no válida')
        if mode == 'super' and s['spins'] < UNLOCK: raise JackpotError('Super se abre tras %d tiradas (%d)' % (UNLOCK, s['spins']))
        cost = bet * BASE_COST
        if int(state['items'].get(ENERGY, 0)) < cost: raise JackpotError('Falta energía')
        state['items'][ENERGY] = int(state['items'][ENERGY]) - cost
        rows = D['machine']; n = rng(sum(r['weight'] for r in rows)); row = rows[-1]
        for r in rows:
            n -= r['weight']
            if n < 0: row = r; break
        got = {k: v * bet for k, v in pairs(row[mode]).items()}; add(state, got)
        s['spins'] += 1; s['pos'] = row['pos']
        if mode == 'super': s['senior'] += cost
        return {'got': got, 'pos': row['pos'], 'row': row['id']}
    if act == 'claim':
        i = int(request.get('index', -1)); rows = D['awards']
        if not 0 <= i < len(rows): raise JackpotError('Premio no disponible')
        if i in s['claimed']: raise JackpotError('Ya reclamado')
        if s['senior'] < rows[i]['need']: raise JackpotError('Aún no llegas')
        got = pairs(rows[i]['awards']); add(state, got); s['claimed'].append(i)
        return {'got': got}
    if act == 'transfer':
        count = int(request.get('count', 1)); cost = pairs(str(M['activity_jackpot_transfer']).split('|')[0]); gain = pairs(str(M['activity_jackpot_transfer']).split('|')[1])
        if count < 1 or count > 9999 or int(state['items'].get(COIN, 0)) < count * cost[COIN]: raise JackpotError('Faltan monedas')
        state['items'][COIN] = int(state['items'][COIN]) - count * cost[COIN]; add(state, {k: v * count for k, v in gain.items()})
        return {'got': {k: v * count for k, v in gain.items()}}
    if act == 'open':
        return {}
    raise JackpotError('Acción no disponible')
