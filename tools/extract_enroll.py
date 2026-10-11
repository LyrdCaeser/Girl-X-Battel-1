"""Enroll (ProphetWindow) art + point-event banners (Capsule Points, Enroll Exam, Slot Points)."""
import shutil, sys
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from extract_visuals import spine  # noqa: E402
HOT = Path.home() / 'Downloads/Decomp files/unity/Assets/hotres'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
ENROLL = ROOT / 'web/assets/enroll'; ENROLL.mkdir(parents=True, exist_ok=True)
EVENTS = ROOT / 'web/assets/events'
for p in CUT.glob('prophet_*.png'):
    if 'giftbag' not in p.name:
        shutil.copyfile(p, ENROLL / p.name)
for n in ('icon_20', 'icon_19', 'checkbox_bg', 'checkbox_tick', 'help_2', 'btn_help'):
    if (CUT / f'{n}.png').exists():
        shutil.copyfile(CUT / f'{n}.png', ENROLL / f'{n}.png')
for n in ('prophet_bg03', 'prophet_icon07'):
    im = Image.open(HOT / f'textures/scenes_web/{n}.png').convert('RGBA')
    box = im.getbbox()
    im.crop(box).save(ENROLL / f'{n}.png')
for name in ('caopi', 'fx_yinzhang'):
    spine(HOT / f'spine/prophet_web/summon/{name}', ROOT / f'web/assets/spine/{name}')
# Event banners (textures + cut sprites), English text art.
banners = {'prophet_summon_giftbag_bg01': HOT / 'textures/activity_web/prophet_summon_giftbag_web/prophet_summon_giftbag_bg01.png',
           'prophet_summon_giftbag_bg02': HOT / 'textures/activity_web/prophet_summon_giftbag_web/prophet_summon_giftbag_bg02.png',
           'summon_giftbag_bg01': HOT / 'textures/activity_web/summon_giftbag/summon_giftbag_bg01.png',
           'summon_giftbag_bg02': HOT / 'textures/activity_web/summon_giftbag/summon_giftbag_bg02.png',
           'summon_giftbag_text01_en_en': HOT / 'textures/activity_text_web/summon_giftbag_text01_en_en.png',
           'prophet_summon_giftbag_text01_en_en': CUT / 'prophet_summon_giftbag_text01_en_en.png',
           'wishing_pool_giftbag_bg01': CUT / 'wishing_pool_giftbag_bg01.png',
           'wishing_pool_giftbag_bg02': CUT / 'wishing_pool_giftbag_bg02.png',
           'wishing_pool_giftbag_text01_en_en': CUT / 'wishing_pool_giftbag_text01_en_en.png'}
for n in ('progress_bar_bg', 'progress_bar_thumb', 'activity_bar_bg', 'activity_bar_thumb', 'item_get_mark', 'award_get_icon', 'get_icon', 'white_btn_65_65', 'activity_tick'):
    if (CUT / f'{n}.png').exists():
        banners[n] = CUT / f'{n}.png'
for n, src in banners.items():
    shutil.copyfile(src, EVENTS / f'{n}.png')
print(len(list(ENROLL.glob('*.png'))), 'enroll sprites;', len(banners), 'banner files')
