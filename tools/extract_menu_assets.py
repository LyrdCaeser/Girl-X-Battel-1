"""Extract menu artwork from the local read-only Unity export."""
from pathlib import Path
import re
from PIL import Image

from extract_navigation_assets import ATLAS, OUT, extract

ROOT = ATLAS.parent / 'textures'
DEST = OUT / 'menus'
DEST.mkdir(parents=True, exist_ok=True)

scenes = {
    'guild-territory': 'scenes_web/guild_territory_bg01.png',
    'guild-building': 'guild_web/guild_territory_bg02.png',
    'settings': 'scenes_web/setting_up_bg.png',
    'shop-map': 'scenes_web/shop_map_bg.png',
    'date': 'scenes_web/date_main_bg.png',
    'dorm': 'scenes_web/house_basic01_bg01.png',
    'arena': 'scenes_web/arena_scene.png',
    'arena-team': 'scenes_web/arena_team_scene.png',
    'arena-cross': 'scenes_web/arena_as_bg1.png',
    'sanctuary': 'scenes_web/trial_bg01.png',
    'echoes': 'scenes_web/time_cloister_bg_1.png',
    'prophet': 'scenes_web/prophet_bg03.png',
    'altar': 'scenes_web/starry_altar_bg.png',
    'collection': 'scenes_web/collection_scene.png',
    'outfit-showcase': 'scenes_web/dress_show_entrance_bg.png',
}
for name, relative in scenes.items():
    image = Image.open(ROOT / relative)
    # Unity scene textures have black unused columns outside the portrait art.
    bounds = image.convert('RGB').getbbox()
    if bounds and bounds[2] - bounds[0] > image.width // 3:
        image = image.crop(bounds)
    image.save(DEST / f'{name}.png', optimize=True)

groups = {
    'guild_territory_web': {
        'guild_territory_icon02', 'guild_territory_icon05',
        'guild_territory_checkin', 'guild_territory_shop_mask',
    },
    'guild_web': {'guild_bg03', 'guild_bg06', 'guild_bg11', 'guild_new_btn_icon'},
    'guild_shop_web': {'guild_shop_en_en', 'guild_shop_icon_exp'},
    'gamble_web': {'gb_normal_icon_3', 'gb_senior_icon_3', 'gb_normal_records'},
    'prophet_web': {'prophet_icon_group1', 'prophet_icon_group2', 'prophet_icon_group3', 'prophet_icon_group4', 'prophet_icon_group5'},
    'daily_quiz_web': {'bg_banner', 'quiz_hero', 'quiz_mana', 'quiz_exp'},
    'trial_web': {'new_trial_boss', 'new_trial_boss2', 'new_trial_nav_icon1', 'new_trial_nav_icon2'},
    'time_cloister_web': {'time_cloister_turntable', 'time_cloister_card_1', 'time_cloister_btn_record'},
    'tower_web': {'tower_icon03', 'towerBox_close', 'towerBox_open'},
    'dates_web': {'dates_icon46', 'dates_icon23', 'dates_text01_en_en'},
    'house_web': {'house_icon_8', 'house_group_img_1', 'house_group_img_2'},
    'shop': {'shop_cafe', 'shop_skin', 'shop_market', 'shop_exchange', 'shop_artifact', 'shop_unopen'},
}
for atlas, names in groups.items():
    extract(atlas, names, DEST)

for directory, atlas, names in (
    ('commonui_seam', 'CommonUI_seam', {'setting_icon_memories', 'setting_icon_achieve'}),
    ('commonui', 'CommonUI', {'setting_icon_notice', 'setting_icon_help', 'setting_icon_enhance', 'setting_icon_comic', 'setting_icon_background'}),
):
    prefab = ATLAS / directory / f'{atlas}.prefab'
    source = prefab.read_text(errors='ignore')
    rgb = Image.open(prefab.with_name(f'{atlas}_RGB.png')).convert('RGB')
    alpha = Image.open(prefab.with_name(f'{atlas}_Alpha.png')).convert('RGB')
    found = set()
    for name, x, y, width, height in re.findall(r'- name: ([^\r\n]+)\s+x: (\d+)\s+y: (\d+)\s+width: (\d+)\s+height: (\d+)', source):
        if name not in names:
            continue
        x, y, width, height = map(int, (x, y, width, height))
        box = x, y, x + width, y + height
        image = rgb.crop(box)
        image.putalpha(alpha.crop(box).getchannel('R'))
        image.save(DEST / f'{name}.png', optimize=True)
        found.add(name)
    if names - found:
        raise ValueError(f'{atlas}: missing {sorted(names - found)}')
