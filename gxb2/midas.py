"""Alchemy / Midas v2 (models/Midas.lua, MidasWindow) offline.

From the client: every day 1 free claim of midas.gold_new[player level] × (1 + vip.extra_midas); then up to
vip.midas_buy_times purchases (5 at VIP 0), the n-th costing midas_buy_coin[n].cost and giving base × multiple.
The day follows midas_time_interval (86400); LOCAL: it resets at 00:00 UTC (the server day) and VIP stays 0.
"""
from __future__ import annotations
import json, time
from . import clock
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/midas.json').read_text())


def pairs(text):
    k, n = str(text).split('#')[:2]
    return k, int(float(n))


def day(now):
    return clock.day(now)


def vip(state):
    return DATA['vip'].get(str(int(state.get('vip', 0))), DATA['vip']['0'])


def base(state, level):
    row = DATA['gold'].get(str(level)) or DATA['gold'][str(max(int(k) for k in DATA['gold']))]
    return round(pairs(row)[1] * (1 + vip(state)['extra']))


def saved(state, now):
    m = state.setdefault('midas', {'day': '', 'free': 0, 'buys': 0})
    if m['day'] != day(now):
        m.update(day=day(now), free=0, buys=0)
    return m


def snapshot(state, level, now=None):
    now = int(time.time()) if now is None else now
    m = dict(state.get('midas') or {})
    if m.get('day') != day(now):
        m = {'day': day(now), 'free': 0, 'buys': 0}
    b = base(state, level)
    times = vip(state)['times']
    nxt = DATA['buy'][m['buys']] if m['buys'] < min(times, len(DATA['buy'])) else None
    return {'base': b, 'free_ready': not m['free'], 'buys': m['buys'], 'times': times,
            'next_cost': dict([pairs(nxt['cost'])]) if nxt else None, 'next_gold': round(b * float(nxt['multiple'])) if nxt else 0,
            'reset': (now // 86400 + 1) * 86400}


def action(state, request, level, now=None):
    now = int(time.time()) if now is None else now
    m = saved(state, now)
    items = state['items']
    b = base(state, level)
    if request.get('action') == 'free':
        if m['free']:
            raise ValueError('Ya has recogido el oro gratis de hoy')
        m['free'] = 1
        gold = b
    elif request.get('action') == 'buy':
        times = vip(state)['times']
        if m['buys'] >= min(times, len(DATA['buy'])):
            raise ValueError('No quedan compras de oro hoy')
        row = DATA['buy'][m['buys']]
        k, n = pairs(row['cost'])
        if int(items.get(k, 0)) < n:
            raise ValueError('Faltan gemas')
        items[k] = int(items[k]) - n
        m['buys'] += 1
        gold = round(b * float(row['multiple']))
    else:
        raise ValueError('Acción de alquimia no disponible')
    items['1'] = int(items.get('1', 0)) + gold
    return {'got': {'1': gold}}
