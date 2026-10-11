"""Original Training/Ulticore tables, client formulas; local calendar and uniform damage RNG."""
import copy,json,math,secrets
from pathlib import Path
from . import clock,home_systems as h,growth_diary as gd
D=json.loads((Path(__file__).resolve().parents[1]/'data/remaining_systems.json').read_text());M=D['misc']
B={int(k):v for k,v in D['pet_training_boss'].items()};LESSONS={int(k):v for k,v in D['pet_training_lesson'].items()}
def pets(s):return (s.get('home_systems') or {}).get('pets') or {}
def unlocked(s):return any(int(p['lv'])>=int(M['pet_training_lock_level']) for p in pets(s).values())
def level(s):
 exp=int(s['items'].get('245',0));return max(int(k) for k,r in D['pet_training'].items() if exp>=int(r['exp']))
def num(v,label,lo=1,hi=2147483647):return h.checked(v,label,lo,hi)
def score(p):
 a,b,c=map(int,str(M['pet_training_pet_atk']).split('|'));return int(p['lv'])*a+int(p.get('exlv',0))*b+sum(map(int,p['skills']))*c
def rate(text,value):return max(float(r) for threshold,r in (v.split('#') for v in str(text).split('|')) if value>=int(threshold))
def saved(s,now):
 t=s.setdefault('pet_training',{'day':'','times':0,'pet_times':{},'buy_times':0,'boss_id':1,'boss_hp':B[1]['hp'],'missions':{},'hang_time':now})
 today=clock.day(now)
 if today>t['day']:t.update(day=today,times=0,pet_times={},buy_times=0)
 return t

def idle(s,t,now):
 lv=level(s);r=D['pet_training_new_awards'][str(lv)];elapsed=min(int(r['time']),max(0,now-int(t['hang_time'])))
 cycles=elapsed//int(M['pet_training_hangup_cycle']);mult=rate(M['pet_training_hangup_awards2_coefficient'],sum(int(p['lv']) for p in pets(s).values()))
 return {i:math.floor(n*cycles*mult) for key in ['awards1','awards2'] for i,n in h.pairs(r[key]).items()}

def core_info(pid,p):
 r=D['pet'][str(pid)];lv=int(p.get('exlv',0));row=D['pet_exskill'].get(str(int(r['exskill_id'])+max(1,lv)-1),{})
 return {'level':lv,'max':int(r['max_exlevel']),'unlocked':int(p['lv'])>=int(M['pet_exskill_open_level']),
         'cost':M['pet_exlevel_unlock_cost'] if lv==0 else row.get('cost','') if lv<int(r['max_exlevel']) else '',
         'effects':row.get('effects','') if lv else '', 'restore':row.get('restore','') if lv>1 else ''}

def core(s,req):
 pid=num(req.get('pet'),'Servant');p=pets(s).get(str(pid))
 if not p:raise ValueError('No tienes ese Servant')
 info=core_info(pid,p);lv=info['level'];kind=req.get('action');got={}
 if not info['unlocked']:raise ValueError('Ulticore requiere Servant Lv120')
 if kind=='core_unlock':
  if lv:raise ValueError('Ulticore ya abierto')
  h.charge(s,h.pairs(info['cost']));p['exlv']=1
 elif kind=='core_upgrade':
  n=num(req.get('count',1),'Cantidad',1,100)
  if not lv or lv+n>info['max']:raise ValueError('Ulticore bloqueado o nivel máximo')
  total={}
  for cur in range(lv,lv+n):
   row=D['pet_exskill'][str(int(D['pet'][str(pid)]['exskill_id'])+cur-1)]
   for i,v in h.pairs(row['cost']).items():total[i]=total.get(i,0)+v
  h.charge(s,total);p['exlv']=lv+n
 elif kind=='core_reset':
  if lv<=1:raise ValueError('Ulticore no tiene mejoras para devolver')
  got=h.pairs(info['restore']);h.grant(s,got);p['exlv']=0
  cap=30
  for i,current in enumerate(p['skills']):
   if current>cap:
    base=str(D['pet'][str(pid)][f'pas_skill{i+1}_id'])
    for cur in range(cap,current):
     cost=h.pairs(h.SKILLS[(base,cur)]['cost']);n=cost.get('27',0);s['items']['27']=int(s['items'].get('27',0))+n;got['27']=got.get('27',0)+n
    p['skills'][i]=cap
 else:raise ValueError('Acción Ulticore no disponible')
 return {'got':got,'pet':pid}

def snapshot(s,now):
 scratch=copy.deepcopy(s);t=saved(scratch,now);lv=level(scratch);used={i for m in t['missions'].values() for i in m['pets']}
 courses=[]
 for i,r in sorted(LESSONS.items(),key=lambda kv:int(kv[1]['rank_unlocked'])):courses.append({**r,'locked':int(r['level'])>lv})
 return {'unlocked':unlocked(s),'level':lv,'times':t['times'],'remaining':max(0,int(M['pet_training_boss_limit'])-t['times']),
         'buy_times':t['buy_times'],'buy_cost':str(M['pet_training_energy_buy_cost']).split('|')[t['buy_times']] if t['buy_times']<int(M['pet_training_energy_buy_limit']) else '',
         'boss':B[t['boss_id']],'boss_hp':t['boss_hp'],'bosses':[r for r in B.values() if int(r['level'])<=lv],
         'pets':[{'id':int(i),'name':h.NAMES.get(int(i),i),'level':p['lv'],'score':score(p),'remaining':max(0,int(M['pet_training_pet_energy'])-t['pet_times'].get(i,0)),'busy':int(i) in used,'core':core_info(i,p)} for i,p in pets(s).items()],
         'missions':[{'slot':pos,**t['missions'].get(str(pos),{}),'ready':bool(t['missions'].get(str(pos))) and now>=t['missions'][str(pos)]['ready_at']} for pos in range(1,4)],
         'lessons':courses,'idle':idle(scratch,t,now),'hang_time':t['hang_time']}

def action(s,req,now,rng=secrets.randbelow):
 if not isinstance(req,dict):raise ValueError('Datos inválidos')
 kind=req.get('action')
 if kind in ('core_unlock','core_upgrade','core_reset'):return core(s,req)
 if not unlocked(s):raise ValueError('Servant Training requiere un Servant Lv120')
 t=saved(s,now);got={};result={};lv=level(s)
 if kind=='open':pass
 elif kind=='select':
  bid=num(req.get('boss'),'Muñeco')
  if bid not in B or int(B[bid]['level'])>lv:raise ValueError('Muñeco bloqueado')
  t.update(boss_id=bid,boss_hp=B[bid]['hp'])
 elif kind in ('fight','buy'):
  pid=str(num(req.get('pet'),'Servant'));p=pets(s).get(pid)
  if not p or int(p['lv'])<int(M['pet_training_boss_level']):raise ValueError('Necesitas Servant Lv120')
  if kind=='buy':
   if t['times']<int(M['pet_training_boss_limit']) or t['buy_times']>=int(M['pet_training_energy_buy_limit']):raise ValueError('Compra no disponible')
   h.charge(s,h.pairs(str(M['pet_training_energy_buy_cost']).split('|')[t['buy_times']]))
   t['buy_times']+=1;t['times']-=1;t['pet_times'][pid]=max(0,t['pet_times'].get(pid,0)-1)
  else:
   if t['times']>=int(M['pet_training_boss_limit']) or t['pet_times'].get(pid,0)>=int(M['pet_training_pet_energy']):raise ValueError('Sin desafíos o energía del Servant')
   if any(int(pid) in m['pets'] for m in t['missions'].values()):raise ValueError('Ese Servant está en una lección')
   low,high=map(float,str(M['pet_training_pet_damage']).split('|'));damage=max(1,math.floor(score(p)*(low+(high-low)*rng(10001)/10000)))
   boss=B[t['boss_id']];remaining=int(t['boss_hp'])-damage;kills=0
   if remaining<=0:kills=1+(-remaining)//int(boss['hp']);remaining+=kills*int(boss['hp'])
   t['boss_hp']=remaining;t['times']+=1;t['pet_times'][pid]=t['pet_times'].get(pid,0)+1
   got={i:n*kills for i,n in h.pairs(boss['final_awards']).items()} if kills else h.pairs(boss['battle_awards'])
   gd.record(s,'growth_training');result.update(harm=damage,reborn_count=kills)
 elif kind=='collect':
  got=idle(s,t,now)
  if not any(got.values()):raise ValueError('Todavía no hay recompensas de entrenamiento')
  t['hang_time']=now
 elif kind=='start':
  pos=str(num(req.get('slot'),'Posición',1,3));mid=num(req.get('lesson'),'Lección');chosen=req.get('pets')
  if pos in t['missions']:raise ValueError('Posición ocupada')
  r=LESSONS.get(mid)
  if not r or int(r['level'])>lv:raise ValueError('Lección bloqueada')
  if not isinstance(chosen,list) or not 1<=len(chosen)<=3 or len(set(chosen))!=len(chosen):raise ValueError('Selecciona entre 1 y 3 Servants distintos')
  for pid in chosen:
   num(pid,'Servant')
   if str(pid) not in pets(s) or any(pid in m['pets'] for m in t['missions'].values()):raise ValueError('Servant no disponible')
  mult=rate(M['pet_training_lesson_award'],sum(int(pets(s)[str(i)]['lv']) for i in chosen))
  t['missions'][pos]={'mission_id':mid,'start_time':now,'ready_at':now+int(r['time']),'pets':chosen[:],'award':{i:math.floor(n*mult) for i,n in h.pairs(r['awards']).items()}}
 elif kind in ('cancel','complete'):
  pos=str(num(req.get('slot'),'Posición',1,3));m=t['missions'].get(pos)
  if not m:raise ValueError('No hay lección en esa posición')
  if kind=='complete':
   if now<m['ready_at']:raise ValueError('Lección sin terminar')
   got=m['award']
  del t['missions'][pos]
 else:raise ValueError('Acción de Training no disponible')
 h.grant(s,got);return {'got':got,**result}
