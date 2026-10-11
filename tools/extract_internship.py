"""Internship (models/Tavern.lua, TavernWindow / TavernDetailWindow / TavernMultimissionWindow): pub_mission (7 star
ranks), pub_mission_condition (faction/class conditions), pub_scroll (Internship Scrolls 24 / Advanced 25), vip
pub_mission_num, misc pub_mission_*, names and texts. Output data/internship.json + web/assets/internship/."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def misc(key):
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', misc_text)
    return json.loads(m.group(1))


vip = read_table('vip')
out = {'missions': sorted(read_table('pub_mission').values(), key=lambda r: r['id']),
       'conditions': {str(r['id']): r for r in read_table('pub_mission_condition').values()},
       'scrolls': sorted(read_table('pub_scroll').values(), key=lambda r: r['id']),
       'vip_daily': {k: int(v.get('pub_mission_num') or 0) for k, v in vip.items()},
       'misc': {k: misc(k) for k in ('pub_mission_refresh_cost', 'pub_mission_max')}}
drop = json.loads((ROOT / 'data/dropbox.json').read_text())
boxes = {int(r['award_dropbox_id']) for r in out['missions']}
out['dropbox'] = [r for r in drop.values() if int(r['dropbox_id']) in boxes]
db = sqlite3.connect(DEC / 'data/en_en.db')
out['names'] = {str(i): n for i, n in db.execute('select * from pub_mission_name_text_en_en')}
out['text'] = dict(db.execute("select name, translation from translation_en_en where name like 'PUB_%' or name like 'TAVERN%'"))
(ROOT / 'data/internship.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
OUT = ROOT / 'web/assets/internship'; OUT.mkdir(parents=True, exist_ok=True)
for p in list(CUT.glob('pub_*.png')) + list(CUT.glob('tavern_*.png')) + [CUT / f'icon_{i}.png' for i in (24, 25)] + [CUT / f'img_group{i}.png' for i in range(1, 8)] + list(CUT.glob('job_icon*.png')) + [CUT / f'{n}.png' for n in ('partner_unlock_btn', 'partner_lock_btn', 'white_btn70_70', 'blue_btn70_70', 'icon_ticket', 'select', 'help_2', 'top_bg_r_v3', '9gongge23')]:
    if p.exists() and not re.search(r'_(de_de|fr_fr|ja_jp|ko_kr|zh_cn|zh_tw)\.png$', p.name):
        shutil.copy2(p, OUT / p.name)
print(len(out['missions']), len(out['dropbox']), out['vip_daily'].get('0'), len(out['names']), sorted(p.name for p in OUT.iterdir())[:40])
