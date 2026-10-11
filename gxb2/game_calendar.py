"""Game calendar: the periods every timed system hangs from and the schedule of the limited events.

The original server opened and closed each limited event (ActivityWindow shows only the ones the server sent, with their
end time) and ran the daily / weekly / monthly resets. LOCAL (LOCAL-082): the calendar is the player's local one.
- Periods: day (local midnight), week (Monday 00:00 → next Monday), month (the 1st → next 1st).
- Limited events rotate on it instead of being all open for ever: the exchange / mission events of the generic kit are
  WEEKLY (6 open, each stays two weeks, half change every Monday); the events with their own minigame (Jackpot, Blind Box,
  Jigsaw, Firework…) are MONTHLY (4 open, each stays two months, half change on the 1st). The order
  is a fixed shuffle of the playable events, so the schedule is the same on every machine and can be listed in advance.
- Daily Login (1) and the 7-day newcomer event (116) are always open. An event that rotates out keeps its progress.
The schedule only decides what the Events window offers; it does not delete anything.
"""
from __future__ import annotations
import datetime, json, random, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALWAYS = (1, 116)
# playable events with their own module (web/events.js WORKING) + every event of the generic kit (data/activity_kit.json)
OWN = (196, 37, 189, 13, 16, 20, 309, 140, 134, 331, 292, 64, 338, 329, 330, 150)
WEEKLY_OPEN, WEEKLY_STEP = 6, 3
MONTHLY_OPEN, MONTHLY_STEP = 4, 2


def _catalog():
    acts = {int(a['id']): a for a in json.loads((ROOT / 'data/events.json').read_text()).get('activities', [])}
    try:
        kit = json.loads((ROOT / 'data/activity_kit.json').read_text())
        kit_ids = [int(k) for k in (kit.get('events') or kit).keys() if str(k).isdigit()]
    except (OSError, ValueError):
        kit_ids = []
    ids = sorted({i for i in list(OWN) + kit_ids if i in acts and i not in ALWAYS})
    # none of the playable events sits in the catalogue's "Monthly Events" tab, so the split is by size: the events with
    # their own minigame (OWN) are the monthly ones, the exchange / mission events of the generic kit the weekly ones
    monthly = [i for i in ids if i in OWN or int(acts[i].get('type2') or 0) == 3]
    weekly = [i for i in ids if i not in monthly]
    random.Random(20260930).shuffle(weekly); random.Random(20261001).shuffle(monthly)
    return acts, weekly, monthly


ACTS, WEEKLY, MONTHLY = _catalog()


def local_midnight(now):
    t = time.localtime(now)
    return int(time.mktime((t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, 0, 0, -1)))


def periods(now):
    """day / week / month the moment `now` falls in: {'id', 'start', 'end'} with local boundaries."""
    d0 = local_midnight(now); day = datetime.date.fromtimestamp(d0)
    ts = lambda d: int(time.mktime((d.year, d.month, d.day, 0, 0, 0, 0, 0, -1)))
    monday = day - datetime.timedelta(days=day.weekday())
    first = day.replace(day=1); nxt = (first.replace(year=first.year + 1, month=1) if first.month == 12 else first.replace(month=first.month + 1))
    week_no = (monday - datetime.date(2024, 1, 1)).days // 7          # 2024-01-01 was a Monday
    month_no = (day.year - 2024) * 12 + day.month - 1
    return {'day': {'id': day.isoformat(), 'start': d0, 'end': ts(day + datetime.timedelta(days=1))},
            'week': {'id': week_no, 'start': ts(monday), 'end': ts(monday + datetime.timedelta(days=7))},
            'month': {'id': month_no, 'start': ts(first), 'end': ts(nxt)}}


def _window(order, n, size, step):
    """Events open in period n: a window of `size` over the shuffled order that advances `step` every period."""
    if not order: return []
    size = min(size, len(order))
    return [order[(n * step + k) % len(order)] for k in range(size)]


def _span(order, n, size, step, eid):
    """How many periods before / after n the event stays open (consecutive)."""
    back = 0
    while back < len(order) and eid in _window(order, n - back - 1, size, step): back += 1
    fwd = 0
    while fwd < len(order) and eid in _window(order, n + fwd + 1, size, step): fwd += 1
    return back, fwd


def schedule(now):
    p = periods(now); out, nxt = [], []
    week_len = 7 * 86400
    for eid in _window(WEEKLY, p['week']['id'], WEEKLY_OPEN, WEEKLY_STEP):
        b, f = _span(WEEKLY, p['week']['id'], WEEKLY_OPEN, WEEKLY_STEP, eid)
        out.append({'id': eid, 'kind': 'week', 'start': p['week']['start'] - b * week_len, 'end': p['week']['end'] + f * week_len})
    for eid in _window(WEEKLY, p['week']['id'] + 1, WEEKLY_OPEN, WEEKLY_STEP):
        if eid not in [e['id'] for e in out]: nxt.append({'id': eid, 'kind': 'week', 'start': p['week']['end']})
    cur = _window(MONTHLY, p['month']['id'], MONTHLY_OPEN, MONTHLY_STEP)
    for eid in cur:
        b, f = _span(MONTHLY, p['month']['id'], MONTHLY_OPEN, MONTHLY_STEP, eid)
        out.append({'id': eid, 'kind': 'month', 'start': _month_shift(p['month']['start'], -b), 'end': _month_shift(p['month']['end'], f)})
    for eid in _window(MONTHLY, p['month']['id'] + 1, MONTHLY_OPEN, MONTHLY_STEP):
        if eid not in cur: nxt.append({'id': eid, 'kind': 'month', 'start': p['month']['end']})
    name = lambda i: str(ACTS.get(i, {}).get('title') or i).replace('\n', ' ')
    for e in out + nxt: e['title'] = name(e['id'])
    return p, out, nxt


def _month_shift(ts, n):
    d = datetime.date.fromtimestamp(ts); m = d.year * 12 + d.month - 1 + n
    d2 = datetime.date(m // 12, m % 12 + 1, 1)
    return int(time.mktime((d2.year, d2.month, d2.day, 0, 0, 0, 0, 0, -1)))


def is_open(eid, now):
    eid = int(eid)
    if eid in ALWAYS or (eid not in WEEKLY and eid not in MONTHLY): return True
    return eid in [e['id'] for e in schedule(now)[1]]


def snapshot(now=None, resets=()):
    """`resets`: extra countdowns gathered by the engine ([{'key', 'label', 'at'}]: seasons, stores…)."""
    now = int(time.time()) if now is None else now
    p, cur, nxt = schedule(now)
    base = [{'key': 'day', 'label': 'Daily reset (Daily Tasks, free draws, Hearts)', 'at': p['day']['end']},
            {'key': 'week', 'label': 'Weekly reset (weekly tasks, stores, weekly events)', 'at': p['week']['end']},
            {'key': 'month', 'label': 'Monthly reset (Monthly Events)', 'at': p['month']['end']}]
    return {'now': now, 'periods': p, 'always': list(ALWAYS), 'events': cur, 'next': nxt,
            'scheduled': sorted(set(WEEKLY) | set(MONTHLY)),
            'resets': sorted(base + [r for r in resets if r.get('at', 0) > now], key=lambda r: r['at'])}
