"""Echoes of Time (models/TimeCloisterModel.lua, TIME_CLOISTER_HELP01-05) offline.

Recovered from the client:
- Worlds of Time (time_cloister 1-3: Skyless Shrine, Nephrite Stairways, Glimmering Stream). World 1 is open; the next
  one unlocks when the Observation Progress (achievement steps reached) of the previous one reaches 85 %.
- Observation: send up to 6 Girls. Clockwork of Memory = time_cloister.energy + "Observation Length" technologies;
  1 is consumed every 360 s and a card is triggered every 300 s of reading, drawn from the world's card boxes
  (card_box/weights, then box weights). Time Essence (287) speeds up 600 s each. It ends when the Clockwork runs out or
  manually; the rewards are claimed at the end.
- Cards: Supply (awards at the end; "Supply" technologies raise the card level), Challenge (enemy Courage/Charisma/
  Knowledge `base`; win and lose sub-cards give different rewards), Encounter (no instant effect; "Points" cards add
  points; they count for achievements). Locked cards (lock 2) need their technology. Each card's `point` adds to the
  Observation grade, which pays the world's Time Shards (time_cloister_award).
- Planetarium: technologies with costs per level, prerequisites (pre_id/pre_lv) and unlock requirements (attributes or
  Observation Progress). Effects: Observation Length, card levels, card unlocks, Courage/Charisma/Knowledge, Speed
  Reading (Time Essences), Stage Unlock. A technology upgraded during an Observation applies from the next one.
- Stages: 10 normal + 1 special per world; 1 Temporal Chip (289) each, 10 max, +1 every 1800 s; first-pass rewards;
  stage N > 1 needs "Stage Unlock" level N-1. Achievements per world (7 styles) with step rewards.

LOCAL decisions (DESIGN_DECISIONS.md LOCAL-036):
- Outfits don't exist offline yet, so the black attributes come only from the Planetarium; the green boost of the sent
  Girls is round(sum of their levels / 3).
- A Challenge Card is won when the three attributes reach the card's `base`; Stages are fought with the original
  engine (the attribute effects of outfits are not applied). The Support Girl, crystals and the Stage 11 ranking are
  not rebuilt (Stage 11 records the best damage for its achievement).
"""
from __future__ import annotations
import json, random, time
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/echoes.json').read_text())
M = DATA['misc']
WORLDS = {int(w['id']): w for w in DATA['worlds']}
CARDS = {int(k): v for k, v in DATA['cards'].items()}
TEC = {int(t['id']): t for t in DATA['tec']}
STAGES = {int(s['id']): s for s in DATA['stages']}
ACH = {int(k): v for k, v in DATA['ach'].items()}
BOXES: dict[int, list] = {}
for _b in DATA['boxes']:
    BOXES.setdefault(int(_b['box_id']), []).append(_b)
ENERGY_TIME = int(M['time_cloister_energy_time'])
CARD_TIME = int(M['time_cloister_card_time'])
ESSENCE, ESSENCE_S = (int(x) for x in str(M['time_cloister_time_accelerata']).split('|'))
CLEAR = float(M['time_cloister_clear'])
CHIP, CHIP_MAX = (int(x) for x in str(M['time_cloister_fight_energy_max']).split('#'))
CHIP_CD = int(M['time_cloister_fight_energy_cd'])
# xyd.TimeCloisterCardType: SUPPLY 1, BATTLE 2 (→ BATTLE_WIN 4 / BATTLE_FAIL 5), EVENT 3, PLOT_EVENT 6,
# ENCOUNTER_BATTLE 7 (→ 8 / 9), DRESS_MISSION_EVENT 10 / DRESS_SUCC 11 (Outfits: not offline).
ENCOUNTER_TYPES = {3, 6, 7}
DRESS_TYPES = {10, 11}
UNLOCK_STAGE = 55  # function 47 (TIME_CLOISTER): open_type 2, open_value 55
HELP = [DATA['text'][k] for k in sorted(DATA['text']) if k.startswith('TIME_CLOISTER_HELP')]


def ids(text):
    return [int(x) for x in str(text or '').split('|') if x not in ('', None)]


def nums(text):
    return [float(x) for x in str(text or '').split('|') if x not in ('', None)]


def pairs(text):
    out = {}
    for part in str(text or '').replace('@', '|').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[k] = out.get(k, 0) + int(float(n))
    return out


def add(items, got):
    for k, n in got.items():
        items[k] = int(items.get(k, 0)) + n


# ---------------------------------------------------------------- state

def saved(state, now):
    e = state.setdefault('echoes', {})
    e.setdefault('tec', {}); e.setdefault('counters', {}); e.setdefault('ach_claimed', {}); e.setdefault('stage_max', {})
    e.setdefault('obs', None); e.setdefault('chip_at', now); e.setdefault('last_green', 0); e.setdefault('world', 1)
    items = state.setdefault('items', {})
    if 'chips_init' not in e:
        items[str(CHIP)] = max(int(items.get(str(CHIP), 0)), CHIP_MAX); e['chips_init'] = 1
    have = int(items.get(str(CHIP), 0))
    if have >= CHIP_MAX:
        e['chip_at'] = now
    else:
        n = (now - int(e['chip_at'])) // CHIP_CD
        if n > 0:
            got = min(n, CHIP_MAX - have)
            items[str(CHIP)] = have + got
            e['chip_at'] = now if have + got >= CHIP_MAX else int(e['chip_at']) + n * CHIP_CD
    return e


def tec_lv(e, tid):
    return int(e['tec'].get(str(tid), 0))


def world_tecs(w):
    return [t for t in TEC.values() if int(t['cloister']) == w]


def tec_value(t, lv):
    vals = nums(t['num'])
    return vals[min(lv, len(vals)) - 1] if lv and vals else 0


def outfit(state):
    """Outfits (gxb2/dress.py) give the black Courage / Charisma / Knowledge, as in TIME_CLOISTER_HELP02."""
    if not state.get('dress'):
        return [0, 0, 0]
    from .dress import attrs
    return attrs(state)


def black_attrs(e, w, dress_attrs=None):
    a = list(dress_attrs or [0, 0, 0])
    for t in world_tecs(w):
        lv = tec_lv(e, t['id'])
        if not lv:
            continue
        typ = int(t['type'])
        if typ in (5, 6, 7):
            a[typ - 5] += int(tec_value(t, lv))
        elif typ == 10:
            for i in range(3):
                a[i] += int(tec_value(t, lv))
    return a


def green_of(state, pids):
    lv = {p['partner_id']: int(p['lv']) for p in state['partners']}
    return round(sum(lv.get(p, 0) for p in pids) / 3)


def clockwork(e, w):
    return int(WORLDS[w]['energy']) + sum(int(tec_value(t, tec_lv(e, t['id']))) for t in world_tecs(w) if int(t['type']) == 4)


# ---------------------------------------------------------------- achievements

def counters(e, w):
    return e['counters'].setdefault(str(w), {'tec_group': {}, 'enc': {}, 'enc_best': {}, 'points': 0, 'points_best': 0, 'dmg_best': 0})


def ach_value(e, w, at):
    c = counters(e, w)
    style, param = int(at['style']), str(at['param'])
    if style == 1:
        return int(c['tec_group'].get(param, 0))
    if style == 2:
        return int(e['stage_max'].get(str(w), 0))
    if style == 3:
        return int(c['enc'].get(param, 0))
    if style == 4:
        return int(c['enc_best'].get(param, 0))
    if style == 5:
        return int(c['points'])
    if style == 6:
        return int(c['points_best'])
    if style == 7:
        return int(c['dmg_best'])
    return 0


def ach_steps(at):
    out, aid = [], int(at['start_achievement'])
    while aid and aid in ACH and len(out) < 50:
        out.append(aid)
        if aid == int(at['end_achievement']):
            break
        aid = int(ACH[aid]['next_achieve_id'] or 0)
    return out


def ach_rows(e, w):
    rows = []
    for at in DATA['ach_type']:
        if int(at['cloister']) != w:
            continue
        steps = ach_steps(at)
        val = ach_value(e, w, at)
        reached = sum(1 for s in steps if val >= int(ACH[s]['complete_value']))
        claimed = int(e['ach_claimed'].get(str(at['id']), 0))
        cur = steps[min(claimed, len(steps) - 1)]
        rows.append({'id': int(at['id']), 'value': val, 'need': int(ACH[cur]['complete_value']), 'steps': len(steps), 'reached': reached,
                     'claimed': claimed, 'claimable': reached > claimed, 'done': claimed >= len(steps), 'awards': pairs(ACH[cur]['awards']),
                     'go': {1: 'tec', 2: 'stages', 7: 'stages'}.get(int(at['style']), 'observe'),
                     'text': DATA['ach_text'].get(str(cur), '').replace('{1}', str(int(ACH[cur]['complete_value'])))})
    return rows


def progress_steps(e, w):
    """TimeCloisterAchievementWindow: Observation Progress counts the *claimed* steps (achieve_id - start_id)."""
    rows = ach_rows(e, w)
    return sum(min(r['claimed'], r['steps']) for r in rows), sum(r['steps'] for r in rows)


def progress(e, w):
    done, total = progress_steps(e, w)
    return done / total if total else 0.0


def world_open(e, w):
    return w == 1 or (w - 1 in WORLDS and progress(e, w - 1) >= CLEAR)


# ---------------------------------------------------------------- cards

def card_unlocked(e, card):
    return int(card.get('lock') or 1) != 2 or (card.get('tec') and tec_lv(e, int(card['tec'])) > 0)


def level_card(e, cid):
    """Cards level up along next_id while the next level is unlocked (lock 2 → its `tec` learned)."""
    for _ in range(20):
        nxt = int(CARDS[cid].get('next_id') or 0)
        if not nxt or nxt not in CARDS or not card_unlocked(e, CARDS[nxt]):
            break
        cid = nxt
    return cid


def draw_card(e, w, rng):
    world = WORLDS[w]
    boxes = list(zip(ids(world['card_box']), [int(x) for x in nums(world['weights'])]))
    for _ in range(20):
        box = pick(boxes, lambda b: b[1], rng)[0]
        opts = [b for b in BOXES.get(box, []) if int(b['cards']) in CARDS and int(CARDS[int(b['cards'])]['type']) not in DRESS_TYPES
                and card_unlocked(e, CARDS[int(b['cards'])])]
        if not opts:
            continue
        return level_card(e, int(pick(opts, lambda b: int(b['weight']), rng)['cards']))
    return level_card(e, int(BOXES[ids(world['card_box'])[0]][0]['cards']))


def pick(options, weight, rng):
    total = sum(max(0, weight(o)) for o in options)
    x = rng.randrange(total) if total > 0 else 0
    for o in options:
        x -= max(0, weight(o))
        if x < 0:
            return o
    return options[-1]


def elapsed(o, now):
    end = o.get('ended') or now
    return min(max(0, end - int(o['start'])) + int(o.get('speed', 0)), int(o['clockwork']) * ENERGY_TIME)


def sync_cards(e, o, now):
    """Cards triggered so far (1 per 300 s of reading), drawn deterministically from the Observation seed."""
    want = elapsed(o, now) // CARD_TIME
    while len(o['cards']) < want:
        rng = random.Random(int(o['seed']) * 1000003 + len(o['cards']))
        o['cards'].append(draw_card(e, int(o['world']), rng))
    if elapsed(o, now) >= int(o['clockwork']) * ENERGY_TIME and not o.get('ended'):
        o['ended'] = int(o['start']) + int(o['clockwork']) * ENERGY_TIME - int(o.get('speed', 0))


def resolve(card_id, attrs):
    """(final card, reward dict, points, encounter score)."""
    card = CARDS[card_id]
    typ = int(card['type'])
    final = card
    if card.get('sub_card'):
        subs = ids(card['sub_card'])
        base = [int(x) for x in nums(card['base'])] or [0, 0, 0]
        win = all(a >= b for a, b in zip(attrs, base))
        final = CARDS[subs[0] if win or len(subs) == 1 else subs[1]]
    at, aw = final.get('award_type'), final.get('awards')
    reward = {}
    if aw not in ('', 0, '0', None):
        reward = {'box': int(aw)} if str(at) == '1' else pairs(aw)
    score = int(final.get('score') or 0)
    return final, reward, int(final.get('point') or 0), score


# ---------------------------------------------------------------- snapshot / actions

def card_view(cid):
    c = CARDS[cid]
    t = DATA['card_text'].get(str(cid)) or DATA['card_text'].get(str(c.get('first_id') or cid)) or {}
    return {'id': cid, 'type': int(c['type']), 'img': c['img'], 'name': t.get('name', ''), 'desc': t.get('desc', ''), 'level': c.get('level') or 1}


def snapshot(state, now=None):
    import copy
    now = int(time.time()) if now is None else now
    view = copy.deepcopy(state)
    e = saved(view, now)
    o = e['obs']
    obs = None
    if o:
        sync_cards(e, o, now)
        obs = {'world': o['world'], 'start': o['start'], 'clockwork': o['clockwork'], 'elapsed': elapsed(o, now), 'ended': bool(o.get('ended')),
               'left': max(0, int(o['clockwork']) * ENERGY_TIME - elapsed(o, now)), 'partners': o['partners'], 'attrs': o['attrs'], 'green': o['green'],
               'cards': [card_view(c) for c in o['cards']], 'next_card': CARD_TIME - elapsed(o, now) % CARD_TIME}
    worlds = []
    for w, row in sorted(WORLDS.items()):
        txt = DATA['world_text'].get(str(w), {})
        worlds.append({'id': w, 'name': txt.get('name', f'World {w}'), 'desc': txt.get('desc', ''), 'open': world_open(e, w), 'progress': int(progress(e, w) * 100),
                       'shard': int(row['tec_icon']), 'shards': int(view['items'].get(str(row['tec_icon']), 0)), 'clockwork': clockwork(e, w),
                       'black': black_attrs(e, w, outfit(view)), 'stage_max': int(e['stage_max'].get(str(w), 0))})
    return {'unlocked': int(view.get('max_stage', 0)) >= UNLOCK_STAGE, 'unlock_stage': UNLOCK_STAGE, 'help': HELP, 'worlds': worlds, 'obs': obs, 'essence': int(view['items'].get(str(ESSENCE), 0)), 'essence_s': ESSENCE_S,
            'chips': int(view['items'].get(str(CHIP), 0)), 'chip_max': CHIP_MAX, 'chip_next': int(e['chip_at']) + CHIP_CD if int(view['items'].get(str(CHIP), 0)) < CHIP_MAX else None, 'card_time': CARD_TIME,
            'energy_time': ENERGY_TIME}


def detail(state, w, now=None):
    """Planetarium, stages and achievements of one world (loaded on demand)."""
    import copy
    from .engine import TABLES
    now = int(time.time()) if now is None else now
    e = saved(copy.deepcopy(state), now)
    prog = progress(e, w)
    green = int(e.get('last_green', 0))
    black = black_attrs(e, w, outfit(state))
    attrs = [b + green for b in black]
    tecs = []
    for t in world_tecs(w):
        lv = tec_lv(e, t['id'])
        costs = [pairs(c) for c in str(t['upgrade_cost']).split('|') if c]
        txt = DATA['tec_text'].get(str(t['id']), {})
        tecs.append({'id': int(t['id']), 'group': int(t['group']), 'type': int(t['type']), 'lv': lv, 'max': int(t['max_lvl']), 'img': t['img'],
                     'xy': [float(x) for x in str(t['xy'] or '0|0').split('|')[:2]], 'pre': ids(t['pre_id']),
                     'cost': costs[lv] if lv < len(costs) else None, 'why': can_upgrade(e, t, black, prog),
                     'name': txt.get('name', ''), 'desc': str(txt.get('desc', '')).replace('{1}', str(int(tec_value(t, max(1, min(lv + 1, int(t['max_lvl']))))))),
                     'unlock': txt.get('unlock', '')})
    stages = []
    smax = int(e['stage_max'].get(str(w), 0))
    for i, s in enumerate([s for s in DATA['stages'] if int(s['cloister']) == w]):
        b = TABLES['battle'].get(str(s['battle_id']), {})
        stages.append({'id': int(s['id']), 'n': i + 1, 'special': int(s['type']) == 2, 'base': [int(x) for x in nums(s['base'])], 'awards': pairs(s['awards']),
                       'passed': i + 1 <= smax, 'open': stage_open(e, w, i + 1), 'boss': int(TABLES['monster'].get(str(b.get('monsters', '')).split('|')[0], {}).get('partner_link') or 0)})
    cards = []
    for cid, c in sorted(CARDS.items()):
        if int(str(cid)[0]) != w or int(c['type']) not in (1, 2, 3, 6, 7) or (c.get('first_id') and int(c['first_id']) != cid):
            continue
        cur = level_card(e, cid)
        v = card_view(cur)
        v.update(unlocked=card_unlocked(e, c), base=[int(x) for x in nums(c['base'])] or None,
                 unlock=DATA['card_text'].get(str(cid), {}).get('unlock_desc', ''))
        cards.append(v)
    done, total = progress_steps(e, w)
    return {'world': w, 'progress': int(100 * done / total) if total else 0, 'progress_steps': [done, total], 'attrs': attrs, 'black': black, 'cards': cards, 'green': green, 'tecs': tecs, 'stages': stages, 'ach': ach_rows(e, w),
            'best_damage': counters(e, w)['dmg_best']}


def can_upgrade(e, t, black, prog):
    """TimeCloisterTechDetailWindow: prerequisite level + xyd.TimeCloisterUnLockType."""
    w = int(t['cloister'])
    lv = tec_lv(e, t['id'])
    if lv >= int(t['max_lvl']):
        return 'Nivel máximo'
    if int(t['type']) in (9, 11, 12):
        return 'Support Girl / Crystals: no disponible offline'
    pre, pre_lv = ids(t['pre_id']), ids(t['pre_lv'])
    if any(tec_lv(e, p) < (pre_lv[i] if i < len(pre_lv) else pre_lv[-1] if pre_lv else 1) for i, p in enumerate(pre)):
        return 'Requiere la tecnología anterior'
    ut = str(t.get('unlock_type') or '')
    need = nums(t['unlock_num'])
    c = counters(e, w)
    if ut == '1' and any(a < b for a, b in zip(black, need)):  # SELF_BASE (black attributes)
        return 'Requiere más Courage / Charisma / Knowledge'
    if ut == '2' and int(c['enc'].get(str(int(need[0])), 0)) < need[1]:  # EVENT_NUM
        return DATA['tec_text'].get(str(t['id']), {}).get('unlock') or 'Requiere más Encounters'
    if ut == '3':  # ACHIEVEMENT: that achievement type claimed past step need[1]
        at = next(a for a in DATA['ach_type'] if int(a['id']) == int(need[0]))
        steps = ach_steps(at)
        claimed = int(e['ach_claimed'].get(str(int(need[0])), 0))
        if claimed <= (steps.index(int(need[1])) if int(need[1]) in steps else len(steps)):
            return DATA['tec_text'].get(str(t['id']), {}).get('unlock') or 'Requiere un logro'
    if ut == '4' and prog < need[0]:  # PROGRESS
        return f"Requiere {round(need[0] * 100)}% de progreso de observación"
    if ut == '5' and int(c.get('fights', {}).get(str(int(need[0])), 0)) < need[1]:  # ENCOUNTER_FIGHT
        return DATA['tec_text'].get(str(t['id']), {}).get('unlock') or 'Requiere más desafíos'
    return None


def stage_open(e, w, n):
    if n == 1:
        return True
    unlock = sum(tec_lv(e, t['id']) for t in world_tecs(w) if int(t['type']) == 8)
    return int(e['stage_max'].get(str(w), 0)) >= n - 1 and unlock >= n - 1


def action(state, request, now=None, fight=None, rng_seed=None):
    now = int(time.time()) if now is None else now
    e = saved(state, now)
    items = state['items']
    kind = request.get('action')
    w = int(request.get('world', e.get('world', 1)))
    if w not in WORLDS:
        raise ValueError('Mundo no válido')
    result = {}
    if int(state.get('max_stage', 0)) < UNLOCK_STAGE:
        raise ValueError(f'Echoes of Time se desbloquea al superar la fase {UNLOCK_STAGE} de la campaña')
    if kind in ('open', 'detail'):
        e['world'] = w
        return result
    if not world_open(e, w):
        raise ValueError('Ese Mundo del Tiempo aún está bloqueado (85% de progreso del anterior)')
    o = e['obs']
    if kind == 'start':
        if o:
            raise ValueError('Ya hay una observación en curso')
        pids = [int(p) for p in request.get('partners') or []]
        owned = {p['partner_id'] for p in state['partners']}
        if not 1 <= len(pids) <= 6 or len(set(pids)) != len(pids) or any(p not in owned for p in pids):
            raise ValueError('Envía entre 1 y 6 chicas')
        green = green_of(state, pids)
        e['last_green'] = green
        e['obs'] = {'world': w, 'start': now, 'clockwork': clockwork(e, w), 'partners': pids, 'green': green,
                    'attrs': [b + green for b in black_attrs(e, w, outfit(state))], 'cards': [], 'speed': 0, 'seed': rng_seed if rng_seed is not None else now}
        e['world'] = w
        return result
    if kind == 'speed':
        if not o or o.get('ended'):
            raise ValueError('No hay observación en curso')
        n = max(1, int(request.get('count', 1)))
        if int(items.get(str(ESSENCE), 0)) < n:
            raise ValueError('Faltan Time Essences')
        items[str(ESSENCE)] = int(items[str(ESSENCE)]) - n
        o['speed'] = int(o.get('speed', 0)) + n * ESSENCE_S
        sync_cards(e, o, now)
        return result
    if kind == 'stop':
        if not o:
            raise ValueError('No hay observación en curso')
        sync_cards(e, o, now)
        o['ended'] = o.get('ended') or now
        return result
    if kind == 'claim':
        if not o:
            raise ValueError('No hay observación que reclamar')
        sync_cards(e, o, now)
        if not o.get('ended'):
            raise ValueError('Termina la observación primero')
        from .engine import TABLES
        c = counters(e, int(o['world']))
        got, points, enc_pts, per = {}, 0, 0, {}
        rng = random.Random(int(o['seed']) + 77)
        for cid in o['cards']:
            final, reward, pt, score = resolve(cid, o['attrs'])
            points += pt
            enc_pts += score
            if int(CARDS[cid]['type']) in ENCOUNTER_TYPES:
                key = str(CARDS[cid].get('first_id') or cid)
                per[key] = per.get(key, 0) + 1
            if 'box' in reward:
                opts = [v for v in TABLES['dropbox'].values() if int(v['dropbox_id']) == reward['box']]
                if opts:
                    ch = pick(opts, lambda v: int(v['weight']), rng)
                    k, lo, *hi = str(ch['item']).split('#')
                    n = int(lo) if not hi else int(lo) + rng.randrange(int(hi[0]) - int(lo) + 1)
                    got[k] = got.get(k, 0) + n
            else:
                for k, n in reward.items():
                    got[k] = got.get(k, 0) + n
        grade = None
        for g in DATA['grades']:
            if int(g['group']) == int(o['world']) and points >= int(g['point']):
                grade = g
        if grade:
            for k, n in pairs(grade['awards']).items():
                got[k] = got.get(k, 0) + n
        add(items, got)
        for cid, n in per.items():
            c['enc'][cid] = int(c['enc'].get(cid, 0)) + n
            c['enc_best'][cid] = max(int(c['enc_best'].get(cid, 0)), n)
        for cid in o['cards']:
            if int(CARDS[cid]['type']) in (2, 7):  # getSumStartEvents: Challenge / Encounter battles started
                c.setdefault('fights', {})[str(cid)] = int(c.setdefault('fights', {}).get(str(cid), 0)) + 1
        c['points'] = int(c['points']) + enc_pts
        c['points_best'] = max(int(c['points_best']), enc_pts)
        e['obs'] = None
        result.update(got=got, points=points, cards=len(o['cards']), encounter_points=enc_pts)
        return result
    if kind == 'upgrade':
        tid = int(request.get('tec', 0))
        t = TEC.get(tid)
        if not t or int(t['cloister']) != w:
            raise ValueError('Tecnología no válida')
        why = can_upgrade(e, t, black_attrs(e, w, outfit(state)), progress(e, w))
        if why:
            raise ValueError(why)
        lv = tec_lv(e, tid)
        cost = [pairs(x) for x in str(t['upgrade_cost']).split('|') if x][lv]
        for k, n in cost.items():
            if int(items.get(k, 0)) < n:
                raise ValueError('Faltan Time Shards')
        for k, n in cost.items():
            items[k] = int(items[k]) - n
        e['tec'][str(tid)] = lv + 1
        g = str(t['group'])
        counters(e, w)['tec_group'][g] = int(counters(e, w)['tec_group'].get(g, 0)) + 1
        if int(t['type']) == 3:  # Speed Reading: Time Essences
            add(items, {str(ESSENCE): int(tec_value(t, lv + 1))})
        result['lv'] = lv + 1
        return result
    if kind == 'claim_ach':
        aid = int(request.get('ach', 0))
        row = next((r for r in ach_rows(e, w) if r['id'] == aid), None)
        if not row or not row['claimable']:
            raise ValueError('Logro no disponible')
        add(items, row['awards'])
        e['ach_claimed'][str(aid)] = int(e['ach_claimed'].get(str(aid), 0)) + 1
        return {'got': row['awards']}
    if kind == 'fight':
        n = int(request.get('stage', 0))
        wst = [s for s in DATA['stages'] if int(s['cloister']) == w]
        if not 1 <= n <= len(wst) or not stage_open(e, w, n):
            raise ValueError('Fase bloqueada: supera la anterior y mejora "Stage Unlock" en el Planetarium')
        team = request.get('team') or []
        owned = {p['partner_id'] for p in state['partners']}
        if not 1 <= len(team) <= 6 or any(int(t['partner_id']) not in owned for t in team):
            raise ValueError('Equipo no válido')
        if int(items.get(str(CHIP), 0)) < 1:
            raise ValueError('No quedan Temporal Chips (se recupera 1 cada 30 min)')
        items[str(CHIP)] = int(items[str(CHIP)]) - 1
        if int(items[str(CHIP)]) == CHIP_MAX - 1:
            e['chip_at'] = now
        s = wst[n - 1]
        report = fight(team, int(s['battle_id']))
        win = bool(report['isWin'])
        result.update(win=win, stage=n, battle=report)
        if int(s['type']) == 2:
            dmg = sum(int(h.get('hurt', 0)) for h in report.get('hurts', []) if int(h.get('pos', 0)) <= 6)
            c = counters(e, w)
            c['dmg_best'] = max(int(c['dmg_best']), dmg)
            result['damage'] = dmg
        elif win and n > int(e['stage_max'].get(str(w), 0)):
            e['stage_max'][str(w)] = n
            got = pairs(s['awards'])
            add(items, got)
            result['got'] = got
        return result
    raise ValueError('Acción de Echoes of Time no disponible')
