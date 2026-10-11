"""Junior Varsity arena data: arena_robot, arena_score, arena_match, arena_battle_award, arena_rank_award and the
misc arena keys (Lua sources). Output data/arena.json + the window art in web/assets/arena/."""
import json, re, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
HOT = DEC / 'unity/Assets/hotres'
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')
misc = {}
for key in ('arena_teach_num', 'arena_default_point', 'arena_ticket_free', 'arena_ticket_cost', 'arena_season_time', 'arena_init_score',
            'arena_free_times', 'daily_mail_awards_arena', 'arena_robot_min_score', 'arena_robot_add_score'):
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', misc_text)
    misc[key] = json.loads(m.group(1)) if m else None
out = {'misc': misc}
for n in ('arena_robot', 'arena_score', 'arena_match', 'arena_battle_award', 'arena_rank_award'):
    out[n] = sorted(read_table(n).values(), key=lambda r: int(r['id']))
drop = json.loads((ROOT / 'data/dropbox.json').read_text())
boxes = {int(r['dropbox_id']) for r in out['arena_battle_award']}
out['dropbox'] = [r for r in drop.values() if int(r['dropbox_id']) in boxes]
(ROOT / 'data/arena.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
OUT = ROOT / 'web/assets/arena'; OUT.mkdir(parents=True, exist_ok=True)
for s in ['arena_bg', 'arena_btn_bg', 'arena_decoration', 'arena_defence', 'arena_record', 'arena_award_s', 'arena_title_en_en', 'arena_label_en_en',
          'arena_fight1', 'arena_fight2', 'arena_rank_bg', 'arena_sword', 'arena_lose', 'force_icon', 'shop', 'help_2', 'blue_btn_65_65', 'white_btn_65_65', 'title_line', '9gongge16', 'rank_icon01', 'rank_icon02', 'rank_icon03', 'arena_bg_rank1', 'arena_bg_rank2', 'arena_bg_rank3', 'arena_bg_rank4', 'icon_34', 'icon_16', 'icon_34_small', 'icon_16_small',
          'arena_title', 'arena_icon_record', 'arena_icon_award', 'arena_icon_rank', 'arena_icon_formation', 'arena_icon_shop', 'arena_icon_help']:
    p = CUT / f'{s}.png'
    if p.exists():
        shutil.copy2(p, OUT / p.name)
for f in list((HOT / 'textures').rglob('arena_bg*.png')) + list((HOT / 'textures').rglob('arena_scene*.png')):
    shutil.copy2(f, OUT / f.name)
print(misc, len(out['dropbox']), sorted(p.name for p in OUT.iterdir()))
