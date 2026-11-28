"""GM-only S4 trial keys, activated in the player's existing profile transaction.

The entitlement is UID-wide but never transferable. No new Neon tables or
migration. Trial playtime is counted only while S4 is globally open; the
72h-open/48h-locked world policy remains authoritative.
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from . import database

ROOT = Path(__file__).resolve().parents[1]
WORLD = 'S4'
KEY_HOURS = {
    '990051':24, '990052':48, '990053':72,
    '990054':96, '990055':120,
}
KEY_IDS = frozenset(KEY_HOURS)


def hours_for(item_id):
    return KEY_HOURS.get(str(item_id))


def _all_other_profiles(uid):
    """Read only the server-side profiles of this exact canonical UID."""
    uid = str(uid or '').strip()
    if not uid:
        return []
    if database.is_postgres():
        db = database.connect(ROOT/'state/live_service.sqlite3', 'live')
        try:
            rows = db.execute(
                "SELECT data FROM player_profiles WHERE uid=? AND server_id<>? AND server_id<>'S5'",
                (uid, WORLD)).fetchall()
            return [r['data'] for r in rows]
        finally:
            db.close()
    rows = []
    folder = ROOT/'state'/'players'/uid
    if folder.is_dir():
        for path in folder.glob('S*.sqlite3'):
            if path.stem.upper() in (WORLD, "S5"):
                continue
            try:
                with sqlite3.connect(f'file:{path}?mode=ro',uri=True) as db:
                    row = db.execute('SELECT data FROM profile WHERE id=1').fetchone()
                    if row:
                        rows.append(row[0])
            except (sqlite3.Error,OSError):
                continue
    return rows


def _expires_from(raw, uid):
    try:
        state = json.loads(raw) if isinstance(raw,str) else raw
        if not isinstance(state,dict) or state.get('uid') not in (None,uid):
            return 0
        if str(state.get('server_id') or '').upper() in (WORLD,'S5'):
            return 0
        return max(0,int(state.get('s4_trial_expires_at') or 0))
    except (ValueError,TypeError,KeyError):
        return 0


def expires_at(uid, state=None):
    uid=str(uid or '').strip()
    best=max((_expires_from(row,uid) for row in _all_other_profiles(uid)),default=0)
    if state and state.get('uid')==uid:
        best=max(best,_expires_from(state,uid))
    return best


def open_seconds_between(start,end,created_at=None):
    """Account for locked 48h segments; proof of duration is server-side."""
    from . import s4_exclusive
    start,end=int(start),int(end)
    total=0
    current=start
    loops=0
    while current<end and loops<128:
        period=s4_exclusive.cycle(now=current,created_at=created_at)
        edge=min(end,period['phase_end'])
        if edge<=current:
            break
        if period['phase']=='open':
            total+=edge-current
        current=edge
        loops+=1
    return total


def trial_end_at(start, hours, created_at=None):
    """Trial hours represent playable S4 hours, excluding S4 rest phases."""
    from . import s4_exclusive
    if int(hours) not in KEY_HOURS.values():
        raise ValueError('Thời lượng Chìa Khóa S4 không hợp lệ')
    remaining=int(hours)*3600
    current=int(start)
    for _ in range(12):
        period=s4_exclusive.cycle(now=current,created_at=created_at)
        if period['phase']!='open':
            current=period['phase_end']
            continue
        length=min(remaining,period['phase_end']-current)
        current+=length
        remaining-=length
        if remaining<=0:
            return current
    raise ValueError('Không tính được thời hạn thử S4')


def status(uid, now=None, state=None):
    now=int(time.time()) if now is None else int(now)
    expiry=expires_at(uid,state)
    active=bool(expiry and expiry>now)
    return {
        'active': active,
        'expires_at': expiry,
        'server_now': now,
        'remaining_seconds':open_seconds_between(now,expiry) if active else 0,
    }


def activate(state,item_id,now=None):
    from . import s4_exclusive
    item_id=str(item_id)
    hours=hours_for(item_id)
    if not hours:
        raise ValueError('Chìa Khóa S4 không hợp lệ')
    uid=str(state.get('uid') or '').strip()
    source=str(state.get('server_id') or '').strip().upper()
    if not uid or not source or source in (WORLD,"S5"):
        raise ValueError('Chìa Khóa S4 chỉ kích hoạt từ máy chủ thường')
    count=int(state.get('items',{}).get(item_id,0))
    if count<1:
        raise ValueError('Không có Chìa Khóa S4 Dùng Thử trong Túi Đồ')
    now=int(time.time()) if now is None else int(now)
    if status(uid,now,state)['active']:
        raise ValueError('Bạn đã có Chìa Khóa S4 đang hoạt động. Hãy dùng chìa tiếp theo sau khi hết hạn.')
    # A VIP15 permanent-key holder must never waste an awarded trial key.
    if s4_exclusive.permanent_access(uid):
        raise ValueError('Tài khoản đã có Chìa Khóa S4 vĩnh viễn')
    s4_exclusive.ensure_open(WORLD,now=now)
    ends=trial_end_at(now,hours)
    state.setdefault('items',{})[item_id]=count-1
    state['s4_trial_expires_at']=ends
    state['s4_trial_activated_at']=now
    state['s4_trial_key_hours']=hours
    return {
        'item_id':int(item_id), 'hours':hours,
        'activated_at':now, 'expires_at':ends,
        'remaining_seconds':hours*3600,
        'consumed':1, 'server_id':WORLD,
    }
