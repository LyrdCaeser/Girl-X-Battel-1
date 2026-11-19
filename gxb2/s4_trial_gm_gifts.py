"""Owner-triggered, UID-bound trial gifts with original Wish Capsule art.

One verified SUPER GM action atomically creates two separate, auditable mails:
 - normal world: the consumable S4 trial key
 - S4: the matching reward, held for the UID even before S4 character creation.
Nothing automatically awards trial gifts when a user activates a key.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
import time

from . import live_service, s4_trial

MARKER = '__s4_trial_gm_reward__'
OPERATOR = 'S4-TRIAL-GM'
ID_RE = re.compile(r'^[0-9a-fA-F]{32}$')
WISH_COUNT = 24
OUTFIT_SETS = (2,3,4,5,6,10,11,17,18,19)  # original full, valid 5-piece premium sets


def wish_goddesses():
    from . import wish, goddess_gifts
    ids = tuple(goddess_gifts.resolve(tid,25)[0] for tid in wish.D['partners'])
    if len(ids)!=WISH_COUNT or len(set(ids))!=WISH_COUNT:
        raise ValueError('Wish Capsule chưa đủ 24 Nữ Thần hợp lệ')
    return ids


def wish_skins():
    """24 real wearable skins for Wish families, never invent skin-family links.

    Three native Wish goddesses currently have no skin. One matching skin is
    selected for each of the other 21, then three more from their real families.
    """
    from . import wish, goddess_gifts, skins
    all_available=[]
    primary=[]
    for source in wish.D['partners']:
        canonical=goddess_gifts.resolve(source,25)[0]
        candidates=sorted((
            (sid, row) for sid,row in skins.SKINS.items()
            if row.get('model') and row.get('partners')
            and (source in row['partners'] or canonical in row['partners'])
        ),key=lambda x:(-int(x[1].get('rarity') or 0),
                         -int(x[1].get('qlt') or 0),x[0]))
        if candidates:
            primary.append(candidates[0][0])
            all_available.extend(sid for sid,_ in candidates)
    remaining=sorted(set(all_available)-set(primary))
    result=primary+remaining[:WISH_COUNT-len(primary)]
    if len(result)!=WISH_COUNT or len(set(result))!=WISH_COUNT:
        raise ValueError('Không đủ 24 skin gốc thuộc Nữ Thần Wish Capsule')
    return tuple(result)


def outfit_pieces():
    from . import dress
    pieces=[]
    for group in OUTFIT_SETS:
        rows=dress.ids(dress.GROUPS[group]['unit'])
        if len(rows)!=5 or any(not dress.complete_piece(did)
                               or dress.max_star(did)!=6 for did in rows):
            raise ValueError('Bộ Outfit Limited '+str(group)+' thiếu dữ liệu gốc')
        pieces.extend(rows)
    if len(pieces)!=50 or len(set(pieces))!=50:
        raise ValueError('Không đủ 10 bộ Outfit Limited hoàn chỉnh')
    return tuple(pieces)


def package(hours):
    try:
        hours=int(hours)
    except (TypeError,ValueError):
        raise ValueError('Chỉ chọn các mốc 24h, 48h, 72h, 96h, 120h') from None
    if hours not in s4_trial.KEY_HOURS.values():
        raise ValueError('Chỉ chọn các mốc 24h, 48h, 72h, 96h, 120h')
    wish_ids=wish_goddesses()
    return {
        'hours': hours,
        'key_item_id':next(k for k,v in s4_trial.KEY_HOURS.items() if v==hours),
        'wish_goddesses':list(wish_ids),
        'random_count':24 if hours>=96 else 0,
        'goddess_count':48 if hours>=96 else 24,
        'skin_ids':list(wish_skins()) if hours>=96 else [],
        'outfit_sets':list(OUTFIT_SETS) if hours>=96 else [],
        'outfit_piece_count':50 if hours>=96 else 0,
        'note': ('24 skin gốc của 21 dòng Wish có skin; ba dòng Wish '
                 'chưa có skin gốc tương thích') if hours>=96 else '',
    }


def _mail_ids(request_id):
    key=hashlib.sha256(request_id.encode()).hexdigest()[:24].upper()
    return 'S4TRYK-'+key,'S4TRYG-'+key


def issue(uid,server_id,character_name,hours,request_id,operator,send_key=True):
    """Exactly one owner-authorized send, atomic in live-service database."""
    if type(send_key) is not bool:
        raise ValueError('Tùy chọn gửi chìa khóa không hợp lệ')
    request_id=str(request_id or '').strip()
    if not ID_RE.fullmatch(request_id):
        raise ValueError('Mã xác nhận gửi quà không hợp lệ')
    uid=str(uid or '').strip()
    sid=str(server_id or '').strip().upper()
    name=str(character_name or '').strip()
    operator=str(operator or '').strip()
    if not uid or len(uid)>64 or not sid or sid=='S4' or not name or not operator:
        raise ValueError('Phải chọn đúng UID, tên nhân vật và máy chủ thường')
    cfg=package(hours)
    key_id,gift_id=_mail_ids(request_id)
    from . import s4_exclusive
    from . import live_service as ls
    db=ls._db()
    try:
        db.execute('BEGIN IMMEDIATE')
        # The key can be sent before an S4 character exists, but the
        # account must already own a live character on the selected world.
        player=db.execute(
            "SELECT character_name,status FROM players WHERE uid=? AND server_id=?",
            (uid,sid)).fetchone()
        if not player or player['status']!='active' or player['character_name'].casefold()!=name.casefold():
            raise ValueError('UID, tên nhân vật hoặc máy chủ thường không khớp người chơi thật')
        prev=db.execute(
            "SELECT uid,server_id,operator,attachments FROM mail WHERE id=?",
            (gift_id,)).fetchone()
        if prev:
            if prev['uid']!=uid or prev['server_id']!='S4' or prev['operator']!=OPERATOR:
                raise ValueError('Mã gửi quà đã được sử dụng cho người nhận khác')
            gift_marker=json.loads(prev['attachments']).get(MARKER) or {}
            if gift_marker.get('hours')!=cfg['hours']:
                raise ValueError('Mã gửi quà đã dùng với thời hạn khác')
            old_key=db.execute("SELECT id FROM mail WHERE id=? AND uid=? AND server_id=?",
                               (key_id,uid,sid)).fetchone()
            if send_key and not old_key:
                raise ValueError('Mã này đã gửi quà S4 mà không kèm chìa khóa')
            db.rollback()
            return {'sent':True,'already_sent':True,'uid':uid,'source_server':sid,
                    'hours':cfg['hours'],'key_mail_id':key_id if old_key else None,
                    'gift_mail_id':gift_id,'goddess_count':cfg['goddess_count'],
                    'skin_count':len(cfg['skin_ids']),
                    'outfit_set_count':len(cfg['outfit_sets'])}
        original=list(cfg['wish_goddesses'])
        if cfg['random_count']:
            candidates=sorted(set(s4_exclusive._source_goddesses())-set(original))
            if len(candidates)<24:
                raise ValueError('Danh mục VIP 15 thiếu Nữ Thần cho phần quay ngẫu nhiên')
            extras=secrets.SystemRandom().sample(candidates,24)
        else:
            extras=[]
        marker={'hours':cfg['hours'],'wish_goddesses':original,
                'extra_goddesses':extras,'skin_ids':cfg['skin_ids'],
                'outfit_sets':cfg['outfit_sets']}
        now=int(time.time())
        if send_key:
            db.execute(
                """INSERT INTO mail(id,uid,server_id,character_name,title,body,
                     attachments,status,created_at,operator)
                   VALUES(?,?,?,?,?,?,?,'pending',?,?)""",
                (key_id,uid,sid,player['character_name'],
                 f'Quà Tri Ân • Chìa Khóa S4 Dùng Thử {cfg["hours"]} Giờ',
                 'SUPER GM đã gửi tặng bạn Chìa Khóa S4 Dùng Thử. '
                 'Nhận thư rồi vào Túi Đồ để kích hoạt. '
                 'Quà Nữ Thần và trang phục tương ứng đã được SUPER GM '
                 'gửi riêng vào Hòm Thư S4 của UID này; hãy tạo nhân vật S4 để nhận.',
                 json.dumps({cfg['key_item_id']:1}),now,OPERATOR))
        db.execute(
            """INSERT INTO mail(id,uid,server_id,character_name,title,body,
                 attachments,status,created_at,operator)
               VALUES(?,?,?,?,?,?,?,'pending',?,?)""",
            (gift_id,uid,'S4',name,
             f'★ S4 • Quà Tri Ân Độc Quyền {cfg["hours"]} Giờ',
             f'Quà do SUPER GM trực tiếp gửi cho UID {uid}: '
             f'{cfg["goddess_count"]} Nữ Thần Wish/VIP 15 25★, cấp 1, '
             'không trang bị. '+(
                '24 skin Wish Capsule và 10 bộ Outfit Limited hoàn chỉnh.'
                if cfg['hours']>=96 else
                'Không kèm skin hoặc Outfit với mốc này.'
             )+' Quà chỉ dùng ở S4; chìa khóa có thời hạn, quà đã nhận vẫn '
               'thuộc hồ sơ S4 sau khi hết giờ.',
             json.dumps({MARKER:marker},ensure_ascii=False,separators=(',',':')),
             now,OPERATOR))
        ls._audit(db,'s4.trial_gm_package.send',f'{sid}:{uid}',
                  {'hours':cfg['hours'],'send_key':send_key,
                   'key_mail_id':key_id if send_key else None,
                   'gift_mail_id':gift_id,'goddess_ids':original+extras,
                   'skin_ids':cfg['skin_ids'],'outfit_sets':cfg['outfit_sets']},operator)
        db.commit()
        return {'sent':True,'already_sent':False,'uid':uid,'source_server':sid,
                'hours':cfg['hours'],'key_mail_id':key_id if send_key else None,
                'gift_mail_id':gift_id,'goddess_count':cfg['goddess_count'],
                'skin_count':len(cfg['skin_ids']),
                'outfit_set_count':len(cfg['outfit_sets'])}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def grant(state, marker, level_cap, mail_id, db):
    """Materialize only genuine signed GM-issued S4 mail, in player txn."""
    from . import s4_exclusive, goddess_gifts, skins, dress
    uid=str(state.get('uid') or '')
    if str(state.get('server_id') or '').upper()!='S4':
        raise ValueError('Gói S4 GM chỉ nhận tại S4 với giao dịch máy chủ')
    owned_db = db is None
    if owned_db:
        # Local SQLite tests have independent live/player databases; Neon
        # production always passes the borrowed atomic player transaction.
        db=live_service._db()
    try:
        row=db.execute(
            "SELECT operator FROM mail WHERE id=? AND uid=? AND server_id='S4' AND status='claimed'",
            (str(mail_id),uid)).fetchone()
    finally:
        if owned_db:
            db.close()
    if not (str(mail_id).startswith('S4TRYG-') and row and row['operator']==OPERATOR):
        raise ValueError('Thư Quà Tri Ân S4 không do SUPER GM cấp hợp lệ')
    if not isinstance(marker,dict):
        raise ValueError('Dữ liệu quà S4 bị lỗi')
    hours=marker.get('hours')
    cfg=package(hours)
    wish_ids=marker.get('wish_goddesses')
    extra=marker.get('extra_goddesses')
    skin_ids=marker.get('skin_ids')
    groups=marker.get('outfit_sets')
    if wish_ids!=cfg['wish_goddesses'] or not isinstance(extra,list) or len(extra)!=cfg['random_count'] or len(set(extra))!=len(extra):
        raise ValueError('Danh sách Nữ Thần gói S4 không hợp lệ')
    pool=set(s4_exclusive._source_goddesses())-set(wish_ids)
    if any(not isinstance(t,int) or t not in pool for t in extra):
        raise ValueError('Nữ Thần bổ sung không thuộc gói VIP 15')
    if skin_ids!=cfg['skin_ids'] or groups!=cfg['outfit_sets']:
        raise ValueError('Danh sách skin/Outfit S4 không hợp lệ')
    # A single mail always grants its intended 24/48 stars. Other packages and
    # preexisting heroes are never removed or replaced.
    result=[]
    for tid in wish_ids+extra:
        result.append(goddess_gifts.grant(state,{
            'girl_id':tid,'stars':25,'level':1,'stats':{},
            'max_stellar':False,'max_red6':False,
        },level_cap))
    new_skins=[]
    if skin_ids:
        owned=skins.collected(state)
        new_skins=[s for s in skin_ids if s not in owned]
        state['skins']['collected']=sorted(owned|set(skin_ids))
    new_outfits=0
    if groups:
        saved=dress.saved(state)
        for did in outfit_pieces():
            key=str(did)
            before=int(saved['owned'].get(key,0))
            target=dress.max_star(did)
            if before<target:
                saved['owned'][key]=target
                new_outfits+=1
    state.setdefault('s4_trial_gm_claims',[]).append(str(mail_id))
    state['s4_trial_reward_claimed']=True
    return {
        'goddesses':result,'wish_count':len(result),
        'skin_ids':list(skin_ids),'skin_count':len(skin_ids),
        'skin_details':[{
            'id':sid,'name':skins.SKINS[sid]['name'],
            'partners':skins.SKINS[sid].get('partners',[]),
            'picture_model':(
                str(skins.SKINS[sid]['model']) if
                (s4_exclusive.ROOT/'web/assets/pictures'/
                 (str(skins.SKINS[sid]['model'])+'.webp')).is_file()
                else '')
        } for sid in skin_ids],
        'outfit_set_count':len(groups),'outfit_count':new_outfits,
        'trial_hours':cfg['hours'],
        'gm_sent':True,'not_vip15':True,
    }
