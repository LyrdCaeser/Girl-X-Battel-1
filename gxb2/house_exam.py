"""House Exam (models/AcademyAssessment.lua + AcademyAssessmentWindow / DetailWindow2 / SweepWindow) offline.

Recovered from the client (tables + ACADEMY_ASSESSMENT_WINDOW_HELP_NEW_2):
- 6 houses (fort 1-6 = Ghost, Human, Monster, Fairy, Demon, Angel), only Girls of that faction (partner group = fort)
  can fight; 100 stages each (school_practise_new2). Unlock: function 35 (open_type 2 = campaign stage ≥ 137).
- Seasons of 14 days from school_practise_season1_start_time: 13 exam days + 1 result display day. The enemies
  change each season: battle_id{(season - 1) % 3 + 1} (AcademyAssessmentWindow).
- Fighting the next stage costs 1 Admission Ticket (item 64). Admission Tickets refresh to 25 each day (unless you
  have more) at 00:00 UTC; extra tickets cost 25 gems (school_practise_ticket02_buy).
- Passing a stage: first_reward the first time ever (kept across seasons), non_first_reward afterwards, and the
  stage's point_reward as Exam Score. Passed stages can be Raided with a Certificate (item 63) for sweep_reward,
  always successful.
- Certificates refresh to 2 each day, +1 each after passing stage 9/18/30 of any house (and +1 that same day); up
  to 10 extra per day at the rising school_practise_ticket_buy prices.
- On the display day progress resets and the season score gives the school_practise_point_new2 reward (item 173).

LOCAL decisions (DESIGN_DECISIONS.md LOCAL-029):
- The season reward (sent by mail in the original) is paid automatically the first time the game is opened after
  the season's exam period ends. The per-house frame for the server's top scorer is not granted (no ranking offline).
- Seasons before the first one the save saw count from that point; older seasons are not paid retroactively.
- Tickets are consumed when the fight starts (win or lose), as the captures show.
"""
from __future__ import annotations
import json, time
from . import clock
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/house_exam.json').read_text())
M = DATA['misc']
STAGES = {int(r['id']): r for r in DATA['stages']}
FORTS = {f: [r for r in DATA['stages'] if int(r['fort_id']) == f] for f in range(1, 7)}
FIRST = {f: int(rows[0]['id']) for f, rows in FORTS.items()}
UNLOCK_STAGE = int(DATA['unlock']['open_value'])
SEASON1 = int(M['school_practise_season1_start_time'])
SEASON = int(M['school_practise_season_duration'])
DISPLAY = int(M['school_practise_display_duration'])
TICKET, CERT = '64', '63'
TICKET_DAILY = int(M['school_practise_ticket02_default_2'])
TICKET_COST = M['school_practise_ticket02_buy']
CERT_BASE = int(M['school_practise_ticket_default'])
CERT_STEPS = [int(x) for x in str(M['school_practise_ticket_limit_up']).split('|')]
CERT_BUY_LIMIT = int(M['school_practise_ticket_buy_limit'])
HOUSES = ['Ghost', 'Human', 'Monster', 'Fairy', 'Demon', 'Angel']


def pairs(text, times=1):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[k] = out.get(k, 0) + int(float(n)) * times
    return out


def add(items, got):
    for k, n in got.items():
        items[k] = int(items.get(k, 0)) + n


def season_of(now):
    """(season number, season start, exam end, season end). Season 1 starts at school_practise_season1_start_time."""
    n = max(0, (now - SEASON1) // SEASON) + 1
    start = SEASON1 + (n - 1) * SEASON
    return n, start, start + SEASON - DISPLAY, start + SEASON


def utc_day(now):   # name kept; the day is the player's local day (LOCAL-058)
    return clock.day(now)


def sort_of(stage_id):
    return int(STAGES[stage_id]['school_sort'])


def season_award(score):
    for r in DATA['points']:
        if score >= int(r['point']):
            return pairs(r['award'])
    return {}


def cert_level(h):
    """Daily Certificate amount: 2 + 1 per stage 9/18/30 passed in any house (best historical stage)."""
    best = max([sort_of(s) for s in h['max'].values() if s] or [0])
    return CERT_BASE + sum(1 for step in CERT_STEPS if best >= step)


def saved(state, now):
    items = state.setdefault('items', {})
    h = state.get('house_exam')
    n, start, exam_end, _ = season_of(now)
    if h is None:
        h = state['house_exam'] = {'season': n, 'current': {str(f): FIRST[f] for f in FORTS}, 'max': {str(f): 0 for f in FORTS},
                                   'first_done': [], 'score': 0, 'history_score': 0, 'day': '', 'cert_bought': 0, 'formations': {},
                                   'last_award': None}
        items.setdefault(TICKET, 0); items.setdefault(CERT, 0)
    if h['season'] != n:
        # Result day passed: pay the finished season's score and reset the progress (max/first_done are kept).
        got = season_award(int(h['score']))
        add(items, got)
        h['last_award'] = {'season': h['season'], 'score': int(h['score']), 'got': got}
        h['history_score'] = max(int(h.get('history_score', 0)), int(h['score']))
        h.update(season=n, score=0, current={str(f): FIRST[f] for f in FORTS})
    if h['day'] != utc_day(now):
        h['day'] = utc_day(now)
        items[TICKET] = max(int(items.get(TICKET, 0)), TICKET_DAILY)
        items[CERT] = cert_level(h)
        h['cert_bought'] = 0
    return h


def exam_open(now):
    n, start, exam_end, _ = season_of(now)
    return start <= now < exam_end


def variant(season):
    return (season - 1) % 3 + 1


def battle_id(stage_id, season):
    return int(STAGES[stage_id][f'battle_id{variant(season)}'])


def passed(h, fort, stage_id):
    cur = int(h['current'][str(fort)])
    return cur == -1 or cur > stage_id


def snapshot(state, now=None):
    now = int(time.time()) if now is None else now
    import copy
    view = copy.deepcopy(state)  # read-only: the daily refresh / season change is only persisted by an action
    h = saved(view, now)
    items = view['items']
    n, start, exam_end, end = season_of(now)
    forts = []
    for f, rows in FORTS.items():
        cur = int(h['current'][str(f)])
        done = len(rows) if cur == -1 else sort_of(cur) - 1
        forts.append({'fort': f, 'name': HOUSES[f - 1], 'current': cur, 'done': done, 'total': len(rows),
                      'max': sort_of(h['max'][str(f)]) if h['max'][str(f)] else 0,
                      'formation': h['formations'].get(str(f), [])})
    cert_i = int(h['cert_bought'])
    return {'unlocked': int(state.get('max_stage', 0)) >= UNLOCK_STAGE, 'unlock_stage': UNLOCK_STAGE, 'open': exam_open(now),
            'season': n, 'variant': variant(n), 'season_start': start, 'exam_end': exam_end, 'season_end': end,
            'tickets': int(items.get(TICKET, 0)), 'certs': int(items.get(CERT, 0)), 'ticket_cost': pairs(TICKET_COST),
            'cert_cost': pairs(DATA['cert_cost'][cert_i]) if cert_i < CERT_BUY_LIMIT else None, 'cert_left': CERT_BUY_LIMIT - cert_i,
            'score': int(h['score']), 'history_score': int(h.get('history_score', 0)), 'season_award': season_award(int(h['score'])),
            'first_done': h['first_done'], 'forts': forts, 'last_award': h.get('last_award')}


def check_team(state, fort, team):
    owned = {x['partner_id']: x for x in state['partners']}
    from .engine import TABLES
    if not 1 <= len(team) <= 6:
        raise ValueError('Elige entre 1 y 6 chicas')
    ids = [int(t['partner_id']) for t in team]
    poss = [int(t['pos']) for t in team]
    if len(set(ids)) != len(ids) or len(set(poss)) != len(poss) or any(not 1 <= p <= 6 for p in poss):
        raise ValueError('Formación no válida')
    for i in ids:
        if i not in owned:
            raise ValueError('Chica no disponible')
        if int(TABLES['partner'][str(owned[i]['table_id'])]['group']) != fort:
            raise ValueError(f'En la casa {HOUSES[fort - 1]} solo pueden luchar chicas de esa facción')
    return [{'partner_id': i, 'pos': p} for i, p in zip(ids, poss)]


def action(state, request, now=None, fight=None):
    """fight(team, battle_id) -> report (original engine with the house's enemy lineup of this season)."""
    now = int(time.time()) if now is None else now
    if int(state.get('max_stage', 0)) < UNLOCK_STAGE:
        raise ValueError(f'House Exam se desbloquea al superar la fase {UNLOCK_STAGE} de la campaña')
    h = saved(state, now)
    items = state['items']
    kind = request.get('action')
    result = {}
    if kind == 'open':
        return result
    if kind == 'formation':
        fort = int(request.get('fort', 0))
        if fort not in FORTS:
            raise ValueError('Casa no válida')
        h['formations'][str(fort)] = check_team(state, fort, request.get('team') or [])
        return result
    if kind == 'buy_tickets':
        n = max(1, int(request.get('count', 1)))
        cost = pairs(TICKET_COST, n)
        if int(items.get('2', 0)) < cost.get('2', 0):
            raise ValueError('Faltan gemas')
        items['2'] = int(items['2']) - cost.get('2', 0); items[TICKET] = int(items.get(TICKET, 0)) + n
        return result
    if kind == 'buy_certs':
        n = max(1, int(request.get('count', 1)))
        if int(h['cert_bought']) + n > CERT_BUY_LIMIT:
            raise ValueError(f'Solo puedes comprar {CERT_BUY_LIMIT} certificados al día')
        cost = {}
        for i in range(int(h['cert_bought']), int(h['cert_bought']) + n):
            for k, v in pairs(DATA['cert_cost'][i]).items():
                cost[k] = cost.get(k, 0) + v
        if int(items.get('2', 0)) < cost.get('2', 0):
            raise ValueError('Faltan gemas')
        items['2'] = int(items['2']) - cost.get('2', 0); items[CERT] = int(items.get(CERT, 0)) + n
        h['cert_bought'] = int(h['cert_bought']) + n
        result['cost'] = cost
        return result
    if kind == 'enemies':
        # AcademyAssessmentEnemyDetailWindow: the lineup of this season's battle for a stage.
        from .engine import TABLES
        stage = int(request.get('stage', 0))
        if stage not in STAGES:
            raise ValueError('Fase no válida')
        b = TABLES['battle'][str(battle_id(stage, h['season']))]
        out = []
        for t, q in zip(str(b['monsters']).split('|'), str(b['stands']).split('|')):
            m = TABLES['monster'][t]
            link = int(m['partner_link'])
            out.append({'table_id': link, 'pos': int(q), 'lv': int(m.get('lv_show') or m['lv']), 'name': TABLES['names'].get(str(link), str(link))})
        result.update(stage=stage, enemies=out, power=int(STAGES[stage]['power']))
        return result
    if not exam_open(now):
        raise ValueError('Exam is over — día de resultados; la nueva temporada empieza pronto')
    stage = int(request.get('stage', 0))
    if stage not in STAGES:
        raise ValueError('Fase no válida')
    fort = int(STAGES[stage]['fort_id'])
    if kind == 'fight':
        if int(h['current'][str(fort)]) != stage:
            raise ValueError('Solo puedes luchar en la siguiente fase de esta casa')
        team = check_team(state, fort, request.get('team') or h['formations'].get(str(fort)) or [])
        h['formations'][str(fort)] = team
        if int(items.get(TICKET, 0)) < 1:
            raise ValueError('Not Enough Admission Tickets')
        items[TICKET] = int(items[TICKET]) - 1
        report = fight(team, battle_id(stage, h['season']))
        win = bool(report['isWin'])
        result.update(win=win, stage=stage, battle=report)
        if win:
            row = STAGES[stage]
            first = stage not in h['first_done']
            got = pairs(row['first_reward'] if first else row['non_first_reward'])
            add(items, got)
            if first:
                h['first_done'].append(stage)
            before = cert_level(h)
            h['max'][str(fort)] = max(int(h['max'][str(fort)]), stage)
            if cert_level(h) > before:
                items[CERT] = int(items.get(CERT, 0)) + 1  # +1 Certificate on the day a new step is reached
                result['cert_up'] = cert_level(h)
            h['score'] = int(h['score']) + int(row['point_reward'])
            nxt = int(row['next_id'])
            h['current'][str(fort)] = nxt if nxt in STAGES else -1
            result.update(got=got, first=first, points=int(row['point_reward']))
    elif kind == 'sweep':
        times = max(1, int(request.get('times', 1)))
        if not passed(h, fort, stage):
            raise ValueError('Solo puedes hacer Raid en fases superadas esta temporada')
        if int(items.get(CERT, 0)) < times:
            raise ValueError('Not Enough Certificates')
        items[CERT] = int(items[CERT]) - times
        got = pairs(STAGES[stage]['sweep_reward'], times)
        add(items, got)
        result.update(got=got, times=times)
    else:
        raise ValueError('Acción de House Exam no disponible')
    return result
