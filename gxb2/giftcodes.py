"""Giftcode Studio: server-owned codes, audited mail rewards, atomic redemption.

No website key alone grants item-writing permissions. Issuance is authorized by
the existing GXB3 SUPER GM session and separate GM action key in server.py.
"""
from __future__ import annotations
import json
import re
import secrets
import threading
import time
import uuid
from pathlib import Path
from . import gm_catalog, live_service

ROOT = Path(__file__).resolve().parents[1]
LAST_CAMPAIGN_STAGE = max(map(int, json.loads((ROOT / 'data/stage.json').read_text())))

_LOCK = threading.RLock()
_READY = False
CODE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9_-]{5,39}$")

def _connection():
    global _READY
    db = live_service._db()
    try:
        if not _READY:
            with _LOCK:
                if not _READY:
                    db.execute("""CREATE TABLE IF NOT EXISTS giftcodes(
                        code TEXT PRIMARY KEY, title TEXT NOT NULL,
                        message TEXT NOT NULL, rewards TEXT NOT NULL,
                        server_id TEXT NOT NULL DEFAULT 'ALL',
                        max_uses INTEGER NOT NULL, used_count INTEGER NOT NULL DEFAULT 0,
                        expires_at BIGINT NOT NULL DEFAULT 0, active INTEGER NOT NULL DEFAULT 1,
                        created_at BIGINT NOT NULL, created_by TEXT NOT NULL,
                        target_uid TEXT NOT NULL DEFAULT '',
                        effect TEXT NOT NULL DEFAULT '')""")
                    if db.backend == 'postgres':
                        columns = {row['column_name'] for row in db.execute(
                            "SELECT column_name FROM information_schema.columns WHERE table_name='giftcodes'"
                        ).fetchall()}
                    else:
                        columns = {row['name'] for row in db.execute("PRAGMA table_info(giftcodes)").fetchall()}
                    if 'target_uid' not in columns:
                        db.execute("ALTER TABLE giftcodes ADD COLUMN target_uid TEXT NOT NULL DEFAULT ''")
                    if 'effect' not in columns:
                        db.execute("ALTER TABLE giftcodes ADD COLUMN effect TEXT NOT NULL DEFAULT ''")
                    db.execute("""CREATE TABLE IF NOT EXISTS giftcode_redemptions(
                        code TEXT NOT NULL, uid TEXT NOT NULL,
                        server_id TEXT NOT NULL, mail_id TEXT NOT NULL,
                        redeemed_at BIGINT NOT NULL,
                        PRIMARY KEY(code,uid),
                        FOREIGN KEY(code) REFERENCES giftcodes(code))""")
                    db.execute("CREATE INDEX IF NOT EXISTS idx_giftcodes_created ON giftcodes(created_at DESC)")
                    db.execute("CREATE INDEX IF NOT EXISTS idx_giftcode_redemptions_code ON giftcode_redemptions(code,redeemed_at DESC)")
                    db.commit()
                    _READY = True
        return db
    except Exception:
        db.rollback()
        db.close()
        raise

def _normalize(code):
    code = str(code or '').strip().upper().replace(' ', '')
    if not CODE_PATTERN.fullmatch(code):
        raise ValueError('Mã giftcode không hợp lệ (6–40 ký tự A-Z, số, _ và -)')
    return code

def exists(code):
    """Server-side uniqueness probe for the optional manually entered giftcode."""
    code = _normalize(code)
    db = _connection()
    try:
        return bool(db.execute("SELECT 1 FROM giftcodes WHERE code=?", (code,)).fetchone())
    finally:
        db.close()


def _public(row):
    d = dict(row)
    d['rewards'] = json.loads(d['rewards'])
    d['active'] = bool(d['active'])
    d['remaining'] = None if int(d['max_uses']) == 0 else max(0,int(d['max_uses'])-int(d['used_count']))
    d['unlimited'] = int(d['max_uses']) == 0
    return d

def list_codes(limit=150):
    db=_connection()
    try:
        rows=db.execute("SELECT * FROM giftcodes ORDER BY created_at DESC,code DESC LIMIT ?",
                        (min(200,max(1,int(limit))),)).fetchall()
        return [_public(row) for row in rows]
    finally:
        db.close()

def create(payload, operator):
    if not isinstance(payload,dict):
        raise ValueError('Dữ liệu giftcode không hợp lệ')
    raw=str(payload.get('code') or '').strip()
    if raw and len(raw) > 24:
        raise ValueError('Mã tùy chọn phải từ 6 đến 24 ký tự')
    code=_normalize(raw if raw else 'GXB3-'+secrets.token_hex(8).upper())
    title=str(payload.get('title') or 'Quà Giftcode GXB 3').strip()[:100]
    message=str(payload.get('message') or 'Chúc bạn chơi game vui vẻ!').strip()[:1000]
    if not title:
        raise ValueError('Vui lòng nhập tiêu đề')
    goddess=payload.get('goddess')
    if goddess is not None:
        from . import goddess_gifts
        if payload.get('rewards'): raise ValueError('Gift Nữ Thần không thể trộn với quà vật phẩm')
        rewards={'__gxb3_goddess__':goddess_gifts.validate(goddess)}
    else:
        rewards=gm_catalog.validate_gift(payload.get('rewards'))
        if len(rewards)>35:raise ValueError('Tối đa 35 loại vật phẩm trên một giftcode')
    try:
        max_uses=int(payload.get('max_uses') or 0)
        expires_at=int(payload.get('expires_at') or 0)
    except (TypeError,ValueError):
        raise ValueError('Số lượt hoặc thời hạn không hợp lệ') from None
    if goddess is None and not 1<=max_uses<=100000:
        raise ValueError('Số lượt sử dụng phải từ 1 đến 100.000')
    now=int(time.time())
    if goddess is not None:
        # 30-day policy is immutable: 0 means unlimited GLOBAL use.
        max_uses=0; expires_at=now+30*86400
    if expires_at and (expires_at<=now or expires_at>now+366*86400*2):
        raise ValueError('Hạn dùng phải ở tương lai, tối đa 2 năm')
    world=str(payload.get('server_id') or 'ALL').strip().upper()
    if world!='ALL' and world not in {w['server_id'] for w in live_service.worlds()}:
        raise ValueError('Máy chủ không tồn tại')
    db=_connection()
    try:
        if db.execute("SELECT code FROM giftcodes WHERE code=?", (code,)).fetchone():
            raise ValueError('Mã đã tồn tại, hãy chọn mã khác')
        db.execute("""INSERT INTO giftcodes
            (code,title,message,rewards,server_id,max_uses,used_count,expires_at,active,created_at,created_by,target_uid,effect)
            VALUES(?,?,?,?,?,?,0,?,1,?,?,?,?)""",
            (code,title,message,json.dumps(rewards,ensure_ascii=False),world,
             max_uses,expires_at,now,str(operator)[:100],'',''))
        live_service._audit(db,'giftcode.create',code,
            {'server_id':world,'max_uses':max_uses,'expires_at':expires_at,'rewards':rewards},str(operator))
        db.commit()
        return {'code':code,'title':title,'message':message,'rewards':rewards,
                'server_id':world,'max_uses':max_uses,'used_count':0,
                'expires_at':expires_at,'active':True,'remaining':None if goddess is not None else max_uses,
                'unlimited':goddess is not None,'created_at':now}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def create_goddess(config: dict, operator: str) -> dict:
    """SUPER GM: 30 days, unlimited global redemptions, once per UID."""
    from . import goddess_gifts
    validated=goddess_gifts.validate(config)
    return create({'goddess':validated,
                   'title':'Gift Nữ Thần · '+validated['name']+' '+str(validated['stars'])+'★',
                   'message':'Quà Nữ Thần SUPER GM. Mỗi tài khoản chỉ được nhận mã này một lần.',
                   'server_id':'ALL'},operator)


def create_s4_exclusive(operator, code='', max_uses=0, days=30):
    """GM-only: complete 24-goddess/76-skin/outfit S4 Wish gift via mail.

    Only S4, once per UID per code. A redeemed S4 welcome does not block a
    deliberate new GM campaign; VIP15 + claimed S4 key remain prerequisites.
    """
    from . import s4_exclusive
    raw=str(code or '').strip()
    if raw and len(raw)>24:
        raise ValueError('Giftcode S4 tối đa 24 ký tự')
    code=_normalize(raw or ('S4WISH-'+secrets.token_hex(6).upper()))
    try:
        max_uses=int(max_uses)
        days=int(days)
    except (TypeError,ValueError):
        raise ValueError('Lượt sử dụng hoặc số ngày không hợp lệ') from None
    if not 0<=max_uses<=100000:
        raise ValueError('Số lượt tối đa từ 0 (không giới hạn) đến 100.000')
    if not 1<=days<=365:
        raise ValueError('Thời hạn giftcode S4 từ 1 đến 365 ngày')
    if not any(w['server_id']==s4_exclusive.WORLD for w in live_service.worlds()):
        raise ValueError('S4 chưa được khởi tạo')
    now=int(time.time())
    title='Độc Quyền S4 • Quà Nữ Thần Wish Limited 25★'
    message=('Giftcode SUPER GM S4: 24 Nữ Thần Wish Limited 25★, cấp 1, '
             'không trang bị; 76 trang phục và trọn bộ Outfit Limited. '
             'Nhấn nhận thư để xem hiệu ứng triệu hồi Wish. '
             'Quà chỉ nhận tại máy chủ S4.')
    rewards={s4_exclusive.KEY:2}
    db=_connection()
    try:
        if db.execute('SELECT 1 FROM giftcodes WHERE code=?',(code,)).fetchone():
            raise ValueError('Giftcode đã tồn tại')
        db.execute("""INSERT INTO giftcodes
          (code,title,message,rewards,server_id,max_uses,used_count,
           expires_at,active,created_at,created_by,target_uid,effect)
          VALUES(?,?,?,?,?, ?,0,?,1,?,?,?,?)""",
          (code,title,message,json.dumps(rewards,ensure_ascii=False),s4_exclusive.WORLD,
           max_uses,now+days*86400,now,str(operator)[:100],'','s4_wish_bundle'))
        live_service._audit(db,'giftcode.create.s4_exclusive',code,
            {'server_id':'S4','max_uses':max_uses,'duration_days':days,
             'bundle':'24 x 25star + 76 skins + full outfits'},str(operator))
        db.commit()
        return {'code':code,'title':title,'message':message,'rewards':rewards,
                'server_id':'S4','max_uses':max_uses,'used_count':0,
                'expires_at':now+days*86400,'remaining':None if max_uses==0 else max_uses,
                'unlimited':max_uses==0,'active':True,'effect':'s4_wish_bundle'}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()



def create_s4_trial_key(uid, server_id, character_name, hours, operator,
                        code='', days=30):
    """SUPER GM: one-use, one-UID code for a matching consumable S4 key."""
    from . import s4_trial_gm_gifts
    cfg=s4_trial_gm_gifts.package(hours)
    uid=str(uid or '').strip()
    server_id=str(server_id or '').strip().upper()
    character_name=str(character_name or '').strip()
    person=live_service.player(uid,server_id)
    if (not person or person['status']!='active' or server_id=='S4'
            or person['character_name'].casefold()!=character_name.casefold()):
        raise ValueError('UID, máy chủ hoặc tên nhân vật thường không hợp lệ')
    try:days=int(days)
    except (TypeError,ValueError):
        raise ValueError('Số ngày dùng mã không hợp lệ') from None
    if not 1<=days<=365:
        raise ValueError('Giftcode có hạn từ 1 đến 365 ngày')
    raw=str(code or '').strip()
    if raw and len(raw)>24:
        raise ValueError('Mã tùy chọn tối đa 24 ký tự')
    code=_normalize(raw or ('S4TRY-'+secrets.token_hex(7).upper()))
    now=int(time.time())
    expires_at=now+days*86400
    rewards={cfg['key_item_id']:1}
    title=f'Quà Tri Ân Nạp Giá Trị Cao • Chìa Khóa S4 {cfg["hours"]} Giờ'
    message=('Mã độc quyền cho UID của bạn. Nhận chìa trong Hòm Thư, '
             'dùng trong Túi Đồ để tự mở gói Quà Tri Ân tương ứng trên S4. '
             'Đăng nhập S4 để nhận quà tự động.')
    db=_connection()
    try:
        if db.execute('SELECT 1 FROM giftcodes WHERE code=?',(code,)).fetchone():
            raise ValueError('Giftcode đã tồn tại')
        db.execute("""INSERT INTO giftcodes
            (code,title,message,rewards,server_id,max_uses,used_count,
             expires_at,active,created_at,created_by,target_uid,effect)
             VALUES(?,?,?,?,?,1,0,?,1,?,?,?,?)""",
             (code,title,message,json.dumps(rewards),server_id,
              expires_at,now,str(operator)[:100],uid,'s4_trial_key'))
        live_service._audit(db,'giftcode.create.s4_trial',code,
            {'target_uid':uid,'source_server':server_id,'hours':cfg['hours'],
             'key_item_id':cfg['key_item_id'],'expires_at':expires_at},str(operator))
        db.commit()
        return {'code':code,'title':title,'target_uid':uid,'server_id':server_id,
                'hours':cfg['hours'],'key_item_id':cfg['key_item_id'],
                'goddess_count':cfg['goddess_count'],
                'skin_count':len(cfg['skin_ids']),
                'outfit_set_count':len(cfg['outfit_sets']),
                'expires_at':expires_at,'max_uses':1}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def create_monthanh_s5_bundle(operator):
    """Private server-side operator issuance; not a public creation endpoint."""
    from . import s5_test as s
    uid=s.MONTHANH_UID
    target=live_service.player(uid,'S5')
    if not s.verified_svip(uid) or not target or target.get('status')!='active':
        raise ValueError('Không tìm thấy tài khoản monthanh đang hoạt động tại S5')
    code=_normalize('S5-MT-'+secrets.token_hex(8).upper())
    rewards={s.MONTHANH_BUNDLE:1}
    count=len(s.roster(uid))
    now=int(time.time())
    title='S5 • Quà Nữ Thần 25★ độc quyền monthanh'
    message=f'Nhận đủ {count} Nữ Thần 25★ cấp 1, không trang bị. Mã riêng của monthanh, chỉ sử dụng một lần tại S5.'
    db=_connection()
    try:
        db.execute("""INSERT INTO giftcodes
            (code,title,message,rewards,server_id,max_uses,used_count,expires_at,active,
             created_at,created_by,target_uid,effect)
            VALUES(?,?,?,?,?,1,0,0,1,?,?,?,?)""",
            (code,title,message,json.dumps(rewards),'S5',now,str(operator)[:100],uid,'s5_monthanh_all25'))
        live_service._audit(db,'giftcode.create.s5_monthanh_all25',code,
            {'uid':uid,'server_id':'S5','max_uses':1,'goddess_count':count},str(operator))
        db.commit()
        return {'code':code,'server_id':'S5','max_uses':1,'used_count':0,
                'expires_at':0,'goddess_count':count}
    except Exception:
        db.rollback();raise
    finally:db.close()


def create_campaign_clear(uid, server_id, operator, code=''):
    """Create one private, one-use code bound to one exact character."""
    uid=str(uid or '').strip()
    server_id=str(server_id or '').strip().upper()
    target=live_service.player(uid,server_id)
    if not target or target.get('status')=='banned':
        raise ValueError('Không tìm thấy nhân vật nhận mã')
    code=_normalize(str(code or '').strip() or ('CLEAR530-'+secrets.token_hex(6).upper()))
    now=int(time.time())
    expires_at=now+30*86400
    db=_connection()
    try:
        if db.execute("SELECT 1 FROM giftcodes WHERE code=?",(code,)).fetchone():
            raise ValueError('Mã đã tồn tại, hãy tạo mã khác')
        db.execute("""INSERT INTO giftcodes
            (code,title,message,rewards,server_id,max_uses,used_count,expires_at,active,
             created_at,created_by,target_uid,effect)
            VALUES(?,?,?,?,?,1,0,?,1,?,?,?,?)""",
            (code,'Quét Sạch Chiến Dịch',
             f'Mở đủ toàn bộ {LAST_CAMPAIGN_STAGE} ải Chiến Dịch cho đúng tài khoản đã chỉ định.',
             '{}',server_id,expires_at,now,str(operator)[:100],uid,'campaign_all'))
        live_service._audit(db,'giftcode.create.campaign_all',code,
            {'uid':uid,'server_id':server_id,'max_stage':LAST_CAMPAIGN_STAGE,
             'max_uses':1,'expires_at':expires_at},str(operator))
        db.commit()
        return {'code':code,'title':'Quét Sạch Chiến Dịch','server_id':server_id,
                'target_uid':uid,'max_uses':1,'used_count':0,'expires_at':expires_at,
                'active':True,'effect':'campaign_all','max_stage':LAST_CAMPAIGN_STAGE}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def revoke(code,operator):
    code=_normalize(code)
    db=_connection()
    try:
        cur=db.execute("UPDATE giftcodes SET active=0 WHERE code=? AND active=1",(code,))
        if cur.rowcount!=1:
            raise ValueError('Giftcode không tồn tại hoặc đã vô hiệu hóa')
        live_service._audit(db,'giftcode.revoke',code,{},str(operator))
        db.commit()
        return {'code':code,'active':False}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def redemptions(code,limit=80):
    code=_normalize(code)
    db=_connection()
    try:
        rows=db.execute("""SELECT code,uid,server_id,mail_id,redeemed_at
                        FROM giftcode_redemptions WHERE code=?
                        ORDER BY redeemed_at DESC LIMIT ?""",
                        (code,max(1,min(200,int(limit))))).fetchall()
        return [dict(x) for x in rows]
    finally:
        db.close()

def redeem(code,uid,server_id):
    code=_normalize(code)
    uid=str(uid or '').strip()
    server_id=str(server_id or '').strip().upper()
    if not uid or not server_id:
        raise ValueError('Vui lòng đăng nhập tài khoản game trước')
    # UID and server_id must come from a verified HTTP session, never request JSON.
    profile=live_service.player(uid,server_id)
    if not profile or profile.get('status')=='banned':
        raise ValueError('Nhân vật không hợp lệ hoặc đã bị khóa')
    now=int(time.time())
    db=_connection()
    try:
        # PG row lock serializes concurrent redeemers; SQLite begins IMMEDIATE
        # to serialize before checking and incrementing available slots.
        if db.backend=='sqlite':
            db.execute("BEGIN IMMEDIATE")
        # Serialize giftcode mail creation against S4 character deletion.
        # An earlier verified session cannot leave orphaned gift mail.
        player_sql="SELECT status FROM players WHERE uid=? AND server_id=?"
        if db.backend=='postgres':
            player_sql+=" FOR UPDATE"
        current=db.execute(player_sql,(uid,server_id)).fetchone()
        if not current or current["status"]!="active":
            raise ValueError("Nhân vật không còn tồn tại hoặc không hoạt động")
        sql="SELECT * FROM giftcodes WHERE code=?"
        if db.backend=='postgres':
            sql+=" FOR UPDATE"
        row=db.execute(sql,(code,)).fetchone()
        if not row:
            raise ValueError('Giftcode không tồn tại')
        if db.execute("SELECT 1 FROM giftcode_redemptions WHERE code=? AND uid=?",(code,uid)).fetchone():
            raise ValueError('Tài khoản đã sử dụng giftcode này')
        if not row['active']:
            raise ValueError('Giftcode đã bị khóa')
        if row['expires_at'] and int(row['expires_at'])<=now:
            raise ValueError('Giftcode đã hết hạn')
        if row['server_id']!='ALL' and row['server_id']!=server_id:
            raise ValueError('Giftcode không áp dụng cho máy chủ này')
        if str(row['target_uid'] or '') and str(row['target_uid'])!=uid:
            raise ValueError('Giftcode này được khóa cho một UID khác')
        if int(row['max_uses']) and int(row['used_count'])>=int(row['max_uses']):
            raise ValueError('Giftcode đã hết lượt sử dụng')
        rewards=json.loads(row['rewards'])
        effect=str(row['effect'] or '')
        if effect=='s4_wish_bundle':
            from . import s4_exclusive
            if (server_id!='S4' or row['server_id']!='S4'
                    or rewards!={s4_exclusive.KEY:2}):
                raise ValueError('Giftcode Wish Limited chỉ dành cho S4')
            s4_exclusive.ensure_vip15(uid,'S4')
            s4_exclusive.ensure_key_claimed(uid,'S4')
        if effect=='s4_trial_key':
            from . import s4_trial
            if (row['server_id']!=server_id or
                    row['target_uid']!=uid or int(row['max_uses'])!=1 or
                    len(rewards)!=1 or next(iter(rewards),None) not in s4_trial.KEY_IDS or
                    next(iter(rewards.values()),None)!=1):
                raise ValueError('Giftcode Chìa Khóa S4 không đúng UID hoặc loại chìa')
        if effect=='s5_monthanh_all25':
            from . import s5_test as s
            if (server_id!='S5' or row['server_id']!='S5' or row['target_uid']!=uid
                    or int(row['max_uses'])!=1 or not s.verified_svip(uid)
                    or rewards!={s.MONTHANH_BUNDLE:1}):
                raise ValueError('Giftcode chỉ dành cho monthanh tại S5')
        state_changed=False
        if effect and effect not in ('s4_wish_bundle','s4_trial_key','s5_monthanh_all25'):
            if effect!='campaign_all':
                raise ValueError('Hiệu lực Giftcode không được hỗ trợ')
            lock=" FOR UPDATE" if db.backend=='postgres' else ""
            saved=db.execute("SELECT data FROM player_profiles WHERE uid=? AND server_id=?"+lock,
                             (uid,server_id)).fetchone()
            if not saved:
                raise ValueError('Không tìm thấy dữ liệu nhân vật')
            state=json.loads(saved['data'])
            state['max_stage']=LAST_CAMPAIGN_STAGE
            state['current_stage']=LAST_CAMPAIGN_STAGE
            db.execute("""UPDATE player_profiles SET data=?,updated_at=?
                          WHERE uid=? AND server_id=?""",
                       (json.dumps(state,ensure_ascii=False,separators=(',',':')),now,uid,server_id))
            mail_id='ACTION-'+uuid.uuid4().hex[:16].upper()
            state_changed=True
        else:
            # Item giftcodes keep the original Mail > Claim Attachment flow.
            mail_id='MAIL-'+uuid.uuid4().hex[:16].upper()
            db.execute("""INSERT INTO mail
                (id,uid,server_id,character_name,title,body,attachments,status,created_at,operator)
                VALUES(?,?,?,?,?,?,?,'pending',?,'GIFTCODE')""",
                (mail_id,uid,server_id,profile['character_name'],row['title'],row['message'],
                 json.dumps(rewards,ensure_ascii=False),now))
        db.execute("""INSERT INTO giftcode_redemptions(code,uid,server_id,mail_id,redeemed_at)
                   VALUES(?,?,?,?,?)""",(code,uid,server_id,mail_id,now))
        cur=db.execute("""UPDATE giftcodes SET used_count=used_count+1
                          WHERE code=? AND (max_uses=0 OR used_count<max_uses) AND active=1""",(code,))
        if cur.rowcount!=1:
            raise ValueError('Giftcode đã hết lượt sử dụng')
        live_service._audit(db,'giftcode.redeem',code,
            {'uid':uid,'server_id':server_id,'mail_id':mail_id,'effect':effect,
             'max_stage':LAST_CAMPAIGN_STAGE if effect=='campaign_all' else None},'PLAYER')
        db.commit()
        if effect=='campaign_all':
            return {'ok':True,'action_id':mail_id,'title':row['title'],
                    'effect':effect,'state_changed':state_changed,
                    'max_stage':LAST_CAMPAIGN_STAGE,
                    'message':f'Kích hoạt thành công! Đã mở đủ {LAST_CAMPAIGN_STAGE} ải Chiến Dịch.'}
        return {'ok':True,'mail_id':mail_id,'title':row['title'],
                'message':('Đã gửi Chìa Khóa S4 đúng mốc vào Hòm Thư! '
                           'Nhận chìa, kích hoạt ở Túi Đồ để được tự phát Quà Tri Ân S4.'
                           if effect=='s4_trial_key' else
                           'Đã gửi Quà Wish Limited 25★ vào Hòm Thư S4. '
                           'Nhận thư để xem hiệu ứng Triệu Hồi Wish!'
                           if effect=='s4_wish_bundle' else
                           'Đổi mã thành công! Mở Hòm Thư để nhận đính kèm.')}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
