"""Old Campus Exploration (models/OldSchool.lua, OldSchoolMainWindow / ActivityExploreCampusFightWindow / OLD_SCHOOL_HELP1):
old_building_a / _b (levels → stages, level rewards) for the alternating seasons, old_building_stage (battles, base
point), old_building_buff_new (Exploration Plans: point, skill, type, group), old_building_{a,b}_award1 (score rewards),
misc old_building_*, function 39 (unlock), English texts and the window art. Output data/old_campus.json."""
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
out = {'misc': {k: misc(k) for k in ('old_building_time_interval', 'old_building_start_time', 'old_building_floor11_point', 'old_building_buff_num', 'old_building_buff_num_2', 'old_building_buff_lock_1', 'old_building_buff_lock_2', 'old_building_buff_lock_3', 'old_building_buff_lock_4')},
       'unlock': read_table('function')['39'], 'levels': {'a': rows('old_building_a'), 'b': rows('old_building_b')},
       'score_awards': {'a': rows('old_building_a_award1'), 'b': rows('old_building_b_award1')},
       'stages': {str(r['id']): r for r in rows('old_building_stage')}, 'plans': rows('old_building_buff_new')}
db = sqlite3.connect(DEC / 'data/en_en.db')
out['plan_text'] = {str(i): {'name': n, 'desc': d} for i, n, d in db.execute('select * from old_building_buff_text_en_en')}
out['text'] = dict(db.execute("select name, translation from translation_en_en where name like 'OLD_SCHOOL%' or name like 'OLD_BUILDING%'"))
(ROOT / 'data/old_campus.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
OUT = ROOT / 'web/assets/old-campus'; OUT.mkdir(parents=True, exist_ok=True)
for p in list(CUT.glob('fangan_*.png')) + list((TEX / 'old_school_web').glob('*.png')) + [TEX / 'activity_text_web/old_building_logo_en_en.png', TEX / 'activity_text_web/old_school_enter_active_en_en.png']:
    if p.exists():
        shutil.copy2(p, OUT / p.name)
print(len(out['stages']), len(out['plans']), out['unlock']['open_value'], len(list(OUT.iterdir())))
