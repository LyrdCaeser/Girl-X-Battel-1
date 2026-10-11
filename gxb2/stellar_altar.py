"""Stellar Altar (StarryAltarWindow / StarrySelectAwardWindow, table starry_altar): the House Cosmos summon.

Rows 4 / 5 are the permanent modes (rows 1 / 3 / 6 / 7 carry activity_lock: event versions). Each draw costs one Star Token (358) and gives one basic reward of dropbox 80001. With probability `wight`[1] (10 %) it
also gives the additional reward (5 Customized 10-star Cosmos Girls Shards, 940059). Surprise Mode (row 4) adds a
0.25 % chance (`wight`[2]) of the grand reward: the chosen Cosmos girl (optional_award). Accumulate Mode (row 5) gives
10 extra shards every 40 draws (type2_award). 100 shards summon the chosen 10★ Cosmos girl. The record keeps the last 50
draws (STARRY_ALTAR_HELP_2). Opens after campaign stage 15-10 (item 358 description)."""
from __future__ import annotations
import json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROWS = json.loads((ROOT / 'data/stellar_altar.json').read_text())
DROP = json.loads((ROOT / 'data/dropbox.json').read_text())
TOKEN, SHARD, SHARDS_FOR_GIRL = '358', '940059', 100
OPEN_STAGE = 152  # campaign 15-10
SURPRISE, ACCUMULATE = 4, 5
GIRLS = [int(x) for x in str(ROWS[str(SURPRISE)]['optional_award']).split('|')]
EVERY, EVERY_AWARD = (lambda a: (int(a[0]), a[1]))(str(ROWS[str(ACCUMULATE)]['type2_award']).split('|'))


class AltarError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def data(state):
    if 'stellar_altar' not in state:
        # carry over the earlier generic Cosmos Portal (home_systems 'cosmos': same rows 4 / 5)
        old = state.get('home_systems', {}).get('cosmos') or {}
        state['stellar_altar'] = {'mode': old.get('mode', SURPRISE) if old.get('mode') in (SURPRISE, ACCUMULATE) else SURPRISE,
                                  'target': old.get('choice', GIRLS[0]) if old.get('choice') in GIRLS else GIRLS[0],
                                  'draws': 0, 'accumulate': int(old.get('count', 0)), 'record': []}
    return state['stellar_altar']


def basic(rng):
    rows = [r for r in DROP.values() if int(r['dropbox_id']) == int(ROWS[str(SURPRISE)]['dropbox_id']) and int(r['weight']) > 0]
    roll = rng.random() * sum(int(r['weight']) for r in rows)
    for r in rows:
        roll -= int(r['weight'])
        if roll < 0: return pairs(r['item'])
    return pairs(rows[-1]['item'])


def snapshot(state, developer=False):
    s = data(state)
    return {'open': developer or int(state.get('max_stage', 0)) >= OPEN_STAGE, 'mode': s['mode'], 'target': s['target'], 'girls': GIRLS,
            'tokens': int(state['items'].get(TOKEN, 0)), 'shards': int(state['items'].get(SHARD, 0)), 'record': s['record'][-50:],
            'to_bonus': EVERY - s['accumulate'] % EVERY, 'draws': s['draws']}


def action(state, request, add_girl, developer=False, rng=None):
    rng = rng or random.SystemRandom()
    s = data(state); act = request.get('action')
    if not snapshot(state, developer)['open']: raise AltarError('Stellar Altar se abre al superar la fase 15-10 de la campaña')
    if act == 'mode':
        mode = int(request.get('mode') or 1)
        if mode not in (SURPRISE, ACCUMULATE): raise AltarError('Modo inválido')
        s['mode'] = mode
        if request.get('target'):
            if int(request['target']) not in GIRLS: raise AltarError('Chica inválida')
            s['target'] = int(request['target'])
        return {}
    if act == 'draw':
        times = 10 if int(request.get('times') or 1) >= 10 else 1
        if int(state['items'].get(TOKEN, 0)) < times: raise AltarError('Faltan Star Tokens')
        state['items'][TOKEN] = int(state['items'][TOKEN]) - times
        row = ROWS[str(s['mode'])]; chances = [float(x) for x in str(row['wight']).split('|')]
        got, girls = {}, []
        for _ in range(times):
            one = basic(rng); entry = {'basic': one}
            if rng.random() < chances[0]:
                for k, v in pairs(row['extra_award']).items(): one[k] = one.get(k, 0) + v
                entry['extra'] = True
            if s['mode'] == SURPRISE and len(chances) > 1 and rng.random() < chances[1]:
                girls.append(add_girl(s['target'])); entry['grand'] = s['target']
            if s['mode'] == ACCUMULATE:
                s['accumulate'] += 1
                if s['accumulate'] % EVERY == 0:
                    for k, v in pairs(EVERY_AWARD).items(): one[k] = one.get(k, 0) + v
                    entry['bonus'] = True
            for k, v in one.items():
                got[k] = got.get(k, 0) + v; state['items'][k] = int(state['items'].get(k, 0)) + v
            s['draws'] += 1; s['record'] = (s['record'] + [entry])[-50:]
        return {'got': got, 'girls': girls}
    if act == 'compose':
        tid = int(request.get('target') or s['target'])
        if tid not in GIRLS: raise AltarError('Chica inválida')
        if int(state['items'].get(SHARD, 0)) < SHARDS_FOR_GIRL: raise AltarError(f'Necesitas {SHARDS_FOR_GIRL} fragmentos')
        state['items'][SHARD] = int(state['items'][SHARD]) - SHARDS_FOR_GIRL
        return {'girls': [add_girl(tid)]}
    raise AltarError('Acción del Stellar Altar desconocida')
