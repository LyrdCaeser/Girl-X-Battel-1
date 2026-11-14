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
from . import gm_catalog, live_service

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
                        created_at BIGINT NOT NULL, created_by TEXT NOT NULL)""")
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
            (code,title,message,rewards,server_id,max_uses,used_count,expires_at,active,created_at,created_by)
            VALUES(?,?,?,?,?,?,0,?,1,?,?)""",
            (code,title,message,json.dumps(rewards,ensure_ascii=False),world,
             max_uses,expires_at,now,str(operator)[:100]))
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
        if int(row['max_uses']) and int(row['used_count'])>=int(row['max_uses']):
            raise ValueError('Giftcode đã hết lượt sử dụng')
        rewards=json.loads(row['rewards'])
        # Reward catalog was validated on creation; mail still validates ownership
        # and the final item application occurs only at Mail > Claim Attachment.
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
        live_service._audit(db,'giftcode.redeem',code,{'uid':uid,'server_id':server_id,'mail_id':mail_id},'PLAYER')
        db.commit()
        return {'ok':True,'mail_id':mail_id,'title':row['title'],
                'message':'Đổi mã thành công! Mở Hòm Thư để nhận đính kèm.'}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
