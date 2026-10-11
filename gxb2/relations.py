"""Relationships (DatesWindow.lua / DatesPledgeWindow.lua / DatesGiftsWindow.lua).

Recovered: intimacy caps (misc.love_point_max_base 10000, love_point_max_grow 12000 after the Oath), gift points
love_gift_point "0|20|40" (disliked / normal / liked, likes = partner.gift_type1, dislikes = gift_type2), gift ids
love_gift_item_num, Oath cost love_point_vow_cost (45#1, requires the base cap), gift compose love_gift_cost (44#10),
appointment levels (icons and atk/hp bonuses, read by HeroAttr through partner.love_point / is_vowed).
Make (DatesGiftsWindow): the chosen gift, love_gift_cost (10 Gift Shards) each, gifts grouped Food / Toy / Accessory /
Variety (dates_gifts). Gift Box (item 43, gift 30001): one gift from dropbox 800001 + 3-5 Gift Shards (800002).
LOCAL: starter gifts love_gift_initial are granted once on the first visit (the original granted them server-side).
"""
from __future__ import annotations
import json, secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/relations.json').read_text())
PARTNERS = json.loads((ROOT / 'data/partner.json').read_text())
RULES = DATA['rules']
BASE_MAX = int(RULES['love_point_max_base'])
VOW_MAX = int(RULES['love_point_max_grow'])
POINTS = [int(x) for x in RULES['love_gift_point'].split('|')]
FIRST, COUNT = [int(x) for x in RULES['love_gift_item_num'].split('|')]
PLOT = json.loads((ROOT / 'data/partner_plot.json').read_text()) if (ROOT / 'data/partner_plot.json').exists() else {'lines': {}, 'titles': {}}
CHAINS = {int(k): v for k, v in DATA.get('dates_chain', {}).items()}
ACH = DATA.get('achievements', {})


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[k] = out.get(k, 0) + int(n)
    return out


def likes(table_id):
    row = PARTNERS.get(str(table_id), {})
    split = lambda v: {int(x) for x in str(v or '').split('|') if x.strip().isdigit()}
    return split(row.get('gift_type1')), split(row.get('gift_type2'))


# ---- Date (DatesStoryWindow, partner_achievement): each chain step is a task (3 girl level, 4 intimacy, 6 background
# girl, 2 forge N gears, 5 consume items) that unlocks its story (partner_plot). LOCAL (LOCAL-073): the server tracked
# the tasks; here levels / intimacy / wallpaper / forges are read from the save and "consume" tasks are paid on completion.
def chain_key(table_id):
    """The chain belongs to the girl's base id (re-issues share it through partner.show_ids)."""
    tid = int(table_id)
    if tid in CHAINS: return tid
    row = PARTNERS.get(str(tid), {})
    for x in str(row.get('show_ids') or '').split('|'):
        if x.strip().isdigit() and int(x) in CHAINS: return int(x)
    return 0


def _same(state, tid):
    ids = {int(tid)}
    for x in str(PARTNERS.get(str(tid), {}).get('show_ids') or '').split('|'):
        if x.strip().isdigit(): ids.add(int(x))
    return [p for p in state.get('partners', []) if int(p['table_id']) in ids or int(p['table_id']) % 100000 == int(tid) % 100000]


def step_status(state, ach_id):
    a = ACH.get(str(ach_id)) or {}
    t, v = int(a.get('type') or 0), str(a.get('value') or '')
    if t in (3, 4):
        tid, need = [int(x) for x in v.split('#')]
        girls = _same(state, tid)
        have = max([int(p.get('lv', 0) if t == 3 else p.get('love_point', 0)) for p in girls] or [0])
        return have >= need, have, need
    if t == 6:
        wp = [int(x) for x in (state.get('profile') or {}).get('wallpapers') or []]
        ok = any(w == int(v) or w % 100000 == int(v) % 100000 for w in wp)
        return ok, int(ok), 1
    if t == 2:
        have = int(((state.get('missions') or {}).get('totals') or {}).get('forge', 0))
        return have >= int(v), have, int(v)
    if t == 5:
        k, n = v.split('#')[:2]
        return int(state['items'].get(k, 0)) >= int(n), int(state['items'].get(k, 0)), int(n)
    return False, 0, 1


def dates_info(state):
    done = state.get('dates_progress') or {}
    out = {}
    for tid, chain in CHAINS.items():
        n = int(done.get(str(tid), 0))
        cur = chain[n] if n < len(chain) else 0
        ok, have, need = step_status(state, cur) if cur else (False, 0, 0)
        out[str(tid)] = {'done': n, 'chain': chain, 'current': cur, 'ready': ok, 'have': have, 'need': need}
    return out


def plot_scene(start):
    out, seen, cur = [], set(), int(start)
    while cur and str(cur) in PLOT['lines'] and cur not in seen and len(out) < 400:
        seen.add(cur); out.append(PLOT['lines'][str(cur)]); cur = int(PLOT['lines'][str(cur)].get('x') or 0)
    return out


def _wedding_map():
    """Girl table id → her wedding skin (a skin whose partner_picture row has is_wedding = 1)."""
    try:
        skins = json.loads((ROOT / 'data/skins.json').read_text())['skins']
        pics = json.loads((ROOT / 'data/partner_pictures.json').read_text())
    except (OSError, ValueError, KeyError):
        return {}
    out = {}
    for sid, row in skins.items():
        if int((pics.get(sid) or {}).get('wed') or 0):
            for p in row.get('partners') or []:
                out.setdefault(int(p), int(sid))
    return out


WEDDING = _wedding_map()


def wedding_skin(table_id):
    tid = int(table_id)
    if tid in WEDDING: return WEDDING[tid]
    for x in str(PARTNERS.get(str(tid), {}).get('show_ids') or '').split('|'):
        if x.strip().isdigit() and int(x) in WEDDING: return WEDDING[int(x)]
    return 0


# ---- Discuss → Partner Data Station (PartnerCommentComponent). LOCAL (LOCAL-074): comments, likes and the player's own
# labels lived on the online server; here they are the player's own notes, kept in the save per comment id.
STATION = json.loads((ROOT / 'web/assets/station/station.json').read_text()) if (ROOT / 'web/assets/station/station.json').exists() else {'girls': {}, 'labels': {}}
STATION_KINDS = ('station', 'station_like', 'station_labels', 'station_comment', 'station_delete')
COMMENT_MIN, COMMENT_MAX = 12, 400  # misc partner_comment_length_limit_en_en
LABEL_MAX = 3


def station_action(state, request):
    kind, cid = request.get('action'), str(request.get('id', ''))
    if cid not in STATION['girls']:
        raise ValueError('Esta chica no tiene ficha')
    box = state.setdefault('station', {})
    rec = box.get(cid) or {'like': 0, 'labels': [], 'comments': []}
    if kind == 'station_like':
        rec['like'] = 1
    elif kind == 'station_labels':
        labels = [int(x) for x in request.get('labels') or []]
        if len(labels) > LABEL_MAX or len(set(labels)) != len(labels) or any(str(x) not in STATION['labels'] for x in labels):
            raise ValueError(f'Elige hasta {LABEL_MAX} etiquetas')
        rec['labels'] = labels
    elif kind == 'station_comment':
        ids = set(STATION['girls'][cid]['ids'])
        if not any(int(p['table_id']) in ids for p in state.get('partners', [])):
            raise ValueError('Consigue a esta chica para comentar')  # PARTNER_COMMENT_LOCKED
        msg = str(request.get('text') or '').strip()
        if len(msg) < COMMENT_MIN: raise ValueError(f'El comentario necesita al menos {COMMENT_MIN} caracteres')
        if len(msg) > COMMENT_MAX: raise ValueError(f'Máximo {COMMENT_MAX} caracteres')
        rec['comments'].insert(0, {'text': msg, 'time': int(request.get('_now') or __import__('time').time())})
    elif kind == 'station_delete':
        i = int(request.get('index', -1))
        if not 0 <= i < len(rec['comments']): raise ValueError('Comentario inexistente')
        rec['comments'].pop(i)
    if kind != 'station':
        box[cid] = rec
    from . import bots
    world = bots.comments('girl:' + cid, int(request.get('_now') or __import__('time').time()))  # LOCAL-085: other players' reviews are bots
    return {'station': rec, 'hot': world['hot'], 'likes': world['likes'] + int(rec.get('like') or 0)}


def cap(partner):
    return VOW_MAX if partner.get('is_vowed') else BASE_MAX


def action(state, request, rng=secrets.randbelow):
    if not isinstance(request, dict):
        raise ValueError('Datos inválidos')
    kind = request.get('action')
    result = {}
    if kind == 'visit':
        if not state.get('relations_init'):
            for k, n in pairs(RULES['love_gift_initial']).items():
                state['items'][k] = int(state['items'].get(k, 0)) + n
            state['relations_init'] = True
        return result
    if kind == 'compose':
        times = int(request.get('count', 1))
        if times < 1:
            raise ValueError('Cantidad inválida')
        item = int(request.get('item_id', 0) or 0)
        if not FIRST <= item < FIRST + COUNT:
            raise ValueError('Elige un regalo')
        cost = {k: n * times for k, n in pairs(RULES['love_gift_cost']).items()}
        if any(int(state['items'].get(k, 0)) < n for k, n in cost.items()):
            raise ValueError('Faltan fragmentos de regalo')
        for k, n in cost.items():
            state['items'][k] = int(state['items'].get(k, 0)) - n
        state['items'][str(item)] = int(state['items'].get(str(item), 0)) + times
        result['got'] = {str(item): times}
        return result
    if kind == 'open_box':
        times = int(request.get('count', 1))
        if times < 1 or int(state['items'].get('43', 0)) < times:
            raise ValueError('No tienes Gift Boxes')
        state['items']['43'] = int(state['items']['43']) - times
        got = {}
        for _ in range(times):
            for rows in DATA['gift_box'].values():
                total = sum(w for _, w in rows); x = rng(total) if total else 0
                for item, w in rows:
                    x -= w
                    if x < 0:
                        k, lo, *hi = item.split('#'); lo = int(lo); n = lo + (rng(int(hi[0]) - lo + 1) if hi and int(hi[0]) > lo else 0)
                        got[k] = got.get(k, 0) + n; break
        for k, n in got.items():
            state['items'][k] = int(state['items'].get(k, 0)) + n
        result['got'] = got
        return result
    if kind == 'date_step':
        tid = chain_key(request.get('table_id', 0))
        if not tid: raise ValueError('This Girl currently has no story')
        prog = state.setdefault('dates_progress', {}); n = int(prog.get(str(tid), 0)); chain = CHAINS[tid]
        if n >= len(chain): raise ValueError('All stories unlocked')
        ach = chain[n]; ok, _, _ = step_status(state, ach)
        if not ok: raise ValueError(ACH[str(ach)]['desc'])
        a = ACH[str(ach)]
        if int(a['type']) == 5:
            k, c = str(a['value']).split('#')[:2]; state['items'][k] = int(state['items'][k]) - int(c)
        prog[str(tid)] = n + 1
        result.update(plot=int(a.get('plot') or 0), achievement=ach)
        return result
    if kind in STATION_KINDS:
        return station_action(state, request)
    pid = request.get('partner_id')
    partner = next((p for p in state['partners'] if p['partner_id'] == pid), None)
    if not partner:
        raise ValueError('Chica inexistente')
    partner.setdefault('love_point', 0)
    if kind == 'gift':
        item = int(request.get('item_id', 0)); num = int(request.get('num', 1))
        if not FIRST <= item < FIRST + COUNT or num < 1:
            raise ValueError('Regalo inválido')
        if int(state['items'].get(str(item), 0)) < num:
            raise ValueError('No tienes suficientes regalos')
        if partner['love_point'] >= cap(partner):
            raise ValueError('La intimidad ya está al máximo')
        like, dislike = likes(partner['table_id'])
        per = POINTS[2] if item in like else POINTS[0] if item in dislike else POINTS[1]
        state['items'][str(item)] = int(state['items'][str(item)]) - num
        before = partner['love_point']
        partner['love_point'] = min(cap(partner), before + per * num)
        result.update(delta=partner['love_point'] - before, reaction=25 if item in like else 23 if item in dislike else 24)
    elif kind == 'vow':
        if partner.get('is_vowed'):
            raise ValueError('Ya habéis hecho el Oath')
        if partner['love_point'] < BASE_MAX:
            raise ValueError(f'Necesitas {BASE_MAX} de intimidad')
        cost = pairs(RULES['love_point_vow_cost'])
        if any(int(state['items'].get(k, 0)) < n for k, n in cost.items()):
            raise ValueError('Necesitas un Anillo de Oath')
        for k, n in cost.items():
            state['items'][k] = int(state['items'].get(k, 0)) - n
        partner['is_vowed'] = 1
        partner['wedding_date'] = int(request.get('_now') or __import__('time').time())  # DatesPledgeWindow shows the Oath date
        # the wedding skin (partner_picture.is_wedding) is the Oath's gift: one copy, once per girl
        skin = wedding_skin(partner['table_id'])
        got = state.setdefault('wedding_skins', [])
        if skin and skin not in got:
            state['items'][str(skin)] = int(state['items'].get(str(skin), 0)) + 1
            got.append(skin); result['got'] = {str(skin): 1}
        result['wedding_skin'] = skin
    else:
        raise ValueError('Acción de citas no disponible')
    return result
