"""Magic Card (activity 134 = ActivityIceSecret re-skinned; capture 2026-09-29-fb/53, 112) and Magician's Assistant
(activity_ice_secret_mission): the reward table (activity_ice_secret_awards: 24 normal cards of level 1, Ultimate Rewards
type 1 unlocked at round `level`, `limit` uses), the Magic Wand cost (misc activity_ice_secret_hammer 180#15), the
Ultimate Reward weights per flip (misc activity_ice_secret_weight), missions + texts and sprites.
Output data/magic_card.json + web/assets/magic-card/. Sources in ~/Downloads are read only."""
import json, re, shutil, sqlite3
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
T = DEC / 'lua/data/tables'
SPR = Path.home() / 'Downloads/Decompiled'
CUT = SPR / 'Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/magic-card'; OUT.mkdir(parents=True, exist_ok=True)


def lua_table(path):
    text = path.read_text(encoding='utf-8-sig')
    keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', text.split('table.keys = {', 1)[1].split('}', 1)[0])}
    rows = {}
    for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\}', text.split('table.rows = {', 1)[1], re.S):
        vals = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p) for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
        rows[m.group(1)] = {k: vals[i] for k, i in keys.items() if i < len(vals)}
    return rows


misc = (T / 'misc.lua').read_text(encoding='utf-8-sig')
g = lambda k: re.search(r'\t' + k + r' = \{\s*"' + k + r'",\s*"([^"]*)"', misc).group(1)
db = sqlite3.connect(DEC / 'data/en_en.db')
out = {'awards': lua_table(T / 'activity_ice_secret_awards.lua'), 'missions': lua_table(T / 'activity_ice_secret_mission.lua'),
       'mission_text': {str(r[0]): r[1] for r in db.execute('select * from activity_ice_secret_mission_text_en_en')},
       'weights': [int(x) for x in g('activity_ice_secret_weight').split('|')], 'hammer': int(g('activity_ice_secret_hammer').split('#')[1]),
       'text': dict(db.execute("select name, translation from translation_en_en where name like 'ACTIVITY_ICE_SECRET%'"))}
(ROOT / 'data/magic_card.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
n = 0
for p in list(CUT.glob('ice_secret*.png')) + list(CUT.glob('activity_ice_secret*.png')) + [CUT / 'icon_180.png', CUT / 'btn_start.png', CUT / 'check_white_btn.png']:
    if 'boss' in p.stem or p.stem.endswith(('_de_de', '_fr_fr', '_ja_jp', '_ko_kr', '_zh_tw')) or not p.exists(): continue
    shutil.copy2(p, OUT / p.name); n += 1
shutil.copy2(SPR / 'Images (other)/activity_text/ice_secret_logo_en_en.png', OUT / 'ice_secret_logo_en_en.png')
Image.open(SPR / 'Images (backgrounds)/scenes/activity_ice_secret_bg1.png').convert('RGB').save(OUT / 'activity_ice_secret_bg1.webp', 'WEBP', quality=82)
print(len(out['awards']), 'awards,', len(out['missions']), 'missions,', n + 2, 'sprites')
