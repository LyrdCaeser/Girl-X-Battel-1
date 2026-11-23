"""Alchemy / Midas v2 (models/Midas.lua, MidasWindow) offline.

The recovered native table contains both gold and gold_new (the latter is
3x higher). GXB3 uses its native gold column as the safer award baseline,
with diminishing VIP bonus and bounded escalating purchases to prevent a
single click of Game Assistant from creating billions of Gold. Keep the
original VIP daily purchase counts and diamond costs.
Daily reset follows the configured game day.
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
    # Native midas.gold is 1/3 of gold_new (verified for all 400 rows).
    # VIP keeps a real, increasing bonus without the former 5x payout.
    native = DATA['gold_native']
    index = max(1, min(int(level), max(int(k) for k in native)))
    gold = pairs(native[str(index)])[1]
    extra = max(0.0, float(vip(state)['extra']))
    return round(gold * (1 + extra / (1 + extra)))


def purchase_gold(base_gold, row):
    # Legacy purchase multiples 5..180 were applied directly, resulting
    # in 8,382,150,000 Gold for 16 buys at player lv400 / VIP15.
    # Preserve their ascending order but compress bonus to +5..180%.
    return round(base_gold * (1 + max(0.0, float(row['multiple'])) / 100))


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
            'next_cost': dict([pairs(nxt['cost'])]) if nxt else None, 'next_gold': purchase_gold(b, nxt) if nxt else 0,
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
        gold = purchase_gold(b, row)
    else:
        raise ValueError('Acción de alquimia no disponible')
    items['1'] = int(items.get('1', 0)) + gold
    return {'got': {'1': gold}}
