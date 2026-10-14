"""Generate all GXB 3 ALPHA launcher icons from the user-supplied game cover.

Run with Pillow: python clients/tools/generate_icons.py
The source is the approved Goddess Battle 3 game image, embedded in the repo.
"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "icons" / "gxb3-icon.jpg"
if not SOURCE.is_file():
    raise SystemExit(f"Missing game icon source: {SOURCE}")

art = Image.open(SOURCE).convert("RGBA")
# The supplied source is already a square, centered crop of the uploaded cover.
art = ImageOps.fit(art, (1024, 1024), method=Image.Resampling.LANCZOS)

res = ROOT / "android" / "app" / "src" / "main" / "res"
for folder, size in (
    ("mipmap-mdpi", 48),
    ("mipmap-hdpi", 72),
    ("mipmap-xhdpi", 96),
    ("mipmap-xxhdpi", 144),
    ("mipmap-xxxhdpi", 192),
):
    dest = res / folder / "ic_launcher.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    art.resize((size, size), Image.Resampling.LANCZOS).save(dest, optimize=True)
    print(dest)

win = ROOT / "windows" / "gxb3.ico"
win.parent.mkdir(parents=True, exist_ok=True)
art.save(win, format="ICO", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
print(win)

ios = ROOT / "ios" / "AppIcon"
ios.mkdir(parents=True, exist_ok=True)
for name, size in (
    ("AppIcon60x60@2x.png", 120),
    ("AppIcon60x60@3x.png", 180),
    ("AppIcon76x76@2x.png", 152),
    ("AppIcon83.5x83.5@2x.png", 167),
    ("AppIcon1024.png", 1024),
):
    dest = ios / name
    art.resize((size, size), Image.Resampling.LANCZOS).convert("RGB").save(dest,optimize=True)
    print(dest)
