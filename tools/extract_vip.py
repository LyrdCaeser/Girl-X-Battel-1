"""VIP table (data/tables/vip.lua): need_exp (cumulative VIP EXP per level) and the perks the local rebuild already
reads (idle bonus, Midas, Internship, Excursion, roster cap, Quiz buys, battle speed, Slots/High Stakes gates).
Output data/vip.json. VIP EXP itself comes from achievements (LOCAL-050), not from this table."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_acquisition import read_table
ROOT = Path(__file__).resolve().parents[1]
KEYS = ('need_exp', 'extra_output', 'extra_midas', 'midas_buy_times', 'partners_limit', 'pub_mission_num',
        'quiz_buy_times', 'battle_speed', 'travel_buy_time_limit', 'gamble', 'gamble_up', 'auto_transfer', 'login_double')
rows = read_table('vip')
out = {'levels': [{'level': int(k), **{n: (float(r[n]) if n in ('extra_output', 'extra_midas') else int(r.get(n) or 0)) for n in KEYS}}
                  for k, r in sorted(rows.items(), key=lambda kv: int(kv[0]))]}
(ROOT / 'data/vip.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
print(len(out['levels']), out['levels'][3])
