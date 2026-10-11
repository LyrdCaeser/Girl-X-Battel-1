"""Anima Gear (models/SoulEquip1.lua, SoulEquip2.lua, SoulEquipInfoWindow, SoulEquip1/2StrengthenWindow, SoulLand summon).

Every girl of Lv 200+ (misc soul_equip_open_lvl) has 5 slots: slot 1 holds an Anima Artifact (soul_equip1: fixed base
buffs × star_grow, level cap soul_equip1_star_lvl[star], random extra buffs from soul_equip1_ex_buff, awaken with copies
of itself), slots 2-5 hold Anima Stones (soul_equip2, one per pos: set group, star, main buff from base/base_weight,
2-4 random extra buffs "id#factor" with factor in soul_equip2_ex_buff_value, quality = awake + 1). Four stones of the same
set give the set skill (ReportHero:getSkillIDs). The partner keeps `souls` (ids per slot) and `soul_infos` (the params of
ReportHero.souls / HeroAttr:getSouls), so attributes and battles use the original formulas.

Local rules where the server is not in the client (LOCAL-045): Anima Stones gain a new extra buff at Lv 5/10/15/20
(soul_equip2_ex_buff_lvl) while they have less than 4; extra buffs of an Artifact are rolled with
soul_equip1_ex_first_cost / soul_equip1_ex_cost and kept or discarded; the Soul Land ritual draws the star from the
dropbox of the current ritual level (weight1 for Soul Token, weight2 for Shiny Soul Token)."""
from __future__ import annotations
import json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/souls.json').read_text())
E1, E2 = D['equip1'], D['equip2']
MISC = D['misc']
OPEN_LV = int(MISC['soul_equip_open_lvl'] or 200)
STAR_LVL = [int(x) for x in MISC['soul_equip1_star_lvl'].split('|')]
EX_NUM1 = [int(x) for x in MISC['soul_equip1_ex_num'].split('|')]
EX_LVL2 = [int(x) for x in MISC['soul_equip2_ex_buff_lvl'].split('#')]
EX_VALUE = [float(x) for x in MISC['soul_equip2_ex_buff_value'].split('|')]
LIMIT = int(MISC['soul_equip_limit'] or 1000)
LV_EXP_BACK = float(MISC['soul_equip2_lvl_exp_cost'] or 0.5)
ESSENCE = 426
STONE_BOX = {5200100 + i: (i - 1) % 4 + 1 for i in range(1, 10)}  # "Random N-star Blue Anima Stone"
ARTIFACT_CHEST = 435


class SoulError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').replace('@', '|').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]
            out[str(k)] = out.get(str(k), 0) + int(float(v))
    return out


def weighted(options, weights, rng):
    total = sum(weights)
    if total <= 0: return options[0]
    roll = rng.random() * total
    for o, w in zip(options, weights):
        roll -= w
        if roll < 0: return o
    return options[-1]


def store(state):
    s = state.setdefault('souls', {})
    s.setdefault('next', 1); s.setdefault('items', {}); s.setdefault('exp', 0)
    return s


def charge(state, cost):
    for k, n in cost.items():
        if int(state['items'].get(str(k), 0)) < n: raise SoulError('Faltan materiales')
    for k, n in cost.items(): state['items'][str(k)] = int(state['items'].get(str(k), 0)) - n


def kind(tid):
    return 1 if str(tid) in E1 else 2


def star(rec):
    return rec['awake'] + 1 if rec['kind'] == 1 else int(E2[str(rec['table_id'])]['star'])


def max_lv(rec):
    if rec['kind'] == 1: return STAR_LVL[min(len(STAR_LVL), star(rec)) - 1]
    return int(E2[str(rec['table_id'])]['max_lvl'])


def roll_ex2(rng, exclude=()):
    ids = [int(k) for k in D['buff2'] if int(k) not in exclude]
    bid = weighted(ids, [int(D['buff2'][str(i)]['weight']) for i in ids], rng)
    return f'{bid}#{round(rng.uniform(EX_VALUE[0], EX_VALUE[-1]), 3)}'


def new_soul(state, tid, rng=None):
    rng = rng or random.SystemRandom()
    s = store(state)
    if len(s['items']) >= LIMIT: raise SoulError('Inventario de Anima Gear lleno')
    tid = int(tid); sid = str(s['next']); s['next'] += 1
    if kind(tid) == 1:
        rec = {'kind': 1, 'table_id': tid, 'lv': 0, 'awake': 0, 'attrs': [], 'lock': 0, 'owner': 0}
    else:
        row = E2[str(tid)]
        bases = [int(x) for x in str(row['base']).split('|')]
        weights = [int(x) for x in str(row['base_weight']).split('|')]
        n = weighted([int(p.split('#')[0]) for p in MISC['soul_equip2_ex_buff_num'].split('|')], [int(p.split('#')[1]) for p in MISC['soul_equip2_ex_buff_num'].split('|')], rng)
        attrs = []
        for _ in range(n): attrs.append(roll_ex2(rng, [int(a.split('#')[0]) for a in attrs]))
        rec = {'kind': 2, 'table_id': tid, 'lv': 0, 'exp': 0, 'awake': 0, 'main': weighted(bases, weights, rng), 'attrs': attrs, 'ex_attrs': [], 'lock': 0, 'owner': 0}
    s['items'][sid] = rec
    return sid


def random_stone(state, star_n, rng, group=None):
    choices = [k for k, r in E2.items() if int(r['star']) == star_n and (group is None or int(r['group']) == group)]
    return new_soul(state, rng.choice(sorted(choices)), rng)


def infos(state, partner):
    """ReportHero.souls / HeroAttr:getSouls params: [artifact, stone pos2..pos5]; {} for an empty slot."""
    items = store(state)['items']
    out = []
    for slot, sid in enumerate((list(partner.get('souls') or []) + [0] * 5)[:5]):
        rec = items.get(str(sid)) if sid else None
        if not rec: out.append({}); continue
        if rec['kind'] == 1:
            out.append({'table_id': rec['table_id'], 'lv': rec['lv'], 'awake': rec['awake'], 'attrs': [int(a) for a in rec['attrs'] if int(a) > 0]})
        else:
            out.append({'table_id': rec['table_id'], 'lv': rec['lv'], 'awake': rec['awake'], 'main': rec['main'], 'attrs': list(rec['attrs']), 'ex_attrs': list(rec['ex_attrs'])})
    return out


def sync(state, partner):
    partner['soul_infos'] = infos(state, partner) if any(partner.get('souls') or []) else []


def sync_owner(state, rec):
    if rec.get('owner'):
        p = next((g for g in state['partners'] if g['partner_id'] == rec['owner']), None)
        if p: sync(state, p)


def release(state, partner):
    """The girl leaves (material, reverse): her Anima Gear goes back to the bag."""
    items = store(state)['items']
    for sid in partner.get('souls') or []:
        if sid and str(sid) in items: items[str(sid)]['owner'] = 0
    partner['souls'] = [0] * 5; partner['soul_infos'] = []


def free(state, sid):
    rec = store(state)['items'].get(str(sid))
    if not rec: raise SoulError('Anima Gear inexistente')
    if rec.get('owner') or rec.get('lock'): raise SoulError('Está equipada o bloqueada')
    return rec


def add_exp2(rec, exp, rng):
    rec['exp'] = int(rec.get('exp', 0)) + exp
    cap = max_lv(rec)
    while rec['lv'] < cap:
        need = int(D['exp2'][str(rec['lv'] + 1)]['cost'])
        if rec['exp'] < need: break
        rec['exp'] -= need; rec['lv'] += 1
        if rec['lv'] in EX_LVL2 and len(rec['attrs']) + len(rec['ex_attrs']) < 4:
            have = [int(a.split('#')[0]) for a in rec['attrs'] + rec['ex_attrs']]
            rec['ex_attrs'].append(roll_ex2(rng, have))
    if rec['lv'] >= cap: rec['exp'] = 0


def action(state, request, rng=None):
    rng = rng or random.SystemRandom()
    s = store(state); items = s['items']; act = request.get('action')
    def partner():
        p = next((g for g in state['partners'] if g['partner_id'] == int(request.get('partner_id') or 0)), None)
        if not p: raise SoulError('No tienes esa chica')
        return p
    def soul():
        rec = items.get(str(request.get('soul_id')))
        if not rec: raise SoulError('Anima Gear inexistente')
        return rec
    if act == 'equip':
        p = partner(); rec = soul()
        if int(p['lv']) < OPEN_LV: raise SoulError(f'Anima Gear se abre con la chica a nivel {OPEN_LV}')
        slot = 0 if rec['kind'] == 1 else int(E2[str(rec['table_id'])]['pos']) - 1
        if rec.get('owner') and rec['owner'] != p['partner_id']:
            old = next((g for g in state['partners'] if g['partner_id'] == rec['owner']), None)
            if old:
                old['souls'] = [0 if x == int(request['soul_id']) else x for x in old.get('souls') or []]; sync(state, old)
        souls = (list(p.get('souls') or []) + [0] * 5)[:5]
        if souls[slot] and str(souls[slot]) in items: items[str(souls[slot])]['owner'] = 0
        souls[slot] = int(request['soul_id']); rec['owner'] = p['partner_id']; p['souls'] = souls; sync(state, p)
        return {}
    if act == 'unequip':
        p = partner(); souls = (list(p.get('souls') or []) + [0] * 5)[:5]
        slots = [int(request['slot']) - 1] if request.get('slot') else range(5)
        for i in slots:
            if souls[i] and str(souls[i]) in items: items[str(souls[i])]['owner'] = 0
            souls[i] = 0
        p['souls'] = souls; sync(state, p)
        return {}
    if act == 'lock':
        rec = soul(); rec['lock'] = 0 if rec.get('lock') else 1
        return {}
    if act == 'lv_up':
        rec = soul(); cap = max_lv(rec)
        if rec['lv'] >= cap: raise SoulError('Nivel máximo para su estrella')
        if rec['kind'] == 1:
            times = max(1, min(int(request.get('times') or 1), cap - rec['lv']))
            for _ in range(times):
                if rec['lv'] >= cap: break
                charge(state, pairs(D['exp1'][str(rec['lv'] + 1)]['cost'])); rec['lv'] += 1
        else:
            exp = 0
            essence = max(0, int(request.get('essence') or 0))
            if essence: charge(state, {str(ESSENCE): essence}); exp += essence
            for fid in request.get('feed') or []:
                if str(fid) == str(request.get('soul_id')): raise SoulError('No puedes usarla consigo misma')
                f = free(state, fid)
                if f['kind'] != 2: raise SoulError('Solo Anima Stones como material')
                exp += int(E2[str(f['table_id'])]['exp']) + int(int(D['exp2'][str(f['lv'])]['all_exp']) * LV_EXP_BACK if f['lv'] else 0)
                del items[str(fid)]
            if exp <= 0: raise SoulError('Elige Soul Essence o Anima Stones')
            add_exp2(rec, exp, rng)
        sync_owner(state, rec)
        return {'soul': rec}
    if act == 'awake':
        rec = soul()
        if rec['kind'] == 1:
            row = E1[str(rec['table_id'])]
            if star(rec) >= int(row['max_star']): raise SoulError('Estrellas al máximo')
            need = pairs(str(row['material']).split('|')[rec['awake']])
            used = []
            for tid, n in need.items():
                pool = [k for k, r in items.items() if k != str(request['soul_id']) and r['table_id'] == int(tid) and not r.get('owner') and not r.get('lock')]
                pool.sort(key=lambda k: (items[k]['lv'], items[k]['awake']))
                if len(pool) < n: raise SoulError('Necesitas copias libres del mismo Anima Artifact')
                used += pool[:n]
            for k in used: del items[k]
            rec['awake'] += 1
            while len(rec['attrs']) < EX_NUM1[star(rec) - 1]: rec['attrs'].append(0)
        else:
            row = E2[str(rec['table_id'])]
            if rec['awake'] + 1 >= int(row['max_qlt']): raise SoulError('Calidad al máximo')
            charge(state, pairs(str(row['material']).split('|')[rec['awake']])); rec['awake'] += 1
        sync_owner(state, rec)
        return {'soul': rec}
    if act == 'roll_ex':
        # SoulEquip1StrengthenWindow: extra buff slots opened by star (soul_equip1_ex_num[star]); the new roll waits in
        # `replace` until it is kept or discarded
        rec = soul()
        if rec['kind'] != 1: raise SoulError('Solo los Anima Artifact')
        slot = int(request.get('slot') or 1) - 1
        opened = EX_NUM1[star(rec) - 1]
        while len(rec['attrs']) < opened: rec['attrs'].append(0)
        if not 0 <= slot < opened: raise SoulError('Ranura de atributo bloqueada')
        charge(state, pairs(MISC['soul_equip1_ex_first_cost'] if not rec['attrs'][slot] else MISC['soul_equip1_ex_cost']))
        ids = [int(k) for k in D['buff1']]
        new = weighted(ids, [int(D['buff1'][str(i)]['weight']) for i in ids], rng)
        if not rec['attrs'][slot]: rec['attrs'][slot] = new
        else: rec['replace'] = {'slot': slot, 'id': new}
        sync_owner(state, rec)
        return {'soul': rec}
    if act in ('save_ex', 'discard_ex'):
        rec = soul(); rep = rec.pop('replace', None)
        if act == 'save_ex' and rep: rec['attrs'][rep['slot']] = rep['id']
        sync_owner(state, rec)
        return {'soul': rec}
    if act == 'open':
        # Random N-star Anima Stone boxes and the Random Anima Artifact Chest
        iid = int(request.get('item_id') or 0); n = max(1, min(int(request.get('count') or 1), 50))
        if iid not in STONE_BOX and iid != ARTIFACT_CHEST: raise SoulError('Ese objeto no se abre aquí')
        charge(state, {str(iid): n}); got = []
        for _ in range(n):
            got.append(random_stone(state, STONE_BOX[iid], rng) if iid in STONE_BOX else new_soul(state, rng.choice(sorted(E1)), rng))
        return {'got': got}
    if act == 'summon':
        # Anima Stone Ritual (soul_land_equip2_gacha): the dropbox follows the ritual exp; each draw adds gacha.exp
        g = D['gacha'].get(str(request.get('gacha') or 1))
        if not g: raise SoulError('Ritual inexistente')
        times = 10 if int(request.get('times') or 1) >= 10 else 1
        charge(state, {k: v * times for k, v in pairs(g['cost']).items()}); got = []
        for _ in range(times):
            box = box_for(s['exp'])
            stars = [1, 2, 3, 4, 5, 6]; w = [int(x) for x in str(box['weight1' if int(g['dropbox_type']) == 1 else 'weight2']).split('|')]
            got.append(random_stone(state, weighted(stars, w, rng), rng, rng.choice([int(x) for x in str(box['equip2']).split('|')])))
            s['exp'] += int(g['exp'])
        return {'got': got}
    raise SoulError('Acción de Anima Gear desconocida')


def box_for(exp):
    box = D['dropbox']['1']
    while True:
        nxt = D['dropbox'].get(str(box.get('next_id') or 0))
        if not nxt or exp < int(box['exp']): return box
        box = nxt


def snapshot(state):
    s = store(state)
    return {'items': s['items'], 'exp': s['exp'], 'level': int(box_for(s['exp'])['id']), 'open_lv': OPEN_LV, 'limit': LIMIT}


def grant_dev(state, rng=None):
    """Developer save: one of every Anima Artifact and a full 6★ set of every group."""
    rng = rng or random.SystemRandom()
    s = store(state)
    if s.get('dev_granted'): return
    for tid in sorted(E1): new_soul(state, tid, rng)
    for tid, r in sorted(E2.items()):
        if int(r['star']) == 6: new_soul(state, tid, rng)
    s['dev_granted'] = 1


def catalog():
    return D
