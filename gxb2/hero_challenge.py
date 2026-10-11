"""Character Challenge, Normal and Puzzle modes (models/HeroChallenge.lua, HeroChallengeWindow,
HeroChallengeFightAwardWindow, HERO_CHALLENGE_DETAIL_WINDOW_HELP) offline.

Recovered from the client:
- 12 forts × 10 stages (partner_challenge). Forts 1-4 and 7-12 are Normal, 5-6 are Puzzle (partner_challenge_type).
  Unlock: function 31 (campaign stage ≥ 102).
- Only the challenge's own Girls fight: fixed-attribute monsters (initial_partner of the fort's first stage, then the
  ones won). Blessings (partner_challenge_buff) enter the battle as god_skills; Servants are pets 101…601 at level 90,
  max grade and skills 30/30/30/30 (challenge_pet_*).
- Challenge Coupons (item 55): start with 10, +1 every 1800 s while below 10. Losing costs 1 Coupon and, in Normal
  mode, the Girls of the lost lineup can't be used again in this run. Passed stages can be replayed with no reward or
  loss. Reset (Normal only) costs 1 Coupon and removes the Girls, buffs and Servants won.
- Puzzle mode: each stage has its fixed Girls (initial_partner of that stage); losing keeps them; no reset.
- First pass of a stage: reward1 items; reward2 "type#n" = n choices of a Girl (1), a Blessing (2) or a Servant (3).

LOCAL decisions (the server generated the choices; DESIGN_DECISIONS.md LOCAL-031):
- Each choice offers 3 candidates: Girls weighted from the stage's partner_challenge_box (without Girls already in the
  run), Blessings and Servants not owned yet. A choice must be taken before the next fight.
- reward1 is paid once per stage ever; the choices are given each run (they rebuild the team after a reset).
- A win does not spend a Coupon (the help text only charges losses); every fight needs at least 1 Coupon.
"""
from __future__ import annotations
import json, secrets, time
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/hero_challenge.json').read_text())
M = DATA['misc']
STAGES = {int(r['id']): r for r in DATA['stages']}
FORTS: dict[int, list] = {}
for _r in DATA['stages']:
    FORTS.setdefault(int(_r['fort_id']), []).append(_r)
PUZZLE = {int(f) for f in str(DATA['types']['2']['fort']).split('|') if f}
FIRST = {f: int(rows[0]['id']) for f, rows in FORTS.items()}
BOX: dict[int, list] = {}
for _r in DATA['boxes']:
    BOX.setdefault(int(_r['box_id']), []).append(_r)
BUFFS = {int(r['id']): r for r in DATA['buffs']}
PETS = {int(k): v for k, v in DATA['pets'].items()}
_SERV = json.loads((Path(__file__).resolve().parents[1] / 'data/servants.json').read_text())['pets']
COUPON = '55'
CAP = int(M['challenge_voucher_max'])
CD = int(M['challenge_voucher_cd'])
UNLOCK_STAGE = int(DATA['unlock']['open_value'])
PET_LV = int(M['challenge_pet_lv'])
PET_SKILLS = [int(x) for x in str(M['challenge_pet_skill']).split('|')]
CHOICES = 3


def ids(text):
    return [int(x) for x in str(text or '').split('|') if x]


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[k] = out.get(k, 0) + int(n)
    return out


def new_run(fort):
    girls = ids(STAGES[FIRST[fort]]['initial_partner'])
    return {'current': FIRST[fort], 'live': [{'uid': i + 1, 'table_id': t} for i, t in enumerate(girls)], 'dead': [],
            'pets': [], 'buffs': [], 'pending': [], 'next_uid': len(girls) + 1, 'team': [], 'pet': 0}


def saved(state, now):
    items = state.setdefault('items', {})
    h = state.get('hero_challenge')
    if h is None:
        h = state['hero_challenge'] = {'forts': {str(f): new_run(f) for f in FORTS}, 'first_done': [], 'coupon_at': now}
        items[COUPON] = max(int(items.get(COUPON, 0)), int(pairs(M['challenge_voucher_init']).get(COUPON, CAP)))
    # Coupon regeneration: +1 every CD seconds while below the cap.
    have = int(items.get(COUPON, 0))
    if have >= CAP:
        h['coupon_at'] = now
    else:
        n = (now - int(h['coupon_at'])) // CD
        if n > 0:
            add = min(n, CAP - have)
            items[COUPON] = have + add
            h['coupon_at'] = now if have + add >= CAP else int(h['coupon_at']) + n * CD
    return h


def weighted(options, rng):
    total = sum(int(o['weight']) for o in options)
    x = rng(total)
    for o in options:
        x -= int(o['weight'])
        if x < 0:
            return o
    return options[-1]


def candidates(run, stage, kind, rng):
    if kind == 1:
        owned = {g['table_id'] for g in run['live'] + run['dead']} | {o for p in run['pending'] if p['kind'] == 1 for o in p['options']}
        pool = [b for b in BOX.get(int(STAGES[stage]['box_id']), []) if int(b['monster_id']) not in owned]
        out = []
        while pool and len(out) < CHOICES:
            b = weighted(pool, rng)
            out.append(int(b['monster_id']))
            pool = [x for x in pool if x is not b]
        return out
    pool = sorted(set(BUFFS) - set(run['buffs'])) if kind == 2 else sorted(set(PETS) - set(run['pets']))
    out = []
    while pool and len(out) < CHOICES:
        out.append(pool.pop(rng(len(pool))))
    return out


def pet_params(pet_id):
    return {'pet_id': pet_id, 'grade': PETS[pet_id]['max_grade'], 'lv': PET_LV, 'skills': PET_SKILLS, 'ex_lv': 0}


def puzzle_girls(stage):
    return [{'uid': 1000 + i, 'table_id': t} for i, t in enumerate(ids(STAGES[stage]['initial_partner']))]


def snapshot(state, now=None):
    import copy
    from .engine import TABLES
    now = int(time.time()) if now is None else now
    view = copy.deepcopy(state)
    h = saved(view, now)
    items = view['items']

    def girl(g):
        m = TABLES['monster'].get(str(g['table_id']), {})
        link = int(m.get('partner_link') or 0)
        return {'uid': g['uid'], 'table_id': g['table_id'], 'show_id': link, 'name': TABLES['names'].get(str(link), str(link)),
                'lv': int(m.get('lv_show') or m.get('lv') or 1), 'group': int(TABLES['partner'].get(str(link), {}).get('group') or 0)}
    forts = []
    for f, rows in sorted(FORTS.items()):
        run = h['forts'][str(f)]
        cur = int(run['current'])
        done = len(rows) if cur == -1 else sum(1 for r in rows if int(r['id']) < cur)
        txt = DATA['stage_text'].get(str(rows[0]['id']), {})
        live = puzzle_girls(cur) if f in PUZZLE and cur != -1 else run['live']
        forts.append({'fort': f, 'puzzle': f in PUZZLE, 'name': txt.get('fort', f'Challenge {f}'), 'img': rows[0]['fort_img'],
                      'icon': rows[0]['chapter_icon'], 'current': cur, 'done': done, 'total': len(rows),
                      'live': [girl(g) for g in live], 'dead': [girl(g) for g in run['dead']], 'pets': run['pets'], 'buffs': run['buffs'],
                      'pending': [{**p, 'girls': [girl({'uid': 0, 'table_id': o}) for o in p['options']] if p['kind'] == 1 else []} for p in run['pending'][:1]], 'team': run['team'], 'pet': run['pet'],
                      'stages': [{'id': int(r['id']), 'name': DATA['stage_text'].get(str(r['id']), {}).get('name', ''),
                                  'desc': DATA['stage_text'].get(str(r['id']), {}).get('desc', ''), 'reward1': pairs(r['reward1']),
                                  'reward2': r['reward2'], 'first': int(r['id']) not in h['first_done']} for r in rows]})
    have = int(items.get(COUPON, 0))
    return {'unlocked': int(state.get('max_stage', 0)) >= UNLOCK_STAGE, 'unlock_stage': UNLOCK_STAGE, 'coupons': have, 'cap': CAP,
            'next_coupon': 0 if have >= CAP else int(h['coupon_at']) + CD, 'forts': forts,
            'buff_info': {str(k): {**DATA['buff_text'].get(str(k), {}), 'icon': v['fx']} for k, v in BUFFS.items()},
            'pet_info': {str(k): {**v, 'name': _SERV.get(str(k), {}).get('name', str(k)), 'avatar': _SERV.get(str(k), {}).get('avatar', '') + str(v['max_grade'])} for k, v in PETS.items()}, 'help': DATA['text'].get('HERO_CHALLENGE_DETAIL_WINDOW_HELP', '')}


def action(state, request, now=None, rng=secrets.randbelow, fight=None):
    """fight(team_rows, battle_id, pet_params|None, god_skills) -> report."""
    now = int(time.time()) if now is None else now
    if int(state.get('max_stage', 0)) < UNLOCK_STAGE:
        raise ValueError(f'Character Challenge se desbloquea al superar la fase {UNLOCK_STAGE} de la campaña')
    h = saved(state, now)
    items = state['items']
    kind = request.get('action')
    fort = int(request.get('fort', 0))
    if kind == 'open':
        return {}
    if fort not in FORTS:
        raise ValueError('Desafío no válido')
    run = h['forts'][str(fort)]
    result = {}
    if kind == 'pick':
        if not run['pending']:
            raise ValueError('No hay recompensa por elegir')
        p = run['pending'][0]
        i = int(request.get('index', -1))
        if not 0 <= i < len(p['options']):
            raise ValueError('Please choose your reward')
        choice = p['options'][i]
        if p['kind'] == 1:
            run['live'].append({'uid': run['next_uid'], 'table_id': choice}); run['next_uid'] += 1
        elif p['kind'] == 2:
            run['buffs'].append(choice)
        else:
            run['pets'].append(choice)
        run['pending'].pop(0)
        result['picked'] = {'kind': p['kind'], 'id': choice}
    elif kind == 'reset':
        if fort in PUZZLE:
            raise ValueError('El modo Puzzle no se puede reiniciar')
        if int(run['current']) == FIRST[fort] and not run['dead'] and not run['pending']:
            raise ValueError("Don't need to reset")
        cost = int(pairs(M['challenge_reset_cost']).get(COUPON, 1))
        if int(items.get(COUPON, 0)) < cost:
            raise ValueError('Not enough Challenge Coupons')
        items[COUPON] = int(items[COUPON]) - cost
        h['forts'][str(fort)] = new_run(fort)
    elif kind == 'fight':
        stage = int(request.get('stage', 0))
        if stage not in STAGES or int(STAGES[stage]['fort_id']) != fort:
            raise ValueError('Fase no válida')
        if run['pending']:
            raise ValueError('Please choose your reward')
        cur = int(run['current'])
        replay = cur == -1 or stage < cur
        if not replay and stage != cur:
            raise ValueError('Esa fase aún está bloqueada')
        if int(items.get(COUPON, 0)) < 1:
            raise ValueError('Not enough Challenge Coupons')
        pool = {g['uid']: g for g in (puzzle_girls(stage) if fort in PUZZLE else run['live'])}
        team = request.get('team') or []
        if not 1 <= len(team) <= 6:
            raise ValueError('Elige entre 1 y 6 chicas del desafío')
        rows = []
        for t in team:
            uid, pos = int(t['uid']), int(t['pos'])
            if uid not in pool or not 1 <= pos <= 6:
                raise ValueError('Esa chica no está disponible en este desafío')
            rows.append({'table_id': pool[uid]['table_id'], 'pos': pos, 'uid': uid})
        if len({r['pos'] for r in rows}) != len(rows) or len({r['uid'] for r in rows}) != len(rows):
            raise ValueError('Formación no válida')
        pet = int(request.get('pet', 0) or 0)
        if pet and pet not in run['pets']:
            raise ValueError('Servant no disponible')
        run['team'] = [{'uid': r['uid'], 'pos': r['pos']} for r in rows]; run['pet'] = pet
        gods = [int(s) for b in run['buffs'] for s in ids(BUFFS[b]['skill'])]
        report = fight(rows, int(STAGES[stage]['battle_id']), pet_params(pet) if pet else None, gods)
        win = bool(report['isWin'])
        result.update(win=win, stage=stage, replay=replay, battle=report)
        if replay:
            return result
        if not win:
            items[COUPON] = int(items[COUPON]) - 1
            if fort not in PUZZLE:
                lost = {r['uid'] for r in rows}
                run['dead'] += [g for g in run['live'] if g['uid'] in lost]
                run['live'] = [g for g in run['live'] if g['uid'] not in lost]
                run['team'] = []
            result['coupon_spent'] = 1
            return result
        row = STAGES[stage]
        if stage not in h['first_done']:
            got = pairs(row['reward1'])
            for k, n in got.items():
                items[k] = int(items.get(k, 0)) + n
            h['first_done'].append(stage)
            result['got'] = got
        for part in str(row['reward2'] or '').split('|'):
            if '#' in part:
                k, n = (int(x) for x in part.split('#')[:2])
                for _ in range(n):
                    opts = candidates(run, stage, k, rng)
                    if opts:
                        run['pending'].append({'kind': k, 'options': opts})
        nxt = int(row['next_id'])
        run['current'] = nxt if nxt in STAGES else -1
        result['picks'] = len(run['pending'])
    else:
        raise ValueError('Acción de Character Challenge no disponible')
    return result
