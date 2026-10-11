"""Menu → Help (SettingUpInfoWindow.lua): setting.lua type 1 = Help, type 2 = FAQ, titles and texts in setting_text_en_en.
Help texts are "subtitle|text||subtitle|text"; a subtitle "a_png#b_png@-Label" shows the status icons a / b before the label
(Status Icons, id 14). FAQ texts are lines separated by "|". Id 15 (Faction Aura) is drawn from group_buff (assets/group-buff).
Output: web/assets/menu/help.json and the buff icons in web/assets/menu/buffs/. Sources are read only."""
import json, re, shutil, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/menu'; (OUT / 'buffs').mkdir(parents=True, exist_ok=True)
lua = (DEC / 'lua/data/tables/setting.lua').read_text(encoding='utf-8-sig')
types = {int(i): int(t) for i, t in re.findall(r'\["(\d+)"\] = \{\s*\d+,\s*(\d+),', lua)}
en = sqlite3.connect(DEC / 'data/en_en.db')
out = {'help': [], 'faq': []}
icons = set()
for i, title, text in en.execute('select id, title, text from setting_text_en_en order by cast(id as integer)'):
    i = int(i); kind = 'help' if types.get(i) == 1 else 'faq'
    if kind == 'help':
        sections = []
        for block in str(text).split('||'):
            parts = block.split('|', 1)
            sub, body = parts[0], parts[1] if len(parts) > 1 else ''
            m = re.match(r'([\w#]+)@(.*)', sub)
            pics = []
            if m:
                pics = [p[:-4] for p in m.group(1).split('#') if p.endswith('_png')]; sub = m.group(2); icons.update(pics)
            sections.append({'title': sub, 'text': body, 'icons': pics})
        out['help'].append({'id': i, 'title': title, 'sections': sections, 'aura': i == 15})
    else:
        out['faq'].append({'id': i, 'title': title, 'lines': str(text).split('|')})
missing = []
for n in sorted(icons):
    if (CUT / f'{n}.png').exists(): shutil.copyfile(CUT / f'{n}.png', OUT / 'buffs' / f'{n}.png')
    else: missing.append(n)
(OUT / 'help.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
print(len(out['help']), 'help,', len(out['faq']), 'faq,', len(icons), 'icons; missing', missing)
