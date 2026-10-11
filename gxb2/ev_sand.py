"""Beach Treasure Hunt (activity 309: ActivitySandSearch, ActivitySandMission "Midsummer Task", ActivitySandShop "Ocean Coin
Exchange"; capture 2026-09-29-fb/61).

The sandcastle has 50 parts (activity_sand_gamble: 32 shells of 10 points, 10 of 50, 5 of 100, and one each of Water Ball,
Hermit Crab and Water Valve). Digging a part costs one Sand Shovel (390) and reveals what it hides; points fill the round
bar (activity_sand_award: 160 / 320 / 640), each mark gives its reward, and at 640 the next round starts with a new castle.
Auto dig opens after round 3 (ACTIVITY_SAND_TEXT03). Midsummer Task: daily missions (Echoes Observation, 3 League battles,
1 House Exam battle, a 3★+ Internship, then "all daily missions") and event missions (special events, a skin bought in the
exchange, shovels used, points earned). Ocean Coins (391) buy skins and items in the exchange (limits per row).

Local rules (LOCAL-051): the server chose which parts a special event opens; locally Water Ball opens the neighbouring
parts, Hermit Crab walks the rest of its row, Water Valve opens `parameter` (4) random parts; opened parts give their own
content (a special opened this way triggers too). The event is always available (no calendar), and the paid
Midsummer Invitation (double shovels) is not sold."""
from __future__ import annotations
import json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/ev_sand.json').read_text())
SHOVEL, COIN = '390', '391'
ROWS = [5, 7, 7, 7, 7, 7, 7, 3]  # castle layout (50 parts), row lengths top to bottom
CELLS = sum(ROWS)
AUTO_ROUND = 3
SPECIAL = {2: 'water_ball', 3: 'hermit_crab', 4: 'water_valve'}


class SandError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def layout():
    pos, i = [], 0
    for r, n in enumerate(ROWS):
        for c in range(n): pos.append((r, c + (7 - n) // 2)); i += 1
    return pos


POS = layout()
AT = {p: i for i, p in enumerate(POS)}


def new_castle(rng):
    cells = []
    for gid, g in sorted(D['gamble'].items(), key=lambda x: int(x[0])): cells += [int(gid)] * int(g['num'])
    rng.shuffle(cells)
    return {'cells': cells, 'open': [0] * CELLS}


def data(state, rng=None):
    s = state.get('ev_sand')
    if not s:
        s = state['ev_sand'] = {'round': 1, 'points': 0, 'claimed': [], 'castle': new_castle(rng or random.SystemRandom()), 'used': 0, 'earned': 0,
                                'specials': {}, 'skins_bought': 0, 'shop': {}, 'missions': [], 'daily_day': ''}
        state['items'][SHOVEL] = int(state['items'].get(SHOVEL, 0)) + 10  # a starting stack so the event can be tried
    return s


def round_row(s):
    rows = D['award']; return rows.get(str(s['round'])) or rows[str(max(int(k) for k in rows))]


def mission_value(state, s, m):
    t = int(m['type']); counts = state.get('missions', {}).get('counts', {})
    if t == 2: return int(counts.get('echoes_obs', 0))
    if t == 3: return int(counts.get('arena', 0))
    if t == 4: return int(counts.get('house_exam', 0))
    if t == 11: return int(counts.get('tavern3', 0))
    if t in (5, 6, 7): return int(s['specials'].get(SPECIAL[t - 3], 0))
    if t == 8: return int(s['skins_bought'])
    if t == 9: return int(s['used'])
    if t == 10: return int(s['earned'])
    if t == 1:
        daily = [x for x in D['mission'].values() if x.get('is_daily') == 1 and int(x['type']) != 1]
        return sum(1 for x in daily if done(state, s, x))
    return 0


def done(state, s, m):
    return mission_value(state, s, m) >= int(m['complete_value'])


def daily_reset(state, s):
    day = state.get('missions', {}).get('day', '')
    if s.get('daily_day') != day:
        s['daily_day'] = day
        s['missions'] = [i for i in s['missions'] if D['mission'][str(i)].get('is_daily') != 1]


def snapshot(state):
    view = json.loads(json.dumps(state)); s = data(view); daily_reset(view, s)
    row = round_row(s)
    return {'round': s['round'], 'points': s['points'], 'marks': [int(row['point1']), int(row['point2']), int(row['point3'])],
            'awards': [row['award1'], row['award2'], row['award3']], 'claimed': s['claimed'],
            'open': s['castle']['open'], 'cells': [c if o else 0 for c, o in zip(s['castle']['cells'], s['castle']['open'])],
            'shovels': int(view['items'].get(SHOVEL, 0)), 'coins': int(view['items'].get(COIN, 0)), 'auto': s['round'] >= AUTO_ROUND,
            'missions': [{'id': int(k), 'type': int(m['type']), 'daily': m.get('is_daily') == 1, 'need': int(m['complete_value']), 'have': mission_value(view, s, m),
                          'award': m['free_awards'], 'claimed': int(k) in s['missions']} for k, m in sorted(D['mission'].items(), key=lambda x: int(x[0]))],
            'shop': s['shop'], 'rows': ROWS}


def reveal(state, s, idx, rng, got, chain):
    castle = s['castle']
    if castle['open'][idx]: return
    castle['open'][idx] = 1; gid = castle['cells'][idx]; g = D['gamble'][str(gid)]; chain.append(idx)
    if int(g['type']) == 1:
        s['points'] += int(g['parameter']); s['earned'] += int(g['parameter'])
        return
    kind = SPECIAL[int(g['type'])]; s['specials'][kind] = int(s['specials'].get(kind, 0)) + 1
    r, c = POS[idx]
    if kind == 'water_ball':
        targets = [AT[p] for p in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1), (r - 1, c - 1), (r - 1, c + 1), (r + 1, c - 1), (r + 1, c + 1)) if p in AT]
    elif kind == 'hermit_crab':
        targets = [AT[p] for p in sorted(POS) if p[0] == r and p in AT]
    else:
        closed = [i for i, o in enumerate(castle['open']) if not o]; rng.shuffle(closed); targets = closed[:int(g['parameter'] or 4)]
    for t in targets: reveal(state, s, t, rng, got, chain)


def settle(state, s, got):
    """Round marks: each reached mark gives its award; the third one opens the next round with a new castle."""
    row = round_row(s)
    for i, (pt, aw) in enumerate(((row['point1'], row['award1']), (row['point2'], row['award2']), (row['point3'], row['award3']))):
        if s['points'] >= int(pt) and i not in s['claimed']:
            s['claimed'].append(i)
            for k, v in pairs(aw).items(): state['items'][k] = int(state['items'].get(k, 0)) + v; got[k] = got.get(k, 0) + v
    if len(s['claimed']) == 3:
        s['round'] += 1; s['points'] = 0; s['claimed'] = []; s['castle'] = new_castle(random.SystemRandom()); return True
    return False


def action(state, request, rng=None):
    rng = rng or random.SystemRandom()
    s = data(state, rng); daily_reset(state, s); act = request.get('action')
    if act == 'open':
        return {}
    if act in ('dig', 'auto'):
        idxs = [int(request.get('index', -1))] if act == 'dig' else None
        times = 1 if act == 'dig' else max(1, min(int(request.get('times') or 1), 50))
        if act == 'auto' and s['round'] < AUTO_ROUND: raise SandError('Auto dig available after entering Round 3')
        got, chain, new_round = {}, [], False
        for _ in range(times):
            if int(state['items'].get(SHOVEL, 0)) < 1: break
            closed = [i for i, o in enumerate(s['castle']['open']) if not o]
            idx = idxs[0] if idxs else rng.choice(closed)
            if not 0 <= idx < CELLS or s['castle']['open'][idx]: raise SandError('Esa parte ya está excavada')
            state['items'][SHOVEL] = int(state['items'][SHOVEL]) - 1; s['used'] += 1
            reveal(state, s, idx, rng, got, chain)
            if settle(state, s, got): new_round = True; break
        if not chain: raise SandError('Faltan Sand Shovels')
        return {'opened': chain, 'got': got, 'new_round': new_round}
    if act == 'mission':
        mid = str(request.get('id')); m = D['mission'].get(mid)
        if not m: raise SandError('Misión inexistente')
        if int(mid) in s['missions']: raise SandError('Ya reclamada')
        if not done(state, s, m): raise SandError('Misión sin completar')
        s['missions'].append(int(mid)); got = pairs(m['free_awards'])
        for k, v in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + v
        return {'got': got}
    if act == 'buy':
        row = D['shop'].get(str(request.get('id')))
        if not row: raise SandError('Artículo inexistente')
        bought = int(s['shop'].get(str(row['id']), 0))
        if row.get('limit') not in ('', None) and bought >= int(row['limit']): raise SandError('Límite alcanzado')
        cost = pairs(row['cost'])
        if any(int(state['items'].get(k, 0)) < v for k, v in cost.items()): raise SandError('Faltan Ocean Coins')
        for k, v in cost.items(): state['items'][k] = int(state['items'][k]) - v
        got = pairs(row['awards'])
        for k, v in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + v
        s['shop'][str(row['id'])] = bought + 1
        if any(7000 <= int(k) < 8000 for k in got): s['skins_bought'] += 1
        return {'got': got}
    raise SandError('Acción de Beach Treasure Hunt desconocida')
