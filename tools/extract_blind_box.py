"""Blind Box Frenzy (activity 338, ActivityBlindBox / ActivityBlindBoxSelectWindow; promo image and the user's description in
docs/references/2026-09-30-user/01): per round one Grand Reward (tier 1) and four tiers to choose from (3, 3, 1, 1 picks,
misc activity_blind_box_select_num); every reward has `num` copies and a `weight`. Output data/blind_box.json + web/assets/blind-box/."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/blind-box'; OUT.mkdir(parents=True, exist_ok=True)
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def misc(key):
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', misc_text)
    return json.loads(m.group(1))


rows = [{'id': int(r['id']), 'round': int(r['cycle']), 'tier': int(r['type']), 'awards': r['awards'], 'num': int(r['num']), 'weight': int(r['weight'])}
        for r in sorted(read_table('activity_blind_box_awards').values(), key=lambda r: int(r['id']))]
db = sqlite3.connect(DEC / 'data/en_en.db')
text = dict(db.execute("select name, translation from translation_en_en where name like 'ACTIVITY_BLIND_BOX%' and name not like '%GIFTBAG%'"))
ids = {p.split('#')[0] for r in rows for p in r['awards'].split('|')} | {'438'}
names = {str(i): n for i, n in db.execute('select id, name from item_text_en_en where id in (%s)' % ','.join(sorted(ids, key=int)))}
out = {'rows': rows, 'select_num': [int(x) for x in str(misc('activity_blind_box_select_num')).split('|')], 'cost': misc('activity_blind_box_cost'),
       'guarantee': int(misc('activity_blind_box_guarantee_time')), 'rounds': max(r['round'] for r in rows), 'text': text, 'names': names}
(ROOT / 'data/blind_box.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
n = 0
for name in ['activity_blind_box', 'activity_blind_box_bg', 'activity_blind_box_bg_2', 'activity_blind_box_bg_title_en_en', 'activity_blind_box_btn_add', 'activity_blind_box_btn_get1',
             'activity_blind_box_btn_get10', 'activity_blind_box_detail_bg', 'activity_blind_box_detail_item', 'activity_blind_box_next', 'activity_blind_box_selected',
             'activity_blind_box_select_ok', 'activity_blind_box_select_text_en_en', 'activity_blind_box_award_text_en_en'] + \
            [f'activity_blind_box_{k}_{i}' for k in ('add_card', 'btn_exchange', 'card_mask') for i in range(1, 6)]:
    p = CUT / f'{name}.png'
    if p.exists(): shutil.copy2(p, OUT / p.name); n += 1
    else: print('missing', name)
print(len(rows), 'rows', out['select_num'], out['guarantee'], out['rounds'], 'rounds', n, 'sprites')
