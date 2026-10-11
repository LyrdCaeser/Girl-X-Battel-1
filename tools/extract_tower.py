"""Import Tests/Tower data and already-cut original sprites from the supplied exports."""
from pathlib import Path
import json
import shutil
from extract_daily_quiz import rows

ROOT = Path(__file__).resolve().parents[1]
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
SCENES = Path.home() / 'Downloads/Decomp files/unity/Assets/hotres/textures/scenes_web'
SPRITES = ('tower_icon02', 'tower_icon03', 'tower_icon04', 'tower_icon08',
           'tower_smallbg00', 'tower_smallbg01', 'tower_detailbg',
           'tower_awards_list_bg', 'towerBox_close', 'towerBox_open',
           'tower_text_en_en', 'icon_13')


def main():
    tower = rows('tower', ['id', 'battle_id', 'reward', 'power', 'map', 'data_record'])
    if len(tower) < 100 or '1' not in tower:
        raise ValueError('Tower table incomplete')
    (ROOT / 'data/tower.json').write_text(json.dumps(tower, ensure_ascii=False) + '\n')
    destination = ROOT / 'web/assets/tower'
    destination.mkdir(parents=True, exist_ok=True)
    for name in SPRITES:
        shutil.copyfile(CUT / f'{name}.png', destination / f'{name}.png')
    for number in range(3):
        name = f'tower_bg0{number}'
        shutil.copyfile(SCENES / f'{name}.png', destination / f'{name}.png')


if __name__ == '__main__':
    main()
