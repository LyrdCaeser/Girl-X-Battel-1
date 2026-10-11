"""Outfits (models/Dress.lua, DressMainWindow, DressItemUpWindow, DressSummonWindow, SenpaiModel) offline.

Recovered from the client:
- 288 pieces (senpai_dress) in 5 positions: head, body, legs, headwear, accessory; each piece has 1-2 styles
  (senpai_dress_style: icon + Spine resource for head/body/legs, slot image + offset for headwear/accessory) and one
  item per star (senpai_dress_item: Courage/Charisma/Knowledge = base1/2/3, quality 1-6, max star by quality).
- Upgrade (DressItemUpWindow): `upgrade_cost` (Plain Silk 260, Dyed Silk 261 and the piece's own shards) plus
  `upgrade_cost2` = common fragments by quality (misc dress_common_fragment_qlt_item_ids "qlt#n").
- Sets (senpai_dress_group): the total stars of the set's pieces unlock its special bonuses (unlock_stars 5..30);
  they work without being worn. Slots 1-3 can't be emptied (senpai_dress_slot.can_rm); body and legs styles may
  collide (senpai_dress_collide → the other one goes back to the default).
- Outfit Store / Outfit Sale (summon_dress 1 / 3, Plain Button 258 / Fancy Button 259): normal pieces from dropbox
  50001 / 50003; an orange draw (dropbox 50002 / 50004) has weight 1500 / 100000, +400 per draw after 50 misses and
  is guaranteed at 100 (misc dress_gacha_*). Free draw every 24 h (Store) / 12 h (Sale). A piece you already own
  becomes its shards (senpai_dress.dress_shard).

LOCAL (DESIGN_DECISIONS.md LOCAL-040): the server summed the attributes; here Courage/Charisma/Knowledge = the sum of
base1/2/3 of every owned piece at its star (+ the draw-count bonus of skill 1000101). Special bonus effects that act on
other systems are shown but only the attributes are applied. Outfit Sale is always open offline. Common fragments of
the upgrade are taken automatically (the client let you choose which ones to spend).
"""
from __future__ import annotations
import copy, json, random, secrets, time
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data/dress.json').read_text())
M = DATA['misc']
PIECES = {int(d['id']): d for d in DATA['dress']}
ITEMS = {int(i['id']): i for i in DATA['items']}
STYLES = {int(s['id']): s for s in DATA['styles']}
SLOTS = {int(s['id']): s for s in DATA['slots']}
GROUPS = {int(g['id']): g for g in DATA['groups']}
COMMON = [int(x) for x in str(M['dress_common_fragment_qlt_item_ids']).split('|')]
TOTAL = int(M['dress_gacha_weight_total'])
ORANGE_W = int(M['dress_gacha_weight_get1'])
ADD_AFTER, ADD_W = (int(x) for x in str(M['dress_gacha_weight_add']).split('|'))
PITY = int(M['dress_gacha_max_drop'])
BOXES = {1: (int(M['dress_gacha_dropbox4']), int(M['dress_gacha_dropbox1'])), 2: (int(M['dress_gacha_dropbox5']), int(M['dress_gacha_dropbox2']))}
COST = {1: '258', 2: '259'}
FREE = {1: int(str(M['dress_gacha_free1']).split('|')[0]), 2: int(str(M['dress_gacha_free2']).split('|')[0])}
POS_NAMES = {1: 'Head', 2: 'Body', 3: 'Legs', 4: 'Headwear', 5: 'Accessories'}


def ids(text):
    return [int(float(x)) for x in str(text or '').split('|') if x not in ('', None, '0')]


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[k] = out.get(k, 0) + int(float(n))
    return out


def piece_items(did):
    return ids(PIECES[did]['items'])


def item_of(did, star):
    its = piece_items(did)
    return its[max(1, min(star, len(its))) - 1]


def max_star(did):
    return len(piece_items(did))


def styles_of(did):
    return ids(PIECES[did]['styles'])


def shard_of(did):
    p = pairs(PIECES[did].get('dress_shard'))
    return next(iter(p.items()), (None, 0))


def saved(state):
    d = state.setdefault('dress', {})
    if 'owned' not in d:
        d['owned'] = {}
        for s in SLOTS.values():
            if s['default_item']:
                it = ITEMS[int(s['default_item'])]
                d['owned'][str(it['dress_id'])] = int(it['star'])
        d['style'] = {}
        d['equipped'] = [int(SLOTS[i]['default_style'] or 0) for i in range(1, 6)]
        d['pity'] = {'1': 0, '2': 0}; d['free'] = {'1': 0, '2': 0}; d['draws'] = 0
    return d


def owned_star(d, did):
    return int(d['owned'].get(str(did), 0))


def attrs(state):
    d = saved(state)
    a = [0, 0, 0]
    for did, star in d['owned'].items():
        it = ITEMS.get(item_of(int(did), int(star)))
        if not it: continue  # pieces without items in the client (see ORPHANS)
        for i in range(3):
            a[i] += int(float(it.get(f'base{i + 1}') or 0))
    # skill 1000101 family: +1 to all per 20 draws (the best owned level's cap)
    act = set(active_skills(state))
    caps = [s for s in DATA['skills'] if str(s.get('first_id')) == '1000101' and int(s['id']) in act]
    if caps:
        cap, every, gain = (int(x) for x in str(caps[-1]['num']).split('|'))
        bonus = min(cap, int(d['draws']) // every) * gain
        a = [x + bonus for x in a]
    return a


def group_stars(d, g):
    return sum(owned_star(d, did) for did in ids(g['unit']))


def active_skills(state):
    d = state.get('dress') or {}
    out = []
    for g in GROUPS.values():
        skills, need = ids(g['skills']), ids(g['unlock_stars'])
        total = sum(int(d.get('owned', {}).get(str(did), 0)) for did in ids(g['unit']))
        got = [s for s, n in zip(skills, need) if total >= n]
        if got:
            out.append(got[-1])
    return out


def collides(style_a, style_b):
    ca, cb = STYLES[style_a].get('collide'), STYLES[style_b].get('collide')
    if not ca or not cb:
        return False
    return str(int(cb)) in str(DATA['collide'].get(str(int(ca)), '')).split('|')


def roll(box, rng):
    from .engine import TABLES
    rows = [r for r in TABLES['dropbox'].values() if int(r['dropbox_id']) == box and int(r['weight']) > 0]
    x = rng.randrange(sum(int(r['weight']) for r in rows))
    for r in rows:
        x -= int(r['weight'])
        if x < 0:
            return int(str(r['item']).split('#')[0])
    return int(str(rows[-1]['item']).split('#')[0])


def grant(state, item_id):
    """A drawn piece: new → owned at its star; already owned → its shards (senpai_dress.dress_shard)."""
    d = saved(state)
    it = ITEMS[item_id]
    did = int(it['dress_id'])
    if owned_star(d, did):
        k, n = shard_of(did)
        items = state.setdefault('items', {})
        items[k] = int(items.get(k, 0)) + n
        return {'item': item_id, 'dress': did, 'new': False, 'shards': {k: n}}
    d['owned'][str(did)] = int(it['star'])
    return {'item': item_id, 'dress': did, 'new': True}


def summon(state, kind, count, now, rng):
    d = saved(state)
    items = state.setdefault('items', {})
    key = str(kind)
    free = count == 1 and now >= int(d['free'].get(key, 0)) + FREE[kind]
    if not free:
        if int(items.get(COST[kind], 0)) < count:
            raise ValueError('No tienes suficientes ' + ('Plain Buttons' if kind == 1 else 'Fancy Buttons'))
        items[COST[kind]] = int(items[COST[kind]]) - count
        from . import growth_diary
        growth_diary.record(state,'growth_buttons',count)
    else:
        d['free'][key] = now
    normal_box, orange_box = BOXES[kind]
    results = []
    for _ in range(count):
        miss = int(d['pity'].get(key, 0))
        w = ORANGE_W + max(0, miss + 1 - ADD_AFTER) * ADD_W
        orange = miss + 1 >= PITY or rng.randrange(TOTAL) < w
        item = roll(orange_box if orange else normal_box, rng)
        d['pity'][key] = 0 if orange else miss + 1
        d['draws'] = int(d['draws']) + 1
        results.append({**grant(state, item), 'orange': orange})
    return results


def upgrade_cost(d, did):
    star = owned_star(d, did)
    it = ITEMS[item_of(did, star)]
    if not it.get('next_id'):
        return None
    cost = pairs(it.get('upgrade_cost'))
    for q, n in pairs(it.get('upgrade_cost2')).items():
        cost[f'qlt{q}'] = cost.get(f'qlt{q}', 0) + n
    return cost


def pay(state, cost):
    """Silk + own shards from the bag; 'qltN' from common fragments of quality N (auto)."""
    items = state.setdefault('items', {})
    for k, n in cost.items():
        have = int(items.get(str(COMMON[int(k[3:]) - 1]), 0)) if k.startswith('qlt') else int(items.get(k, 0))
        if have < n:
            raise ValueError('Faltan materiales para mejorar la pieza')
    for k, n in cost.items():
        key = str(COMMON[int(k[3:]) - 1]) if k.startswith('qlt') else k
        items[key] = int(items[key]) - n


def action(state, request, now=None, seed=None):
    now = int(time.time()) if now is None else now
    d = saved(state)
    kind = request.get('action')
    rng = random.Random(seed if seed is not None else secrets.randbits(32))
    if kind == 'open':
        return {}
    if kind == 'equip':
        pos, style = int(request.get('pos', 0)), int(request.get('style', 0))
        if pos not in SLOTS:
            raise ValueError('Posición no válida')
        eq = list(d['equipped'])
        if not style:
            if not int(SLOTS[pos]['can_rm']):
                raise ValueError('Esta pieza no se puede quitar')
            eq[pos - 1] = 0
        else:
            st = STYLES.get(style)
            if not st or int(st['pos']) != pos or not owned_star(d, int(st['dress_id'])):
                raise ValueError('No tienes esa pieza')
            eq[pos - 1] = style
            other = {2: 3, 3: 2}.get(pos)
            if other and eq[other - 1] and collides(style, eq[other - 1]):
                eq[other - 1] = int(SLOTS[other]['default_style'] or 0)  # DressMainWindow: the colliding piece goes back
            d['style'][str(st['dress_id'])] = style
        d['equipped'] = eq
        return {}
    if kind == 'save':  # Locker Room edit (capture 2026-09-29-i/02: Cancel / Save)
        new = [int(x or 0) for x in (request.get('styles') or [])][:5]
        if len(new) != 5:
            raise ValueError('Conjunto no válido')
        for pos, style in enumerate(new, 1):
            if style:
                st = STYLES.get(style)
                if not st or int(st['pos']) != pos or not owned_star(d, int(st['dress_id'])):
                    raise ValueError('No tienes esa pieza')
            elif not int(SLOTS[pos]['can_rm']):
                raise ValueError('Cabeza, cuerpo y piernas no se pueden quitar')
        if new[1] and new[2] and collides(new[1], new[2]):
            raise ValueError('Esa parte de arriba y esa parte de abajo no se pueden combinar')
        d['equipped'] = new
        return {}
    if kind == 'upgrade':
        did = int(request.get('dress', 0))
        if not owned_star(d, did):
            raise ValueError('No tienes esa pieza')
        cost = upgrade_cost(d, did)
        if cost is None:
            raise ValueError('Reached Max Level!')
        before = attrs(state)
        pay(state, cost)
        d['owned'][str(did)] = owned_star(d, did) + 1
        return {'before': before, 'after': attrs(state), 'star': owned_star(d, did)}
    if kind == 'summon':
        k, count = int(request.get('kind', 1)), int(request.get('count', 1))
        if k not in (1, 2) or count not in (1, 10):
            raise ValueError('Tirada no válida')
        return {'results': summon(state, k, count, now, rng)}
    raise ValueError('Acción de Outfits no disponible')


def snapshot(state, now=None):
    now = int(time.time()) if now is None else now
    view = copy.deepcopy(state)
    d = saved(view)
    items = view.get('items', {})
    pieces = []
    for did, star in d['owned'].items():
        did = int(did)
        cost = upgrade_cost(d, did)
        pieces.append({'dress': did, 'star': int(star), 'max': max_star(did), 'cost': cost})
    return {'attrs': attrs(view), 'equipped': d['equipped'], 'style': d['style'], 'owned': pieces, 'skills': active_skills(view),
            'pity': d['pity'], 'draws': d['draws'], 'max_drop': PITY,
            'free': {k: max(0, int(d['free'].get(k, 0)) + FREE[int(k)] - now) for k in ('1', '2')},
            'buttons': {'258': int(items.get('258', 0)), '259': int(items.get('259', 0))},
            'silk': {'260': int(items.get('260', 0)), '261': int(items.get('261', 0))},
            'common': {str(i + 1): int(items.get(str(c), 0)) for i, c in enumerate(COMMON)}}


def catalog():
    """Static data for the UI (loaded once)."""
    return {'pieces': {str(k): {'pos': int(v['pos']), 'group': int(v['group'] or 0), 'styles': styles_of(k), 'items': piece_items(k),
                                'shard': shard_of(k)[0], 'name': DATA['names'].get(str(piece_items(k)[0]), '')} for k, v in PIECES.items()},
            'items': {str(k): {'star': int(v['star']), 'qlt': int(v['qlt']), 'base': [int(float(v.get(f'base{i}') or 0)) for i in (1, 2, 3)],
                               'icon': str(v['icon']).split('|')} for k, v in ITEMS.items()},
            'styles': {str(k): {'pos': int(v['pos']), 'dress': int(v['dress_id']), 'image': v['image'], 'res': v['resource'], 'slot': v.get('slot') or '',
                                'offset': [float(x) for x in str(v.get('offset') or '0|0').split('|')], 'scale': [float(x) for x in str(v.get('scale') or '1|1').split('|')],
                                'rotation': float(v.get('rotation') or 0)} for k, v in STYLES.items()},
            'groups': {str(k): {'name': DATA['group_names'].get(str(k), ''), 'unit': ids(v['unit']), 'skills': ids(v['skills']), 'need': ids(v['unlock_stars'])}
                       for k, v in GROUPS.items()},
            'skill_text': DATA['skill_text'], 'slots': {str(k): {'can_rm': int(v['can_rm']), 'default': int(v['default_style'] or 0), 'name': POS_NAMES[k]} for k, v in SLOTS.items()},
            'common': COMMON, 'item_names': DATA['item_names'], 'shard_names': DATA['shard_names']}
