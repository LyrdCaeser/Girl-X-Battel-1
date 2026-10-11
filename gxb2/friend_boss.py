"""Current Friend Boss (friend_boss_new), offline own team; no fabricated support friends."""
import copy,json,secrets
from pathlib import Path
from . import clock,home_systems as h,growth_diary as gd,explore
D=json.loads((Path(__file__).resolve().parents[1]/'data/remaining_systems.json').read_text());B={int(k):v for k,v in D['friend_boss_new'].items()};M=D['misc']
def saved(s,now):
 f=s.setdefault('friend_boss',{'day':'','done':False,'unlock':1,'pending':1,'wins':{},'selected':1,'power':0})
 day=clock.day(now)
 if day>f['day']:f.update(day=day,done=False,unlock=max(f['unlock'],f['pending']))
 return f

def observe_power(s,now,power):
 f=saved(s,now);f['power']=power;f['pending']=max(f['pending'],max(i for i,r in B.items() if int(r['power'])<=power))

def snapshot(s,now,level):
 view=copy.deepcopy(s);f=saved(view,now)
 return {'unlocked':level>=int(M['friend_search_level']),'unlock_level':int(M['friend_search_level']),'done':f['done'],'unlock':f['unlock'],'pending':f['pending'],'power':f['power'],'selected':f['selected'],
         'bosses':[{**r,'locked':i>f['unlock'],'wins':f['wins'].get(str(i),0),'skip':f['wins'].get(str(i),0)>=int(M['friend_boss_skip_limit'])} for i,r in B.items()]}

def action(s,req,now,level,fight=None,rng=secrets.randbelow):
 if not isinstance(req,dict):raise ValueError('Datos inválidos')
 if level<int(M['friend_search_level']):raise ValueError('Friend Boss requiere Player Lv36')
 f=saved(s,now);kind=req.get('action');got={};report=None
 if kind=='open':pass
 elif kind in ('select','fight'):
  bid=h.checked(req.get('boss'),'Dificultad',1,max(B));row=B[bid]
  if bid>f['unlock']:raise ValueError('Dificultad bloqueada; el poder nuevo abre niveles al día siguiente')
  f['selected']=bid
  if kind=='fight':
   if f['done']:raise ValueError('Ya derrotaste el Friend Boss de hoy')
   if not fight:raise ValueError('Motor de combate no disponible')
   report=fight(row)
   if report['isWin']:
    for box in str(row['dropbox_ids']).split('|'):
     for i,n in explore.dropbox(int(box),rng).items():got[i]=got.get(i,0)+n
    h.grant(s,got);f['done']=True;f['wins'][str(bid)]=f['wins'].get(str(bid),0)+1;gd.record(s,'growth_friend_boss')
 elif kind=='skip':
  bid=h.checked(req.get('boss'),'Dificultad',1,max(B));row=B[bid]
  if bid>f['unlock'] or f['wins'].get(str(bid),0)<int(M['friend_boss_skip_limit']):raise ValueError('Necesitas tres victorias propias en esta dificultad')
  if f['done']:raise ValueError('Ya derrotaste el Friend Boss de hoy')
  for box in str(row['dropbox_ids']).split('|'):
   for i,n in explore.dropbox(int(box),rng).items():got[i]=got.get(i,0)+n
  h.grant(s,got);f['done']=True;f['wins'][str(bid)]+=1;gd.record(s,'growth_friend_boss')
 else:raise ValueError('Acción Friend Boss no disponible')
 return {'got':got,**({'report':report,'win':bool(report['isWin'])} if report else {})}
