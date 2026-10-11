"""House Exam (models/AcademyAssessment.lua, AcademyAssessmentWindow / DetailWindow2 / SweepWindow / BuyWindow).
Current version of the client tables (after school_practise_switch_time): school_practise_new2 (6 houses × 100 stages,
3 enemy variants per stage), school_practise_point_new2 (season score rewards), school_practise_ticket_buy
(Certificate prices), misc school_practise_*, function 35 (unlock) and the English strings. Output data/house_exam.json
+ web/assets/house-exam/. Sources in ~/Downloads/Decomp files are read only."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
TEX = DEC / 'unity/Assets/hotres/textures/academy_assessment_web'

misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def misc(key):
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', misc_text)
    return json.loads(m.group(1))


out = {
    'misc': {k: misc(k) for k in ('school_practise_ticket_default', 'school_practise_ticket_limit_up', 'school_practise_ticket_buy_limit',
                                   'school_practise_ticket02_buy', 'school_practise_ticket02_default_2', 'school_practise_season1_start_time',
                                   'school_practise_season_duration', 'school_practise_display_duration')},
    'unlock': read_table('function')['35'],
    'stages': sorted(read_table('school_practise_new2').values(), key=lambda r: int(r['id'])),
    'points': sorted(read_table('school_practise_point_new2').values(), key=lambda r: -int(r['point'])),
    'cert_cost': [r['cost'] for r in sorted(read_table('school_practise_ticket_buy').values(), key=lambda r: int(r['id']))],
}
db = sqlite3.connect(DEC / 'data/en_en.db')
out['text'] = dict(db.execute("select name, translation from translation_en_en where name like 'SCHOOL_PRACTICE%' or name like 'ACADEMY_ASSESSMENT%'"))
(ROOT / 'data/house_exam.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))

OUT = ROOT / 'web/assets/house-exam'; OUT.mkdir(parents=True, exist_ok=True)
names = ['academy_assessment_logo_en_en', 'academy_assessment_done_en_en', 'academy_assessment_lock', 'academy_assessment_award_bg',
         'academy_assessment_award_bg_first', 'academy_assessment_award_bg_lock', 'academy_assessment_right_bg_new', 'academy_assessment_title_bg_new',
         'icon_63', 'icon_63_small', 'icon_64', 'icon_64_small',
         # AcademyAssessmentWindow header / list item (capture 2026-09-29-k/01)
         'help_2', 'shop', 'btn_rank_2', 'btn_award', 'friend_btn_bg1', 'dress_show_score_icon', 'activity_popularity_vote_up'] + [f'boss_award_bg_{i}' for i in range(1, 9)]
for i in range(1, 7):
    names += [f'academy_assessment_text_{i}_en_en', f'btn_academy_assessment_{i}_new', f'academy_assessment_activity_icon_{i}', f'img_group{i}']
for n in names:
    if (CUT / f'{n}.png').exists():
        shutil.copy2(CUT / f'{n}.png', OUT / f'{n}.png')
for p in list(TEX.glob('academy_assessment_[1-6].png')) + [TEX / 'academy_assessment_bg.png']:
    shutil.copy2(p, OUT / p.name)
print(len(out['stages']), len(out['points']), out['unlock']['open_type'], out['unlock']['open_value'], len(list(OUT.iterdir())))
