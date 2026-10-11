"""Personal House and outfit equipment. Original catalogs; local validated persistence.
Room income (HouseComfortWindow): house_award by comfort, every 5 s, up to hang_up_time_max (12 h) since the last Collect.
Social visits and outfit gacha remain unimplemented rather than invent rewards.
"""
import copy,json,time
from collections import Counter
from pathlib import Path
DATA=json.loads((Path(__file__).resolve().parents[1]/'data/house_dress.json').read_text())
F=DATA['house_furniture'];STYLE=DATA['senpai_dress_style'];DRESS=DATA['senpai_dress'];M=DATA['misc']
_AW=Path(__file__).resolve().parents[1]/'data/house_award.json'
AWARD=json.loads(_AW.read_text()) if _AW.exists() else {'rows':[],'tick':5,'max':43200}

# ---- Dorm resource output. LOCAL (LOCAL-075): the server kept hang_time / hang_update_time / the award record; here
# 'at' = last Collect, 'upd' = last comfort change, 'rec' = what accrued before that change at the old comfort.
def award_row(c):
 rows=[r for r in AWARD['rows'] if r['comfort']<=c];return {k:float(v) for k,v in (p.split('#') for p in rows[-1]['award'].split('|'))} if rows else {}
def hang_now(s,now):
 h=s.get('house_dress') or {};g=h.get('hang')
 if not g:return {}
 end=min(now,g['at']+AWARD['max']);t=max(0,min(AWARD['max'],end-g['upd']));ticks=t//AWARD['tick']
 rate=award_row(comfort(s));out={}
 for k in set(rate)|set(g['rec']):
  n=int(rate.get(k,0)*ticks+float(g['rec'].get(k,0)))
  if n>0:out[k]=n
 return out
def hang_touch(s,now):
 """Before the comfort changes: bank what accrued at the old comfort."""
 g=s['house_dress'].get('hang')
 if not g:return
 end=min(now,g['at']+AWARD['max']);ticks=max(0,min(AWARD['max'],end-g['upd']))//AWARD['tick']
 for k,v in award_row(comfort(s)).items():g['rec'][k]=float(g['rec'].get(k,0))+v*ticks
 g['upd']=max(g['upd'],end)

def num(v,label,lo=0,hi=2**31-1):
 if isinstance(v,bool) or not isinstance(v,int) or not lo<=v<=hi:raise ValueError(label+': valor inválido')
 return v

def pairs(s):return {k:int(v) for k,v in (p.split('#') for p in str(s).split('|') if '#' in p)}
def initial_layout():
 entries=[]
 def visit(r,parent=0,plane='floor'):
  row=F[str(r['table_id'])];uid=len(entries)+1
  plane='wall' if int(row['type'])==2 else ('background' if int(row['type'])==10 else plane)
  entries.append({'uid':uid,'id':r['table_id'],'x':r['x'],'y':r['y'],'flip':r['flip'],'plane':plane,'parent':parent})
  for c in r.get('children',[]):visit(c,uid if int(row['type']) not in [1,2] else 0,'wall' if int(row['type'])==2 else plane)
 for r in json.loads(DATA['house_furniture_unit'][M['house_furniture_unit_initial']]['unit']):visit(r)
 return entries

def defaults():return {'name':'Simple Dorm','revision':0,'rooms':{'1':initial_layout()},'bought':{},'girls':[],'outfit':{k:int(r['default_style']) for k,r in DATA['senpai_dress_slot'].items() if r['default_style']}}
def open_state(s):
 if 'house_dress' not in s:
  s['house_dress']=defaults()
  grants=pairs(M['house_furniture_initial'])
  for r in DATA['senpai_dress_slot'].values():
   if r['default_item']:grants[str(r['default_item'])]=1
  for k,v in grants.items():s['items'][k]=int(s['items'].get(k,0))+v
 s['house_dress'].setdefault('hang',{'at':int(time.time()),'upd':int(time.time()),'rec':{}})
 return s['house_dress']

def comfort(s):
 caps=[int(v) for v in M['dorm_comfort_top_num_by_type'].split('|')];total=0
 for typ,cap in enumerate(caps,1):
  rows=sorted((r for r in F.values() if r['type']==typ),key=lambda r:int(r['comfort']),reverse=True)
  for r in rows:
   n=min(cap,int(s['items'].get(str(r['id']),0)));total+=n*int(r['comfort']);cap-=n
   if cap<=0:break
 return total

def snapshot(s):
 h=copy.deepcopy(s.get('house_dress',defaults()))
 h['comfort']=comfort(s);h['inventory']={k:int(s['items'].get(k,0)) for k in F if int(s['items'].get(k,0))>0}
 h['clothes']={k:int(s['items'].get(k,0)) for k in DATA['senpai_dress_item'] if int(s['items'].get(k,0))>0}
 h['styles']=[int(k) for k,r in STYLE.items() if available(s,r)]
 h['opened']='house_dress' in s
 g=(s.get('house_dress') or {}).get('hang');now=int(time.time())
 h['hang']={'award':hang_now(s,now),'rate':award_row(h['comfort']),'full_at':(g['at']+AWARD['max']) if g else 0}
 return h

def available(s,r):
 dress=DRESS[str(r['dress_id'])]
 owns=any(int(s['items'].get(k,0))>0 for k in str(dress['items']).split('|'))
 # Paid alternative styles require the style unlock system, not just ownership of a base piece.
 unlocked=str(r['id']) in str(dress['unlock_styles']).split('|') and int(dress['unlock_style_type'])==1
 return owns and unlocked

def validate_layout(s,entries,floor):
 if not isinstance(entries,list) or len(entries)>180:raise ValueError('Distribución inválida')
 clean=[];used=Counter();types=Counter();uids=set();occupied=[];limits=[int(v) for v in M['dorm_top_num_by_type'].split('|')]
 for e in entries:
  if not isinstance(e,dict):raise ValueError('Mueble inválido')
  iid=str(num(e.get('id'),'Mueble',1));r=F.get(iid)
  if r is None:raise ValueError('Mueble desconocido')
  uid=num(e.get('uid'),'Identificador',1);x=num(e.get('x'),'X',0,47);y=num(e.get('y'),'Y',0,23);flip=num(e.get('flip',0),'Giro',0,1);parent=num(e.get('parent',0),'Apilado')
  if uid in uids:raise ValueError('Identificador repetido')
  uids.add(uid);used[iid]+=1;types[int(r['type'])]+=1
  plane=e.get('plane','floor')
  if plane not in ['floor','wall','background']:raise ValueError('Superficie inválida')
  if int(r['type'])==2 and plane!='wall':raise ValueError('Pared: superficie inválida')
  if int(r['type'])==10 and plane!='background':raise ValueError('Fondo: superficie inválida')
  if int(r['type']) not in [2,9,10] and plane!='floor':raise ValueError('Mueble: superficie inválida')
  if int(r['type'])==9 and plane!='wall':raise ValueError('Decoración de pared')
  if flip and str(r['can_flip'])=='0':raise ValueError('Este mueble no se puede girar')
  c={'uid':uid,'id':int(iid),'x':x,'y':y,'flip':flip,'plane':plane,'parent':parent};clean.append(c)
 for room,rows in s.get('house_dress',defaults())['rooms'].items():
  if room!=str(floor):used.update(str(e['id']) for e in rows)
 for iid,count in used.items():
  if count>int(s['items'].get(iid,0)):raise ValueError('No tienes suficientes copias del mueble')
 for typ,n in types.items():
  if n>limits[typ-1]:raise ValueError('Límite de muebles de esa categoría')
 index={e['uid']:e for e in clean};stacked=[]
 for e in clean:
  r=F[str(e['id'])]
  if e['parent']:
   p=index.get(e['parent'])
   if not p or p['parent'] or p['uid']==e['uid'] or str(F[str(p['id'])]['can_be_pile']) not in ['1','1|1']:raise ValueError('Soporte de apilado inválido')
   if str(r['can_pile'])!='1' or e['plane']!='floor' or p['plane']!='floor':raise ValueError('Este mueble no puede apilarse')
   pw,ph=map(int,str(F[str(p['id'])]['area']).split('|'));w,hh=map(int,str(r['area']).split('|'))
   if p['flip']:pw,ph=ph,pw
   if e['flip']:w,hh=hh,w
   if e['x']+w>pw or e['y']+hh>ph:raise ValueError('Mueble fuera de su soporte')
   rect=(e['x'],e['y'],e['x']+w,e['y']+hh)
   if any(parent==e['parent'] and rect[0]<b[2] and rect[2]>b[0] and rect[1]<b[3] and rect[3]>b[1] for parent,b in stacked):raise ValueError('Los objetos del soporte se superponen')
   stacked.append((e['parent'],rect))
   continue
  if e['plane']=='floor' and int(r['type']) not in [1,3]:
   wh=[int(v) for v in str(r['area']).split('|')];w,h=wh[:2]
   if e['flip']:w,h=h,w
   if e['x']+w>24 or e['y']+h>24:raise ValueError('Mueble fuera de la habitación')
   rect=(e['x'],e['y'],e['x']+w,e['y']+h)
   if any(rect[0]<b[2] and rect[2]>b[0] and rect[1]<b[3] and rect[3]>b[1] for b in occupied):raise ValueError('Los muebles se superponen')
   occupied.append(rect)
 return clean

def action(s,req):
 h=open_state(s);a=req.get('action','open')
 if a=='open':return {}
 now=int(req.get('_now') or time.time())
 if a=='hang_collect':
  got=hang_now(s,now)
  if not got:raise ValueError('Todavía no hay recursos para recoger')
  for k,v in got.items():s['items'][k]=int(s['items'].get(k,0))+v
  h['hang']={'at':now,'upd':now,'rec':{}}
  from . import missions, growth_diary;missions.record(s,'dorm_collect',1,now)
  growth_diary.record(s,'growth_dorm_gold',int(got.get('1',0)))
  return {'got':got}
 if a in ('save_room','buy_furniture'):hang_touch(s,now)
 if a=='save_room':
  rev=num(req.get('revision'),'Revisión')
  if rev!=h['revision']:raise ValueError('La habitación cambió. Vuelve a abrirla antes de guardar.')
  floor=num(req.get('floor',1),'Piso',1,2)
  if str(floor) not in h['rooms']:raise ValueError('Piso cerrado')
  layout=validate_layout(s,req.get('layout'),floor)
  name=req.get('name',h['name'])
  if not isinstance(name,str) or not 1<=len(name.strip())<=32:raise ValueError('Nombre inválido')
  h['rooms'][str(floor)]=layout;h['name']=name.strip();h['revision']+=1
  return {}
 if a=='buy_furniture':
  rid=str(num(req.get('shop_id'),'Artículo',1));n=num(req.get('count',1),'Cantidad',1,10);r=DATA['shop_house_furniture'].get(rid)
  if not r:raise ValueError('Artículo desconocido')
  limit=int(r['limit']);bought=h['bought'].get(rid,0)
  if limit>=0 and bought+n>limit:raise ValueError('Límite de compra alcanzado')
  cost={k:v*n for k,v in pairs(r['cost']).items()};reward={k:v*n for k,v in pairs(r['item']).items()}
  if any(s['items'].get(k,0)<v for k,v in cost.items()):raise ValueError('Recursos insuficientes')
  for k,v in cost.items():s['items'][k]-=v
  for k,v in reward.items():s['items'][k]=s['items'].get(k,0)+v
  h['bought'][rid]=bought+n;return {'got':reward}
 if a=='open_floor':
  if '2' in h['rooms']:raise ValueError('El piso ya está abierto')
  if comfort(s)<int(DATA['house_floor']['2']['need_comfort']):raise ValueError('Necesitas 200 de confort')
  for k,v in pairs(DATA['house_floor']['2']['awards']).items():s['items'][k]=s['items'].get(k,0)+v
  h['rooms']['2']=[e for e in initial_layout() if F[str(e['id'])]['type'] in [1,2,10]];h['revision']+=1;return {}
 if a=='equip':
  styles=req.get('styles')
  if not isinstance(styles,list) or len(styles)>5:raise ValueError('Atuendo inválido')
  outfit={}
  for sid in styles:
   r=STYLE.get(str(num(sid,'Estilo',1)))
   if not r or not available(s,r):raise ValueError('Estilo no disponible')
   pos=str(r['pos'])
   if pos in outfit:raise ValueError('Solo una pieza por ranura')
   outfit[pos]=sid
  if not all(k in outfit for k in ['1','2','3']):raise ValueError('Elige cabeza, cuerpo y piernas')
  h['outfit']=outfit;return {}
 if a=='girls':
  ids=req.get('ids');owned={g['partner_id'] for g in s.get('partners',[])}
  if not isinstance(ids,list) or len(ids)>5 or len(ids)!=len(set(ids)) or any(type(i)!=int or i not in owned for i in ids):raise ValueError('Selección de chicas inválida')
  h['girls']=ids;return {}
 raise ValueError('Acción no disponible')
