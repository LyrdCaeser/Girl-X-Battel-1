"""Friend Hearts (Friend.lua sendGifts / getGifts, FriendWindow "Claim & Send").

Original rules kept: a Heart (item 11, used in the BFF Capsule) can be sent to each friend once a day and claimed from each
friend once a day, at most love_coin_daily_max (30) claimed a day and friend_love_sum_max (1000) held.

LOCAL (LOCAL-081): there is no friend server. The friends are the local contacts of the Friends list (home_systems
contacts); every contact has a Heart waiting for you each day (the original needed the friend to send it). "Recommended"
offers the Junior Varsity ladder rivals as contacts to add, so the list is usable from the first day. Sending counts for the
Daily Task and the Fantasy Book task "Send out 5 Hearts" (missions counter 'hearts').
"""
from __future__ import annotations
import time
from . import clock, missions

HEART = '11'
DAILY_MAX = 30     # misc love_coin_daily_max
HELD_MAX = 1000    # misc friend_love_sum_max
CONTACT_MAX = 30   # home_systems contact_add limit


class HeartError(ValueError):
    pass


def saved(state, now):
    h = state.setdefault('hearts', {'day': '', 'sent': [], 'got': []})
    if h['day'] != clock.day(now):
        h.update(day=clock.day(now), sent=[], got=[])
    return h


def contacts(state):
    return (state.get('home_systems') or {}).get('contacts') or []


def recommended(state):
    from . import arena
    have = {c['name'] for c in contacts(state)}
    return [{'rid': r['id'], 'name': r['name'], 'lv': r['lv']} for r in arena.ladder() if r['name'] not in have][:10]


def snapshot(state, now=None):
    now = int(time.time()) if now is None else now
    h = dict(state.get('hearts') or {'day': '', 'sent': [], 'got': []})
    today = h.get('day') == clock.day(now)
    sent, got = (h['sent'], h['got']) if today else ([], [])
    return {'held': int(state['items'].get(HEART, 0)), 'max': HELD_MAX, 'daily_max': DAILY_MAX, 'sent': sent, 'got': got,
            'recommended': recommended(state), 'contact_max': CONTACT_MAX}


def action(state, request, now=None):
    now = int(time.time()) if now is None else now
    h = saved(state, now); kind = request.get('action'); people = contacts(state)
    ids = request.get('ids'); ids = [c['id'] for c in people] if ids in (None, 'all') else [int(x) for x in ids]
    valid = {c['id'] for c in people}
    result = {'sent': 0, 'got': {}}
    if kind in ('send', 'all'):
        for cid in ids:
            if cid in valid and cid not in h['sent']:
                h['sent'].append(cid); result['sent'] += 1
        if result['sent']: missions.record(state, 'hearts', result['sent'], now)
        elif kind == 'send': raise HeartError('Ya enviaste Hearts a estos amigos hoy')
    if kind in ('claim', 'all'):
        n = 0
        for cid in ids:
            if cid not in valid or cid in h['got']: continue
            if int(state['items'].get(HEART, 0)) + n >= HELD_MAX:
                if not n and kind == 'claim': raise HeartError('Hearts limit has been reached')
                break
            if len(h['got']) >= DAILY_MAX:
                if not n and kind == 'claim': raise HeartError("Already claimed today's maximum Hearts")
                break
            h['got'].append(cid); n += 1
        if n:
            state['items'][HEART] = int(state['items'].get(HEART, 0)) + n; result['got'] = {HEART: n}
        elif kind == 'claim': raise HeartError('No hay Hearts por reclamar')
    if kind == 'add':
        rec = next((r for r in recommended(state) if r['rid'] == int(request.get('rid', 0))), None)
        if not rec: raise HeartError('Jugador no disponible')
        home = state.setdefault('home_systems', {}); home.setdefault('contacts', []); home.setdefault('next_id', 1)
        if len(home['contacts']) >= CONTACT_MAX: raise HeartError('Máximo 30 contactos locales')
        home['contacts'].append({'id': home['next_id'], 'name': rec['name'], 'avatar': 'head_1001', 'local': True}); home['next_id'] += 1
    elif kind not in ('send', 'claim', 'all'):
        raise HeartError('Acción de Hearts desconocida')
    if kind == 'all' and not result['sent'] and not result['got']: raise HeartError('Nada que enviar ni reclamar hoy')
    return result
