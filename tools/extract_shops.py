"""Shopping Street stores: shop_config + per-shop tables (Lua sources, SQLite columns are displaced), shop texts,
market dropboxes, shelf/scene textures, shop sprites and the shopkeeper Spines (girls_model.resource).
Output data/shops.json, web/assets/shops/, web/assets/spine/<resource>/."""
import json, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
from extract_slots_dealers import spine
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
HOT = DEC / 'unity/Assets/hotres'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/shops'; OUT.mkdir(parents=True, exist_ok=True)
SHOPS = [7, 11, 17, 2, 3, 13, 5, 6, 9]

cfg = read_table('shop_config')
names = dict(sqlite3.connect(DEC / 'data/en_en.db').execute('select * from shop_config_text_en_en'))
models = read_table('girls_model')
drop = json.loads((ROOT / 'data/dropbox.json').read_text())
out = {'shops': {}, 'tables': {}, 'dropbox': {}, 'models': {}}
for sid in SHOPS:
    c = cfg[str(sid)]
    out['shops'][sid] = {k: c.get(k) for k in ('id', 'excel_table', 'is_refresh', 'refresh_type', 'refresh_free_time', 'refresh_cost',
                                                'economy_show', 'girls_model', 'shop_bg', 'shop_banner', 'icon', 'slot_buy_time', 'slot_num',
                                                'limit_level', 'rank', 'type', 'offset', 'scale')}
    out['shops'][sid]['name'] = names.get(str(sid)) or names.get(sid) or {17: 'Antique Store'}.get(sid, '')  # 17: SHOP_MAP_TEXT05
    t = c['excel_table']
    if t not in out['tables']:
        out['tables'][t] = sorted(read_table(t).values(), key=lambda r: int(r['id']))
    m = models.get(str(c.get('girls_model') or ''))
    if m:
        out['models'][str(c['girls_model'])] = {'resource': m['resource'], 'idle': m['texiao_name'], 'enter': m['enter_texiao'],
                                                 'click': [m.get(f'click_texiao{i}') for i in range(1, 7) if m.get(f'click_texiao{i}')], 'size': m['size']}
boxes = {int(r['dropbox_id']) for r in out['tables']['shop_black_new']}
out['dropbox'] = {k: r for k, r in drop.items() if int(r['dropbox_id']) in boxes}
(ROOT / 'data/shops.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))

for f in (HOT / 'textures/shop_web').glob('*.png'):
    shutil.copy2(f, OUT / f.name)
for f in (HOT / 'textures/scenes_web').glob('market_scene*.png'):
    shutil.copy2(f, OUT / f.name)
shutil.copy2(HOT / 'textures/scenes_web/shop_map_bg.png', OUT / 'shop_map_bg.png')
for s in ['blue_btn_54_54', 'white_btn_54_54', 'market_arrow', 'market_dot_bg1', 'market_dot_bg2', 'shop_icon_bg', 'shop_frame_bg', 'purchased', 'shop_btn_3',
          'prop_img', 'nav_btn_blue_left', 'nav_btn_blue_mid', 'nav_btn_blue_right', 'nav_btn_white_left', 'nav_btn_white_mid', 'nav_btn_white_right',
          'alert_icon', 'shop_cafe', 'shop_skin', 'shop_market', 'shop_exchange', 'shop_artifact', 'shop_unopen', 'icon_58', 'refresh_icon'] + \
         [f'shop_group{i}_{j}' for i in range(1, 7) for j in (1, 2)] + [f'icon_{x}_small' for x in (2, 4, 6, 7, 15, 16, 65, 66, 73, 170, 173)]:
    p = CUT / f'{s}.png'
    if p.exists():
        shutil.copy2(p, OUT / p.name)
for m in out['models'].values():
    src = next((d for d in (HOT / 'spine').rglob(m['resource']) if d.is_dir()), None)
    if src:
        spine(src, ROOT / 'web/assets/spine' / m['resource'])
print(len(out['shops']), {k: len(v) for k, v in out['tables'].items()}, len(out['dropbox']), [m['resource'] for m in out['models'].values()])

# Item icons missing from web/assets/item-icons (girl shards use partner_avatar_*): copy them for shop goods.
catalog = {str(r['id']): r for r in json.loads((ROOT / 'web/assets/items-catalog.json').read_text()).values()} if (ROOT / 'web/assets/items-catalog.json').exists() else {}
have = {p.stem for p in (ROOT / 'web/assets/item-icons').glob('*.png')}
IT = OUT / 'items'; IT.mkdir(exist_ok=True)
ids = {str(r.get('item', '0#0')).split('#')[0] for rows in out['tables'].values() for r in rows} | {str(r['item']).split('#')[0] for r in out['dropbox'].values()}
copied = 0
for i in ids:
    icon = (catalog.get(i) or {}).get('icon')
    if icon and icon not in have and (CUT / f'{icon}.png').exists():
        shutil.copy2(CUT / f'{icon}.png', IT / f'{icon}.png'); copied += 1
print('item icons', copied)
