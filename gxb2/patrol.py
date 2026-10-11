"""Patrol (models/Dungeon.lua, DungeonWindow / DungeonSelectHerosWindow / DungeonShopWindow) offline.

Recovered from the client (tables + DUNGEON_WINDOW_HELP):
- Opens 48 h, closes 48 h. Unlock: function 19 (open_type 2 = campaign stage ≥ 92).
- Up to 5 Girls per round; their build is frozen until the next round. Each fight: 1 chosen Girl vs the stage enemies.
- HP/energy of both sides is kept between fights (status.hp %, status.mp); a Girl at 0 HP can't fight. 15 rounds max,
  battle type DUNGEON (4) so only killing every enemy wins.
- 600 stages (misc dungeon_top) = 6 phases × 100 (Easy, Normal, Hard, Extreme, Fantasy, Nightmare). Each stage picks
  a random battle from its dungeon_battle pool (random_battle).
- Victory → 1 of 3 results: Chest (dropbox_id), Item (dungeon_drug by weight) or Merchant (dungeon_shop by weight).
  Stationery (drug type 1) stops dropping at num_max (20) and gives a permanent buff in every fight of the round.
- Rice Balls (drug type 0) heal/restore energy of the selected Girl (DungeonWindow: needs one Girl alive; not at full HP
  except the Jujube Riceball). A skipped Merchant offer goes to the Patrol shop to buy later.
- After passing 50 stages of a phase, earlier phases are Auto Smashed when Patrol opens again.

LOCAL decisions (server behaviour not in the client; DESIGN_DECISIONS.md LOCAL-028):
- Calendar: 4-day cycle anchored at local midnight of 2019-01-07; open the first 48 h.
- dungeon.award_weight "a|b|c" follows the column order after it: chest (dropbox_id), item (drug), merchant (trader).
- Merchant offer tier: phases 1-2 → dungeon_shop type 1 (Primary), 3-4 → 2 (Medium), 5-6 → 3 (Senior).
- Auto Smash rolls one normal victory result per smashed stage (chests to the bag, items/merchant offers kept).
- Enemies keep their own HP/energy only while the same stage lasts; a new stage starts at full HP.
- No Servant in Patrol fights (the original request only carries partner_index).
"""
from __future__ import annotations
import copy, json, secrets, time
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/patrol.json').read_text())
TOP = DATA['top']
STAGES = {int(r['id']): r for r in DATA['dungeon']}
POOLS: dict[int, list] = {}
for _r in DATA['dungeon_battle']:
    POOLS.setdefault(int(_r['random_battle']), []).append(_r)
DRUGS = {int(r['id']): r for r in DATA['dungeon_drug']}
SHOP = {int(r['id']): r for r in DATA['dungeon_shop']}
BOX: dict[int, list] = {}
for _r in DATA['dropbox']:
    BOX.setdefault(int(_r['dropbox_id']), []).append(_r)
UNLOCK_STAGE = int(DATA['unlock']['open_value'])
PHASES = ['Easy', 'Normal', 'Hard', 'Extreme', 'Fantasy', 'Nightmare']
HOURS_OPEN = 48
CYCLE = 4 * 86400
ANCHOR = int(time.mktime((2019, 1, 7, 0, 0, 0, 0, 0, -1)))
MAX_GIRLS = 5
BATTLE_TYPE = 4  # xyd.ReportBattleType.DUNGEON


def window(now):
    """(period index, is_open, start of the current/next open window, end of it)."""
    k, off = divmod(now - ANCHOR, CYCLE)
    start = ANCHOR + k * CYCLE
    if off < HOURS_OPEN * 3600:
        return k, True, start, start + HOURS_OPEN * 3600
    return k, False, start + CYCLE, start + CYCLE + HOURS_OPEN * 3600


def phase(stage):
    return min(len(PHASES), (max(1, stage) - 1) // 100 + 1)


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[k] = out.get(k, 0) + int(float(n))
    return out


def weighted(options, weight, rng):
    total = sum(max(0, int(weight(o))) for o in options)
    if total <= 0:
        return None
    x = rng(total)
    for o in options:
        x -= max(0, int(weight(o)))
        if x < 0:
            return o
    return options[-1]


def fresh(max_stage=0, skip_report=0):
    return {'period': None, 'max_stage': max_stage, 'current_stage': 1, 'partners': [], 'enemies': [], 'battle_id': 0,
            'drugs': {}, 'shop_items': [], 'curr_shop_item': 0, 'skip_report': skip_report, 'last': None}


def saved(state, now):
    p = state.setdefault('patrol', fresh())
    k, is_open, _, _ = window(now)
    if is_open and p.get('period') != k:
        # A new Patrol round: the team, items and shop reset; the historical best stage is kept.
        state['patrol'] = p = {**fresh(p.get('max_stage', 0), p.get('skip_report', 0)), 'period': k}
    return p


def enemies_for(stage, rng):
    """Random battle of the stage pool → enemy lineup at full HP (battle.json monsters/stands)."""
    from .engine import TABLES  # late import: engine imports this module
    row = weighted(POOLS[int(STAGES[stage]['random_battle'])], lambda _: 1, rng)
    battle = TABLES['battle'][str(row['battle_id'])]
    team = [{'table_id': int(t), 'pos': int(q), 'status': {'hp': 100, 'mp': 50}}
            for t, q in zip(str(battle['monsters']).split('|'), str(battle['stands']).split('|'))]
    return int(row['battle_id']), team


def roll_chest(stage, rng):
    opt = weighted(BOX.get(int(STAGES[stage]['dropbox_id']), []), lambda o: o['weight'], rng)
    if not opt:
        return {}
    k, lo, *hi = str(opt['item']).split('#')
    lo = int(lo); hi = int(hi[0]) if hi else lo
    return {k: lo + (rng(hi - lo + 1) if hi > lo else 0)}


def roll_drug(p, rng):
    opts = [d for d in DRUGS.values() if int(d['type']) == 0 or int(p['drugs'].get(str(d['id']), 0)) < int(d['num_max'])]
    d = weighted(opts, lambda o: o['weight'], rng)
    return int(d['id']) if d else 0


def shop_tier(stage):
    return (phase(stage) + 1) // 2


def roll_merchant(stage, rng):
    opts = [s for s in SHOP.values() if int(s['type']) == shop_tier(stage)]
    s = weighted(opts, lambda o: o['weight'], rng)
    return int(s['id']) if s else 0


def victory_award(p, items, stage, rng):
    """1 of 3 results after a win (award_weight: chest | item | merchant)."""
    row = STAGES[stage]
    w = [int(x) for x in str(row['award_weight']).split('|')]
    w += [0] * (3 - len(w))
    if not int(row.get('drug', 1)): w[1] = 0
    if not int(row.get('trader', 1)): w[2] = 0
    kind = weighted([0, 1, 2], lambda i: w[i], rng)
    if kind == 1:
        drug = roll_drug(p, rng)
        if drug:
            p['drugs'][str(drug)] = int(p['drugs'].get(str(drug), 0)) + 1
            return {'kind': 'item', 'drug': drug}
        kind = 0
    if kind == 2:
        offer = roll_merchant(stage, rng)
        if offer:
            return {'kind': 'merchant', 'offer': offer}
        kind = 0
    got = roll_chest(stage, rng)
    for k, n in got.items():
        items[k] = int(items.get(k, 0)) + n
    return {'kind': 'chest', 'got': got}


def smash_start(max_stage):
    """First stage after Auto Smash: the highest phase whose stage 50 was passed in an earlier round."""
    k = 1
    for ph in range(1, len(PHASES) + 1):
        if max_stage >= (ph - 1) * 100 + 50:
            k = ph
    return (k - 1) * 100 + 1


def stationery_buffs(p):
    out = []
    for d in DRUGS.values():
        if int(d['type']) == 1:
            out += [int(d['effect'])] * min(int(d['num_max']), int(p['drugs'].get(str(d['id']), 0)))
    return out


def alive(p):
    return any(int(x['status']['hp']) > 0 for x in p['partners'])


def snapshot(state, now=None):
    from .engine import TABLES
    now = int(time.time()) if now is None else now
    p = saved(copy.deepcopy(state), now) if 'patrol' not in state else state['patrol']
    k, is_open, start, end = window(now)
    fresh_round = is_open and p.get('period') != k
    if fresh_round:
        p = {**fresh(p.get('max_stage', 0), p.get('skip_report', 0)), 'period': k}
    stage = min(int(p['current_stage']), TOP + 1)
    names = TABLES['names']
    monsters = TABLES['monster']
    prow = lambda tid: TABLES['partner'].get(str(tid), {})
    partners = [{'index': i + 1, 'partner_id': x['partner_id'], 'table_id': x['table_id'], 'lv': x['lv'],
                 'group': int(prow(x['table_id']).get('group') or 0), 'stars': int(prow(x['table_id']).get('max_star') or 0) + int(x.get('awake', 0)),
                 'name': names.get(str(x['table_id']), str(x['table_id'])), 'hp': int(x['status']['hp']), 'mp': int(x['status'].get('mp', 0))}
                for i, x in enumerate(p['partners'])]
    enemies = []
    for e in p['enemies']:
        m = monsters.get(str(e['table_id']), {})
        link = int(m.get('partner_link') or e['table_id'])
        enemies.append({'table_id': link, 'lv': int(m.get('lv_show') or m.get('lv') or 1), 'pos': e['pos'], 'name': names.get(str(link), str(link)),
                        'group': int(prow(link).get('group') or 0), 'stars': int(prow(link).get('max_star') or 0),
                        'hp': int(e['status']['hp']), 'mp': int(e['status'].get('mp', 0))})
    offer = lambda sid: {'id': sid, 'cost': pairs(SHOP[sid]['cost']), 'item': pairs(SHOP[sid]['item'])}
    drugs = []
    for d in DRUGS.values():
        n = int(p['drugs'].get(str(d['id']), 0))
        text = DATA['drug_text'].get(str(d['id']), {})
        entry = {'id': int(d['id']), 'type': int(d['type']), 'count': n, 'max': int(d['num_max']), 'icon': int(d['icon']),
                 'name': text.get('name', f"Drug {d['id']}"), 'desc': text.get('desc', '')}
        if int(d['type']) == 1:
            st = DATA['stationery'].get(str(d['effect']), {})
            per = float(st.get('num', 0)) / float(st.get('factor') or 1) * 100
            entry['per_unit'] = round(per, 2); entry['total'] = round(per * min(n, entry['max']), 2)
            entry['desc'] = entry['desc'].replace('{1}', f"{entry['total']:g}")
        drugs.append(entry)
    row = STAGES.get(stage) or STAGES[TOP]
    return {'unlocked': int(state.get('max_stage', 0)) >= UNLOCK_STAGE, 'unlock_stage': UNLOCK_STAGE, 'open': is_open,
            'window_start': start, 'window_end': end, 'stage': stage, 'top': TOP, 'all_pass': stage > TOP,
            'phase': PHASES[phase(min(stage, TOP)) - 1], 'phase_index': phase(min(stage, TOP)), 'phase_stage': (min(stage, TOP) - 1) % 100 + 1,
            'max_stage': int(p.get('max_stage', 0)), 'smash_to': smash_start(int(p.get('max_stage', 0))), 'started': bool(p['partners']),
            'alive': alive(p) if p['partners'] else False, 'partners': partners, 'enemies': enemies, 'drugs': drugs,
            'shop_items': [offer(s) for s in p['shop_items']], 'curr_shop_item': offer(p['curr_shop_item']) if p['curr_shop_item'] else None,
            'shop_tier': shop_tier(min(stage, TOP)), 'skip_report': int(p.get('skip_report', 0)), 'map': row['map_source'],
            'map_scale': float(row.get('map_scale') or 1), 'map_position': [float(v) for v in str(row.get('map_position') or '0|0').split('|')],
            'max_girls': MAX_GIRLS, 'last': p.get('last')}


def pay(items, cost):
    for k, n in cost.items():
        if int(items.get(k, 0)) < n:
            raise ValueError('Faltan ' + ('gemas' if k == '2' else 'monedas' if k == '1' else f'objetos {k}'))
    for k, n in cost.items():
        items[k] = int(items[k]) - n


def action(state, request, now=None, rng=secrets.randbelow, fight=None):
    """fight(partner, enemies, battle_id, buffs) -> report (original engine, battle type DUNGEON, statuses applied)."""
    now = int(time.time()) if now is None else now
    if int(state.get('max_stage', 0)) < UNLOCK_STAGE:
        raise ValueError(f'Patrol se desbloquea al superar la fase {UNLOCK_STAGE} de la campaña')
    kind = request.get('action')
    p = saved(state, now)
    items = state['items']
    result = {}
    if kind == 'skip_report':
        p['skip_report'] = 0 if int(p.get('skip_report', 0)) else 1
        return result
    if not window(now)[1]:
        raise ValueError('Patrol está cerrada; vuelve a abrir en la próxima ventana de 48 h')
    if kind == 'start':
        if p['partners']:
            raise ValueError('El equipo de Patrol ya está fijado hasta la próxima ronda')
        ids = [int(x) for x in request.get('partner_ids') or []]
        if not ids or len(ids) > MAX_GIRLS or len(set(ids)) != len(ids):
            raise ValueError(f'Elige entre 1 y {MAX_GIRLS} chicas distintas')
        owned = {x['partner_id']: x for x in state['partners']}
        if any(i not in owned for i in ids):
            raise ValueError('Chica no disponible')
        p['partners'] = [{**copy.deepcopy(owned[i]), 'status': {'hp': 100, 'mp': 50, 'pos': 1}} for i in ids]
        start = smash_start(int(p.get('max_stage', 0)))
        smashed = {'items': {}, 'drugs': {}, 'offers': 0, 'stages': start - 1}
        for st in range(1, start):
            before = dict(items)
            r = victory_award(p, items, st, rng)
            if r['kind'] == 'merchant':
                p['shop_items'].append(r['offer']); smashed['offers'] += 1
            elif r['kind'] == 'item':
                smashed['drugs'][str(r['drug'])] = smashed['drugs'].get(str(r['drug']), 0) + 1
            for k in set(items) | set(before):
                d = int(items.get(k, 0)) - int(before.get(k, 0))
                if d: smashed['items'][k] = smashed['items'].get(k, 0) + d
        p['current_stage'] = start
        p['battle_id'], p['enemies'] = enemies_for(start, rng)
        result['smashed'] = smashed if start > 1 else None
    elif kind == 'fight':
        if not p['partners']:
            raise ValueError('Primero elige el equipo de Patrol')
        if p['curr_shop_item']:
            raise ValueError('Atiende primero al mercader (comprar o saltar)')
        if p['current_stage'] > TOP:
            raise ValueError('Patrol completada')
        idx = int(request.get('index', 0))
        if not 1 <= idx <= len(p['partners']):
            raise ValueError('Chica no válida')
        girl = p['partners'][idx - 1]
        if int(girl['status']['hp']) <= 0:
            raise ValueError('Esta chica no tiene HP y ya no puede luchar en esta ronda')
        report = fight(girl, p['enemies'], p['battle_id'], stationery_buffs(p))
        end = {int(s['pos']): s for s in report.get('end_status', [])}
        mine = end.get(1) or next((s for s in report.get('end_status', []) if int(s['pos']) <= 6), None)
        if mine:
            girl['status'].update(hp=max(0, int(mine['hp'])), mp=max(0, int(mine['mp'])))
        win = bool(report['isWin'])
        stage = p['current_stage']
        result.update(win=win, stage=stage)
        if win:
            p['current_stage'] = stage + 1
            p['max_stage'] = max(int(p.get('max_stage', 0)), stage)
            award = victory_award(p, items, stage, rng)
            if award['kind'] == 'merchant':
                p['curr_shop_item'] = award['offer']
            result['award'] = award
            if p['current_stage'] <= TOP:
                p['battle_id'], p['enemies'] = enemies_for(p['current_stage'], rng)
            else:
                p['enemies'] = []
        else:
            for e in p['enemies']:
                s = end.get(int(e['pos']) + 6)
                if s:
                    e['status'].update(hp=max(0, int(s['hp'])), mp=max(0, int(s['mp'])))
        p['last'] = {'at': now, 'stage': stage, 'win': win, 'girl': girl['table_id']}
        result['battle'] = report
    elif kind == 'use_drug':
        drug = int(request.get('drug_id', 0)); idx = int(request.get('index', 0))
        d = DRUGS.get(drug)
        if not d or int(d['type']) != 0:
            raise ValueError('Solo los Rice Balls se usan manualmente')
        if int(p['drugs'].get(str(drug), 0)) <= 0:
            raise ValueError('No te quedan de este objeto')
        if not p['partners'] or not alive(p):
            raise ValueError('No queda ninguna chica en pie')
        if not 1 <= idx <= len(p['partners']):
            raise ValueError('Chica no válida')
        st = p['partners'][idx - 1]['status']
        if drug != 2 and int(st['hp']) >= 100:
            raise ValueError("The Girl's HP is full")
        p['drugs'][str(drug)] = int(p['drugs'][str(drug)]) - 1
        for part in str(d['effect']).split('|'):
            name, val = part.split('#')
            if name == 'healP':
                st['hp'] = min(100, int(st['hp']) + round(100 * float(val)))
            elif name == 'energy':
                st['mp'] = int(st.get('mp', 0)) + int(float(val))
    elif kind == 'merchant':
        sid = p['curr_shop_item']
        if not sid:
            raise ValueError('No hay mercader')
        if request.get('skip'):
            p['shop_items'].append(sid)
        else:
            pay(items, pairs(SHOP[sid]['cost']))
            for k, n in pairs(SHOP[sid]['item']).items():
                items[k] = int(items.get(k, 0)) + n
            result['got'] = pairs(SHOP[sid]['item'])
        p['curr_shop_item'] = 0
    elif kind == 'buy':
        i = int(request.get('index', -1))
        if not 0 <= i < len(p['shop_items']):
            raise ValueError('Oferta no disponible')
        sid = p['shop_items'][i]
        pay(items, pairs(SHOP[sid]['cost']))
        for k, n in pairs(SHOP[sid]['item']).items():
            items[k] = int(items.get(k, 0)) + n
        p['shop_items'].pop(i)
        from . import growth_diary
        growth_diary.record(state,'growth_patrol_buy')
        result['got'] = pairs(SHOP[sid]['item'])
    else:
        raise ValueError('Acción de Patrol no disponible')
    return result
