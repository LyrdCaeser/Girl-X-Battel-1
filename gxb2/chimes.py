"""Tree of Chimes (Shrine chimeInfo, ChimeMainWindow / ChimeDetailWindow / ChimeDebrisBackpackWindow / ChimePokedexWindow).

Ten account-wide Chimes. A Chime is activated with its shards (chime.unlock, e.g. 20 Shard of Cherries) and then:
- Charge: Chimelight 0 → 100 % (max_lv), each point costs gold + Fantasy Dust (325) from chime_lv_cost[level]['cost' + quality];
- Enchant: buffs 1-3 in order, each once Chimelight reaches limit1-3, paying cost1-3 (gold, Fantasy Talisman 326, shards);
- Ascend: buff 4 when Chimelight reaches limit4[1] and limit4[2..4] Enchantments are done, paying cost4.
Every girl gets HeroAttr:getChimeAttr from the Chimes (base attrs scaled by level, % buffs, faction boosts) and the Ascension
skills join the team's god skills; locally they reach the original battle through Report chimeBonusA passed for each save.
Spare shards (more than what the Chime still needs) can be transferred into Chime Chips (373, chime_decompose.awards each).
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/chimes.json').read_text())
CHIMES = D['chimes']
SHARD_OF = {str(r['chime_id']): str(r['id']) for r in D['decompose'].values()}
CHIP = '373'


class ChimeError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def data(state):
    s = state.setdefault('chimes', {})
    for cid in CHIMES: s.setdefault(cid, {'lev': -1, 'buffs': [0, 0, 0, 0]})
    return s


def row(cid):
    r = CHIMES.get(str(cid))
    if not r: raise ChimeError('Campanilla desconocida')
    return r


def limit4(r):
    return [int(x) for x in str(r.get('limit4') or '').split('|') if x != '']


def enchants(r):
    """Enchantments that exist for this Chime (ChimeDetailWindow SuitAttr: 1 and 2 by limit1, 3 by limit3)."""
    has = lambda k: str(r.get(k) or '').strip() not in ('', '0')
    return [i for i, ok in ((1, has('limit1')), (2, has('limit1') and has('buff2')), (3, has('limit3'))) if ok]


def charge_cost(r, lev):
    return pairs(D['lv_cost'].get(str(lev), {}).get('cost' + str(r['qlt'])))


def can_pay(state, cost):
    return all(int(state['items'].get(k, 0)) >= v for k, v in cost.items())


def pay(state, cost):
    if not can_pay(state, cost): raise ChimeError('Faltan materiales')
    for k, v in cost.items(): state['items'][k] = int(state['items'][k]) - v


def needed_shards(state, cid):
    """Shards this Chime still needs (activation + pending Enchant / Ascend costs); the rest are spare."""
    r = row(cid); c = data(state)[str(cid)]; shard = SHARD_OF.get(str(cid)); need = 0
    if c['lev'] < 0: need += pairs(r['unlock']).get(shard, 0)
    for i in (1, 2, 3, 4):
        if not c['buffs'][i - 1] and (i == 4 or i in enchants(r)): need += pairs(r.get(f'cost{i}')).get(shard, 0)
    return need


def bonus(state):
    """Report chimeBonusA: every activated Chime."""
    return [{'chime_id': int(cid), 'lev': int(c['lev']), 'buffs': [int(b) for b in c['buffs']]}
            for cid, c in sorted((state.get('chimes') or {}).items()) if int(c.get('lev', -1)) >= 0]


def snapshot(state):
    view = json.loads(json.dumps(state)); s = data(view); out = {}
    for cid, c in s.items():
        r = CHIMES[cid]; shard = SHARD_OF.get(cid)
        out[cid] = {'lev': c['lev'], 'buffs': c['buffs'], 'shards': int(view['items'].get(shard, 0)), 'shard': shard,
                    'spare': max(0, int(view['items'].get(shard, 0)) - needed_shards(view, cid)),
                    'charge_cost': charge_cost(r, c['lev']) if 0 <= c['lev'] < int(r['max_lv']) else {}}
    return {'chimes': out}


def action(state, request):
    s = data(state); act = request.get('action'); cid = str(request.get('id') or '')
    if act == 'unlock':
        r = row(cid); c = s[cid]
        if c['lev'] >= 0: raise ChimeError('Ya está activada')
        pay(state, pairs(r['unlock'])); c['lev'] = 0
        return {}
    if act == 'charge':
        r = row(cid); c = s[cid]; times = max(1, min(int(request.get('times') or 1), 100)); done = 0
        if c['lev'] < 0: raise ChimeError(D['text'].get('CHIME_TEXT05', 'Locked'))
        for _ in range(times):
            if c['lev'] >= int(r['max_lv']): break
            cost = charge_cost(r, c['lev'])
            if not can_pay(state, cost): break
            pay(state, cost); c['lev'] += 1; done += 1
        if not done: raise ChimeError(D['text'].get('CHIME_TEXT08', 'Max. Chimelight reached') if c['lev'] >= int(r['max_lv']) else 'Faltan materiales')
        return {'charged': done}
    if act == 'enchant':
        r = row(cid); c = s[cid]
        if c['lev'] < 0: raise ChimeError(D['text'].get('CHIME_TEXT05', 'Locked'))
        todo = [i for i in enchants(r) if not c['buffs'][i - 1]]
        if not todo: raise ChimeError(D['text'].get('CHIME_TEXT09', 'Enchanted'))
        i = todo[0]; lim = int(r.get(f'limit{i}') or 0)
        if c['lev'] < lim: raise ChimeError(D['text'].get('CHIME_TEXT11', "Hasn't reached {1} Chimelight yet!").replace('{1}', f'{lim}%'))
        pay(state, pairs(r.get(f'cost{i}'))); c['buffs'][i - 1] = 1
        return {'enchant': i}
    if act == 'ascend':
        r = row(cid); c = s[cid]; lim = limit4(r)
        if c['lev'] < 0: raise ChimeError(D['text'].get('CHIME_TEXT05', 'Locked'))
        if c['buffs'][3]: raise ChimeError(D['text'].get('CHIME_TEXT10', 'Ascended'))
        if lim and sum(c['buffs'][:3]) < sum(lim[1:]): raise ChimeError(D['text'].get('CHIME_TEXT07', "Some Enchantments haven't been unlocked!"))
        if lim and c['lev'] < lim[0]: raise ChimeError(D['text'].get('CHIME_TEXT11', "Hasn't reached {1} Chimelight yet!").replace('{1}', f'{lim[0]}%'))
        pay(state, pairs(r.get('cost4'))); c['buffs'][3] = 1
        return {}
    if act == 'transfer':
        shard = str(request.get('shard') or ''); n = int(request.get('count') or 0)
        dec = D['decompose'].get(shard)
        if not dec: raise ChimeError('Fragmento desconocido')
        spare = max(0, int(state['items'].get(shard, 0)) - needed_shards(state, dec['chime_id']))
        if n <= 0 or n > spare: raise ChimeError(D['text'].get('CHIME_TEXT18', 'Only Spare Shards can be used for the transfer'))
        state['items'][shard] = int(state['items'][shard]) - n
        got = {k: v * n for k, v in pairs(dec['awards']).items()}
        for k, v in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + v
        return {'got': got}
    raise ChimeError('Acción de Tree of Chimes desconocida')
