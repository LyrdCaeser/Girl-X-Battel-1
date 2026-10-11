"""Alchemy / Midas v2 (models/Midas.lua, MidasWindow): midas.gold_new by player level, midas_buy_coin (cost and multiple
per daily purchase), vip midas_buy_times / extra_midas, MIDAS_* texts and midas_* sprites. Output data/midas.json."""
import json, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
v = read_table('vip')
out = {'gold': {k: r['gold_new'] for k, r in read_table('midas').items()},
       'buy': sorted(read_table('midas_buy_coin').values(), key=lambda r: r['id']),
       'vip': {k: {'times': int(r.get('midas_buy_times') or 0), 'extra': float(r.get('extra_midas') or 0)} for k, r in v.items()}}
db = sqlite3.connect(DEC / 'data/en_en.db')
out['text'] = dict(db.execute("select name, translation from translation_en_en where name like 'MIDAS%'"))
(ROOT / 'data/midas.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
OUT = ROOT / 'web/assets/midas'; OUT.mkdir(parents=True, exist_ok=True)
for p in (Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)').glob('midas_*.png'):
    shutil.copy2(p, OUT / p.name)
print(len(out['gold']), out['vip']['0'])
