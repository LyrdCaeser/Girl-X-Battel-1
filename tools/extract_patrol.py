"""Patrol (models/Dungeon.lua, DungeonWindow.lua): dungeon (600 stages), dungeon_battle (random battle pools),
dungeon_drug (Rice Balls / Stationery), dungeon_shop (merchant), misc dungeon_top, function 19 (unlock), the chest
dropboxes, the effect/buff rows the Stationery use and the English strings. Output data/patrol.json + web/assets/patrol/.
Sources in ~/Downloads/Decomp files are read only."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
HOT = DEC / 'unity/Assets/hotres'


def misc(key):
    text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', text)
    return json.loads(m.group(1))


def rows(name):
    return sorted(read_table(name).values(), key=lambda r: int(r['id']))


out = {'top': int(misc('dungeon_top')), 'unlock': read_table('function')['19']}
for n in ('dungeon', 'dungeon_battle', 'dungeon_drug', 'dungeon_shop'):
    out[n] = rows(n)
drop = json.loads((ROOT / 'data/dropbox.json').read_text())
boxes = {int(r['dropbox_id']) for r in out['dungeon']}
out['dropbox'] = [r for r in drop.values() if int(r['dropbox_id']) in boxes]
# Stationery effects (type 1): effect rows live in effect/effect1/effect2; the UI shows num / buff.factor * 100 per unit.
want = {str(d['effect']) for d in out['dungeon_drug'] if int(d['type']) == 1}
effects = {}
for part in ('effect', 'effect1', 'effect2'):
    try:
        effects.update({k: v for k, v in read_table(part).items() if k in want})
    except (AssertionError, FileNotFoundError):
        pass
# buff.lua rows are keyed by buff name (atkP, crit…); column 16 is the display factor.
btext = (DEC / 'lua/data/tables/buff.lua').read_text(encoding='utf-8-sig').split('table.rows =', 1)[1]
factor = {}
for name, block in re.findall(r'\n\t\[?"?(\w+)"?\]? = \{(.*?)\n\t\}', btext, re.S):
    vals = [v.strip() for v in block.strip().split(',\n')]
    factor[name] = json.loads(vals[15]) if len(vals) > 15 and vals[15] not in ('""', '') else 1
out['stationery'] = {k: {'buff': e['buff'], 'num': e['num'], 'factor': factor.get(e['buff'], 1)} for k, e in effects.items()}
db = sqlite3.connect(DEC / 'data/en_en.db')
out['drug_text'] = {str(i): {'name': n, 'desc': d.replace('%%', '%')} for i, n, d in db.execute('select * from dungeon_drug_text_en_en')}
out['text'] = dict(db.execute("select name, translation from translation_en_en where name like 'DUNGEON%'"))
(ROOT / 'data/patrol.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))

OUT = ROOT / 'web/assets/patrol'; OUT.mkdir(parents=True, exist_ok=True)
for p in CUT.glob('dungeon_*.png'):
    if not re.search(r'_(de_de|fr_fr|ja_jp|ko_kr|zh_cn|zh_tw)\.png$', p.name):
        shutil.copy2(p, OUT / p.name)
for p in [CUT / 'btn_dungeon_shop.png', HOT / 'textures/scenes_web/dungeon_bg.png'] + [CUT / f'img_group{i}.png' for i in range(1, 8)]:
    if p.exists():
        shutil.copy2(p, OUT / p.name)
print(out['top'], len(out['dungeon']), len(out['dungeon_battle']), len(out['dropbox']), out['stationery'], sorted(x.name for x in OUT.iterdir())[:8])

# Original Spine effects of DungeonWindow: enemy/hero appear, merchant portal + merchants, chest open.
from extract_slots_dealers import spine
SP = HOT / 'spine/dungeon_web'
for name in ('difangchuchang', 'chuchangtongyong', 'chuansongmen', 'baoxiang_dakai', 'zhanghongpifu', 'shengdanxueqiao', 'mizhubaozang'):
    if (SP / name).exists():
        spine(SP / name, ROOT / 'web/assets/spine' / name)
        print(name, list(json.loads((ROOT / 'web/assets/spine' / name / 'model.json').read_text())['animations']))
