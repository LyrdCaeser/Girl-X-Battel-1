"""Campaign window art (campaign_window.prefab) and per-stage display data.
Output: web/assets/campaign/*.png and data/campaign.json {stages:{id:{img,name,monsters,reward,drops}}, forts:{id:{name,desc}}}."""
import json, shutil, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/campaign'
OUT.mkdir(parents=True, exist_ok=True)
names = ['stage_frame01', 'stage_frame02', 'stage_lock', 'route_bg', 'campaign_resource', 'btn_help', 'btn_rank',
         'campaign_battle_01', 'campaign_battle_02', 'recover', 'recover_bg', 'campaign_icon_map', 'campaign_icon_gift',
         'select_bg_min', 'icon_1', 'icon_3', 'icon_9', 'blue_btn_65_65', 'alert_icon', 'little_tips_bg',
         'arena_sword', 'battle_detail_icon_2', 'battle_detail_progress_1', 'battle_detail_progress_2', 'battle_detail_item_bg', 'battle_detail_bg']
names += [p.stem for p in CUT.glob('stage_img*.png')]
for n in names:
    if (CUT / f'{n}.png').exists():
        shutil.copyfile(CUT / f'{n}.png', OUT / f'{n}.png')
# Hang scene maps (set_map) cropped from their square power-of-two textures, the stage list background,
# and any battle map the battle viewer was missing.
from PIL import Image
TEX = Path.home() / 'Downloads/Decomp files/unity/Assets/hotres/textures'
(OUT / 'maps').mkdir(exist_ok=True)
for src in [*(TEX / 'battle_map_web').glob('battle_map_*.png'), *(TEX / 'local_tex').glob('battle_map_*.png')]:
    im = Image.open(src).convert('RGB')
    box = im.convert('L').point(lambda v: 255 if v > 10 else 0).getbbox()
    im.crop(box).save(OUT / 'maps' / (src.stem + '.webp'), 'WEBP', quality=88)
    full = ROOT / 'web/assets/battle-maps' / src.name
    if not full.exists():
        shutil.copyfile(src, full)
rgba = Image.open(TEX / 'scenes_web/campaign_select_bg.png').convert('RGBA')
rgba.crop(rgba.getchannel('A').getbbox()).save(OUT / 'campaign_ground.png')
bg = Image.open(TEX / 'scenes_web/campaign_select_bg.png').convert('RGB')
bg.crop(bg.convert('L').point(lambda v: 255 if v > 6 else 0).getbbox()).save(OUT / 'campaign_select_bg.webp', 'WEBP', quality=88)
en = sqlite3.connect(Path.home() / 'Downloads/Decomp files/data/en_en.db')
stage_names = {r[0]: r[1] for r in en.execute('select id, name from stage_text_en_en')}
forts = {r[0]: {'name': r[1], 'desc': r[2]} for r in en.execute('select id, name, desc from fort_text_en_en')}
stages = {}
for sid, row in json.loads((ROOT / 'data/stage.json').read_text()).items():
    stages[sid] = {'img': row.get('stage_img') or 'stage_img',
                'map': row.get('set_map') or 'battle_map_26_1', 'name': stage_names.get(sid, ''),
                   'monsters': [int(x) for x in str(row.get('monsterShow') or '').split('|') if x],
                   'reward': row.get('reward') or '', 'drops': str(row.get('dropbox_show') or ''),
                   'rate': [row.get('gold'), row.get('exp_partner'), row.get('exp_player')]}
(ROOT / 'data/campaign.json').write_text(json.dumps({'stages': stages, 'forts': forts}, ensure_ascii=False, separators=(',', ':')))
names = sorted(p.stem for p in (ROOT / 'web/assets/battle-maps').glob('battle_map_*.png'))
(ROOT / 'web/assets/battle-maps.json').write_text(json.dumps(names))
print(len(stages), 'stages', len(forts), 'forts', len(list(OUT.glob('*.png'))), 'sprites')

# CampaignFortWindow: chapter banners fort_img_1..10 (reused by every difficulty), lock / mask / frames
import shutil as _sh
_CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
for _n in [f'fort_img_{i}' for i in range(1, 11)] + ['fort_mask', 'fort_dot', 'lock', 'window_bg07', 'window_bg08']:
    if (_CUT / f'{_n}.png').exists(): _sh.copy2(_CUT / f'{_n}.png', ROOT / 'web/assets/campaign' / f'{_n}.png')
