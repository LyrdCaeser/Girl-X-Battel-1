"""Faction auras shown in every formation window (group_buff + group_buff_text; GroupBuffTable:getBuffIds, GroupBuffIcon
group_buff_on_N / group_buff_off_N). Output web/assets/group-buff/ (buffs.json + sprites)."""
import json, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/group-buff'; OUT.mkdir(parents=True, exist_ok=True)
db = sqlite3.connect(DEC / 'data/en_en.db')
text = {str(r[0]): (r[1], r[2]) for r in db.execute('select * from group_buff_text_en_en')}
rows = {}
for r in read_table('group_buff').values():
    i = str(r['id'])
    name, desc = text.get(i, ('', ''))
    rows[i] = {'id': int(i), 'type': int(r['type']), 'config': str(r['group_config'] or ''), 'rank': int(r['rank'] or 0),
               'show': str(r['effect_show'] or ''), 'name': name, 'desc': desc}
    for state in ('on', 'off'):
        src = CUT / f'group_buff_{state}_{i}.png'
        if src.exists():
            shutil.copy2(src, OUT / src.name)
(OUT / 'buffs.json').write_text(json.dumps(rows, ensure_ascii=False, separators=(',', ':')))
print(len(rows), len(list(OUT.glob('*.png'))))
