"""Main story (StoryWindow with xyd.StoryType.MAIN): main_plot1-4 lines + main_plot_text, main_plot_list (stage → '#pre#post'
plots, memories, unlock cost), main_plot_fort / main_plot_episode + texts, sound table (music / ambient / voices).
Output data/story.json + web/assets/story/{bg,pic,cg,snd}/."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
HOT = DEC / 'unity/Assets/hotres'
TEX = HOT / 'textures'
OUT = ROOT / 'web/assets/story'
for d in ('bg', 'pic', 'cg', 'snd'):
    (OUT / d).mkdir(parents=True, exist_ok=True)
db = sqlite3.connect(DEC / 'data/en_en.db')
q = lambda sql: list(db.execute(sql))
text = {str(r[0]): (r[2] or '', r[3] or '') for r in q('select * from main_plot_text_en_en')}
rows = {}
for i in range(1, 5):
    rows.update(read_table(f'main_plot{i}'))
sound = {**read_table('sound1'), **read_table('sound2')}
used_snd = set()


def num(v, default=0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def snd(v):
    s = sound.get(str(v)) if v not in ('', None, 0, -1) else None
    if not s:
        return ''
    used_snd.add(s['res'])
    return s['res'].split('/')[-1]


lines = {}
for k, r in rows.items():
    name, dialog = text.get(k, ('', ''))
    dialog = dialog.split('|')[0]  # "male|female" variants: the first one
    lines[k] = {'bg': r.get('image_path') or '', 'pic': r.get('res_path') or '', 'xy': r.get('partner_picture_xy') or '',
                'sc': num(r.get('scale'), 1) or 1, 't': int(num(r.get('type'))), 'n': name, 'd': dialog,
                'v': snd(r.get('sound')), 'm': snd(r.get('music')), 'a': snd(r.get('ambient_sound')), 'j': int(num(r.get('jitter'))),
                'cg': r.get('cg_path') or '', 'x': int(num(r.get('next_id'))), 'mem': int(num(r.get('is_memory'))),
                'mv': r.get('position_move') or '', 'fx': (r.get('effect') or '').split('#')[0]}
lines = {k: {a: b for a, b in v.items() if b not in ('', 0, None) or a in ('t', 'x')} for k, v in lines.items()}
plist = sorted(read_table('main_plot_list').values(), key=lambda r: int(r['id']))
list_text = {str(r[0]): r[1] for r in q('select * from main_plot_list_text_en_en')}
fort_text = {str(r[0]): (r[1], r[2]) for r in q('select * from main_plot_fort_text_en_en')}
ep_text = {str(r[0]): r[1] for r in q('select * from main_plot_episode_text_en_en')}
out = {'lines': lines,
       'list': [{'id': int(r['id']), 'stage': int(num(r['stage_id'])), 'fort': int(r['plot_fort_id']), 'label': str(r['fort_id']),
                 'plots': [int(x) for x in str(r['plot_id']).split('#')[1:] if x] if str(r['plot_id']).count('#') else [],
                 'pre': int(num((str(r['plot_id']).split('#') + ['', '', ''])[1])), 'post': int(num((str(r['plot_id']).split('#') + ['', '', ''])[2])),
                 'memory': [int(x) for x in str(r['memory_plot_id']).split('|') if x.strip()], 'unlock': str(r['unlock'] or ''),
                 'former': int(num(r['unlock_plot_list_id'])), 'icon': r['chapter_icon'], 'name': list_text.get(str(r['id']), '')} for r in plist],
       'forts': [{'id': int(r['id']), 'episode': int(r['episode_id']), 'icon': r['chapter_icon'], 'name': fort_text.get(str(r['id']), ('', ''))[0],
                  'desc': fort_text.get(str(r['id']), ('', ''))[1]} for r in sorted(read_table('main_plot_fort').values(), key=lambda r: int(r['id']))],
       'episodes': [{'id': int(r['id']), 'img': r['episode_img'], 'first': int(r['first_plot_id']), 'name': ep_text.get(str(r['id']), '')}
                    for r in sorted(read_table('main_plot_episode').values(), key=lambda r: int(r['id']))],
       'text': dict(q("select name, translation from translation_en_en where name like 'PLOT_%' or name in ('LOCK_MEMORY','CHAPTER_TITLE','MAIN_PLOT_NEW')"))}
(ROOT / 'data/story.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))


def find(name):
    for p in TEX.rglob(name + '.png'):
        return p


n = 0
for key, folder in (('bg', 'bg'), ('pic', 'pic'), ('cg', 'cg')):
    for name in sorted({v[key] for v in lines.values() if v.get(key)}):
        dst = OUT / folder / f'{name}.webp'
        if dst.exists():
            continue
        src = find(name)
        if not src:
            continue
        im = Image.open(src)
        if key == 'pic':
            im = im.convert('RGBA'); im = im.resize((im.width // 2, im.height // 2))
        else:
            im = im.convert('RGB')
        im.save(dst, quality=80); n += 1
for res in sorted(used_snd):
    src = HOT / 'sounds' / (res + '.ogg')
    if src.exists():
        shutil.copy2(src, OUT / 'snd' / (res.split('/')[-1] + '.ogg')); n += 1
for name in {r['chapter_icon'] for r in plist} | {r['episode_img'] for r in read_table('main_plot_episode').values()} | \
        {r['chapter_icon'] for r in read_table('main_plot_fort').values()}:
    for base in (Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)', ):
        src = base / f'{name}.png'
        if src.exists():
            shutil.copy2(src, OUT / 'cg' / src.name); n += 1
print(len(lines), len(out['list']), len(out['forts']), n)
shutil.copy2(Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)/icon_208.png', OUT / 'cg/icon_208.png')  # Key of Memory
