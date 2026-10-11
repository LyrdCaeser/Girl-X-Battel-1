"""Limit-Break potentials (PotentialityComponent / PotentialityChooseWindow): partner.potential gives, per Limit-Break
stage, the three skills a girl can activate (Partner.potentials[stage] = 1..3, sent to the battle as ReportHero.potentials).
Also misc hero_break_lv_cap / hero_break_attr_up (window rows MAX LVL / HP / ATK). Icons: skill icon_id → skill_icon_<n>.
Output data/potentials.json. Sources in ~/Downloads are read only."""
import json, re, shutil, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'


def lua_table(path):
    text = path.read_text(encoding='utf-8-sig')
    keys_text = text.split('table.keys = {', 1)[1].split('}', 1)[0]
    keys = {key: int(index) - 1 for key, index in re.findall(r'(\w+)\s*=\s*(\d+)', keys_text)}
    rows = {}
    for match in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\n\s*\}', text, re.S):
        values = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p)
                  for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', match.group(2))]
        rows[match.group(1)] = {key: values[index] for key, index in keys.items() if index < len(values)}
    return rows


partners = json.loads((ROOT / 'data/partner.json').read_text())
ids = sorted({int(s) for r in partners.values() for st in str(r.get('potential') or '').split('|') for s in st.split('#') if s.strip()})
skills = {}
for f in sorted(T.glob('skill[0-9]*.lua')):
    rows = lua_table(f)
    for i in ids:
        if str(i) in rows: skills[i] = rows[str(i)]
db = sqlite3.connect(DEC / 'data/en_en.db')
text = {int(r[0]): (r[2], r[3]) for r in db.execute('select * from skill_text_en_en where id in (%s)' % ','.join(map(str, ids)))}
misc = (T / 'misc.lua').read_text(encoding='utf-8-sig')
def m(key): return re.search(r'\t' + key + r' = \{\s*"' + key + r'",\s*"([^"]*)"', misc).group(1)
out = {'skills': {}, 'lv_cap': [int(x) for x in m('hero_break_lv_cap').split('|')], 'attr_up': [float(x) for x in m('hero_break_attr_up').split('|')]}
for i in ids:
    icon = skills.get(i, {}).get('icon_id')
    name, desc = text.get(i, ('', ''))
    out['skills'][str(i)] = {'name': name, 'desc': desc, 'icon': str(icon) if icon not in (None, '', -1) else ''}
    src = CUT / f'{icon}.png'
    if src.exists() and not (ROOT / 'web/assets/skills' / src.name).exists():
        shutil.copy2(src, ROOT / 'web/assets/skills' / src.name)
(ROOT / 'data/potentials.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
print(len(ids), 'potential skills', out['lv_cap'], out['attr_up'], sorted({v['icon'] for v in out['skills'].values()}))
