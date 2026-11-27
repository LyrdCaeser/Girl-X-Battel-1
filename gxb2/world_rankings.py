"""Read-only local rankings and the public S1–S3 cross-world power board."""
import json
import time
import threading
from functools import lru_cache
from . import live_service, guild_lab
from .engine import TABLES, TOWER, player_level, Engine

_lock = threading.RLock()
CROSS_WORLDS = ("S1", "S2", "S3")

@lru_cache(maxsize=256)
def _combat_stats(serialized):
    state=json.loads(serialized)
    owned={int(p['partner_id']):p for p in state['partners']}
    roster=list(owned.values())
    attrs=Engine._attributes(state,roster,guild_skills=guild_lab.skills(state)) if roster else {}
    groups={i:[] for i in range(1,9)}
    for pid,p in owned.items():
        group=int(TABLES['partner'][str(p['table_id'])]['group'])
        if group in groups:
            groups[group].append(int(attrs.get(str(pid),attrs.get(pid,{})).get('power',0)))
    # HeroAttr is evaluated independently for every hero; the saved
    # formation determines which of these exact powers are summed.
    ids={int(slot['partner_id']) for slot in state['formation']}
    power=sum(int(attrs.get(str(pid),attrs.get(pid,{})).get('power',0)) for pid in ids if pid in owned)
    return (power,{g:sum(sorted(vals,reverse=True)[:6]) for g,vals in groups.items() if vals})

def _profile_row(row, current_uid, current_world=None):
    state=json.loads(row['data']) if isinstance(row['data'],str) else dict(row['data'])
    # Ignore unrelated inventory/mail updates for the combat cache. Never use
    # a client-submitted power or stale leaderboard value.
    combat={k:state.get(k,default) for k,default in (
        ('partners',[]),('formation',[]),('guild_lab',{'levels':{},'reset_times':{}}),('chimes',{}))}
    with _lock:
        power,groups=_combat_stats(json.dumps(combat,sort_keys=True,separators=(',',':')))
    profile=state.get('profile') or {}
    stage=int(state.get('max_stage',0));stage_row=TABLES['stage'].get(str(stage))
    floor=min(len(TOWER),max(0,int((state.get('tower') or {}).get('max_stage',0))))
    return {'uid':row['uid'],'name':row['character_name'],'server_id':row['server_id'],
            'level':player_level(state),'power':power,'campaign':stage,
            'campaign_label':f"{stage_row['fort_id']}-{stage_row['name']}" if stage_row else 'Chưa vượt ải',
            'tower':floor,'groups':groups,'avatar':profile.get('avatar') or 'head_1001',
            'frame':profile.get('frame') or 'frame_8007','me':row['uid']==current_uid and (current_world is None or row['server_id']==current_world)}

def ranking(server_id, current_uid, mode='power', group=1, limit=100):
    if mode not in ('power','level','campaign','tower','guild','faction','cross'):
        raise ValueError('Bảng xếp hạng không hợp lệ')
    if mode=='faction' and group not in range(1,9):
        raise ValueError('Hệ nữ thần không hợp lệ')
    cross=mode=='cross'
    if cross and server_id not in CROSS_WORLDS:
        raise ValueError('BXH Liên Server chỉ dành cho S1–S3')
    worlds=CROSS_WORLDS if cross else (server_id,)
    placeholders=','.join('?' for _ in worlds)
    limit=max(1,min(100,int(limit)))
    db=live_service._db()
    try:
        rows=db.execute(f"""SELECT p.uid,p.server_id,p.character_name,pp.data
            FROM players p JOIN player_profiles pp ON p.uid=pp.uid AND p.server_id=pp.server_id
            WHERE p.server_id IN ({placeholders}) AND p.status='active'""",worlds).fetchall()
        guilds=db.execute("""SELECT g.id,g.name,g.server_id,g.level,g.exp,gp.state
            FROM world_guilds g LEFT JOIN world_guild_progress gp ON gp.guild_id=g.id
            WHERE g.server_id=?""",(server_id,)).fetchall() if mode=='guild' else []
        members=db.execute("""SELECT m.guild_id,m.uid FROM world_guild_members m
            JOIN world_guilds g ON g.id=m.guild_id AND g.server_id=m.server_id
            WHERE m.server_id=?""",(server_id,)).fetchall() if mode=='guild' else []
    finally:db.close()
    players=[_profile_row(r,current_uid,server_id) for r in rows]
    if mode=='guild':
        board=[]
        by_uid={p['uid']:p for p in players}
        for g in guilds:
            roster=[by_uid[m['uid']] for m in members if m['guild_id']==g['id'] and m['uid'] in by_uid]
            if not roster:continue
            progress=json.loads(g['state'] or '{}')
            flag=int(progress.get('flag',1))
            total=sum(p['power'] for p in roster)
            board.append({'name':g['name'],'server_id':server_id,'level':int(g['level']),
                'power':total,'score':total,'score_label':'Tổng lực chiến','guild_flag':flag,
                'member_count':len(roster),'me':any(p['me'] for p in roster),'uid':str(g['id'])})
    else:
        labels={'power':'Lực chiến','level':'Cấp độ','campaign':'Ải đã vượt','tower':'Tầng đã vượt','faction':'Lực chiến hệ','cross':'Lực chiến'}
        board=[]
        for p in players:
            if mode=='faction' and group not in p['groups']:continue
            score=p['groups'][group] if mode=='faction' else p['power' if cross else mode]
            board.append({**p,'score':score,'score_label':labels[mode],
                          'display_score':p['campaign_label'] if mode=='campaign' else str(score)})
    board.sort(key=lambda p:(-p['score'],-p['power'],-p['level'],p['server_id'],p['uid']))
    for i,p in enumerate(board,1):p['rank']=i
    own=next((p['rank'] for p in board if p['me']),None)
    # Only display information, not profile contents, inventory or account UID.
    return {'server_id':server_id,'scope':'cross' if cross else 'local','worlds':list(worlds),'mode':mode,'group':group if mode=='faction' else None,
            'my_rank':own,'total':len(board),'server_time':int(time.time()),
            'ranking':[{k:v for k,v in p.items() if k not in ('uid','groups')} for p in board[:limit]]}
