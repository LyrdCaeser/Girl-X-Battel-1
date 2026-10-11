"""Girl skins (Partner.equipments[7] + show_skin, SkinDetailWindow, partner detail "Skins" tab, CollectionSkinWindow).

Recovered from the client:
- A skin is an item (equip pos 7) that fits the girls whose partner.skin_ids list it (the same skin for the 5★, 6★
  and 10★ forms). Wearing it moves it from the bag to the girl (equipments[7]); taking it off returns it.
- Its stats (equip base1/base2, e.g. HP +3 %, Damage reduction +20) are applied by the original HeroAttr, and the
  battle report carries skin_id: the replay draws the skin's chibi (model partner_model) unless show_skin is off.
- Yume Collection · Skins: every skin you have owned gives its collection points (collection.awards 123#n); the points
  reach collection_skin_effect tiers (HP / ATK for every girl).

LOCAL (DESIGN_DECISIONS.md LOCAL-041): the collection HP / ATK tiers are shown but not added to battles yet;
where to get each skin ("Method") is the Skin Shop when it is sold there, otherwise "Exclusive / events".
"""
from __future__ import annotations
import copy, json
from pathlib import Path
from . import local_config

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/skins.json').read_text())
SKINS = {int(k): v for k, v in DATA['skins'].items()}


def saved(state):
    s = state.setdefault('skins', {})
    s.setdefault('collected', [])
    return s


def collected(state):
    """Skins owned at some point: in the bag or worn (Yume Collection keeps them)."""
    s = saved(state)
    have = set(s['collected'])
    for k, n in state.get('items', {}).items():
        if k.isdigit() and int(k) in SKINS and int(n) > 0:
            have.add(int(k))
    for p in state.get('partners', []):
        eq = p.get('equips') or []
        if len(eq) >= 7 and int(eq[6] or 0) in SKINS:
            have.add(int(eq[6]))
    s['collected'] = sorted(have)
    return have


def points(state):
    return sum(int(SKINS[i]['points']) for i in collected(state))


def tier(pts):
    got = [e for e in DATA['effects'] if pts >= e['point']]
    return got[-1] if got else None


def fits(skin, partner):
    return int(partner['table_id']) in SKINS.get(int(skin), {}).get('partners', [])


def action(state, request):
    from .equipment import equips_of
    kind = request.get('action')
    items = state.setdefault('items', {})
    partner = next((p for p in state['partners'] if p['partner_id'] == int(request.get('partner_id', 0))), None)
    if kind in ('equip', 'unequip', 'show') and not partner:
        raise ValueError('Chica no encontrada')
    if kind == 'theme_claim':
        # CollectionSkinWindow themes: collection_skin_group.awards "count#item#num|…" — a reward for owning N skins of a theme
        theme = next((t for t in DATA['themes'] if t['id'] == int(request.get('theme', 0))), None)
        if not theme: raise ValueError('Tema inexistente')
        count = int(request.get('count', 0)); have = collected(state)
        prize = next((p for p in str(theme['awards']).split('|') if p.split('#')[0] == str(count)), None)
        if not prize: raise ValueError('Premio inexistente')
        if sum(1 for x in theme['skins'] if x in have) < count: raise ValueError('Aún no tienes suficientes skins de este tema')
        claimed = state.setdefault('skins', {}).setdefault('theme_claimed', {}).setdefault(str(theme['id']), [])
        if count in claimed: raise ValueError('Ya reclamado')
        _, item, num = prize.split('#'); items[item] = int(items.get(item, 0)) + int(num); claimed.append(count)
        return {'got': {item: int(num)}}
    if kind == 'equip':
        skin = int(request.get('skin', 0))
        if skin not in SKINS or not fits(skin, partner):
            raise ValueError('Esta skin no es de esta chica')
        if int(items.get(str(skin), 0)) < 1:
            raise ValueError('No tienes esta skin (Amount: 0)')
        slots = equips_of(partner)
        if slots[6]:
            items[str(slots[6])] = int(items.get(str(slots[6]), 0)) + 1
        items[str(skin)] = int(items[str(skin)]) - 1
        slots[6] = skin
        partner['show_skin'] = 1
        collected(state)
        return {}
    if kind == 'unequip':
        slots = equips_of(partner)
        if not slots[6]:
            raise ValueError('No lleva ninguna skin')
        items[str(slots[6])] = int(items.get(str(slots[6]), 0)) + 1
        slots[6] = 0
        return {}
    if kind == 'show':
        partner['show_skin'] = 0 if int(partner.get('show_skin', 1) or 0) else 1
        return {}
    if kind == 'buy':
        # Skin Store (SkinDetailBuyWindow, SHOP_SKIN): shop_skin rows sell one skin for Costume Tickets (item 74)
        skin = int(request.get('skin', 0)); row = SKINS.get(skin)
        if not row or not row.get('shop'):
            raise ValueError('Esta skin no se vende en la Skin Store')
        ck, cn = str(row['shop']).split('#')[:2]; cn = local_config.shop_cost(int(cn))
        if int(items.get(ck, 0)) < cn:
            raise ValueError('Not enough Costume Tickets')
        items[ck] = int(items[ck]) - cn
        items[str(skin)] = int(items.get(str(skin), 0)) + 1
        collected(state)
        return {'got': {str(skin): 1}}
    raise ValueError('Acción de skins no disponible')


def snapshot(state):
    have = collected(state)  # updates state['skins']['collected'] (kept at the next save)
    view = copy.deepcopy(state)
    pts = sum(int(SKINS[i]['points']) for i in have)
    items = view.get('items', {})
    got = [e for e in DATA['effects'] if pts >= e['point']]
    nxt = DATA['effects'][len(got)] if len(got) < len(DATA['effects']) else None
    return {'owned': {str(k): int(n) for k, n in items.items() if k.isdigit() and int(k) in SKINS and int(n) > 0},
            'collected': sorted(have), 'points': pts, 'tier': tier(pts), 'total': len(SKINS),
            'level': len(got), 'next_point': nxt['point'] if nxt else None, 'theme_claimed': view.get('skins', {}).get('theme_claimed', {})}


def catalog():
    return {'skins': {str(k): {f: v[f] for f in ('name', 'qlt', 'attrs', 'partners', 'shop', 'points', 'rarity')} for k, v in SKINS.items()},
            'effects': DATA['effects'], 'themes': DATA['themes']}
