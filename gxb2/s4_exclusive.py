"""S4 • Thời Không Sai Lệch: VIP15 account gate and one-time isolated welcome.

No automatic distribution to other worlds. This is a new-world feature only.
Mail is issued under an exact UID/S4 key and redeemed in the existing Neon
profile+mail transaction, never using a second account or a public grant API.
"""
from __future__ import annotations
import hashlib
import json
import sqlite3
import time
from pathlib import Path

from . import database, vip

WORLD = "S4"
NAME = "S4 • Thời Không Sai Lệch (Độc Quyền)"
REQUIRED_VIP = 15
KEY = "__s4_exclusive_bundle__"
ROOT = Path(__file__).resolve().parents[1]


def paid_exp_in_other_worlds(uid):
    """Return paid VIP EXP only from the authenticated UID's other worlds.

    Never use developer mode, client-provided VIP, user name or admin status.
    """
    uid = str(uid or "").strip()
    if not uid:
        return 0
    rows = []
    if database.is_postgres():
        conn = database.connect(ROOT / 'state/live_service.sqlite3', 'live')
        try:
            rows = conn.execute(
                "SELECT data FROM player_profiles WHERE uid=? AND server_id<>?",
                (uid, WORLD)
            ).fetchall()
        finally:
            conn.close()
    else:
        folder = ROOT / "state" / "players" / uid
        if folder.is_dir():
            for path in folder.glob("S*.sqlite3"):
                if path.stem.upper() == WORLD:
                    continue
                try:
                    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
                        r = db.execute("SELECT data FROM profile WHERE id=1").fetchone()
                        if r:
                            rows.append((r[0],))
                except (sqlite3.Error, OSError):
                    continue
    best = 0
    for row in rows:
        try:
            raw = row["data"] if isinstance(row, dict) else row[0]
            profile = json.loads(raw) if isinstance(raw, str) else raw
            if isinstance(profile, dict) and profile.get('uid') in (None, uid):
                best = max(best, vip.exp(profile))
        except (TypeError, ValueError, KeyError):
            continue
    return best


def ensure_vip15(uid, server_id):
    if str(server_id or "").upper() != WORLD:
        return 0
    earned = paid_exp_in_other_worlds(uid)
    if vip.level_for(earned) < REQUIRED_VIP:
        raise ValueError("S4 • Thời Không Sai Lệch là máy chủ độc quyền VIP 15. Tài khoản cần có nhân vật đạt VIP 15 tại S1–S3 trước khi vào S4.")
    return earned


def mail_id(uid):
    return "S4-GIFT-" + hashlib.sha256(str(uid).encode('utf-8')).hexdigest()[:24].upper()


def ensure_welcome(uid, server_id, character_name):
    """Idempotent insertion, with the exact same UID/S4 scope as its claim."""
    if str(server_id).upper() != WORLD:
        return False
    ensure_vip15(uid, server_id)
    from . import live_service
    db = live_service._db()
    try:
        if not db.execute(
                "SELECT 1 FROM players WHERE uid=? AND server_id=? AND status='active'",
                (str(uid), WORLD)).fetchone():
            raise ValueError("Chưa có nhân vật S4 hợp lệ")
        mid = mail_id(uid)
        db.execute(
            """INSERT INTO mail
               (id,uid,server_id,character_name,title,body,attachments,
                status,created_at,operator)
               VALUES(?,?,?,?,?,?,?,'pending',?,'S4-EXCLUSIVE')
               ON CONFLICT(id) DO NOTHING""",
            (mid, str(uid), WORLD, str(character_name),
             "Độc Quyền S4 • Quà Nữ Thần Wish Limited 25★",
             "Gói độc quyền S4: 24 Nữ Thần Wish Limited 25★, cấp 1, "
             "không trang bị; các trang phục Nữ Thần tương ứng và bộ Outfit "
             "đầy đủ. Nhận thư để mở màn triệu hồi Wish đặc biệt. "
             "Quà chỉ có hiệu lực tại S4.",
             json.dumps({KEY: 1}), int(time.time()))
        )
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _source_goddesses():
    from . import wish, goddess_gifts
    return tuple(int(x) for x in wish.D['partners']
                 if goddess_gifts.resolve(int(x), 25))


def _skin_ids(goddesses):
    from . import goddess_gifts, skins
    family = set()
    for source in goddesses:
        target, _ = goddess_gifts.resolve(source, 25)
        family.add(source)
        family.add(target)
        current = source
        for _ in range(3):
            candidate = goddess_gifts.COMPOSE.get(current)
            if not candidate or candidate in family:
                break
            family.add(candidate)
            current = candidate
        for tid in (source, target):
            for piece in str(goddess_gifts.PARTNERS.get(str(tid), {}).get('skin_ids') or '').split('|'):
                if piece.isdecimal() and int(piece) in skins.SKINS:
                    family.add(int(piece))
    # SKINS partners are original character form IDs. Do not accidentally
    # gift skins of unrelated heroines that merely share the same faction.
    resolved = {
        sid for sid, row in skins.SKINS.items()
        if set(map(int, row.get('partners', []))) & family
    }
    return sorted(resolved | {k for k in family if k in skins.SKINS})


def grant_bundle(state, marker, level_cap):
    """Redeem exactly once while caller holds its player/mail transaction."""
    if state.get('server_id') != WORLD or int(marker) != 1:
        raise ValueError('Quà độc quyền này chỉ dành cho S4')
    if state.get('s4_exclusive_claimed'):
        raise ValueError('Gói quà độc quyền S4 đã nhận')
    from . import goddess_gifts, skins, dress
    original = _source_goddesses()
    prizes = []
    for tid in original:
        prizes.append(goddess_gifts.grant(
            state, {'girl_id': tid, 'stars': 25, 'level': 1,
                    'max_stellar': False, 'max_red6': False,
                    'stats': {}}, level_cap))
    ids = _skin_ids(original)
    have = skins.collected(state)
    state['skins']['collected'] = sorted(have | set(ids))
    wardrobe = dress.saved(state)
    obtained = 0
    for did in dress.PIECES:
        if dress.complete_piece(did):
            newstar = dress.max_star(did)
            before = int(wardrobe['owned'].get(str(did), 0))
            wardrobe['owned'][str(did)] = max(before, newstar)
            if newstar > before:
                obtained += 1
    state['s4_exclusive_claimed'] = True
    return {'goddesses': prizes, 'skin_count': len(ids), 'skin_ids': ids,
            'outfit_count': obtained, 'outfit_total': len(wardrobe['owned']),
            'wish_count': len(prizes)}
