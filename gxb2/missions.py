"""Daily Tasks (DailyMissionWindow.lua / daily_mission) and Trophies (AchievementWindow.lua / achievement,
achievement_type, achievement_text).

Daily tasks count local actions per day and reset at local midnight (the original reset came from the server).
Task 11 "Complete all Daily Tasks" (complete_value 10) counts the tasks claimed that day. Tasks whose systems do not
exist offline yet (Hearts 10; Internship 3 and Alchemy 1 count since WAVE-011) stay visible and cannot progress — LOCAL-025.
The per-level `coefficient` column is not used by the client and its server formula is unknown: base awards only.

Trophies are measured from the save itself (level, girls by stars, intimacy, campaign, Tests, Excursion levels,
Enroll count); chains follow achievement.next_achieve_id and each step is claimed in order.
"""
from __future__ import annotations
import json, sqlite3, time
from . import clock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/missions.json').read_text())
DAILY = {int(r['id']): r for r in DATA['daily']}
ACH = {int(r['id']): r for r in DATA['achievements']}
TYPES = {int(r['id']): r for r in DATA['types']}
COUNTER = {1: 'midas', 2: 'gamble', 3: 'tavern', 4: 'forge', 5: 'regular', 6: 'advanced', 7: 'arena', 8: 'idle', 9: 'quiz', 10: 'hearts'}


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[k] = out.get(k, 0) + int(n)
    return out


def day(now):
    return clock.day(now)


def saved(state, now):
    m = state.setdefault('missions', {})
    new_day = m.get('day', '') < day(now)   # ISO dates: a rewound clock is not a new day
    if new_day:
        m.update(day=day(now), counts={}, claimed=[])
    m.setdefault('totals', {}); m.setdefault('ach', {})
    if new_day: m['totals']['login'] = int(m['totals'].get('login', 0)) + 1  # days played (Magic Card "Log in 5 Days")
    return m


def record(state, key, count=1, now=None):
    now = int(time.time()) if now is None else now
    m = saved(state, now)
    m['counts'][key] = int(m['counts'].get(key, 0)) + count
    m['totals'][key] = int(m['totals'].get(key, 0)) + count


def metric(state, tid, level):
    stars = [int(p.get('stars', 0)) for p in state.get('roster', [])] if state.get('roster') else []
    travel = (state.get('home_systems') or {}).get('travel') or {}
    blds = travel.get('buildings') or {}
    totals = (state.get('missions') or {}).get('totals', {})
    if tid == 1: return level
    if tid in (3, 4, 5, 6, 22): return sum(1 for s in stars if s >= {3: 4, 4: 5, 5: 6, 6: 9, 22: 10}[tid])
    if tid == 24: return max([int(p.get('love_point', 0)) for p in state['partners']] or [0])
    if tid == 25: return int(state.get('max_chapter', 0))
    if tid == 27: return int(state.get('max_stage', 0))
    if tid == 36: return int((state.get('tower') or {}).get('max_stage', 0))
    if tid == 19: return int(totals.get('enroll', 0))
    if tid == 39: return min([int(v) for v in (travel.get('training') or {}).values()] or [0])
    if tid in (40, 41, 42): return int((blds.get({40: '1', 41: '2', 42: '3'}[tid]) or {}).get('lv', 0))
    if tid == 43: return int((travel.get('explore') or {}).get('lv', 1))
    return None


def snapshot(state, level, roster, now=None):
    now = int(time.time()) if now is None else now
    m = (state.get('missions') or {})
    today = m.get('day') == day(now)
    counts = m.get('counts', {}) if today else {}
    claimed = set(m.get('claimed', [])) if today else set()
    daily = []
    for i, r in sorted(DAILY.items(), key=lambda kv: int(kv[1]['rank']) if int(kv[1]['rank']) > 0 else 99):
        need = int(r['complete_value'])
        have = len([c for c in claimed if c != 11]) if i == 11 else int(counts.get(COUNTER.get(i, ''), 0))
        daily.append({'id': i, 'text': r['text'], 'need': need, 'have': min(need, have), 'award': r['award'], 'lv': int(r['lv_limit'] or 0),
                      'claimed': i in claimed, 'tracked': True,  # Hearts count since gxb2/hearts.py
                      'window': r['go_window']})
    probe = {**state, 'roster': roster}
    trophies = []
    done = (m.get('ach') or {})
    for tid, t in sorted(TYPES.items()):
        value = metric(probe, tid, level)
        step = int(done.get(str(tid), t['start']))
        if step == -1:
            row = ACH[int(t['end'])]; trophies.append({'type': tid, 'text': t['text'], 'id': int(t['end']), 'need': row['complete_value'], 'have': value, 'award': row['award'], 'done': True, 'tracked': value is not None}); continue
        row = ACH[step]
        need = row['complete_value']
        ok = value is not None and need.lstrip('-').isdigit() and value >= int(need)
        trophies.append({'type': tid, 'text': t['text'], 'id': step, 'need': need, 'have': value, 'award': row['award'], 'can': ok, 'done': False, 'tracked': value is not None})
    return {'daily': daily, 'trophies': trophies}


def action(state, request, level, roster, now=None):
    now = int(time.time()) if now is None else now
    m = saved(state, now)
    snap = snapshot(state, level, roster, now)
    kind = request.get('action')
    got = {}
    if kind == 'daily':
        mid = int(request.get('id', 0))
        task = next((t for t in snap['daily'] if t['id'] == mid), None)
        if not task or task['claimed'] or task['have'] < task['need'] or level < task['lv']:
            raise ValueError('Tarea sin completar')
        got = pairs(task['award']); m['claimed'].append(mid)
    elif kind == 'trophy':
        tid = int(request.get('type', 0))
        t = next((x for x in snap['trophies'] if x['type'] == tid), None)
        if not t or t['done'] or not t.get('can'):
            raise ValueError('Trofeo sin completar')
        got = pairs(t['award'])
        nxt = int(ACH[t['id']]['next'] or 0)
        m['ach'][str(tid)] = nxt if nxt and nxt in ACH and nxt <= int(TYPES[tid]['end']) else -1
    else:
        raise ValueError('Acción de misiones no disponible')
    # Provisional "popularity" (stand-in for VIP EXP until LOCAL-050): 10 per daily task, 25 per trophy.
    m['totals']['popularity'] = int(m['totals'].get('popularity', 0)) + (10 if kind == 'daily' else 25)
    for k, n in got.items():
        state['items'][k] = int(state['items'].get(k, 0)) + n
    return {'got': got}
