"""Draw-with-a-token minigames (LOCAL-061): Goldfish Scooper, Seaside Fishing, Spin the Wheel, Easter Egg Factory, Childhood
Memories, Lucky Dips, Jungle Exploration, Ring Toss. One engine (gxb2/activity_draw.py); this file pairs each event with the
client tables and misc costs (activity_*_cost, activity_*_buy). Output data/activity_draw.json.

Tables give the prizes (a weighted table or dropboxes) and the milestone awards (`complete` / `point`); which counter the
server used for the milestones and the details marked LOCAL below aren't in the client, see DESIGN_DECISIONS LOCAL-061."""
import json, re, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')
boxes = {}
for r in json.loads((ROOT / 'data/dropbox.json').read_text()).values(): boxes.setdefault(int(r['dropbox_id']), []).append(r)
titles = {a['id']: a['title'].replace('\n', ' ') for a in json.load(open(ROOT / 'data/events.json'))['activities']}
item_ids = set()


def misc(key):
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', misc_text)
    return json.loads(m.group(1))


def ids(text):
    return [p.split('#')[0] for p in str(text or '').split('|') if '#' in p]


def prizes_from_box(box):
    rows = [{'awards': r['item'], 'weight': int(r['weight'])} for r in boxes[int(box)] if int(r['weight']) > 0 and r['item'] not in ('0', '')]
    for r in rows: item_ids.update(ids(r['awards']))
    return rows


def prizes_from_table(name, weight='weight', awards='awards', stock=None, where=None):
    out = []
    for r in sorted(read_table(name).values(), key=lambda r: int(r['id'])):
        if where and not where(r): continue
        a = str(r.get(awards) or '')
        if '#' not in a or not int(r.get(weight) or 0): continue
        p = {'awards': a, 'weight': int(r[weight])}
        if stock and r.get(stock): p['stock'] = int(r[stock])
        out.append(p); item_ids.update(ids(a))
    return out


def milestones(name, need_key, awards='awards'):
    rows = [{'need': int(r[need_key]) if need_key else int(r['id']), 'awards': str(r[awards]), 'area': int(r.get('area') or 0)}
            for r in sorted(read_table(name).values(), key=lambda r: int(r['id'])) if '#' in str(r.get(awards) or '')]
    for r in rows: item_ids.update(ids(r['awards']))
    return rows


def mode(cost, groups, always=''):
    item_ids.update(ids(cost)); item_ids.update(ids(always))
    return {'cost': cost, 'always': always, 'groups': [{'weight': w, 'prizes': p} for w, p in groups]}


EVENTS = {
    308: dict(unit='pulls', modes=[mode(misc('activity_chime_cost1'), [(1, prizes_from_table('activity_chime_dropbox', awards='award', where=lambda r: r['type'] == 1))]),
                                  mode(misc('activity_chime_cost2'), [(1, prizes_from_table('activity_chime_dropbox', awards='award', where=lambda r: r['type'] == 2))])],
              guarantee={'mode': 1, 'every': 20, 'awards': '986001#1'}, milestones=[]),  # a Shard of Reflections per 20 Gilded Cranes (ACTIVITY_CHIME_HELP)
    317: dict(unit='scoops', modes=[mode(misc('activity_goldfish_cost'), [(1, prizes_from_table('activity_goldfish'))])],
              milestones=milestones('activity_goldfish_awards', 'complete'), buy={'cost': misc('activity_goldfish_pack_cost'), 'get': misc('activity_goldfish_pack_get'),
                                                                                    'limit': int(misc('activity_goldfish_pack_times'))}),
    245: dict(unit='fish', modes=[mode(misc('activity_fish_cost'), [(1, prizes_from_table('activity_fish_main'))])],
              bonus={'chance': int(misc('activity_fish_extra_pro')), 'prizes': prizes_from_box(32004)},
              milestones=milestones('activity_fish_awards', 'complete')),
    286: dict(unit='spins', modes=[mode(misc('activity_clock_cost'), [(1, prizes_from_table('activity_clock_gamble', stock='num'))])],
              milestones=milestones('activity_clock_awards', 'complete')),
    290: dict(unit='eggs', modes=[mode(misc('activity_easter2022_cost1'), [(1, prizes_from_box(32014))]),
                                  mode(misc('activity_easter2022_cost2'), [(1, prizes_from_box(32015))])],
              milestones=milestones('activity_easter2022_awards', 'point')),
    298: dict(unit='draws', modes=[mode(misc('activity_children_gamble_cost'), [(1, prizes_from_box(32016))], always=misc('activity_children_gamble_award'))],
              milestones=milestones('activity_children_collect_award', 'point'), buy={'cost': misc('activity_children_buy_cost'), 'get': misc('activity_children_gamble_cost'),
                                                                                       'limit': int(misc('activity_children_buy_limit'))}),
    260: dict(unit='draws', modes=[mode(misc('activity_luckyboxes_cost'), [(1, prizes_from_box(32008))])],
              big=[{'awards': r['awards'], 'rate': float(r['rate'])} for r in read_table('activity_luckyboxes_award').values()],
              pity={'max': int(misc('activity_luckyboxes_pointmax')), 'add': int(misc('activity_luckyboxes_pointuprise'))}, milestones=[]),
    234: dict(unit='explorations', modes=[mode(misc('activity_jungle_cost'), [(1, prizes_from_box(250101))])],
              milestones=[m for m in milestones('activity_jungle_awards', 'point') if m['area'] == 1]),
    283: dict(unit='rings', modes=[mode(misc('activity_lasso_cost'), [(60, prizes_from_box(32011)), (60, prizes_from_box(32012)),
                                                                     (80, prizes_from_box(32009)), (80, prizes_from_box(32010))])],
              milestones=milestones('activity_lasso_awards', None), buy={'cost': misc('activity_lasso_buy').split('|')[0], 'get': misc('activity_lasso_buy').split('|')[1],
                                                                        'limit': int(misc('activity_lasso_buy_limit'))}),
}
for eid, ev in EVENTS.items():
    ev['title'] = titles.get(eid, str(eid))
    for b in ev.get('buy', {}).values(): item_ids.update(ids(b))
    for m in ev.get('big', []): item_ids.update(ids(m['awards']))
    for m in ev.get('bonus', {}).get('prizes', []): item_ids.update(ids(m['awards']))
    if ev.get('guarantee'): item_ids.update(ids(ev['guarantee']['awards']))
db = sqlite3.connect(DEC / 'data/en_en.db')
names = {}
for i in sorted(item_ids, key=int):
    row = db.execute('select name from item_text_en_en where id=?', (int(i),)).fetchone()
    if row: names[i] = row[0]
(ROOT / 'data/activity_draw.json').write_text(json.dumps({'events': {str(k): v for k, v in EVENTS.items()}, 'names': names}, ensure_ascii=False, separators=(',', ':')))
for eid, ev in EVENTS.items():
    print(eid, ev['title'], [m['cost'] for m in ev['modes']], sum(len(g['prizes']) for m in ev['modes'] for g in m['groups']), 'prizes', len(ev['milestones']) if 'milestones' in ev else 0, 'milestones')
