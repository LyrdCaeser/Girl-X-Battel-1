"""Guild v1 (LOCAL-060): a personal guild with simulated (NPC) members. Office, Cafeteria, Gym (Guild Boss).

Original (client tables, models/Guild.lua, GuildTerritoryWindow / GuildDiningHall / GuildGymWindow):
* Unlock: function 22 = campaign stage 32. Create cost misc create_guild_cost (500 gems), name 3-12 characters, rename 1000 gems.
* Guild level from guild_exp (all_exp per level; `member` capacity, `assistant` deputies). Office sign-in once a day:
  misc guild_sign_in_coin (50 Guild Coins, item 4) + guild_sign_in_exp (30 guild EXP).
* Cafeteria opens at guild level guild_order_open (8). guild_mill: donating gold (misc guild_mill_donate) raises the Mill level,
  which sets the reward `factor` (x/10000) and how many orders (`order_num`) are open. guild_order: each order lasts `time`
  seconds after Start, pays `awards` x factor; an order can be upgraded with gems (`up_cost`) to `next_id`.
* Gym: guild_boss chain 1-60 (`next_id`); a win opens the next boss. Fights cost misc guild_boss_fight_cost by fight number
  (0,0,40 gems,80 gems) and a fight cooldown guild_boss_fight_cd (16 h since the last fight resets the count). Every fight pays
  `battle_awards`; a win adds `kill_awards` and `guild_exp` (at most guild_boss_exp_num_max exp-giving wins a day).

Local (not in the client; the server ran guilds): the guild is yours alone plus NPC members (`members`) who join one a day up
to the level's capacity, get generated names/levels/power from the guild seed and sign in (30 guild EXP) on ~70 % of the days.
Applications, recruiting, chat, kicking, the final boss (id 61+), Guild War and the Merchant's paid gift bags aren't rebuilt.
"""
from __future__ import annotations
import hashlib, json, secrets
from datetime import date
from pathlib import Path
from . import clock

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'data/guild.json').read_text())
EXP = {int(k): v for k, v in D['exp'].items()}
BOSS = {int(k): v for k, v in D['boss'].items()}
ORDER = {int(k): v for k, v in D['order'].items()}
MILL = {int(k): v for k, v in D['mill'].items()}
M = D['misc']
UNLOCK_STAGE = 32
MAX_CATCHUP_DAYS = 30
SYL = ['Lu', 'Mi', 'Ka', 'Sa', 'Ri', 'Yu', 'No', 'Ha', 'Ne', 'To', 'El', 'Ai', 'Ko', 'Fu', 'Ma', 'Chi', 'Ve', 'Ro', 'Ni', 'Ze']


class GuildError(ValueError):
    pass


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, v = part.split('#')[:2]; out[k] = out.get(k, 0) + int(v)
    return out


def add(state, got):
    for k, n in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + n


def take(state, cost):
    for k, n in cost.items():
        if int(state['items'].get(k, 0)) < n: raise GuildError('Không đủ tài nguyên')
    for k, n in cost.items(): state['items'][k] = int(state['items'].get(k, 0)) - n


def level_of(exp):
    return max(k for k, r in EXP.items() if int(r['all_exp']) <= exp)


def h(*parts):
    return int(hashlib.sha256('|'.join(str(p) for p in parts).encode()).hexdigest()[:12], 16)


def unlocked(state):
    return int(state.get('max_stage', 0)) >= UNLOCK_STAGE


def mill_level(g):
    return max(k for k, r in MILL.items() if int(r['all_gold']) <= int(g['mill']['gold']))


def order_slots(g):
    return int(MILL[mill_level(g)]['order_num'])


def capacity(g):
    return int(EXP[level_of(g['exp'])]['member'])


def members(g, now, player_level=1):
    """NPC members joined so far (one a day up to the level's capacity), deterministic from the guild seed."""
    days = max(0, (now - int(g['created'])) // 86400)
    count = min(capacity(g) - 1, 4 + days)
    deputies = int(EXP[level_of(g['exp'])]['assistant'])
    out = []
    for i in range(count):
        r = h(g['seed'], i)
        name = ''.join(SYL[(r >> (5 * k)) % len(SYL)] for k in range(2 + r % 2))
        lv = max(1, int(player_level * (0.6 + (r >> 20) % 41 / 100)))
        out.append({'id': 1000 + i, 'name': name, 'level': lv, 'power': lv * (900 + (r >> 8) % 400), 'role': 'deputy' if i < deputies else 'member',
                    'joined': int(g['created']) + i * 86400, 'online': (r >> 12) % 5 == 0})
    return out


def new_orders(g, rng, keep=()):
    slots = order_slots(g); rows = list(keep); total = sum(int(r['weight']) for r in ORDER.values())
    while len(rows) < slots:
        pick = rng(total)
        for oid, r in ORDER.items():
            pick -= int(r['weight'])
            if pick < 0: rows.append({'id': oid, 'start': 0}); break
    return rows


def data(state, now, rng=secrets.randbelow):
    g = state.get('guild')
    if not g: return None
    today = clock.day(now); last = g.get('tick_day', today)
    if last < today:
        # every NPC member signs in on ~70 % of the elapsed local days, like a real guild (catch-up capped)
        elapsed = min(MAX_CATCHUP_DAYS, (date.fromisoformat(today) - date.fromisoformat(last)).days)
        day0 = date.fromisoformat(today).toordinal() - elapsed
        for d in range(elapsed):
            at = now - (elapsed - 1 - d) * 86400
            g['exp'] += sum(int(M['guild_sign_in_exp']) for m in members(g, at) if h(g['seed'], m['id'], day0 + d) % 10 < 7)
        g['tick_day'] = today
    if level_of(g['exp']) >= int(M['guild_order_open']) and not g['orders']['list']:
        g['orders']['list'] = new_orders(g, rng)
    return g


def fresh(name, flag, notice, now, rng):
    g = {'name': name, 'flag': flag, 'notice': notice, 'created': now, 'seed': rng(1 << 40), 'exp': 0, 'checkin_day': '',
         'tick_day': clock.day(now), 'boss': {'current': 1, 'cleared': [], 'fights': 0, 'fight_time': 0, 'exp_day': '', 'exp_n': 0},
         'mill': {'gold': 0}, 'orders': {'list': [], 'refresh_at': 0}, 'log': []}
    return g


def boss_cost(g, now):
    b = g['boss']
    costs = [c.split('#') for c in str(M['guild_boss_fight_cost']).split('|')]
    fights = 0 if now - int(b['fight_time']) >= int(M['guild_boss_fight_cd']) else int(b['fights'])
    if fights >= len(costs): return None, fights
    return ({costs[fights][0]: int(costs[fights][1])} if int(costs[fights][1]) else {}), fights


def log(g, now, text):
    g['log'] = ([{'at': now, 'text': text}] + g['log'])[:30]


def snapshot(state, now, player_level=1):
    g = state.get('guild')
    base = {'unlocked': unlocked(state), 'unlock_stage': UNLOCK_STAGE, 'has': bool(g), 'create_cost': M['create_guild_cost'],
            'name_len': M['guild_name_num_max'], 'flags': D['flags']}
    if not g: return base
    import copy
    view = copy.deepcopy(g); vs = {'guild': view, 'items': dict(state['items'])}
    data(vs, now); view = vs['guild']
    lv = level_of(view['exp']); nxt = EXP.get(lv + 1); b = view['boss']
    cost, fights = boss_cost(view, now)
    return {**base, 'name': view['name'], 'flag': view['flag'], 'notice': view['notice'], 'level': lv, 'exp': view['exp'], 'base_exp': int(EXP[lv]['all_exp']),
            'next_exp': int(nxt['all_exp']) if nxt else None, 'capacity': capacity(view), 'members': members(view, now, player_level),
            'checked_in': view['checkin_day'] == clock.day(now), 'sign_in': {'coin': M['guild_sign_in_coin'], 'exp': M['guild_sign_in_exp']},
            'log': view['log'], 'created': view['created'],
            'boss': {'current': b['current'], 'cleared': b['cleared'], 'fights': fights, 'cost': cost, 'fight_at': int(b['fight_time']) + int(M['guild_boss_fight_cd']) if b['fight_time'] else 0,
                     'exp_left': max(0, int(M['guild_boss_exp_num_max']) - (b['exp_n'] if b['exp_day'] == clock.day(now) else 0)), 'max': min(int(M['guild_boss_max_id']) - 1, max(BOSS))},
            'mill': {'gold': view['mill']['gold'], 'level': mill_level(view), 'max_level': max(MILL), 'factor': int(MILL[mill_level(view)]['factor']),
                     'next_gold': int(MILL[mill_level(view) + 1]['all_gold']) if mill_level(view) + 1 in MILL else None, 'donate': M['guild_mill_donate']},
            'orders': {'open': lv >= int(M['guild_order_open']), 'open_level': int(M['guild_order_open']), 'slots': order_slots(view),
                       'list': [{**o, 'time': int(ORDER[o['id']]['time']), 'awards': ORDER[o['id']]['awards'], 'picture': ORDER[o['id']]['picture'],
                                 'up_cost': ORDER[o['id']]['up_cost'] if int(ORDER[o['id']]['next_id'] or 0) in ORDER else '',
                                 'ready_at': o['start'] + int(ORDER[o['id']]['time']) if o['start'] else 0} for o in view['orders']['list']],
                       'refresh_at': int(view['orders']['refresh_at'])}}


def boss_view(row):
    return {'id': int(row['id']), 'lv': int(row['lv']), 'hp': int(row['hp'] or 0), 'power': int(row['power'] or 0), 'show': row['show'],
            'battle_awards': row['battle_awards'], 'kill_awards': row['kill_awards'], 'guild_exp': int(row['guild_exp'] or 0)}


def bosses():
    return [boss_view(r) for _, r in sorted(BOSS.items())]


def action(state, request, now, rng=secrets.randbelow, fight=None, player_level=1):
    act = request.get('action')
    if act == 'create':
        if state.get('guild'): raise GuildError('Bạn đã có Bang Hội')
        if not unlocked(state): raise GuildError('Bang Hội mở khóa sau ải %d' % UNLOCK_STAGE)
        name = str(request.get('name', '')).strip(); lo, hi = [int(x) for x in str(M['guild_name_num_max']).split('|')]
        if not lo <= len(name) <= hi: raise GuildError('Tên Bang Hội phải có từ %d đến %d ký tự' % (lo, hi))
        if not any(c.isalpha() for c in name): raise GuildError('Tên Bang Hội phải chứa ít nhất một chữ cái')
        flag = int(request.get('flag', 1))
        if flag not in D['flags']: raise GuildError('Lá cờ không hợp lệ')
        cd = int(state.get('guild_dissolved_at', 0)) + int(M['guild_dissolve_cd'])
        if now < cd: raise GuildError('Vui lòng chờ trước khi tạo Bang Hội mới')
        take(state, pairs(M['create_guild_cost']))
        state['guild'] = fresh(name, flag, str(request.get('notice', ''))[:100], now, rng)
        log(state['guild'], now, 'Đã tạo Bang Hội')
        return {}
    g = data(state, now, rng)
    if not g: raise GuildError('Bạn chưa gia nhập Bang Hội')
    lv = level_of(g['exp'])
    if act == 'edit':
        if 'name' in request and str(request['name']).strip() != g['name']:
            name = str(request['name']).strip(); lo, hi = [int(x) for x in str(M['guild_name_num_max']).split('|')]
            if not lo <= len(name) <= hi or not any(c.isalpha() for c in name): raise GuildError('Tên không hợp lệ')
            take(state, pairs(M['modify_guild_name_cost'])); g['name'] = name
        if 'flag' in request:
            if int(request['flag']) not in D['flags']: raise GuildError('Lá cờ không hợp lệ')
            g['flag'] = int(request['flag'])
        if 'notice' in request: g['notice'] = str(request['notice'])[:100]
        return {}
    if act == 'dissolve':
        state['guild'] = None; state['guild_dissolved_at'] = now
        return {}
    if act == 'checkin':
        if g['checkin_day'] == clock.day(now): raise GuildError('Hôm nay bạn đã điểm danh')
        g['checkin_day'] = clock.day(now); got = pairs(M['guild_sign_in_coin']); add(state, got)
        g['exp'] += int(M['guild_sign_in_exp']); log(g, now, 'Điểm danh hằng ngày: +%s EXP' % M['guild_sign_in_exp'])
        return {'got': got}
    if act == 'donate':
        if lv < int(M['guild_order_open']): raise GuildError('Mở khóa khi Bang Hội đạt cấp %s' % M['guild_order_open'])
        opts = [pairs(x) for x in str(M['guild_mill_donate']).split('|')]
        i = int(request.get('index', 0))
        if not 0 <= i < len(opts): raise GuildError('Lựa chọn không hợp lệ')
        if mill_level(g) >= max(MILL) and int(g['mill']['gold']) >= int(MILL[max(MILL)]['all_gold']): raise GuildError('Cối xay đã đạt cấp tối đa')
        take(state, opts[i]); g['mill']['gold'] += sum(opts[i].values())
        g['orders']['list'] = new_orders(g, rng, g['orders']['list'])   # a higher Mill opens more order slots
        return {}
    if act in ('order_start', 'order_complete', 'order_upgrade', 'order_refresh'):
        if lv < int(M['guild_order_open']): raise GuildError('Mở khóa khi Bang Hội đạt cấp %s' % M['guild_order_open'])
        orders = g['orders']['list']
        if act == 'order_refresh':
            if now < int(g['orders']['refresh_at']): raise GuildError('Đơn hàng mới xuất hiện sau mỗi 12 giờ')
            keep = [o for o in orders if o['start']]
            g['orders']['list'] = new_orders(g, rng, keep); g['orders']['refresh_at'] = now + int(M['guild_order_cd'])
            return {}
        i = int(request.get('slot', -1))
        if not 0 <= i < len(orders): raise GuildError('Đơn hàng không khả dụng')
        o = orders[i]; row = ORDER[o['id']]
        if act == 'order_start':
            if o['start']: raise GuildError('Đơn hàng đang được xử lý')
            o['start'] = now; return {}
        if act == 'order_upgrade':
            nid = int(row['next_id'] or 0)
            if o['start'] or nid not in ORDER: raise GuildError('Không thể nâng cấp đơn hàng này')
            take(state, pairs(row['up_cost'])); o['id'] = nid; return {}
        if not o['start'] or now < o['start'] + int(row['time']): raise GuildError('Đơn hàng chưa hoàn tất')
        factor = int(MILL[mill_level(g)]['factor']) / 10000
        got = {k: int(n * factor) for k, n in pairs(row['awards']).items()}; add(state, got)
        orders.pop(i); g['orders']['list'] = new_orders(g, rng, orders)
        return {'got': got}
    if act == 'boss_fight':
        if not callable(fight): raise GuildError('Battle engine chưa sẵn sàng; không thể xử lý Guild Boss')
        bid = int(request.get('boss', 0)); b = g['boss']
        if bid not in BOSS or bid > min(int(M['guild_boss_max_id']) - 1, max(BOSS)): raise GuildError('Thủ lĩnh chưa khả dụng')
        if bid > b['current']: raise GuildError('Hãy đánh bại thủ lĩnh trước đó')
        cost, fights = boss_cost(g, now)
        if cost is None: raise GuildError('Đã hết lượt chiến đấu, hãy chờ hồi lượt')
        if any(int(state['items'].get(k, 0)) < n for k, n in cost.items()): raise GuildError('Không đủ tài nguyên')
        row = BOSS[bid]
        outcome = fight(row)
        if not isinstance(outcome, tuple) or len(outcome) != 2 or type(outcome[0]) is not bool:
            raise GuildError('Kết quả Guild Boss không hợp lệ; không cấp thưởng')
        win, report = outcome
        take(state, cost)
        got = pairs(row['battle_awards'])
        b['fights'] = fights + 1; b['fight_time'] = now
        if win:
            for k, n in pairs(row['kill_awards']).items(): got[k] = got.get(k, 0) + n
            if bid not in b['cleared']: b['cleared'].append(bid)
            if bid == b['current']: b['current'] = int(row['next_id'] or bid)
            day = clock.day(now)
            if b['exp_day'] != day: b['exp_day'] = day; b['exp_n'] = 0
            if b['exp_n'] < int(M['guild_boss_exp_num_max']): b['exp_n'] += 1; g['exp'] += int(row['guild_exp'] or 0)
            log(g, now, 'Đã đánh bại thủ lĩnh %d' % bid)
        add(state, got)
        return {'got': got, 'win': win, 'report_index': report}
    if act == 'open':
        return {}
    raise GuildError('Thao tác không khả dụng')
