"""Deep Sea Treasures (activity 329, ActivityPirate / ActivityPirateSwapWindow; captures docs/references/2026-09-30-user/05-06 and 07):
five lands (ACTIVITY_PIRATE_PLACE1-5), each with its own dropbox (activity_pirate_5_drop_awards), a Raid costs a Voyager Compass (misc
activity_pirate_explore_cost 410#1) and always pays 20 Pirate Coins (activity_pirate_drop_awards 411#20); a chest (activity_pirate_random_awards,
weight = its %) falls with the misc explore_is_drop chance and is guaranteed every 10 raids (explore_dropbox_guarantee 9); chests fill the
Collection Progress whose rewards are activity_pirate_mission. Output data/pirate.json + web/assets/pirate/."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/pirate'; OUT.mkdir(parents=True, exist_ok=True)
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def misc(key):
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', misc_text)
    return json.loads(m.group(1))


boxes = {}
for r in json.loads((ROOT / 'data/dropbox.json').read_text()).values(): boxes.setdefault(int(r['dropbox_id']), []).append(r)
lands = [{'id': int(r['id']), 'drop': [{'awards': x['item'], 'weight': int(x['weight'])} for x in boxes[int(r['dropbox_id'])] if int(x['weight']) > 0]}
         for r in sorted(read_table('activity_pirate_5_drop_awards').values(), key=lambda r: int(r['id']))]
chests = [{'id': int(r['id']), 'awards': r['awards'], 'weight': int(r['weight'])} for r in sorted(read_table('activity_pirate_random_awards').values(), key=lambda r: int(r['id']))]
collection = [{'id': int(r['id']), 'item': int(r['item_id']), 'need': int(r['complete_value']), 'awards': r['awards']} for r in sorted(read_table('activity_pirate_mission').values(), key=lambda r: int(r['id']))]
out = {'lands': lands, 'chests': chests, 'collection': collection,
       'misc': {k: misc(k) for k in ('activity_pirate_explore_cost', 'activity_pirate_explore_is_drop', 'activity_pirate_explore_dropbox_guarantee', 'activity_pirate_drop_awards',
                                     'activity_pirate_giftbag_free_awards', 'activity_pirate_shop_unlock_item')}}
db = sqlite3.connect(DEC / 'data/en_en.db')
out['text'] = dict(db.execute("select name, translation from translation_en_en where name like 'ACTIVITY_PIRATE%' and name not like 'ACTIVITY_PIRATE_PLOT%'"))
ids = {p.split('#')[0] for l in lands for d in l['drop'] for p in d['awards'].split('|')} | {p.split('#')[0] for c in chests for p in c['awards'].split('|')} | {str(c['item']) for c in collection} | {'410', '411'}
out['names'] = {str(i): n for i, n in db.execute('select id, name from item_text_en_en where id in (%s)' % ','.join(sorted(ids, key=int)))}
(ROOT / 'data/pirate.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
n = 0
for p in list(CUT.glob('activity_pirate_land*.png')) + list(CUT.glob('activity_pirate_icon_box*.png')) + list(CUT.glob('activity_pirate_progress_bg*.png')) + \
         [CUT / f'{x}.png' for x in ('activity_pirate_logo_en_en', 'activity_pirate_item_bg', 'activity_pirate_giftbag', 'activity_pirate_shop_logo_en_en', 'activity_pirate_shop_bg2', 'activity_pirate_shop_item_bg', 'activity_pirate_shop_nav1_1', 'activity_pirate_shop_nav1_2', 'activity_pirate_shop_nav2_1', 'activity_pirate_shop_nav2_2')]:
    if p.exists(): shutil.copy2(p, OUT / p.name); n += 1
print(len(lands), 'lands', len(chests), 'chests', len(collection), 'collection', n, 'sprites', out['misc'])
