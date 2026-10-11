"""Guild v1 (Office, Cafeteria, Gym/Guild Boss, Merchant): guild_exp (levels), guild_boss (60 normal bosses; 61+ is the
final boss and isn't rebuilt), guild_order + guild_mill (Cafeteria), guild_trader (Merchant), guild_flag, misc guild_* values,
GUILD_* texts and the sprites. Output data/guild.json + web/assets/guild/. Sources in ~/Downloads are read only."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/guild'; (OUT / 'boss').mkdir(parents=True, exist_ok=True)
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def misc(key):
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', misc_text)
    return json.loads(m.group(1))


boss = {k: v for k, v in read_table('guild_boss').items() if int(k) <= 60}
db = sqlite3.connect(DEC / 'data/en_en.db')
text = dict(db.execute("select name, translation from translation_en_en where name like 'GUILD%'"))
names = {}
for r in db.execute('select id, name from item_text_en_en where id in (1,2,4,5)'): names[str(r[0])] = r[1]
out = {'exp': read_table('guild_exp'), 'boss': boss, 'order': read_table('guild_order'), 'mill': read_table('guild_mill'),
       'trader': read_table('guild_trader'), 'flags': sorted(int(k) for k in read_table('guild_flag')),
       'misc': {k: misc(k) for k in ('create_guild_cost', 'guild_sign_in_coin', 'guild_sign_in_exp', 'guild_boss_fight_cost', 'guild_boss_fight_cd',
                                     'guild_boss_max_id', 'guild_boss_exp_num_max', 'guild_mill_donate', 'guild_order_cd', 'guild_order_open',
                                     'guild_dissolve_cd', 'guild_name_num_max', 'modify_guild_name_cost')},
       'text': text, 'names': names}
(ROOT / 'data/guild.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
n = 0
for pat in ('guild_flag_*.png', 'guild_food*.png', 'guild_boss_card_*.png', 'guild_boss_clear_en_en.png', 'guild_boss_hp*.png', 'guild_boss_bg_*.png',
            'guild_boss_lace.png', 'guild_icon0*.png', 'guild_order_progressbar*.png', 'guild_level_max_en_en.png', 'guild_log_bg01.png'):
    for p in CUT.glob(pat): shutil.copy2(p, OUT / p.name); n += 1
for row in boss.values():
    p = CUT / f"{row['show']}.png"
    if p.exists(): shutil.copy2(p, OUT / 'boss' / p.name); n += 1
print(len(out['exp']), 'levels', len(boss), 'bosses', len(out['order']), 'orders', len(out['mill']), 'mill', len(out['trader']), 'trader', n, 'sprites')
