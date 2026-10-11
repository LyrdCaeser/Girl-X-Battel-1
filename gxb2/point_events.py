"""Point-reward events: Capsule Points (13, activity_gacha), Enroll Exam (16, activity_tree) and Slot Points
(20, activity_gamble). Views: SummonGiftBag.lua, ProphetSummonGiftBag.lua, WishingPoolGiftBag.lua.

activity.round = "max|times": points loop up to `max`; each full loop counts one completion, up to `times`.
The original mailed each tier reward when its points were reached; locally the reward goes straight to the bag.
Points per action: Enroll = 1 per Seal used (PROPHET_SUMMON_GIFTBAG_TEXT01), Slot = 1 per pull
(WISHING_POOL_GIFTBAG_TEXT01). Capsule Points counts Adv. Capsule draws; the per-draw value was server-side, here 10.
"""
from __future__ import annotations
import copy, json
from . import clock
from pathlib import Path

CONFIG = json.loads((Path(__file__).resolve().parents[1] / 'data/point_events.json').read_text())


def pairs(text):
    out = {}
    for part in str(text or '').split('|'):
        if '#' in part:
            k, n = part.split('#')[:2]
            out[k] = out.get(k, 0) + int(n)
    return out


def current(state, aid, now=None):
    """Pure view. Legacy progress is bound to the first observed period on mutation.
    Never reopen an older week after clock rollback; retain the last observed period.
    """
    old=copy.deepcopy((state.get('point_events') or {}).get(str(aid), {}))
    period=clock.week(now)
    if old.get('period') and old['period'] < period:
        old={'history': (old.get('history', [])+[{'period':old['period'],'point':old['point'],'rounds':old['rounds']}])[-8:]}
    old.setdefault('point',0);old.setdefault('rounds',0);old.setdefault('got',[])
    old['period']=max(old.get('period',period),period)
    return old


def saved(state, aid, now=None):
    ev=current(state,aid,now)
    state.setdefault('point_events',{})[str(aid)]=ev
    return ev


def add(state, source, amount, now=None):
    """Add points to every event fed by `source`; returns the rewards granted."""
    granted = {}
    for aid, cfg in CONFIG.items():
        if cfg['source'] != source or amount <= 0:
            continue
        ev = saved(state, aid, now)
        top, times = cfg['round']
        left = amount * cfg['per']
        while left > 0 and ev['rounds'] < times:
            step = min(left, top - ev['point'])
            ev['point'] += step
            left -= step
            for i, tier in enumerate(cfg['table']):
                if i not in ev['got'] and ev['point'] >= tier['point']:
                    ev['got'].append(i)
                    for k, n in pairs(tier['awards']).items():
                        state['items'][k] = int(state['items'].get(k, 0)) + n
                        granted[k] = granted.get(k, 0) + n
            if ev['point'] >= top:
                ev['rounds'] += 1
                if ev['rounds'] < times:
                    ev['point'], ev['got'] = 0, []
    return granted


def snapshot(state, now=None):
    out = {}
    for aid, cfg in CONFIG.items():
        ev = current(state, aid, now)
        done = ev['rounds'] >= cfg['round'][1]
        out[aid] = {'period': ev['period'], 'ends_at': clock.week_end(ev['period']), 'point': cfg['round'][0] if done else ev['point'], 'rounds': ev['rounds'], 'times': cfg['round'][1],
                    'done': done, 'tiers': [{'point': t['point'], 'awards': t['awards'], 'got': done or i in ev['got']}
                                            for i, t in enumerate(cfg['table'])]}
    return out
