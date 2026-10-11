"""Skill-Synchronize (SkillResonateWindow, Cosmic girls of group 7): each of the 4 elite skills goes 1→10 (stored 0-9,
cost skill_resonate_cost[lv+1]); the Synchronize Level is the sum + 4 (HeroAttr: getTotalExLev() + 4) and unlocks the
cumulative bonuses of skill_resonate_effect (crit / critTime / hit per mille). Output data/resonate.json."""
import json, re, shutil, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
T = Path.home() / 'Downloads/Decomp files/lua/data/tables'


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


cost = {k: r['cost'] for k, r in lua_table(T / 'skill_resonate_cost.lua').items()}
effects = {}
for r in sorted(lua_table(T / 'skill_resonate_effect.lua').values(), key=lambda r: int(r['id'])):
    effects.setdefault(str(r['pr_table_id']), []).append({'level': int(r['level']), 'show': r['effect_show'], 'effect': r['effect']})
# the four elite skills of each Cosmic girl, one skill id per level (<girl><n>01 .. <girl><n>10) with their texts
db = sqlite3.connect(Path.home() / 'Downloads/Decomp files/data/en_en.db')
skills = {}
for girl in effects:
    ids = [int(girl) * 1000 + n * 100 + lv for n in range(1, 5) for lv in range(1, 11)]
    for r in db.execute('select id, name, desc from skill_text_en_en where id in (%s)' % ','.join(map(str, ids))):
        skills[str(r[0])] = [r[1], r[2]]
out = {'cost': cost, 'max': len(cost), 'effects': effects, 'skills': skills}
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
TEX = Path.home() / 'Downloads/Decomp files/unity/Assets/hotres/textures/common_ui_texture_web'
dst = ROOT / 'web/assets/souls'
for name in ['skill_resonate_effect_arrow', 'skill_resonate_icon', 'switch_btn', '9gongge53', 'line_bold'] + [f'skill_resonate_effect_bg{i}' for i in range(1, 12)]:
    for src in (CUT / f'{name}.png', TEX / f'{name}.png'):
        if src.exists(): shutil.copy2(src, dst / src.name); break
(ROOT / 'data/resonate.json').write_text(json.dumps(out, separators=(',', ':')))
print(len(cost), 'levels,', {k: len(v) for k, v in effects.items()}, len(skills), 'skill texts')
