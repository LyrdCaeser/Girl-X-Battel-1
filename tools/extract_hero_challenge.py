"""Character Challenge, Normal and Puzzle modes (models/HeroChallenge.lua, HeroChallengeWindow /
HeroChallengeFightAwardWindow): partner_challenge (12 forts × 10 stages), partner_challenge_type, partner_challenge_box
(girl pools), partner_challenge_buff (blessings = god_skills), misc challenge_*, function 31 (unlock) and the English
texts. Output data/hero_challenge.json + web/assets/hero-challenge/. Sources in ~/Downloads/Decomp files are read only."""
import json, re, shutil, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
DEC = Path.home() / 'Downloads/Decomp files'
CUT = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)'
misc_text = (DEC / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def misc(key):
    m = re.search(r'\t' + key + r' = \{\n\t\t"' + key + r'",\n\t\t([^\n]+?),?\n', misc_text)
    return json.loads(m.group(1))


out = {
    'misc': {k: misc(k) for k in ('challenge_voucher_init', 'challenge_voucher_max', 'challenge_voucher_cd', 'partner_challenge_cost',
                                   'challenge_random_pet', 'challenge_pet_lv', 'challenge_pet_skill', 'challenge_reset_cost')},
    'unlock': read_table('function')['31'],
    'types': read_table('partner_challenge_type'),
    'stages': sorted(read_table('partner_challenge').values(), key=lambda r: int(r['id'])),
    'boxes': sorted(read_table('partner_challenge_box').values(), key=lambda r: int(r['id'])),
    'buffs': sorted(read_table('partner_challenge_buff').values(), key=lambda r: int(r['id'])),
}
db = sqlite3.connect(DEC / 'data/en_en.db')
out['stage_text'] = {str(r[0]): {'fort': r[1], 'name': r[3], 'desc': r[4]} for r in db.execute('select * from partner_challenge_text_en_en')}
out['buff_text'] = {str(r[0]): {'name': r[1], 'desc': r[2]} for r in db.execute('select * from partner_challenge_buff_text_en_en')}
out['text'] = dict(db.execute("select name, translation from translation_en_en where name like 'HERO_CHALLENGE%'"))
pets = read_table('pet')
out['pets'] = {str(p): {'id': int(p), 'max_grade': int(pets[str(p)].get('max_grade') or pets[str(p)].get('grade_max') or 1)} for p in str(out['misc']['challenge_random_pet']).split('|') if str(p) in pets}
(ROOT / 'data/hero_challenge.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))

OUT = ROOT / 'web/assets/hero-challenge'; OUT.mkdir(parents=True, exist_ok=True)
for p in list(CUT.glob('btn_h_challenge_*.png')) + list(CUT.glob('hero_challenge_*.png')) + list(CUT.glob('h_challenge_*.png')) + list(CUT.glob('blessing_icon_*.png')) + list(CUT.glob('icon_55*.png')):
    if not re.search(r'_(de_de|fr_fr|ja_jp|ko_kr|zh_cn|zh_tw)\.png$', p.name) and 'ios_test' not in p.name:
        shutil.copy2(p, OUT / p.name)
print(len(out['stages']), len(out['boxes']), len(out['buffs']), out['pets'], out['unlock']['open_value'], len(list(OUT.iterdir())))
