"""Astral Core (StarOriginDetailWindow, HeroAttr:getStarOrigin, ReportHero.star_origin): 15★ girls whose partner.star_origin
> 0 own 10 nodes (star_origin_list: start/end ids, unlock limits "pre_node#lv", node ids → star_origin_node xy). Node k at
level v is star_origin row start_k + v: cumulative `effect`, the `cost` of reaching it (items 359 / 360). Reset cost:
misc star_origin_reset_cost. Output data/astral.json. Sources in ~/Downloads are read only."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
T = Path.home() / 'Downloads/Decomp files/lua/data/tables'


def lua_table(path):
    text = path.read_text(encoding='utf-8-sig')
    keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', text.split('table.keys = {', 1)[1].split('}', 1)[0])}
    rows = {}
    for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\n\s*\}', text, re.S):
        vals = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p) for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
        rows[m.group(1)] = {k: vals[i] for k, i in keys.items() if i < len(vals)}
    return rows


levels = {k: {'cost': r['cost'], 'effect': r['effect']} for k, r in lua_table(T / 'star_origin.lua').items()}
lists = {}
for k, r in lua_table(T / 'star_origin_list.lua').items():
    lists[k] = {'start': [int(x) for x in str(r['start_ids']).split('|')], 'end': [int(x) for x in str(r['end_ids']).split('|')],
                'limits': [[int(y) for y in x.split('#')] for x in str(r['limits']).split('|')], 'nodes': [int(x) for x in str(r['node_ids']).split('|')]}
nodes = {k: [int(x) for x in str(r['xy']).split('|')] for k, r in lua_table(T / 'star_origin_node.lua').items() if r.get('xy')}
misc = (T / 'misc.lua').read_text(encoding='utf-8-sig')
reset = re.search(r'\tstar_origin_reset_cost = \{\s*"star_origin_reset_cost",\s*"([^"]*)"', misc).group(1)
out = {'levels': levels, 'lists': lists, 'nodes': nodes, 'reset_cost': reset}
# PartnerDetailWindow content_6: the faction constellation (group.star_origin_img1; Cosmos girls: partner_group7) at the list's xy
out['group_img'] = {k: r.get('star_origin_img1') for k, r in lua_table(T / 'group.lua').items()}
out['group7_img'] = {k: r['star_origin_img1'] for k, r in lua_table(T / 'partner_group7.lua').items() if r.get('star_origin_img1')}
out['group_img2'] = {k: r.get('star_origin_img2') for k, r in lua_table(T / 'group.lua').items()}
out['group7_img2'] = {k: r['star_origin_img2'] for k, r in lua_table(T / 'partner_group7.lua').items() if r.get('star_origin_img2')}
out['list_xy'] = {k: [int(x) for x in str(r.get('xy') or '0|0').split('|')] for k, r in lua_table(T / 'star_origin_list.lua').items()}
(ROOT / 'data/astral.json').write_text(json.dumps(out, separators=(',', ':')))
print(len(levels), 'levels,', len(lists), 'lists,', len(nodes), 'node positions, reset', reset)
