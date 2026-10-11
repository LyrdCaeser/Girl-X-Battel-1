"""Offline Events hub (ActivityWindow). Rules follow CheckIn.lua and ActivitySevenDay.lua.

The original server tracked `online_days` (days the player logged in) and `count`
(days already claimed). Locally a day counts when the Events hub is opened or an
event action runs on that local calendar day.
"""
from __future__ import annotations
import json, time
from . import clock
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/events.json').read_text())
LOGIN = {r['id']: r for r in DATA['login']}
LOGIN_MAX = max(LOGIN)                      # xyd.getCheckTableLimit.LIMIT (390)
LOOP_EXCLUDE = DATA['login_loop_exclude']   # misc.login_loop_exclude (30)
SEVENDAY = {r['day']: r for r in DATA['sevenday']}
ROUND = 15                                  # CheckIn.roundCount


def today(now=None):
    return clock.day(now, local=True)


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[k] = out.get(k, 0) + int(n)
    return out


def login_show_id(day):
    """CheckInPopUpItem:ctor — days past the table loop, skipping the first 30."""
    if day <= LOGIN_MAX:
        return day
    loop = LOGIN_MAX - LOOP_EXCLUDE
    day -= LOGIN_MAX
    return LOGIN_MAX if day % loop == 0 else day % loop + LOOP_EXCLUDE


def saved(state):
    ev = state.setdefault('events', {})
    ev.setdefault('days', [])
    ev.setdefault('checkin', {'count': 0})
    ev.setdefault('sevenday', {'count': 0})
    return ev


def touch(state, now=None):
    ev = saved(state)
    day = today(now)
    if not ev['days'] or day > ev['days'][-1]:   # a rewound clock must not add earlier days
        ev['days'].append(day)
    return ev


def snapshot(state, now=None):
    ev = state.get('events') or {}
    days = list(ev.get('days', []))
    online = len(days) + (0 if today(now) in days else 1)   # today counts once the hub is opened
    got = int(ev.get('checkin', {}).get('count', 0))
    start = got // ROUND * ROUND + 1                     # CheckIn:initData
    grid = []
    for i in range(ROUND):
        real = start + i
        row = LOGIN[login_show_id(real)]
        grid.append({'day': real, 'pos': i + 1, 'award': row['award'], 'double': row['double'],
                     'got': real <= got, 'can': got < real <= online})
    seven_got = int(ev.get('sevenday', {}).get('count', 0))
    seven = [{'day': d, 'award': r['award'], 'got': d <= seven_got, 'can': seven_got < d <= min(online, 7)}
             for d, r in sorted(SEVENDAY.items())]
    return {'online_days': online, 'checkin': {'count': got, 'grid': grid},
            'sevenday': {'count': seven_got, 'days': seven, 'done': seven_got >= len(SEVENDAY)}}


def action(state, request, now=None):
    if not isinstance(request, dict):
        raise ValueError('Datos inválidos')
    ev = touch(state, now)
    online = len(ev['days'])
    kind = request.get('action')
    awards = {}
    if kind == 'visit':
        pass
    elif kind == 'checkin':
        got = ev['checkin']['count']
        if got >= online:
            raise ValueError('Ya has firmado hoy. Vuelve mañana.')
        # CheckIn:getAwards claims every claimable day in the visible block.
        end = min(online, got // ROUND * ROUND + ROUND)
        for day in range(got + 1, end + 1):
            for k, n in pairs(LOGIN[login_show_id(day)]['award']).items():
                awards[k] = awards.get(k, 0) + n
        ev['checkin']['count'] = end
    elif kind == 'sevenday':
        got = ev['sevenday']['count']
        if got >= len(SEVENDAY) or got >= online:
            raise ValueError('No hay recompensa disponible hoy')
        awards = pairs(SEVENDAY[got + 1]['award'])
        ev['sevenday']['count'] = got + 1
    else:
        raise ValueError('Acción de evento no disponible')
    for k, n in awards.items():
        state['items'][k] = int(state['items'].get(k, 0)) + n
    return {'awards': awards}
