"""NewbieCamp original 30 visible missions + 3 automatic phase bonuses (LOCAL-079).

Local contacts satisfy the friend task. Online Chat and Elite League remain
untracked. No reconstructed historical login streak: count consecutive local
calendar days with persisted activity, preserving a completed maximum streak.
"""
import json
from datetime import date
from pathlib import Path
from . import growth_diary as gd, clock
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data/newbie_camp.json').read_text())
TASKS={int(k):v for k,v in D['tasks'].items()}
BOARDS={int(k):v for k,v in D['boards'].items()}
STAGES=json.loads((ROOT/'data/stage.json').read_text())
ENDS={c:max(int(r['id']) for r in STAGES.values() if int(r['fort_id'])==c) for c in (1,5,7,10)}
COUNTERS={2:'forge',7:'gamble',8:'arena',13:'advanced',14:'enroll',15:'sanctuary',16:'tavern',19:'growth_high_slots',24:'newbie_patrol'}
def saved(s):return s.setdefault('newbie_camp',{'claimed':[],'bonuses':[],'progress':{},'day':'','streak':0,'best_streak':0})
def metric(s,r,roster,level):
 mid=int(r['id']);typ=int(r['type']);h=s.get('home_systems') or {}
 if typ==1:return int(int(s.get('max_stage',0))>=ENDS[{1:1,13:7,24:10,33:5}[mid]])
 if typ==3:return int(any(int(p.get('lv',1))>={3:30,15:100}[mid] for p in roster))
 if typ==4:return int(bool(h.get('contacts')))
 if typ==6:return int((s.get('growth_diary') or {}).get('counts',{}).get('newbie_wallpaper',0))
 if typ==9:return int(bool(s.get('guild')))
 if typ==10:return int(int((s.get('tower') or {}).get('max_stage',0))>={10:1,19:10}[mid])
 if typ==11:return int((s.get('newbie_camp') or {}).get('best_streak',0))
 if typ==12:return int(level>=50)
 if typ==17:return int(any(len(p.get('equips',[]))>=7 and p['equips'][6] for p in roster))
 if typ==18:return int(any(int(p.get('stars',0))>=6 for p in roster))
 if typ==20:return int((s.get('arena3v3') or {}).get('fights',0))
 if typ==22:
  from .hero_challenge import STAGES
  done=set((s.get('hero_challenge') or {}).get('first_done',[]))
  return sum(int(i in done) for i,r in STAGES.items() if not int(r.get('next_id') or 0) or int(r['next_id']) not in STAGES)
 if typ==23:return len(h.get('pets') or {})
 if typ in COUNTERS:
  k=COUNTERS[typ];return int((s.get('missions') or {}).get('totals',{}).get(k,0))+int((s.get('growth_diary') or {}).get('counts',{}).get(k,0))
 return None

def observe(s,roster,level,now):
 d=saved(s);today=clock.day(now)
 if today>d['day']:
  consecutive=bool(d['day']) and (date.fromisoformat(today)-date.fromisoformat(d['day'])).days==1
  d['streak']=d['streak']+1 if consecutive else 1;d['day']=today
  d['best_streak']=max(d['best_streak'],d['streak'])
 for mid,r in TASKS.items():
  if r['is_hide']:continue
  have=metric(s,r,roster,level)
  if have is not None:d['progress'][str(mid)]=max(int(d['progress'].get(str(mid),0)),min(int(r['complete_value']),have))

def snapshot(s,roster,level):
 d=s.get('newbie_camp') or {};claimed=set(d.get('claimed',[]));bonus=set(d.get('bonuses',[]));pages=[]
 for phase,b in sorted(BOARDS.items()):
  prev=pages[-1] if pages else None
  locked=level<int(b['unlock_lev']) and not (prev and all(t['complete'] for t in prev['tasks']))
  tasks=[]
  for mid in b['missions']:
   r=TASKS[mid];raw=metric(s,r,roster,level);need=int(r['complete_value'])
   have=min(need,max(int(d.get('progress',{}).get(str(mid),0)),raw or 0))
   tasks.append({'id':mid,'text':r['text'],'have':have,'need':need,'tracked':raw is not None,'complete':mid in claimed or raw is not None and have>=need,'claimed':mid in claimed,'can':not locked and mid not in claimed and raw is not None and have>=need,'award':r['award'],'window':r['go_window']})
  pages.append({'id':phase,'tasks':tasks,'locked':locked,'unlock_level':b['unlock_lev'],'award':b['award'],'bonus_claimed':phase in bonus,'complete':sum(t['complete'] for t in tasks)})
 return {'phases':pages,'total':30,'tracked':sum(t['tracked'] for b in pages for t in b['tasks']),'streak':d.get('streak',0),'best_streak':d.get('best_streak',0)}

def action(s,req,roster,level,now):
 if not isinstance(req,dict):raise ValueError('Datos inválidos')
 kind=req.get('action');ident=gd.checked(req.get('id')) if kind=='mission' else None
 if kind not in ('open','mission'):raise ValueError('Acción no disponible')
 observe(s,roster,level,now);snap=snapshot(s,roster,level);got={};d=saved(s)
 def grant(text):
  for i,n in gd.awards(text).items():s['items'][i]=int(s['items'].get(i,0))+n;got[i]=got.get(i,0)+n
 if kind=='mission':
  task=next((t for p in snap['phases'] for t in p['tasks'] if t['id']==ident),None)
  if not task or not task['can']:raise ValueError('Misión sin completar, bloqueada o ya reclamada')
  d['claimed'].append(ident);grant(task['award'])
 # Client reqLostAward: repair a missed automatic bonus, only after all visible rewards.
 for phase,b in BOARDS.items():
  if phase not in d['bonuses'] and all(mid in d['claimed'] for mid in b['missions']):
   d['bonuses'].append(phase);grant(b['award'])
 return {'got':got}
