"""Arena 3v3 (Arena3v3Window / Arena3v3BattleFormationWindow, models/Arena3v3.lua) offline with simulated rivals.

Recovered from the client (data/arena3v3.json, tools/extract_arena3v3.py):
- ARENA_3V3_HELP: three teams of Girls (at least 1 each, up to 6), best of three battles (the first to win 2), each battle
  15 rounds, the result adds to / deducts from the rank score; the last 10 battles are kept in the Battle Record.
- A fight costs arena_3v3_ticket_cost (3 Arena Tickets, item 34); arena_3v3_open_awards (5 tickets) when it opens.
- After a fight: 3 reward cards rolled from arena_battle_award_3v3 by player level (one is yours, as in Junior Varsity).
- Season awards by rank: arena_rank_award_3v3 (rank_front "a" or "a-b").

LOCAL decisions (DESIGN_DECISIONS.md LOCAL-069; the server ran matchmaking and the ladder, as in LOCAL-027):
- Rivals are the Junior Varsity ladder (gxb2/arena.py: 15 original robots + NPC rivals) with a separate 3v3 score; each
  rival fields three teams built from three robot lineups, scaled like the Junior Varsity NPCs.
- The score uses the Junior Varsity Elo rule (arena.coefficient / arena.expected); a 2-0 counts 1.25×.
- Seasons last arena_season_time (15) days like Junior Varsity and start with the player's first visit.
"""
from __future__ import annotations
import json, secrets, time
from pathlib import Path
from . import arena, clock

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/arena3v3.json').read_text())
TICKET = arena.TICKET
COST = int(str(DATA['misc']['arena_3v3_ticket_cost']).split('#')[1])
OPEN = arena.pairs(DATA['misc']['arena_3v3_open_awards'])
INIT = int(arena.M['arena_init_score'])
SEASON = int(arena.M['arena_season_time']) * 86400
BOX = {}
for _r in DATA['dropbox']:
    BOX.setdefault(int(_r['dropbox_id']), []).append(_r)


class Arena3v3Error(ValueError):
    pass


def saved(state, now):
    a = state.setdefault('arena3v3', {})
    if 'score' not in a:
        a.update(score=INIT, best=INIT, season_start=now, rivals={str(r['id']): r['score'] for r in arena.ladder()},
                 records=[], enemies=[], wins=0, fights=0, teams=[[], [], []])
        for k, n in OPEN.items():
            state['items'][k] = int(state['items'].get(k, 0)) + n
    return a


def rank_of(a):
    return 1 + sum(1 for s in a['rivals'].values() if s > a['score'])


def rank_award(rank):
    rows = DATA['arena_rank_award_3v3']
    for r in rows:
        f = str(r['rank_front'])
        lo, hi = (int(f), int(f)) if '-' not in f else map(int, f.split('-'))
        if lo <= rank <= hi:
            return r
    return rows[-1]


def teams_of(rival, level):
    """Three lineups: the rival's robot and the two robots 5 and 10 places further in arena_robot."""
    robots = arena.ROBOTS
    i = next(k for k, r in enumerate(robots) if r['id'] == rival['robot'])
    out = []
    for step in (0, 5, 10):
        r = robots[(i + step) % len(robots)]
        out.append(arena.lineup({**rival, 'robot': r['id']}, level))
    return out


def enemies(a, level):
    near = sorted(arena.ladder(), key=lambda r: abs(a['rivals'][str(r['id'])] - a['score']))[:4]
    out = []
    for r in sorted(near, key=lambda r: -a['rivals'][str(r['id'])]):
        teams = teams_of(r, level)
        out.append({'id': r['id'], 'name': r['name'], 'score': a['rivals'][str(r['id'])], 'avatar': r['avatar'],
                    'lv': max(u['lv'] for t in teams for u in t), 'power': sum(arena.power(t) for t in teams), 'teams': teams})
    return out


def check_teams(teams, owned):
    """Arena3v3BattleFormationWindow: 3 teams, 1-6 Girls each, positions 1-6, a Girl in one team only."""
    if not isinstance(teams, list) or len(teams) != 3:
        raise Arena3v3Error('Hacen falta 3 equipos')
    seen = set(); clean = []
    for t in teams:
        if not isinstance(t, list) or not 1 <= len(t) <= 6:
            raise Arena3v3Error('Cada equipo necesita entre 1 y 6 chicas')
        row = []; spots = set()
        for x in t:
            pid, pos = int(x.get('partner_id', 0)), int(x.get('pos', 0))
            if pid not in owned or pid in seen or not 1 <= pos <= 6 or pos in spots:
                raise Arena3v3Error('Equipo inválido')
            seen.add(pid); spots.add(pos); row.append({'partner_id': pid, 'pos': pos})
        clean.append(row)
    return clean


def roll(level, rng):
    cards = []
    for r in DATA['arena_battle_award_3v3']:
        if not int(r['level_begin']) <= level <= int(r['level_end']):
            continue
        opts = BOX.get(int(r['dropbox_id']), [])
        total = sum(int(o['weight']) for o in opts); x = rng(total) if total else 0
        for o in opts:
            x -= int(o['weight'])
            if x < 0:
                k, n = str(o['item']).split('#')[:2]; cards.append({k: int(n)}); break
    return cards


def board_row(r, a, level):
    """Arena3v3 rank row: like Junior Varsity with the three teams (Arena3v3FormationWindow shows them)."""
    teams = teams_of(r, level)
    return {'id': r['id'], 'name': r['name'], 'score': a['rivals'][str(r['id'])], 'lv': max(u['lv'] for t in teams for u in t),
            'avatar': r['avatar'], 'power': sum(arena.power(t) for t in teams), 'teams': teams}


def snapshot(state, level, now=None):
    now = int(time.time()) if now is None else now
    if 'arena3v3' not in state:
        return {'opened': False, 'score': INIT, 'rank': 0, 'tickets': int(state['items'].get(TICKET, 0)), 'cost': COST}
    a = state['arena3v3']; rank = rank_of(a)
    board = sorted([board_row(r, a, level) for r in arena.ladder()] +
                   [{'name': state.get('name') or 'Tú', 'score': a['score'], 'lv': level, 'me': True}], key=lambda x: -x['score'])[:20]
    return {'opened': True, 'score': a['score'], 'best': a['best'], 'rank': rank, 'tickets': int(state['items'].get(TICKET, 0)),
            'cost': COST, 'teams': a['teams'], 'enemies': [{k: v for k, v in e.items() if k != 'teams'} | {'sizes': [len(t) for t in e['teams']]} for e in a['enemies']],
            'records': a['records'][:10], 'board': board, 'season_award': rank_award(rank)['season_awards'],
            'season_end': a['season_start'] + SEASON, 'wins': a['wins'], 'fights': a['fights'],
            'help': DATA['text'].get('ARENA_3V3_HELP', '')}


def action(state, request, level, owned=(), now=None, rng=secrets.randbelow, fight=None):
    """fight(k, lineup) -> (win, report_index) runs battle k (0-2) of the player's team k against lineup."""
    now = int(time.time()) if now is None else now
    a = saved(state, now); items = state['items']; kind = request.get('action'); result = {}
    if now >= a['season_start'] + SEASON:
        got = arena.pairs(rank_award(rank_of(a))['season_awards'])
        for k, n in got.items():
            items[k] = int(items.get(k, 0)) + n
        a.update(score=INIT, season_start=now, rivals={str(r['id']): r['score'] for r in arena.ladder()}, enemies=[])
        result['season_got'] = got
    if kind in ('open', 'refresh'):
        a['enemies'] = enemies(a, level)
    elif kind == 'teams':
        a['teams'] = check_teams(request.get('teams'), set(owned))
    elif kind == 'fight':
        enemy = next((e for e in a['enemies'] if e['id'] == int(request.get('id', 0))), None)
        if not enemy:
            raise Arena3v3Error('Rival no disponible: actualiza la lista')
        teams = check_teams(request.get('teams') or a['teams'], set(owned))
        a['teams'] = teams
        if int(items.get(TICKET, 0)) < COST:
            raise Arena3v3Error(f'Hacen falta {COST} Arena Tickets')
        items[TICKET] = int(items[TICKET]) - COST
        rounds = []
        for k in range(3):
            win, rep = fight(k, enemy['teams'][k]) if fight else (True, None)
            rounds.append({'win': bool(win), 'report': rep})
            if sum(r['win'] for r in rounds) == 2 or sum(not r['win'] for r in rounds) == 2:
                break
        won = sum(r['win'] for r in rounds) >= 2
        k_, e_ = arena.coefficient(a['score']), arena.expected(a['score'], enemy['score'])
        delta = max(1, round(k_ * (1 - e_))) if won else -max(1, round(k_ * e_))
        if len(rounds) == 2: delta = round(delta * 1.25)  # 2-0
        a['score'] = max(0, a['score'] + delta); a['best'] = max(a['best'], a['score'])
        rid = str(enemy['id']); a['rivals'][rid] = max(0, a['rivals'][rid] - (delta if won else delta // 2))
        a['wins'] += 1 if won else 0; a['fights'] += 1
        cards = roll(level, rng); pick = rng(len(cards)) if cards else 0; got = cards[pick] if cards else {}
        for kk, n in got.items():
            items[kk] = int(items.get(kk, 0)) + n
        a['records'].insert(0, {'at': now, 'name': enemy['name'], 'win': won, 'delta': delta, 'rounds': [r['win'] for r in rounds]})
        a['records'] = a['records'][:10]
        a['enemies'] = enemies(a, level)
        result.update(win=won, delta=delta, rounds=rounds, cards=cards, pick=pick, got=got)
    else:
        raise Arena3v3Error('Acción de Arena 3v3 no disponible')
    return result
