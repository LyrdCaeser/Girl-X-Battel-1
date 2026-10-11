"""Blind Box Frenzy (activity 338; ACTIVITY_BLIND_BOX_HELP, ActivityBlindBox.lua, ActivityBlindBoxData.lua).

Original: two rounds. In a round you customize your rewards from four tiers (3, 3, 1 and 1 picks; misc activity_blind_box_select_num)
and the round's Grand Reward is always in the box. Each reward has `num` copies and a `weight`. A Blind Box Coupon (item 438) opens
one box (x1) or five (x5): every box is drawn among the copies left, weighted by weight x copies left. The selection can be changed
until you obtain any reward. The Grand Reward comes within 30 draws (misc guarantee_time 29: the 30th draw is the grand one); after
getting it in round 1 you may enter round 2 (round 1's leftovers are lost); round 2 keeps going after its grand reward.

Local (LOCAL-063): coupons came from the Blind Box Bonus pass and the paid Recharge Gift; the kit mission board (event 338, VIP EXP)
pays them and `DAILY_COUPONS` coupons are also given once per local day. The server's random draw is a plain weighted draw here.
"""
from __future__ import annotations
import json, secrets
from pathlib import Path
from . import clock

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/blind_box.json').read_text())
ROWS = {r['id']: r for r in D['rows']}
TICKET = str(D['cost']).split('#')[0]
TIERS = (2, 3, 4, 5)
DAILY_COUPONS = 3


class BlindError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def grand(rnd):
    return next(r['id'] for r in D['rows'] if r['round'] == rnd and r['tier'] == 1)


def data(state):
    s = state.get('blind_box')
    if not s:
        s = state['blind_box'] = {'round': 1, 'selects': [], 'taken': {}, 'draws': 0, 'day': ''}
    return s


def slots(s):
    return [grand(s['round'])] + list(s['selects'])


def remaining(s, rid):
    return ROWS[rid]['num'] - int(s['taken'].get(str(rid), 0))


def locked(s):
    return any(int(n) > 0 for n in s['taken'].values())


def snapshot(state, now):
    s = json.loads(json.dumps(data({'items': state['items'], 'blind_box': state.get('blind_box')}))) if state.get('blind_box') else {'round': 1, 'selects': [], 'taken': {}, 'draws': 0, 'day': ''}
    ready = len(s['selects']) == 8; sl = slots(s) if ready else [grand(s['round'])]
    total = sum(ROWS[r]['weight'] * remaining(s, r) for r in sl) or 1
    return {'round': s['round'], 'rounds': D['rounds'], 'selects': s['selects'], 'locked': locked(s), 'draws': s['draws'], 'ready': ready,
            'tickets': int(state['items'].get(TICKET, 0)), 'slots': [{'id': r, 'left': remaining(s, r), 'chance': round(100 * ROWS[r]['weight'] * remaining(s, r) / total, 2) if ready else None} for r in sl],
            'total_left': sum(remaining(s, r) for r in sl) if ready else 0,
            'grand_taken': int(s['taken'].get(str(grand(s['round'])), 0)) > 0, 'daily_ready': s['day'] != clock.day(now), 'daily': DAILY_COUPONS,
            'pool': {str(t): [r['id'] for r in D['rows'] if r['round'] == s['round'] and r['tier'] == t] for t in TIERS}}


def action(state, request, now, rng=secrets.randbelow):
    s = data(state); act = request.get('action')
    if act == 'select':
        if locked(s): raise BlindError('Ya no puedes cambiar la selección')
        ids = [int(i) for i in request.get('ids', [])]
        if len(ids) != 8 or len(set(ids)) != 8: raise BlindError('Faltan recompensas por elegir')
        for t, need in zip(TIERS, D['select_num']):
            chosen = [i for i in ids if i in ROWS and ROWS[i]['tier'] == t and ROWS[i]['round'] == s['round']]
            if len(chosen) != need: raise BlindError('Elige %d recompensa(s) del nivel %d' % (need, t - 1))
        s['selects'] = [i for t in TIERS for i in ids if ROWS[i]['tier'] == t]
        return {}
    if act == 'open':
        n = int(request.get('num', 1))
        if n not in (1, 5): raise BlindError('Solo ×1 o ×5')
        if len(s['selects']) != 8: raise BlindError('Elige primero tus recompensas')
        left = sum(remaining(s, r) for r in slots(s))
        if n > left: raise BlindError('No quedan tantas cajas')
        if int(state['items'].get(TICKET, 0)) < n: raise BlindError('Faltan cupones')
        state['items'][TICKET] = int(state['items'][TICKET]) - n
        got, ids, g = {}, [], grand(s['round'])
        for _ in range(n):
            sl = [r for r in slots(s) if remaining(s, r) > 0]
            if s['draws'] >= D['guarantee'] and remaining(s, g) > 0: pick = g          # the 30th draw is the grand reward
            else:
                w = [ROWS[r]['weight'] * remaining(s, r) for r in sl]; x = rng(sum(w)); pick = sl[-1]
                for r, wi in zip(sl, w):
                    x -= wi
                    if x < 0: pick = r; break
            s['taken'][str(pick)] = int(s['taken'].get(str(pick), 0)) + 1; s['draws'] += 1; ids.append(pick)
            for k, v in pairs(ROWS[pick]['awards']).items(): got[k] = got.get(k, 0) + v; state['items'][k] = int(state['items'].get(k, 0)) + v
        return {'got': got, 'ids': ids, 'grand': g in ids}
    if act == 'next':
        if s['round'] >= D['rounds']: raise BlindError('No hay más rondas')
        if int(s['taken'].get(str(grand(s['round'])), 0)) < 1: raise BlindError('Primero consigue el premio gordo')
        s.update(round=s['round'] + 1, selects=[], taken={}, draws=0)
        return {}
    if act == 'daily':
        if s['day'] == clock.day(now): raise BlindError('Ya recibiste los cupones de hoy')
        s['day'] = clock.day(now); state['items'][TICKET] = int(state['items'].get(TICKET, 0)) + DAILY_COUPONS
        return {'got': {TICKET: DAILY_COUPONS}}
    if act == 'open_view':
        return {}
    raise BlindError('Acción no disponible')
