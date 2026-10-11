"""Offline clock contract (LOCAL-057/058). Epoch seconds are injectable; the original server calendar is unknown.

Every day and week boundary follows the player's own machine time zone: a day ends at local midnight and weeks run from
local Monday 00:00 (ISO weeks). `Engine.now()` is monotonic, so these boundaries can't be replayed by rewinding the
system clock. Fixed absolute schedules (season start epochs from the client tables) are left as they are.
"""
from datetime import date, datetime, timedelta
import time

MONDAY0 = date(1970, 1, 5)   # first Monday after the epoch


def epoch(value=None):
    return int(time.time() if value is None else value)


def day(value=None, local=True):
    """Local calendar day 'YYYY-MM-DD' (`local` kept for old callers)."""
    return time.strftime('%Y-%m-%d', time.localtime(epoch(value)))


def week(value=None):
    y, w, _ = datetime.fromtimestamp(epoch(value)).isocalendar()
    return f'{y:04d}-W{w:02d}'


def week_end(period):
    """Epoch of the next local Monday 00:00 after ISO week `period`."""
    y, w = period.split('-W')
    monday = datetime.fromisocalendar(int(y), int(w), 1) + timedelta(days=7)
    return int(time.mktime(monday.timetuple()))


def week_index(value=None):
    """Local weeks elapsed since 1970-01-05 (Monday); changes at local Monday 00:00."""
    return (datetime.fromtimestamp(epoch(value)).date() - MONDAY0).days // 7


def week_start(index):
    """Epoch of local Monday 00:00 that opens week `index`."""
    return int(time.mktime((datetime.combine(MONDAY0, datetime.min.time()) + timedelta(days=7 * index)).timetuple()))
