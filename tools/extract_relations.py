"""Dates / relationships (DatesWindow.lua, DatesPledgeWindow.lua): appointment levels, misc rules, gifts,
per-girl voice lines (partner_dialog → sound1/sound2) and dates art. Output: data/relations.json, web/assets/dates/.
Voice audio is converted on demand by the server (/assets/voice/<sound_id>.mp3) from the read-only sources."""
import json, re, shutil, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/dates'; OUT.mkdir(parents=True, exist_ok=True)
d = sqlite3.connect(DEC / 'data/data.db'); en = sqlite3.connect(DEC / 'data/en_en.db')
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig')
def misc(k):
    m = re.search(r'\t' + k + r' = \{\s*"[^"]+",\s*"?([^"\n,]*)"?,', misc_text); return m.group(1) if m else ''
rules = {k: misc(k) for k in ('love_point_max_base', 'love_point_max_grow', 'love_point_max_wall_papper', 'love_gift_cost',
                               'love_gift_point', 'love_gift_item_num', 'love_point_vow_cost', 'love_gift_initial', 'partner_data_lev')}
appointment = [{'id': int(r[0]), 'point': int(r[1]), 'icon': r[2], 'bonus': r[3]} for r in d.execute('select * from appointment')]
item_text = {r[0]: r[1] for r in en.execute('select id, name from item_text_en_en')}
first, count = [int(x) for x in rules['love_gift_item_num'].split('|')]
groups = dict(d.execute('select id, _group from dates_gifts'))
gifts = {str(i): {'name': item_text.get(str(i), str(i)), 'group': int(groups.get(str(i), 0) or 0)} for i in range(first, first + count)}
sounds = {}
for t in ('sound1', 'sound2'):
    for sid, res in d.execute(f'select id, destroy from {t}'):
        if res and res.startswith('partner_sound/'):
            sounds[sid] = res
text = dict(en.execute('select id, text from partner_dialog_text_en_en'))
types = dict(en.execute('select id, text from partner_dialog_type_text_en_en'))
dialogs = {}
for did, sound, typ, cond, skin, pid, *_ in d.execute('select * from partner_dialog'):
    if not pid:
        continue
    dialogs.setdefault(pid, []).append({'id': did, 'type': int(typ), 'cond': int(cond or 0), 'text': text.get(did, ''),
                                        'sound': sound if sound in sounds else ''})
for n in [f'icon_{i}' for i in range(first, first + count)] + [p.stem for p in CUT.glob('dates_*.png')] + [f'love_point_icon{i}' for i in range(1, 7)] + ['partner_cv_bg', 'blue_btn_60_60', 'help_2', 'icon_43', 'icon_44', 'icon_45', 'icon_49', 'partner_detail_bubble_bg', 'partner_detail_bubble_arrow']:
    if (CUT / f'{n}.png').exists():
        shutil.copyfile(CUT / f'{n}.png', OUT / f'{n}.png')
# Gift Box (item 43, gift_id 30001 → gift.lua dropbox_ids): 1 random gift + several Gift Shards
gift_lua = (DEC / 'lua/data/tables/gift.lua').read_text(encoding='utf-8-sig')
box_ids = [int(x) for x in re.search(r'\["30001"\] = \{\s*30001,\s*[^,]*,\s*"[^"]*",\s*"[^"]*",\s*"([^"]*)"', gift_lua).group(1).split('|')]
drop = json.loads((ROOT / 'data/dropbox.json').read_text())
gift_box = {str(b): [[r['item'], int(r['weight'])] for r in drop.values() if int(r['dropbox_id']) == b and int(r['weight']) > 0] for b in box_ids}
# CV names (partner_text.cv_name), File data (partner.partner_data_id → appointment_partner_data_text, unlocked at
# partner_data_lev) and the Date chain (partner.achievement_id → partner_achievement: desc, plot, next)
def lua_rows(path):
    text = path.read_text(encoding='utf-8-sig')
    keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', text.split('table.keys = {', 1)[1].split('}', 1)[0])}
    rows = {}
    for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\n\s*\}', text, re.S):
        vals = [json.loads(v) if v.startswith('"') else float(v) if '.' in v else int(v) for v in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
        rows[m.group(1)] = {k: vals[i] for k, i in keys.items() if i < len(vals)}
    return rows
T = DEC / 'lua/data/tables'
ptext = lua_rows(T / 'en_en/partner_text_en_en.lua')
cv = {k: r.get('cv_name') for k, r in ptext.items() if isinstance(r.get('cv_name'), str) and r.get('cv_name') not in ('', '-1', 'undefined')}
pdata = {}
for f in ('partner1.lua', 'partner2.lua'):
    for k, r in lua_rows(T / f).items():
        pdata[k] = {'data': str(r.get('partner_data_id') or ''), 'ach': str(r.get('achievement_id') or '')}
dtext = {k: {'title': r.get('title'), 'text': r.get('text')} for k, r in lua_rows(T / 'en_en/appointment_partner_data_text_en_en.lua').items()}
files = {k: [dtext[i] for i in v['data'].split('|') if i in dtext] for k, v in pdata.items() if v['data'] and v['data'] != '0'}
ach_rows = lua_rows(T / 'partner_achievement.lua'); ach_text = {k: r.get('desc') for k, r in lua_rows(T / 'en_en/partner_achievement_text_en_en.lua').items()}
achievements = {k: {'desc': ach_text.get(k, ''), 'type': r.get('type'), 'value': r.get('complete_value'), 'plot': r.get('plot_id'), 'next': r.get('next_achieve_id'), 'bg': r.get('bg_icon')} for k, r in ach_rows.items()}
dates_chain = {k: [int(x) for x in v['ach'].split('|') if x.isdigit()] for k, v in pdata.items() if v['ach'] and v['ach'] != '0'}
(ROOT / 'data/relations.json').write_text(json.dumps({'rules': rules, 'appointment': appointment, 'gifts': gifts, 'dialog_types': types, 'gift_box': gift_box,
                                                     'cv': cv, 'files': files, 'achievements': achievements, 'dates_chain': dates_chain,
                                                     'dialogs': dialogs, 'sounds': sounds}, ensure_ascii=False, separators=(',', ':')))
(OUT / 'cv.json').write_text(json.dumps(cv, ensure_ascii=False, separators=(',', ':')))  # small file for the girl sheet
print(len(gifts), 'gifts;', len(dialogs), 'girls with lines;', len(sounds), 'voice files;', len(list(OUT.glob('*'))), 'sprites')
