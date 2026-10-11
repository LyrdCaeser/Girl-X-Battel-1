"""Extract original menu and currency sprites from the user's read-only Unity export."""
from pathlib import Path
import re
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ATLAS = Path('/Users/schroyle/Downloads/Decomp files/unity/Assets/hotres/atlases')
OUT = ROOT / 'web/assets'


def extract(atlas, names, dest):
    prefab = ATLAS / atlas / f'{atlas}.prefab'
    source = prefab.read_text(errors='ignore')
    rgb = Image.open(prefab.with_name(f'{atlas}_RGB.png')).convert('RGB')
    alpha = Image.open(prefab.with_name(f'{atlas}_Alpha.png')).convert('RGB')
    dest.mkdir(parents=True, exist_ok=True)
    found = set()
    for name, x, y, width, height in re.findall(r'- name: ([^\r\n]+)\s+x: (\d+)\s+y: (\d+)\s+width: (\d+)\s+height: (\d+)', source):
        if name not in names:
            continue
        x, y, width, height = map(int, (x, y, width, height))
        box = x, y, x + width, y + height
        img = rgb.crop(box)
        img.putalpha(alpha.crop(box).getchannel('R'))
        img.save(dest / f'{name}.png', optimize=True)
        found.add(name)
    missing = names - found
    if missing:
        raise ValueError(f'{atlas}: missing {sorted(missing)}')


if __name__ == '__main__':
    nav = {f'bottom_icon_{n}{suffix}_v3' for n in range(1, 7) for suffix in ('', '_o')}
    nav |= {'top_school_icon_v3', 'top_story_icon_v3', 'top_arena_icon_v3', 'icon_plus_v3'}
    extract('main_window_v3_1', nav, OUT / 'nav')
    extract('icon_image_web', {'icon_1', 'icon_1_small', 'icon_2', 'icon_2_small', 'icon_9', 'icon_12', 'icon_33', 'icon_36'}, OUT / 'currency')
    # The 32 px icon_*_small look blurry at the sizes the UI uses: serve the full icon (padded square) under that name.
    from PIL import Image
    for n in ('1', '2'):
        im = Image.open(OUT / 'currency' / f'icon_{n}.png').convert('RGBA'); side = max(im.size)
        sq = Image.new('RGBA', (side, side), (0, 0, 0, 0)); sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
        for p in OUT.rglob(f'icon_{n}_small.png'): sq.save(p)
