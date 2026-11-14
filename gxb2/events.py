"""Offline Events hub (ActivityWindow). Rules follow CheckIn.lua and ActivitySevenDay.lua.

The original server tracked `online_days` (days the player logged in) and `count`
(days already claimed). Locally a day counts when the Events hub is opened or an
event action runs on that local calendar day.
"""
from __future__ import annotations
import json, time
from . import clock, world_live_config
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
    server_id = str(state.get('server_id') or 'S1').upper()
    checkin_enabled = world_live_config.event_enabled(server_id, 'checkin')
    sevenday_enabled = world_live_config.event_enabled(server_id, 'sevenday')
    days = list(ev.get('days', []))
    online = len(days) + (0 if today(now) in days else 1)   # today counts once the hub is opened
    got = int(ev.get('checkin', {}).get('count', 0))
    start = got // ROUND * ROUND + 1                     # CheckIn:initData
    grid = []
    for i in range(ROUND):
        real = start + i
        row = LOGIN[login_show_id(real)]
        grid.append({'day': real, 'pos': i + 1, 'award': row['award'], 'double': row['double'],
                     'got': real <= got, 'can': checkin_enabled and got < real <= online})
    seven_got = int(ev.get('sevenday', {}).get('count', 0))
    seven = [{'day': d, 'award': r['award'], 'got': d <= seven_got, 'can': sevenday_enabled and seven_got < d <= min(online, 7)}
             for d, r in sorted(SEVENDAY.items())]
    return {'online_days': online, 'checkin': {'count': got, 'grid': grid, 'enabled': checkin_enabled},
            'sevenday': {'count': seven_got, 'days': seven, 'done': seven_got >= len(SEVENDAY), 'enabled': sevenday_enabled}}


def action(state, request, now=None):
    if not isinstance(request, dict):
        raise ValueError('Datos inválidos')
    ev = touch(state, now)
    server_id = str(state.get('server_id') or 'S1').upper()
    online = len(ev['days'])
    kind = request.get('action')
    awards = {}
    if kind == 'visit':
        pass
    elif kind == 'checkin':
        if not world_live_config.event_enabled(server_id, 'checkin'):
            raise ValueError('Điểm danh đang tạm đóng trên server này')
        got = ev['checkin']['count']
        if got >= online:
            raise ValueError('Ya has firmado hoy. Vuelve mañana.')
        # CheckIn:getAwards claims every claimable day in the visible block.
        end = min(online, got // ROUND * ROUND + ROUND)
        for day in range(got + 1, end + 1):
            for k, n in pairs(LOGIN[login_show_id(day)]['award']).items():
                awards[k] = awards.get(k, 0) + world_live_config.event_reward(n, server_id)
        ev['checkin']['count'] = end
    elif kind == 'sevenday':
        if not world_live_config.event_enabled(server_id, 'sevenday'):
            raise ValueError('Quà 7 ngày đang tạm đóng trên server này')
        got = ev['sevenday']['count']
        if got >= len(SEVENDAY) or got >= online:
            raise ValueError('No hay recompensa disponible hoy')
        awards = {k: world_live_config.event_reward(n, server_id) for k, n in pairs(SEVENDAY[got + 1]['award']).items()}
        ev['sevenday']['count'] = got + 1
    else:
        raise ValueError('Acción de evento no disponible')
    for k, n in awards.items():
        state['items'][k] = int(state['items'].get(k, 0)) + n
    return {'awards': awards}
