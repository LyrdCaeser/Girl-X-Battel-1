"""Tsuruga Grand Shrine (models/ShrineHurdleModel.lua, models/Shrine.lua, SHRINE_HURDLE_HELP): Realm of Trials floors
(shrine_hurdle), routes and environments (shrine_route + route text), difficulty (shrine_difficulty), battles and bosses,
buffs (shrine_hurdle_buff + text), recover options, Message Board tasks / achievements, Pond of Prayers shops, story
(shrine_plot_list + shrine_plot1/2 + texts), misc shrine_*, window art. Output data/shrine.json + web/assets/shrine/."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
TEX = DEC / 'unity/Assets/hotres/textures'
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def misc(key):
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', misc_text)
    return json.loads(m.group(1))


rows = lambda n: sorted(read_table(n).values(), key=lambda r: int(r['id']))
plot = {**read_table('shrine_plot1'), **read_table('shrine_plot2')}
keep = ('id', 'next_id', 'type', 'image_path', 'res_path', 'partner_picture_xy', 'scale', 'show_type', 'face', 'face_pos')
out = {'misc': {k: misc(k) for k in ('shrine_open_limit', 'shrine_time_start', 'shrine_time_interval', 'shrine_hurdle_ticket',
                                     'shrine_hurdle_ticket_buy_cost', 'shrine_hurdle_ticket_buy_limit', 'shrine_hurdle_buff_giveup',
                                     'shrine_hurdle_difficulty_count', 'shrine_hurdle_difficulty_float', 'shrine_hurdle_boss_score_count')},
       'floors': rows('shrine_hurdle'), 'routes': rows('shrine_route'), 'diff': {str(r['id']): r for r in rows('shrine_difficulty')},
       'battles': {str(r['id']): r for r in rows('shrine_hurdle_battle')}, 'bosses': {str(r['id']): r for r in rows('shrine_hurdle_boss')},
       'buffs': rows('shrine_hurdle_buff'), 'missions': rows('shrine_mission'), 'ach': {str(r['id']): r for r in rows('shrine_achievement')},
       'ach_type': rows('shrine_achievement_type'), 'shop1': rows('shop_shrine1'), 'shop2': rows('shop_shrine2'), 'rank': rows('shrine_hurdle_rank'),
       'plots': rows('shrine_plot_list'),
       'plot': {k: {f: v[f] for f in keep if v.get(f) not in ('', None)} for k, v in plot.items()}}
db = sqlite3.connect(DEC / 'data/en_en.db')
q = lambda sql: list(db.execute(sql))
out['route_text'] = {str(r[0]): {'name': r[1], 'title': r[2], 'desc': r[3]} for r in q('select * from shrine_hurdle_route_text_en_en')}
# Environment icons (ShrineHurdleChooseWayWindow: skillTable:getSkillIcon(environment id) → skill_icon_N)
import re as _re
_T = Path.home() / 'Downloads/Decomp files/lua/data/tables'
for _f in sorted(_T.glob('skill[0-9]*.lua')):
    _t = _f.read_text(encoding='utf-8-sig')
    if 'table.keys = {' not in _t: continue
    _k = {k: int(i) - 1 for k, i in _re.findall(r'(\w+)\s*=\s*(\d+)', _t.split('table.keys = {', 1)[1].split('}', 1)[0])}
    for _m in _re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\n\s*\}', _t, _re.S):
        if _m.group(1) in out['route_text']:
            _v = _re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', _m.group(2))
            _ic = _v[_k['icon_id']].strip('"') if _k['icon_id'] < len(_v) else ''
            if _ic and _ic != '-1': out['route_text'][_m.group(1)]['icon'] = ('skill_icon_' + _ic) if _ic.isdigit() else _ic
out['buff_text'] = {str(r[0]): {'name': r[1], 'desc': r[2]} for r in q('select * from shrine_hurdle_buff_text_en_en')}
out['restore_text'] = {str(r[0]): {'name': r[1], 'desc': r[2]} for r in q('select * from shrine_hurdle_restore_text_en_en')}
out['mission_text'] = {str(r[0]): r[1] for r in q('select * from shrine_mission_text_en_en')}
out['ach_text'] = {str(r[0]): r[1] for r in q('select * from shrine_achievement_text_en_en')}
out['plot_title'] = {str(r[0]): r[1] for r in q('select * from shrine_plot_list_text_en_en')}
out['plot_tab'] = {str(r[0]): r[1] for r in q('select * from shrine_plot_tab_text_en_en')}
out['plot_text'] = {str(r[0]): {'title': r[1], 'name': r[2], 'dialog': r[3]} for r in q('select * from shrine_plot_text_en_en')}
out['items'] = {str(r[0]): {'name': r[1], 'desc': r[3]} for r in q('select * from item_text_en_en where id in (322,323,324,325,326,331,332,374)')}
out['text'] = dict(q("select name, translation from translation_en_en where name like 'SHRINE%' or name = 'SURE'"))
(ROOT / 'data/shrine.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))

OUT = ROOT / 'web/assets/shrine'; OUT.mkdir(parents=True, exist_ok=True)
n = 0
for p in [*CUT.glob('shrine_*.png'), *CUT.glob('broadcast_*.png'), CUT / 'btn_shrine_hurdle.png', CUT / 'shrine_icon1.png', CUT / 'shrine_icon_2.png',
          *[CUT / f'icon_{i}.png' for i in (322, 323, 324, 325, 326, 331, 332, 374)]]:
    if p.exists() and not re.search(r'_(de_de|fr_fr|ja_jp|ko_kr|zh_tw)\.png$', p.name):
        shutil.copy2(p, OUT / p.name); n += 1
# Scenes (entrance, trial background, story backgrounds) and story pictures → WebP to keep the bundle small.
scenes = {'shrine_main_bg', 'shrine_main_bg2', 'shrine_wait'} | {v['image_path'] for v in plot.values() if v.get('image_path')}
for name in scenes:
    for sub in ('scenes_web', 'scenes_big_web'):
        src = TEX / sub / f'{name}.png'
        if src.exists():
            Image.open(src).convert('RGB').save(OUT / f'{name}.webp', quality=82); n += 1; break
big = TEX / 'scenes_big_web/shrine_hurdle_main_bg.png'
im = Image.open(big).convert('RGB')
im.crop(im.point(lambda v: 255 if v > 8 else 0).convert('L').getbbox()).save(OUT / 'shrine_hurdle_main_bg.webp', quality=82); n += 1  # drop black padding
for name in {v['res_path'] for v in plot.values() if v.get('res_path')}:
    for sub in ('partner_picture_web', 'partner_picture'):
        src = TEX / sub / f'{name}.png'
        if src.exists():
            Image.open(src).save(OUT / f'pic_{name}.webp', quality=85); n += 1; break
print(len(out['floors']), len(out['battles']), len(out['buffs']), len(out['plot']), n)
# Next-stage indicators (ShrineHurdleWindow indexToName: battle / reward / store / recover), played with "texiao01".
from extract_slots_dealers import spine
SPD = DEC / 'unity/Assets/hotres/spine/shrine_hurdle_web'
for name in ('shrine_zhandou', 'shrine_jiangli', 'shrine_shangdian', 'shrine_huifu'):
    spine(SPD / name, ROOT / 'web/assets/spine' / name)
shutil.copy2(CUT / 'btn_shrine_hurdle.png', ROOT / 'web/assets/league/btn_shrine_hurdle.png')  # League card (BattleChooseWindow)
