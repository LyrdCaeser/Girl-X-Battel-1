"""Galaxy Voyage (models/GalaxyTrip.lua, GalaxyTripMapWindow.lua, GALAXY_TRIP_HELP01-03) offline.

Recovered from the client:
- Seasons of 28 days (misc.galaxy_trip_time from galaxy_trip_open_time): 27 exploring + 1 result day. Unlock: campaign
  stage 156 (function 55) and a 10★ Girl. Systems per season: galaxy_trip_open_num (4, 4, 6, 6, 6, 8…), each one opened by
  meeting the 3 requirements of the previous one (galaxy_trip_map_unlock: defeat the Ruler, open every Supply Crate,
  reach the end point). System of Eternity opens with System 4's requirements (galaxy_trip_black_hole_open 4|2|1).
- Map = W x H grid (galaxy_trip_map.size); server row 1 is the start (drawn at the bottom, "qd") and the last row the
  end ("zd"). A cell holds "event#battle" or -1 (NOTHING, not drawn); events can span 2x1, 2x2, 3x3 cells. You may
  explore the start row or any cell next (↑↓←→) to an explored one. Only one System at a time: moving to another resets
  the progress of the current one (points and Galaxy Stones stay).
- Enemies (common / elite / Ruler) cost 1 Galaxy Challenge Coupon (402: 10 at the start, +10 a day, 25 max). Common and
  elite HP persists; the Ruler must fall in one attempt and loses 1 % HP / Attack for every area explored beyond 30 %
  progress (max 40 %: galaxy_trip_enemy_weaken) — sent to the original engine as galaxy_info {hpP, atkP}.
- Other events take time (galaxy_trip_event_type.time): Blank Space 2 h, Mystery Planet 1 h (a battle buff for this
  System), Supply Crate 12 h. A route plans up to 6 areas (+ Voyage Team 2), explored one after another; Recall cancels
  the rest. Rewards: Tarnished Sphere (360), Galaxy Stones (398), Exploration Points (397).
- 3 Voyage Teams (galaxy_trip_team): the sum of (stars - 10) of their Girls sets the tier: team 1 = battle buff (god
  skill), team 2 = exploration time cut + route areas, team 3 = more 360 / 398.
- System of Eternity: Space Pirates appear each day (72 h, one attempt), the Galaxy Tyrant has difficulty 1..20 (5 at
  the start of a season; beating the highest opens the next level); battles by season count.
- Tasks give Exploration Points; Voyager Passport (free track) and the two Galaxy Stone stores unlock by points.

LOCAL decisions (DESIGN_DECISIONS.md LOCAL-038):
- The server drew the maps. Here a seeded generator follows the map table: `line_events_num` Blank Spaces open on the
  start and end rows, each elite row holds only its elites (you must beat them to go on), every event goes in its
  `area_id` rows with its size, the rest of the ordinary rows are Blank Space (no voids, as in the System of Phantom
  capture 2026-09-29-h) and the result must connect start and end. Battle ids per enemy are drawn from the event list.
- Routes only plan explorable areas (enemies are fought by hand). Space Pirates use the elite battles of the highest
  open System; pirates per day = 2 + (open Systems - 4). Beating a Tyrant level also pays the lower unpaid levels once.
- Unreadable task texts: 1009 = Mystery Planets explored, 1010 = highest Tyrant difficulty beaten. The paid Passport
  track isn't sold offline. Ranking brackets come from the season points (LOCAL_BRACKET).
"""
from __future__ import annotations
import copy, json, random, time
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/galaxy.json').read_text())
M = DATA['misc']
DAY = 86400
START = int(M['galaxy_trip_open_time'])
SEASON = int(M['galaxy_trip_time'])
EXPLORE = SEASON - DAY
COUPON = 402
C_INIT, C_DAY, C_MAX = (int(x) for x in str(M['galaxy_trip_challenge']).split('|'))
PLACES = int(M['galaxy_trip_explore_place'])
PIRATE_TIME = int(M['galaxy_trip_robber_time'])
OPEN_NUM = [int(x) for x in str(M['galaxy_trip_open_num']).split('|')]
W_FROM, W_STEP, W_MAX = (float(x) for x in str(M['galaxy_trip_enemy_weaken']).split('|'))
HOLE_NEED, PIRATE_BASE, PIRATE_STEP = (int(x) for x in str(M['galaxy_trip_black_hole_open']).split('|'))
BOSS_START, _BOSS_STEP, BOSS_MAX = (int(x) for x in str(M['galaxy_trip_boss_max_level']).split('|'))
UNLOCK_STAGE = 156  # function 55 (GALAXY_TRIP): open_type 2, open_value 156 ("Campaign Stage 16-4")
POINTS, STONE, SPHERE = '397', '398', '360'
HOLE = 999
MAPS = {int(m['id']): m for m in DATA['maps']}
EVENTS = {int(k): v for k, v in DATA['events'].items()}
TYPES = {int(k): v for k, v in DATA['types'].items()}
ENEMY, ELITE, RULER, BOX, EMPTY, PIRATE, TYRANT = 1, 2, 3, 9, 10, 11, 12
BUFF_TYPES = {4, 5, 6, 7, 8}
LOCAL_BRACKET = [(1200, 3), (1000, 4), (800, 5), (500, 6), (300, 7), (150, 8), (50, 9), (1, 10)]


def ids(text):
    return [int(float(x)) for x in str(text or '').split('|') if x not in ('', None)]


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[k] = out.get(k, 0) + int(float(n))
    return out


def add(items, got):
    for k, n in got.items():
        items[k] = int(items.get(k, 0)) + n


def season_of(now):
    n = max(0, (now - START) // SEASON) + 1
    start = START + (n - 1) * SEASON
    return n, start, start + EXPLORE, start + SEASON


def size_of(t):
    w, h = (int(x) for x in str(TYPES[t]['size']).split('|'))
    return w, h


def ev_type(eid):
    return int(EVENTS[eid]['type'])


# ---------------------------------------------------------------- map generator (LOCAL-038)

def generate(map_id, season):
    """Grid of W*H cells (index = (row-1)*W + col, row 1 = start). Each cell: {'e': event, 'b': battle, 'a': anchor}."""
    m = MAPS[map_id]
    W, H = (int(x) for x in str(m['size']).split('|'))
    for attempt in range(40):
        rng = random.Random(f'{season}:{map_id}:{attempt}')
        grid = [None] * (W * H)
        blank = next(e for e in ids(m['events']) if ev_type(e) == EMPTY)

        def put(eid, row, col):
            w, h = size_of(ev_type(eid))
            if col + w > W or row + h - 1 > H:
                return False
            cells = [(row - 1 + dy) * W + col + dx for dy in range(h) for dx in range(w)]
            if any(grid[c] is not None for c in cells):
                return False
            bids = ids(EVENTS[eid].get('battle_id'))
            cell = {'e': eid, 'b': rng.choice(bids) if bids else 0, 'a': cells[0]}
            for c in cells:
                grid[c] = dict(cell)
            return True

        def place(eid, rows, count):
            for _ in range(count):
                for _try in range(200):
                    if put(eid, rng.choice(rows), rng.randrange(W)):
                        break
                else:
                    return False
            return True

        line = int(m['line_events_num'] or 3)
        for row in (1, H):
            for col in rng.sample(range(W), line):
                put(blank, row, col)
        elite_rows = set()
        ok = True
        evs = [e for e in ids(m['events']) if ev_type(e) != EMPTY]
        evs.sort(key=lambda e: -size_of(ev_type(e))[0] * size_of(ev_type(e))[1])  # big events first
        for eid in evs:
            lo, hi = (int(x) for x in str(EVENTS[eid]['area_id']).split('|'))
            rows = [r for r in range(lo, hi + 1) if 1 < r < H]
            if ev_type(eid) == ELITE:
                elite_rows.update(rows)
            else:
                rows = [r for r in rows if r not in elite_rows] or rows
            ok = ok and place(eid, rows, int(EVENTS[eid]['amount']))
        if not ok:
            continue
        for row in range(2, H):  # elite rows are walls apart from their elites
            if row in elite_rows:
                continue
            free = [c for c in range((row - 1) * W, row * W) if grid[c] is None]
            for c in free:
                grid[c] = {'e': blank, 'b': 0, 'a': c}
        # capture 2026-09-29-h/04-06: ordinary rows are complete (no voids); only start / end / elite rows have gaps
        if connected(grid, W, H):
            return {'w': W, 'h': H, 'cells': [c if c else {'e': -1} for c in grid]}
    raise RuntimeError('No se pudo generar el mapa')


def neighbours(c, W, H):
    r, col = divmod(c, W)
    if col > 0: yield c - 1
    if col < W - 1: yield c + 1
    if r > 0: yield c - W
    if r < H - 1: yield c + W


def connected(grid, W, H):
    seen = [c for c in range(W) if grid[c]]
    todo = list(seen); seen = set(seen)
    while todo:
        c = todo.pop()
        for n in neighbours(c, W, H):
            if n not in seen and grid[n]:
                seen.add(n); todo.append(n)
    return any(c in seen for c in range(W * (H - 1), W * H)) and all(i in seen for i, g in enumerate(grid) if g)


def generate_hole(season):
    m = MAPS[HOLE]
    W, H = (int(x) for x in str(m['size']).split('|'))
    cells = [{'e': -1} for _ in range(W * H)]
    col, row = (W - 3) // 2, (H - 3) // 2  # Galaxy Tyrant (3x3) in the middle
    for dy in range(3):
        for dx in range(3):
            cells[(row + dy) * W + col + dx] = {'e': 12001, 'b': 0, 'a': row * W + col}
    return {'w': W, 'h': H, 'cells': cells}


# ---------------------------------------------------------------- state

def stars(p):
    from .engine import TABLES
    return int(TABLES['partner'][str(p['table_id'])]['max_star']) + int(p.get('awake', 0))


def unlocked(state):
    return int(state.get('max_stage', 0)) >= UNLOCK_STAGE and any(stars(p) >= 10 for p in state['partners'])


def fresh_season(n):
    return {'n': n, 'points': 0, 'maps': {}, 'cur': None, 'explore': None, 'open': 1, 'hole': False, 'counters': {}, 'tasks': [],
            'pass': [], 'store1': {}, 'boss_max': BOSS_START, 'boss_paid': [], 'pirates': [], 'pirate_day': 0, 'rewarded': False}


def saved(state, now):
    g = state.setdefault('galaxy', {})
    g.setdefault('teams', [[], [], []]); g.setdefault('history', {}); g.setdefault('store2', {})
    items = state.setdefault('items', {})
    n, start, explore_end, end = season_of(now)
    old = g.get('season')
    if not old or old['n'] != n:
        if old:
            finish_explore(state, g, now=min(now, season_of(start - 1)[2]))
            if not old.get('rewarded'):
                season_reward(state, g, old)
            g['history'][str(old['n'])] = old['points']
        g['season'] = fresh_season(n)
        if 'coupon_day' not in g:
            items[str(COUPON)] = max(int(items.get(str(COUPON), 0)), C_INIT)
        g['coupon_day'] = now // DAY
    s = g['season']
    days = now // DAY - int(g.get('coupon_day', now // DAY))
    if days > 0:
        items[str(COUPON)] = min(C_MAX, int(items.get(str(COUPON), 0)) + C_DAY * days) if int(items.get(str(COUPON), 0)) < C_MAX else int(items[str(COUPON)])
        g['coupon_day'] = now // DAY
    if now >= explore_end and s.get('explore'):
        finish_explore(state, g, now=explore_end)
    if now >= explore_end and not s.get('rewarded'):
        season_reward(state, g, s)
    return g


def season_reward(state, g, season):
    """LOCAL-038: ranking bracket from the season's Exploration Points."""
    season['rewarded'] = True
    pts = int(season['points'])
    rank = {int(r['id']): r for r in DATA['rank']}
    for need, row in LOCAL_BRACKET:
        if pts >= need:
            got = pairs(rank[row]['season_awards'])
            add(state['items'], got)
            g['last_reward'] = {'points': pts, 'bracket': rank[row]['rank_front'], 'got': got}
            return


def systems_open(n):
    return OPEN_NUM[min(n, len(OPEN_NUM)) - 1]


def map_state(s, mid):
    ms = s['maps'].get(str(mid))
    if not ms:
        grid = generate_hole(s['n']) if mid == HOLE else generate(mid, s['n'])
        ms = s['maps'][str(mid)] = {'grid': grid, 'opened': [], 'hp': {}, 'buffs': [], 'ruler': False, 'end': False}
    return ms


def cells_of(grid, anchor):
    return [i for i, c in enumerate(grid['cells']) if c.get('a') == anchor]


def explorable_total(grid):
    return sum(1 for c in grid['cells'] if c['e'] != -1)


def progress(ms):
    return len(ms['opened']) / max(1, explorable_total(ms['grid']))


def pct(ms):
    """GalaxyTrip:getGalaxyProgress: floor(explored / total * 100 + 0.1)."""
    import math
    return math.floor(progress(ms) * 100 + 0.1)


def crates(ms):
    anchors = {c['a'] for c in ms['grid']['cells'] if c['e'] != -1 and ev_type(c['e']) == BOX}
    done = {c for c in anchors if c in ms['opened']}
    return len(done), len(anchors)


def requirements(ms):
    got, need = crates(ms)
    return {'ruler': ms['ruler'], 'crates': [got, need], 'end': ms['end']}


def reqs_met(ms):
    r = requirements(ms)
    return r['ruler'] and r['crates'][0] >= r['crates'][1] and r['end']


def can_reach(ms, cell):
    grid = ms['grid']; W, H = grid['w'], grid['h']
    c = grid['cells'][cell]
    if c['e'] == -1:
        return False
    for part in cells_of(grid, c['a']):
        if part < W:
            return True
        if any(n in ms['opened'] for n in neighbours(part, W, H)):
            return True
    return False


def open_cells(state, g, ms, anchor, mult=True):
    """Mark an event explored and pay its rewards (Voyage Team 3 multiplies 360 / 398)."""
    s = g['season']
    grid = ms['grid']
    eid = grid['cells'][anchor]['e']
    ev = EVENTS[eid]
    parts = cells_of(grid, anchor)
    for p in parts:
        if p not in ms['opened']:
            ms['opened'].append(p)
    got = {}
    for key in ('award1', 'award2'):
        for k, n in pairs(ev.get(key)).items():
            got[k] = got.get(k, 0) + n
    if mult:
        loot = team_bonus(state, g, 3)
        if loot:
            if SPHERE in got:
                got[SPHERE] = int(got[SPHERE] * (1 + float(loot['award1_add'] or 0)))
            if STONE in got:
                got[STONE] = int(got[STONE] * (1 + float(loot['award2_add'] or 0)))
    add(state['items'], got)
    pts = int(ev.get('explore_points') or 0)
    s['points'] += pts
    got[POINTS] = pts
    t = ev_type(eid)
    counter(s, 1001, len(parts) if t not in (PIRATE, TYRANT) else 0)
    counter(s, {ENEMY: 1007, ELITE: 1003, RULER: 1008, BOX: 1004, PIRATE: 1005}.get(t, 0), 1)
    if t in BUFF_TYPES:
        ms['buffs'].append(int(ev['skill_id']))
        counter(s, 1009, 1)
    if t == RULER:
        ms['ruler'] = True
    W, H = grid['w'], grid['h']
    if any(p >= W * (H - 1) for p in parts) and not ms['end'] and s['cur'] != HOLE:
        ms['end'] = True
        counter(s, 1002, 1)
    counter_max(s, 1006, pct(ms))
    unlock_next(s)
    return got


def counter(s, key, n):
    if key and n:
        s['counters'][str(key)] = int(s['counters'].get(str(key), 0)) + n


def counter_max(s, key, v):
    s['counters'][str(key)] = max(int(s['counters'].get(str(key), 0)), v)


def unlock_next(s):
    while s['open'] < systems_open(s['n']):
        ms = s['maps'].get(str(s['open']))
        if not ms or not reqs_met(ms):
            break
        s['open'] += 1
    if not s['hole']:
        ms = s['maps'].get(str(HOLE_NEED))
        if ms and reqs_met(ms):
            s['hole'] = True


# ---------------------------------------------------------------- teams

def team_tier(state, members, typ):
    by = {p['partner_id']: p for p in state['partners']}
    total = sum(max(0, stars(by[m]) - 10) for m in members if m in by)
    rows = [t for t in DATA['teams'] if int(t['type']) == typ and total >= int(t['star_limit'])]
    return (rows[-1] if rows else None), total


def team_bonus(state, g, typ):
    return team_tier(state, g['teams'][typ - 1], typ)[0]


def explore_time(state, g, eid):
    t = int(TYPES[ev_type(eid)]['time'] or 0)
    cut = team_bonus(state, g, 2)
    return int(t * (1 - float(cut['explore_time_cut'] or 0))) if cut else t


def route_limit(state, g):
    b = team_bonus(state, g, 2)
    return PLACES + (int(b['explore_place_add'] or 0) if b else 0)


# ---------------------------------------------------------------- exploration

def explore_state(ex, now):
    """Which planned cells are done (claimable) at `now`."""
    done, t = [], int(ex['start'])
    for cell, dur in zip(ex['ids'], ex['times']):
        t += dur
        if t <= min(now, ex.get('stop') or now):
            done.append(cell)
    return done, t


def finish_explore(state, g, now):
    s = g['season']
    ex = s.get('explore')
    if not ex:
        return {}
    done, _ = explore_state(ex, now)
    ms = map_state(s, ex['map'])
    got = {}
    for cell in done:
        for k, n in open_cells(state, g, ms, cell).items():
            got[k] = got.get(k, 0) + n
    s['explore'] = None
    return got


def battle_gods(state, g, ms, eid):
    gods = [int(EVENTS[eid]['battle_skill'])] if EVENTS[eid].get('battle_skill') else []
    t1 = team_bonus(state, g, 1)
    if t1 and t1.get('god_skill'):
        gods.append(int(t1['god_skill']))
    return gods + list(ms['buffs'])


def weaken(ms):
    total = explorable_total(ms['grid'])
    extra = len(ms['opened']) - int(total * W_FROM + 0.999)
    return round(min(W_MAX, max(0, extra) * W_STEP), 4)


def spawn_pirates(state, g, now):
    s = g['season']
    if not s['hole'] or s['pirate_day'] == now // DAY:
        return
    s['pirate_day'] = now // DAY
    ms = map_state(s, HOLE)
    grid = ms['grid']
    s['pirates'] = [p for p in s['pirates'] if p['expire'] > now]
    taken = {p['cell'] for p in s['pirates']} | {i for i, c in enumerate(grid['cells']) if c['e'] != -1}
    free = [i for i in range(len(grid['cells'])) if i not in taken]
    rng = random.Random(f"{s['n']}:{now // DAY}:pirates")
    count = PIRATE_BASE + max(0, s['open'] - HOLE_NEED) * PIRATE_STEP
    top = max(1, min(s['open'], 8))
    elite = [e for e in ids(MAPS[top]['events']) if ev_type(e) == ELITE]
    battles = ids(EVENTS[elite[-1]]['battle_id']) if elite else []
    for cell in rng.sample(free, min(count, len(free))):
        s['pirates'].append({'cell': cell, 'battle': rng.choice(battles), 'expire': now + PIRATE_TIME, 'done': False})


def action(state, request, now=None, fight=None):
    now = int(time.time()) if now is None else now
    if not unlocked(state):
        raise ValueError(f'Galaxy Voyage se desbloquea al superar la fase {UNLOCK_STAGE} de la campaña y tener una chica de 10★')
    g = saved(state, now)
    s = g['season']
    items = state['items']
    kind = request.get('action')
    n, start, explore_end, end = season_of(now)
    exploring = now < explore_end
    if kind == 'open':
        if s['hole']:
            spawn_pirates(state, g, now)
        return {}
    if kind == 'teams':
        if s.get('explore'):
            raise ValueError('Cannot do this during an ongoing Exploration')
        teams = [[int(x) for x in t][:6] for t in (request.get('teams') or [[], [], []])][:3]
        owned = {p['partner_id'] for p in state['partners']}
        flat = [x for t in teams for x in t]
        if len(flat) != len(set(flat)) or any(x not in owned for x in flat):
            raise ValueError('Equipos no válidos')
        g['teams'] = teams + [[]] * (3 - len(teams))
        return {}
    if kind == 'claim_task':
        row = next((t for t in task_rows(s) if t['id'] == int(request.get('id', 0))), None)
        if not row or not row['claimable']:
            raise ValueError('Tarea no disponible')
        s['tasks'].append(row['id']); s['points'] += row['points']
        return {'got': {POINTS: row['points']}}
    if kind == 'claim_pass':
        pid = int(request.get('id', 0))
        row = next((p for p in DATA['pass'] if int(p['id']) == pid), None)
        if not row or pid in s['pass'] or s['points'] < int(row['point_limit']):
            raise ValueError('Premio no disponible')
        got = pairs(row['free_awards']); add(items, got); s['pass'].append(pid)
        return {'got': got}
    if kind == 'store':
        which, sid = int(request.get('store', 1)), int(request.get('id', 0))
        row = next((r for r in DATA['store1' if which == 1 else 'store2'] if int(r['id']) == sid), None)
        if not row:
            raise ValueError('Artículo no válido')
        bag = s['store1'] if which == 1 else g['store2']
        if int(bag.get(str(sid), 0)) >= int(row['buy_limit']):
            raise ValueError('Ya no quedan unidades')
        if not store_open(g, which, row):
            raise ValueError('Aún no cumples el requisito de Exploration Points')
        cost = pairs(row['cost'])
        if any(int(items.get(k, 0)) < v for k, v in cost.items()):
            raise ValueError('Faltan Galaxy Stones')
        for k, v in cost.items():
            items[k] = int(items[k]) - v
        got = pairs(row['item']); add(items, got); bag[str(sid)] = int(bag.get(str(sid), 0)) + 1
        return {'got': got}
    if not exploring and kind not in ('claim',):
        raise ValueError('Cannot do this in result phase')
    mid = int(request.get('map', s.get('cur') or 1))
    if kind == 'enter':
        if mid == HOLE:
            if not s['hole']:
                raise ValueError(f'Unlock after meeting the requirement of System No.{HOLE_NEED}')
            map_state(s, HOLE); spawn_pirates(state, g, now)
            return {}
        if mid not in MAPS or mid > s['open']:
            raise ValueError('Ese sistema aún está bloqueado')
        if s['cur'] and s['cur'] != mid:
            if s.get('explore'):
                raise ValueError('You need to Recall your current Exploration before moving to another System.')
            s['maps'].pop(str(s['cur']), None)  # "the Exploration Progress in this System will be reset"
        s['cur'] = mid
        map_state(s, mid)
        return {}
    if kind in ('route', 'recall', 'claim'):
        if kind == 'route':
            if s.get('explore'):
                raise ValueError('Please claim your Exploration Reward first')
            if mid != s['cur']:
                raise ValueError('Entra primero en este sistema')
            ms = map_state(s, mid)
            route = [int(c) for c in request.get('cells') or []]
            if not 1 <= len(route) <= route_limit(state, g) or len(set(route)) != len(route):
                raise ValueError(f'Planifica entre 1 y {route_limit(state, g)} áreas')
            seen = set(ms['opened'])
            anchors = []
            for c in route:
                cell = ms['grid']['cells'][c]
                if cell['e'] == -1 or ev_type(cell['e']) in (ENEMY, ELITE, RULER):
                    raise ValueError('Las rutas solo incluyen áreas explorables (sin enemigos)')
                a = cell['a']
                if a in ms['opened'] or a in anchors:
                    raise ValueError('Esa área ya está explorada')
                tmp = {**ms, 'opened': list(seen)}
                if not can_reach(tmp, a):
                    raise ValueError('Cada área debe estar junto al inicio o a una zona explorada')
                anchors.append(a); seen.update(cells_of(ms['grid'], a))
            s['explore'] = {'map': mid, 'ids': anchors, 'times': [explore_time(state, g, ms['grid']['cells'][a]['e']) for a in anchors], 'start': now}
            return {}
        if not s.get('explore'):
            raise ValueError('No hay ninguna exploración')
        if kind == 'recall':
            return {'got': finish_explore(state, g, now)}
        done, end_t = explore_state(s['explore'], now)
        if end_t > now:
            got = {}
            ex = s['explore']; ms = map_state(s, ex['map'])
            for cell in done:
                for k, v in open_cells(state, g, ms, cell).items():
                    got[k] = got.get(k, 0) + v
            ex['start'] = ex['start'] + sum(ex['times'][:len(done)])
            ex['ids'] = ex['ids'][len(done):]; ex['times'] = ex['times'][len(done):]
            return {'got': got}
        return {'got': finish_explore(state, g, now)}
    if kind == 'fight':
        team = request.get('team') or []
        owned = {p['partner_id']: p for p in state['partners']}
        if not 1 <= len(team) <= 6 or any(int(t['partner_id']) not in owned for t in team):
            raise ValueError('Equipo no válido')
        rows = [{**copy.deepcopy(owned[int(t['partner_id'])]), 'pos': int(t['pos'])} for t in team]
        if mid == HOLE:
            return fight_hole(state, g, request, rows, now, fight)
        if mid != s['cur']:
            raise ValueError('Entra primero en este sistema')
        ms = map_state(s, mid)
        cell = int(request.get('cell', -1))
        c = ms['grid']['cells'][cell] if 0 <= cell < len(ms['grid']['cells']) else {'e': -1}
        if c['e'] == -1 or ev_type(c['e']) not in (ENEMY, ELITE, RULER):
            raise ValueError('Ahí no hay ningún enemigo')
        a = c['a']
        if a in ms['opened']:
            raise ValueError('Ese enemigo ya fue derrotado')
        if not can_reach(ms, a):
            raise ValueError('Primero explora un área contigua')
        if int(items.get(str(COUPON), 0)) < 1:
            raise ValueError('No te quedan Galaxy Challenge Coupons (+10 cada día)')
        items[str(COUPON)] = int(items[str(COUPON)]) - 1
        t = ev_type(c['e'])
        status = ms['hp'].get(str(a)) if t != RULER else None
        w = weaken(ms) if t == RULER else 0
        report = fight(rows, int(c['b']), battle_gods(state, g, ms, c['e']), status, {'hpP': w, 'atkP': w} if w else None)
        win = bool(report['isWin'])
        result = {'battle': report, 'win': win, 'weaken': w}
        if win:
            ms['hp'].pop(str(a), None)
            result['got'] = open_cells(state, g, ms, a)
        elif t != RULER:
            ms['hp'][str(a)] = {str(x['pos'] - 6): {'hp': max(0, int(x['hp'])), 'mp': int(x['mp'])} for x in report.get('end_status', []) if x['pos'] > 6}
        return result
    raise ValueError('Acción de Galaxy Voyage no disponible')


def fight_hole(state, g, request, rows, now, fight):
    s = g['season']
    if not s['hole']:
        raise ValueError('System of Eternity está bloqueado')
    ms = map_state(s, HOLE)
    gods = battle_gods(state, g, {'buffs': []}, 12001)
    if 'pirate' in request:
        p = next((x for x in s['pirates'] if x['cell'] == int(request['pirate']) and not x['done']), None)
        if not p or p['expire'] <= now:
            raise ValueError('The enemy has escaped')
        report = fight(rows, int(p['battle']), gods, None, None)
        p['done'] = True  # one attempt
        result = {'battle': report, 'win': bool(report['isWin'])}
        if report['isWin']:
            ev = EVENTS[11001]
            got = pairs(ev.get('award2')); add(state['items'], got)
            s['points'] += int(ev['explore_points']); got[POINTS] = int(ev['explore_points'])
            counter(s, 1005, 1); result['got'] = got
        return result
    level = int(request.get('level', 1))
    if not 1 <= level <= s['boss_max']:
        raise ValueError(f'Dificultad no disponible (máximo {s["boss_max"]})')
    eid = 12000 + level
    bids = ids(EVENTS[eid]['battle_id'])
    report = fight(rows, bids[(s['n'] - 1) % len(bids)], gods, None, None)
    result = {'battle': report, 'win': bool(report['isWin'])}
    if report['isWin']:
        got = {}
        for lv in range(1, level + 1):  # LOCAL-038: a higher level also pays the unpaid lower ones
            if lv in s['boss_paid']:
                continue
            ev = EVENTS[12000 + lv]
            for k, v in pairs(ev.get('award2')).items():
                got[k] = got.get(k, 0) + v
            got[POINTS] = got.get(POINTS, 0) + int(ev['explore_points'])
            s['boss_paid'].append(lv)
        pts = got.pop(POINTS, 0)
        add(state['items'], got); s['points'] += pts
        if pts:
            got[POINTS] = pts
        if level == s['boss_max'] and s['boss_max'] < BOSS_MAX:
            s['boss_max'] += 1
        counter_max(s, 1010, level)
        result['got'] = got
    return result


def store_open(g, which, row):
    s = g['season']
    if which == 1:
        return s['points'] >= int(row['point_limit'] or 0)
    need_seasons, need_pts = (int(x) for x in str(row.get('trip_limit') or '0|0').split('|'))
    good = sum(1 for v in list(g['history'].values()) + [s['points']] if int(v) >= need_pts)
    return good >= need_seasons


def task_rows(s):
    out = []
    for m in DATA['missions']:
        if int(m['begin_season']) > s['n']:
            continue
        key = str(m['text_id'])
        text = DATA['mission_text'].get(key) or {'1009': 'Explore {1} Mystery Planet(s) in this season',
                                                 '1010': 'Defeat Galaxy Tyrant of Difficulty Level {1} in this season'}.get(key, key)
        val, need = int(s['counters'].get(key, 0)), int(m['complete'])
        out.append({'id': int(m['id']), 'text': text.replace('{1}', str(need)).replace('%%', '%'), 'value': val, 'need': need,
                    'points': int(m['explore_points']), 'claimed': int(m['id']) in s['tasks'], 'claimable': val >= need and int(m['id']) not in s['tasks']})
    return out


# ---------------------------------------------------------------- snapshot

def enemy_view(battle_id):
    from .engine import TABLES
    b = TABLES['battle'].get(str(battle_id), {})
    out = []
    for m in str(b.get('monsters', '')).split('|'):
        mon = TABLES['monster'].get(m)
        if mon:
            out.append({'table_id': int(mon['partner_link']), 'lv': int(mon.get('lv') or 0)})
    return out


def cell_view(ms, s, now, mid):
    grid = ms['grid']
    ex = s.get('explore') if s.get('explore') and s['explore']['map'] == mid else None
    done, _ = explore_state(ex, now) if ex else ([], 0)
    planned = {a: i for i, a in enumerate(ex['ids'])} if ex else {}
    out = []
    for i, c in enumerate(grid['cells']):
        if c['e'] == -1:
            out.append(None); continue
        t = ev_type(c['e'])
        a = c['a']
        st = 'done' if i in ms['opened'] else 'ready' if a in done else 'exploring' if a in planned else ('open' if can_reach(ms, a) else 'fog')
        v = {'t': t, 'a': a, 's': st}
        if a == i:
            v['e'] = c['e']
            if str(a) in ms['hp']:
                hp = ms['hp'][str(a)]
                v['hp'] = round(sum(x['hp'] for x in hp.values()) / (100 * max(1, len(hp))), 3)
        if a in planned:
            v['n'] = planned[a] + 1
        out.append(v)
    return out


def snapshot(state, now=None):
    now = int(time.time()) if now is None else now
    view = copy.deepcopy(state)
    if not unlocked(view):
        return {'unlocked': False, 'unlock_stage': UNLOCK_STAGE}
    g = saved(view, now)
    s = g['season']
    if s['hole']:
        spawn_pirates(view, g, now)
    n, start, explore_end, end = season_of(now)
    systems = []
    for mid, m in sorted(MAPS.items()):
        if mid == HOLE:
            continue
        ms = s['maps'].get(str(mid))
        systems.append({'id': mid, 'name': DATA['map_text'].get(str(m['name_text_id']), ''), 'intro': DATA['map_text'].get(str(m['intro_text_id']), ''),
                        'icon': m['icon_text'], 'big': m['icon_big_text'], 'bg': m['map_text'], 'mask': m['icon_mask_text'],
                        'available': mid <= systems_open(n), 'open': mid <= s['open'] and mid <= systems_open(n),
                        'progress': pct(ms) if ms else 0, 'req': requirements(ms) if ms else None, 'current': s['cur'] == mid})
    hole = MAPS[HOLE]
    info = {'unlocked': True, 'season': n, 'exploring': now < explore_end, 'explore_end': explore_end, 'season_end': end,
            'points': s['points'], 'coupons': int(view['items'].get(str(COUPON), 0)), 'coupon_max': C_MAX, 'stones': int(view['items'].get(STONE, 0)),
            'systems': systems, 'current': s['cur'], 'hole': {'open': s['hole'], 'name': DATA['map_text'].get(str(hole['name_text_id']), ''),
                                                             'intro': DATA['map_text'].get(str(hole['intro_text_id']), ''), 'icon': hole['icon_text'], 'big': hole['icon_big_text'], 'bg': hole['map_text']},
            'route_limit': route_limit(view, g), 'tasks': task_rows(s), 'last_reward': g.get('last_reward'),
            'pass': [{'id': int(p['id']), 'need': int(p['point_limit']), 'free': pairs(p['free_awards']), 'pay': pairs(p['pay_awards']),
                      'claimed': int(p['id']) in s['pass']} for p in DATA['pass'] if int(p['begin_season']) <= n],
            'store': {'season': [{**r, 'bought': int(s['store1'].get(str(r['id']), 0)), 'ok': store_open(g, 1, r)} for r in DATA['store1'] if int(r['begin_season']) <= n],
                      'permanent': [{**r, 'bought': int(g['store2'].get(str(r['id']), 0)), 'ok': store_open(g, 2, r)} for r in DATA['store2'] if int(r['begin_season']) <= n]},
            'store_text': DATA['store_text'], 'help': [DATA['text'].get(f'GALAXY_TRIP_HELP0{i}', '') for i in (1, 2, 3)]}
    teams = []
    for i, members in enumerate(g['teams']):
        row, total = team_tier(view, members, i + 1)
        teams.append({'members': members, 'total': total, 'tier': row, 'text': DATA['team_text'].get(str(1001 + i), '')})
    info['teams'] = teams
    info['team_tiers'] = DATA['teams']
    maps = {}
    for mid_s, ms in s['maps'].items():
        mid = int(mid_s)
        v = {'id': mid, 'w': ms['grid']['w'], 'h': ms['grid']['h'], 'cells': cell_view(ms, s, now, mid), 'buffs': ms['buffs'], 'progress': pct(ms),
             'req': requirements(ms) if mid != HOLE else None, 'weaken': weaken(ms) if mid != HOLE else 0}
        maps[mid_s] = v
    info['maps'] = maps
    ex = s.get('explore')
    if ex:
        done, end_t = explore_state(ex, now)
        info['explore'] = {'map': ex['map'], 'ids': ex['ids'], 'times': ex['times'], 'start': ex['start'], 'end': end_t, 'done': len(done)}
    info['pirates'] = [p for p in s['pirates'] if p['expire'] > now]
    info['boss'] = {'max': s['boss_max'], 'top': BOSS_MAX, 'paid': s['boss_paid'],
                    'levels': [{'level': lv, 'points': int(EVENTS[12000 + lv]['explore_points']), 'awards': pairs(EVENTS[12000 + lv].get('award2')),
                                'enemy': enemy_view(ids(EVENTS[12000 + lv]['battle_id'])[(n - 1) % len(ids(EVENTS[12000 + lv]['battle_id']))])} for lv in range(1, BOSS_MAX + 1)]}
    info['events'] = {str(k): {'type': ev_type(k), 'points': int(v.get('explore_points') or 0), 'awards': {**pairs(v.get('award1')), **pairs(v.get('award2'))}, 'skill': v.get('skill_id')}
                      for k, v in EVENTS.items()}
    info['types'] = {str(k): {'name': DATA['type_text'].get(str(v['name_text_id']), ''), 'intro': DATA['type_text'].get(str(v['intro_text_id']), ''),
                              'icon': v['icon_text'], 'big': v['icon_big_text'], 'size': [int(x) for x in str(v['size']).split('|')], 'time': int(v['time'] or 0)} for k, v in TYPES.items()}
    info['buff_text'] = DATA['buff_text']
    return info
