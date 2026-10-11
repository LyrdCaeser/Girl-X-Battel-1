"""Reverse (PotentialityBackWindow / PartnerReturnRule2Table) and 10★ Exchange (TenStarExchangeWindow):
partner_return_rule2 rows by star (dolls "table#num@awake" per group, award_self namesake 5★ copies, cost, exp / bento
returns), misc replace_10_cost_hero (identical 5★ copies per 10★+ stage), activity_10_replace_cost (5 Diplomas),
return_10star_puppet_id. Output data/partner_return.json. Sources in ~/Downloads are read only."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
T = Path.home() / 'Downloads/Decomp files/lua/data/tables'
text = (T / 'partner_return_rule2.lua').read_text(encoding='utf-8-sig')
keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', text.split('table.keys = {', 1)[1].split('}', 1)[0])}
rows = {}
for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\}', text.split('table.rows = {', 1)[1], re.S):
    vals = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p) for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
    rows[m.group(1)] = {k: vals[i] for k, i in keys.items() if i < len(vals)}
misc = (T / 'misc.lua').read_text(encoding='utf-8-sig')
g = lambda k: re.search(r'\t' + k + r' = \{\s*"' + k + r'",\s*"([^"]*)"', misc).group(1)
out = {'rules': rows, 'replace_cost_hero': [int(x) for x in g('replace_10_cost_hero').split('|')], 'replace_cost': g('activity_10_replace_cost'),
       'puppets': [int(x) for x in g('return_10star_puppet_id').split('|')]}
(ROOT / 'data/partner_return.json').write_text(json.dumps(out, separators=(',', ':')))
print(sorted(rows, key=int), out['replace_cost'])
