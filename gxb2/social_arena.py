"""S5 tournament rules and persistent, isolated matchmaking core.

No writes to regular arena, inventory, or player profiles. Not exposed until
the tournament UI, authenticated integration and referee controls pass QA.
"""
import json
import random
import secrets
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from contextlib import contextmanager
from . import live_service, s5_test
from .battle import simulate, normalize_online_seed

TZ=ZoneInfo('Asia/Ho_Chi_Minh')
EVENT='S5-20261128'
def stamp(hour, minute=0):
    return int(datetime(2026,11,28,hour,minute,tzinfo=TZ).timestamp())
START=stamp(20)
QUEUE_END=stamp(22,50)
END=stamp(23)
INITIAL=100
DELTA=20
QUEUE_TTL=35
ACCEPT_TTL=20
PREVIEW=5
BEGIN_TTL=25
rng=random.SystemRandom()

def phase(now):
    return 'waiting' if now<START else 'open' if now<QUEUE_END else 'closing' if now<END else 'closed'

def validate_snapshot(snap, uid):
    if snap.get('uid')!=uid or snap.get('server_id')!='S5':
        raise ValueError('Đội hình không thuộc nhân vật S5')
    team=snap.get('team')
    if not isinstance(team,list) or not 1<=len(team)<=6:
        raise ValueError('Đội hình cần từ 1 đến 6 Nữ Thần')
    if any(int(p['table_id'])==s5_test.SONIA for p in team):
        raise ValueError('Lyr Sonia không được tham chiến Giao Lưu')
    positions=[int(p['pos']) for p in team]
    if len(set(positions))!=len(team) or any(not 1<=p<=6 for p in positions):
        raise ValueError('Vị trí đội hình không hợp lệ')
    return json.loads(json.dumps(snap))

def round_points(report):
    # At the round cap, both surviving sides draw, regardless of native
    # campaign defeat-on-timeout flag. No third tiebreak battle.
    if int(report.get('total_round',0))>20:
        raise ValueError('Vượt quá 20 hiệp')
    status=report.get('end_status')
    if not isinstance(status,list) or not status:
        raise ValueError('Thiếu trạng thái kết thúc trận')
    a=any(1<=int(u['pos'])<=6 and int(u['hp'])>0 for u in status)
    b=any(7<=int(u['pos'])<=12 and int(u['hp'])>0 for u in status)
    if a==b:
        return (1,1)
    return (1,0) if a else (0,1)

def match_points(reports):
    if len(reports)!=2:raise ValueError('Cần đủ hai lượt đối đầu')
    scores=[round_points(r) for r in reports]
    return [sum(x[i] for x in scores) for i in (0,1)]

def simulate_pair(a,b,battle_id,seed):
    return simulate(a['team'],b['team'],battle_id=battle_id,
                    seed=normalize_online_seed(seed),max_round=20,battle_type=1,
                    pet_a=a.get('pet'),pet_b=b.get('pet'),
                    guild_skills_a=a.get('guild_skills') or [],
                    guild_skills_b=b.get('guild_skills') or [],
                    chime_bonus_a=a.get('chime_bonus') or [],
                    chime_bonus_b=b.get('chime_bonus') or [])

def _schema(db):
    db.execute("""CREATE TABLE IF NOT EXISTS social_arena_events
        (id TEXT PRIMARY KEY, state TEXT NOT NULL)""")
    db.execute("""CREATE TABLE IF NOT EXISTS social_arena_reports
        (event_id TEXT NOT NULL, match_id TEXT NOT NULL, round_no INTEGER NOT NULL,
         report TEXT NOT NULL, PRIMARY KEY(event_id,match_id,round_no))""")
    db.execute("""CREATE TABLE IF NOT EXISTS social_arena_awards
        (event_id TEXT NOT NULL, uid TEXT NOT NULL, rank INTEGER NOT NULL,
         mail_id TEXT NOT NULL UNIQUE, PRIMARY KEY(event_id,uid), UNIQUE(event_id,rank))""")
    db.commit()

@contextmanager
def transaction(event=EVENT):
    db=live_service._db()
    try:
        _schema(db)
        db.execute('BEGIN IMMEDIATE')
        db.execute("INSERT INTO social_arena_events(id,state) VALUES(?,?) ON CONFLICT(id) DO NOTHING",
                   (event,json.dumps({'players':{},'queue':{},'matches':{},'closed':False})))
        row=db.execute(live_service._for_update(db,'SELECT state FROM social_arena_events WHERE id=?'),(event,)).fetchone()
        state=json.loads(row['state'])
        yield state,db
        db.execute('UPDATE social_arena_events SET state=? WHERE id=?',(json.dumps(state,separators=(',',':')),event))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:db.close()

def _record(state,uid,name):
    return state['players'].setdefault(uid,{'uid':uid,'name':name,'points':INITIAL,'wins':0,'losses':0,'draws':0,'achieved_at':0})

def _active(state,uid):
    return next((m for m in state['matches'].values() if uid in m['uids'] and m['status'] in ('accept','preview','ready','running')),None)

def _cleanup(state,now):
    for uid,q in list(state['queue'].items()):
        if now-q['at']>QUEUE_TTL or now>=QUEUE_END:
            state['queue'].pop(uid)
    for m in state['matches'].values():
        if (m['status'] in ('accept','preview','ready') and now>=min(m['deadline'],END)) or (m['status']=='running' and now-m['running_at']>90):
            m['status']='cancelled'
            m.pop('snapshots',None)

def join(uid,name,snap,*,world,admin=False,now=None):
    now=int(time.time() if now is None else now)
    if world!='S5' or admin or uid==s5_test.owner_uid():
        raise ValueError('Chỉ người chơi S5 được ghép trận')
    if phase(now)!='open':raise ValueError('Chưa mở ghép trận hoặc đã hết giờ')
    snap=validate_snapshot(snap,uid)
    with transaction() as (state,db):
        _cleanup(state,now)
        if state['closed']:raise ValueError('Giải đấu đã đóng')
        p=_record(state,uid,name)
        if p['points']<=0 or p.get('disqualified'):raise ValueError('Bạn đã bị loại khỏi giải')
        existing=_active(state,uid)
        if existing:return existing['id']
        state['queue'][uid]={'at':now,'snapshot':snap}
        if len(state['queue'])<4:return None
        others=[x for x in state['queue'] if x!=uid]
        uids=[uid]+rng.sample(others,3)
        rng.shuffle(uids)
        mid=secrets.token_hex(12)
        snapshots={u:state['queue'].pop(u)['snapshot'] for u in uids}
        state['matches'][mid]={'id':mid,'uids':uids,'status':'accept',
            'accepted':[],'started':[],'deadline':now+ACCEPT_TTL,
            'snapshots':snapshots,'seed':secrets.randbelow(233280)+1,
            'created_at':now}
        return mid

def accept(uid,mid,*,now=None):
    now=int(time.time() if now is None else now)
    with transaction() as (state,db):
        _cleanup(state,now)
        m=state['matches'].get(mid)
        if not m or uid not in m['uids'] or m['status']!='accept':
            raise ValueError('Lời mời trận không còn hiệu lực')
        if uid not in m['accepted']:m['accepted'].append(uid)
        if len(m['accepted'])==4:
            m['status']='preview';m['preview_until']=now+PREVIEW
            m['deadline']=now+PREVIEW+BEGIN_TTL
        return m['status']

def begin(uid,mid,*,now=None):
    now=int(time.time() if now is None else now)
    with transaction() as (state,db):
        _cleanup(state,now)
        m=state['matches'].get(mid)
        if not m or uid not in m['uids'] or m['status'] not in ('preview','ready'):
            raise ValueError('Trận chưa sẵn sàng')
        if now<m['preview_until']:raise ValueError('Hãy xem đội hình đủ 5 giây')
        if uid not in m['started']:m['started'].append(uid)
        if len(m['started'])==4:m['status']='ready'
        return m['status']

def cancel(uid,mid=None,*,now=None):
    now=int(time.time() if now is None else now)
    with transaction() as (state,db):
        _cleanup(state,now);state['queue'].pop(uid,None)
        m=_active(state,uid)
        if m and m['status'] in ('accept','preview','ready') and (mid is None or mid==m['id']):
            m['status']='cancelled';m.pop('snapshots',None)

def resolve(uid,mid,battle_id,*,now=None):
    """One worker owns the simulation; commits results once after both reports."""
    now=int(time.time() if now is None else now)
    with transaction() as (state,db):
        _cleanup(state,now)
        m=state['matches'].get(mid)
        if not m or uid not in m['uids']:raise ValueError('Bạn không thuộc trận')
        if m['status'] in ('finished','running'):return m['status']
        if m['status']!='ready' or now>=END:raise ValueError('Chưa đủ bốn người sẵn sàng hoặc đã hết giờ')
        m['status']='running';m['running_at']=now
        uids=list(m['uids']);snaps=m['snapshots'];seed=m['seed']
    try:
        reports=[simulate_pair(snaps[uids[i]],snaps[uids[i+2]],battle_id,seed+i*7919) for i in (0,1)]
        points=match_points(reports)
        with transaction() as (state,db):
            m=state['matches'][mid]
            if m['status']!='running':return m['status']
            for i,r in enumerate(reports):
                db.execute('INSERT INTO social_arena_reports(event_id,match_id,round_no,report) VALUES(?,?,?,?)',
                           (EVENT,mid,i,json.dumps(r,separators=(',',':'))))
            for i,u in enumerate(uids):
                p=state['players'][u];side=i//2
                d=0 if points[0]==points[1] else DELTA if points[side]>points[1-side] else -DELTA
                p['points']=max(0,p['points']+d)
                p['wins' if d>0 else 'losses' if d<0 else 'draws']+=1
                p['achieved_at']=now
            m.update(status='finished',score=points,finished_at=now)
            m.pop('snapshots',None)
            return 'finished'
    except Exception:
        with transaction() as (state,db):
            m=state['matches'][mid]
            if m['status']=='running':
                m['status']='cancelled';m.pop('snapshots',None)
        raise

def status(uid,*,now=None):
    now=int(time.time() if now is None else now)
    with transaction() as (state,db):
        _cleanup(state,now)
        p=state['players'].get(uid)
        m=_active(state,uid)
        # Refresh only a caller who actually entered the queue.
        if uid in state['queue']:state['queue'][uid]['at']=now
        board=sorted(state['players'].values(),key=lambda p:(-p['points'],-p['wins'],-p['wins']/max(1,p['wins']+p['losses']+p['draws']),p['achieved_at'],p['uid']))
        result={'event':EVENT,'phase':phase(now),'server_time':now,'queued':uid in state['queue'],
                'queue_count':len(state['queue']),'me':p,'board':[dict(x,rank=i) for i,x in enumerate(board,1)],
                'match':None}
        if m:
            result['match']={k:v for k,v in m.items() if k not in ('snapshots','seed')}
            if m['status'] in ('preview','ready','running'):
                result['match']['formations']=[{'uid':u,'name':m['snapshots'][u].get('name'),
                    'power':m['snapshots'][u].get('power'),'team':[{k:g.get(k) for k in ('table_id','level','awake','pos','skin_id')} for g in m['snapshots'][u]['team']]} for u in m['uids']]
        result['history']=[{k:v for k,v in x.items() if k not in ('snapshots','seed')} for x in state['matches'].values() if uid in x['uids'] and x['status'] in ('finished','cancelled')][-20:]
        return result

def replay(uid,mid,round_no):
    if round_no not in (0,1):raise ValueError('Lượt không hợp lệ')
    with transaction() as (state,db):
        m=state['matches'].get(mid)
        if not m or uid not in m['uids'] or m['status']!='finished':raise ValueError('Không có quyền xem trận')
        row=db.execute('SELECT report FROM social_arena_reports WHERE event_id=? AND match_id=? AND round_no=?',(EVENT,mid,round_no)).fetchone()
        return json.loads(row['report'])


def eligible_board(state):
    """Only actual participants; do not reward an idle registration."""
    rows=[p for p in state['players'].values() if p['wins']+p['losses']+p['draws']>0 and not p.get('disqualified')]
    return sorted(rows,key=lambda p:(-p['points'],-p['wins'],-p['wins']/max(1,p['wins']+p['losses']+p['draws']),p['achieved_at'],p['uid']))


def referee(action, *, authorized, now=None, target=None):
    if not authorized:raise PermissionError('Chỉ SUPER GM')
    now=int(time.time() if now is None else now)
    with transaction() as (state,db):
        _cleanup(state,now)
        if action=='close':
            state['closed']=True
            state['queue'].clear()
        elif action=='open':
            if phase(now)!='open' or state.get('final'):raise ValueError('Không thể mở lại kỳ này')
            state['closed']=False
        elif action=='cancel':
            m=state['matches'].get(target)
            if not m or m['status'] in ('finished','cancelled'):raise ValueError('Trận đã kết thúc hoặc không tồn tại')
            m['status']='cancelled';m.pop('snapshots',None)
        elif action=='disqualify':
            if state.get('final'):raise ValueError('BXH đã chốt')
            p=state['players'].get(target)
            if not p:raise ValueError('Không tìm thấy người chơi')
            p['disqualified']=True
            state['queue'].pop(target,None)
            m=_active(state,target)
            if m:m['status']='cancelled';m.pop('snapshots',None)
        elif action=='finalize':
            if now<END:raise ValueError('Chỉ chốt sau khi hết giờ')
            if any(m['status'] in ('accept','preview','ready','running') for m in state['matches'].values()):
                raise ValueError('Còn trận chưa kết thúc')
            state['closed']=True
            if not state.get('final'):
                state['final']=[dict(p,rank=i) for i,p in enumerate(eligible_board(state)[:5],1)]
        elif action!='status':
            raise ValueError('Thao tác không hợp lệ')
        if action!='status':
            live_service._audit(db,'social_arena.'+action,EVENT,{'target':target},'SUPER_GM')
        return {'event':EVENT,'closed':state['closed'],'queue':list(state['queue']),
                'matches':[{k:v for k,v in m.items() if k not in ('snapshots','seed')} for m in state['matches'].values()],
                'board':[dict(p,rank=i) for i,p in enumerate(eligible_board(state),1)],
                'final':state.get('final',[]),
                'awards':[dict(r) for r in db.execute('SELECT uid,rank,mail_id FROM social_arena_awards WHERE event_id=?',(EVENT,)).fetchall()]}


def award(rank, world, attachments, title, body, *, authorized):
    """A single transaction creates one normal-world item-mail per ranked account."""
    if not authorized:raise PermissionError('Chỉ SUPER GM')
    if world not in ('S1','S2','S3'):raise ValueError('Chỉ nhận quà tại S1–S3')
    from . import gm_catalog
    clean=gm_catalog.validate_gift(attachments)
    rank=int(rank)
    with transaction() as (state,db):
        winner=next((p for p in state.get('final',[]) if p['rank']==rank),None)
        if not winner:raise ValueError('Chưa có kết quả được chốt cho hạng này')
        uid=winner['uid']
        prior=db.execute('SELECT mail_id FROM social_arena_awards WHERE event_id=? AND uid=?',(EVENT,uid)).fetchone()
        if prior:return {'mail_id':prior['mail_id'],'already_sent':True}
        p=db.execute("SELECT character_name FROM players WHERE uid=? AND server_id=? AND status='active'",(uid,world)).fetchone()
        if not p:raise ValueError('Người thắng chưa có nhân vật hoạt động ở máy chủ này')
        mid='SOCIAL-'+secrets.token_hex(12).upper()
        db.execute("""INSERT INTO mail(id,uid,server_id,character_name,title,body,attachments,status,created_at,operator)
            VALUES(?,?,?,?,?,?,?,'pending',?,?)""",
            (mid,uid,world,p['character_name'],str(title or 'Quà Đấu Trường Giao Lưu')[:100],str(body or '')[:1000],json.dumps(clean),int(time.time()),'SUPER_GM'))
        db.execute('INSERT INTO social_arena_awards(event_id,uid,rank,mail_id) VALUES(?,?,?,?)',(EVENT,uid,rank,mid))
        live_service._audit(db,'social_arena.award',mid,{'event':EVENT,'uid':uid,'server_id':world,'rank':rank,'attachments':clean},'SUPER_GM')
        return {'mail_id':mid,'already_sent':False}
