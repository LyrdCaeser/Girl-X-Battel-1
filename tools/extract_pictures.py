"""Recover full illustrations, including bundled local_tex girls; preserve skin assets."""
import json, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = Path.home() / 'Downloads/Decomp files/unity/Assets/hotres/textures/partner_picture_web'
LOCAL = SRC.parent / 'local_tex'
OUT = ROOT / 'web/assets/pictures'
OUT.mkdir(parents=True, exist_ok=True)
ids = {int(f.stem) for f in OUT.glob('*.webp') if f.stem.isdigit()}
known = set(json.loads((ROOT / 'data/partner_pictures.json').read_text()))
for f in sorted(SRC.glob('partner_picture_*.png')) + sorted(LOCAL.glob('partner_picture_*.png')):
    m = re.fullmatch(r'partner_picture_(\d+)\.png', f.name)
    if not m:
        continue
    if f.parent == LOCAL and m.group(1) not in known:
        continue  # Bundled story-only images are not necessarily playable girls.
    dst = OUT / f'{m.group(1)}.webp'
    if not dst.exists():
        Image.open(f).convert('RGBA').save(dst, 'WEBP', quality=86, method=4)
    ids.add(int(m.group(1)))
(ROOT / 'data/pictures.json').write_text(json.dumps(sorted(ids)))
print(len(ids), 'pictures')

# Native illustrations have different transparent margins. Graduate aligns the visible bounds.
layouts = {}
for f in sorted(OUT.glob('*.webp')):
    if not f.stem.isdigit():
        continue
    with Image.open(f) as im:
        bounds = im.getchannel('A').getbbox() if im.mode == 'RGBA' else (0, 0, im.width, im.height)
        if bounds:
            layouts[f.stem] = {'width': im.width, 'height': im.height, 'bounds': list(bounds)}
encoded = json.dumps(layouts, separators=(',', ':'))
(ROOT / 'web/assets/picture-layouts.json').write_text(encoded)
app = ROOT / 'web/app.js'
source = app.read_text()
source = re.sub(r'/\* PICTURE_LAYOUTS_START \*/.*?/\* PICTURE_LAYOUTS_END \*/',
                '/* PICTURE_LAYOUTS_START */\nconst pictureLayouts=' + encoded + ';\n/* PICTURE_LAYOUTS_END */',
                source, flags=re.S)
app.write_text(source)
