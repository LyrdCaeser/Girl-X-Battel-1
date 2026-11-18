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
CATALOG_VERSION = 2
CATALOG_OPERATOR = "S4-EXPANSION-V2"
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
             "Gói độc quyền S4: 104 dòng Nữ Thần 25★, cấp 1, "
             "không trang bị; 324 skin gốc và bộ Outfit khả dụng "
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


def catalog_upgrade_mail_id(uid):
    return "S4-EXPAND2-" + hashlib.sha256(str(uid).encode("utf-8")).hexdigest()[:24].upper()


def ensure_catalog_upgrade(uid, server_id, character_name):
    """Issue one S4-only compensation mail to a claimed legacy welcome.

    Called only after the verified S4 player snapshot; never touches other
    worlds or writes player inventory outside the authenticated mail claim.
    """
    if str(server_id).upper() != WORLD:
        return False
    from . import live_service
    db = live_service._db()
    try:
        row = db.execute(
            "SELECT 1 FROM players WHERE uid=? AND server_id=? AND status='active'",
            (str(uid), WORLD)
        ).fetchone()
        if not row:
            return False
        db.execute(
            """INSERT INTO mail
             (id,uid,server_id,character_name,title,body,attachments,
              status,created_at,operator)
             VALUES(?,?,?,?,?,?,?,'pending',?,?)
             ON CONFLICT(id) DO NOTHING""",
            (catalog_upgrade_mail_id(uid),str(uid),WORLD,str(character_name),
             "Bổ Sung S4 • Toàn Bộ Nữ Thần 25★ Và Trang Phục",
             "Đã mở rộng quà độc quyền S4: đủ 104 dòng Nữ Thần đạt 25★, "
             "324 trang phục Nữ Thần có dữ liệu gốc và 242 món Outfit khả dụng. "
             "Nhấn Nhận để bổ sung chính xác phần còn thiếu. "
             "Nữ Thần và trang phục đã sở hữu được giữ nguyên. "
             "Chỉ có hiệu lực trong máy chủ S4.",
             json.dumps({KEY: 3}),int(time.time()),CATALOG_OPERATOR)
        )
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _source_goddesses():
    """Canonical 10★ forms only, without their 5★/6★ duplicate incarnations.

    Wish Capsule's 24 featured choices are NOT the complete goddess roster.
    The original guide has 104 unique 10★ forms eligible for 25★.
    """
    from . import goddess_gifts
    result = []
    for girl in goddess_gifts.GIRLS:
        tid = int(girl['id'])
        row = goddess_gifts.PARTNERS.get(str(tid), {})
        if int(row.get('max_star') or 0) != 10:
            continue
        try:
            target, _ = goddess_gifts.resolve(tid,25)
        except ValueError:
            continue
        if target == tid:
            result.append(tid)
    return tuple(sorted(set(result)))


def _skin_ids(goddesses):
    """All real original skins, not just the 24 Wish-goddess families.

    12 catalogue placeholders have no compatible character; those are not
    wearable assets and must never be represented as gifts.
    """
    from . import skins
    return tuple(sorted(
        sid for sid, row in skins.SKINS.items()
        if row.get('partners') and row.get('model')
    ))


def grant_bundle(state, marker, level_cap):
    """Atomic S4-only full gift, GM giftcode, or once-only legacy expansion.

    All gifts are attached to the authenticated UID/S4 mail transaction.
    Never remove, downgrade, or overwrite any existing partner/skin/outfit.
    """
    if state.get('server_id') != WORLD or int(marker) not in (1,2,3):
        raise ValueError('Quà độc quyền này chỉ dành cho S4')
    if int(marker) == 1 and state.get('s4_exclusive_claimed'):
        raise ValueError('Gói quà độc quyền S4 đã nhận')
    if int(marker) == 3:
        if not state.get('s4_exclusive_claimed'):
            raise ValueError('Thư bổ sung chỉ dành cho người đã nhận quà S4 cũ')
        if int(state.get('s4_catalog_version') or 0) >= CATALOG_VERSION:
            raise ValueError('Quà bổ sung S4 đã nhận')
    from . import goddess_gifts, skins, dress
    original = _source_goddesses()
    # Every canonical 25★ goddess appears at most once in the S4 welcome
    # or legacy supplement. GM giftcodes retain independent reward semantics.
    existing = {
        int(p.get('table_id') or 0) for p in state.get('partners', [])
        if int(p.get('awake') or 0) >= 15
    }
    prizes = []
    for tid in original:
        if int(marker) != 2 and tid in existing:
            continue
        prizes.append(goddess_gifts.grant(
            state, {'girl_id': tid, 'stars': 25, 'level': 1,
                    'max_stellar': False, 'max_red6': False,
                    'stats': {}}, level_cap))
        existing.add(tid)
    ids = _skin_ids(original)
    have = skins.collected(state)
    new_ids = sorted(set(ids)-have)
    state['skins']['collected'] = sorted(have|set(ids))
    wardrobe = dress.saved(state)
    obtained = 0
    for did in dress.PIECES:
        if dress.complete_piece(did):
            newstar = dress.max_star(did)
            before = int(wardrobe['owned'].get(str(did), 0))
            wardrobe['owned'][str(did)] = max(before, newstar)
            if newstar > before:
                obtained += 1
    if int(marker) == 1:
        state['s4_exclusive_claimed'] = True
    state['s4_catalog_version'] = CATALOG_VERSION
    # Return only newly collected skins so supplementary mail doesn't
    # replay the previous 76 outfits as if they were newly awarded.
    display_ids = ids if int(marker)==2 else new_ids
    return {'goddesses': prizes,'skin_count': len(display_ids),
            'skin_ids': list(display_ids),
            'skin_details': [
                {'id': sid, 'name': skins.SKINS[sid]['name'],
                 'partners': skins.SKINS[sid].get('partners', []),
                 'picture_model': (
                     str(skins.SKINS[sid].get('model', ''))
                     if (ROOT / 'web/assets/pictures' /
                         (str(skins.SKINS[sid].get('model', '')) + '.webp')).is_file()
                     else '')}
                for sid in display_ids],
            'outfit_count': obtained,'outfit_total': len(wardrobe['owned']),
            'wish_count': len(prizes),
            'catalog_total': len(original),
            'skin_catalog_total': len(ids),
            'catalog_version': CATALOG_VERSION}



def replay_payload(state):
    """Read-only S4 Wish replay for rewards the player actually owns.

    No grants, duplicate mail claims, or cross-world access. Player identity
    comes exclusively from the authenticated engine state.
    """
    if str(state.get('server_id') or '').upper() != WORLD:
        raise ValueError('Chỉ có thể xem lại Wish tại máy chủ S4')
    if not (state.get('s4_exclusive_claimed') or
            int(state.get('s4_catalog_version') or 0) >= CATALOG_VERSION):
        raise ValueError('Chưa nhận quà Wish độc quyền S4')
    from . import goddess_gifts, skins
    canonical = set(_source_goddesses())
    rewarded = {}
    for p in state.get('partners', []):
        try:
            tid = int(p.get('table_id') or 0)
            stars = 10 + int(p.get('awake') or 0)
        except (ValueError, TypeError):
            continue
        if tid in canonical and stars >= 25 and tid not in rewarded:
            metadata = goddess_gifts.BY_ID.get(tid, {})
            rewarded[tid] = {
                'table_id': tid, 'name': str(metadata.get('name') or tid),
                'stars': 25,
            }
    # Unlike skins.collected(), reading the replay must not migrate or write
    # saved ownership. Inspect historical bags/equipped IDs without mutation.
    saved_skins = state.get('skins') or {}
    owned = {int(x) for x in saved_skins.get('collected', [])
             if str(x).isdigit() and int(x) in skins.SKINS}
    for item_id, amount in (state.get('items') or {}).items():
        if str(item_id).isdigit() and int(item_id) in skins.SKINS and int(amount)>0:
            owned.add(int(item_id))
    for hero in state.get('partners', []):
        equipped = hero.get('equips') or []
        if len(equipped)>=7 and int(equipped[6] or 0) in skins.SKINS:
            owned.add(int(equipped[6]))
    valid = set(_skin_ids(canonical))
    ids = sorted(owned & valid)
    catalog = [{
        'id': sid,
        'name': skins.SKINS[sid]['name'],
        'partners': skins.SKINS[sid].get('partners', []),
        'picture_model': (
            str(skins.SKINS[sid].get('model', ''))
            if (ROOT / 'web/assets/pictures' /
                (str(skins.SKINS[sid].get('model', '')) + '.webp')).is_file()
            else ''),
    } for sid in ids]
    outfit = state.get('dress') or {}
    return {
        'goddesses': list(rewarded.values()),
        'wish_count': len(rewarded),
        'skin_ids': ids, 'skin_details': catalog, 'skin_count': len(ids),
        'outfit_total': len(outfit.get('owned', {})),
        'catalog_total': len(canonical),
        'skin_catalog_total': len(valid),
        'replay': True, 'granted': False,
    }
