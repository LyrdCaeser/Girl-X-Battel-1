"""Date stories (DatesStoryWindow → StoryWindow with xyd.StoryType.PARTNER): partner_plot1-6 lines + partner_plot_text
(title, name, dialog), in the same line format as the main story (tools/extract_story.py) so Story.play() shows them.
Output data/partner_plot.json + missing art in web/assets/story/{bg,pic,cg,snd}/. Sources in ~/Downloads are read only."""
import json, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
HOT = DEC / 'unity/Assets/hotres'
TEX = HOT / 'textures'
OUT = ROOT / 'web/assets/story'
db = sqlite3.connect(DEC / 'data/en_en.db')
text = {str(r[0]): (r[1] or '', r[2] or '', r[3] or '') for r in db.execute('select id, title, name, dialog from partner_plot_text_en_en')}
rows = {}
for i in ('', '1', '2', '3', '4', '5', '6'):
    try: rows.update(read_table(f'partner_plot{i}'))
    except Exception: pass
sound = {**read_table('sound1'), **read_table('sound2')}
used = set()
def num(v, d=0):
    try: return float(v)
    except (TypeError, ValueError): return d
def snd(v):
    s = sound.get(str(v)) if v not in ('', None, 0, -1) else None
    if not s: return ''
    used.add(s['res']); return s['res'].split('/')[-1]
lines, titles = {}, {}
for k, r in rows.items():
    title, name, dialog = text.get(k, ('', '', ''))
    if title: titles[k] = title
    lines[k] = {'bg': r.get('image_path') or '', 'pic': r.get('res_path') or '', 'xy': r.get('partner_picture_xy') or '',
                'sc': num(r.get('scale'), 1) or 1, 't': int(num(r.get('type'))), 'n': name, 'd': dialog.split('|')[0],
                'v': snd(r.get('sound')), 'm': snd(r.get('music')), 'a': snd(r.get('ambient_sound')), 'j': int(num(r.get('jitter'))),
                'cg': r.get('cg_path') or '', 'x': int(num(r.get('next_id'))), 'mv': r.get('position_move') or '', 'fx': (r.get('effect') or '').split('#')[0]}
lines = {k: {a: b for a, b in v.items() if b not in ('', 0, None) or a in ('t', 'x')} for k, v in lines.items()}
(ROOT / 'data/partner_plot.json').write_text(json.dumps({'lines': lines, 'titles': titles}, ensure_ascii=False, separators=(',', ':')))
def find(name):
    for p in TEX.rglob(name + '.png'): return p
n = 0
for key in ('bg', 'pic', 'cg'):
    for name in sorted({v[key] for v in lines.values() if v.get(key)}):
        dst = OUT / key / f'{name}.webp'
        if dst.exists(): continue
        src = find(name)
        if not src: continue
        im = Image.open(src)
        im = im.convert('RGBA').resize((im.width // 2, im.height // 2)) if key == 'pic' else im.convert('RGB')
        im.save(dst, quality=80); n += 1
for res in sorted(used):
    src = HOT / 'sounds' / (res + '.ogg'); dst = OUT / 'snd' / (res.split('/')[-1] + '.ogg')
    if src.exists() and not dst.exists(): shutil.copy2(src, dst); n += 1
print(len(lines), 'lines,', len(titles), 'titles,', n, 'new files')
