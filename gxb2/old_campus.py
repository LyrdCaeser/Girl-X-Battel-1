"""Old Campus Exploration (models/OldSchool.lua, OldSchoolMainWindow, ActivityExploreCampusFightWindow, OLD_SCHOOL_HELP1).

Recovered from the client:
- Seasons of 13 battle days + 1 result day from old_building_start_time (old_building_time_interval); the levels
  alternate between old_building_a and old_building_b each season. Unlock: function 39 (campaign stage ≥ 132).
- 10 levels of 2-3 stages. Level 1 is open; clearing any stage of a level opens the next one.
- A team (1-6 Girls) is set for every stage of a level; a Girl can only be in one team of the level.
- Exploration Plans (old_building_buff_new, the server-provided variant in use at the end) are offered in 4 categories
  (Primary / Standard / Advanced / Ultimate Plan, ActivityExploreCampusFightWindow) whose sizes per point value are
  old_building_buff_lock_1..4 (cumulative), unlocked at Total Score old_building_buff_num and, for Ultimate, from level
  old_building_buff_num_2 (9). They make the enemies stronger (skills as god_skills) and add their points:
  stage score = base point (10) + chosen plan points. Plans of the same group exclude each other.
- Current Stage Score keeps the best win with the same team and resets when that team changes; the Best Level Score
  (sum of the current stage scores) is never lowered; Total Score = sum of the 10 Best Level Scores.
- Level Reward (old_building_{a,b}.awards, one part per stage passed without changing the lineup) and Score Rewards
  (old_building_{a,b}_award1) are claimed manually.

LOCAL decisions (DESIGN_DECISIONS.md LOCAL-035):
- Level 11 (damage ranking between players), the score/damage rankings, frames and the season shop are not rebuilt.
- Odd seasons use table A and even seasons table B.
- Which plans fill each category was chosen by the server every season: here they are drawn from buff_new by point
  value with a generator seeded by the season number (same plans for the whole season).
"""
from __future__ import annotations
import json, time
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/old_campus.json').read_text())
BATTLE, DISPLAY = (int(x) for x in str(DATA['misc']['old_building_time_interval']).split('|'))
START = int(DATA['misc']['old_building_start_time'])
PLANS = {int(p['id']): p for p in DATA['plans']}
STAGES = {int(k): v for k, v in DATA['stages'].items()}
UNLOCK_STAGE = int(DATA['unlock']['open_value'])
LEVELS = 10
CATS = ['Primary Plan', 'Standard Plan', 'Advanced Plan', 'Ultimate Plan']
M = DATA['misc']


def season_plans(n):
    """{plan_id: category 0-3} for season n: cumulative counts per point value from old_building_buff_lock_1..4."""
    import random
    rnd = random.Random(7919 * n)
    locks = [[int(x) for x in str(M[f'old_building_buff_lock_{k}']).split('|')] for k in range(1, 5)]
    out = {}
    for point in range(1, 6):
        pool = sorted(int(p['id']) for p in DATA['plans'] if int(p['point']) == point)
        rnd.shuffle(pool)
        prev = 0
        for cat, lock in enumerate(locks):
            upto = min(lock[point - 1], len(pool))
            for pid in pool[prev:upto]:
                out[pid] = cat
            prev = max(prev, upto)
    return out


def cat_open(cat, total_score, level):
    need = [int(x) for x in str(M['old_building_buff_num']).split('|')]
    floor = [int(x) for x in str(M['old_building_buff_num_2']).split('|')]
    return total_score >= need[cat] and level >= floor[cat]


def ids(text):
    return [int(x) for x in str(text or '').split('|') if x]


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[k] = out.get(k, 0) + int(n)
    return out


def season_of(now):
    n = max(0, (now - START) // (BATTLE + DISPLAY)) + 1
    start = START + (n - 1) * (BATTLE + DISPLAY)
    return n, start, start + BATTLE, start + BATTLE + DISPLAY


def table(n):
    return 'a' if n % 2 == 1 else 'b'


def level_rows(n):
    return [r for r in DATA['levels'][table(n)] if int(r['type']) == 1][:LEVELS]


def fresh(n):
    return {'season': n, 'levels': {str(i + 1): {'teams': [], 'plans': [], 'cur': [], 'done': [], 'best': 0, 'claimed': 0}
                                    for i in range(LEVELS)}, 'score_claimed': []}


def saved(state, now):
    n = season_of(now)[0]
    oc = state.get('old_campus')
    if not oc or oc.get('season') != n:
        oc = state['old_campus'] = fresh(n)
    return oc


def stage_ids(n, level):
    return ids(level_rows(n)[level - 1]['stage'])


def total(oc):
    return sum(int(l['best']) for l in oc['levels'].values())


def unlocked(oc, level):
    return level == 1 or any(oc['levels'][str(level - 1)]['done'] or [False])


def pad(lst, n, value):
    return (list(lst) + [value] * n)[:n]


def snapshot(state, now=None):
    import copy
    from .engine import TABLES
    now = int(time.time()) if now is None else now
    view = copy.deepcopy(state)
    oc = saved(view, now)
    n, start, battle_end, end = season_of(now)
    levels = []
    for i, row in enumerate(level_rows(n)):
        lv = oc['levels'][str(i + 1)]
        sids = ids(row['stage'])
        k = len(sids)
        stages = []
        for j, sid in enumerate(sids):
            st = STAGES[sid]
            link = int(st['partner_id'] or 0)
            b = TABLES['battle'].get(str(st['battle_id']), {})
            foes = [{'table_id': int(TABLES['monster'].get(t, {}).get('partner_link') or 0), 'lv': int(TABLES['monster'].get(t, {}).get('lv_show') or TABLES['monster'].get(t, {}).get('lv') or 1)}
                    for t in str(b.get('monsters', '')).split('|') if t]
            stages.append({'id': sid, 'base': int(st['point']), 'boss': link, 'boss_name': TABLES['names'].get(str(link), ''), 'enemies': foes,
                           'team': pad(lv['teams'], k, [])[j], 'plans': pad(lv['plans'], k, [])[j], 'cur': pad(lv['cur'], k, 0)[j],
                           'done': pad(lv['done'], k, False)[j]})
        parts = [pairs(x) for x in str(row['awards']).split('@') if x]
        levels.append({'level': i + 1, 'open': unlocked(oc, i + 1), 'best': int(lv['best']), 'stages': stages,
                       'rewards': parts, 'claimed': int(lv['claimed']), 'claimable': min(sum(pad(lv['done'], k, False)), len(parts)) - int(lv['claimed'])})
    return {'unlocked': int(state.get('max_stage', 0)) >= UNLOCK_STAGE, 'unlock_stage': UNLOCK_STAGE, 'season': n, 'table': table(n),
            'open': start <= now < battle_end, 'battle_end': battle_end, 'season_end': end, 'total': total(oc), 'levels': levels,
            'score_awards': [{'id': int(r['id']), 'point': int(r['point']), 'awards': pairs(r['awards']), 'claimed': int(r['id']) in oc['score_claimed']}
                             for r in DATA['score_awards'][table(n)]],
            'cats': [{'name': c, 'need': int(str(M['old_building_buff_num']).split('|')[i]), 'floor': int(str(M['old_building_buff_num_2']).split('|')[i])} for i, c in enumerate(CATS)],
            'plans': [{'id': pid, 'cat': cat, 'point': int(PLANS[pid]['point']), 'group': int(PLANS[pid]['group'] or 0), 'icon': PLANS[pid]['icon'],
                       **DATA['plan_text'].get(str(pid), {})} for pid, cat in sorted(season_plans(n).items(), key=lambda x: (x[1], int(PLANS[x[0]]['point']), x[0]))]}


def action(state, request, now=None, fight=None):
    """fight(team, battle_id, god_skills) -> report."""
    now = int(time.time()) if now is None else now
    if int(state.get('max_stage', 0)) < UNLOCK_STAGE:
        raise ValueError(f'Old Campus se desbloquea al superar la fase {UNLOCK_STAGE} de la campaña')
    oc = saved(state, now)
    n, start, battle_end, _ = season_of(now)
    items = state['items']
    kind = request.get('action')
    result = {}
    if kind == 'open':
        return result
    if kind == 'claim_score':
        rid = int(request.get('id', 0))
        row = next((r for r in DATA['score_awards'][table(n)] if int(r['id']) == rid), None)
        if not row or rid in oc['score_claimed'] or total(oc) < int(row['point']):
            raise ValueError('Premio de puntuación no disponible')
        oc['score_claimed'].append(rid)
        got = pairs(row['awards'])
        for k, v in got.items():
            items[k] = int(items.get(k, 0)) + v
        return {'got': got}
    level = int(request.get('level', 0))
    if not 1 <= level <= LEVELS:
        raise ValueError('Nivel no válido')
    lv = oc['levels'][str(level)]
    sids = stage_ids(n, level)
    k = len(sids)
    if kind == 'claim_level':
        parts = [pairs(x) for x in str(level_rows(n)[level - 1]['awards']).split('@') if x]
        if int(lv['claimed']) >= min(sum(pad(lv['done'], k, False)), len(parts)):
            raise ValueError('No hay premio de nivel por reclamar')
        got = parts[int(lv['claimed'])]
        lv['claimed'] = int(lv['claimed']) + 1
        for key, v in got.items():
            items[key] = int(items.get(key, 0)) + v
        return {'got': got}
    if not start <= now < battle_end:
        raise ValueError('La temporada está en fase de resultados')
    if not unlocked(oc, level):
        raise ValueError('Supera una fase del nivel anterior para abrir este')
    if kind == 'teams':
        owned = {p['partner_id'] for p in state['partners']}
        teams = request.get('teams') or []
        if len(teams) != k:
            raise ValueError(f'Este nivel tiene {k} fases: pon un equipo en cada una')
        seen = set()
        clean = []
        for t in teams:
            if not 1 <= len(t) <= 6:
                raise ValueError('Cada equipo necesita entre 1 y 6 chicas')
            row = []
            for m in t:
                pid, pos = int(m['partner_id']), int(m['pos'])
                if pid not in owned or pid in seen or not 1 <= pos <= 6:
                    raise ValueError('Una chica solo puede estar en un equipo del nivel')
                seen.add(pid); row.append({'partner_id': pid, 'pos': pos})
            clean.append(sorted(row, key=lambda x: x['pos']))
        old = pad(lv['teams'], k, [])
        cur, done = pad(lv['cur'], k, 0), pad(lv['done'], k, False)
        for j in range(k):
            if clean[j] != old[j]:
                cur[j], done[j] = 0, False  # a new lineup resets the Current Stage Score
        lv.update(teams=clean, cur=cur, done=done)
        return result
    idx = int(request.get('index', -1))
    if not 0 <= idx < k:
        raise ValueError('Fase no válida')
    if kind == 'plans':
        chosen = sorted({int(x) for x in request.get('plans') or []})
        offer = season_plans(n)
        if any(p not in offer or not cat_open(offer[p], total(oc), level) for p in chosen):
            raise ValueError('Ese plan no está disponible (bloqueado o no es de esta temporada)')
        groups = [int(PLANS[p]['group'] or 0) for p in chosen]
        g = [x for x in groups if x]
        if len(g) != len(set(g)):
            raise ValueError('Dos planes del mismo grupo no se pueden combinar')
        plans = pad(lv['plans'], k, [])
        plans[idx] = chosen
        lv['plans'] = plans
        return result
    if kind == 'fight':
        team = pad(lv['teams'], k, [])[idx]
        if not team:
            raise ValueError('Primero pon el equipo de esta fase (Set Team)')
        plans = pad(lv['plans'], k, [])[idx]
        gods = [s for p in plans for s in ids(PLANS[p]['skill'])]
        st = STAGES[sids[idx]]
        report = fight(team, int(st['battle_id']), gods)
        win = bool(report['isWin'])
        result.update(win=win, battle=report)
        if win:
            score = int(st['point']) + sum(int(PLANS[p]['point']) for p in plans)
            cur, done = pad(lv['cur'], k, 0), pad(lv['done'], k, False)
            cur[idx] = max(int(cur[idx]), score); done[idx] = True
            lv.update(cur=cur, done=done, best=max(int(lv['best']), sum(cur)))
            result.update(score=score, level_score=sum(cur), best=lv['best'], total=total(oc))
        return result
    raise ValueError('Acción de Old Campus no disponible')
