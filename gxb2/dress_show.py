"""Outfit Showcase (models/DressShow.lua, DressShowWindow; capture 2026-09-29-fb/40).

Four booths (show_window), each with three rows of five slots: row type 1 / 2 / 3 is the Courage / Charisma / Knowledge
booth (SHOW_WINDOW_TEXT10-12). A slot opens after the previous one and its condition (show_window_slot unlock_type:
1-3 Outfit Courage / Charisma / Knowledge, 4 Tests floor, 5 Patrol stage, 6 Friend Team Boss, 7 House Exam record) and only
takes an Outfit piece meeting add_type/add_num (DressShow:checkDressAddType: 1 pos, 2 quality, 3 star, 4-6 base1-3).
A booth's score is the sum of its slots; its rating comes from misc show_window_point_rank and its daily reward from
show_window_award (Rare Tag 314 / Metal Tag 315, "Rewards sent at 0:00"). Tags buy in the Showcase Store (shop2 / shop3,
point requirement = total score, weekly limits).

Local rules (LOCAL-052): a slot scores the placed piece's attribute of its row (Courage / Charisma / Knowledge), which is
what the booth names say; the daily reward is claimed in the booth screen (up to 7 days accumulate); the Friend Team Boss
condition (co-op, not offline) uses campaign stages ×10.
Buff shop (shop1, DressShow.buyBuff): each purchase adds a stack of `num` (3) battles of `skill` to its modes (func_id: 15 Tests /
39 Old Campus, 19 Patrol, 32 Security Squad, 35 House Exams), at most `max_time` stacks active and `buy_time` buys a week.
LOCAL (LOCAL-076): the server applied the stacks; here every active stack adds its skill to the battle as a god skill and
spends one battle. Security Squad (co-op) is not playable offline, so its buffs are listed but not sold."""
from __future__ import annotations
import json, time
from pathlib import Path
from . import dress, clock

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/dress_show.json').read_text())
SLOTS, WINDOWS, AWARDS = D['slots'], D['windows'], D['awards']
DAY = 86400


class ShowError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def data(state, now):
    s = state.setdefault('dress_show', {})
    s.setdefault('slots', {}); s.setdefault('shop', {}); s.setdefault('buffs', {}); s.setdefault('shop_week', 0); s.setdefault('history', 0)
    s.setdefault('award_day', clock.day(now, local=True))
    for sid, row in SLOTS.items():  # a Slot without condition is open from the start
        if not row['unlock_type'] and not row['last_id']: s['slots'].setdefault(sid, 0)
    week = now // D['refresh']
    if s['shop_week'] != week:
        s['shop_week'] = week; s['shop'] = {}
        for b in s['buffs'].values(): b['bought'] = 0
    return s


def value_now(state, kind):
    a = dress.attrs(state)
    if kind in (1, 2, 3): return int(a[kind - 1])
    if kind == 4: return int((state.get('tower') or {}).get('max_stage', 0))
    if kind == 5: return int((state.get('patrol') or {}).get('max_stage', 0))
    if kind == 6: return int(state.get('max_stage', 0)) // 10
    if kind == 7: return int((state.get('house_exam') or {}).get('history_score', 0))
    return 0


def piece_item(state, did):
    star = int(dress.saved(state)['owned'].get(str(did), 0))
    return dress.ITEMS.get(dress.item_of(int(did), star)) if star else None


def fits(state, sid, did):
    row = SLOTS[str(sid)]; it = piece_item(state, did)
    if not it: return False
    types = [int(x) for x in str(row['add_type']).split('|') if x]; nums = [int(x) for x in str(row['add_num']).split('|') if x]
    for t, n in zip(types, nums):
        v = {1: int(dress.PIECES[int(did)]['pos']), 2: int(it.get('qlt') or 0), 3: int(it.get('star') or 0),
             4: int(float(it.get('base1') or 0)), 5: int(float(it.get('base2') or 0)), 6: int(float(it.get('base3') or 0))}[t]
        if (t == 1 and v != n) or (t != 1 and v < n): return False
    return True


def slot_score(state, sid, did):
    it = piece_item(state, did)
    return int(float(it.get(f"base{SLOTS[str(sid)]['type']}") or 0)) if it else 0


def booth_score(state, s, wid):
    return sum(slot_score(state, sid, did) for sid, did in s['slots'].items() if did and str(sid)[0] == str(wid))


def rating(score):
    lv = 1
    for i, p in enumerate(D['rank']):
        if score >= p: lv = i + 1
    return lv


def daily_award(wid, score):
    tiers = sorted((a for a in AWARDS.values() if int(a['group']) == int(WINDOWS[str(wid)]['award_group'])), key=lambda a: int(a['point']))
    got = {}
    for a in tiers:
        if score >= int(a['point']): got = pairs(a['awards'])
    return got


def snapshot(state, now=None):
    now = int(time.time()) if now is None else now
    view = json.loads(json.dumps(state)); s = data(view, now)
    booths = []
    for wid, w in sorted(WINDOWS.items(), key=lambda x: int(x[0])):
        slots = []
        for sid in str(w['slot']).split('|'):
            row = SLOTS[sid]; did = s['slots'].get(sid)
            prev_ok = not row['last_id'] or str(row['last_id']) in s['slots']
            slots.append({'id': int(sid), 'type': int(row['type']), 'unlocked': sid in s['slots'], 'piece': did or 0, 'score': slot_score(view, sid, did) if did else 0,
                          'unlock_type': int(row['unlock_type'] or 0), 'unlock_num': int(row['unlock_num'] or 0), 'now': value_now(view, int(row['unlock_type'] or 0)),
                          'can_unlock': prev_ok and value_now(view, int(row['unlock_type'] or 0)) >= int(row['unlock_num'] or 0), 'add_type': str(row['add_type']), 'add_num': str(row['add_num'])})
        score = booth_score(view, s, wid)
        booths.append({'id': int(wid), 'slots': slots, 'score': score, 'rating': rating(score), 'daily': daily_award(wid, score)})
    return {'booths': booths, 'total': sum(b['score'] for b in booths), 'history': max(s['history'], sum(b['score'] for b in booths)),
            'pending_days': pending_days(s, now), 'shop': s['shop'], 'buffs': s['buffs']}


def pending_days(s, now):
    today = clock.day(now, local=True)
    if s['award_day'] >= today: return 0
    import datetime
    a = datetime.date.fromisoformat(s['award_day']); b = datetime.date.fromisoformat(today)
    return max(0, min(7, (b - a).days))


def action(state, request, now=None):
    now = int(time.time()) if now is None else now
    s = data(state, now); act = request.get('action')
    if act == 'unlock':
        sid = str(request.get('slot')); row = SLOTS.get(sid)
        if not row: raise ShowError('Hueco inexistente')
        if sid in s['slots']: raise ShowError('Ya desbloqueado')
        if row['last_id'] and str(row['last_id']) not in s['slots']: raise ShowError('You need to unlock the previous Slot in this Booth first')
        if value_now(state, int(row['unlock_type'] or 0)) < int(row['unlock_num'] or 0): raise ShowError('Aún no cumples la condición')
        s['slots'][sid] = 0
        return {}
    if act == 'place':
        sid = str(request.get('slot')); did = int(request.get('piece') or 0)
        if sid not in s['slots']: raise ShowError('Hueco bloqueado')
        if did:
            if not fits(state, sid, did): raise ShowError('Esta pieza no cumple el requisito del hueco')
            for other, d in s['slots'].items():
                if d == did and other[0] == sid[0]: s['slots'][other] = 0  # a piece is shown once per booth
        s['slots'][sid] = did
        s['history'] = max(s['history'], sum(booth_score(state, s, w) for w in WINDOWS))
        return {}
    if act == 'claim':
        days = pending_days(s, now)
        if not days: raise ShowError('Rewards sent at 0:00 — vuelve mañana')
        got = {}
        for wid in WINDOWS:
            for k, v in daily_award(wid, booth_score(state, s, wid)).items(): got[k] = got.get(k, 0) + v * days
        for k, v in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + v
        s['award_day'] = clock.day(now, local=True)
        return {'got': got, 'days': days}
    if act == 'buy':
        shop, rid = str(request.get('shop')), str(request.get('id'))
        row = D.get('shop' + shop, {}).get(rid)
        if shop not in ('2', '3') or not row: raise ShowError('Artículo inexistente')
        key = shop + ':' + rid; bought = int(s['shop'].get(key, 0))
        if int(row['point'] or 0) > s['history']: raise ShowError('Necesitas más puntuación total')
        if bought >= int(row['buy_time']): raise ShowError('Límite semanal alcanzado')
        cost = pairs(row['cost'])
        if any(int(state['items'].get(k, 0)) < v for k, v in cost.items()): raise ShowError('Faltan Tags')
        for k, v in cost.items(): state['items'][k] = int(state['items'][k]) - v
        got = pairs(row['item'])
        for k, v in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + v
        s['shop'][key] = bought + 1
        return {'got': got}
    if act == 'buy_buff':
        rid = str(request.get('id')); row = SHOP1.get(rid); n = max(1, int(request.get('num', 1)))
        if not row: raise ShowError('Buff inexistente')
        if '32' in funcs(row): raise ShowError('Security Squad se juega con amigos en línea')
        b = s['buffs'].setdefault(rid, {'times': [], 'bought': 0})
        if b['bought'] + n > int(row['buy_time']): raise ShowError('Purchase limit reached')
        if len(b['times']) + n > int(row['max_time']): raise ShowError('Ya tienes el máximo de stacks activos')
        cost = {k: v * n for k, v in pairs(row['cost']).items()}
        if any(int(state['items'].get(k, 0)) < v for k, v in cost.items()): raise ShowError('Faltan Tags')
        for k, v in cost.items(): state['items'][k] = int(state['items'][k]) - v
        b['times'] += [int(row['num'])] * n; b['bought'] += n
        return {}
    raise ShowError('Acción de Outfit Showcase desconocida')


SHOP1 = D.get('shop1', {})
def funcs(row): return str(row['func_id']).split('|')


def battle_skills(state, func):
    """God skills of the active buff stacks for a battle of function `func`; each stack spends one battle."""
    s = (state.get('dress_show') or {}).get('buffs') or {}
    out = []
    for rid, b in s.items():
        row = SHOP1.get(rid)
        if not row or str(func) not in funcs(row) or not b.get('times'): continue
        out += [int(row['skill'])] * len(b['times'])
        b['times'] = [t - 1 for t in b['times'] if t > 1]
    return out
