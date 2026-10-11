"""Practical Work / activity_boss: three original eight-boss projects, local 30-day seasons.

The current table has 8 tiers, whereas old Growth Diary objectives say 1-10,
2-10 and 3-10. Those objectives are intentionally not translated to tier 8.
"""
import copy,json,secrets
from pathlib import Path
from . import home_systems as h,explore
D=json.loads((Path(__file__).resolve().parents[1]/'data/remaining_systems.json').read_text());B={int(k):v for k,v in D['activity_boss'].items()};M=D['misc'];PERIOD=30*86400
FIRST={p:min(i for i,r in B.items() if int(r['type'])==p) for p in (1,2,3)}
def saved(s,now):
 anchor=int(s.get('created',now));season=max(0,(now-anchor)//PERIOD)
 p=s.setdefault('practical_work',{'season':season,'projects':{str(i):{'boss':b,'hp':int(B[b]['hp']),'done':[]} for i,b in FIRST.items()},'bought':0})
 if season>p['season']:p.update(season=season,projects={str(i):{'boss':b,'hp':int(B[b]['hp']),'done':[]} for i,b in FIRST.items()},bought=0)
 return p

def snapshot(s,now):
 v=copy.deepcopy(s);p=saved(v,now)
 return {'season':p['season']+1,'reset_at':int(s.get('created',now))+(p['season']+1)*PERIOD,'tickets':int(s['items'].get('28',0)),
         'cost':M['activity_boss_buy_cost'],'projects':[{'id':i,'name':{1:'Coins',2:'EXP Juice',3:'Servant Cookies'}[i],**p['projects'][str(i)],'row':B[p['projects'][str(i)]['boss']],'total':8,'finished':len(p['projects'][str(i)]['done'])==8} for i in FIRST]}

def action(s,req,now,fight=None,rng=secrets.randbelow):
 if not isinstance(req,dict):raise ValueError('Datos inválidos')
 p=saved(s,now);kind=req.get('action');got={};result={}
 if kind=='open':pass
 elif kind=='buy':
  n=h.checked(req.get('count',1),'Cantidad',1,100)
  if p['bought']+n>int(M['activity_boss_buy_limit']):raise ValueError('Límite de compra')
  h.charge(s,{i:v*n for i,v in h.pairs(M['activity_boss_buy_cost']).items()});h.grant(s,{'28':n});p['bought']+=n;got={'28':n}
 elif kind=='fight':
  ident=h.checked(req.get('project'),'Proyecto',1,3);project=p['projects'][str(ident)];row=B[project['boss']]
  if len(project['done'])==8:raise ValueError('Proyecto completo hasta la próxima temporada')
  if not fight:raise ValueError('Motor de combate no disponible')
  h.charge(s,h.pairs(M['activity_boss_fight_cost']))
  report=fight({**row,'remaining_hp':project['hp']})
  # Original help: Servant damage is excluded from the boss's accumulated damage.
  damage=sum(max(0,int(x.get('hurt',0))) for x in report.get('hurts',[]) if 1<=int(x.get('pos',0))<=6)
  actual=min(project['hp'],damage);project['hp']-=actual
  got=explore.dropbox(int(row['dropbox_id']),rng);h.grant(s,got)
  won=project['hp']<=0
  if won:
   award=h.pairs(row['final_award']);home=h.saved(s,now);mid=home['next_id'];home['next_id']+=1
   home['mail'].append({'id':mid,'title':'Practical Work · Project '+str(ident)+' · Stage '+str(row['level_tips']),'type':'system','text':'Original stage completion reward.','awards':row['final_award'],'read':False,'claimed':False,'at':now})
   project['done'].append(int(row['id']));nxt=int(row['next_id'])
   if nxt:project.update(boss=nxt,hp=int(B[nxt]['hp']))
  result.update(report=report,damage=actual,defeated=won)
 else:raise ValueError('Acción de Practical Work no disponible')
 return {'got':got,**result}
