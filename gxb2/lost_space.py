"""Lost Space Zone (activity 292, ActivityLostSpaceData / ActivityLostSpaceMapWindow; capture 2026-09-29-fb/62).

Each Space Zone is a 6x11 board (66 blocks). A block can be explored only next to (up / down / left / right) an explored one;
each costs 1 Space Radar (349) and gives 1 Laser Energy to the selected skill. What a block hides stays on it until it is
claimed (one by one or "Claim All"); special events are triggered by tapping them: Copier (the next reward found is
doubled), Hologram Machine (reveals where a high-value reward lies), Laser Energy +2 / +4, the Portal (after claiming the
zone's rewards: the zone chest, activity_lost_space_awards.award, and the next zone), Supply Coordinates (3 of them turn
into a Supply Stash, a second board with far better rewards, activity_lost_space_boxes group 3). The six lasers
(activity_lost_space_skill; ActivityLostSpaceMapWindow:getSkillIds) explore several blocks at once from the last explored
one when their energy is full: Sweep (the row), Cross (2 each side), Charged (3 up and down, 6 less energy per use, max 18),
Circle (the 8 around), Unstable (5 random), Adaptive (up and down, 1 more block per use up to 4). Switching laser resets the
energy. Auto Explore (5+ radars) explores, triggers events and lasers and claims, until the radars run out or a portal is
found. Radars can be bought with gems (misc activity_lost_space_buy_cost 2#100, limit 40).

Local rules (LOCAL-056): the server generated the boards; locally a zone holds the 55 boxes of group 1 and the events of
activity_lost_space_event (3 Copiers, 3 Holograms, 2x Energy+2, 1x Energy+4), the portal appears on the n-th exploration
drawn from export_step (23-33) and, in zones with if_treasure, a Supply Coordinate on one drawn from treasure_step. What a
block hides is decided when it is explored (a Hologram reserves a group-1 high-value box, show_icon, for the block it
points at). The Supply Stash holds the 57 boxes of group 3 plus 3 Copiers, 2 Holograms and 2x Energy+2, and its portal is
the last block, so it is explored fully. All six lasers are selectable. The event is always open; it starts with 30 radars
and gives 10 each day it is opened; the radar purchase limit (40) is per day; the paid Spaceship Supplies are not sold."""
from __future__ import annotations
import json, random, secrets
from pathlib import Path
from . import missions as daily

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/lost_space.json').read_text())
RADAR = '349'
COLS, ROWS, CELLS = 6, 11, 66
NO_OPEN, CAN_GET, EMPTY, KNOW_POS = 0, 1, 3, 4
DOUBLE, SEEK, ENERGY2, ENERGY4, EXIT, STASH, PART = 1, 2, 3, 4, 5, 6, 7
BUY = D['buy_cost']; BUY_LIMIT = D['buy_limit']


class SpaceError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def boxes(group):
    return [int(k) for k, b in sorted(D['boxes'].items(), key=lambda x: int(x[0])) if int(b['boxes']) == group for _ in range(int(b['num']))]


def span(text, rng):
    a, b = (int(x) for x in str(text).split('|'))
    return a + rng(b - a + 1)


def new_board(stage, rng, stash=False):
    start = rng(CELLS)
    board = {'map': [NO_OPEN] * CELLS, 'content': [''] * CELLS, 'last': start, 'opened': 1, 'reserved': {}}
    board['map'][start] = EMPTY
    if stash:
        board['bag'] = [str(b) for b in boxes(3)] + ['e#%d' % DOUBLE] * 3 + ['e#%d' % SEEK] * 2 + ['e#%d' % ENERGY2] * 2
        board['portal_at'] = CELLS; board['part_at'] = 0
    else:
        row = D['awards'][str(min(stage, len(D['awards'])))]
        bag = [str(b) for b in boxes(1)]
        for eid in (DOUBLE, SEEK, ENERGY2, ENERGY4): bag += ['e#%d' % eid] * int(D['events'][str(eid)]['num'])
        board['portal_at'] = span(row['export_step'], rng)
        board['part_at'] = span(row['treasure_step'], rng) if row.get('if_treasure') else 0
        extra = CELLS - 1 - 1 - (1 if board['part_at'] else 0) - len(bag)
        while extra < 0: bag.pop(rng(len(bag))); extra += 1
        g1 = boxes(1)
        for _ in range(extra): bag.append(str(g1[rng(len(g1))]))
        board['bag'] = bag
    return board


def data(state, now, rng=None):
    rng = rng or secrets.randbelow
    m = daily.saved(state, now)
    s = state.get('lost_space')
    if not s:
        first = random.Random('lost-space-1').randrange  # the same first board for the snapshot and the first action
        s = state['lost_space'] = {'stage': 1, 'board': new_board(1, first), 'stash': None, 'double': 0, 'piece': 0, 'skill': 0, 'energy': 0,
                                   'lvs': {'3': 0, '6': 0}, 'buy': 0, 'day': ''}
        state['items'][RADAR] = int(state['items'].get(RADAR, 0)) + 20  # starting radars (the daily 10 below make 30)
    if s['day'] != m['day']:
        s['day'] = m['day']; s['buy'] = 0; state['items'][RADAR] = int(state['items'].get(RADAR, 0)) + 10  # daily radars (local)
    return s


def board(s):
    return s['stash'] or s['board']


def neighbours(i):
    r, c = divmod(i, COLS)
    return [j for j, ok in ((i - COLS, r > 0), (i + COLS, r < ROWS - 1), (i - 1, c > 0), (i + 1, c < COLS - 1)) if ok]


def explorable(b, i):
    return b['map'][i] in (NO_OPEN, KNOW_POS) and any(b['map'][j] in (CAN_GET, EMPTY) for j in neighbours(i))


def skill_cost(s, sid):
    base = int(D['skills'][str(sid)]['energy'])
    return base - 6 * min(3, int(s['lvs'].get('3', 0))) if sid == 3 else base


def skill_ids(s, rng):
    """Blocks a laser explores from the last explored one (ActivityLostSpaceMapWindow:getSkillIds)."""
    b = board(s); sid = s['skill']; last = b['last']; r0, c0 = divmod(last, COLS)
    closed = lambda j: 0 <= j < CELLS and b['map'][j] in (NO_OPEN, KNOW_POS)
    same_col = lambda j: j % COLS == c0
    if sid == 1: ids = [j for j in range(r0 * COLS, r0 * COLS + COLS) if closed(j)]
    elif sid == 2: ids = [last + d for d in (-2, -1, 1, 2) if 0 <= c0 + d < COLS and closed(last + d)] + [last + d for d in (-12, -6, 6, 12) if closed(last + d)]
    elif sid == 3: ids = [last + d for d in (-18, -12, -6, 6, 12, 18) if closed(last + d)]
    elif sid == 4: ids = [last + dr * COLS + dc for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr or dc) and 0 <= c0 + dc < COLS and 0 <= r0 + dr < ROWS and closed(last + dr * COLS + dc)]
    elif sid == 5:
        pool = [j for j in range(CELLS) if closed(j)]; ids = []
        while pool and len(ids) < 5: ids.append(pool.pop(rng(len(pool))))
    elif sid == 6:
        lv = int(s['lvs'].get('6', 0)); ds = [-6, 6] + [d for n, d in ((1, -12), (2, 12), (3, -18), (4, 18)) if lv >= n]
        ids = [last + d for d in ds if closed(last + d)]
    else: ids = []
    return ids


def reveal(state, s, i, rng):
    """Explore block i: decide what it hides."""
    b = board(s); b['opened'] += 1; n = b['opened']
    if n == b['portal_at'] or (not b['bag'] and 'e#%d' % EXIT not in b['content']): content = 'e#%d' % EXIT
    elif n == b['part_at']: content = 'e#%d' % PART
    elif str(i) in b['reserved']: content = b['reserved'].pop(str(i))
    else: content = b['bag'].pop(rng(len(b['bag']))) if b['bag'] else str(boxes(1)[0])
    if not content.startswith('e#') and s['double'] > 0: content = str(int(content) + 10000); s['double'] -= 1
    b['content'][i] = content; b['map'][i] = CAN_GET; b['last'] = i
    return content


def claim(state, s, ids=None):
    b = board(s); got = {}
    for i in (ids if ids is not None else range(CELLS)):
        c = b['content'][i]
        if b['map'][i] != CAN_GET or not c or c.startswith('e#'): continue
        box = int(c); mult = 2 if box > 10000 else 1
        for k, v in pairs(D['boxes'][str(box % 10000)]['award']).items(): got[k] = got.get(k, 0) + v * mult
        b['map'][i] = EMPTY
    for k, v in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + v
    return got


def energy_cap(s):
    return skill_cost(s, s['skill']) if s['skill'] else 0


def gain_energy(s, n):
    if s['skill']: s['energy'] = min(energy_cap(s), s['energy'] + n)


def open_block(state, s, i, rng, now):
    b = board(s)
    if not 0 <= i < CELLS or not explorable(b, i): raise SpaceError('This area is hidden and cannot be explored')
    if int(state['items'].get(RADAR, 0)) < 1: raise SpaceError('Insufficient Space Radar')
    state['items'][RADAR] = int(state['items'][RADAR]) - 1; daily.record(state, 'radar', 1, now)
    gain_energy(s, 1)
    return reveal(state, s, i, rng)


def use_event(state, s, i, rng):
    b = board(s); c = b['content'][i]
    if b['map'][i] != CAN_GET or not c.startswith('e#'): raise SpaceError('Nada que activar')
    eid = int(c.split('#')[1]); out = {'event': eid}
    if eid == DOUBLE: s['double'] += 1
    elif eid == SEEK:
        closed = [j for j in range(CELLS) if b['map'][j] == NO_OPEN]
        if not closed: raise SpaceError('No explorable area')
        j = closed[rng(len(closed))]; b['map'][j] = KNOW_POS
        best = [str(k) for k, x in D['boxes'].items() if x.get('show_icon') and int(x['boxes']) == (3 if s['stash'] else 1)]
        b['reserved'][str(j)] = best[rng(len(best))]; out['pos'] = j
    elif eid in (ENERGY2, ENERGY4): gain_energy(s, int(D['events'][str(eid)]['energy_num']))
    elif eid == PART:
        s['piece'] += 1
        if s['piece'] >= 3:
            s['piece'] = 0; b['content'][i] = 'e#%d' % STASH
            return {'event': eid, 'stash_found': True}
    elif eid == STASH:
        b['map'][i] = EMPTY; s['stash'] = new_board(s['stage'], rng, stash=True)
        return {'event': eid}
    elif eid == EXIT:
        if any(b['map'][j] == CAN_GET and b['content'][j] and not b['content'][j].startswith('e#') for j in range(CELLS)):
            raise SpaceError('Please claim the rewards you found before entering the next Space Zone.')
        if s['stash']: s['stash'] = None; return {'event': eid, 'left_stash': True}
        row = D['awards'].get(str(s['stage']))
        got = pairs(row['award']) if row else {}
        for k, v in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + v
        s['stage'] += 1; s['board'] = new_board(s['stage'], rng)
        return {'event': eid, 'got': got, 'stage': s['stage']}
    b['map'][i] = EMPTY
    return out


def use_skill(state, s, rng):
    if not s['skill']: raise SpaceError('Elige un láser primero')
    if s['energy'] < energy_cap(s): raise SpaceError('Insufficient Laser Energy')
    ids = skill_ids(s, rng)
    if not ids: raise SpaceError('No explorable area is in your current skill range')
    found = [(i, reveal(state, s, i, rng)) for i in ids]
    s['energy'] = 0
    if s['skill'] == 3: s['lvs']['3'] = min(3, int(s['lvs'].get('3', 0)) + 1)
    if s['skill'] == 6: s['lvs']['6'] = min(4, int(s['lvs'].get('6', 0)) + 1)
    return found


def snapshot(state, now):
    view = json.loads(json.dumps(state)); s = data(view, now, rng=lambda k: 0)
    b = board(s)
    return {'stage': s['stage'], 'stash': bool(s['stash']), 'map': b['map'], 'content': [c if st in (CAN_GET, EMPTY) else '' for c, st in zip(b['content'], b['map'])],
            'explorable': [explorable(b, i) for i in range(CELLS)], 'last': b['last'], 'double': s['double'], 'piece': s['piece'], 'skill': s['skill'],
            'energy': s['energy'], 'cap': energy_cap(s), 'lvs': s['lvs'], 'radars': int(view['items'].get(RADAR, 0)), 'buy': s['buy'], 'buy_limit': BUY_LIMIT,
            'costs': {k: skill_cost(s, int(k)) for k in D['skills']}, 'treasure_zone': bool(D['awards'].get(str(s['stage']), {}).get('if_treasure'))}


def action(state, request, now, rng=None):
    rng = rng or secrets.randbelow
    s = data(state, now, rng); act = request.get('action')
    if s['stage'] > len(D['awards']) and not s['stash'] and act in ('open', 'auto'): raise SpaceError('You have explored all Space Zones!')
    if act == 'open':
        c = open_block(state, s, int(request.get('id', -1)), rng, now)
        return {'content': c}
    if act == 'claim':
        ids = request.get('ids'); got = claim(state, s, [int(x) for x in ids] if ids else None)
        if not got: raise SpaceError('No Rewards to Claim')
        return {'got': got}
    if act == 'event':
        return use_event(state, s, int(request.get('id', -1)), rng)
    if act == 'skill':
        sid = int(request.get('id') or 0)
        if str(sid) not in D['skills']: raise SpaceError('Láser inexistente')
        if sid != s['skill']: s['skill'] = sid; s['energy'] = 0
        return {}
    if act == 'laser':
        return {'found': use_skill(state, s, rng)}
    if act == 'buy':
        n = max(1, min(int(request.get('num') or 1), BUY_LIMIT))
        if s['buy'] + n > BUY_LIMIT: raise SpaceError('Límite de compra alcanzado')
        cost = {k: v * n for k, v in pairs(BUY).items()}
        if any(int(state['items'].get(k, 0)) < v for k, v in cost.items()): raise SpaceError('Faltan gemas')
        for k, v in cost.items(): state['items'][k] = int(state['items'][k]) - v
        state['items'][RADAR] = int(state['items'].get(RADAR, 0)) + n; s['buy'] += n
        return {}
    if act == 'auto':
        if int(state['items'].get(RADAR, 0)) < 5: raise SpaceError('Auto Explore is only available when you have 5 or more Space Radars')
        used, got, portal = 0, {}, False
        for _ in range(400):
            b = board(s)
            for i in range(CELLS):  # trigger events (not the portal / stash)
                c = b['content'][i]
                if b['map'][i] == CAN_GET and c.startswith('e#') and int(c[2:]) not in (EXIT, STASH):
                    try: use_event(state, s, i, rng)
                    except SpaceError: b['map'][i] = EMPTY
            if s['skill'] and s['energy'] >= energy_cap(s) and skill_ids(s, rng): use_skill(state, s, rng)
            for k, v in claim(state, s).items(): got[k] = got.get(k, 0) + v
            b = board(s)
            if any(b['map'][i] == CAN_GET and b['content'][i] == 'e#%d' % EXIT for i in range(CELLS)): portal = True; break
            opts = [i for i in range(CELLS) if explorable(b, i)]
            if not opts or int(state['items'].get(RADAR, 0)) < 1: break
            open_block(state, s, opts[rng(len(opts))], rng, now); used += 1
        for k, v in claim(state, s).items(): got[k] = got.get(k, 0) + v
        return {'used': used, 'got': got, 'portal': portal}
    raise SpaceError('Acción de Lost Space Zone desconocida')
