"""Junior Varsity arena (ArenaWindow / ArenaChoosePlayerWindow / ArenaBattleAwardWindow, models/Arena.lua) offline.

Recovered from the client/tables: start score 1000 (arena_init_score), 2 free fights a day (arena_free_times) and
then 1 Arena Ticket (item 34) per fight, ticket price 20 gems (arena_ticket_cost), 15-day seasons, the 15 robot
opponents (arena_robot: name, level, lineup, partner levels) with score 900 + 30·i (arena_robot_min/add_score),
score coefficients per score band (arena_score), 3 reward cards per fight rolled from arena_battle_award by level,
daily/season awards by rank (arena_rank_award).

LOCAL decisions (the server ran matchmaking, ratings and the ladder, see DESIGN_DECISIONS.md LOCAL-027):
- Score change is Elo-like with K = arena_score.coefficient of the player's band: win +K·(1-E), loss -K·E, E =
  1/(1+10^((opp-me)/400)); minimum ±1 on win/loss, never below 0.
- Opponents above the robots are persistent NPC rivals built from robot lineups; partner levels scale with the
  player's level and the rival's score. The ladder is 50 rivals (robots + NPCs) whose rank decides the awards.
- The player gets one of the 3 rolled cards (the others are revealed, as in the original flip animation).
- Daily rank award is claimed from the window once per local day; season awards when the 15-day season ends.
"""
from __future__ import annotations
import json, math, secrets, time
from . import clock
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/arena.json').read_text())
M = DATA['misc']
ROBOTS = DATA['arena_robot']
TICKET = '34'
BOX = {}
for _r in DATA['dropbox']:
    BOX.setdefault(int(_r['dropbox_id']), []).append(_r)
RIVALS = 50


def day(now):
    return clock.day(now)


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]; out[k] = out.get(k, 0) + int(n)
    return out


def ladder():
    """50 persistent rivals: the 15 original robots (900 + 30·i) followed by NPC rivals up to ~3000 points."""
    base, add = int(M['arena_robot_min_score']), int(M['arena_robot_add_score'])
    out = []
    for i in range(RIVALS):
        r = ROBOTS[i % len(ROBOTS)]
        score = base + add * i if i < len(ROBOTS) else base + add * len(ROBOTS) + (i - len(ROBOTS) + 1) * 48
        name = r['name'] if i < len(ROBOTS) else f"{ROBOTS[(i * 7) % len(ROBOTS)]['name']}{(i * 37) % 90 + 10}"
        out.append({'id': i + 1, 'name': name, 'score': score, 'robot': r['id'], 'lv': r['lv'], 'avatar': r['avatar_id'], 'is_robot': i < len(ROBOTS)})
    return out


def saved(state, now):
    a = state.setdefault('arena', {})
    a.setdefault('score', int(M['arena_init_score'])); a.setdefault('best', a['score'])
    a.setdefault('season_start', now); a.setdefault('free', {'day': day(now), 'used': 0})
    a.setdefault('rivals', {str(r['id']): r['score'] for r in ladder()}); a.setdefault('records', []); a.setdefault('claimed_day', '')
    a.setdefault('enemies', []); a.setdefault('wins', 0)
    if a['free']['day'] != day(now):
        a['free'] = {'day': day(now), 'used': 0}
    return a


def rank_of(a):
    return 1 + sum(1 for s in a['rivals'].values() if s > a['score'])


def rank_award(rank):
    for r in DATA['arena_rank_award']:
        f = str(r['rank_front'])
        lo, hi = (int(f), int(f)) if '-' not in f else map(int, f.split('-'))
        if lo <= rank <= hi:
            return r
    return DATA['arena_rank_award'][-1]


def coefficient(score):
    k = 100
    for r in DATA['arena_score']:
        if score >= int(r['interval'] or 0):
            k = int(r['coefficient'])
    return k


def expected(me, opp):
    return 1 / (1 + 10 ** ((opp - me) / 400))


def lineup(rival, level):
    r = next(x for x in ROBOTS if x['id'] == rival['robot'])
    ids = [int(x) for x in str(r['partner_ids']).split('|')]
    lvs = [int(x) for x in str(r['partner_lv']).split('|')]
    # Robots keep their original levels; NPC rivals scale with the player's level and their score.
    scale = 0 if rival['is_robot'] else max(1, int(level * min(1.15, 0.7 + (rival['score'] - 1300) / 4000)))
    return [{'table_id': t, 'lv': max(l, scale), 'pos': i + 1} for i, (t, l) in enumerate(zip(ids, lvs))]


def power(team):
    return sum(40 * u['lv'] + 60 for u in team)


def enemies(a, level, rng=secrets.randbelow):
    """Four opponents around the player's score (arena_match: two above, two below)."""
    rivals = sorted(ladder(), key=lambda r: abs(a['rivals'][str(r['id'])] - a['score']))[:10]
    picks = []
    for r in rivals:
        if len(picks) < 4 and r['id'] not in [p['id'] for p in picks]:
            picks.append(r)
    out = []
    for r in sorted(picks, key=lambda r: -a['rivals'][str(r['id'])]):
        team = lineup(r, level)
        out.append({'id': r['id'], 'name': r['name'], 'score': a['rivals'][str(r['id'])], 'lv': max(r['lv'], max(u['lv'] for u in team)),
                    'avatar': r['avatar'], 'power': power(team), 'team': team, 'is_robot': r['is_robot']})
    return out


def board_row(r, a, level):
    """ArenaWindowItem: avatar + level, name, power and the defence line-up (ArenaFormationWindow on tapping the icon)."""
    team = lineup(r, level)
    return {'id': r['id'], 'name': r['name'], 'score': a['rivals'][str(r['id'])], 'lv': max(r['lv'], max(u['lv'] for u in team)),
            'avatar': r['avatar'], 'power': power(team), 'teams': [team]}


def snapshot(state, level, now=None):
    now = int(time.time()) if now is None else now
    a = saved(dict(state), now) if 'arena' not in state else state['arena']
    free_left = max(0, int(M['arena_free_times']) - (a['free']['used'] if a['free']['day'] == day(now) else 0))
    rank = rank_of(a)
    board = sorted([board_row(r, a, level) for r in ladder()] +
                   [{'name': state.get('name') or 'Tú', 'score': a['score'], 'lv': level, 'me': True}], key=lambda x: -x['score'])[:20]
    season_end = a['season_start'] + int(M['arena_season_time']) * 86400
    return {'score': a['score'], 'best': a['best'], 'rank': rank, 'free': free_left, 'tickets': int(state['items'].get(TICKET, 0)),
            'ticket_price': int(M['arena_ticket_cost']), 'enemies': [{k: v for k, v in e.items() if k != 'team'} for e in a.get('enemies', [])],
            'records': a['records'][:10], 'board': board, 'daily_award': rank_award(rank)['awards'], 'season_award': rank_award(rank)['season_awards'],
            'daily_claimed': a['claimed_day'] == day(now), 'season_end': season_end, 'wins': a['wins']}


def roll(level, rng):
    rows = [r for r in DATA['arena_battle_award'] if int(r['level_begin']) <= level <= int(r['level_end'])]
    cards = []
    for r in rows:
        opts = BOX.get(int(r['dropbox_id']), [])
        total = sum(int(o['weight']) for o in opts); x = rng(total) if total else 0
        for o in opts:
            x -= int(o['weight'])
            if x < 0:
                k, n = str(o['item']).split('#')[:2]; cards.append({k: int(n)}); break
    return cards


def action(state, request, level, now=None, rng=secrets.randbelow, fight=None):
    """fight(team_b) -> (win, report_index) runs the original battle engine with the rival lineup."""
    now = int(time.time()) if now is None else now
    a = saved(state, now)
    items = state['items']
    kind = request.get('action')
    result = {}
    if now >= a['season_start'] + int(M['arena_season_time']) * 86400:
        got = pairs(rank_award(rank_of(a))['season_awards'])
        for k, n in got.items():
            items[k] = int(items.get(k, 0)) + n
        a.update(score=int(M['arena_init_score']), season_start=now, rivals={str(r['id']): r['score'] for r in ladder()}, enemies=[])
        result['season_got'] = got
    if kind in ('open', 'refresh'):
        a['enemies'] = enemies(a, level, rng)
    elif kind == 'fight':
        rid = int(request.get('id', 0))
        enemy = next((e for e in a['enemies'] if e['id'] == rid), None)
        if not enemy:
            raise ValueError('Rival no disponible: actualiza la lista')
        if a['free']['used'] < int(M['arena_free_times']):
            a['free']['used'] += 1
        elif int(items.get(TICKET, 0)) >= 1:
            items[TICKET] = int(items[TICKET]) - 1
        else:
            raise ValueError('No quedan combates gratis ni Arena Tickets')
        win, report = fight(enemy['team']) if fight else (True, None)
        k, e = coefficient(a['score']), expected(a['score'], enemy['score'])
        delta = max(1, round(k * (1 - e))) if win else -max(1, round(k * e))
        a['score'] = max(0, a['score'] + delta); a['best'] = max(a['best'], a['score'])
        a['rivals'][str(rid)] = max(0, a['rivals'][str(rid)] - (delta if win else delta // 2))
        a['wins'] += 1 if win else 0
        cards = roll(level, rng)
        pick = rng(len(cards)) if cards else 0
        got = cards[pick] if cards else {}
        for kk, n in got.items():
            items[kk] = int(items.get(kk, 0)) + n
        a['records'].insert(0, {'at': now, 'name': enemy['name'], 'win': win, 'delta': delta}); a['records'] = a['records'][:20]
        a['enemies'] = enemies(a, level, rng)
        result.update(win=win, delta=delta, cards=cards, pick=pick, got=got, battle=report)
    elif kind == 'buy_ticket':
        n = max(1, int(request.get('count', 1))); cost = int(M['arena_ticket_cost']) * n
        if int(items.get('2', 0)) < cost:
            raise ValueError('Faltan gemas')
        items['2'] = int(items['2']) - cost; items[TICKET] = int(items.get(TICKET, 0)) + n
    elif kind == 'daily':
        if a['claimed_day'] == day(now):
            raise ValueError('Ya reclamado hoy')
        got = pairs(rank_award(rank_of(a))['awards'])
        for kk, n in got.items():
            items[kk] = int(items.get(kk, 0)) + n
        a['claimed_day'] = day(now); result['got'] = got
    else:
        raise ValueError('Acción de arena no disponible')
    return result
