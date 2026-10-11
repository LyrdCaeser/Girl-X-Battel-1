"""Wish Capsule (activity 140, WishCapsuleData / SummonWindow wish page / activity/WishCapsule; capture 2026-09-29-fb/47).

A second page of the Capsule window: summons 22-26 (250 / 2200 gems, 1 / 10 Advanced Capsules 36, one free a day) draw from
dropbox 10008. The player picks a Wish Girl (misc wish_gacha_partners, one 5★ per faction and generation) and may switch
her at any time without touching the progress (WISH_GACHA_TIPS_3). The event tab gives rewards for the number of Wish
draws (activity_wish_gacha: limit / awards, type 1 repeats every `limit` draws). Wish draws don't count for daily tasks
and trophies (WISH_GACHA_PS).

Local rule (LOCAL-053): the server's odds are not in the client, only misc wish_gacha_*: out of weight_ini_total
(1,000,000) the Wish Girl starts at weight_ini_get (100) and gains weight_add (100) every weight_add_num (100) draws — the
×2 / ×3 / ×4 / ×5 of the tips window at 100-400 draws —; from weight_special_start (400) each draw adds
weight_special_add (220) more, and draw `guarantee` (500) gives her for sure (Guaranteed New Girl). Getting her, by the
wish roll or from the normal pool, resets the progress."""
from __future__ import annotations
import json, secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/wish.json').read_text())
ODDS = D['odds']
SUMMONS = (22, 23, 24, 25, 26)
FREE = 26


class WishError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def data(state):
    return state.setdefault('wish', {'select': 0, 'times': 0, 'total': 0, 'claimed': {}, 'free_at': 0})


def weight(times):
    """Wish Girl weight (of weight_ini_total) for the `times`-th draw since she was last obtained."""
    w = ODDS['weight_ini_get'] + ODDS['weight_add'] * min(4, (times - 1) // ODDS['weight_add_num'])
    if times > ODDS['weight_special_start']: w += ODDS['weight_special_add'] * (times - ODDS['weight_special_start'])
    return w


def roll(state, table_id, rng=None):
    """One Wish draw: `table_id` came from the normal pool; returns the girl actually obtained."""
    rng = rng or secrets.randbelow
    s = data(state); s['times'] += 1; s['total'] += 1
    if s['select'] and (s['times'] >= ODDS['guarantee'] or rng(ODDS['weight_ini_total']) < weight(s['times'])):
        table_id = s['select']
    if table_id == s['select']: s['times'] = 0
    return table_id


def available(s, row):
    """Times this reward row can be claimed now."""
    got = int(s['claimed'].get(str(row['id']), 0))
    if int(row['type']) == 1: return s['total'] // int(row['limit']) - got
    return int(s['total'] >= int(row['limit']) and not got)


def snapshot(state, now):
    s = json.loads(json.dumps(data(state)))
    return {'select': s['select'], 'times': s['times'], 'total': s['total'], 'rate': weight(s['times'] + 1) / ODDS['weight_ini_total'],
            'free_in': max(0, int(s['free_at']) - now), 'claimed': s['claimed'],
            'can_claim': [int(k) for k, r in D['rows'].items() if available(s, r) > 0]}


def action(state, request):
    s = data(state); act = request.get('action')
    if act == 'select':
        pid = int(request.get('partner') or 0)
        if pid not in D['partners']: raise WishError('Esa chica no está entre las Wish Girls')
        s['select'] = pid
        return {}
    if act == 'claim':
        row = D['rows'].get(str(request.get('id')))
        if not row: raise WishError('Recompensa inexistente')
        n = available(s, row)
        if n <= 0: raise WishError('Aún no llegas a esas tiradas')
        got = {k: v * n for k, v in pairs(row['awards']).items()}
        for k, v in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + v
        s['claimed'][str(row['id'])] = int(s['claimed'].get(str(row['id']), 0)) + n
        return {'got': got}
    raise WishError('Acción de Wish Capsule desconocida')
