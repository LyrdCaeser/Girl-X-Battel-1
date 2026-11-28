"""Short-lived, match-scoped text and audio relay. No voice recordings on disk."""
import base64
import threading
import time
from collections import deque
from . import live_service

_lock = threading.RLock()
_rooms = {}
MAX_ROOMS = 64

def exchange(uid, world, data):
    match_id = str(data.get('match_id') or '')
    db=live_service._db()
    try:
        match=db.execute('SELECT player_a,player_b,server_a,server_b,mode,status,resolved_at,challenge_uid FROM pvp_matches WHERE id=?',(match_id,)).fetchone()
    finally:db.close()
    if not match or not ((match['player_a']==uid and match['server_a']==world) or (match['player_b']==uid and match['server_b']==world)):
        raise ValueError('Bạn không thuộc trận So Tài này')
    if 'S5' in (match['server_a'],match['server_b']) and (match['server_a']!=match['server_b'] or match['mode']=='cross'):
        raise ValueError('S5 không mở Đấu Trường Liên Server')
    match=dict(match)
    now = time.time()
    if (not str(match.get('challenge_uid','')).startswith('LIVE:') or
        match['status'] not in ('active','finished') or
        (match['status']=='finished' and now-int(match['resolved_at'])>600)):
        raise ValueError('Kênh trò chuyện chỉ mở trong trận So Tài đã đồng ý')
    kind=data.get('kind','poll')
    if kind not in ('poll','text','audio'):raise ValueError('Loại tin nhắn không hợp lệ')
    if kind=='text':
        payload=data.get('text')
        if not isinstance(payload,str) or not 1<=len(payload.strip())<=300:
            raise ValueError('Tin nhắn cần từ 1–300 ký tự')
        payload=payload.strip()
    elif kind=='audio':
        payload=data.get('audio')
        mime=data.get('mime')
        if mime not in ('audio/webm','audio/webm;codecs=opus','audio/ogg','audio/ogg;codecs=opus','audio/mp4'):
            raise ValueError('Định dạng âm thanh không hỗ trợ')
        if not isinstance(payload,str) or len(payload)>48000:raise ValueError('Âm thanh quá dài')
        try:
            if not base64.b64decode(payload,validate=True):raise ValueError()
        except Exception:raise ValueError('Âm thanh không hợp lệ')
    try:cursor=max(0,int(data.get('after',0)))
    except (ValueError,TypeError):raise ValueError('Mốc tin nhắn không hợp lệ')
    with _lock:
        for key,room in list(_rooms.items()):
            if now-room['last']>90:del _rooms[key]
        if match_id not in _rooms:
            if len(_rooms)>=MAX_ROOMS:raise ValueError('Kênh thoại đang bận')
            _rooms[match_id]={'last':now,'seq':int(now*1000),'events':deque(maxlen=100),'rate':{}}
        room=_rooms[match_id];room['last']=now
        room['events']=deque((e for e in room['events'] if now-e['at']<(12 if e['kind']=='audio' else 90)),maxlen=100)
        if kind!='poll':
            k=(uid,kind)
            if now-room['rate'].get(k,0)<(0.6 if kind=='audio' else 0.8):raise ValueError('Gửi quá nhanh')
            room['rate'][k]=now;room['seq']+=1
            event={'id':room['seq'],'uid':uid,'kind':kind,'at':now}
            if kind=='audio':event.update(audio=payload,mime=mime)
            else:event['text']=payload
            room['events'].append(event)
            # Bound per-room memory and never replay stale voice.
            while sum(len(e.get('audio','')) for e in room['events'])>480000:room['events'].popleft()
        events=[e for e in room['events'] if e['id']>cursor and (e['kind']=='text' or (e['uid']!=uid and now-e['at']<5))]
        return {'events':events[:30],'after':events[min(len(events),30)-1]['id'] if events else max(cursor,room['seq'])}
