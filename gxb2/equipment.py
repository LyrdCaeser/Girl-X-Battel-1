"""Offline equipment: gear, Smithy forge, antiques and treasures.

Rules follow PartnerDetailWindow.lua (equip, equip-all, treasure), SmithyWindow.lua (forge),
ArtifactUpWindow.lua (antique upgrade) and EquipTable.lua. partner['equips'] keeps the original
7-slot layout (1 weapon, 2 clothes, 3 accessory, 4 shoes, 5 treasure, 6 antique, 7 skin), which the
recovered battle engine (ReportHero/HeroAttr) reads directly for stats, set bonuses and job bonuses.
Unequipped gear and antiques live in state['items'] like any other bag item.
"""
from __future__ import annotations
import json, secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/equipment.json').read_text())
EQUIP = {int(k): v for k, v in DATA['items'].items()}
PARTNERS = json.loads((ROOT / 'data/partner.json').read_text())
GEAR_SLOTS = (1, 2, 3, 4, 6)          # slots handled by equip/unequip; 5 is the treasure
TREASURE_OPEN = DATA['treasure_open_level']
EXCESS_ID, EXCESS_EXP = 6000, 10      # misc.artifact_upgrade_excess_return = 6000#10
TIERS = {}
for _row in EQUIP.values():
    if _row['pos'] == 5:
        TIERS.setdefault(_row['item_lv'], []).append(_row['id'])


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[int(k)] = out.get(int(k), 0) + int(n)
    return out


def number(value, label, low=0, high=2**31 - 1):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f'{label} inválido')
    return value


def have(state, item):
    return int(state['items'].get(str(item), 0))


def add(state, item, n):
    key = str(item)
    left = int(state['items'].get(key, 0)) + n
    if left < 0:
        raise ValueError('Faltan objetos')
    if left:
        state['items'][key] = left
    else:
        state['items'].pop(key, None)


def charge(state, cost):
    if any(have(state, k) < n for k, n in cost.items()):
        raise ValueError('Faltan recursos para esta acción')
    for k, n in cost.items():
        add(state, k, -n)


def equips_of(partner):
    slots = list(partner.get('equips') or [])
    slots += [0] * (7 - len(slots))
    partner['equips'] = [int(x or 0) for x in slots[:7]]
    return partner['equips']


def job_of(partner):
    return int(PARTNERS[str(partner['table_id'])]['job'])


def fits(item, partner):
    row = EQUIP.get(item)
    return bool(row) and int(row.get('job', 0) or 0) in (0, job_of(partner))


def release(state, partner):
    """Return gear and antique to the bag (used when a girl is consumed as material). Treasures are bound."""
    from . import souls
    souls.release(state, partner)
    slots = equips_of(partner)
    for slot in GEAR_SLOTS:
        if slots[slot - 1]:
            add(state, slots[slot - 1], 1)
            slots[slot - 1] = 0
    if slots[6]:  # the skin (slot 7) also goes back to the bag
        items = state.setdefault('items', {})
        items[str(slots[6])] = int(items.get(str(slots[6]), 0)) + 1
        slots[6] = 0


def pick(tier):
    ids = TIERS[tier]
    total = sum(int(EQUIP[i].get('treasure_weight', 10)) for i in ids)
    roll = secrets.randbelow(total)
    for i in ids:
        roll -= int(EQUIP[i].get('treasure_weight', 10))
        if roll < 0:
            return i
    return ids[-1]


def best_for(state, partner, slot, current):
    """PartnerDetailWindow:onclickBtnEquipAll — highest item_lv, own-job piece wins ties."""
    job = job_of(partner)
    best = None
    for key, count in state['items'].items():
        item = int(key) if key.isdecimal() else 0
        row = EQUIP.get(item)
        if not count or not row or row['pos'] != slot or not fits(item, partner):
            continue
        rank = (row['item_lv'], int(row.get('job', 0) or 0) == job)
        if best is None or rank > best[0]:
            best = (rank, item)
    if not best:
        return current
    old = EQUIP.get(current)
    old_rank = (old['item_lv'], int(old.get('job', 0) or 0) == job) if old else (-1, False)
    return best[1] if best[0] > old_rank else current


def action(state, request, level=None):
    if not isinstance(request, dict):
        raise ValueError('Datos inválidos')
    kind = request.get('action')
    result = {}
    partner = None
    if 'partner_id' in request:
        pid = number(request.get('partner_id'), 'Chica', 1)
        partner = next((p for p in state['partners'] if p['partner_id'] == pid), None)
        if not partner:
            raise ValueError('Chica inexistente')
        slots = equips_of(partner)

    if kind == 'equip':
        item = number(request.get('item_id'), 'Objeto', 1)
        row = EQUIP.get(item)
        if not partner or not row or row['pos'] not in GEAR_SLOTS:
            raise ValueError('Equipo inválido')
        if not fits(item, partner):
            raise ValueError('Esta pieza es de otra clase')
        add(state, item, -1)
        if slots[row['pos'] - 1]:
            add(state, slots[row['pos'] - 1], 1)
        slots[row['pos'] - 1] = item
    elif kind == 'unequip':
        slot = number(request.get('slot'), 'Ranura', 1, 6)
        if not partner or slot not in GEAR_SLOTS or not slots[slot - 1]:
            raise ValueError('Ranura vacía')
        add(state, slots[slot - 1], 1)
        slots[slot - 1] = 0
    elif kind == 'equip_all':
        if not partner:
            raise ValueError('Chica inexistente')
        changed = False
        for slot in GEAR_SLOTS:
            best = best_for(state, partner, slot, slots[slot - 1])
            if best != slots[slot - 1]:
                add(state, best, -1)
                if slots[slot - 1]:
                    add(state, slots[slot - 1], 1)
                slots[slot - 1] = best
                changed = True
        if not changed:
            raise ValueError('No hay equipo mejor en la Bolsa')
    elif kind == 'unequip_all':
        if not partner or not any(slots[s - 1] for s in GEAR_SLOTS):
            raise ValueError('No lleva equipo')
        release(state, partner)
    elif kind == 'forge':
        item = number(request.get('item_id'), 'Objeto', 1)
        count = number(request.get('count', 1), 'Cantidad', 1, 100000)
        need = pairs(EQUIP.get(item, {}).get('need_formula'))
        if not need:
            raise ValueError('Esta pieza no se puede forjar')
        charge(state, {k: n * count for k, n in need.items()})
        add(state, item, count)
        result['forged'] = {str(item): count}
    elif kind == 'forge_auto':
        # SmithyWindow:autoCompose — cascades through one slot's chain, cheapest first.
        pos = number(request.get('pos'), 'Tipo', 1, 4)
        chain = sorted(i for i, r in EQUIP.items() if r['pos'] == pos and r.get('need_formula'))
        made = {}
        for item in chain:
            need = pairs(EQUIP[item]['need_formula'])
            source, per = next((k, n) for k, n in need.items() if k != 1)
            gold = need.get(1, 0)
            count = have(state, source) // per
            if gold:
                count = min(count, have(state, 1) // gold)
            if count:
                charge(state, {source: per * count, 1: gold * count} if gold else {source: per * count})
                add(state, item, count)
                made[str(item)] = count
        if not made:
            raise ValueError('No hay materiales suficientes para forjar')
        result['forged'] = made
    elif kind == 'artifact_upgrade':
        # ArtifactUpWindow: feed antiques until artifact_upg exp; the piece becomes artifact_next.
        item = number(request.get('item_id'), 'Antigüedad', 1)
        row = EQUIP.get(item)
        if not row or row['pos'] != 6 or not row.get('artifact_next'):
            raise ValueError('Esta antigüedad no se puede mejorar')
        feed = request.get('materials')
        if not isinstance(feed, dict) or not feed:
            raise ValueError('Elige materiales')
        feed = {number(int(k), 'Material', 1): number(v, 'Cantidad', 1, 100000) for k, v in feed.items()}
        equipped = partner is not None and slots[5] == item
        if not equipped:
            feed_self = feed.get(item, 0) + 1
            if have(state, item) < feed_self:
                raise ValueError('La antigüedad no está en la Bolsa')
        exp = 0
        for k, n in feed.items():
            mat = EQUIP.get(k)
            if not mat or mat['pos'] != 6 or not mat.get('artifact_exp'):
                raise ValueError('Material inválido')
            exp += int(mat['artifact_exp']) * n
        need = int(row['artifact_upg'])
        if exp < need:
            raise ValueError('Experiencia insuficiente')
        charge(state, feed)
        nxt = int(row['artifact_next'])
        if equipped:
            slots[5] = nxt
        else:
            add(state, item, -1)
            add(state, nxt, 1)
        back = (exp - need) // EXCESS_EXP
        if back:
            add(state, EXCESS_ID, back)
        result.update(upgraded=nxt, returned=back)
    elif kind in ('treasure_on', 'treasure_upgrade', 'treasure_refresh', 'treasure_save', 'treasure_discard'):
        if not partner:
            raise ValueError('Chica inexistente')
        current = slots[4]
        if kind == 'treasure_on':
            if current:
                raise ValueError('El tesoro ya está desbloqueado')
            if int(partner['lv']) < TREASURE_OPEN:
                raise ValueError(f'Disponible desde el nivel {TREASURE_OPEN}')
            slots[4] = pick(1)
        elif not current:
            raise ValueError('Desbloquea primero el tesoro')
        elif kind == 'treasure_upgrade':
            row = EQUIP[current]
            if not row.get('treasure_upgrade'):
                raise ValueError('Tesoro al máximo')
            cost = pairs(row['treasure_upgrade'])
            locked = request.get('lock') is True
            if locked:
                target, extra = row['treasure_lock_up'].split('|')
                for k, n in pairs(extra).items():
                    cost[k] = cost.get(k, 0) + n
            charge(state, cost)
            slots[4] = int(target) if locked else pick(row['item_lv'] + 1)
            partner.pop('tmp_treasure', None)
        elif kind == 'treasure_refresh':
            charge(state, pairs(EQUIP[current]['treasure_refresh']))
            partner['tmp_treasure'] = pick(EQUIP[current]['item_lv'])
        elif kind == 'treasure_save':
            if not partner.get('tmp_treasure'):
                raise ValueError('No hay atributo nuevo')
            slots[4] = partner.pop('tmp_treasure')
        else:
            partner.pop('tmp_treasure', None)
        result['treasure'] = slots[4]
    else:
        raise ValueError('Acción de equipo no disponible')
    return result
