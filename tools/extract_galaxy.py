"""Galaxy Voyage (models/GalaxyTrip.lua, GALAXY_TRIP_HELP01-03): Systems (galaxy_trip_map), unlock requirements, events
and event types, Voyage Teams, Ruler weakening buffs, tasks, Voyager Passport, stores, ranking brackets, misc galaxy_trip_*,
texts and window art. Output data/galaxy.json + web/assets/galaxy/."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
TEX = DEC / 'unity/Assets/hotres/textures'
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def misc(key):
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', misc_text)
    return json.loads(m.group(1))


def rows(n):
    return sorted(read_table(n).values(), key=lambda r: int(r['id']))


db = sqlite3.connect(DEC / 'data/en_en.db')
q = lambda sql: list(db.execute(sql))
two = lambda t: {str(r[0]): r[1] for r in q(f'select * from {t}')}
out = {'misc': {k: misc(k) for k in ('galaxy_trip_challenge', 'galaxy_trip_explore_place', 'galaxy_trip_robber_time', 'galaxy_trip_open_time',
                                     'galaxy_trip_open_num', 'galaxy_trip_time', 'galaxy_trip_enemy_weaken', 'galaxy_trip_black_hole_open',
                                     'galaxy_trip_boss_max_level', 'galaxy_trip_stop_time_limit')},
       'maps': rows('galaxy_trip_map'), 'unlock': rows('galaxy_trip_map_unlock'), 'events': {str(r['id']): r for r in rows('galaxy_trip_event')},
       'types': {str(r['id']): r for r in rows('galaxy_trip_event_type')}, 'teams': rows('galaxy_trip_team'), 'buff_show': rows('galaxy_trip_buff_show'),
       'missions': rows('galaxy_trip_mission'), 'pass': rows('galaxy_trip_battlepass'), 'store1': rows('galaxy_trip_store1'),
       'store2': rows('galaxy_trip_store2'), 'rank': rows('galaxy_trip_rank'),
       'map_text': two('galaxy_trip_map_text_en_en'), 'unlock_text': two('galaxy_trip_map_unlock_text_en_en'),
       'type_text': two('galaxy_trip_event_type_text_en_en'), 'team_text': two('galaxy_trip_team_text_en_en'),
       'buff_text': two('galaxy_trip_buff_show_text_en_en'), 'mission_text': two('galaxy_trip_mission_text_en_en'),
       'store_text': two('galaxy_trip_store_text_en_en'),
       'items': {str(r[0]): r[1] for r in q('select id, name from item_text_en_en where id in (356,358,359,360,396,397,398,402)')},
       'text': dict(q("select name, translation from translation_en_en where name like 'GALAXY_TRIP%'"))}
(ROOT / 'data/galaxy.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))

OUT = ROOT / 'web/assets/galaxy'; OUT.mkdir(parents=True, exist_ok=True)
n = 0
for p in [*CUT.glob('galaxy_trip_*.png'), *CUT.glob('activity_galaxy_trip_mission_*.png'),
          *[CUT / f'icon_{i}.png' for i in (356, 358, 359, 360, 396, 397, 398, 402)]]:
    if p.exists() and not re.search(r'_(de_de|fr_fr|ja_jp|ko_kr|zh_tw)\.png$', p.name):
        shutil.copy2(p, OUT / p.name); n += 1
for src in [*TEX.glob('scenes_web/galaxy_trip_*.png'), *TEX.glob('common_ui_texture_web/galaxy_trip/*.png')]:
    im = Image.open(src).convert('RGB') if 'map' in src.name or 'banner' in src.name else Image.open(src)
    if 'galaxy_trip_map' in src.name:  # 1024² textures with black side bands: keep the painted column
        box = im.point(lambda v: 255 if v > 6 else 0).convert('L').getbbox()
        im = im.crop(box)
    im.save(OUT / (src.stem + '.webp'), quality=84); n += 1
print(len(out['maps']), len(out['events']), len(out['types']), len(out['teams']), len(out['missions']), n)
