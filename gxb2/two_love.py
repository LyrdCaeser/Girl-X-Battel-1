"""Matching Pairs (activity 331, Activity2LoveWindow / Activity2LoveData; capture 2026-09-29-fb/88).

Sixteen cards, eight pairs (activity_2love_awards: `group` = pair, `weight`). Unrevealed places show the rewards still to be
found; Start (1 Arrow of Love 427, misc activity_2love_random_cost; the first one free) shuffles them face down, then one
card is tapped and the server reveals which card sits there, by weight among the ones left (the second card of a pair
weighs far less than the first). Revealing both cards of a pair gives its reward. "Recharge Task"
(activity_2love_mission): 1 Arrow of Love at 50 / 250 / 500 / 1000 / 2000 / 3000 / 4000 VIP EXP gained during the event.

Local rules (LOCAL-055): VIP EXP comes from recharges, which don't exist offline; the Recharge Task counts the VIP EXP
earned by achievements while playing (gxb2/vip.py, LOCAL-050) and one Arrow of Love is given each day the event is opened. The event is always available; after all 16 cards are revealed a new
board can be dealt (the free first attempt comes back)."""
from __future__ import annotations
import json, secrets
from pathlib import Path
from . import missions as daily, vip

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/two_love.json').read_text())
ARROW = '427'
CARDS = {int(k): r for k, r in D['awards'].items()}


class LoveError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def data(state, now):
    m = daily.saved(state, now)
    s = state.get('two_love')
    if not s:
        s = state['two_love'] = {'ids': [0] * 16, 'is_cost': 0, 'free': 1, 'claimed': [], 'vip_base': vip.exp(state), 'day': ''}
    if 'vip_base' not in s:
        # save from the provisional popularity counter: keep the progress already earned inside the event
        s['vip_base'] = vip.exp(state) - (int(m['totals'].get('popularity', 0)) - int(s.pop('base', 0)))
    if s['day'] != m['day']:
        s['day'] = m['day']; state['items'][ARROW] = int(state['items'].get(ARROW, 0)) + 1  # daily Arrow of Love (local)
    return s


def popularity(state, s):
    return vip.exp(state) - s['vip_base']


def snapshot(state, now):
    view = json.loads(json.dumps(state)); s = data(view, now)
    return {'ids': s['ids'], 'is_cost': s['is_cost'], 'free': s['free'], 'arrows': int(view['items'].get(ARROW, 0)), 'over': all(s['ids']),
            'popularity': popularity(view, s), 'claimed': s['claimed']}


def action(state, request, now, rng=None):
    rng = rng or secrets.randbelow
    s = data(state, now); act = request.get('action')
    if act == 'start':
        if s['is_cost']: raise LoveError('Ya puedes elegir una carta')
        if all(s['ids']): raise LoveError('All Rewards are obtained')
        cost = pairs(D['cost'])
        if not s['free']:
            if any(int(state['items'].get(k, 0)) < v for k, v in cost.items()): raise LoveError('Not enough Arrow of Love')
            for k, v in cost.items(): state['items'][k] = int(state['items'][k]) - v
        s['free'] = 0; s['is_cost'] = 1
        return {}
    if act == 'flip':
        idx = int(request.get('index', -1))
        if not s['is_cost']: raise LoveError('Pulsa Start primero')
        if not 0 <= idx < 16 or s['ids'][idx]: raise LoveError('Esa carta ya está descubierta')
        left = [c for c in CARDS if c not in s['ids']]
        total = sum(int(CARDS[c]['weight']) for c in left); roll = rng(total)
        for card in left:
            roll -= int(CARDS[card]['weight'])
            if roll < 0: break
        s['ids'][idx] = card; s['is_cost'] = 0
        group = int(CARDS[card]['group']); got = {}
        if all(c in s['ids'] for c in CARDS if int(CARDS[c]['group']) == group):
            got = pairs(CARDS[card]['awards'])
            for k, v in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + v
        return {'card': card, 'got': got, 'pair': bool(got)}
    if act == 'reset':
        if not all(s['ids']): raise LoveError('Aún quedan cartas')
        s.update(ids=[0] * 16, is_cost=0, free=1)
        return {}
    if act == 'mission':
        mid = str(request.get('id')); row = D['missions'].get(mid)
        if not row: raise LoveError('Misión inexistente')
        if int(mid) in s['claimed']: raise LoveError('Ya reclamada')
        if popularity(state, s) < int(row['num']): raise LoveError('Aún no llegas')
        s['claimed'].append(int(mid)); got = pairs(row['awards'])
        for k, v in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + v
        return {'got': got}
    raise LoveError('Acción de Matching Pairs desconocida')
