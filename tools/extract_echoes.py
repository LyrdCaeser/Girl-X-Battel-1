"""Echoes of Time (models/TimeCloisterModel.lua, TIME_CLOISTER_HELP01-05): worlds (time_cloister), cards and card boxes,
Planetarium technologies (time_cloister_tec), stages (time_cloister_battle), achievements (time_cloister_ach / _type),
observation grades (time_cloister_award), misc time_cloister_*, texts and window art. Output data/echoes.json."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
TEX = DEC / 'unity/Assets/hotres/textures'
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def misc(key):
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', misc_text)
    return json.loads(m.group(1))


rows = lambda n: sorted(read_table(n).values(), key=lambda r: int(r['id']))
out = {'misc': {k: misc(k) for k in ('time_cloister_energy_time', 'time_cloister_card_time', 'time_cloister_time_accelerata', 'time_cloister_clear',
                                      'time_cloister_fight_energy_init', 'time_cloister_fight_energy_max', 'time_cloister_fight_energy_cd',
                                      'time_cloister_fight_energy_cost')},
       'worlds': [r for r in rows('time_cloister') if r['card_box']], 'cards': {str(r['id']): r for r in rows('time_cloister_card')},
       'boxes': rows('time_cloister_card_box'), 'tec': rows('time_cloister_tec'), 'stages': rows('time_cloister_battle'),
       'ach': {str(r['id']): r for r in rows('time_cloister_ach')}, 'ach_type': rows('time_cloister_ach_type'), 'grades': rows('time_cloister_award')}
db = sqlite3.connect(DEC / 'data/en_en.db')
q = lambda sql: list(db.execute(sql))
out['world_text'] = {str(r[0]): {'name': r[1], 'desc': r[2]} for r in q('select * from time_cloister_text_en_en')}
out['tec_text'] = {str(r[0]): {'name': r[1], 'desc': r[2], 'unlock': r[3]} for r in q('select * from time_cloister_tec_text_en_en')}
out['ach_text'] = {str(r[0]): r[1] for r in q('select * from time_cloister_ach_text_en_en')}
cols = [r[1] for r in q('pragma table_info(time_cloister_card_text_en_en)')]
out['card_text'] = {str(r[0]): dict(zip(cols[1:], r[1:])) for r in q('select * from time_cloister_card_text_en_en')}
out['text'] = dict(q("select name, translation from translation_en_en where name like 'TIME_CLOISTER%'"))
(ROOT / 'data/echoes.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
OUT = ROOT / 'web/assets/echoes'; OUT.mkdir(parents=True, exist_ok=True)
for p in list(CUT.glob('time_cloister_*.png')) + [CUT / f'icon_{i}.png' for i in (287, 288, 289, 307, 337)] + [CUT / 'mission_awarded_en_en.png']:
    if p.exists() and not re.search(r'_(de_de|fr_fr|ja_jp|ko_kr|zh_cn|zh_tw)\.png$', p.name):
        shutil.copy2(p, OUT / p.name)
for p in TEX.rglob('time_cloister*.png'):
    if not re.search(r'_(de_de|fr_fr|ja_jp|ko_kr|zh_cn|zh_tw)\.png$', p.name):
        shutil.copy2(p, OUT / p.name)
print(len(out['worlds']), len(out['cards']), len(out['tec']), len(out['stages']), len(out['ach_type']), cols, len(list(OUT.iterdir())))
