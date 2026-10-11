"""Deep Sea Treasures (activity 329) and the Palace Vaults collection (330). See tools/extract_pirate.py for the sources.

Original: five lands (Sea Lord's Palace, The Beach, Coastal Waters, Open Sea, Abyssal Palace). A Raid on a land costs 1 Voyager
Compass (410) and always pays 20 Pirate Coins (411); besides that it rolls that land's dropbox once. A Chest (one of 5 vaults, chance
30/25/20/15/10 %) falls with the 20 % of misc explore_is_drop and is guaranteed after 9 raids without one (the 10th). Each chest also
pays Pirate Coins (30-120). The Collection Progress counts the 5 vaults you own; each one you hold pays its collection reward once.
Up to 100 raids at a time. The vault shop (Palace Vaults 330) is gxb2/activity_kit.py; its bigger vaults open with Pirate Coins spent.

Local (LOCAL-064): the story (activity_pirate_plot, 348 lines) isn't rebuilt and every land is open; Voyager Compasses came from the
paid Server Pack and events, so here the free pack (misc activity_pirate_giftbag_free_awards) is claimed once and `DAILY_COMPASS`
compasses arrive each local day.
"""
from __future__ import annotations
import json, secrets
from pathlib import Path
from . import clock

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/pirate.json').read_text())
M = D['misc']
COMPASS, COIN = '410', '411'
GUARANTEE = int(M['activity_pirate_explore_dropbox_guarantee'])
P_CHEST = int(str(M['activity_pirate_explore_is_drop']).split('|')[0])      # out of 100
MAX_RAIDS = 100
DAILY_COMPASS = 15


class PirateError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def data(state):
    s = state.get('pirate')
    if not s:
        s = state['pirate'] = {'raids': 0, 'no_box': 0, 'claimed': [], 'day': '', 'pack': False, 'chests': {}}
    return s


def pick(rows, rng):
    x = rng(sum(r['weight'] for r in rows))
    for r in rows:
        x -= r['weight']
        if x < 0: return r
    return rows[-1]


def snapshot(state, now):
    s = json.loads(json.dumps(state.get('pirate') or {'raids': 0, 'no_box': 0, 'claimed': [], 'day': '', 'pack': False, 'chests': {}}))
    have = {str(c['item']): int(state['items'].get(str(c['item']), 0)) for c in D['collection']}
    return {'compass': int(state['items'].get(COMPASS, 0)), 'coin': int(state['items'].get(COIN, 0)), 'raids': s['raids'], 'claimed': s['claimed'],
            'guarantee_in': max(1, GUARANTEE + 1 - int(s['no_box'])), 'have': have, 'daily_ready': s['day'] != clock.day(now), 'daily': DAILY_COMPASS,
            'pack_ready': not s['pack'], 'pack': M['activity_pirate_giftbag_free_awards'], 'started': 'pirate' in state}


def add(state, got):
    for k, n in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + n


def action(state, request, now, rng=secrets.randbelow):
    s = data(state); act = request.get('action')
    if act == 'raid':
        land = int(request.get('land', 0)); n = int(request.get('num', 1))
        if not 1 <= land <= len(D['lands']) or not 1 <= n <= MAX_RAIDS: raise PirateError('Incursión no válida')
        cost = pairs(M['activity_pirate_explore_cost'])[COMPASS] * n
        if int(state['items'].get(COMPASS, 0)) < cost: raise PirateError('Faltan brújulas')
        state['items'][COMPASS] = int(state['items'][COMPASS]) - cost
        got, chests = {}, []
        coin = pairs(M['activity_pirate_drop_awards'])
        for _ in range(n):
            for k, v in coin.items(): got[k] = got.get(k, 0) + v
            for k, v in pairs(pick(D['lands'][land - 1]['drop'], rng)['awards']).items(): got[k] = got.get(k, 0) + v
            s['no_box'] = int(s['no_box'])
            if s['no_box'] >= GUARANTEE or rng(100) < P_CHEST:
                ch = pick(D['chests'], rng); chests.append(ch['id']); s['no_box'] = 0
                for k, v in pairs(ch['awards']).items(): got[k] = got.get(k, 0) + v
            else: s['no_box'] += 1
        add(state, got); s['raids'] += n
        return {'got': got, 'chests': chests}
    if act == 'collect':
        i = int(request.get('id', 0)); row = next((c for c in D['collection'] if c['id'] == i), None)
        if not row: raise PirateError('Recompensa no disponible')
        if i in s['claimed']: raise PirateError('Ya reclamada')
        if int(state['items'].get(str(row['item']), 0)) < row['need']: raise PirateError('Esta recompensa sigue bloqueada')
        got = pairs(row['awards']); add(state, got); s['claimed'].append(i)
        return {'got': got}
    if act == 'daily':
        if s['day'] == clock.day(now): raise PirateError('Ya recibiste las brújulas de hoy')
        s['day'] = clock.day(now); add(state, {COMPASS: DAILY_COMPASS}); return {'got': {COMPASS: DAILY_COMPASS}}
    if act == 'pack':
        if s['pack']: raise PirateError('Ya reclamaste el paquete gratis')
        got = pairs(M['activity_pirate_giftbag_free_awards']); add(state, got); s['pack'] = True
        return {'got': got}
    if act == 'open':
        return {}
    raise PirateError('Acción no disponible')
