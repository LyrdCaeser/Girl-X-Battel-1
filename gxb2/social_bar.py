"""Authenticated room and chat core, independent of battle and economy.
Voice transport is deliberately not enabled by this module.
"""
import base64
import hashlib
import hmac
import io
import json
import os
import re
import secrets
import threading
import time
from contextlib import contextmanager
from . import live_service

WORLDS=('S1','S2','S3','S4','S5')
TTL=45
RETENTION=30*86400
MAX_LISTENERS=32
MAX_MIC=8
MAX_IMAGE=180_000
MAX_IMAGES_TOTAL=100*1024*1024
_lock=threading.RLock()
_ready=set()

def enabled():
    return os.environ.get('GXB3_SOCIAL_BAR_ENABLED','0')=='1'

def _schema(db):
    live_service._ensure_social_tables(db)
    statements=(
      """CREATE TABLE IF NOT EXISTS social_bar_rooms(id TEXT PRIMARY KEY, name TEXT NOT NULL, scope TEXT NOT NULL,
        kind TEXT NOT NULL, owner_uid TEXT NOT NULL, owner_world TEXT NOT NULL, password TEXT NOT NULL,
        guild_id TEXT NOT NULL, created_at BIGINT NOT NULL, closed INTEGER NOT NULL DEFAULT 0, mic_locked INTEGER NOT NULL DEFAULT 0)""",
      """CREATE TABLE IF NOT EXISTS social_bar_members(room_id TEXT NOT NULL, uid TEXT NOT NULL, world TEXT NOT NULL,
        name TEXT NOT NULL, last_seen BIGINT NOT NULL, mic INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(room_id,uid,world))""",
      """CREATE TABLE IF NOT EXISTS social_bar_messages(id TEXT PRIMARY KEY,room_id TEXT NOT NULL,
        uid TEXT NOT NULL,world TEXT NOT NULL,name TEXT NOT NULL,kind TEXT NOT NULL,text TEXT NOT NULL,
        image TEXT NOT NULL,created_at BIGINT NOT NULL,reply_to TEXT NOT NULL,deleted INTEGER NOT NULL DEFAULT 0)""",
      """CREATE TABLE IF NOT EXISTS social_bar_invites(room_id TEXT NOT NULL,uid TEXT NOT NULL,world TEXT NOT NULL,
        PRIMARY KEY(room_id,uid,world))""",
      """CREATE TABLE IF NOT EXISTS social_bar_blocks(uid TEXT NOT NULL,target_uid TEXT NOT NULL,PRIMARY KEY(uid,target_uid))""",
      """CREATE TABLE IF NOT EXISTS social_bar_sanctions(room_id TEXT NOT NULL,uid TEXT NOT NULL,kind TEXT NOT NULL,
        until_at BIGINT NOT NULL,PRIMARY KEY(room_id,uid,kind))""",
      """CREATE TABLE IF NOT EXISTS social_bar_reports(id TEXT PRIMARY KEY,room_id TEXT NOT NULL,reporter TEXT NOT NULL,
        message_id TEXT NOT NULL,reason TEXT NOT NULL,created_at BIGINT NOT NULL,status TEXT NOT NULL)""",
      'CREATE INDEX IF NOT EXISTS social_bar_message_room_time ON social_bar_messages(room_id,created_at,id)',
      'CREATE INDEX IF NOT EXISTS social_bar_member_time ON social_bar_members(last_seen)',
    )
    for sql in statements:db.execute(sql)
    now=int(time.time())
    for scope in (*WORLDS,'CROSS'):
        rid='public:'+scope
        db.execute("""INSERT INTO social_bar_rooms(id,name,scope,kind,owner_uid,owner_world,password,guild_id,created_at)
            VALUES(?,?,?,'public','','','','',?) ON CONFLICT(id) DO NOTHING""",
            (rid,'Phòng Liên Server' if scope=='CROSS' else 'Phòng Server '+scope,scope,now))
    db.commit()

@contextmanager
def transaction():
    with _lock:
        db=live_service._db()
        try:
            if db.identity not in _ready:
                _schema(db);_ready.add(db.identity)
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except Exception:
            db.rollback();raise
        finally:db.close()

def _room(db,rid):
    r=db.execute(live_service._for_update(db,'SELECT * FROM social_bar_rooms WHERE id=?'),(str(rid),)).fetchone()
    if not r or r['closed']:raise ValueError('Phòng không còn mở')
    return r

def _check_world(world):
    if world not in WORLDS:raise ValueError('Máy chủ không hợp lệ')

def _password(raw):
    if not raw:return ''
    if not isinstance(raw,str) or not 4<=len(raw)<=64:raise ValueError('Mật khẩu phòng từ 4 đến 64 ký tự')
    salt=secrets.token_hex(16)
    digest=hashlib.pbkdf2_hmac('sha256',raw.encode(),bytes.fromhex(salt),180000).hex()
    return salt+':'+digest

def _password_ok(stored,raw):
    if not stored or not isinstance(raw,str) or len(raw)>64:return False
    salt,digest=stored.split(':')
    actual=hashlib.pbkdf2_hmac('sha256',raw.encode(),bytes.fromhex(salt),180000).hex()
    return hmac.compare_digest(actual,digest)

def _guild(db,uid,world):
    r=db.execute('SELECT guild_id FROM world_guild_members WHERE uid=? AND server_id=?',(uid,world)).fetchone()
    return str(r['guild_id']) if r else ''

def _sanction(db,rid,uid,kind,now):
    return db.execute("SELECT 1 FROM social_bar_sanctions WHERE room_id IN (?, '*') AND uid=? AND kind=? AND until_at>?",(rid,uid,kind,now)).fetchone()

def _member(db,rid,uid,world,now):
    if not db.execute('SELECT 1 FROM social_bar_members WHERE room_id=? AND uid=? AND world=? AND last_seen>?',(rid,uid,world,now-TTL)).fetchone():
        raise ValueError('Hãy vào phòng trước')
    if _sanction(db,rid,uid,'kick',now):raise ValueError('Bạn đang bị hạn chế vào phòng')
    r=db.execute('SELECT * FROM social_bar_rooms WHERE id=?',(rid,)).fetchone()
    if not r or r['closed'] or r['scope'] not in (world,'CROSS'):raise ValueError('Phòng không còn mở')
    if r['kind']=='guild' and _guild(db,uid,world)!=r['guild_id']:raise ValueError('Bạn không còn trong Bang Hội')
    if r['kind']=='friends' and not _owner(r,uid,world,False) and not live_service._are_friends(db,uid,r['owner_uid'],world):raise ValueError('Bạn không còn là Bạn Bè')

def _owner(r,uid,world,admin):
    return admin or (r['owner_uid']==uid and r['owner_world']==world)

def _clean_room(r):
    return {k:r[k] for k in ('id','name','scope','kind','owner_uid','owner_world','mic_locked')}

def rooms(uid,world,now=None):
    _check_world(world);now=int(time.time() if now is None else now)
    with transaction() as db:
        rows=db.execute("""SELECT r.*, (SELECT COUNT(*) FROM social_bar_members m
            WHERE m.room_id=r.id AND m.last_seen>?) AS online FROM social_bar_rooms r
            WHERE r.closed=0 AND r.scope IN (?, 'CROSS') ORDER BY r.kind,r.created_at DESC LIMIT 100""",
            (now-TTL,world)).fetchall()
        return [{**_clean_room(r),'online':r['online'],'locked':bool(r['password']) or r['kind']=='private'} for r in rows]

def create(uid,world,name,scope,kind,password='',admin=False,now=None):
    _check_world(world);now=int(time.time() if now is None else now)
    name=str(name or '').strip()
    if not 1<=len(name)<=48 or kind not in ('public','private','guild','friends','gm'):raise ValueError('Tên hoặc loại phòng không hợp lệ')
    if scope not in (world,'CROSS') or kind in ('guild','friends') and scope!=world:raise ValueError('Phạm vi phòng không hợp lệ')
    if kind=='gm' and not admin:raise ValueError('Chỉ QTV được tạo phòng QTV')
    pw=_password(password) if kind=='private' else ''
    with transaction() as db:
        owned=db.execute('SELECT COUNT(*) AS n FROM social_bar_rooms WHERE owner_uid=? AND closed=0',(uid,)).fetchone()['n']
        if owned>=3:raise ValueError('Tối đa 3 phòng đang mở mỗi tài khoản')
        guild=_guild(db,uid,world) if kind=='guild' else ''
        if kind=='guild' and not guild:raise ValueError('Bạn chưa gia nhập Bang Hội')
        rid='room:'+secrets.token_hex(10)
        db.execute("""INSERT INTO social_bar_rooms(id,name,scope,kind,owner_uid,owner_world,password,guild_id,created_at)
            VALUES(?,?,?,?,?,?,?,?,?)""",(rid,name,scope,kind,uid,world,pw,guild,now))
        return rid

def enter(uid,world,name,rid,password='',admin=False,now=None):
    _check_world(world);now=int(time.time() if now is None else now)
    with transaction() as db:
        r=_room(db,rid)
        if r['scope'] not in (world,'CROSS'):raise ValueError('Phòng thuộc máy chủ khác')
        if _sanction(db,rid,uid,'kick',now):raise ValueError('Bạn đang bị hạn chế vào phòng')
        if r['kind']=='guild' and _guild(db,uid,world)!=r['guild_id']:raise ValueError('Chỉ thành viên cùng Bang Hội')
        if not _owner(r,uid,world,admin):
            if r['kind']=='friends' and not live_service._are_friends(db,uid,r['owner_uid'],world):raise ValueError('Chỉ Bạn Bè của chủ phòng')
            if r['kind']=='private':
                invited=db.execute('SELECT 1 FROM social_bar_invites WHERE room_id=? AND uid=? AND world=?',(rid,uid,world)).fetchone()
                if not invited and not _password_ok(r['password'],password):raise ValueError('Cần mật khẩu hoặc lời mời')
        active=db.execute('SELECT COUNT(*) AS n FROM social_bar_members WHERE room_id=? AND last_seen>? AND NOT(uid=? AND world=?)',(rid,now-TTL,uid,world)).fetchone()['n']
        if active>=MAX_LISTENERS:raise ValueError('Phòng đã đầy')
        db.execute('DELETE FROM social_bar_members WHERE uid=? AND world=?',(uid,world))
        db.execute('INSERT INTO social_bar_members(room_id,uid,world,name,last_seen,mic) VALUES(?,?,?,?,?,0)',(rid,uid,world,name,now))
        return _clean_room(r)

def leave(uid,world,rid):
    with transaction() as db:db.execute('DELETE FROM social_bar_members WHERE room_id=? AND uid=? AND world=?',(rid,uid,world))

def _normalize_image(raw):
    from PIL import Image,ImageOps
    if not isinstance(raw,str) or len(raw)>650_000:raise ValueError('Ảnh gửi lên quá lớn')
    try:
        payload=base64.b64decode(raw,validate=True)
        with Image.open(io.BytesIO(payload)) as im:
            if im.format not in ('PNG','JPEG','WEBP') or im.width*im.height>12_000_000:raise ValueError()
            im=ImageOps.exif_transpose(im).convert('RGB')
            im.thumbnail((960,960))
            out=io.BytesIO();im.save(out,'WEBP',quality=76,method=4)
            if len(out.getvalue())>MAX_IMAGE:
                out=io.BytesIO();im.thumbnail((640,640));im.save(out,'WEBP',quality=60)
            if len(out.getvalue())>MAX_IMAGE:raise ValueError()
            return base64.b64encode(out.getvalue()).decode('ascii')
    except Exception:raise ValueError('Ảnh không hợp lệ hoặc quá lớn') from None

def send(uid,world,name,rid,text='',image='',reply_to='',now=None):
    now=int(time.time() if now is None else now)
    text=str(text or '').strip();reply_to=str(reply_to or '')
    if len(text)>500 or not(text or image):raise ValueError('Tin nhắn cần có nội dung, tối đa 500 ký tự')
    encoded=_normalize_image(image) if image else ''
    with transaction() as db:
        r=_room(db,rid);_member(db,rid,uid,world,now)
        if _sanction(db,rid,uid,'chat',now):raise ValueError('Bạn đang bị cấm chat')
        recent=db.execute('SELECT MAX(created_at) AS at FROM social_bar_messages WHERE uid=? AND world=? AND room_id=?',(uid,world,rid)).fetchone()['at']
        if recent is not None and now-int(recent)<2:raise ValueError('Gửi tin nhắn quá nhanh')
        if reply_to and not db.execute('SELECT 1 FROM social_bar_messages WHERE id=? AND room_id=? AND deleted=0',(reply_to,rid)).fetchone():raise ValueError('Tin nhắn trả lời không hợp lệ')
        db.execute('DELETE FROM social_bar_messages WHERE created_at<?',(now-RETENTION,))
        if encoded:
            total=db.execute("SELECT COALESCE(SUM(LENGTH(image)),0) AS n FROM social_bar_messages WHERE image<>''").fetchone()['n']
            if int(total)+len(encoded)>MAX_IMAGES_TOTAL:raise ValueError('Kho ảnh tạm đầy')
        mid=secrets.token_hex(16)
        db.execute("""INSERT INTO social_bar_messages(id,room_id,uid,world,name,kind,text,image,created_at,reply_to)
            VALUES(?,?,?,?,?,?,?,?,?,?)""",(mid,rid,uid,world,name,'image' if encoded else 'text',text,encoded,now,reply_to))
        return mid

def _attach_portraits(db, rows):
    # Read only public appearance, in one bounded query keyed by character
    # (account UID + world). Never ship private profile JSON to room clients.
    keys=sorted({(r['uid'],r['world']) for r in rows})
    portraits={}
    if keys:
        if db.backend=='postgres':
            fields="data::jsonb->'profile'->>'avatar' AS avatar, data::jsonb->'profile'->>'frame' AS frame"
        else:
            fields="json_extract(data,'$.profile.avatar') AS avatar, json_extract(data,'$.profile.frame') AS frame"
        where=' OR '.join('(uid=? AND server_id=?)' for _ in keys)
        for r in db.execute('SELECT uid,server_id,'+fields+' FROM player_profiles WHERE '+where,
                            tuple(v for pair in keys for v in pair)).fetchall():
            avatar=str(r['avatar'] or '')
            frame=str(r['frame'] or '')
            if not re.fullmatch(r'(?:head|partner_avatar)_\d{4,9}|custom_[0-9a-f]{32}',avatar):avatar='head_1001'
            if not re.fullmatch(r'frame_\d{4,9}',frame):frame='frame_8007'
            portraits[(r['uid'],r['server_id'])]=(avatar,frame)
    for row in rows:
        row['avatar'],row['frame']=portraits.get((row['uid'],row['world']),('head_1001','frame_8007'))


def poll(uid,world,rid,now=None):
    now=int(time.time() if now is None else now)
    with transaction() as db:
        r=_room(db,rid);_member(db,rid,uid,world,now)
        if r['kind']=='guild' and not _owner(r,uid,world,False) and _guild(db,uid,world)!=r['guild_id']:raise ValueError('Bạn không còn trong Bang Hội')
        if r['kind']=='friends' and not _owner(r,uid,world,False) and not live_service._are_friends(db,uid,r['owner_uid'],world):raise ValueError('Bạn không còn là Bạn Bè')
        db.execute('UPDATE social_bar_members SET last_seen=? WHERE room_id=? AND uid=? AND world=? AND last_seen<?',(now,rid,uid,world,now-10))
        blocked={x['target_uid'] for x in db.execute('SELECT target_uid FROM social_bar_blocks WHERE uid=?',(uid,)).fetchall()}
        members=[dict(x) for x in db.execute('SELECT uid,world,name,mic FROM social_bar_members WHERE room_id=? AND last_seen>? ORDER BY name',(rid,now-TTL)).fetchall()]
        messages=[dict(x) for x in db.execute("""SELECT id,uid,world,name,kind,text,created_at,reply_to
            FROM social_bar_messages WHERE room_id=? AND deleted=0 AND created_at>? ORDER BY created_at DESC,id DESC LIMIT 50""",(rid,now-RETENTION)).fetchall() if x['uid'] not in blocked]
        _attach_portraits(db,members+messages)
        return {'room':_clean_room(r),'members':members,'messages':list(reversed(messages)),
                'blocked':list(blocked),'voice_enabled':False,'server_time':now}

def image(uid,world,rid,mid,now=None):
    now=int(time.time() if now is None else now)
    with transaction() as db:
        _room(db,rid);_member(db,rid,uid,world,now)
        r=db.execute("""SELECT image FROM social_bar_messages WHERE id=? AND room_id=? AND deleted=0 AND created_at>?
            AND uid NOT IN (SELECT target_uid FROM social_bar_blocks WHERE uid=?)""",(mid,rid,now-RETENTION,uid)).fetchone()
        if not r or not r['image']:raise ValueError('Không tìm thấy ảnh')
        return r['image']

def action(uid,world,rid,kind,target='',target_world='',mid='',reason='',admin=False,now=None):
    now=int(time.time() if now is None else now)
    with transaction() as db:
        r=_room(db,rid);_member(db,rid,uid,world,now)
        owner=_owner(r,uid,world,admin)
        if kind=='block':
            if target==uid:raise ValueError('Không thể chặn chính mình')
            db.execute('INSERT INTO social_bar_blocks(uid,target_uid) VALUES(?,?) ON CONFLICT(uid,target_uid) DO NOTHING',(uid,target))
        elif kind=='unblock':db.execute('DELETE FROM social_bar_blocks WHERE uid=? AND target_uid=?',(uid,target))
        elif kind=='report':
            if not db.execute('SELECT 1 FROM social_bar_messages WHERE room_id=? AND id=?',(rid,mid)).fetchone():raise ValueError('Tin nhắn không tồn tại')
            db.execute("INSERT INTO social_bar_reports(id,room_id,reporter,message_id,reason,created_at,status) VALUES(?,?,?,?,?,?,'pending')",
                       (secrets.token_hex(12),rid,uid,mid,str(reason)[:300],now))
        elif kind=='delete':
            msg=db.execute('SELECT uid,world FROM social_bar_messages WHERE room_id=? AND id=?',(rid,mid)).fetchone()
            if not msg or not (owner or msg['uid']==uid and msg['world']==world):raise ValueError('Không có quyền thu hồi')
            db.execute("UPDATE social_bar_messages SET deleted=1,image='',text='' WHERE id=? AND room_id=?",(mid,rid))
        else:
            if not owner:raise ValueError('Chỉ chủ phòng hoặc QTV')
            if kind=='invite':
                if r['scope'] not in (target_world,'CROSS') or target_world not in WORLDS:raise ValueError('Sai phạm vi máy chủ')
                if not db.execute("SELECT 1 FROM players WHERE uid=? AND server_id=? AND status='active'",(target,target_world)).fetchone():raise ValueError('Không tìm thấy người chơi')
                db.execute('INSERT INTO social_bar_invites(room_id,uid,world) VALUES(?,?,?) ON CONFLICT(room_id,uid,world) DO NOTHING',(rid,target,target_world))
            elif kind in ('kick','chat','mic'):
                if not target or target==r['owner_uid']:raise ValueError('Không thể hạn chế chủ phòng')
                db.execute('INSERT INTO social_bar_sanctions(room_id,uid,kind,until_at) VALUES(?,?,?,?) ON CONFLICT(room_id,uid,kind) DO UPDATE SET until_at=excluded.until_at',(rid,target,kind,now+600))
                if kind=='kick':db.execute('DELETE FROM social_bar_members WHERE room_id=? AND uid=?',(rid,target))
                if kind=='mic':db.execute('UPDATE social_bar_members SET mic=0 WHERE room_id=? AND uid=?',(rid,target))
            elif kind=='close':
                if rid.startswith('public:'):raise ValueError('Không thể giải tán phòng mặc định')
                db.execute('UPDATE social_bar_rooms SET closed=1 WHERE id=?',(rid,))
                db.execute('DELETE FROM social_bar_members WHERE room_id=?',(rid,))
            else:raise ValueError('Thao tác không hợp lệ')
        return {'ok':True}
