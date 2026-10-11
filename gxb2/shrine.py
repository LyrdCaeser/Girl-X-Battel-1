"""Tsuruga Grand Shrine (models/ShrineHurdleModel.lua, models/Shrine.lua, SHRINE_HURDLE_HELP) offline.

Recovered from the client:
- Seasons of 12 challenge days + 2 rest days from misc.shrine_time_start. At the start of each season Trial Invitations
  (322) are set to 15; up to 5 more can be bought for 10 gems each. Unlock: Tests floor > 500 and a 10★ Girl.
- 3 Trials per season (shrine_route 1-3); each has 2 environment effects (environment1..3 by season count, as god
  skills) and its own battle set (shrine_hurdle c{count}_route{route}). Entering costs 1 Invitation; only 10★+ Girls
  can take part and they are frozen (stats and gear) for that Trial.
- Difficulty 1-300 (shrine_difficulty applied by the original engine through `shrineId`); points = stage score x
  score_ratio. The highest difficulty unlocked per Trial grows with misc.shrine_hurdle_difficulty_count, and it never
  goes back down; the suggested level is max - 5 (shrine_hurdle_difficulty_float).
- 15 stages (shrine_hurdle.hurdle): 1 Battle (15 rounds max, HP kept between stages, enemies reset after a defeat),
  2 Reward (3 random buffs or Give Up for 180 Trial Tokens), 3 Store (buy buffs for 180 / upgrade owned buffs for 90, max
  +2), 4 Recover (all +30 %, the 3 lowest +80 %, or revive one Girl to 100 %), 5 Boss (one attempt; points =
  shrine_hurdle_boss_score_count(ratio, damage)). Stages with two types let you choose the way.
- Buffs = god skills (skill_1..3 by level) added to the environment. Battles win 90 Trial Tokens (324).
- Message Board: season Tasks (shrine_mission) and permanent Achievements (shrine_achievement / _type).
  Pond of Prayers: Origami Crane (323) shops, seasonal (shop_shrine2 type 1, reset each season) and permanent.
- Story: the Prologue plays on the first visit; chapters (shrine_plot_list) can be reviewed.

LOCAL decisions (DESIGN_DECISIONS.md LOCAL-037):
- Ranking doesn't exist offline: when a season's challenge phase ends, the ranking reward is chosen from the season
  total (>=24000 → 201-500 bracket … any Trial → 10001+), with the overall and per-Trial rows as the original sends.
- The server chose which enemy group of a stage appears; here a seeded draw. The Trial seed decides the buffs offered.
- Chime achievements (Tree of Chimes isn't rebuilt yet) stay at 0. Story chapter N unlocks after N completed Trials.
"""
from __future__ import annotations
import copy, json, math, random, time
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/shrine.json').read_text())
M = DATA['misc']
DAY = 86400
START = int(M['shrine_time_start'])
FIGHT_DAYS, REST_DAYS = (int(x) for x in str(M['shrine_time_interval']).split('|'))
SEASON = (FIGHT_DAYS + REST_DAYS) * DAY
TICKET, TICKET_MAX = (int(x) for x in str(M['shrine_hurdle_ticket']).split('#'))
BUY_COST = int(str(M['shrine_hurdle_ticket_buy_cost']).split('#')[1])
BUY_LIMIT = int(M['shrine_hurdle_ticket_buy_limit'])
GOLD = 324
GIVEUP_GOLD = int(str(M['shrine_hurdle_buff_giveup']).split('#')[1])
DIFF_FLOAT = int(M['shrine_hurdle_difficulty_float'])
DIFF_MAX = max(int(k) for k in DATA['diff'])
OPEN_FLOOR = int(M['shrine_open_limit'])
CRANE = 323
BATTLE_TYPE = 61  # xyd.BattleType.SHRINE_HURDLE
MAX_ROUND = 15
FLOORS = {int(f['id']): f for f in DATA['floors']}
BUFFS = {int(b['id']): b for b in DATA['buffs']}
ROUTES = {int(r['id']): r for r in DATA['routes']}
TYPE_NAME = {1: 'battle', 2: 'reward', 3: 'store', 4: 'recover', 5: 'boss'}


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
    return n, start, start + FIGHT_DAYS * DAY, start + SEASON


def count_of(n):
    return (n - 1) % 3 + 1  # the season "count" picks environment{count} and c{count}_route{route}


def stars(p):
    from .engine import TABLES
    return int(TABLES['partner'][str(p['table_id'])]['max_star']) + int(p.get('awake', 0))


def unlock_state(state):
    floor = int(state.get('tower', {}).get('max_stage', 0))
    ten = any(stars(p) >= 10 for p in state['partners'])
    return floor, ten, floor >= OPEN_FLOOR + 1 and ten


def difficulty_after(score, diff):
    """misc.shrine_hurdle_difficulty_count: score / ratio / 10 / (diff / 10 + 1.5) + diff + 5 (ratio = score_ratio)."""
    ratio = float(DATA['diff'][str(diff)]['score_ratio'])
    return min(DIFF_MAX, int(score / ratio / 10 / (diff / 10 + 1.5) + diff + 5))


def boss_points(diff, damage):
    """misc.shrine_hurdle_boss_score_count: ceil(1000 * ratio * (1 - e^(-2e-11 * damage)))."""
    ratio = float(DATA['diff'][str(diff)]['score_ratio'])
    return math.ceil(1000 * ratio * (1 - math.pow(2.71828, -0.00000000002 * damage)))


# ---------------------------------------------------------------- state

def fresh_season(n):
    return {'n': n, 'scores': {}, 'wins': 0, 'done': {}, 'claimed': [], 'shop': {}, 'buys': 0, 'rewarded': False}


def saved(state, now):
    s = state.setdefault('shrine', {})
    s.setdefault('max_diff', {}); s.setdefault('ach', {}); s.setdefault('ach_val', {}); s.setdefault('shop1', {})
    s.setdefault('completed', 0); s.setdefault('plots', []); s.setdefault('run', None)
    n, start, fight_end, end = season_of(now)
    items = state.setdefault('items', {})
    old = s.get('season')
    if not old or old['n'] != n:
        if old and s.get('run'):
            s['run'] = None  # a Trial left open when the season ended is closed without score
        if old and not old.get('rewarded'):
            season_reward(state, s, old)
        s['season'] = fresh_season(n)
        items[str(TICKET)] = TICKET_MAX  # "set to 15 (max capacity)" at the beginning of each season
    elif now >= fight_end and not s['season'].get('rewarded'):
        if s.get('run'):
            end_run(state, s, completed=False)
        season_reward(state, s, s['season'])
    return s


def season_total(season):
    return sum(int(v) for v in season['scores'].values())


LOCAL_BRACKET = [(24000, 3), (18000, 4), (12000, 5), (6000, 6), (2000, 7), (1, 8)]


def rank_row(i):
    return next(r for r in DATA['rank'] if int(r['id']) == i)


def season_reward(state, s, season):
    """LOCAL-037: offline ranking bracket from the season total (overall awards_0 + awards_{route} per Trial)."""
    season['rewarded'] = True
    total = season_total(season)
    rank = {int(r['id']): r for r in DATA['rank']}
    got = {}
    for need, row in LOCAL_BRACKET:
        if total >= need:
            for k, n in pairs(rank[row]['awards_0']).items():
                got[k] = got.get(k, 0) + n
            break
    for route, score in season['scores'].items():
        for need, row in LOCAL_BRACKET:
            if int(score) >= need / 3:
                for k, n in pairs(rank[row][f'awards_{route}']).items():
                    got[k] = got.get(k, 0) + n
                break
    add(state.setdefault('items', {}), got)
    s['last_reward'] = got


# ---------------------------------------------------------------- achievements

def ach_steps(at):
    return list(range(int(at['start_achievement']), int(at['end_achievement']) + 1))


def ach_rows(s):
    rows = []
    for at in DATA['ach_type']:
        steps = ach_steps(at)
        val = int(s['ach_val'].get(str(at['id']), 0))
        claimed = int(s['ach'].get(str(at['id']), 0))
        cur = steps[min(claimed, len(steps) - 1)]
        need = int(DATA['ach'][str(cur)]['complete_value'])
        rows.append({'id': int(at['id']), 'value': val, 'need': need, 'steps': len(steps), 'claimed': claimed, 'done': claimed >= len(steps),
                     'claimable': claimed < len(steps) and val >= need, 'awards': pairs(DATA['ach'][str(cur)]['awards']),
                     'text': DATA['ach_text'].get(str(at['id']), '').replace('{1}', f'{need:,}').replace('%%', '%')})
    return rows


def ach_max(s, aid, value):
    s['ach_val'][str(aid)] = max(int(s['ach_val'].get(str(aid), 0)), int(value))


def mission_rows(s):
    season = s['season']
    out = []
    for m in DATA['missions']:
        typ, need = int(m['type']), int(m['complete'])
        if typ <= 3:
            val = int(season['done'].get(str(typ), 0))
            text = DATA['mission_text'][str(m['id'])].replace('{1}', route_name(typ, season['n']))
        elif typ == 4:
            val, text = int(season['wins']), DATA['mission_text'][str(m['id'])]
        else:
            val, text = season_total(season), DATA['mission_text'][str(m['id'])]
        out.append({'id': int(m['id']), 'text': text, 'value': val, 'need': need, 'awards': pairs(m['awards']),
                    'claimed': int(m['id']) in season['claimed'], 'claimable': val >= need and int(m['id']) not in season['claimed']})
    return out


def route_env(route, n):
    return ids(ROUTES[route][f'environment{count_of(n)}'])


def route_name(route, n):
    return DATA['route_text'].get(str(route_env(route, n)[0]), {}).get('name', f'Trial {route}')


# ---------------------------------------------------------------- run

def floor_types(floor):
    return ids(FLOORS[floor]['hurdle'])


def floor_options(run, floor):
    return ids(FLOORS[floor][f"c{count_of(run['season'])}_route{run['route']}"])


def rng_for(run, tag):
    return random.Random(f"{run['seed']}:{run['floor']}:{tag}")


def enter_floor(run):
    """Set up the current stage (ShrineHurdleModel:onNextFloor / extra)."""
    types = floor_types(run['floor'])
    run['type'] = types[0] if len(types) == 1 else None  # None → choose the way first
    run['extra'] = {}
    run['can_next'] = False
    if run['type']:
        setup_type(run)


def setup_type(run):
    typ, rng = run['type'], rng_for(run, 'setup')
    ex = run['extra']
    if typ == 1:
        opts = floor_options(run, run['floor'])
        ex['battle'] = rng.choice(opts)
    elif typ == 5:
        ex['boss'] = floor_options(run, run['floor'])[0]
    elif typ == 2:
        free = [b for b in BUFFS if str(b) not in run['skills']]
        ex['skills'] = rng.sample(free, min(3, len(free)))
    elif typ == 3:
        free = [b for b in BUFFS if str(b) not in run['skills']]
        ex['buys'] = rng.sample(free, min(3, len(free)))
        ups = [int(b) for b, lv in run['skills'].items() if lv < 3]
        ex['upgrades'] = rng.sample(ups, min(3, len(ups)))
        ex['bought'] = []
        run['can_next'] = True
        run['flags']['store'] = True
    elif typ == 4:
        run['flags']['recover'] = True


def god_skills(run):
    out = list(run['env'])
    for b, lv in run['skills'].items():
        out.append(int(BUFFS[int(b)][f'skill_{min(3, int(lv))}']))
    return out


def run_view(state, s):
    run = s['run']
    if not run:
        return None
    from .engine import TABLES
    ex = run['extra']
    view = {'route': run['route'], 'name': route_name(run['route'], run['season']), 'diff': run['diff'], 'floor': run['floor'], 'type': run['type'],
            'types': floor_types(run['floor']), 'gold': run['gold'], 'score': run['score'], 'can_next': run['can_next'],
            'skills': run['skills'], 'partners': [{'partner_id': int(k), **v} for k, v in run['partners'].items()], 'extra': copy.deepcopy(ex)}
    if run['type'] in (1, 5):
        key = ex.get('battle') or ex.get('boss')
        row = DATA['battles' if run['type'] == 1 else 'bosses'][str(key)]
        b = TABLES['battle'][str(row['battle_id'])]
        mons = [int(x) for x in str(b['monsters']).split('|')]
        view['enemy'] = [{'table_id': int(TABLES['monster'][str(m)]['partner_link']), 'lv': int(TABLES['monster'][str(m)].get('lv') or 0)} for m in mons]
        view['points'] = int(row.get('score') or 0) * int(DATA['diff'][str(run['diff'])]['score_ratio']) if run['type'] == 1 else None
    return view


def start_run(state, s, route, diff, now, seed):
    season = s['season']
    if route not in ROUTES:
        raise ValueError('Prueba no válida')
    maxd = max(1, int(s['max_diff'].get(str(route), 1)))
    if not 1 <= diff <= maxd:
        raise ValueError(f'Dificultad no desbloqueada (máximo {maxd})')
    girls = [p for p in state['partners'] if stars(p) >= 10]
    if not girls:
        raise ValueError('Solo pueden participar chicas de 10★ o más')
    items = state['items']
    if int(items.get(str(TICKET), 0)) < 1:
        raise ValueError('No te quedan Trial Invitations')
    items[str(TICKET)] = int(items[str(TICKET)]) - 1
    s['run'] = run = {'route': route, 'diff': diff, 'season': season['n'], 'env': route_env(route, season['n']), 'floor': 1, 'seed': seed,
                      'gold': 0, 'score': 0, 'skills': {}, 'lineup': None,
                      'partners': {str(p['partner_id']): {'hp': 100, 'mp': 50} for p in girls},
                      'frozen': {str(p['partner_id']): copy.deepcopy(p) for p in girls},
                      'flags': {'recover': False, 'store': False, 'relineup': False, 'dead': False, 'plus2': False}}
    enter_floor(run)


def end_run(state, s, completed):
    run = s['run']
    s['run'] = None
    season = s['season']
    route, score = str(run['route']), int(run['score'])
    season['scores'][route] = max(int(season['scores'].get(route, 0)), score)
    old = int(s['max_diff'].get(route, 1))
    if score > 0:  # LOCAL-037: a Trial left with 0 points doesn't unlock higher levels
        s['max_diff'][route] = max(old, difficulty_after(score, run['diff']))
    else:
        s['max_diff'][route] = old
    result = {'score': score, 'completed': completed, 'max_diff': s['max_diff'][route]}
    if completed:
        season['done'][route] = int(season['done'].get(route, 0)) + 1
        s['completed'] = int(s['completed']) + 1
        ach_max(s, 2, run['diff'])
        f = run['flags']
        for aid, ok in ((3, not f['recover']), (4, not f['store']), (5, not f['relineup']), (6, not f['dead'])):
            if ok:
                ach_max(s, aid, 1)
    ach_max(s, 1, season_total(season))
    return result


def action(state, request, now=None, fight=None, seed=None):
    now = int(time.time()) if now is None else now
    floor, ten, ok = unlock_state(state)
    if not ok:
        raise ValueError(f'El Santuario Tsuruga se desbloquea al superar el piso {OPEN_FLOOR} de Tests y tener una chica de 10★')
    s = saved(state, now)
    items = state['items']
    kind = request.get('action')
    n, start, fight_end, end = season_of(now)
    if kind == 'open':
        return {}
    if kind == 'plot':
        pid = int(request.get('plot', 1000))
        if pid not in s['plots']:
            s['plots'].append(pid)
        return {}
    if kind == 'buy_ticket':
        k = max(1, int(request.get('count', 1)))
        if s['season']['buys'] + k > BUY_LIMIT:
            raise ValueError('Has alcanzado el límite de compras de esta temporada')
        if int(items.get('2', 0)) < BUY_COST * k:
            raise ValueError('Faltan gemas')
        items['2'] = int(items['2']) - BUY_COST * k
        items[str(TICKET)] = int(items.get(str(TICKET), 0)) + k
        s['season']['buys'] += k
        return {}
    if kind == 'claim_task':
        row = next((m for m in mission_rows(s) if m['id'] == int(request.get('id', 0))), None)
        if not row or not row['claimable']:
            raise ValueError('Tarea no disponible')
        add(items, row['awards']); s['season']['claimed'].append(row['id'])
        return {'got': row['awards']}
    if kind == 'claim_ach':
        row = next((a for a in ach_rows(s) if a['id'] == int(request.get('id', 0))), None)
        if not row or not row['claimable']:
            raise ValueError('Logro no disponible')
        add(items, row['awards']); s['ach'][str(row['id'])] = row['claimed'] + 1
        return {'got': row['awards']}
    if kind == 'shop':
        which, sid = int(request.get('shop', 2)), int(request.get('id', 0))
        rows = {int(r['id']): r for r in DATA['shop1' if which == 1 else 'shop2']}
        row = rows.get(sid)
        if not row:
            raise ValueError('Artículo no válido')
        bag = s['shop1'] if which == 1 or int(row.get('type', 2)) == 2 else s['season']['shop']
        key = f'{which}:{sid}'
        if int(bag.get(key, 0)) >= int(row['buy_time']):
            raise ValueError('Ya no quedan unidades')
        cost = pairs(row['cost'])
        if any(int(items.get(k, 0)) < v for k, v in cost.items()):
            raise ValueError('Faltan Origami Cranes' if str(CRANE) in cost else 'Faltan materiales')
        for k, v in cost.items():
            items[k] = int(items[k]) - v
        got = pairs(row['item']); add(items, got)
        bag[key] = int(bag.get(key, 0)) + 1
        return {'got': got}
    # ---- Realm of Trials
    if kind == 'start':
        if s['run']:
            raise ValueError('Ya hay una prueba en curso')
        if now >= fight_end:
            raise ValueError('La fase de desafío de la temporada ha terminado')
        start_run(state, s, int(request.get('route', 0)), int(request.get('diff', 1)), now, seed if seed is not None else now)
        return {}
    run = s['run']
    if not run:
        raise ValueError('No hay ninguna prueba en curso')
    ex = run['extra']
    if kind == 'giveup_trial':
        return {'end': end_run(state, s, completed=False)}
    if kind == 'way':
        types = floor_types(run['floor'])
        i = int(request.get('index', 0))
        if run['type'] or not 0 <= i < len(types):
            raise ValueError('Camino no válido')
        run['type'] = types[i]; setup_type(run)
        return {}
    if kind == 'next':
        if not run['can_next']:
            raise ValueError('Completa esta fase primero')
        if run['floor'] >= max(FLOORS):
            return {'end': end_run(state, s, completed=True)}
        run['floor'] += 1; enter_floor(run)
        return {}
    typ = run['type']
    if kind == 'pick_buff' and typ == 2 and not run['can_next']:
        i = request.get('index')
        if i is None:  # Give Up → Trial Tokens
            run['gold'] += GIVEUP_GOLD
        else:
            run['skills'][str(ex['skills'][int(i)])] = 1
        run['can_next'] = True
        return {}
    if kind == 'store' and typ == 3:
        i, mode = int(request.get('index', 0)), request.get('mode', 'buy')
        if mode == 'buy':
            if not 0 <= i < len(ex['buys']) or i in ex['bought']:
                raise ValueError('No disponible')
            b = BUFFS[ex['buys'][i]]; cost = pairs(b['cost'])[str(GOLD)]
            if run['gold'] < cost:
                raise ValueError('Faltan Trial Tokens')
            run['gold'] -= cost; run['skills'][str(b['id'])] = 1; ex['bought'].append(i)
        else:
            if not 0 <= i < len(ex['upgrades']):
                raise ValueError('No disponible')
            bid = str(ex['upgrades'][i]); lv = int(run['skills'].get(bid, 0))
            if lv < 1 or lv >= 3:
                raise ValueError('Reached Max Level!')
            cost = pairs(BUFFS[int(bid)][f'upgrade_{lv}'])[str(GOLD)]
            if run['gold'] < cost:
                raise ValueError('Faltan Trial Tokens')
            run['gold'] -= cost; run['skills'][bid] = lv + 1
            if lv + 1 == 3:
                ach_max(s, 10, 2)
        return {}
    if kind == 'recover' and typ == 4 and not run['can_next']:
        choice = int(request.get('choice', 1))
        ps = run['partners']
        if choice == 1:
            for v in ps.values():
                if v['hp'] > 0:
                    v['hp'] = min(100, v['hp'] + 30)
        elif choice == 2:
            alive = sorted([k for k, v in ps.items() if v['hp'] > 0], key=lambda k: ps[k]['hp'])[:3]
            for k in alive:
                ps[k]['hp'] = min(100, ps[k]['hp'] + 80)
        elif choice == 3:
            pid = str(request.get('partner_id'))
            if pid not in ps:
                raise ValueError('Elige una chica')
            ps[pid]['hp'] = 100
        else:
            raise ValueError('Opción no válida')
        run['can_next'] = True
        return {}
    if kind == 'fight' and typ in (1, 5):
        if typ == 1 and run['can_next']:
            raise ValueError('Ya has superado esta fase')
        team = request.get('team') or []
        pids = [str(t['partner_id']) for t in team]
        if not 1 <= len(team) <= 6 or len(set(pids)) != len(pids) or any(p not in run['partners'] for p in pids):
            raise ValueError('Equipo no válido')
        if any(run['partners'][p]['hp'] <= 0 for p in pids):
            raise ValueError('Esa chica está derrotada')
        lineup = sorted((p, int(t['pos'])) for p, t in zip(pids, team))
        if run['lineup'] and run['lineup'] != lineup:
            run['flags']['relineup'] = True
        run['lineup'] = lineup
        rows = [{**copy.deepcopy(run['frozen'][p]), 'pos': int(t['pos']), 'status': dict(run['partners'][p])} for p, t in zip(pids, team)]
        key = ex.get('battle') if typ == 1 else ex.get('boss')
        row = DATA['battles' if typ == 1 else 'bosses'][str(key)]
        report = fight(rows, int(row['battle_id']), god_skills(run), run['diff'])
        end = {int(x['pos']): x for x in report.get('end_status', [])}
        for p, t in zip(pids, team):
            st = end.get(int(t['pos']))
            if st:
                run['partners'][p] = {'hp': max(0, int(st['hp'])), 'mp': max(0, int(st['mp']))}
                if typ == 1 and st['hp'] <= 0:
                    run['flags']['dead'] = True
        result = {'battle': report, 'win': bool(report['isWin'])}
        if typ == 1:
            if report['isWin']:
                pts = int(row['score']) * int(DATA['diff'][str(run['diff'])]['score_ratio'])
                run['score'] += pts; run['gold'] += pairs(row['coin'])[str(GOLD)]
                run['can_next'] = True; s['season']['wins'] += 1
                result.update(points=pts, gold=pairs(row['coin'])[str(GOLD)])
            if all(v['hp'] <= 0 for v in run['partners'].values()):
                result['end'] = end_run(state, s, completed=False)
        else:
            dmg = int(report.get('total_harm') or sum(int(h.get('hurt', 0)) for h in report.get('hurts', []) if int(h.get('pos', 0)) <= 6))
            pts = boss_points(run['diff'], dmg)
            run['score'] += pts
            result.update(points=pts, damage=dmg, end=end_run(state, s, completed=True))
        return result
    raise ValueError('Acción del Santuario no disponible')


def plot_lines(text_id):
    out, seen, cur = [], set(), int(text_id)
    while cur and str(cur) in DATA['plot'] and cur not in seen and len(out) < 200:
        seen.add(cur)
        row = DATA['plot'][str(cur)]
        t = DATA['plot_text'].get(str(cur), {})
        out.append({'bg': row.get('image_path', ''), 'pic': row.get('res_path', ''), 'type': int(row.get('type', 1)),
                    'name': t.get('name', ''), 'text': t.get('dialog', ''), 'title': t.get('title', '')})
        cur = int(row.get('next_id') or 0)
    return out


def snapshot(state, now=None):
    now = int(time.time()) if now is None else now
    view = copy.deepcopy(state)
    floor, ten, ok = unlock_state(view)
    base = {'unlocked': ok, 'open_floor': OPEN_FLOOR, 'tower_floor': floor, 'has_ten_star': ten}
    if not ok:
        return base
    s = saved(view, now)
    n, start, fight_end, end = season_of(now)
    season = s['season']
    routes = []
    for r in sorted(ROUTES):
        env = route_env(r, n)
        maxd = max(1, int(s['max_diff'].get(str(r), 1)))
        routes.append({'id': r, 'name': route_name(r, n), 'env': [DATA['route_text'].get(str(e), {}) for e in env],
                       'best': int(season['scores'].get(str(r), 0)), 'max_diff': maxd, 'suggest': max(1, maxd - DIFF_FLOAT)})
    chapters = []
    for p in DATA['plots']:
        if p['text_id'] in ('', None):
            continue
        order = int(p['order'] or 0)
        chapters.append({'id': int(p['id']), 'title': DATA['plot_title'].get(str(p['id']), ''), 'tab': DATA['plot_tab'].get(str(p['tab2']), ''),
                         'text_id': int(p['text_id']), 'open': order <= int(s['completed'])})
    return {**base, 'season': n, 'fighting': now < fight_end, 'fight_end': fight_end, 'season_end': end,
            'tickets': int(view['items'].get(str(TICKET), 0)), 'ticket_buys_left': BUY_LIMIT - season['buys'], 'ticket_cost': BUY_COST,
            'cranes': int(view['items'].get(str(CRANE), 0)), 'total': season_total(season), 'routes': routes, 'run': run_view(view, s),
            'tasks': mission_rows(s), 'ach': ach_rows(s), 'prologue_seen': 1000 in s['plots'], 'chapters': chapters,
            'shop': {'season': [{**r, 'bought': int(season['shop'].get(f"2:{r['id']}", 0))} for r in DATA['shop2'] if int(r['type']) == 1],
                     'permanent': [{**r, 'shop': 1, 'bought': int(s['shop1'].get(f"1:{r['id']}", 0))} for r in DATA['shop1']] +
                                  [{**r, 'shop': 2, 'bought': int(s['shop1'].get(f"2:{r['id']}", 0))} for r in DATA['shop2'] if int(r['type']) == 2]},
            'buff_info': {str(b): {'name': DATA['buff_text'][str(b)]['name'], 'desc': DATA['buff_text'][str(b)]['desc'].replace('%%', '%'),
                                   'values': str(BUFFS[b]['value']).split('|'), 'image': BUFFS[b]['image'], 'cost': pairs(BUFFS[b]['cost'])[str(GOLD)],
                                   'up': [pairs(BUFFS[b]['upgrade_1'])[str(GOLD)], pairs(BUFFS[b]['upgrade_2'])[str(GOLD)]]} for b in BUFFS},
            'restore': DATA['restore_text'], 'giveup_gold': GIVEUP_GOLD, 'help': DATA['text'].get('SHRINE_HURDLE_HELP', ''),
            'last_reward': s.get('last_reward'),
            'brackets': [{'need': need, 'show': rank_row(row)['show'], 'awards': pairs(rank_row(row)['awards_0'])} for need, row in reversed(LOCAL_BRACKET)]}
