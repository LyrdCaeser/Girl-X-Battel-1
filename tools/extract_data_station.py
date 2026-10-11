"""Partner Data Station ("Student Files", PartnerDataStationWindow.lua), opened by Discuss in the Dates window.

direct.lua: per comment id (partner_comment / direct ids 8xxxxx, table_ids = the girl and her re-issues) the radar points
(atk / arm / spd / ctrl / hp over misc direct_partner_point_full), three labels (direct_label → direct_label_type colour
and sprite), four recommended skills and two artifacts (item ids). direct_text_en_en: name, review and skill notes;
direct_artifact_text_en_en: artifact name and description. direct_array.lua: recommended line-ups for Campaign /
Tower / Guild (monsters_n = six table ids, pet_n, point_n = stars). Output web/assets/station/station.json + sprites.
Sources are read only."""
import json, re, shutil, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
IMG = Path.home() / 'Downloads/Decompiled/Images (other)/partner_station'
OUT = ROOT / 'web/assets/station'; OUT.mkdir(parents=True, exist_ok=True)


def lua_table(path):
    text = path.read_text(encoding='utf-8-sig')
    keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', text.split('table.keys = {', 1)[1].split('}', 1)[0])}
    rows = {}
    for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\n\s*\}', text, re.S):
        vals = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p) for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
        rows[m.group(1)] = {k: vals[i] for k, i in keys.items() if i < len(vals)}
    return rows


num = lambda v: float(v) if v not in ('', None) else 0
en = sqlite3.connect(DEC / 'data/en_en.db')
text = {str(r[0]): r for r in en.execute('select id, name, desc, skill_desc1, skill_desc2, skill_desc3, skill_desc4 from direct_text_en_en')}
art_text = {str(r[0]): (r[1], r[2]) for r in en.execute('select id, artifact_name, artifact_desc from direct_artifact_text_en_en')}
label_text = {str(r[0]): r[1] for r in en.execute('select id, desc from direct_label_text_en_en')}
labels_t = lua_table(T / 'direct_label.lua'); types = lua_table(T / 'direct_label_type.lua')
labels = {k: {'text': label_text.get(k, ''), 'color': '#' + types[str(r['label_type'])]['label_text_color'], 'icon': types[str(r['label_type'])]['label_icon']}
          for k, r in labels_t.items()}
direct = lua_table(T / 'direct.lua'); arrays = lua_table(T / 'direct_array.lua')
skill_ids = {int(r[f'skill_id{i}']) for r in direct.values() for i in range(1, 5) if r.get(f'skill_id{i}')}
skills = {}
for f in sorted(T.glob('skill[0-9]*.lua')):
    rows = lua_table(f)
    for i in skill_ids:
        if str(i) in rows: skills[i] = rows[str(i)]
skill_name = {int(r[0]): r[1] for r in en.execute('select id, name from skill_text_en_en where id in (%s)' % ','.join(map(str, skill_ids)))}
misc = (T / 'misc.lua').read_text(encoding='utf-8-sig')
full = int(re.search(r'\tdirect_partner_point_full = \{\s*"[^"]+",\s*"?(\d+)', misc).group(1))
girls = {}
for cid, r in direct.items():
    t = text.get(cid)
    if not r.get('skill_id1') and not t: continue
    row = {'ids': [int(x) for x in str(r['table_ids']).split('|') if x],
           'points': [num(r.get(k)) for k in ('point_atk', 'point_arm', 'point_spd', 'point_ctrl', 'point_hp')],
           'labels': [int(r[f'label_id{i}']) for i in range(1, 4) if r.get(f'label_id{i}')],
           'name': t[1] if t else '', 'desc': t[2] if t else '', 'skills': [], 'artifacts': []}
    for i in range(1, 5):
        sid = r.get(f'skill_id{i}')
        if sid:
            icon = skills.get(int(sid), {}).get('icon_id')
            row['skills'].append({'id': int(sid), 'name': skill_name.get(int(sid), ''), 'icon': str(icon) if icon not in (None, '', -1) else '',
                                  'desc': (t[2 + i] if t else '') or ''})
    for i in range(1, 3):
        aid = r.get(f'artifact_id{i}')
        if aid:
            n, d = art_text.get(str(aid), ('', ''))
            row['artifacts'].append({'id': int(aid), 'name': n, 'desc': d})
    a = arrays.get(cid) or {}
    row['lineups'] = [{'ids': [int(x) for x in str(a.get(f'monsters_{i}') or '').split('|') if x], 'pet': int(a.get(f'pet_{i}') or 0),
                       'stars': int(a.get(f'point_{i}') or 0)} if a.get(f'monsters_{i}') else None for i in range(1, 4)]
    girls[cid] = row
for n in [p.stem for p in CUT.glob('station_*.png')] + ['partner_station_change', 'partner_like01', 'partner_like02', 'left_btn_bg',
                                                        'comic_comment_input_bg', 'comic_comment_send_btn', 'bp_none_bg', 'blue_btn_65_65']:
    if (CUT / f'{n}.png').exists(): shutil.copyfile(CUT / f'{n}.png', OUT / f'{n}.png')
for n in ('station_bg_top1', 'station_bg_top2', 'station_title_en_en'):
    shutil.copyfile(IMG / f'{n}.png', OUT / f'{n}.png')
(OUT / 'station.json').write_text(json.dumps({'full': full, 'labels': labels, 'girls': girls}, ensure_ascii=False, separators=(',', ':')))
print(len(girls), 'girls,', sum(1 for g in girls.values() if any(g['lineups'])), 'with line-ups,', len(labels), 'labels, full', full,
      '; missing skill icons', sum(1 for g in girls.values() for s in g['skills'] if not s['icon']))
