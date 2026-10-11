"""Use the downloaded H5 atlas to restore the six original bottom icons.

The downloaded PNG is the Unity atlas cropped to its nontransparent bounds.
The original prefab supplies sprite names and rectangles in the uncut atlas.
"""
from pathlib import Path
import re
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('/Users/schroyle/Downloads/Decompiled/Sprites (atlases, uncut sheets)/main_window_h5.png')
UNITY = Path('/Users/schroyle/Downloads/Decomp files/unity/Assets/hotres/atlases/main_window_h5')
DEST = ROOT / 'web/assets/nav-reference'


def main():
    sheet = Image.open(SOURCE).convert('RGBA')
    rgb = Image.open(UNITY / 'main_window_h5_RGB.png').convert('RGB')
    alpha = Image.open(UNITY / 'main_window_h5_Alpha.png').convert('RGB')
    rgb.putalpha(alpha.getchannel('R'))
    bounds = rgb.getbbox()
    if sheet.size != rgb.crop(bounds).size or ImageChops.difference(sheet, rgb.crop(bounds)).getbbox():
        raise ValueError('The downloaded atlas differs from the original Unity atlas')
    prefab = (UNITY / 'main_window_h5.prefab').read_text(errors='ignore')
    sprites = {name: tuple(map(int, (x, y, width, height)))
               for name, x, y, width, height in re.findall(
                   r'- name: ([^\r\n]+)\s+x: (\d+)\s+y: (\d+)\s+width: (\d+)\s+height: (\d+)', prefab)}
    DEST.mkdir(parents=True, exist_ok=True)
    for index in range(1, 7):
        x, y, width, height = sprites[f'bottom_icon_{index}_v3_h5']
        icon = sheet.crop((x - bounds[0], y - bounds[1], x + width - bounds[0], y + height - bounds[1]))
        icon.save(DEST / f'bottom-{index}.png', optimize=True)


if __name__ == '__main__':
    main()
