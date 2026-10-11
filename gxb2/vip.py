"""VIP by achievements (LOCAL-050). The original VIP EXP came from recharges; offline it is earned by playing.

VIP EXP ("popularity") is a pure function of the save, so it can't be double-counted and existing saves get it
retroactively. Sources and weights (LOCAL, adjustable in one place):
  campaign  12 per stage reached (max_stage)      level  6 per player level above 1
  tasks     10 per daily task / 25 per trophy claimed (missions.action keeps the running total)
  login      5 per day played                     lab     8 per Guild Lab technology level
  collection 1 per Yume Collection Point (trophy), WAVE-049 · user's idea: the trophies feed VIP
The level thresholds and perks are the original vip table (data/vip.json); nothing there is rebalanced.
"""
import json
from pathlib import Path

LEVELS = json.loads((Path(__file__).resolve().parents[1] / 'data/vip.json').read_text())['levels']
WEIGHTS = {'campaign': 12, 'level': 6, 'login': 5, 'lab': 8, 'collection': 1}  # tasks: 10 / 25 live in missions.action
MAX_LEVEL = len(LEVELS) - 1
_PLAYER_EXP = sorted((int(r['all_exp']), int(k)) for k, r in json.loads((Path(__file__).resolve().parents[1] / 'data/exp_player.json').read_text()).items())


def player_level(state):
    exp = int((state.get('items') or {}).get('3', 0))
    return max(lv for need, lv in _PLAYER_EXP if need <= exp)


def breakdown(state):
    """VIP EXP per source."""
    totals = (state.get('missions') or {}).get('totals') or {}
    lab = sum(int(v) for v in ((state.get('guild_lab') or {}).get('levels') or {}).values() if str(v).lstrip('-').isdigit())
    return {'campaign': int(state.get('max_stage', 0)) * WEIGHTS['campaign'],
            'level': max(0, player_level(state) - 1) * WEIGHTS['level'],
            'tasks': int(totals.get('popularity', 0)),  # missions.action adds 10 per daily task / 25 per trophy
            'login': int(totals.get('login', 0)) * WEIGHTS['login'],
            'lab': lab * WEIGHTS['lab'],
            'collection': collection_points(state) * WEIGHTS['collection']}


def collection_points(state):
    try:
        from . import collection
        return collection.points(state)
    except Exception:  # a save without the collection data still gets the other sources
        return 0


def exp(state):
    return sum(breakdown(state).values())


def level_for(total):
    return max(row['level'] for row in LEVELS if row['need_exp'] <= total)


def info(state, developer=False):
    parts = breakdown(state); total = sum(parts.values())
    lv = MAX_LEVEL if developer else level_for(total)
    nxt = LEVELS[lv + 1] if lv < MAX_LEVEL else None
    return {'level': lv, 'exp': total, 'base': LEVELS[lv]['need_exp'], 'next': nxt['need_exp'] if nxt else None,
            'sources': parts, 'weights': WEIGHTS, 'perks': LEVELS[lv], 'next_perks': nxt}


def apply(state, developer=False):
    """Expose the derived level where the other systems already look (state['vip'] / state['vip_level'])."""
    lv = info(state, developer)['level']
    state['vip'] = state['vip_level'] = lv
    return lv

