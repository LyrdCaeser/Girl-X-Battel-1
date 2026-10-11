"""Summon result window (summon_result_window.prefab + components/HeroIcon): the glowing band `summon_res`, the white
buttons and the HeroIcon parts (hero_frame halves, hero_group + img_group1-7 faction, star / star_red).
Output web/assets/summon-result/. Sources in ~/Downloads are read only."""
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/summon-result'; OUT.mkdir(parents=True, exist_ok=True)
names = ['summon_res', 'white_btn70_70', 'hero_frame', 'hero_group', 'star', 'star_red'] + [f'img_group{i}' for i in range(1, 8)]
for n in names: shutil.copy2(CUT / f'{n}.png', OUT / f'{n}.png')
print(len(names), 'sprites')
