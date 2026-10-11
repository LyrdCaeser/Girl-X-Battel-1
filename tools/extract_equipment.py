"""Extract gear, antiques (artifacts) and treasures from equip1.lua + equip2.lua.

Slots follow Partner.equipments: 1 weapon, 2 clothes, 3 accessory, 4 shoes, 5 treasure, 6 antique, 7 skin.
Output: data/equipment.json and missing icons in web/assets/equipment/.
"""
from __future__ import annotations
import json, re, shutil, sqlite3, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from extract_inventory_assets import lua_table  # noqa: E402

DECOMP = Path.home() / 'Downloads/Decomp files'
TABLES = DECOMP / 'lua/data/tables'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/equipment'
FIELDS = ('pos', 'qlt', 'star', 'item_lv', 'job', 'group', 'base1', 'base2', 'base3', 'base4', 'act', 'form',
          'suit1', 'suit2', 'suit3', 'suit_skills', 'need_formula', 'formula', 'power', 'artifact_exp',
          'artifact_upg', 'artifact_next', 'treasure_upgrade', 'treasure_refresh', 'treasure_lock_up',
          'treasure_weight', 'price')


def equip_rows():
    first = (TABLES / 'equip1.lua').read_text(encoding='utf-8-sig')
    keys = first.split('table.keys = {', 1)[1].split('}', 1)[0]
    second = (TABLES / 'equip2.lua').read_text(encoding='utf-8-sig')
    rows = lua_table(TABLES / 'equip1.lua')
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'equip2.lua'   # equip2 inherits the keys of equip1 through a metatable
        path.write_text('table.keys = {' + keys + '}\ntable.rows' + second.split('table.rows', 1)[1])
        rows.update(lua_table(path))
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    catalog = json.loads((ROOT / 'web/assets/items-catalog.json').read_text())
    have = {p.stem for p in (ROOT / 'web/assets/item-icons').glob('*.png')}
    en = sqlite3.connect(DECOMP / 'data/en_en.db')
    tr = dict(en.execute('select name, translation from translation_en_en'))
    skills = {str(r[0]): r[1] for r in en.execute('select id, name from skill_text_en_en')} if en.execute(
        "select 1 from sqlite_master where name='skill_text_en_en'").fetchone() else {}

    names = {str(r[0]): r[1] for r in en.execute('select id, name from equip_text_en_en')}
    item_rows = {}
    for n in range(1, 6):
        if (TABLES / f'item{n}.lua').exists():
            item_rows.update(lua_table(TABLES / f'item{n}.lua'))
    items, icons, attrs = {}, {}, set()
    for rid, row in equip_rows().items():
        if not 1 <= int(row.get('pos', 0)) <= 6:
            continue
        entry = {k: row[k] for k in FIELDS if row.get(k) not in (None, '', 0, -1)}
        entry['id'] = int(rid)
        entry['name'] = names.get(rid) or catalog.get(rid, {}).get('name') or f'Equipo {rid}'
        entry['desc'] = catalog.get(rid, {}).get('description', '')
        icon = catalog.get(rid, {}).get('icon') or item_rows.get(rid, {}).get('icon')
        if icon in have:
            icons[rid] = f'/assets/item-icons/{icon}.png'
        elif icon and (CUT / f'{icon}.png').exists():
            shutil.copyfile(CUT / f'{icon}.png', OUT / f'{icon}.png')
            icons[rid] = f'/assets/equipment/{icon}.png'
        if entry.get('suit_skills'):
            entry['suit_skill_names'] = [skills.get(s, s) for s in str(entry['suit_skills']).split('|')]
        for k in ('base1', 'base2', 'base3', 'base4', 'act', 'suit1', 'suit2', 'suit3'):
            for part in str(entry.get(k, '')).split('|'):
                if '#' in part:
                    attrs.add(part.split('#')[0])
        items[rid] = entry
    misc = (TABLES / 'misc.lua').read_text(encoding='utf-8-sig')
    open_level = int(re.search(r'treasure_open_level = \{\s*"treasure_open_level",\s*(\d+)', misc).group(1))
    # Frames and the Smithy art used by the screens.
    for name in ('bp_smithy_top', 'mergeArrow', 'bp_bar_bg', 'bp_bar_green', 'bp_bar_blue', 'icon_1', 'equip_star',
                 'partner_weapon', 'partner_cloth', 'partner_pants', 'partner_shoes', 'partner_treasure',
                 'partner_artifact', 'alert_icon', 'nav_btn_blue_mid', 'nav_btn_white_mid', 'white_btn_65_65',
                 'blue_btn_65_65', 'choose_equip_bg', 'equip_bg', 'red_btn_65_65'):
        if (CUT / f'{name}.png').exists():
            shutil.copyfile(CUT / f'{name}.png', OUT / f'{name}.png')
    jobs = {'zs': 1, 'fs': 2, 'yx': 3, 'ck': 4, 'ms': 5}
    names_attr = {a: tr.get(a.upper(), a) for a in sorted(attrs)}
    for key, job in jobs.items():
        names_attr[key] = 'DMG vs ' + tr.get(f'JOB_{job}', key)
    partners = json.loads((ROOT / 'data/partner.json').read_text())
    result = {'partner_jobs': {k: int(v['job']) for k, v in partners.items()},
              'partner_groups': {k: int(v['group']) for k, v in partners.items()},
              'items': items, 'icons': icons, 'treasure_open_level': open_level,
              'attr_names': names_attr, 'jobs': {str(j): tr.get(f'JOB_{j}', '') for j in range(1, 6)},
              'art': sorted(p.stem for p in OUT.glob('*.png'))}
    (ROOT / 'data/equipment.json').write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')))
    by_pos = {}
    for e in items.values():
        by_pos[e['pos']] = by_pos.get(e['pos'], 0) + 1
    print(f'{len(items)} equipment rows {by_pos}; {len(icons)} icons; {len(attrs)} attributes')


if __name__ == '__main__':
    main()
