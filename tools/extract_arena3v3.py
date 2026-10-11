"""Arena 3v3 data (Arena3v3Window, models/Arena3v3.lua): arena_battle_award_3v3 (reward cards by level → dropbox),
arena_rank_award_3v3 / arena_rank_new_award_3v3 (season awards by rank), misc arena_3v3_open_awards / arena_3v3_ticket_cost
and the ARENA_3V3_HELP rules. Output data/arena3v3.json. Sources in ~/Downloads are read only."""
import json, re, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')
misc = {}
for key in ('arena_3v3_open_awards', 'arena_3v3_ticket_cost'):
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', misc_text)
    misc[key] = json.loads(m.group(1)) if m else None
out = {'misc': misc}
for n in ('arena_battle_award_3v3', 'arena_rank_award_3v3', 'arena_rank_new_award_3v3'):
    out[n] = sorted(read_table(n).values(), key=lambda r: int(r['id']))
drop = json.loads((ROOT / 'data/dropbox.json').read_text())
boxes = {int(r['dropbox_id']) for r in out['arena_battle_award_3v3']}
out['dropbox'] = [r for r in drop.values() if int(r['dropbox_id']) in boxes]
db = sqlite3.connect(DEC / 'data/en_en.db')
out['text'] = dict(db.execute("select name, translation from translation_en_en where name like 'ARENA_3V3%' or name like 'ARENA3V3%'"))
(ROOT / 'data/arena3v3.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
print(misc, {k: len(v) for k, v in out.items() if isinstance(v, list)}, list(out['text'])[:8])
# window art (Arena3v3Window: scene, title, team badges T1-T3, win / lost banners, entrance button)
import shutil
S = Path.home() / 'Downloads/Decompiled'
OUT = ROOT / 'web/assets/arena'
for src in [S / 'Images (backgrounds)/scenes/arena_3v3_scene.png'] + [S / 'Sprites (atlases, cut)' / f'{n}.png' for n in (
        'arena3v3_title_en_en', 'arena_3v3_t1', 'arena_3v3_t2', 'arena_3v3_t3', 'arena_3v3_team_bg', 'btn_arena_3v3',
        'arena_3v3_win_en_en', 'arena_3v3_lost_en_en')]:
    if src.exists(): shutil.copy(src, OUT / src.name)
