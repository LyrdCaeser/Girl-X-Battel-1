"""Fantasy Book (battle pass: BattlePassWindow.lua and its four pages). Data: data/fantasy_book.json (tools/extract_fantasy_book.py).

Progress: Pages (item 117 in the task awards) raise the Book level (battlepass_award.cost_total); each level's Basic Book
reward is claimed once. Book levels can be bought with Gems (cost_diamonds, cost_dct_diamonds in the last 2 weeks).
Task: Daily (reset at local midnight), Weekly (reset on Monday) and Extra (once per season, shown from their Book level)
tasks; each gives its award plus Pages. Exchange: Floral Stamp (221) and Crystal Leaf (222) stores and Flora Bookmark draws
(bp_lottery_cost from dropbox bp_lottery_dropbox). Trophies are the general achievements (gxb2/missions.py).

LOCAL (LOCAL-077): the server ran the season and counted the tasks. Here a season lasts 42 days from the first visit and then
starts over (Pages, claims, store limits and Extra tasks reset; currencies stay). Task progress comes from the counters
of gxb2/missions.record: today's counts for Daily tasks and the growth since the week / season started for the others.
Luxury / Collector's Book were real-money purchases and are not sold (their column is shown locked), like the Passport
paid row. Hearts count through gxb2/hearts.py and Friend Boss through gxb2/friend_boss.py; Seals and Antique upgrades have no counter yet.
"""
from __future__ import annotations
import json, secrets, time
from pathlib import Path
from . import clock

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/fantasy_book.json').read_text())
LEVELS = D['levels']
MISSIONS = {m['id']: m for m in D['missions']}
SHOP = {r['id']: r for r in D['shop']}
SEASON = 42 * 86400
PAGES = '117'
DROP = {}
for _r in json.loads((ROOT / 'data/dropbox.json').read_text()).values():
    if int(_r['dropbox_id']) == int(D['lottery_dropbox']): DROP[int(_r['id'])] = _r

# task id → (missions counter, how it is measured). 'day' = today's count, 'week' / 'season' = growth since the period began.
COUNTERS = {1: ('midas', 'day'), 2: ('gamble', 'day'), 3: ('tavern', 'day'), 5: ('regular', 'day'), 6: ('advanced', 'day'),
            7: ('arena', 'day'), 8: ('idle', 'day'), 9: ('quiz', 'day'), 10: ('hearts', 'day'), 26: ('dorm_collect', 'day'),
            12: ('arena_win', 'week'), 13: ('graduate', 'week'), 14: ('sanctuary', 'week'), 16: ('tavern5', 'week'),
            25: ('forge', 'week'), 22: ('tavern7', 'season'), 23: ('arena_win', 'season')}
UNTRACKED = {21, 24}   # Antique upgrades, Seals (no counter yet)


# Two themed seasons alternate (BattlePassSteam = "Restart the Engine!", BattlePassSteamNew = "Fantasy Book"): odd seasons
# are the Book (Pages 223, Floral Stamp 221, Crystal Leaf 222), even ones the Engine (Gearwheel 117, Screws 119, Mecha Core 120).
ENGINE = {'221': '119', '222': '120'}


def theme_of(season):
    return 'book' if int(season) % 2 else 'engine'


def tr(got, season):
    """Table rows name the Book currencies; in an Engine season they are the Engine ones."""
    return {ENGINE.get(k, k): v for k, v in got.items()} if theme_of(season) == 'engine' else got


class BookError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def week_of(now):
    import datetime
    d = datetime.date.fromisoformat(clock.day(now))
    return (d - datetime.timedelta(days=d.weekday())).isoformat()


def totals(state):
    return dict(((state.get('missions') or {}).get('totals') or {}))


def boss_wins(state):
    return sum(int(v) for v in ((state.get('friend_boss') or {}).get('wins') or {}).values())


def comfort(state):
    try:
        from . import house_dress
        return house_dress.comfort(state) if 'house_dress' in state else 0
    except Exception:
        return 0


def data(state, now):
    b = state.get('fantasy_book')
    if not b or now >= b['start'] + SEASON:
        season = (b['season'] % len(D['seasons']) + 1) if b else 1
        b = state['fantasy_book'] = {'season': season, 'start': now if not b else b['start'] + SEASON * ((now - b['start']) // SEASON),
                                     'pages': 0, 'free': [], 'claimed': {}, 'shop': {}, 'week': '', 'wbase': {}, 'sbase': totals(state),
                                     'scomfort': comfort(state), 'days_all': []}
    if b['week'] != week_of(now):
        b['week'] = week_of(now); b['wbase'] = totals(state); b['wcomfort'] = comfort(state); b['wboss'] = boss_wins(state)
        b['claimed'] = {k: v for k, v in b['claimed'].items() if not k.startswith('w:')}
    today = clock.day(now)
    b['claimed'] = {k: v for k, v in b['claimed'].items() if not k.startswith('d:') or k.startswith('d:' + today)}
    return b


def level_of(pages):
    lv = 1
    for row in LEVELS:
        if pages >= row['need']: lv = row['lv']
    return lv


def daily_done(state, now):
    m = state.get('missions') or {}
    return len([c for c in m.get('claimed', []) if c != 11]) if m.get('day') == clock.day(now) else 0


def progress(state, b, mid, now, roster=()):
    m = MISSIONS[mid]
    if mid in UNTRACKED: return 0
    if mid == 11: return daily_done(state, now)
    if mid == 15: return max(0, boss_wins(state) - int(b.get('wboss', 0)))   # Friend Boss wins this week (gxb2/friend_boss.py)
    if mid == 17: return max(0, comfort(state) - int(b.get('wcomfort', 0)))
    if mid == 18: return len([d for d in b.get('days_all', []) if d >= b['week']])
    if mid == 19: return 1 if any(int(p.get('stars', 0)) >= 10 for p in roster) else 0
    if mid == 20:
        try:
            from . import skins
            return len(skins.collected(state))
        except Exception:
            return len((state.get('skins') or {}).get('collected') or [])
    key, how = COUNTERS.get(mid, ('', ''))
    if how == 'day':
        ms = state.get('missions') or {}
        return int((ms.get('counts') or {}).get(key, 0)) if ms.get('day') == clock.day(now) else 0
    base = b['wbase'] if how == 'week' else b['sbase']
    return max(0, int(totals(state).get(key, 0)) - int(base.get(key, 0)))


def claim_key(m, now, b):
    return {1: 'd:' + clock.day(now) + ':', 2: 'w:', 3: 's:'}[m['type']] + str(m['id'])


def snapshot(state, level, roster=(), now=None):
    now = int(time.time()) if now is None else now
    view = json.loads(json.dumps(state))
    b = data(view, now)
    if daily_done(view, now) >= 10 and clock.day(now) not in b['days_all']: b['days_all'].append(clock.day(now))
    lv = level_of(b['pages']); nxt = next((r for r in LEVELS if r['lv'] == lv + 1), None)
    tasks = []
    for m in D['missions']:
        if m['lv'] > level or m['bp'] > lv: continue
        have = progress(view, b, m['id'], now, roster)
        tasks.append({**m, 'have': min(have, m['need']), 'claimed': claim_key(m, now, b) in b['claimed'], 'tracked': m['id'] not in UNTRACKED})
    days_left = max(0, (b['start'] + SEASON - now))
    th = theme_of(b['season'])
    return {'season': b['season'], 'theme': th, 'cur': ['119', '120'] if th == 'engine' else ['221', '222'], 'page': '117' if th == 'engine' else '223', 'end': b['start'] + SEASON, 'left': days_left, 'pages': b['pages'], 'level': lv, 'max': LEVELS[-1]['lv'],
            'into': b['pages'] - next(r['need'] for r in LEVELS if r['lv'] == lv), 'span': (nxt['need'] - next(r['need'] for r in LEVELS if r['lv'] == lv)) if nxt else 0,
            'free': b['free'], 'tasks': tasks, 'shop': b['shop'], 'discount': days_left <= 14 * 86400,
            'refresh_day': (now // 86400 + 1) * 86400}


def grant(state, got):
    for k, v in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + v


def action(state, request, level, roster=(), now=None, rng=secrets.randbelow):
    now = int(time.time()) if now is None else now
    b = data(state, now); act = request.get('action')
    if daily_done(state, now) >= 10 and clock.day(now) not in b['days_all']: b['days_all'].append(clock.day(now))
    lv = level_of(b['pages'])
    if act == 'open':
        return {}
    if act in ('claim', 'claim_all'):
        todo = [int(request.get('lv', 0))] if act == 'claim' else [r['lv'] for r in LEVELS if r['lv'] <= lv and r['lv'] not in b['free']]
        got = {}
        for n in todo:
            row = next((r for r in LEVELS if r['lv'] == n), None)
            if not row or n > lv: raise BookError('Nivel del Book no alcanzado')
            if n in b['free']: raise BookError('Ya reclamado')
            for k, v in tr(pairs(row['free']), b['season']).items(): got[k] = got.get(k, 0) + v
            b['free'].append(n)
        if not got: raise BookError('No hay recompensas para reclamar')
        grant(state, got); return {'got': got}
    if act == 'buy_level':
        n = max(1, int(request.get('num', 1)))
        if lv + n > LEVELS[-1]['lv']: raise BookError(D['text'].get('BP_LEV_MAX', 'Nivel máximo'))
        discount = b['start'] + SEASON - now <= 14 * 86400
        cost = {}
        for i in range(n):
            row = next(r for r in LEVELS if r['lv'] == lv + i)
            for k, v in pairs(row['gems_dct' if discount else 'gems']).items(): cost[k] = cost.get(k, 0) + v
        if any(int(state['items'].get(k, 0)) < v for k, v in cost.items()): raise BookError('Faltan gemas')
        for k, v in cost.items(): state['items'][k] = int(state['items'][k]) - v
        # "After upgrading your Book level with Gems your Current Pages will remain": the level's threshold is added
        into = b['pages'] - next(r['need'] for r in LEVELS if r['lv'] == lv)
        b['pages'] = next(r['need'] for r in LEVELS if r['lv'] == lv + n) + into
        return {'cost': cost}
    if act == 'task':
        mid = int(request.get('id', 0)); m = MISSIONS.get(mid)
        if not m or m['lv'] > level or m['bp'] > lv: raise BookError('Tarea no disponible')
        key = claim_key(m, now, b)
        if key in b['claimed']: raise BookError('Ya reclamada')
        if progress(state, b, mid, now, roster) < m['need']: raise BookError('Tarea sin completar')
        got = tr(pairs(m['award']), b['season']); pages = pairs(m['pages']).get(PAGES, 0)
        grant(state, got); b['pages'] += pages; b['claimed'][key] = 1
        return {'got': got, 'pages': pages, 'level': level_of(b['pages'])}
    if act == 'buy':
        rid = int(request.get('id', 0)); row = SHOP.get(rid); n = max(1, int(request.get('num', 1)))
        if not row: raise BookError('Artículo inexistente')
        bought = int(b['shop'].get(str(rid), 0))
        if bought + n > row['limit']: raise BookError('Límite de compra alcanzado')
        cost = {k: v * n for k, v in tr(pairs(row['cost']), b['season']).items()}
        if any(int(state['items'].get(k, 0)) < v for k, v in cost.items()): raise BookError('No tienes suficiente moneda de la temporada')
        for k, v in cost.items(): state['items'][k] = int(state['items'][k]) - v
        got = {k: v * n for k, v in tr(pairs(row['item']), b['season']).items()}
        grant(state, got); b['shop'][str(rid)] = bought + n
        return {'got': got}
    if act == 'draw':
        n = max(1, min(10, int(request.get('num', 1))))
        cost = {k: v * n for k, v in tr(pairs(D['lottery_cost']), b['season']).items()}
        if any(int(state['items'].get(k, 0)) < v for k, v in cost.items()): raise BookError('No tienes suficiente moneda de la temporada')
        for k, v in cost.items(): state['items'][k] = int(state['items'][k]) - v
        rows = [r for r in DROP.values() if int(r['weight']) > 0]; total = sum(int(r['weight']) for r in rows)
        got = {}
        for _ in range(n):
            x = rng(total)
            for r in rows:
                x -= int(r['weight'])
                if x < 0:
                    for k, v in tr(pairs(r['item']), b['season']).items(): got[k] = got.get(k, 0) + v
                    break
        grant(state, got); return {'got': got}
    raise BookError('Acción del Fantasy Book desconocida')


def odds():
    rows = [r for r in DROP.values() if int(r['weight']) > 0]; total = sum(int(r['weight']) for r in rows) or 1
    return [[r['item'], round(int(r['weight']) * 100 / total, 2)] for r in rows]
