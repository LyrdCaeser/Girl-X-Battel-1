"""Sanctuary (models/Trial.lua, TrialWindow, ActivityNewTrialFightAwardWindow, NEW_TRIAL_HELP) offline.

Recovered from the client:
- 9 stages: Normal (1), Elite (2: choose a Blessing afterwards), Blessing (5: Fountain of Life / Healing Voice),
  Store (3: no fight, Sanctuary store) and Boss (4: rewards by damage dealt, new_trial_boss_reward by player-level band
  trial_boss_levs). Volcano Sanctum (boss 1, new_trial_stage) and Deep Sea Sanctum (boss 2, new_trial_stage_sea).
- Your own Girls fight; their HP is kept between stages (partner_status); a Girl at 0 HP can't fight this round.
  Blessings (new_trial_buff skill_ids) boost the rest of the round (god_skills). Battle type TRIAL_NEW (9).
- Weekly event; 1 Reset Chance each day at 00:00 UTC that doesn't stack. Unlock: function 18 (campaign ≥ 52).

LOCAL decisions (the server matched enemies from other players; DESIGN_DECISIONS.md LOCAL-032):
- Normal/Elite enemies mirror your 6 strongest Girls (level, grade, stars, gear) with the level scaled by
  (0.6 + stage power), i.e. 80–95 %. Their HP is kept while you stay on the stage.
- Elite offers 3 random Blessings from its buff list; the Blessing stage offers its 2. Normal stages give no Blessing
  (their buff lists are not explained by the client).
- Sanctums alternate every week (Monday 00:00 UTC). The boss can be fought while you have Girls standing; each
  damage tier reached pays its reward once per round.
"""
from __future__ import annotations
import copy, json, secrets, time
from . import clock
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/sanctuary.json').read_text())
STAGES = {int(k): {int(r['id']): r for r in rows} for k, rows in DATA['stages'].items()}
BUFFS = {int(r['id']): r for r in DATA['buffs']}
UNLOCK_STAGE = int(DATA['unlock']['open_value'])
WEEK = 7 * 86400
EPOCH_MONDAY = 345600  # 1970-01-05 00:00 UTC
BATTLE_TYPE = 9  # xyd.ReportBattleType.TRIAL_NEW
HEALS = {13: ('lowest', 3, 50), 14: ('revive', 1, 100)}


def ids(text):
    return [int(x) for x in str(text or '').split('|') if x]


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[k] = out.get(k, 0) + int(n)
    return out


def week(now):
    return clock.week_index(now)


def boss_of(now):
    return 1 + week(now) % 2


def day(now):
    return clock.day(now)


def band(level):
    levs = DATA['boss_levs']
    for i in range(len(levs) - 1):
        if level < levs[i]:
            return i + 1
    return len(levs)


def new_round(boss):
    return {'boss': boss, 'stage': 1, 'hp': {}, 'buffs': [], 'enemy': None, 'pending': None, 'damage': 0, 'tiers': 0}


def saved(state, now):
    s = state.get('sanctuary')
    if s is None or s.get('week') != week(now):
        s = state['sanctuary'] = {'week': week(now), 'reset_day': '', 'round': new_round(boss_of(now))}
    return s


def reset_ready(s, now):
    return s['reset_day'] != day(now)


def strongest(state, n=6):
    return sorted(state['partners'], key=lambda p: (-int(p.get('lv', 1)), -int(p.get('awake', 0)), -int(p.get('grade', 0))))[:n]


def make_enemy(state, stage_row):
    """Mirror of the player's strongest Girls, level × (0.6 + power)."""
    f = 0.6 + float(stage_row['power'] or 0.2)
    team = []
    for i, p in enumerate(strongest(state)):
        team.append({'partner_id': 2000 + i, 'table_id': p['table_id'], 'lv': max(1, round(int(p['lv']) * f)), 'grade': int(p.get('grade', 0)),
                     'awake': int(p.get('awake', 0)), 'equips': copy.deepcopy(p.get('equips', [])), 'pos': i + 1, 'show_skin': 1,
                     'status': {'hp': 100, 'mp': 50}})
    return team


def god_skills(r):
    return [s for b in r['buffs'] for s in ids(BUFFS[b]['skill_ids'])]


def apply_heal(r, state, buff):
    kind, n, pct = HEALS[buff]
    owned = [p['partner_id'] for p in state['partners']]
    hp = {pid: int(r['hp'].get(str(pid), 100)) for pid in owned}
    if kind == 'revive':
        dead = [pid for pid, v in hp.items() if v <= 0]
        target = dead[0] if dead else min(hp, key=hp.get)
        r['hp'][str(target)] = 100
    else:
        used = [pid for pid in hp if str(pid) in r['hp']] or list(hp)
        for pid in sorted(used, key=lambda x: hp[x])[:n]:
            if hp[pid] > 0:
                r['hp'][str(pid)] = min(100, hp[pid] + pct)


def items_of(state):
    return state.get('items', {})


def snapshot(state, now=None):
    from .engine import TABLES
    now = int(time.time()) if now is None else now
    view = copy.deepcopy(state)
    s = saved(view, now)
    r = s['round']
    rows = STAGES[r['boss']]
    cur = rows.get(r['stage'])
    scene = next(x for x in DATA['boss_scenes'] if int(x['id']) == r['boss'])
    enemy = []
    for e in (r['enemy'] or []):
        enemy.append({'table_id': e['table_id'], 'lv': e['lv'], 'hp': int(e['status']['hp']), 'name': TABLES['names'].get(str(e['table_id']), '')})
    level = int(view.get('level') or 1)
    try:
        from .engine import player_level
        level = player_level(view)
    except Exception:
        pass
    tiers = [{'damage': int(t['damage_to_boss']), 'rewards': pairs(t[f'rewards_{band(level)}'])} for t in DATA['boss_reward']]
    start = clock.week_start(week(now))
    return {'unlocked': int(state.get('max_stage', 0)) >= UNLOCK_STAGE, 'unlock_stage': UNLOCK_STAGE, 'boss': r['boss'],
            'sanctum': DATA['text'].get('NEW_TRIAL_VOLCAN_SECRET' if r['boss'] == 1 else 'NEW_TRIAL_SEA_SECRET', ''),
            'scene': scene['stage_scene'], 'boss_image': scene['boss_image'], 'boss_name': TABLES['names'].get(str(scene['partner_id']), ''),
            'week_end': clock.week_start(week(now) + 1), 'reset_ready': reset_ready(s, now), 'stage': r['stage'],
            'stages': [{'id': k, 'type': int(v['type']), 'rewards': pairs(v['rewards']), 'buffs': ids(v['buff_id'])} for k, v in sorted(rows.items())],
            'current_type': int(cur['type']) if cur else 0, 'done': r['stage'] > max(rows),
            'hp': {k: int(v) for k, v in r['hp'].items()}, 'buffs': r['buffs'], 'enemy': enemy, 'pending': r['pending'],
            'damage': int(r['damage']), 'tiers_paid': int(r['tiers']), 'tiers': tiers,
            'buff_info': {str(k): {**DATA['buff_text'].get(str(k), {}), 'icon': v['icon']} for k, v in BUFFS.items()},
            'nodes': [{'x': float(o['offsetX']), 'y': float(o['offsetY']), 'stage': int(o['type']), 'belong': int(o['stage_belong']) or int(o['type'])}
                      for o in DATA['offsets'] if int(o['boss_id']) == r['boss']], 'coins': int(items_of(view).get('15', 0))}


def action(state, request, level=1, now=None, rng=secrets.randbelow, fight=None):
    """fight(team_a_rows, team_b, battle_id, god_skills) -> report (TRIAL_NEW, statuses applied)."""
    now = int(time.time()) if now is None else now
    if int(state.get('max_stage', 0)) < UNLOCK_STAGE:
        raise ValueError(f'Sanctuary se desbloquea al superar la fase {UNLOCK_STAGE} de la campaña')
    s = saved(state, now)
    r = s['round']
    rows = STAGES[r['boss']]
    items = state['items']
    kind = request.get('action')
    result = {}
    if kind == 'open':
        return result
    if kind == 'reset':
        if not reset_ready(s, now):
            raise ValueError('Cannot Reset: la oportunidad de hoy ya se usó (vuelve a medianoche, hora local)')
        s['reset_day'] = day(now)
        s['round'] = new_round(boss_of(now))
        return result
    if kind == 'pick':
        if not r['pending']:
            raise ValueError('No hay bendición por elegir')
        i = int(request.get('index', -1))
        if not 0 <= i < len(r['pending']):
            raise ValueError('Please choose a blessing!')
        b = r['pending'][i]
        if b in HEALS:
            apply_heal(r, state, b)
        else:
            r['buffs'].append(b)
        r['pending'] = None
        r['stage'] += 1
        result['picked'] = b
        return result
    row = rows.get(r['stage'])
    if row is None:
        raise ValueError('Ronda terminada: reinicia o espera a la próxima semana')
    if r['pending']:
        raise ValueError('Please choose a blessing!')
    typ = int(row['type'])
    if kind == 'continue':
        if typ == 3:
            r['stage'] += 1
        elif typ == 5:
            r['pending'] = ids(row['buff_id'])
        else:
            raise ValueError('Esta fase se supera luchando')
        return result
    if kind != 'fight':
        raise ValueError('Acción de Sanctuary no disponible')
    if typ not in (1, 2, 4):
        raise ValueError('En esta fase no se lucha')
    owned = {p['partner_id']: p for p in state['partners']}
    team = request.get('team') or []
    if not 1 <= len(team) <= 6:
        raise ValueError('Elige entre 1 y 6 chicas')
    rows_a = []
    for t in team:
        pid, pos = int(t['partner_id']), int(t['pos'])
        if pid not in owned or not 1 <= pos <= 6:
            raise ValueError('Chica no disponible')
        hp = int(r['hp'].get(str(pid), 100))
        if hp <= 0:
            raise ValueError('Esa chica no tiene HP en esta ronda')
        rows_a.append({**copy.deepcopy(owned[pid]), 'pos': pos, 'status': {'hp': hp, 'mp': int(r['hp'].get(f'mp{pid}', 50))}})
    if len({x['pos'] for x in rows_a}) != len(rows_a) or len({x['partner_id'] for x in rows_a}) != len(rows_a):
        raise ValueError('Formación no válida')
    if typ == 4:
        team_b = None
        battle_id = int(row['battle_id'])
    else:
        if not r['enemy']:
            r['enemy'] = make_enemy(state, row)
        team_b = r['enemy']
        battle_id = 0  # engine: neutral battle row, sanctum map
    report = fight(rows_a, team_b, battle_id, god_skills(r))
    if int(r['stage'])==9:
        from . import growth_diary
        growth_diary.record(state,'growth_sanctuary9')
    end = {int(x['pos']): x for x in report.get('end_status', [])}
    for x in rows_a:
        st = end.get(int(x['pos']))
        if st:
            r['hp'][str(x['partner_id'])] = max(0, int(st['hp'])); r['hp'][f"mp{x['partner_id']}"] = max(0, int(st['mp']))
    win = bool(report['isWin'])
    result.update(win=win, stage=r['stage'], battle=report)
    if typ == 4:
        dealt = sum(int(h.get('hurt', 0)) for h in report.get('hurts', []) if int(h.get('pos', 0)) <= 6)
        r['damage'] = int(r['damage']) + dealt
        got = {}
        tiers = DATA['boss_reward']
        while int(r['tiers']) < len(tiers) and r['damage'] >= int(tiers[int(r['tiers'])]['damage_to_boss']):
            for k, n in pairs(tiers[int(r['tiers'])][f'rewards_{band(level)}']).items():
                got[k] = got.get(k, 0) + n
            r['tiers'] = int(r['tiers']) + 1
        for k, n in got.items():
            items[k] = int(items.get(k, 0)) + n
        result.update(damage=dealt, total_damage=r['damage'], got=got)
        # Boss bar of the battle window (captura 3): accumulated damage vs the next reward tier.
        report['boss_bar'] = {'before': int(r['damage']) - dealt, 'dealt': dealt, 'tiers': [int(t['damage_to_boss']) for t in tiers]}
        return result
    if not win:
        for e in r['enemy']:
            st = end.get(int(e['pos']) + 6)
            if st:
                e['status'] = {'hp': max(0, int(st['hp'])), 'mp': max(0, int(st['mp']))}
        return result
    got = pairs(row['rewards'])
    for k, n in got.items():
        items[k] = int(items.get(k, 0)) + n
    result['got'] = got
    r['enemy'] = None
    if typ == 2:
        pool = [b for b in ids(row['buff_id']) if b not in r['buffs']]
        opts = []
        while pool and len(opts) < 3:
            opts.append(pool.pop(rng(len(pool))))
        r['pending'] = opts or None
        if not opts:
            r['stage'] += 1
    else:
        r['stage'] += 1
    return result
