"""Dorm resource output (HouseComfortWindow.lua): house_award.lua rows (comfort threshold → award per HANG_AWARD_TIME = 5 s,
const.lua) and misc hang_up_time_max (12 h cap). Output data/house_award.json. Sources are read only."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
T = Path.home() / 'Downloads/Decomp files/lua/data/tables'
text = (T / 'house_award.lua').read_text(encoding='utf-8-sig')
rows = [{'id': int(i), 'comfort': int(c), 'award': a} for i, c, a in re.findall(r'\["(\d+)"\] = \{\s*\d+,\s*(\d+),\s*"([^"]*)"', text)]
misc = (T / 'misc.lua').read_text(encoding='utf-8-sig')
cap = int(re.search(r'\thang_up_time_max = \{\s*"hang_up_time_max",\s*(\d+)', misc).group(1))
(ROOT / 'data/house_award.json').write_text(json.dumps({'rows': rows, 'tick': 5, 'max': cap}, indent=1))
print(len(rows), 'rows, cap', cap)
