"""Land of Souls (models/SoulLand.lua, SoulLandMainWindow / SoulLandFightWindow / SoulLandShopWindow): the Anima Gear mode.

Three forts of 50 stages (soul_land): each fight costs one Soul Challenge Ticket (item 421: 10 at the start, +10 a day,
at most 100) and runs the original engine with the stage god skill (BattleType SOUL_LAND = 71). A win clears the stage,
gives its first-clear `awards` and one drop of its dropbox (Anima Stones). The idle reward (soul_land_award) gives Soul
Branches per hour depending on the stages cleared, up to 24 h (soul_land_award_time_max); Soul Branches buy in the Store
(soul_land_shop, limits per 28-day cycle). The Anima Stone Ritual and boxes live in gxb2/souls.py.
Local rule (LOCAL-046): progress is kept between cycles (the original resets the map every 28 days)."""
from __future__ import annotations
import json, random
from pathlib import Path
from . import souls

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/souls.json').read_text())
LAND, AWARD, SHOP, MISC = D['land'], D['land_award'], D['land_shop'], D['misc']
DROP = json.loads((ROOT / 'data/dropbox.json').read_text())
BATTLE_TYPE = 71
TICKET = '421'
INIT, MAX_T, DAILY = (int(MISC[k].split('#')[1]) for k in ('soul_land_ticket_init', 'soul_land_ticket_max', 'soul_land_ticket_daliy'))
HANG_MAX = int(MISC['soul_land_award_time_max'] or 86400)
OPEN_LV = int(MISC['soul_land_open_lvl'] or 200)
CYCLE = int(MISC['soul_land_cycle_time'] or 2419200)
START = int(MISC['soul_land_start_time'] or 0)


class LandError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def first_stage(fort):
    return min(int(k) for k, r in LAND.items() if int(r['fort_id']) == fort)


def data(state, now):
    s = state.setdefault('soul_land', {})
    if 'day' not in s:
        s.update({'cleared': {}, 'hang_at': now, 'day': now // 86400, 'shop': {}, 'cycle': cycle(now)})
        state['items'][TICKET] = max(INIT, int(state['items'].get(TICKET, 0)))
    day = now // 86400
    if day > s['day']:
        have = int(state['items'].get(TICKET, 0))
        state['items'][TICKET] = max(have, min(MAX_T, have + DAILY * (day - s['day'])))
        s['day'] = day
    if cycle(now) != s.get('cycle'):
        s['cycle'] = cycle(now); s['shop'] = {}
    return s


def cycle(now):
    return max(0, (now - START) // CYCLE)


def cleared_count(s):
    return sum(int(v) - first_stage(int(f)) + 1 for f, v in s['cleared'].items() if v)


def hang_rate(s):
    n = cleared_count(s); row = None
    for r in sorted(AWARD.values(), key=lambda r: int(r['point'])):
        if n >= int(r['point']): row = r
    return pairs(row['awards']) if row else {}


def pending(s, now):
    hours = min(HANG_MAX, max(0, now - s['hang_at'])) // 3600
    return {k: v * hours for k, v in hang_rate(s).items()}, hours


def unlocked(state):
    return max((int(p['lv']) for p in state['partners']), default=0) >= OPEN_LV


def snapshot(state, now):
    if not unlocked(state): return {'open': False, 'open_lv': OPEN_LV}
    s = data(state, now); got, hours = pending(s, now)
    forts = []
    for f in (1, 2, 3):
        last = s['cleared'].get(str(f), 0); first = first_stage(f)
        forts.append({'fort': f, 'first': first, 'cleared': last, 'next': (int(LAND[str(last)]['next_id']) if last else first) if not last or LAND[str(last)].get('next_id') else 0,
                      'total': sum(1 for r in LAND.values() if int(r['fort_id']) == f)})
    return {'open': True, 'forts': forts, 'tickets': int(state['items'].get(TICKET, 0)), 'max_tickets': MAX_T, 'hang': got, 'hang_hours': hours,
            'hang_rate': hang_rate(s), 'shop': s['shop'], 'cycle_end': START + (s['cycle'] + 1) * CYCLE, 'cleared_total': cleared_count(s)}


def drop(state, box, rng):
    rows = [r for r in DROP.values() if int(r['dropbox_id']) == int(box) and int(r['weight']) > 0]
    if not rows: return {}
    total = sum(int(r['weight']) for r in rows); roll = rng.random() * total
    for r in rows:
        roll -= int(r['weight'])
        if roll < 0: return pairs(r['item'])
    return pairs(rows[-1]['item'])


def give(state, items, rng):
    out = {}
    for k, n in items.items():
        if k in souls.E1 or k in souls.E2:
            for _ in range(n): souls.new_soul(state, int(k), rng)
        else:
            state['items'][k] = int(state['items'].get(k, 0)) + n
        out[k] = out.get(k, 0) + n
    return out


def action(state, request, now, fight=None, rng=None):
    rng = rng or random.SystemRandom()
    if not unlocked(state): raise LandError(f'Land of Souls se abre con una chica de nivel {OPEN_LV}')
    s = data(state, now); act = request.get('action')
    if act == 'open':
        return {}
    if act == 'fight':
        stage = int(request.get('stage') or 0); row = LAND.get(str(stage))
        if not row: raise LandError('Fase inexistente')
        fort = str(row['fort_id']); last = s['cleared'].get(fort, 0)
        allowed = (int(LAND[str(last)]['next_id']) if last else first_stage(int(fort)))
        if stage > allowed: raise LandError('Supera primero la fase anterior')
        if int(state['items'].get(TICKET, 0)) < 1: raise LandError('Sin Soul Challenge Tickets')
        state['items'][TICKET] = int(state['items'][TICKET]) - 1
        report = fight(int(row['battle_id']), [int(row['god_skill'])] if row.get('god_skill') else [])
        got = {}
        if report.get('isWin'):
            if stage == allowed and stage > last:
                s['cleared'][fort] = stage
                got = give(state, pairs(row.get('awards')), rng)
            for k, n in give(state, drop(state, row['dropbox'], rng), rng).items(): got[k] = got.get(k, 0) + n
        else:
            state['items'][TICKET] = int(state['items'][TICKET]) + 1  # a lost fight gives the ticket back (LOCAL-046)
        return {'win': bool(report.get('isWin')), 'got': got}
    if act == 'hang':
        got, hours = pending(s, now)
        if not hours: raise LandError('Aún no hay recompensa acumulada')
        give(state, got, rng); s['hang_at'] = now if now - s['hang_at'] >= HANG_MAX else s['hang_at'] + hours * 3600
        return {'got': got}
    if act == 'buy':
        row = SHOP.get(str(request.get('id'))); n = max(1, min(int(request.get('count') or 1), 999))
        if not row: raise LandError('Artículo inexistente')
        if int(s['shop'].get(str(row['id']), 0)) + n > int(row['limit']): raise LandError('Límite de compra alcanzado este ciclo')
        cost = {k: v * n for k, v in pairs(row['cost']).items()}
        if any(int(state['items'].get(k, 0)) < v for k, v in cost.items()): raise LandError('Faltan Soul Branches')
        for k, v in cost.items(): state['items'][k] = int(state['items'][k]) - v
        s['shop'][str(row['id'])] = int(s['shop'].get(str(row['id']), 0)) + n
        return {'got': give(state, {k: v * n for k, v in pairs(row['item']).items()}, rng)}
    raise LandError('Acción de Land of Souls desconocida')
