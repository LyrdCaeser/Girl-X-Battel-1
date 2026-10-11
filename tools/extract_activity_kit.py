"""Generic event kit data: exchange shops (activity_*_shop / *_exchange) and mission boards (activity_*_task / *_mission)
of many limited events, keyed by activity id (data/events.json catalog). Output data/activity_kit.json.

Shop rows share one shape {id, cost 'item#n|item#n', award(s), limit}. Mission rows vary (complete / complete_value / value / num,
award / awards, limit) and their text lives in <table>_text_en_en; the counter each mission needs is derived from that text in
gxb2/activity_kit.py. The event -> table pairing is inferred from xyd.ActivityID usage in the client Lua and the activity
titles; tables that couldn't be paired with confidence are NOT listed (see UNPAIRED)."""
import json, os, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
# activity id: (shop table | None, mission table | None)
EVENTS = {
    183: ('activity_exchange_award', None),        # Super Exchange
    64: ('activity_jackpot_exchange', None),       # Jackpot of Fortune shop (spins are gxb2/jackpot.py)
    232: ('activity_beach_shop', None),            # Skin Exchange
    244: ('activity_equip_exchange', None),        # Antique Limited Exchange
    299: ('activity_children_shop', 'activity_children_task'),          # Kid's Store
    274: ('activity_firework_shop', None),         # Firework Display
    206: ('activity_time_shop', 'activity_time_mission'),               # The Secret of Time
    346: ('activity_star_plan_shop', None),        # Catch An Astral
    166: ('activity_lafuli_shop', None),           # Luvly's Journey
    304: ('activity_4birthday_shop', 'activity_4birthday_task'),        # Celebration Party
    330: ('activity_pirate_shop_awards', None),    # Palace Vaults (collection rewards: gxb2/pirate.py)
    333: ('activity_halloween2022_shop', None),    # Lantern Secrets
    295: ('activity_star_altar_exchange', 'activity_star_altar_mission'),  # Falling Stars
    234: ('activity_jungle_shop', None),           # Jungle Exploration
    317: ('activity_goldfish_shop', None),         # Goldfish Scooper
    248: ('activity_trickortreat_shop', 'activity_trickortreat_task'),  # Trick or Treat
    141: ('activity_fairytale_shop', 'activity_fairytale_mission'),     # Fairytale Land
    121: ('activity_date_shop', None),             # Lovely Date
    260: (None, 'activity_luckyboxes_mission'),    # Lucky Dips
    251: (None, 'activity_secrettreasure_mission'),  # Treasure Hunt
    214: (None, 'activity_space_explore_mission'),   # Bizarre Adventures
    230: (None, 'activity_beach_mission'),         # To The Beach!
    325: (None, 'activity_repair_console_mission'),  # Game Console Fixer
    338: (None, 'activity_blind_box_mission'),     # Blind Box Frenzy
    308: (None, 'activity_chime_mission'),         # Wish Upon a Chime
    93: (None, 'activity_making_coffee_mission'),  # Coffee Lab
    279: (None, 'activity_lflcastle_task'),        # Luvly's Dream Castle
    300: (None, 'activity_spfarm_task'),           # Dimensional Manor
    290: (None, 'activity_easter2022_mission'),    # Easter Egg Factory
}
UNPAIRED = ['activity_limit_exchange_awards (Girls/10-Star Exchange need a girl picker)', 'activity_doll_buy', 'activity_return_shop',
            'activity_festival', 'activity_food_festival_awards', 'activity_point_giftbox', 'activity_giftbox', 'activity_gamble_plus_mission',
            'activity_turing_task', 'activity_vampire_task', 'activity_candy_collect_task']
# Missions whose text isn't in a <table>_text table: the client shows them from the window they lead to / a shared key.
WINDOW_TEXT = {'campaign_window': 'Collect Auto-Battle Loot {1} times in Campaign', 'tavern_window': 'Complete {1} Internship Quest(s) (4-star or above)',
               'arena_window': 'Complete {1} battles in Junior Varsity', 'summon_window': 'Pull Adv. Capsule {1} times'}
TABLE_TEXT = {'activity_blind_box_mission': 'Obtain {1} VIP Exp'}
NEED = ('complete_value', 'complete', 'value', 'num', 'complete_value1')
AWARD = ('awards', 'award', 'free_awards')
db = sqlite3.connect(DEC / 'data/en_en.db')
titles = {a['id']: a['title'].replace('\n', ' ') for a in json.load(open(ROOT / 'data/events.json'))['activities']}
item_ids = set()


def first(row, keys, default=''):
    for k in keys:
        if k in row and row[k] not in ('', None): return row[k]
    return default


def pair_ids(text):
    return [p.split('#')[0] for p in str(text or '').split('|') if '#' in p]


def shop_rows(table):
    rows = []
    for r in sorted(read_table(table).values(), key=lambda r: int(r['id'])):
        aw, cost = first(r, AWARD), str(first(r, ('cost',)))
        if not aw or not cost: continue
        item_ids.update(pair_ids(aw)); item_ids.update(pair_ids(cost))
        rows.append({'id': int(r['id']), 'cost': cost, 'award': str(aw), 'limit': int(first(r, ('limit', 'limit_times'), 0) or 0),
                     'group': int(first(r, ('tab', 'type'), 0) or 0), 'unlock': int(r.get('unlock') or 0) if isinstance(r.get('unlock'), (int, float)) else 0})
    return rows


def mission_rows(table):
    try: text = {str(k): v for k, v in db.execute(f'select * from {table}_text_en_en')}
    except sqlite3.OperationalError: text = {}
    rows = []
    for r in sorted(read_table(table).values(), key=lambda r: int(r['id'])):
        aw = first(r, AWARD)
        if not aw or '#' not in str(aw): continue
        need = int(first(r, NEED, 1) or 1)
        item_ids.update(pair_ids(aw))
        label = text.get(str(r['id'])) or text.get(str(r.get('desc', ''))) or TABLE_TEXT.get(table) or WINDOW_TEXT.get(str(r.get('go_window', ''))) or ''
        rows.append({'id': int(r['id']), 'need': need, 'award': str(aw), 'limit': int(first(r, ('limit', 'repeat_times'), 1) or 1),
                     'daily': int(r.get('is_daily') or 0), 'text': label})
    return rows


out = {'events': {}, 'unpaired': UNPAIRED}
for eid, (shop, mission) in EVENTS.items():
    ev = {'title': titles.get(eid, str(eid))}
    if shop: ev['shop'] = shop_rows(shop); ev['shop_table'] = shop
    if mission: ev['missions'] = mission_rows(mission); ev['mission_table'] = mission
    out['events'][str(eid)] = ev
names = {}
for i in sorted(item_ids, key=int):
    row = db.execute('select name from item_text_en_en where id=?', (int(i),)).fetchone()
    if row: names[i] = row[0]
out['names'] = names
(ROOT / 'data/activity_kit.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
for eid, ev in out['events'].items():
    print(eid, ev['title'], len(ev.get('shop', [])), 'shop', len(ev.get('missions', [])), 'missions')
