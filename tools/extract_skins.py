"""Girl skins (Partner.equipments[7], SkinDetailWindow, partner detail Skins tab, CollectionSkinWindow):
equip rows with pos 7 (stats base1/base2, partner_model → chibi + picture + avatar, quality), item rows (name,
collection_id), partner.skin_ids (which girls wear it), shop_skin prices, collection (Yume Collection points 123 per skin),
collection_skin_group (themes) and collection_skin_effect (points → HP / ATK for every girl).
Assets: the skin picture saved as web/assets/pictures/<skin>.webp (partner_pictures.json already has the skin ids),
avatars web/assets/skins/<skin>.png, skin chibis web/assets/chibis/<model> + chibis/catalog.json entries by skin id.
Output data/skins.json."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
from spine36 import decode
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
HOT = DEC / 'unity/Assets/hotres'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'


def lua_table(path):
    """Same parser as tools/extract_inventory_assets.lua_table (importing that module runs its whole extraction)."""
    text = path.read_text(encoding='utf-8-sig')
    keys_text = text.split('table.keys = {', 1)[1].split('}', 1)[0]
    keys = {key: int(index) - 1 for key, index in re.findall(r'(\w+)\s*=\s*(\d+)', keys_text)}
    rows = {}
    for match in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\n\s*\}', text, re.S):
        values = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p)
                  for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', match.group(2))]
        rows[match.group(1)] = {key: values[index] for key, index in keys.items() if index < len(values)}
    return rows


def split(name):
    rows = {}
    for f in sorted(T.glob(name + '[0-9]*.lua')):
        rows.update(lua_table(f))
    return rows


equip = split('equip')
item = split('item')
model = read_table('model')
partners = json.loads((ROOT / 'data/partner.json').read_text())
db = sqlite3.connect(DEC / 'data/en_en.db')
names = {str(r[0]): r[1] for r in db.execute('select id, name from item_text_en_en where id between 7000 and 7999')}
coll = {str(r['item_id']): r for r in read_table('collection').values() if str(r.get('item_id', '')).startswith('7')}
shop = {str(r['item']).split('#')[0]: str(r['cost']) for r in read_table('shop_skin').values()}
wearers = {}
for pid, row in partners.items():
    for sid in str(row.get('skin_ids') or '').split('|'):
        if sid.strip():
            wearers.setdefault(sid.strip(), []).append(int(pid))
skins = {}
for sid, row in equip.items():
    if str(row.get('pos')) != '7':
        continue
    mid = str(row.get('partner_model') or '')
    it = item.get(sid, {})
    attrs = [str(row.get(k)) for k in ('base1', 'base2', 'base3') if row.get(k) not in ('', None, 0)]
    c = coll.get(sid, {})
    skins[sid] = {'id': int(sid), 'name': names.get(sid, ''), 'qlt': int(row.get('qlt') or it.get('qlt') or 1), 'model': mid,
                  'spine': (model.get(mid) or {}).get('model_name', ''), 'attrs': attrs, 'partners': wearers.get(sid, []),
                  'shop': shop.get(sid, ''), 'points': int(str(c.get('awards') or '0#0').split('#')[-1] or 0), 'group': int(c.get('group') or 0),
                  'rarity': int(c.get('qlt') or 1)}  # collection qlt → COLLECTION_SKIN_TEXT13..16: 1 Common, 2 Rare, 3 Epic, 4 Legendary
theme_names = {str(r[0]): r[1] for r in db.execute('select id, name from collection_skin_group_text_en_en')}
out = {'skins': skins,
       'themes': [{'id': int(r['id']), 'name': theme_names.get(str(r['id']), ''), 'skins': [int(x) for x in str(r['skins']).split('|') if x], 'type': int(r['type']), 'awards': str(r['awards'])}
                  for r in sorted(read_table('collection_skin_group').values(), key=lambda r: int(r['id']))],
       'effects': [{'point': int(r['point']), 'effect': str(r['effect'])} for r in sorted(read_table('collection_skin_effect').values(), key=lambda r: int(r['id']))]}
(ROOT / 'data/skins.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))

# pictures by skin id (partner_pictures.json is keyed by skin id already)
pics = set(json.loads((ROOT / 'data/pictures.json').read_text()))
n = 0
for sid, s in skins.items():
    src = HOT / 'textures/partner_picture_web' / f"partner_picture_{s['model']}.png"
    dst = ROOT / 'web/assets/pictures' / f'{sid}.webp'
    if src.exists():
        if not dst.exists():
            Image.open(src).convert('RGBA').save(dst, 'WEBP', quality=86, method=4); n += 1
        pics.add(int(sid))
(ROOT / 'data/pictures.json').write_text(json.dumps(sorted(pics)))
AV = ROOT / 'web/assets/skins'; AV.mkdir(parents=True, exist_ok=True)
for sid, s in skins.items():
    src = CUT / f"partner_avatar_{s['model']}.png"
    if src.exists():
        shutil.copy2(src, AV / f'{sid}.png'); n += 1
# skin cards (PartnerCard:setSkinCard): partner_card_<model> art, the partner_card03 frame (sliced), rarity ribbons
# collection_dress_new_bg_<qlt>, faction icons img_group<n>, worn check skin_icon01
(AV / 'cards').mkdir(exist_ok=True)
for sid, s in skins.items():
    src = CUT / f"partner_card_{s['model']}.png"
    if not src.exists(): src = CUT / f"partner_crad_{s['model']}.png"  # typo in the client for 5600105 / 5301502
    if not src.exists(): src = CUT / f"partner_avatar_{s['model']}.png"  # no card at all (e.g. 5401307): its avatar
    if src.exists() and not (AV / 'cards' / f'{sid}.webp').exists():
        Image.open(src).convert('RGBA').save(AV / 'cards' / f'{sid}.webp', 'WEBP', quality=88, method=4); n += 1
(AV / 'ui').mkdir(exist_ok=True)
for name in ['partner_card03', 'partner_card_mask', 'skin_icon01', 'skin_bg01', 'skin_bg02', 'skin_btn01', 'skin_btn02', 'skin_show_btn', 'red_btn_65_65', 'blue_btn_65_65', 'btn_skin_collection', 'collection_skin_bg'] + [f'collection_dress_new_bg_{i}' for i in range(1, 5)] + [f'img_group{i}' for i in range(1, 8)]:
    if (CUT / f'{name}.png').exists():
        shutil.copy2(CUT / f'{name}.png', AV / 'ui' / f'{name}.png'); n += 1
# skin chibis (hero_web skeletons), same export as tools/import_battle_assets.py
SRC = HOT / 'spine/hero_web'
skel = {x.name[:-len('.skel.bytes')]: x for x in SRC.parent.rglob('*.skel.bytes') if 'hero' in str(x.parent)}
chib = ROOT / 'web/assets/chibis'
catalog = json.loads((chib / 'catalog.json').read_text())
for sid, s in skins.items():
    src = skel.get(s['spine'])
    if not src:
        continue
    folder = chib / s['spine']
    if not (folder / 'model.atlas').exists():
        folder.mkdir(exist_ok=True)
        (folder / 'model.json').write_text(json.dumps(decode(src.read_bytes()), separators=(',', ':')))
        atlas = src.with_name(s['spine'] + '.atlas.txt').read_text()
        for page in re.findall(r'^([^\r\n]+\.png)\r?$', atlas, re.M):
            im = Image.open(src.parent / (Path(page).stem + '_RGB.png')).convert('RGBA')
            im.putalpha(Image.open(src.parent / (Path(page).stem + '_Alpha.png')).convert('RGB').getchannel('R'))
            im.save(folder / page)
        (folder / 'model.atlas').write_text(atlas); n += 1
    group = int(partners[str(s['partners'][0])]['group']) if s['partners'] and str(s['partners'][0]) in partners else 0
    catalog[sid] = {'model': s['spine'], 'animations': list(json.loads((folder / 'model.json').read_text())['animations']), 'group': group}
(chib / 'catalog.json').write_text(json.dumps(catalog, separators=(',', ':')))
print(len(skins), 'skins,', sum(1 for s in skins.values() if s['partners']), 'with wearers,', sum(1 for s in skins.values() if s['spine'] in skel), 'chibis,', n, 'files')
