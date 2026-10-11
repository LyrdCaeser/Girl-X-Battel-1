"""Fantasy Book (BattlePassWindow.lua + BattlePassSteamNew / BattlePassMission / BattlePassExchange / BattlePassAchieve).

battlepass_award.lua: 50 levels, cost_total = Pages needed for the level, free_award (Basic Book), paid_award (Luxury Book),
cost_diamonds / cost_dct_diamonds (Gems per level; discount in the last 2 weeks), is_bigreward. battlepass_mission.lua:
tasks type 1 Daily / 2 Weekly / 3 Extra, complete_value_new, award_new + award2_new (117 = Pages), lv_limit (player level),
bp_limit (Book level). shop_battlepass.lua: type 1 Floral Stamp (221) / type 2 Crystal Leaf (222) exchanges; misc
bp_lottery_cost / bp_lottery_dropbox: Flora Bookmark draws. Texts: BP_* and battlepass_mission_text. Output
data/fantasy_book.json + web/assets/fantasy-book/ sprites. Sources are read only."""
import json, re, shutil, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/fantasy-book'; OUT.mkdir(parents=True, exist_ok=True)


def lua_table(path):
    text = path.read_text(encoding='utf-8-sig')
    keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', text.split('table.keys = {', 1)[1].split('}', 1)[0])}
    rows = {}
    for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\n\s*\}', text, re.S):
        vals = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p) for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
        rows[m.group(1)] = {k: vals[i] for k, i in keys.items() if i < len(vals)}
    return rows


misc = (T / 'misc.lua').read_text(encoding='utf-8-sig')
g = lambda k: re.search(r'\t' + k + r' = \{\s*"' + k + r'",\s*"?([^"\n,]*)"?,', misc).group(1)
en = sqlite3.connect(DEC / 'data/en_en.db')
mtext = {str(r[0]): r[1] for r in en.execute('select id, mission_des from battlepass_mission_text_en_en')}
text = dict(en.execute("select name, translation from translation_en_en where name like 'BP\\_%' escape '\\'"))
levels = [{'lv': int(r['id']), 'need': int(r['cost_total']), 'free': r['free_award'], 'paid': r['paid_award'], 'gems': r['cost_diamonds'],
           'gems_dct': r['cost_dct_diamonds'], 'big': int(r['is_bigreward'] or 0)} for r in sorted(lua_table(T / 'battlepass_award.lua').values(), key=lambda r: int(r['id']))]
missions = [{'id': int(r['id']), 'type': int(r['type']), 'need': int(r['complete_value_new']), 'award': r['award_new'], 'pages': r['award2_new'],
             'lv': int(r['lv_limit'] or 0), 'bp': int(r['bp_limit'] or 0), 'rank': int(r['rank'] or 0), 'text': mtext.get(str(r['id']), '')}
            for r in sorted(lua_table(T / 'battlepass_mission.lua').values(), key=lambda r: (int(r['type']), int(r['rank'] or 0), int(r['id'])))]
shop = [{'id': int(r['id']), 'type': int(r['type']), 'item': r['item'], 'cost': r['cost'], 'limit': int(r['buy_time'])}
        for r in sorted(lua_table(T / 'shop_battlepass.lua').values(), key=lambda r: int(r['id']))]
seasons = {k: {'pre': r['pre_award'], 'core': r['core_award']} for k, r in lua_table(T / 'battlepass.lua').items()}
out = {'levels': levels, 'missions': missions, 'shop': shop, 'seasons': seasons, 'lottery_cost': g('bp_lottery_cost'),
       'lottery_dropbox': int(g('bp_lottery_dropbox')), 'text': text}
(ROOT / 'data/fantasy_book.json').write_text(json.dumps(out, ensure_ascii=False, indent=0))
drop = [r for r in json.loads((ROOT / 'data/dropbox.json').read_text()).values() if int(r['dropbox_id']) == out['lottery_dropbox'] and int(r['weight']) > 0]
total = sum(int(r['weight']) for r in drop) or 1
(OUT / 'book.json').write_text(json.dumps({'levels': levels, 'shop': shop, 'text': text, 'lottery_cost': out['lottery_cost'],
                                           'odds': [[r['item'], round(int(r['weight']) * 100 / total, 2)] for r in drop]}, ensure_ascii=False, separators=(',', ':')))
names = ['battle_pass_achieve_bg_new', 'battle_pass_b_nav_1', 'battle_pass_bottom_bg_new', 'battle_pass_buy_btn_new', 'battle_pass_buy_btn_shadow_new',
         'battle_pass_exchange_flower_bg', 'battle_pass_gift_1', 'battle_pass_gift_2', 'battle_pass_lev_bg', 'battle_pass_lev_bg3_new', 'battle_pass_lev_bg_new',
         'battle_pass_level_text_bg', 'battle_pass_line1', 'battle_pass_line2', 'battle_pass_logo_bg', 'battle_pass_logo_new_en_en', 'battle_pass_mission_bar',
         'battle_pass_mission_bar_bg', 'battle_pass_nav', 'battle_pass_nav_select', 'battle_pass_title_0_new', 'battle_pass_title_1_new', 'battle_pass_title_2_new',
         'battle_pass_tmp3', 'battle_pass_top_bg_new', 'bp_bg_mengban', 'bp_exchange_shop_en_en', 'bp_exchange_top_bg', 'bp_flower', 'bp_mission_total_bar',
         'bp_mission_total_bar_bg', 'bp_mission_yeqina_1', 'bp_mission_yeqina_2', 'bp_mission_yeqina_bg', 'bp_none_bg', 'bp_shop_cost_bg', 'bp_shop_item_bg',
         'bp_shop_line', 'icon_117', 'icon_221', 'icon_222', 'icon_223', 'icon_119', 'icon_120', 'battle_pass_top_bg', 'battle_pass_top_bg_b', 'battle_pass_logo_en_en',
         'battle_pass_title_0', 'battle_pass_title_1', 'battle_pass_title_2', 'battle_pass_exchange_top_bg_1', 'battle_pass_exchange_top_bg_2', 'battle_pass_shop_1_en_en',
         'battle_pass_shop_2_en_en', 'battle_pass_shop_item_bg', 'battle_pass_buy_btn', 'bp_smithy_top', '9gongge17', 'mission_awarded_en_en', 'blue_btn_54_54', 'white_btn_check', 'help_2', 'awake_lock', 'alert_icon']
for n in names:
    if (CUT / f'{n}.png').exists(): shutil.copyfile(CUT / f'{n}.png', OUT / f'{n}.png')
print(len(levels), 'levels,', len(missions), 'tasks,', len(shop), 'shop rows,', len(list(OUT.glob('*.png'))), 'sprites')
