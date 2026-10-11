"""Girl sheet (PartnerDetailWindow, prefab partner_detail_window) sprites for the full-screen layout:
tab buttons nav_btn_{blue,white}_{left,mid,right} (sliced 10/10/10/25), panel frame 9gongge20, labels 9gongge16,
cost bar 9gongge22, divider partner_divide_line_1, lock / unlock / zoom / comment buttons, bubble, power and job icons,
level-up arrow and grade-up button, side buttons (Anima Gear, unique skills), gear slot art and buttons.
Output web/assets/detail/sheet/. Sources in ~/Downloads are read only."""
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/detail/sheet'; OUT.mkdir(parents=True, exist_ok=True)
names = [f'nav_btn_{c}_{s}' for c in ('blue', 'white', 'grey') for s in ('left', 'mid', 'right')] + \
        ['partner_lock_btn', 'partner_unlock_btn', 'partner_zoom_btn', 'btn_partner_station', '9gongge20', '9gongge16', '9gongge22',
         'main_bubble', 'main_bubble_arrow', 'partner_divide_line_1', 'force_icon', 'attr_exclamation', 'partner_detail_arrow_up',
         'partner_max_lev_bg', 'shengjie_btn', 'awake_lock', 'soul_equip_icon_rk_lszb', 'advanced_skill', 'partner_cv_bg',
         'white_btn70_70', 'red_btn_65_65', 'blue_btn_65_65', 'item_icon_bg01', 'icon_add', 'lock_icon', 'equip_bg',
         'partner_weapon', 'partner_cloth', 'partner_pants', 'partner_shoes', 'partner_treasure', 'partner_artifact', 'alert_icon',
         'partner_grade_icon', 'partner_grade_icon_bg', 'icon_1', 'icon_9', 'icon_10',
         # common window (9gongge21: blue title bar, sliced 25/25/60/20), close / help, Limit-Break (potentiality_component)
         '9gongge21', '9gongge23', '9gongge24', 'close_btn_2', 'help_2', 'blue_btn70_70', 'partner_detail_btn_zjht', 'potentiality_bg01', 'potentiality_bg02', 'potentiality_bg03',
         'potentiality_divide_line', 'potentiality_arrow', 'potentiality_lock', 'potentiality_empty', 'potentiality_ten_star', 'potentiality_star_icon',
         'partner_potential_bg_big', 'partner_potential_dark_big', 'partner_potential_light_big', 'grade_up_unlock_skill_bg', 'partner_divide_line_2'] + \
        [f'job_icon{i}' for i in range(1, 6)] + [f'img_group{i}' for i in range(1, 8)] + [f'love_point_icon{i}' for i in range(1, 7)]
n = 0
for name in names:
    src = CUT / f'{name}.png'
    if src.exists():
        shutil.copy2(src, OUT / src.name); n += 1
    else:
        print('missing', name)
print(n, 'sprites')
