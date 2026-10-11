"""Outfits (models/Dress.lua, components/SenpaiModel.lua, DressMainWindow / DressItemUpWindow / DressSummonWindow):
senpai_dress (pieces), senpai_dress_item (piece per star: Courage/Charisma/Knowledge, upgrade costs, shards), styles
(icon, Spine resource, slot image + offset/scale/rotation, collide), slots (defaults), groups (sets and their special
bonuses by total stars), skills / skill buffs + texts, collide table, summon_dress + misc dress_gacha_*.
Assets: every Senpai Spine (senpai_dress_web, 337 skeletons), slot images (senpai_slot_web), piece icons, frames,
buff icons and window art. Output data/dress.json + web/assets/dress/."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
from extract_slots_dealers import decode
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
HOT = DEC / 'unity/Assets/hotres'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/dress'
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def misc(key):
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', misc_text)
    return json.loads(m.group(1))


rows = lambda n: sorted(read_table(n).values(), key=lambda r: int(r['id']))
db = sqlite3.connect(DEC / 'data/en_en.db')
q = lambda sql: list(db.execute(sql))
items = rows('senpai_dress_item')
names = {str(r[0]): r[1] for r in q('select id, name from item_text_en_en where id between 3100000 and 3999999')}
out = {'misc': {k: misc(k) for k in ('dress_gacha_dropbox1', 'dress_gacha_dropbox2', 'dress_gacha_dropbox4', 'dress_gacha_dropbox5', 'dress_gacha_max_drop',
                                     'dress_gacha_weight_total', 'dress_gacha_weight_get1', 'dress_gacha_weight_add', 'dress_gacha_cost1', 'dress_gacha_cost2',
                                     'dress_common_fragment_qlt_item_ids', 'dress_gacha_free1', 'dress_gacha_free2', 'dress_gacha_show')},
       'dress': rows('senpai_dress'), 'items': items, 'styles': rows('senpai_dress_style'), 'slots': rows('senpai_dress_slot'),
       'groups': rows('senpai_dress_group'), 'skills': rows('senpai_dress_skill'), 'buffs': rows('senpai_dress_skill_buff'),
       'collide': {str(r['id']): str(r['collide']) for r in rows('senpai_dress_collide')}, 'summon': rows('summon_dress'),
       'names': {str(r['id']): names.get(str(r['id']), '') for r in items},
       'shard_names': {k: v for k, v in names.items() if k.startswith('32') or k.startswith('39999')},
       'group_names': {str(r[0]): r[1] for r in q('select * from senpai_dress_group_text_en_en')},
       'skill_text': {str(r[0]): r[1] for r in q('select * from senpai_dress_skill_text_en_en')},
       'buff_text': {str(r[0]): r[1] for r in q('select id, desc from senpai_dress_skill_buff_text_en_en')},
       'item_names': {str(r[0]): r[1] for r in q('select id, name from item_text_en_en where id in (258,259,260,261)')}}
(ROOT / 'data/dress.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))

n = 0
# Spines: one folder per skeleton (a senpai_dress_web folder can hold several).
SPD = HOT / 'spine/senpai_dress_web'
for skel in SPD.rglob('*.skel.bytes'):
    name = skel.name[:-len('.skel.bytes')]
    dst = OUT / 'spine' / name
    if (dst / 'model.json').exists():
        continue
    dst.mkdir(parents=True, exist_ok=True)
    (dst / 'model.json').write_text(json.dumps(decode(skel.read_bytes()), separators=(',', ':')))
    atlas = (skel.parent / (name + '.atlas.txt')).read_text()
    for page in re.findall(r'^([^\r\n]+\.png)\r?$', atlas, re.M):
        stem = Path(page).stem
        im = Image.open(skel.parent / (stem + '_RGB.png')).convert('RGBA')
        im.putalpha(Image.open(skel.parent / (stem + '_Alpha.png')).convert('RGB').getchannel('R'))
        im.save(dst / (stem + '.webp'), quality=88, method=5)  # WebP pages (atlas rewritten below): ~1/4 of PNG
    (dst / 'model.atlas').write_text(re.sub(r'^([^\r\n]+)\.png(\r?)$', r'\1.webp\2', atlas, flags=re.M))
    n += 1
(OUT / 'slot').mkdir(parents=True, exist_ok=True)
for p in (HOT / 'textures/senpai_slot_web').glob('*.png'):
    shutil.copy2(p, OUT / 'slot' / p.name); n += 1
(OUT / 'ui').mkdir(parents=True, exist_ok=True)
icons = {i for r in items for i in str(r['icon']).split('|') if i} | {str(st['image']) for st in out['styles'] if st.get('image')} | {f'dress_buff_{i}' for i in range(1, 50)} | \
        {f'lead_skin_border_{i}' for i in range(1, 8)} | {'dress_summon_btn', 'dress_summon_btn_gy', 'dress_summon_cost_bg', 'dress_summon_free_bg',
                                                         'dress_summon_logo_en_en', 'dress_summon_limit_logo_en_en', 'dress_summon_limit_star'} | \
        {f'icon_{i}' for i in (258, 259, 260, 261, 3999991, 3999992, 3999993, 3999994, 3999995, 3999996)} | {str(r['icon']) for r in out['buffs']}
for name in icons:
    src = CUT / f'{name}.png'
    if src.exists():
        shutil.copy2(src, OUT / 'ui' / src.name); n += 1
for src, name in ((HOT / 'textures/scenes_big_web/dress_main_bg.png', 'dress_main_bg'), (HOT / 'textures/activity_web/dress_summon/dress_summon_normal_bg.png', 'dress_summon_normal_bg'),
                  (HOT / 'textures/activity_web/dress_summon/dress_summon_limit_bg.png', 'dress_summon_limit_bg')):
    im = Image.open(src).convert('RGB')
    im.crop(im.point(lambda v: 255 if v > 6 else 0).convert('L').getbbox()).save(OUT / 'ui' / f'{name}.webp', quality=82); n += 1
print(len(out['dress']), len(items), len(out['styles']), len(out['groups']), n)
# Campus cards (SchoolChooseWindow btnDress / btnDressBuy)
for name in ('btn_dress', 'btn_dress_buy', 'dress_text_en_en', 'dress_buy_text_en_en'):
    shutil.copy2(CUT / f'{name}.png', ROOT / 'web/assets/campus' / f'{name}.png')
