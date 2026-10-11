"""Servant (pet) screens: PetWindow / PetDetailWindow art, Spine models per grade and English texts.
Output: web/assets/servant/*.png, web/assets/spine/pets/<model>/ and data/servants.json. Sources read-only.
Does not import extract_inventory_assets (its import regenerates catalogues as a side effect)."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from spine36 import decode  # noqa: E402
HOT = Path.home() / 'Downloads/Decomp files/unity/Assets/hotres'
TABLES = Path.home() / 'Downloads/Decomp files/lua/data/tables'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/servant'; OUT.mkdir(parents=True, exist_ok=True)
SPINE = ROOT / 'web/assets/spine/pets'


def spine(src: Path, out: Path):
    skel = next(src.glob('*.skel.bytes')); name = skel.name[:-len('.skel.bytes')]
    out.mkdir(parents=True, exist_ok=True)
    if not (out / 'model.atlas').exists():
        (out / 'model.json').write_text(json.dumps(decode(skel.read_bytes()), separators=(',', ':')))
        atlas = (src / f'{name}.atlas.txt').read_text()
        for page in re.findall(r'^([^\r\n]+\.png)\r?$', atlas, re.M):
            stem = Path(page).stem
            im = Image.open(src / f'{stem}_RGB.png').convert('RGBA')
            im.putalpha(Image.open(src / f'{stem}_Alpha.png').convert('RGB').getchannel('R')); im.save(out / page)
        (out / 'model.atlas').write_text(atlas)
    return sorted(json.loads((out / 'model.json').read_text())['animations'])


home = json.loads((ROOT / 'data/home_systems.json').read_text())
model_text = (TABLES / 'model.lua').read_text(encoding='utf-8-sig')
def model_name(mid):
    m = re.search(r'\["' + str(mid) + r'"\] = \{\s*\d+,\s*[^,]+,\s*[^,]+,\s*"([^"]+)"', model_text)
    return m.group(1) if m else ''
en = sqlite3.connect(Path.home() / 'Downloads/Decomp files/data/en_en.db')
pet_text = {r[0]: {'name': r[1], 'weapon': r[2]} for r in en.execute('select * from pet_text_en_en')}
skill_text = {r[0]: {'name': r[2], 'desc': r[3]} for r in en.execute('select id, missing_field_2, name, desc from skill_text_en_en')}
pas_text = {r[0]: {'name': r[1], 'desc': r[2]} for r in en.execute('select id, name, desc from pet_skill_text_en_en')}
icons = set()
pets = {}
for row in home['pet']:
    pid = row['id']; base = int(row['pet_model'])
    models = {}
    for grade in range(1, int(row['max_grade']) + 1):
        name = model_name(base - 1 + grade)
        family = name.rsplit('_', 1)[0]
        src = HOT / f'spine/pet_web/{family}/{name}'
        if name and src.is_dir():
            models[grade] = {'name': name, 'animations': spine(src, SPINE / name)}
    act = int(row['act_skill_id'])
    pets[pid] = {'id': int(pid), **pet_text.get(pid, {'name': pid, 'weapon': ''}), 'models': models,
                 'act_skill': {str(lv): skill_text.get(str(act + lv - 1), {}) for lv in (1, 30, 60, 90, 120, 150, 180)},
                 'act_icon': f'pet_skill_{str(act)[:4]}',
                 'passives': [{**pas_text.get(row[f'pas_skill{i}_id'], {}), 'icon': f"pet_skill_{row[f'pas_skill{i}_id'][:4]}"} for i in range(1, 5)],
                 'exskill_icon': f"pet_exskill_{pid}", 'avatar': row['pet_avatar'], 'frame': row['pet_frame']}
    icons.update([pets[pid]['act_icon'], pets[pid]['exskill_icon']] + [p['icon'] for p in pets[pid]['passives']])
    icons.update(f"{row['pet_avatar']}{g}" for g in range(1, 5))
# Every per-level skill text for the energy skill (1..max_lv) is large; keep the level milestones above and the
# formula lives in skill_text for exact levels on demand.
for n in list(icons) + ['pet_kind01', 'pet_name_bg', 'pet_bg01', 'pet_bg02', 'pet_bg03', 'pet_bg04', 'pet_bg05', 'pet_bg06',
                        'pet_btn_data', 'pet_btn_reborn', 'pet_exskill_bg', 'icon_26', 'icon_27', 'icon_1', 'fort_bg_1_up',
                        'fort_bg_1_down', 'help_2', 'partner_detail_arrow', 'blue_btn_65_65', 'white_btn_65_65',
                        'nav_btn_blue_left', 'nav_btn_blue_right', 'nav_btn_white_left', 'nav_btn_white_right', 'pet_lock',
                        'pet_star', 'pet_star_grey', 'pet_skill_bg', 'pet_skill_lock', 'btn_levup', 'btn_up_arrow',
                        'partner_levelup_btn', 'pet_attr_bg', 'pet_card_bg']:
    if (CUT / f'{n}.png').exists():
        shutil.copyfile(CUT / f'{n}.png', OUT / f'{n}.png')
_scene = Image.open(HOT / 'textures/scenes_web/pet_scene1.png').convert('RGB')
_scene.crop(_scene.convert('L').point(lambda v: 255 if v > 10 else 0).getbbox()).save(OUT / 'pet_scene1.webp', 'WEBP', quality=88)
(ROOT / 'data/servants.json').write_text(json.dumps({'pets': pets, 'assets': sorted(p.stem for p in OUT.glob('*.*'))}, ensure_ascii=False, separators=(',', ':')))
print(len(pets), 'servants;', sum(len(p['models']) for p in pets.values()), 'models;', len(list(OUT.glob('*'))), 'assets')
