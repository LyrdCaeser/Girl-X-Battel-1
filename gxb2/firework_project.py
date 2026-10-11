"""Firework Project 196: original crafting weights, costs, unlocks and shop.
LOCAL-071: permanent archive, 250 daily dust replacing missing server sources.
"""
import copy, json, random
from pathlib import Path
from . import clock
from .puzzle_events import pairs, grant, integer as strict_integer
D=json.loads((Path(__file__).resolve().parents[1]/'data/firework_project.json').read_text())
DAILY=250
class FireworkError(ValueError):pass

def integer(value, low, high):
    try:return strict_integer(value,low,high)
    except ValueError as exc:raise FireworkError(str(exc)) from exc

def read(state):
    data={'spent':0,'buys':{},'day':''}
    data.update(copy.deepcopy(state.get('firework_project') or {}))
    return data

def snapshot(state,now):
    data=read(state)
    return {**data,'dust':int(state['items'].get('225',0)), 'fireworks':int(state['items'].get('226',0)),
            'level':data['spent']//D['level_step'],'level_progress':data['spent']%D['level_step'],
            'daily':DAILY,'daily_ready':clock.day(now)>data['day'],
            'shop':[{'id':int(k),**r,'left':max(0,r['limit']-data['buys'].get(k,0)),
                     'unlocked':data['spent']>=r['num']} for k,r in D['activity_bomb_award'].items()]}

def action(state,request,now,rng=None):
    work=copy.deepcopy(state);data=read(work);got={};outcomes=[]
    act=request.get('action')
    if act=='daily':
        day=clock.day(now)
        if day<=data['day']:raise FireworkError('Ya recogiste el suministro de hoy')
        data['day']=day;got={'225':DAILY}
    elif act=='craft':
        count=integer(request.get('num',1),1,10)
        if count not in (1,10):raise FireworkError('Elige fabricar 1 o 10')
        cost={k:v*count for k,v in pairs(D['cost']).items()}
        if any(int(work['items'].get(k,0))<v for k,v in cost.items()):raise FireworkError('Falta polvo para fabricar')
        for k,v in cost.items():work['items'][k]-=v
        data['spent']+=sum(cost.values())
        rows=list(D['activity_bomb_make'].values());chooser=rng or random.SystemRandom()
        for _ in range(count):
            row=chooser.choices(rows,weights=[r['weight'] for r in rows],k=1)[0]
            outcomes.append(row['id'])
            for k,v in pairs(row['awards']).items():got[k]=got.get(k,0)+v
    elif act=='buy':
        rid=str(integer(request.get('id'),1,len(D['activity_bomb_award'])))
        row=D['activity_bomb_award'][rid]
        if data['spent']<row['num']:raise FireworkError('Sube el nivel de fabricación para desbloquearlo')
        if data['buys'].get(rid,0)>=row['limit']:raise FireworkError('Premio agotado')
        cost=pairs(row['cost'])
        if any(int(work['items'].get(k,0))<v for k,v in cost.items()):raise FireworkError('Faltan fuegos artificiales')
        for k,v in cost.items():work['items'][k]-=v
        data['buys'][rid]=data['buys'].get(rid,0)+1;got=pairs(row['awards'])
    else:raise FireworkError('Acción no disponible')
    grant(work,got);work['firework_project']=data;state.clear();state.update(work)
    return {'got':got,'outcomes':outcomes}
