"""Create retina-density, gently sharpened WebP versions of existing GXB3 avatars.

The artwork is never redrawn or recolored. Original PNGs remain untouched; these
300%-scale WebP derivatives improve sampling on high-DPI phones and tablets.
Run: python clients/tools/generate_avatar_hd.py
"""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "web" / "assets" / "avatar-hd"
SCALE = 3


def render(source: Path, destination: Path) -> None:
    with Image.open(source) as original:
        image = original.convert("RGBA")
        target_size = (image.width * SCALE, image.height * SCALE)
        image = image.resize(target_size, Image.Resampling.LANCZOS)
        # A restrained unsharp mask compensates for the original 100px source
        # being enlarged; avoid halos and do not introduce generated details.
        image = image.filter(ImageFilter.UnsharpMask(radius=1.25, percent=115, threshold=3))
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, format="WEBP", quality=96, method=6, exact=True)


def main() -> int:
    jobs = 0
    sources = (
        (ROOT / "web/assets/original-ui/portraits", OUT / "portraits", ("partner_avatar_*.png",)),
        (ROOT / "web/assets/profile", OUT / "profile", ("partner_avatar_*.png", "head_*.png")),
    )
    for source_dir, out_dir, patterns in sources:
        for pattern in patterns:
            for source in sorted(source_dir.glob(pattern)):
                target = out_dir / (source.stem + ".webp")
                render(source, target)
                jobs += 1
    # Point every character portrait record at its retina-density counterpart.
    catalog_path = ROOT / "web/assets/avatars.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    changed = 0
    for entry in catalog.values():
        src = str(entry.get("src") or "")
        prefix = "/assets/original-ui/portraits/"
        if src.startswith(prefix) and src.endswith(".png"):
            name = Path(src).stem
            entry["src"] = f"/assets/avatar-hd/portraits/{name}.webp?v=1.1.2"
            changed += 1
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {jobs} HD avatar derivatives; updated {changed} avatar catalog entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
