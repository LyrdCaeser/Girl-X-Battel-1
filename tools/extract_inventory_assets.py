"""Extract a small, reproducible subset of the original Unity atlases.

Reads the user's decompiled copy; writes only inside this local web project.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('/Users/schroyle/Downloads/Decomp files')
ATLAS = SOURCE / 'unity/Assets/hotres/atlases'
TABLES = SOURCE / 'lua/data/tables'
OUT = ROOT / 'web/assets'


def lua_table(path: Path):
    text = path.read_text(encoding='utf-8-sig')
    keys_text = text.split('table.keys = {', 1)[1].split('}', 1)[0]
    keys = {key: int(index) - 1 for key, index in re.findall(r'(\w+)\s*=\s*(\d+)', keys_text)}
    rows = {}
    for match in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\n\s*\}', text, re.S):
        values = []
        for part in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', match.group(2)):
            values.append(json.loads(part) if part.startswith('"') else float(part) if '.' in part else int(part))
        rows[match.group(1)] = {key: values[index] for key, index in keys.items() if index < len(values)}
    return rows


def sprites(prefab: Path):
    text = prefab.read_text(errors='ignore')
    return [(m.group(1), *(int(m.group(i)) for i in range(2, 6))) for m in re.finditer(
        r'- name: ([^\r\n]+)\s+x: (\d+)\s+y: (\d+)\s+width: (\d+)\s+height: (\d+)', text)]


def extract(prefab: Path, wanted: set[str], dest: Path):
    found = [row for row in sprites(prefab) if row[0] in wanted]
    if not found:
        return set()
    basename = prefab.stem
    rgb = Image.open(prefab.with_name(basename + '_RGB.png')).convert('RGB')
    alpha = Image.open(prefab.with_name(basename + '_Alpha.png')).convert('RGB')
    dest.mkdir(parents=True, exist_ok=True)
    names = set()
    for name, x, y, width, height in found:
        box = (x, y, x + width, y + height)
        crop = rgb.crop(box)
        crop.putalpha(alpha.crop(box).getchannel('R'))
        crop.save(dest / f'{name}.png', optimize=True)
        names.add(name)
    return names


items = {}
for table in sorted(TABLES.glob('item[1-5].lua')):
    items.update(lua_table(table))
english = lua_table(TABLES / 'en_en/item_text_en_en.lua')
catalog = {}
for item_id, row in items.items():
    if int(row.get('show_in_bag') or 0) != 1:
        continue
    catalog[item_id] = {
        'id': int(item_id), 'name': english.get(item_id, {}).get('name') or f'Objeto {item_id}',
        'description': english.get(item_id, {}).get('desc') or '',
        'icon': row.get('icon') or '', 'quality': int(row.get('qlt') or 0),
        'category': int(row.get('show_bag_type') or 0), 'type': int(row.get('type') or 0),
    }
(OUT / 'items-catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, separators=(',', ':')))

card_names = {'partner_card_' + str(g['id']) for g in json.loads((OUT / 'girls-catalog.json').read_text())}
card_found = set()
for prefab in sorted(ATLAS.glob('partner_card_group_*_web/*.prefab')):
    card_found |= extract(prefab, card_names - card_found, OUT / 'cards')
(OUT / 'cards.json').write_text(json.dumps(sorted(int(n.removeprefix('partner_card_')) for n in card_found)))

# Item icon sheets are split in two atlases. Extract images named by the item table.
icon_names = {str(row['icon']) for row in catalog.values() if row['icon']}
icon_found = set()
for prefab in [ATLAS / 'icon_image_web/icon_image_web.prefab', ATLAS / 'icon_image2_web/icon_image2_web.prefab']:
    icon_found |= extract(prefab, icon_names - icon_found, OUT / 'item-icons')
(OUT / 'item-icons.json').write_text(json.dumps(sorted(icon_found)))

extract(ATLAS / 'commonbtn/CommonBtn.prefab', {'win_back_btn', 'switch_btn', 'chat_return_icon', 'btn_partner_station', 'partner_station_change', 'partner_data_btn'}, OUT / 'ui')
extract(ATLAS / 'commonui/CommonUI.prefab', {'item_bg', 'equip_star', 'partner_card', 'partner_card_2', 'quality_0', 'quality_1', 'quality_2', 'quality_3', 'quality_4', 'quality_5', 'quality_6', 'quality_7', 'quality_select'}, OUT / 'ui')
extract(ATLAS / 'peace_sprite2_web/peace_sprite2_web.prefab', {'new_formation_team_nav_icon1', 'new_formation_team_nav_icon2'}, OUT / 'ui')
extract(ATLAS / 'partner/partner.prefab', {'partner_battle_point_icon', 'attr_hp_icon', 'attr_atk_icon', 'attr_def_icon', 'attr_spd_icon', 'partner_star_red', 'partner_detail_arrow', 'partner_detail_bubble_bg', 'partner_cv_bg', 'partner_like01', 'partner_like02', 'skill_icon_bg', 'grade_crown', 'partner_weapon', 'partner_cloth', 'partner_shoes', 'partner_treasure'}, OUT / 'detail')
extract(ATLAS / 'partner_gravity1_web/partner_gravity1_web.prefab', {'partner_new_bg_cloud'}, OUT / 'detail')

partners = json.loads((ROOT / 'data/partner.json').read_text())
jobs = lua_table(TABLES / 'en_en/job_text_en_en.lua')
dialog = lua_table(TABLES / 'en_en/partner_dialog_text_en_en.lua')
skill_names = lua_table(TABLES / 'en_en/skill_text_en_en.lua')
skills = {}
for table in sorted(TABLES.glob('skill[1-8].lua')):
    skills.update(lua_table(table))
skill_dest = OUT / 'skills'
skill_dest.mkdir(exist_ok=True)
details = {}
for partner_id, row in partners.items():
    if not partner_id.isdecimal():
        continue
    skill_list = []
    for key in ('act_skill_id', 'pas_skill1_id', 'pas_skill2_id', 'pas_skill3_id'):
        skill_id = str(row.get(key) or '')
        if not skill_id or skill_id == '-1':
            continue
        info = skills.get(skill_id, {})
        icon = str(info.get('icon_id') or '')
        source = SOURCE / 'unity/Assets/hotres/textures/skill_web' / (icon + '.png')
        if re.fullmatch(r'skill_icon_[0-9]+', icon) and source.is_file():
            shutil.copyfile(source, skill_dest / source.name)
        else:
            icon = ''
        skill_list.append({'id': int(skill_id), 'name': skill_names.get(skill_id, {}).get('name') or 'Skill', 'icon': icon})
    dialog_ids = str(row.get('dialogs') or '').split('|')
    quote = next((dialog[d]['text'] for d in dialog_ids if d in dialog and dialog[d].get('text')), '')
    details[partner_id] = {'job': jobs.get(str(row.get('job')), {}).get('name') or '', 'quote': quote,
                           'stats': {key: row.get(key, 0) for key in ('base_hp', 'base_atk', 'base_arm', 'base_spd', 'grow_hp', 'grow_atk', 'grow_arm', 'grow_spd')},
                           'skills': skill_list}
(OUT / 'girl-details.json').write_text(json.dumps(details, ensure_ascii=False, separators=(',', ':')))
print(f'{len(details)} partner detail records')
print(f'{len(card_found)} card portraits, {len(icon_found)} item icons, {len(catalog)} catalog rows')
