"""Audio-only LiveKit SFU bridge. Tokens are short-lived and never logged.
The game server, not the client, controls publishing permissions and seats.
"""
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import threading
import time
import urllib.request
import urllib.error
from . import social_arena, social_bar

CREDENTIALS=Path('/etc/gxb3-voice/credentials.json')
PUBLIC_URL='wss://180-93-111-99.sslip.io/voice'
RPC='http://127.0.0.1:7880/twirp/livekit.RoomService/'
LEASE=35
TOKEN_TTL=20
MAX_SEATS=8
MAX_GLOBAL_SESSIONS=48
_lock=threading.RLock()
_leases={}
_watchdog=None

def enabled():
    return os.getenv('GXB3_SOCIAL_VOICE_ENABLED','0')=='1' and CREDENTIALS.is_file()

def _credentials():
    return json.loads(CREDENTIALS.read_text())

def _b64(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b'=').decode('ascii')

def token(identity,video,name='',ttl=TOKEN_TTL):
    cfg=_credentials();now=int(time.time())
    payload={'iss':cfg['key'],'sub':identity,'nbf':now-2,'exp':now+ttl,'video':video}
    if name:payload['name']=name
    content=_b64(b'{"alg":"HS256","typ":"JWT"}')+'.'+_b64(json.dumps(payload,separators=(',',':')).encode())
    return content+'.'+_b64(hmac.new(cfg['secret'].encode(),content.encode(),hashlib.sha256).digest())

def rpc(method,room,**kwargs):
    grant={'roomList':True} if method=='ListRooms' else {'roomAdmin':True,'room':room}
    jwt=token('gxb3-room-service',grant,ttl=15)
    payload=kwargs if method=='ListRooms' else {'room':room,**kwargs}
    req=urllib.request.Request(RPC+method,json.dumps(payload).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+jwt})
    try:
        with urllib.request.urlopen(req,timeout=2) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code==404:return None
        raise ValueError('Dịch vụ Voice chưa phản hồi') from None
    except (OSError,ValueError):
        raise ValueError('Không kết nối được Voice') from None

def _room(kind,rid):
    return 'gxb3-'+kind+'-'+hashlib.sha256(rid.encode()).hexdigest()[:36]

def _identity(uid,world):
    return world+':'+uid+':'+secrets.token_hex(8)

def permission(mic):
    return {'canSubscribe':True,'canPublish':bool(mic),'canPublishData':False,'canPublishSources':['MICROPHONE']}

def authorize(kind,rid,uid,world,admin=False):
    """Return mic eligibility after checking the exact authenticated membership."""
    if not isinstance(rid,str) or not 1<=len(rid)<=64:raise ValueError('Phòng Voice không hợp lệ')
    now=int(time.time())
    if kind=='bar' and social_bar.enabled():
        with social_bar.transaction() as db:
            r=social_bar._room(db,rid)
            social_bar._member(db,rid,uid,world,now)
            return (not r['mic_locked'] or social_bar._owner(r,uid,world,admin)) and not social_bar._sanction(db,rid,uid,'mic',now)
    if kind=='arena' and social_arena.enabled():
        if world!='S5':raise ValueError('Chỉ dành cho S5')
        with social_arena.transaction() as (state,db):
            m=state['matches'].get(rid)
            if not m or uid not in m['uids'] or m['status'] not in ('preview','ready','running','viewing'):
                raise ValueError('Bạn không thuộc trận Giao Lưu đang mở')
            return True
    raise ValueError('Phòng Voice chưa mở')

def _remove(key,lease):
    # Keep failed revocations in the registry; the watchdog retries instead
    # of freeing the seat while an unrevoked publisher may still be online.
    try:
        rpc('RemoveParticipant',lease['room'],identity=lease['identity'])
    except ValueError:
        lease['expires']=0
        return False
    _leases.pop(key,None)
    return True

def _reap():
    now=time.monotonic()
    for key,l in list(_leases.items()):
        if l['expires']<=now:
            _remove(key,l)

def _watch():
    tick=0
    while True:
        time.sleep(5)
        with _lock:
            _reap()
            tick+=1
            if tick%3:continue
            # Reconcile after restart or stale reconnect. Only these game-room
            # prefixes belong to this bridge; never touch other rooms.
            try:
                rooms=rpc('ListRooms','') or {}
                for room in rooms.get('rooms',[]):
                    name=room.get('name','')
                    if not name.startswith(('gxb3-bar-','gxb3-arena-')):continue
                    people=rpc('ListParticipants',name) or {}
                    for participant in people.get('participants',[]):
                        identity=participant.get('identity','')
                        lease=_leases.get((name,identity))
                        if not lease or lease['expires']<=time.monotonic():
                            rpc('RemoveParticipant',name,identity=identity)
            except ValueError:
                pass

def _start():
    global _watchdog
    if _watchdog is None:
        _watchdog=threading.Thread(target=_watch,daemon=True,name='gxb3-voice-lease')
        _watchdog.start()

def startup():
    if enabled():
        with _lock:_start()

def join(kind,rid,uid,world,name,admin=False):
    if not enabled():raise ValueError('Voice chưa mở')
    with _lock:
        authorize(kind,rid,uid,world,admin)
        _reap()
        ident=_identity(uid,world);room=_room(kind,rid);key=(room,ident)
        for old,l in list(_leases.items()):
            if l['uid']==uid and not _remove(old,l):raise ValueError('Chưa đóng phiên Voice cũ')
        if len(_leases)>=MAX_GLOBAL_SESSIONS:raise ValueError('Voice đang đầy')
        if sum(l['room']==room for l in _leases.values())>=32:raise ValueError('Phòng Voice đã đầy')
        lease={'uid':uid,'world':world,'identity':ident,'room':room,'lease':secrets.token_urlsafe(24),'mic':False,'expires':time.monotonic()+LEASE}
        _leases[key]=lease
        _start()
        grant={'roomJoin':True,'room':room,'canSubscribe':True,'canPublish':False,'canPublishData':False,'canPublishSources':['microphone']}
        return {'url':PUBLIC_URL,'token':token(ident,grant,name),'lease':lease['lease'],'mic':False}

def control(kind,rid,uid,world,lease_id,action,admin=False):
    if not enabled():raise ValueError('Voice chưa mở')
    if not isinstance(lease_id,str) or len(lease_id)>80:raise ValueError('Phiên Voice không hợp lệ')
    room=_room(kind,rid)
    with _lock:
        _reap()
        key=next((k for k,l in _leases.items() if l['room']==room and l['uid']==uid and l['world']==world and hmac.compare_digest(l['lease'],lease_id)),None)
        l=_leases.get(key)
        if not l:raise ValueError('Phiên Voice đã hết hạn')
        ident=l['identity']
        if action=='leave':
            _remove(key,l);return {'ok':True}
        try:allowed=authorize(kind,rid,uid,world,admin)
        except ValueError:
            _remove(key,l);raise
        if action not in ('heartbeat','mic_on','mic_off'):raise ValueError('Thao tác Voice không hợp lệ')
        if action=='mic_on' and not allowed:raise ValueError('Bạn chưa được phép bật Mic')
        desired=(action=='mic_on' or (l['mic'] and action!='mic_off')) and bool(allowed)
        if desired and not l['mic'] and sum(x['room']==room and x['mic'] for x in _leases.values())>=MAX_SEATS:
            raise ValueError('Đã đủ 8 ghế Voice')
        if desired!=l['mic']:
            reply=rpc('UpdateParticipant',room,identity=ident,permission=permission(desired))
            if reply is None:raise ValueError('Chưa kết nối vào phòng Voice')
            l['mic']=desired
        l['expires']=time.monotonic()+LEASE
        return {'mic':l['mic'],'speakers':sum(x['room']==room and x['mic'] for x in _leases.values()),'seats':MAX_SEATS}
