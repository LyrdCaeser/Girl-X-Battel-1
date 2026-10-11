"""Excursion (ExploreWindow / ExploreAdventureWindow) art: map scene, building overlays, event scenes and UI sprites.
Output: web/assets/excursion/. Sources read-only; textures with power-of-two black padding are cropped."""
import shutil
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
TEX = Path.home() / 'Downloads/Decomp files/unity/Assets/hotres/textures/explore_web'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/excursion'; OUT.mkdir(parents=True, exist_ok=True)
for src in TEX.glob('*.png'):
    im = Image.open(src).convert('RGBA')
    box = im.getbbox()
    if src.stem.startswith('explore_scene') or src.stem == 'explore_main_scene':
        rgb = im.convert('RGB'); box = rgb.convert('L').point(lambda v: 255 if v > 8 else 0).getbbox()
        rgb.crop(box).save(OUT / f'{src.stem}.webp', 'WEBP', quality=88)
    else:
        im.crop(box).save(OUT / f'{src.stem}.png')
names = ['building_name_bg', 'can_level_up', 'btn_get_img_1', 'get_all_img', 'help_3', 'title_bg1', 'btn_back', 'divide_line1',
         'explore_help_btn', 'tips_btn', 'huawen_2', 'huawen_3', 'btn_level_up_new', 'label_bg', 'level_max', 'nav_bg',
         'explore_main_bg', 'com_btn_bg', 'icon_go', 'gift_bg_1', 'gift_bg_2', 'gift_open_bg', 'time_bg', 'icon_level_up',
         'btn_change_icon', 'btn_open_box', 'btn_setup', 'btn_formation', 'icon_203', 'icon_204', 'icon_205', 'icon_2', 'icon_1',
         'alert_icon', 'lock_icon', 'icon_lock']
names += [p.stem for p in CUT.glob('icon_bx_*.png')]
for n in names:
    if (CUT / f'{n}.png').exists():
        shutil.copyfile(CUT / f'{n}.png', OUT / f'{n}.png')
print(len(list(OUT.iterdir())), 'excursion assets')

# Building animations (ExploreWindow plays travel_main_01..07 at each building's effectNode, scale 1.5).
import json, re, sys
sys.path.insert(0, str(ROOT / 'tools'))
from spine36 import decode  # noqa: E402
SP = Path.home() / 'Downloads/Decomp files/unity/Assets/hotres/spine/explore_web'
for name in ('travel_main', 'travel_box_all', 'travel_fog'):
    src, out = SP / name, ROOT / f'web/assets/spine/{name}'
    if not src.is_dir() or (out / 'model.atlas').exists():
        continue
    out.mkdir(parents=True, exist_ok=True)
    skel = next(src.glob('*.skel.bytes')); stem = skel.name[:-len('.skel.bytes')]
    (out / 'model.json').write_text(json.dumps(decode(skel.read_bytes()), separators=(',', ':')))
    atlas = (src / f'{stem}.atlas.txt').read_text()
    for page in re.findall(r'^([^\r\n]+\.png)\r?$', atlas, re.M):
        p = Path(page).stem
        im = Image.open(src / f'{p}_RGB.png').convert('RGBA'); im.putalpha(Image.open(src / f'{p}_Alpha.png').convert('RGB').getchannel('R')); im.save(out / page)
    (out / 'model.atlas').write_text(atlas)
    print(name, sorted(json.loads((out / 'model.json').read_text())['animations']))
