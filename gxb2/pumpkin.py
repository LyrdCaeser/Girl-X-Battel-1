"""Halloween Pumpkin Patch (activity 150, ActivityHalloweenPumpkinField; capture 2026-09-29-fb/78).

Ten pumpkins (1 large, 2 medium, 3 small, 4 tiny). "Cut" uses 1 Pumpkin Dagger (182) to cut one pumpkin still whole, which
gives one reward of its row (activity_halloween_award rows 1-10, by weight). When the ten are cut, "Claim" gives the round
reward (the rows with times >= 1, one per round, the last one repeating) and the pumpkins grow back. Daggers can be bought
with gems (misc halloween_buy 2#150 each, halloween_limit 30).

Local rules (LOCAL-065): the server chose which pumpkin a cut opens; locally it is one of the whole ones at random. Daggers
came from Enroll Exam, the daily mail and packs: locally the event starts with 10, gives 5 each day it is opened, and the
purchase limit (30) is per day. The event is always available."""
from __future__ import annotations
import json, secrets
from pathlib import Path
from . import local_config
from . import missions as daily

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/pumpkin.json').read_text())
DAGGER = '182'


class PumpkinError(ValueError):
    pass


def pairs(text):
    out = []
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out.append((k, int(v)))
    return out


def data(state, now):
    m = daily.saved(state, now)
    s = state.get('pumpkin')
    if not s:
        s = state['pumpkin'] = {'times': 0, 'awards': [0] * 10, 'buy': 0, 'day': ''}
        state['items'][DAGGER] = int(state['items'].get(DAGGER, 0)) + 5  # starting daggers (+5 of the day = 10)
    if s['day'] != m['day']:
        s['day'] = m['day']; s['buy'] = 0; state['items'][DAGGER] = int(state['items'].get(DAGGER, 0)) + 5
    return s


def round_row(s):
    return D['rounds'][min(s['times'], len(D['rounds']) - 1)]


def snapshot(state, now):
    view = json.loads(json.dumps(state)); s = data(view, now)
    return {'round': s['times'] + 1, 'awards': s['awards'], 'left': s['awards'].count(0), 'daggers': int(view['items'].get(DAGGER, 0)),
            'buy': s['buy'], 'limit': D['limit'], 'final': round_row(s)['award']}


def action(state, request, now, rng=None):
    rng = rng or secrets.randbelow
    s = data(state, now); act = request.get('action')
    if act == 'cut':
        whole = [i for i, a in enumerate(s['awards']) if not a]
        if not whole: raise PumpkinError('Reclama la recompensa de la ronda')
        if int(state['items'].get(DAGGER, 0)) < 1: raise PumpkinError('Not enough Pumpkin Dagger')
        state['items'][DAGGER] = int(state['items'][DAGGER]) - 1
        i = whole[rng(len(whole))]; row = D['pumpkins'][i]
        weights = [int(w) for w in str(row['weight']).split('|')]; roll = rng(sum(weights)); idx = 0
        while roll >= weights[idx]: roll -= weights[idx]; idx += 1
        k, v = pairs(row['award'])[idx]
        state['items'][k] = int(state['items'].get(k, 0)) + v
        s['awards'][i] = idx + 1
        return {'pumpkin': i, 'got': {k: v}}
    if act == 'claim':
        if s['awards'].count(0): raise PumpkinError(D['text'].get('ACTIVITY_HALLOWEEN_TEXT2', 'Cut 10 Pumpkins first'))
        got = {}
        for k, v in pairs(round_row(s)['award']): state['items'][k] = int(state['items'].get(k, 0)) + v; got[k] = got.get(k, 0) + v
        s['times'] += 1; s['awards'] = [0] * 10
        return {'got': got}
    if act == 'buy':
        n = max(1, int(request.get('num') or 1))
        if s['buy'] + n > D['limit']: raise PumpkinError('Límite de compra alcanzado')
        cost = {k: local_config.shop_cost(v) * n for k, v in pairs(D['buy']) if k != DAGGER}
        if any(int(state['items'].get(k, 0)) < v for k, v in cost.items()): raise PumpkinError('Faltan gemas')
        for k, v in cost.items(): state['items'][k] = int(state['items'][k]) - v
        state['items'][DAGGER] = int(state['items'].get(DAGGER, 0)) + n; s['buy'] += n
        return {}
    raise PumpkinError('Acción de Pumpkin Patch desconocida')
