"""Scenes, portrait layout, Spine effects and music for the girl sheet, Graduate and battle results.

Usage: python3 tools/extract_visuals.py            (scenes, pictures table, result Spines, sounds)
       python3 tools/extract_visuals.py --lihui    (also every animated portrait, ~1 GB, slow)
Needs Pillow and ffmpeg (sounds are converted from Ogg to MP3 so Safari can play them).
"""
from __future__ import annotations
import json, re, shutil, subprocess, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from extract_inventory_assets import lua_table  # noqa: E402
from spine36 import decode  # noqa: E402

HOT = Path.home() / 'Downloads/Decomp files/unity/Assets/hotres'
TABLES = Path.home() / 'Downloads/Decomp files/lua/data/tables'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
WEB = ROOT / 'web/assets'
SOUNDS = {'ui_sound_web': ['home_bg_music', 'campaign_bg_music', 'battle_win', 'battle_lose', 'gain_window_sound',
                           'equip_forge', 'hero_upstart', 'girl_compose', 'girl_enrol', 'ui_switch_page', 'battle_card_reward'],
          'ui_sound': ['battle_bg_music_1', 'ui_click', 'ui_click_back', 'ui_hero', 'main_story_campus']}


def spine(src: Path, out: Path):
    """Spine 3.6 binary + Unity RGB/Alpha pages -> model.json, model.atlas and RGBA pages."""
    skel = next(src.glob('*.skel.bytes'))
    name = skel.name[:-len('.skel.bytes')]
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'model.atlas').exists():
        return name
    (out / 'model.json').write_text(json.dumps(decode(skel.read_bytes()), separators=(',', ':')))
    atlas = (src / f'{name}.atlas.txt').read_text()
    for page in re.findall(r'^([^\r\n]+\.png)\r?$', atlas, re.M):
        stem = Path(page).stem
        image = Image.open(src / f'{stem}_RGB.png').convert('RGBA')
        image.putalpha(Image.open(src / f'{stem}_Alpha.png').convert('RGB').getchannel('R'))
        image.save(out / page)
    (out / 'model.atlas').write_text(atlas)
    return name


def main(lihui=False):
    scenes = WEB / 'scenes'; scenes.mkdir(parents=True, exist_ok=True)
    for n in range(1, 8):
        # Unity stored the 656×1024 scene centred in a square power-of-two texture: drop the black padding.
        im = Image.open(HOT / f'textures/scenes_web/college_scene{n}.png').convert('RGB')
        box = im.convert('L').point(lambda v: 255 if v > 10 else 0).getbbox()
        im.crop(box).save(scenes / f'college_scene{n}.png')
    ui = WEB / 'girl-ui'; ui.mkdir(exist_ok=True)
    for name in ('partner_grade_icon', 'partner_grade_icon_bg', 'partner_star_red', 'partner_star_yellow', 'partner_star_purple',
                 'partner_star_blue', 'partner_star_bg', 'partner_detail_lv_bg', 'partner_battle_point_icon', 'job_icon_1',
                 'job_icon_2', 'job_icon_3', 'job_icon_4', 'job_icon_5', 'partner_detail_bubble_bg', 'partner_attr_bg',
                 'soul_equip_entry_icon', 'partner_star_origin_icon', 'partner_detail_zoom_icon', 'partner_detail_lock_icon',
                 'blue_btn_65_65', 'white_btn_65_65', 'nav_btn_blue_mid', 'nav_btn_white_mid', 'potentiality_card_star',
                 'potentiality_card_star_max', 'potentiality_nametag_star', 'potentiality_nametag_star_max'):
        if (CUT / f'{name}.png').exists():
            shutil.copyfile(CUT / f'{name}.png', ui / f'{name}.png')
    models = {k: r for k, r in lua_table(TABLES / 'girls_model.lua').items()}   # dragon_bone -> girls_model.resource
    pictures = {}
    for pid, row in lua_table(TABLES / 'partner_picture.lua').items():
        xy = [float(v) for v in str(row.get('partner_picture_xy') or '0|0').split('|')[:2]]
        xy2 = [float(v) for v in str(row.get('partner_picture_xy2') or row.get('partner_picture_xy') or '0|0').split('|')[:2]]  # MainMap (Front Page)
        pictures[pid] = {'xy': xy, 'xy2': xy2, 'scale': float(row.get('partner_picture_scale') or 1), 'wed': int(row.get('is_wedding') or 0),
                         'summon_static_scale': float(row.get('show_scale_special') or 1), 'summon_spine_scale': float(row.get('show_scale') or 1),
                         'spine': str(models.get(str(row.get('dragon_bone')), {}).get('resource') or '')}
    (ROOT / 'data/partner_pictures.json').write_text(json.dumps(pictures, separators=(',', ':')))
    for name in ('shengli_new', 'shibai_new'):
        spine(HOT / f'spine/battle_result/{name}', WEB / f'spine/{name}')
    sounds = WEB / 'sounds'; sounds.mkdir(exist_ok=True)
    for folder, names in SOUNDS.items():
        for name in names:
            src, dst = HOT / f'sounds/{folder}/{name}.ogg', sounds / f'{name}.mp3'
            if src.exists() and not dst.exists():
                subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(src), '-b:a', '128k', str(dst)], check=True)
    made = []
    if lihui:
        wanted = {p['spine'] for p in pictures.values() if p['spine']}
        for name in sorted(wanted):
            src = HOT / f'spine/picture_web/{name}'
            if src.is_dir():
                try:
                    spine(src, WEB / f'lihui/{name}'); made.append(name)
                except Exception as exc:  # keep going; report at the end
                    print('lihui failed', name, exc)
    (ROOT / 'data/lihui.json').write_text(json.dumps(sorted(p.name for p in (WEB / 'lihui').iterdir()) if (WEB / 'lihui').exists() else []))
    print(f'{len(pictures)} pictures, scenes 1–7, result spines, {len(list(sounds.glob("*.mp3")))} sounds, {len(made)} lihui')


if __name__ == '__main__':
    main('--lihui' in sys.argv)
