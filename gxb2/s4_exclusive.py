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
ACCESS_KEY = "__s4_exclusive_key__"
ACCESS_OPERATOR = "S4-VIP15-KEY"
ROOT = Path(__file__).resolve().parents[1]



# The cycle is global to S4, anchored to the world's immutable Neon
# created_at, not to each player's login time or their device clock.
OPEN_SECONDS = 72 * 3600
LOCK_SECONDS = 48 * 3600
CYCLE_SECONDS = OPEN_SECONDS + LOCK_SECONDS
_s4_epoch = None


def cycle(now=None, created_at=None):
    """Public schedule: 72h open, 48h locked, repeating every five days."""
    global _s4_epoch
    if created_at is None:
        if _s4_epoch is None:
            from . import live_service
            world = next((w for w in live_service.worlds() if w['server_id'] == WORLD), None)
            if world is None:
                raise ValueError('S4 chưa được khởi tạo')
            _s4_epoch = int(world['created_at'])
        created_at = _s4_epoch
    now = int(time.time()) if now is None else int(now)
    created_at = int(created_at)
    elapsed = max(0, now-created_at)
    index, offset = divmod(elapsed, CYCLE_SECONDS)
    opened_at = created_at + index*CYCLE_SECONDS
    open_phase = offset < OPEN_SECONDS
    phase_end = opened_at + (OPEN_SECONDS if open_phase else CYCLE_SECONDS)
    return {
        'server_id': WORLD,
        'phase': 'open' if open_phase else 'locked',
        'server_now': now,
        'started_at': created_at,
        'phase_end': phase_end,
        'remaining_seconds': max(0, phase_end-now),
        'open_seconds': OPEN_SECONDS,
        'lock_seconds': LOCK_SECONDS,
        'cycle_index': index,
        'next_open_at': opened_at if open_phase else opened_at+CYCLE_SECONDS,
    }


def ensure_open(server_id, now=None):
    if str(server_id or '').upper() != WORLD:
        return None
    current = cycle(now)
    if current['phase'] != 'open':
        raise ValueError(
            'S4 • Thời Không Sai Lệch đang khóa 48 giờ. '
            'Hãy quay lại khi đồng hồ đếm ngược kết thúc.'
        )
    return current


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
        raise ValueError("S4 • Thời Không Sai Lệch là máy chủ độc quyền VIP 15. Tài khoản cần có nhân vật đạt VIP 15 tại một máy chủ khác S4 trước khi vào.")
    return earned


def access_key_mail_id(uid):
    """One deterministic, UID-wide reward ID across all current/future worlds."""
    return "S4-KEY-" + hashlib.sha256(str(uid).encode("utf-8")).hexdigest()[:24].upper()


def key_claimed(uid):
    """Non-consumable entitlement tied to verified, claimed account mail."""
    if not str(uid or "").strip():
        return False
    from . import live_service
    db = live_service._db()
    try:
        row = db.execute(
            """SELECT 1 FROM mail WHERE id=? AND uid=? AND status='claimed'
               AND server_id<>? AND operator=?""",
            (access_key_mail_id(uid), str(uid), WORLD, ACCESS_OPERATOR)
        ).fetchone()
        return bool(row)
    finally:
        db.close()


def ensure_key_claimed(uid, server_id):
    if str(server_id or "").upper() != WORLD:
        return True
    if not key_claimed(uid):
        raise ValueError(
            "Tài khoản chưa mở khóa S4. Hãy vào Hòm Thư tại máy chủ đã đạt "
            "VIP 15, nhận Chìa Khóa S4 • Độc Quyền rồi quay lại."
        )
    return True


def ensure_key_mail(state, db=None):
    """Issue once on a real non-S4 world after paid VIP EXP reaches level 15.

    When db is the borrowed Neon mail transaction, the award is committed
    together with the paid VIP claim and character profile; no phantom mails.
    Older VIP15 accounts receive the mail on their next profile snapshot.
    """
    from . import live_service
    uid = str(state.get("uid") or "").strip()
    server_id = str(state.get("server_id") or "").upper()
    name = str(state.get("name") or "").strip()
    if not uid or not server_id or server_id == WORLD or not name:
        return False
    if vip.level_for(vip.exp(state)) < REQUIRED_VIP:
        return False
    owned_db = db is None
    if owned_db:
        db = live_service._db()
    try:
        mid = access_key_mail_id(uid)
        # Source server is determined only by the saved character state,
        # never by a request body; must be a registered real UID/world.
        row = db.execute(
            "SELECT 1 FROM players WHERE uid=? AND server_id=? AND status='active'",
            (uid, server_id)
        ).fetchone()
        if not row:
            raise ValueError("Chưa xác nhận nhân vật của máy chủ nhận chìa khóa S4")
        result = db.execute(
            """INSERT INTO mail
              (id,uid,server_id,character_name,title,body,attachments,
               status,created_at,operator)
              VALUES(?,?,?,?,?,?,?,'pending',?,?)
              ON CONFLICT(id) DO NOTHING""",
            (mid, uid, server_id, name,
             "Chúc Mừng VIP 15 • Chìa Khóa S4 Độc Quyền",
             "Chúc mừng bạn đã đạt VIP 15! Bạn được trao Chìa Khóa S4 • "
             "Độc Quyền để mở cửa Thời Không Sai Lệch. "
             "Nhấn Nhận Chìa Khóa để mở quyền vào S4 vĩnh viễn. "
             "S4 hoạt động theo chu kỳ 72 giờ mở, 48 giờ nghỉ; "
             "hãy theo dõi đồng hồ khi chọn S4. "
             "Chìa khóa gắn với tài khoản, không tiêu hao và chỉ cấp một lần.",
             json.dumps({ACCESS_KEY: 1}, ensure_ascii=False),
             int(time.time()), ACCESS_OPERATOR)
        )
        if owned_db:
            db.commit()
        return result.rowcount == 1
    except Exception:
        if owned_db:
            db.rollback()
        raise
    finally:
        if owned_db:
            db.close()


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
    if state.get('server_id') != WORLD or int(marker) not in (1, 2):
        raise ValueError('Quà độc quyền này chỉ dành cho S4')
    # Marker 1 is the immutable one-time welcome. Marker 2 is issued only
    # by the dedicated SUPER GM S4 giftcode factory (one redemption per UID/code).
    # The mail's claimed transition and grants share one Neon transaction.
    if int(marker) == 1 and state.get('s4_exclusive_claimed'):
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
    # A GM campaign must not consume the original one-time S4 welcome.
    # Keep the original welcome available even if a code is redeemed first.
    if int(marker) == 1:
        state['s4_exclusive_claimed'] = True
    # Return the exact ORIGINAL skin labels/art identifiers to the S4 Wish
    # presentation (no new inventory writes, and no additional DB requests).
    # The frontend receives these only on a successful, atomic S4 mail claim.
    return {'goddesses': prizes, 'skin_count': len(ids), 'skin_ids': ids,
            'skin_details': [{'id': sid, 'name': skins.SKINS[sid]['name']} for sid in ids],
            'outfit_count': obtained, 'outfit_total': len(wardrobe['owned']),
            'wish_count': len(prizes)}
