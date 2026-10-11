"""Sanctuary (models/Trial.lua, TrialWindow / ActivityNewTrialFightAwardWindow / NewTrialBossInfoWindow): new_trial_stage
(Volcano Sanctum, boss 1) and new_trial_stage_sea (Deep Sea Sanctum, boss 2), new_trial_buff (+ English texts),
new_trial_boss_reward (damage tiers), new_trial_boss_scenes, misc trial_boss_levs, function for Sanctuary and the
window art. Output data/sanctuary.json + web/assets/sanctuary/. Sources read only."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
TEX = DEC / 'unity/Assets/hotres/textures'
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')
m = re.search(r'\ttrial_boss_levs = \{\n\t\t"trial_boss_levs",\n\t\t([^\n]+?),?\n', misc_text)
enums = (DEC / 'lua/app/common/enums.lua').read_text(encoding='utf-8-sig')
fid = int(re.search(r'xyd\.FunctionID = \{.*?\n\tTRIAL = (\d+)', enums, re.S).group(1))
out = {'boss_levs': [int(x) for x in json.loads(m.group(1)).split('|')], 'function_id': fid, 'unlock': read_table('function')[str(fid)],
       'stages': {'1': sorted(read_table('new_trial_stage').values(), key=lambda r: r['id']),
                  '2': sorted(read_table('new_trial_stage_sea').values(), key=lambda r: r['id'])},
       'buffs': sorted(read_table('new_trial_buff').values(), key=lambda r: r['id']),
       'boss_reward': sorted(read_table('new_trial_boss_reward').values(), key=lambda r: r['id']),
       'boss_scenes': sorted(read_table('new_trial_boss_scenes').values(), key=lambda r: r['id']),
       'offsets': sorted(read_table('new_trial_offset').values(), key=lambda r: r['id'])}
db = sqlite3.connect(DEC / 'data/en_en.db')
out['buff_text'] = {str(i): {'name': n, 'desc': d} for i, n, d in db.execute('select * from new_trial_buff_text_en_en')}
out['text'] = dict(db.execute("select name, translation from translation_en_en where name like 'NEW_TRIAL%' and name not like '%BATTLEPASS%'"))
(ROOT / 'data/sanctuary.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
OUT = ROOT / 'web/assets/sanctuary'; OUT.mkdir(parents=True, exist_ok=True)
icons = {b['icon'] for b in out['buffs']}
for p in list(CUT.glob('new_trial_*.png')) + list(CUT.glob('trial_*.png')) + [CUT / f'{i}.png' for i in icons]:
    if p.exists() and not re.search(r'_(de_de|fr_fr|ja_jp|ko_kr|zh_cn|zh_tw)\.png$', p.name):
        shutil.copy2(p, OUT / p.name)
for s in out['boss_scenes']:
    for key in ('stage_scene', 'stage_scene_detail', 'boss_image'):
        for p in TEX.rglob(f"{s[key]}.png"):
            shutil.copy2(p, OUT / p.name)
print(fid, out['unlock']['open_type'], out['unlock']['open_value'], out['boss_levs'], len(list(OUT.iterdir())))
