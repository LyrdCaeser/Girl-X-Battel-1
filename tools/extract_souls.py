"""Anima Gear (models/SoulEquip1.lua, SoulEquip2.lua, HeroAttr:getSouls, ReportHero souls, SoulEquipInfoWindow,
SoulEquip1/2StrengthenWindow): soul_equip1 (centre piece: base/grow, star_grow, copies to awaken), soul_equip2 (4 round
pieces: pos 2-5, group set, star, main buff, random ex buffs), buff tables, exp tables, set groups + set skill text,
misc soul_* values, Soul Land summon (soul_land_equip2_gacha / dropbox). Icons: soul_equip_<id>, frames
lead_skin_border_<qlt>, soul_equip_icon_pos_<qlt>, pub_star_require<n>, window art. Output data/souls.json +
web/assets/souls/. Sources in ~/Downloads are read only."""
import json, re, shutil, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
HOT = DEC / 'unity/Assets/hotres'
OUT = ROOT / 'web/assets/souls'; OUT.mkdir(parents=True, exist_ok=True)


def lua_table(path):
    text = path.read_text(encoding='utf-8-sig')
    keys_text = text.split('table.keys = {', 1)[1].split('}', 1)[0]
    keys = {key: int(index) - 1 for key, index in re.findall(r'(\w+)\s*=\s*(\d+)', keys_text)}
    rows = {}
    for match in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\n\s*\}', text, re.S):
        values = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p)
                  for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', match.group(2))]
        rows[match.group(1)] = {key: values[index] for key, index in keys.items() if index < len(values)}
    return rows


t = lambda n: lua_table(T / f'{n}.lua')
misc = (T / 'misc.lua').read_text(encoding='utf-8-sig')
def m(key):
    r = re.search(r'\t' + key + r' = \{\s*"' + key + r'",\s*"([^"]*)"', misc)
    return r.group(1) if r else ''
db = sqlite3.connect(DEC / 'data/en_en.db')
equip1, equip2 = t('soul_equip1'), t('soul_equip2')
ids = list(equip1) + list(equip2) + ['425', '427', '435', '417', '418', '419', '420', '421', '422', '423', '424', '426', '14'] + [str(5200100 + i) for i in range(1, 10)]
names = {str(r[0]): r[1] for r in db.execute('select id, name from item_text_en_en where id in (%s)' % ','.join(ids + [str(5200000 + i) for i in range(1, 10)]))}
items = {}
for f in sorted(T.glob('item[0-9]*.lua')):
    for k, r in lua_table(f).items():
        if k in ids: items[k] = r
groups = t('soul_equip2_group')
skill_text = {str(r[0]): (r[2], r[3]) for r in db.execute('select * from skill_text_en_en where id in (%s)' % ','.join(str(g['skill']) for g in groups.values()))}
out = {'equip1': equip1, 'equip2': equip2, 'buff1': t('soul_equip1_ex_buff'), 'base2': t('soul_equip2_base_buff'), 'buff2': t('soul_equip2_ex_buff'),
       'exp1': t('exp_soul_equip1'), 'exp2': t('exp_soul_equip2'), 'gacha': t('soul_land_equip2_gacha'), 'dropbox': t('soul_land_equip2_dropbox'),
       'groups': {k: {**g, 'name': names.get(str(g['item']), ''), 'skill_name': skill_text.get(str(g['skill']), ('', ''))[0], 'skill_desc': skill_text.get(str(g['skill']), ('', ''))[1]} for k, g in groups.items()},
       'names': {k: names.get(k, '') for k in ids}, 'icons': {k: str(items.get(k, {}).get('icon') or '') for k in ids},
       'qlt1': {k: int(items.get(k, {}).get('qlt') or 1) for k in equip1},
       'land': t('soul_land'), 'land_award': t('soul_land_award'), 'land_shop': t('soul_land_shop'),
       'misc': {k: m(k) for k in ('soul_equip1_ex_num', 'soul_equip1_ex_first_cost', 'soul_equip1_ex_cost', 'soul_equip1_star_lvl', 'soul_equip2_ex_buff_num',
                                   'soul_equip2_ex_buff_value', 'soul_equip2_ex_cost', 'soul_equip2_ex_buff_lvl', 'soul_equip_limit', 'soul_equip_open_lvl',
                                   'soul_equip2_lvl_exp_cost', 'soul_equip2_sp_item', 'soul_equip2_qlt_cost',
                                   'soul_land_ticket_init', 'soul_land_ticket_max', 'soul_land_ticket_daliy', 'soul_land_award_time_max', 'soul_land_open_lvl',
                                   'soul_land_cycle_time', 'soul_land_start_time')}}
gods = sorted({int(r['god_skill']) for r in out['land'].values() if r.get('god_skill')})
out['god_text'] = {str(r[0]): [r[2], r[3]] for r in db.execute('select * from skill_text_en_en where id in (%s)' % ','.join(map(str, gods)))}
(ROOT / 'data/souls.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
n = 0
wanted = {v for v in out['icons'].values() if v} | {f'lead_skin_border_{i}' for i in range(1, 8)} | {f'soul_equip_icon_pos_{i}' for i in range(1, 7)} | \
         {f'pub_star_require{i}' for i in range(1, 7)} | {f'soul_equip_kuang_small_{i}' for i in range(1, 7)} | \
         {'soul_equip_bg_lx', 'soul_equip_bg_di', 'soul_equip_bg_xinxi', 'soul_equip_icon_rk_lszb', 'soul_equip_kuang_bg', 'red_btn_60_60', 'blue_btn_60_60',
          'battle_detail_icon_2', '9gongge19', '9gongge26', 'white_btn_0', 'icon_plus', 'soul_equip_btn_0', 'soul_equip_btn_0_xz', 'soul_equip_btn_00', 'soul_equip_btn_00_xz',
          'soul_land_enter_logo_en_en', 'btn_gq_1', 'btn_gq_2', 'btn_gq_3', 'icon_421', 'icon_422', 'icon_423', 'icon_424', 'icon_426', 'icon_435', 'soul_equip_bg_zonglan_1', 'soul_equip_bg_zonglan_2', 'soul_equip_bg_zonglan_3', 'soul_equip_bg_zonglan_4', 'skill_resonate_icon', 'advanced_skill'} | \
         {f'soul_equip_{5200000 + i}' for i in range(1, 10)}
for name in wanted:
    src = CUT / f'{name}.png'
    if src.exists():
        shutil.copy2(src, OUT / src.name); n += 1
print(len(equip1), 'equip1,', len(equip2), 'equip2,', len(groups), 'sets,', n, 'sprites')
# Land of Souls art: league card (soul_land_enter_bg + logo), main banner
from PIL import Image
card = Image.open(CUT / 'soul_land_enter_bg.png').convert('RGBA'); logo = Image.open(CUT / 'soul_land_enter_logo_en_en.png').convert('RGBA')
card.alpha_composite(logo.resize((logo.width * 2, logo.height * 2)), (30, 30)); card.save(ROOT / 'web/assets/league/btn_soul_land.png')
TEXB = HOT / 'textures'
for src in [TEXB / 'scenes_big_web/soul_land_main_bg_banner.png'] + list((TEXB / 'common_ui_texture_web/soul_land').glob('*.png')):
    Image.open(src).convert('RGBA').save(OUT / (src.stem + '.webp'), 'WEBP', quality=86)
for name in ['soul_land_btn_gq', 'soul_land_btn_gq_n', 'soul_land_btn_gq_zy', 'soul_land_btn_sd', 'soul_land_btn_sj', 'soul_land_btn_zd', 'soul_land_bg_gqjd', 'soul_land_bg_sjsd', 'soul_land_hk_1', 'soul_land_hk_2', 'soul_land_bg_dx_1', 'soul_land_btn_ck_1']:
    if (CUT / f'{name}.png').exists(): shutil.copy2(CUT / f'{name}.png', OUT / f'{name}.png')
# SoulEquip1StrengthenWindow (capture fb/120): the winged header (texture chess_exchange), the Star up / Upgrade / Infuse
# tab buttons, the MAX label and the "+" slot of the Star up material.
shutil.copy2(HOT / 'textures/hero_challenge_web/chess_exchange.png', OUT / 'chess_exchange.png')
for name in ['nav_btn_blue_left', 'nav_btn_blue_mid', 'nav_btn_blue_right', 'nav_btn_white_left', 'nav_btn_white_mid', 'nav_btn_white_right', 'pet_skill_max_en_en', 'arena_team_plus', 'chat_privacy_line']:
    if (CUT / f'{name}.png').exists(): shutil.copy2(CUT / f'{name}.png', OUT / f'{name}.png')
