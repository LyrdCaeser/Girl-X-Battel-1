"""Altar (Campus → Transfer, AltarWindow): backgrounds fort_bg_1_up/down, title, empty slot, preview and buttons.
Output web/assets/altar/. Sources in ~/Downloads are read only."""
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/altar'; OUT.mkdir(parents=True, exist_ok=True)
names = [p.stem for p in CUT.glob('altar_*.png') if 'ios_test' not in p.stem] + ['fort_bg_1_up', 'fort_bg_1_down', 'icon_none', 'btn_preview', 'help_2', 'shop',
         'nav_btn_blue_left', 'nav_btn_blue_right', 'nav_btn_white_left', 'nav_btn_white_right', 'white_btn70_70', 'blue_btn70_70', 'bg_tips', '9gongge23']
n = 0
for name in names:
    if (CUT / f'{name}.png').exists(): shutil.copy2(CUT / f'{name}.png', OUT / f'{name}.png'); n += 1
print(n, 'sprites')
