"""Jackpot of Fortune (activity 64, ActivityJackPotMachine; capture 2026-09-29-fb/3): the 27 reel combinations of
activity_jackpot_machine (positions 1-3, weight, awards for Basic / awards_updated for Super), the head sprites of
activity_jackpot_list, the progress awards (activity_jackpot_award, `complete` = Super energy spent) and the misc
activity_jackpot_* values (energy start/cd/add/limit, bets, draw cost, Super unlock). Output data/jackpot.json + web/assets/jackpot/."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/jackpot'; OUT.mkdir(parents=True, exist_ok=True)
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def misc(key):
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', misc_text)
    return json.loads(m.group(1))


machine = [{'id': int(r['id']), 'pos': [r['position_1'], r['position_2'], r['position_3']], 'weight': int(r['weight']),
            'basic': r['awards'], 'super': r['awards_updated']} for r in sorted(read_table('activity_jackpot_machine').values(), key=lambda r: int(r['id']))]
lst = read_table('activity_jackpot_list')
heads = {i: {'basic': lst[str(i)]['use_pic'].replace('_png', ''), 'super': lst[str(i)]['updated_use_pic'].replace('_png', '')} for i in (1, 2, 3)}
awards = [{'need': int(r['complete']), 'awards': r['awards']} for r in sorted(read_table('activity_jackpot_award').values(), key=lambda r: int(r['id']))]
keys = ('activity_jackpot_energy_initial', 'activity_jackpot_energy_cd', 'activity_jackpot_energy_add', 'activity_jackpot_energy_limit',
        'activity_jackpot_energy_bet_num', 'activity_jackpot_draw', 'activity_jackpot_unlock', 'activity_jackpot_exchange_item', 'activity_jackpot_transfer')
out = {'machine': machine, 'heads': heads, 'awards': awards, 'misc': {k: misc(k) for k in keys}}
db = sqlite3.connect(DEC / 'data/en_en.db')
out['text'] = dict(db.execute("select name, translation from translation_en_en where name like 'ACTIVITY_JACKPOT%'"))
(ROOT / 'data/jackpot.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
n = 0
names = ['jackpot_machine', 'jackpot_senior_machine', 'jackpot_normal_btn_up', 'jackpot_normal_btn_down', 'jackpot_senior_btn_up', 'jackpot_senior_btn_down',
         'jackpot_normal_start_btn_up', 'jackpot_normal_start_btn_down', 'jackpot_senior_start_btn_up', 'jackpot_senior_start_btn_down', 'jackpot_energy_btn',
         'jackpot_energy_icon', 'jackpot_bg07', 'jackpot_res', 'jackpot_res2', 'jackpot_score', 'jackpot_normal_en_en', 'jackpot_senior_en_en', 'jackpot_start_en_en',
         'jackpot_start2_en_en', 'jackpot_line', 'jackpot_text_x2', 'jackpot_text_x3']
for h in heads.values():
    for v in h.values(): names += [v, v + '_vague']
for name in names:
    p = CUT / f'{name}.png'
    if p.exists(): shutil.copy2(p, OUT / p.name); n += 1
    else: print('missing', name)
print(len(machine), 'rows', len(awards), 'awards', n, 'sprites', out['misc'])
