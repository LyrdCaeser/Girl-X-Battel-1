"""Manga pages (ComicWindow / ComicDetailWindow) from the user's folder ~/Downloads/Decompiled/Manga.

comic_text_en_en.get_url_h5 names each episode's page (manga_001_1_en_en.png …); the pages were served from the publisher's
site, so they are not in the client. Each page becomes web/assets/menu/manga/<comic id>.webp (720 px wide) plus a cover
<id>_c.webp cut from the top of the page (the client's cover_*.png were web-hosted too). The 62 "Birthday Manga - <girl>"
pages become birthday/<n>.webp. Output: web/assets/menu/manga/manga.json. Sources are read only."""
import json, re, sqlite3
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
SRC = Path.home() / 'Downloads/Decompiled/Manga'
DB = Path.home() / 'Downloads/Decomp files/data/en_en.db'
OUT = ROOT / 'web/assets/menu/manga'
(OUT / 'birthday').mkdir(parents=True, exist_ok=True)
Image.MAX_IMAGE_PIXELS = None


def save(src, dst, cover=None):
    if dst.exists() and (cover is None or cover.exists()): return
    im = Image.open(src).convert('RGB')
    if im.width != 720: im = im.resize((720, round(im.height * 720 / im.width)), Image.LANCZOS)
    im.save(dst, 'WEBP', quality=82, method=5)
    if cover:
        # the first panel sits below the "[EPISODE n] Title + logo" header (about y 185-545 on the 720-wide pages)
        top = 185 if im.height > 900 else 0
        c = im.crop((82, top, 638, min(im.height, top + 360))); c.thumbnail((320, 320)); c.save(cover, 'WEBP', quality=80)


files = {p.name.lower(): p for p in SRC.iterdir() if p.suffix.lower() in ('.png', '.jpg')}
def find(name):
    if name.lower() in files: return files[name.lower()]
    num = re.match(r'manga_(sp\.?\d+|\d+(?:\.\d+)?)', name.lower())
    if not num: return None
    key = num.group(1).lstrip('0')
    for n, p in files.items():
        m = re.match(r'manga_(sp\.?\d+|\d+(?:\.\d+)?)', n)
        if m and m.group(1).lstrip('0') == key: return p
    return None


db = sqlite3.connect(DB)
eps, missing = [], []
for cid, chapter, url in db.execute('select c.id, c.get_chapter, t.get_url_h5 from comic_en_en c left join comic_text_en_en t on t.id = c.id order by cast(c.id as integer)'):
    name = str(url or '').split('?')[0].rsplit('/', 1)[-1]
    p = find(name) if name else None
    if not p and re.match(r'Episode \d+$', chapter):  # typos in the client URL (menga_045, manga_1140, P26-en-finished)
        p = find('manga_%03d_en_en.png' % int(chapter.split()[1]))
    if p: save(p, OUT / f'{cid}.webp', OUT / f'{cid}_c.webp')
    else: missing.append((cid, chapter, name))
    eps.append([int(cid), chapter, bool(p)])
birthday = []
for i, p in enumerate(sorted(q for q in SRC.iterdir() if q.name.startswith('Birthday Manga - ')), 1):
    save(p, OUT / f'birthday/{i}.webp', OUT / f'birthday/{i}_c.webp')
    birthday.append([i, p.stem.replace('Birthday Manga - ', '')])
(OUT / 'manga.json').write_text(json.dumps({'episodes': eps, 'birthday': birthday}, ensure_ascii=False, separators=(',', ':')))
print(len(eps), 'episodes,', sum(e[2] for e in eps), 'with pages,', len(birthday), 'birthday; missing', missing)
