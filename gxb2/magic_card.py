"""Magic Card (activity 134, ActivityIceSecret re-skinned; captures 2026-09-29-fb/53 and 112) and Magician's Assistant
(ActivityIceSecretMission).

Each round shows its 25 cards face up: the 24 normal rewards and, in the middle (position 13), the Ultimate Reward the player
sets from those unlocked by the round (type 1, `level` <= round, used fewer than `limit` times). Start hides and shuffles
them; each card flipped costs 15 Magic Wands (180). When the Ultimate Reward comes out its card turns into NEXT: tapping it
starts the next round (the Ultimate Reward must be set again). The player may keep flipping the round's other cards first
(ACTIVITY_ICE_SECRET_GAME_TIP). Magician's Assistant gives Magic Wands for daily and weekly missions.

Local rules (LOCAL-054): the server chose which reward each flip gives; locally the flip on which the Ultimate Reward
appears is drawn at Start with misc activity_ice_secret_weight (25 weights, one per flip, peaking at the 13th) and every
other flip gives one of the remaining normal rewards at random. Missions use the local counters; the ones whose system
does not exist offline (Furniture, gems spent, Elemental Orbs, Rudders) are not shown, "a battle in
Magician's Assistant" (the Backstage Prep boss, not offline) counts flipped cards, and "Complete all the other missions"
counts the shown ones. The event is always open, starts with 150 Magic Wands, and the paid Magic Gift Box is not sold."""
from __future__ import annotations
import json, secrets
from . import clock
from pathlib import Path
from . import missions as daily

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/magic_card.json').read_text())
WAND = '180'
COST = D['hammer']
BIG_POS = 12  # position 13 of the 5x5 board
NORMAL = [int(k) for k, r in sorted(D['awards'].items(), key=lambda x: int(x[0])) if int(r['type']) == 0]
HIDDEN = {5, 7, 16, 17, 18, 19}
# mission id → (period, local counter)
COUNTER = {2: 'tower', 3: 'arena', 4: 'magic_flip', 6: 'login', 8: 'gamble', 9: 'gamble', 10: 'advanced', 11: 'advanced',
           12: 'enroll', 13: 'enroll', 14: 'star5', 15: 'graduate', 20: 'radar', 21: 'radar'}
WEEK = 7 * 86400


class MagicError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def data(state, now):
    s = state.get('magic_card')
    if not s:
        s = state['magic_card'] = {'round': 1, 'status': 0, 'select': 0, 'used': {}, 'board': [], 'open': [], 'big_at': 0, 'got_big': -1,
                                   'daily_day': '', 'daily': [], 'week': 0, 'weekly': [], 'base': {}}
        state['items'][WAND] = int(state['items'].get(WAND, 0)) + 150  # a starting stack so the event can be tried
    m = daily.saved(state, now)
    if s['daily_day'] != m['day']: s['daily_day'] = m['day']; s['daily'] = []
    week = clock.week_index(now) + 1  # local weeks start on Monday
    if s['week'] != week: s['week'] = week; s['weekly'] = []; s['base'] = dict(m['totals'])
    return s


def bigs(s):
    """Ultimate Rewards that can be set this round."""
    return [int(k) for k, r in sorted(D['awards'].items(), key=lambda x: int(x[0]))
            if int(r['type']) == 1 and int(r['level']) <= s['round'] and int(s['used'].get(k, 0)) < int(r['limit'])]


def mission_value(state, s, mid):
    m = D['missions'][str(mid)]; totals = state['missions']['totals']
    if mid == 1: return sum(1 for i in shown() if D['missions'][str(i)]['type'] == 0 and i != 1 and mission_done(state, s, i))
    key = COUNTER.get(mid)
    if not key: return 0
    if int(m['type']) == 0: return int(state['missions']['counts'].get(key, 0))
    return int(totals.get(key, 0)) - int(s['base'].get(key, 0)) + (key == 'login')  # today counts


def need(state, mid):
    if mid == 1: return sum(1 for i in shown() if D['missions'][str(i)]['type'] == 0 and i != 1)
    return int(D['missions'][str(mid)]['complete_value'])


def mission_done(state, s, mid):
    return mission_value(state, s, mid) >= need(state, mid)


def shown():
    return [int(k) for k in sorted(D['missions'], key=int) if int(k) not in HIDDEN]


def snapshot(state, now):
    view = json.loads(json.dumps(state)); s = data(view, now)
    board = []
    for pos in range(25):
        if s['status'] == 0: board.append({'award': s['select'] if pos == BIG_POS else NORMAL[pos - (pos > BIG_POS)], 'open': True})
        else:
            got = s['board'][pos] if pos in s['open'] else 0
            board.append({'award': got, 'open': pos in s['open'], 'next': pos == s['got_big']})
    return {'round': s['round'], 'status': s['status'], 'select': s['select'], 'bigs': bigs(s), 'board': board, 'wands': int(view['items'].get(WAND, 0)),
            'cost': COST, 'got_big': s['got_big'] >= 0,
            'missions': [{'id': i, 'weekly': int(D['missions'][str(i)]['type']) == 1, 'have': mission_value(view, s, i), 'need': need(view, i),
                          'award': D['missions'][str(i)]['award'], 'claimed': i in (s['weekly'] if int(D['missions'][str(i)]['type']) == 1 else s['daily'])} for i in shown()]}


def action(state, request, now, rng=None):
    rng = rng or secrets.randbelow
    s = data(state, now); act = request.get('action')
    if act == 'select':
        aid = int(request.get('id') or 0)
        if s['status'] != 0: raise MagicError('La ronda ya ha empezado')
        if aid not in bigs(s): raise MagicError(D['text']['ACTIVITY_ICE_SECRET_MAXAWARD_TIP'].replace('{1}', str(D['awards'][str(aid)]['level'])) if str(aid) in D['awards'] else 'Recompensa inexistente')
        s['select'] = aid
        return {}
    if act == 'start':
        if s['status'] != 0: raise MagicError('La ronda ya ha empezado')
        if not s['select']: raise MagicError(D['text']['ACTIVITY_ICE_SECRET_MAXAWARD_ERROR'])
        w = D['weights']; roll = rng(sum(w)); at = 0
        while roll >= w[at]: roll -= w[at]; at += 1
        s.update(status=1, board=[0] * 25, open=[], big_at=at + 1, got_big=-1)
        return {}
    if act == 'flip':
        pos = int(request.get('pos', -1))
        if s['status'] != 1: raise MagicError('Pulsa Start para empezar la ronda')
        if not 0 <= pos < 25 or pos in s['open']: raise MagicError('Esa carta ya está girada')
        if int(state['items'].get(WAND, 0)) < COST: raise MagicError('Not enough Magic Wand')
        state['items'][WAND] = int(state['items'][WAND]) - COST
        n = len(s['open']) + 1
        if n == s['big_at'] or (s['got_big'] < 0 and n == 25): award = s['select']; s['got_big'] = pos; s['used'][str(award)] = int(s['used'].get(str(award), 0)) + 1
        else:
            seen = {s['board'][p] for p in s['open']}
            left = [a for a in NORMAL if a not in seen]
            award = left[rng(len(left))]
        s['board'][pos] = award; s['open'].append(pos)
        got = pairs(D['awards'][str(award)]['award'])
        for k, v in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + v
        daily.record(state, 'magic_flip', 1, now)
        return {'award': award, 'got': got, 'big': award == s['select'] and s['got_big'] == pos}
    if act == 'next':
        if s['status'] != 1 or s['got_big'] < 0: raise MagicError('Primero consigue la Ultimate Reward')
        s.update(status=0, round=s['round'] + 1, select=0, board=[], open=[], big_at=0, got_big=-1)
        return {}
    if act == 'mission':
        mid = int(request.get('id') or 0)
        if mid not in shown(): raise MagicError('Misión inexistente')
        done = s['weekly'] if int(D['missions'][str(mid)]['type']) == 1 else s['daily']
        if mid in done: raise MagicError('Ya reclamada')
        if not mission_done(state, s, mid): raise MagicError('Misión sin completar')
        done.append(mid); got = pairs(D['missions'][str(mid)]['award'])
        for k, v in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + v
        return {'got': got}
    raise MagicError('Acción de Magic Card desconocida')
