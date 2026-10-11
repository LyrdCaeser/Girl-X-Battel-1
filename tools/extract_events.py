"""Extract the Events hub (ActivityWindow) data and art from the archived client.

Sources (read-only):
  ~/Downloads/Decomp files/lua/data/tables/activity.lua      activity list, icons, tabs, rank
  ~/Downloads/Decomp files/data/data.db + en_en.db           reward tables and English text
  ~/Downloads/Decomp files/unity/Assets/hotres/textures      check-in textures
  ~/Downloads/Decompiled/Sprites (atlases, cut)              title icons, tiles, item icons
Output: data/events.json and web/assets/events/*.png
"""
from __future__ import annotations
import json, re, shutil, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECOMP = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
TEX = DECOMP / 'unity/Assets/hotres/textures'
OUT = ROOT / 'web/assets/events'


def activity_rows():
    text = (DECOMP / 'lua/data/tables/activity.lua').read_text(encoding='utf-8-sig')
    head, body = text.split('table.rows', 1)
    keys = {k: int(v) for k, v in re.findall(r'\t(\w+) = (\d+),?\n', head)}
    rows = {}
    for rid, block in re.findall(r'\["(\d+)"\] = \{(.*?)\n\t\}', body, re.S):
        vals = [v.strip().strip('"') for v in re.split(r',\n', block.strip())]
        rows[int(rid)] = {k: (vals[i - 1] if i - 1 < len(vals) else '') for k, i in keys.items()}
    return rows


def table(db, name):
    cur = db.execute(f'select * from {name}')
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur]


def copy(src: Path, name: str):
    if src.exists():
        shutil.copyfile(src, OUT / f'{name}.png')
        return True
    return False


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = sqlite3.connect(DECOMP / 'data/data.db')
    en = sqlite3.connect(DECOMP / 'data/en_en.db')
    text = {r['id']: r for r in table(en, 'activity_text_en_en')}
    tr = dict(en.execute('select name, translation from translation_en_en'))

    activities = []
    for aid, row in sorted(activity_rows().items()):
        icon = row['icon'].split('|')[0].removesuffix('_png')
        if not icon or not copy(CUT / f'{icon}.png', f'icon_{icon}'):
            continue
        t = text.get(str(aid), {})
        activities.append({'id': aid, 'icon': icon, 'title': (t.get('title') or '').replace('\\n', '\n'),
                           'desc': t.get('desc') or '', 'type1': int(row['type1'] or 0),
                           'type2': int(row['type2'] or 0), 'rank': int(row['rank'] or 0)})

    copy(TEX / 'partner_picture_web/partner_picture_11001.png', 'partner_picture_11001')
    for name in ('activity_icon_0_middle', 'activity_icon_1_middle', 'activity_bg03', 'activity_bg_new',
                 'check_in_pop_up_check_in_location', 'person_icon_red_point', 'fort_bg_1_up', 'activity_bg08',
                 'nav_btn_blue_left', 'nav_btn_blue_mid', 'nav_btn_blue_right', 'nav_btn_white_left',
                 'nav_btn_white_mid', 'nav_btn_white_right', 'alert_icon'):
        copy(CUT / f'{name}.png', name)
    for f in (TEX / 'activity_web/check_in_pop_up').glob('*.png'):
        shutil.copyfile(f, OUT / f.name)
    for day in range(1, 8):
        for s in (1, 2):
            copy(CUT / f'day_{day}_{s}.png', f'day_{day}_{s}')
    copy(CUT / 'activity_sevenday_text01_en_en.png', 'activity_sevenday_text01_en_en')

    login = [{'id': int(r['id']), 'award': r['award'], 'double': r['double_award'] == '1', 'special': r['special'] == '1'}
             for r in table(data, 'activity_login')]
    login.sort(key=lambda r: r['id'])
    sevenday = sorted(({'day': int(r['days']), 'award': r['award']} for r in table(data, 'activity_sevendays_awards')),
                      key=lambda r: r['day'])

    # Item icons referenced by rewards that the Bag extraction did not already include.
    catalog = json.loads((ROOT / 'web/assets/items-catalog.json').read_text())
    have = {p.stem for p in (ROOT / 'web/assets/item-icons').glob('*.png')}
    icons = {}
    for award in [r['award'] for r in login] + [r['award'] for r in sevenday]:
        for part in award.split('|'):
            iid = part.split('#')[0]
            icon = catalog.get(iid, {}).get('icon')
            if not icon:
                continue
            if icon in have:
                icons[iid] = f'/assets/item-icons/{icon}.png'
            elif copy(CUT / f'{icon}.png', f'item_{icon}'):
                icons[iid] = f'/assets/events/item_{icon}.png'

    misc = (DECOMP / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig')
    exclude = int(re.search(r'login_loop_exclude = \{\s*"login_loop_exclude",\s*(\d+)', misc).group(1))
    result = {'activities': activities, 'login': login, 'login_loop_exclude': exclude, 'sevenday': sevenday,
              'item_icons': icons, 'item_names': {k: catalog[k]['name'] for k in icons if k in catalog},
              'text': {k: tr.get(k, '') for k in ('CHECKIN_POPUP_TITLE', 'CHECKIN_POPUP_TEXT1', 'CHECKIN_POPUP_TEXT2', 'GET2',
                                                   'ACTIVITY_NAV_TEXT_2_1', 'ACTIVITY_NAV_TEXT_2_3')}}
    (ROOT / 'data/events.json').write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')))
    print(f'{len(activities)} activities, {len(login)} login days, {len(icons)} reward icons')


if __name__ == '__main__':
    main()
