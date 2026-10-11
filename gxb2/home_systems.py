"""Offline Home systems backed by archived client tables. No network/social service."""
from __future__ import annotations
import copy, json, math, secrets, time
from . import clock
from pathlib import Path
DATA=json.loads((Path(__file__).resolve().parents[1]/'data/home_systems.json').read_text())
ROWS={k:{r.get('id',r.get('max_star')):r for r in v} for k,v in DATA.items() if isinstance(v,list)}
EXP={(r['pet_id'],int(r['lv'])):r for r in DATA['exp_pet']}
SKILLS={(r['pet_skill_id'],int(r['lv'])):r for r in DATA['pet_skill']}
# These goals have corresponding working local commands. Others remain visible as archived goals.
MISSIONS={5:('regular','Invoca una cápsula regular','capsule'),6:('advanced','Invoca una cápsula avanzada','capsule'),9:('quiz','Supera 2 Daily Quiz','quiz'),13:('graduate','Gradúa o despierta chicas 10 veces','graduate')}
NAMES={101:'Hunter',201:'Kraken',301:'Deerling',401:'Void',501:'Robert',601:'Elixir',701:'Flora',801:'Sea Serpent',901:'Crystal Golem'}

def pairs(value):
    if not value or value=='0':return {}
    return {k:int(v) for k,v in (s.split('#') for s in str(value).split('|'))}

def checked(value, label, low=0, high=2147483647):
    if isinstance(value,bool) or not isinstance(value,int) or not low<=value<=high:raise ValueError(f'{label}: valor inválido')
    return value

def charge(state,cost):
    if any(int(state['items'].get(k,0))<n for k,n in cost.items()):raise ValueError('Faltan recursos para esta acción')
    for k,n in cost.items():state['items'][k]=int(state['items'].get(k,0))-n

def grant(state,rewards):
    for k,n in rewards.items():state['items'][k]=int(state['items'].get(k,0))+n

def saved(state,now):
    home=state.setdefault('home_systems',{})
    home.setdefault('pets',{});home.setdefault('contacts',[]);home.setdefault('mail',[]);home.setdefault('drafts',[])
    home.setdefault('next_id',1);home.setdefault('book',{'counters':{},'claimed':[],'tiers':[],'shop':{}})
    home.setdefault('travel',{'buildings':{str(i):{'lv':1,'at':now,'stock':0,'partners':[]} for i in range(1,4)},'training':{str(i):1 for i in range(1,6)}})
    home.setdefault('cosmos',{'mode':4,'choice':757001,'count':0,'history':[]})
    return home

def period(row,now):
    # Client periods depend on server calendar; local daily/weekly cycles use the player's local time (LOCAL-058).
    if int(row['type'])==1:return clock.day(now)
    if int(row['type'])==2:return clock.week(now)
    return 'season-local'

def record(state,key,count=1,now=None):
    now=int(time.time()) if now is None else now
    from . import missions
    missions.record(state,key,count,now)
    home=saved(state,now)
    for mid,(counter,_,_) in MISSIONS.items():
        if key!=counter:continue
        row=ROWS['battlepass_mission'][str(mid)]
        token=f'{mid}:{period(row,now)}';counters=home['book']['counters']
        counters[token]=min(int(row['complete_value']),int(counters.get(token,0))+count)

def stock(state,home,bid,now):
    b=home['travel']['buildings'][str(bid)];row=ROWS[f'travel_building{bid}'][str(b['lv'])]
    amount=list(pairs(row['out_put']).values())[0];cap=int(row['stay_max'])
    output_bonus=capacity_bonus=0
    partners={p['partner_id']:p for p in state['partners']}
    from .engine import TABLES
    for idx,pid in enumerate(b['partners']):
        p=partners.get(pid)
        if not p:continue
        stars=int(TABLES['partner'][str(p['table_id'])]['max_star'])+int(p.get('awake',0))
        bonus=ROWS['travel_facility_add'].get(str(stars))
        if bonus:
            if idx%2==0:output_bonus+=float(bonus[f'out_add{bid}'])
            else:capacity_bonus+=float(bonus[f'stay_add{bid}'])
    amount=math.floor(amount*(1+output_bonus));cap=math.floor(cap*(1+capacity_bonus))
    cd=int(DATA['misc']['travel_facility_cd'].split('|')[bid-1]);steps=max(0,now-int(b['at']))//cd if home.get('started_travel') else 0
    available=min(cap,int(b['stock'])+math.floor(steps*amount*cd/86400))
    return available,amount,cap,cd

def pet_aura_cap(pet):
    from .pet_training import M
    values=list(map(int,str(M['pet_exlevel_add_pas']).split('|')))
    index=max(1,min(len(values),int(pet.get('exlv',0))//5))
    return 30+values[index-1]


def pet_info(pet,row):
    grade=int(pet['grade']);cap=int(row[f'grade_lv{grade+1}']) if grade<int(row['max_grade']) else int(row['max_lv'])
    cost=EXP.get((row['id'],int(pet['lv'])),{}).get('cost','') if pet['lv']<cap else ''
    result={**pet,'cap':cap,'level_cost':cost,'grade_cost':row.get(f'grade_exp{grade+1}','') if pet['lv']>=cap else ''}
    skills=[]
    for i in range(1,5):
        lv=int(pet['skills'][i-1]);base=row[f'pas_skill{i}_id']
        r=SKILLS.get((base,max(1,lv)),{})
        effect=SKILLS.get((base,lv),{}).get('effect','')
        skills.append({'slot':i,'lv':lv,'open':grade>=int(row[f'pas_tier{i}']),'cost':r.get('cost',''),'effect':effect,'icon':r.get('icon',''),'max':pet_aura_cap(pet)})
    result['skill_details']=skills
    return result

def snapshot(state,now=None):
    now=int(time.time()) if now is None else now
    # View defaults in a copy; GET must not create or update save data.
    home=copy.deepcopy(state.get('home_systems',{}));scratch={**state,'home_systems':home};saved(scratch,int(state.get('created',now)))
    result={**home}
    result['pet_details']={pid:pet_info(pet,ROWS['pet'][pid]) for pid,pet in home['pets'].items()}
    result['missions']=[]
    for mid,(key,label,route) in MISSIONS.items():
        row=ROWS['battlepass_mission'][str(mid)];token=f'{mid}:{period(row,now)}'
        result['missions'].append({'id':mid,'label':label,'route':route,'goal':int(row['complete_value']),'progress':home['book']['counters'].get(token,0),'claimed':token in home['book']['claimed'],'award':row['award'],'xp':row['award2'],'period':int(row['type'])})
    result['buildings']=[]
    for bid in range(1,4):
        b=home['travel']['buildings'][str(bid)];value,out,cap,cd=stock(state,home,bid,now);row=ROWS[f'travel_building{bid}'][str(b['lv'])]
        slots=max(int(v) for k,v in pairs(DATA['misc']['travel_building_slot_limit']).items() if int(k)<=b['lv'])
        result['buildings'].append({**b,'id':bid,'stock':value,'out':out,'cap':cap,'item':next(iter(pairs(row['out_put']))),'cost':row['update'],'slots':slots,'wait':cd-max(0,now-b['at'])%cd if home.get('started_travel') else cd})
    return result

def action(state,request,developer=False,now=None,rng=None):
    if not isinstance(request,dict):raise ValueError('Datos inválidos')
    now=int(time.time()) if now is None else now;rng=rng or secrets.randbelow
    home=saved(state,now);kind=request.get('action');result={}
    def new_id():
        value=home['next_id'];home['next_id']+=1;return value
    if kind=='pet_select' and request.get('id') in (0,'0',None):home['selected_pet']=None;return {}  # fight without a Servant
    if kind in ('pet_activate','pet_level','pet_grade','pet_skill','pet_select'):
        pid=str(checked(request.get('id'),'Servant',1));row=ROWS['pet'].get(pid)
        if not row or row['is_open']!='1':raise ValueError('Servant no disponible')
        pet=home['pets'].get(pid)
        if kind=='pet_activate':
            if pet:raise ValueError('Servant ya activado')
            charge(state,pairs(row['active_cost']));pet={'lv':1,'grade':1,'skills':[0,0,0,0]};home['pets'][pid]=pet
        else:
            if not pet:raise ValueError('Activa el Servant primero')
            info=pet_info(pet,row)
            if kind=='pet_level':
                if not info['level_cost']:raise ValueError('Evoluciona antes de subir más niveles')
                charge(state,pairs(info['level_cost']));pet['lv']+=1
            elif kind=='pet_grade':
                if pet['grade']>=int(row['max_grade']) or pet['lv']<info['cap']:raise ValueError('Nivel insuficiente o evolución máxima')
                charge(state,pairs(info['grade_cost']));pet['grade']+=1
            elif kind=='pet_skill':
                slot=checked(request.get('slot'),'Habilidad',1,4);skill=info['skill_details'][slot-1]
                if not skill['open'] or skill['lv']>=skill['max']:raise ValueError('Habilidad bloqueada o al máximo')
                charge(state,pairs(skill['cost']));pet['skills'][slot-1]+=1
            else:home['selected_pet']=int(pid)
    elif kind=='contact_add':
        name=request.get('name','');avatar=request.get('avatar','head_1001')
        if not isinstance(name,str) or not 1<=len(name.strip())<=20 or any(ord(c)<32 for c in name):raise ValueError('Nombre de 1 a 20 caracteres')
        from .engine import PROFILE_CATALOG
        if avatar not in PROFILE_CATALOG['heads'] and avatar not in PROFILE_CATALOG['partners']:raise ValueError('Icono inválido')
        if len(home['contacts'])>=30:raise ValueError('Máximo 30 contactos locales')
        home['contacts'].append({'id':new_id(),'name':name.strip(),'avatar':avatar,'local':True})
    elif kind=='contact_delete':
        cid=checked(request.get('id'),'Contacto',1)
        if not any(c['id']==cid for c in home['contacts']):raise ValueError('Contacto inexistente')
        home['contacts']=[c for c in home['contacts'] if c['id']!=cid]
    elif kind=='draft':
        text=request.get('text');recipient=request.get('recipient','')
        if not isinstance(text,str) or not 1<=len(text.strip())<=500 or not isinstance(recipient,str) or len(recipient)>40:raise ValueError('Borrador inválido: máximo 500 caracteres')
        if len(home['drafts'])>=50:raise ValueError('Máximo 50 borradores')
        home['drafts'].append({'id':new_id(),'recipient':recipient,'text':text.strip(),'at':now})
    elif kind=='draft_delete':
        did=checked(request.get('id'),'Borrador',1);home['drafts']=[d for d in home['drafts'] if d['id']!=did]
    elif kind=='mail_test':
        if not developer:raise ValueError('Correo de prueba solo en modo desarrollador')
        if len(home['mail'])>=100:raise ValueError('Buzón lleno')
        home['mail'].append({'id':new_id(),'type':'system','title':'Prueba local de adjuntos','text':'Correo de prueba. Los adjuntos se pueden cobrar una sola vez.','awards':'1#100|2#10','read':False,'claimed':False,'at':now})
    elif kind in ('mail_read','mail_claim','mail_delete','mail_claim_all'):
        selected=home['mail'] if kind=='mail_claim_all' else [m for m in home['mail'] if m['id']==checked(request.get('id'),'Correo',1)]
        if not selected and kind!='mail_claim_all':raise ValueError('Correo inexistente')
        for m in selected:
            if kind=='mail_delete':
                if m['awards'] and not m['claimed']:raise ValueError('Recoge los adjuntos antes de borrar')
                home['mail'].remove(m)
            else:
                m['read']=True
                if kind in ('mail_claim','mail_claim_all') and not m['claimed']:
                    grant(state,pairs(m['awards']));m['claimed']=True
                elif kind=='mail_claim':raise ValueError('Adjuntos ya recogidos')
    elif kind=='book_mission':
        mid=checked(request.get('id'),'Misión',1)
        if mid not in MISSIONS:raise ValueError('Misión aún no reconstruida')
        row=ROWS['battlepass_mission'][str(mid)];token=f'{mid}:{period(row,now)}';book=home['book']
        if token in book['claimed']:raise ValueError('Misión ya recogida')
        if int(book['counters'].get(token,0))<int(row['complete_value']):raise ValueError('Misión incompleta')
        grant(state,pairs(row['award']));grant(state,pairs(row['award2']));book['claimed'].append(token)
    elif kind=='book_tier':
        tier=checked(request.get('id'),'Nivel',1,50);row=ROWS['battlepass_award'][str(tier)];book=home['book']
        if tier in book['tiers']:raise ValueError('Premio ya recogido')
        if int(state['items'].get('117',0))<int(row['cost_total']):raise ValueError('Falta experiencia del Libro')
        grant(state,pairs(row['free_award']));book['tiers'].append(tier)
    elif kind in ('book_shop','castle_shop'):
        table='shop_battlepass' if kind=='book_shop' else 'activity_lafuli_shop';sid=str(checked(request.get('id'),'Oferta',1));row=ROWS[table].get(sid)
        if not row:raise ValueError('Oferta inexistente')
        purchases=home['book']['shop'] if kind=='book_shop' else home.setdefault('castle_shop',{})
        limit=int(row['buy_time'] if kind=='book_shop' else row['limit'])
        if int(purchases.get(sid,0))>=limit:raise ValueError('Límite de compra alcanzado')
        charge(state,pairs(row['cost']));grant(state,pairs(row['item'] if kind=='book_shop' else row['award']));purchases[sid]=int(purchases.get(sid,0))+1
    elif kind in ('travel_start','travel_collect','travel_upgrade','travel_assign'):
        bid=checked(request.get('id',1),'Edificio',1,3);b=home['travel']['buildings'][str(bid)];row=ROWS[f'travel_building{bid}'][str(b['lv'])]
        value,out,cap,cd=stock(state,home,bid,now)
        if kind=='travel_start':
            if home.get('started_travel'):raise ValueError('Producción ya iniciada')
            home['started_travel']=True
            for building in home['travel']['buildings'].values():building['at']=now
        elif kind=='travel_collect':
            if value<=0:raise ValueError('Todavía no hay recursos para recoger')
            grant(state,{next(iter(pairs(row['out_put']))):value});b['stock']=0;b['at']=now-((now-b['at'])%cd)
        elif kind=='travel_upgrade':
            if str(b['lv']+1) not in ROWS[f'travel_building{bid}']:raise ValueError('Edificio al máximo')
            requirements=pairs(DATA['misc']['travel_train_facility_limit'])
            if sum(home['travel']['training'].values())<requirements[str(b['lv']+1)]:raise ValueError('Mejora el entrenamiento para ampliar este edificio')
            charge(state,pairs(row['update']));b['stock']=value;b['at']=now-((now-b['at'])%cd);b['lv']+=1
        elif kind=='travel_assign':
            ids=request.get('partners');slots=max(int(v) for k,v in pairs(DATA['misc']['travel_building_slot_limit']).items() if int(k)<=b['lv'])
            if not isinstance(ids,list) or len(ids)>slots or any(isinstance(i,bool) or not isinstance(i,int) for i in ids) or len(set(ids))!=len(ids):raise ValueError('Formación de edificio inválida')
            owned={p['partner_id'] for p in state['partners']};other={p for key,x in home['travel']['buildings'].items() if key!=str(bid) for p in x['partners']}
            if not set(ids)<=owned or set(ids)&other:raise ValueError('Chica no disponible para este edificio')
            b['stock']=value;b['at']=now-((now-b['at'])%cd);b['partners']=ids
    elif kind=='travel_train_set':
        # ExploreTrainingRoomWindow: three girls per discipline; slot k opens at misc.travel_train_slot_limit ("1#1|11#2|21#3")
        tid=str(checked(request.get('id'),'Entrenamiento',1,5));slot=checked(request.get('slot'),'Hueco',1,3);pid=checked(request.get('partner_id',0),'Chica',0)
        lv=int(home['travel']['training'].get(tid,1));need={int(n):int(l) for l,n in (p.split('#') for p in str(DATA['misc'].get('travel_train_slot_limit','1#1|11#2|21#3')).split('|'))}
        if lv<need.get(slot,99):raise ValueError(f'Se abre al nivel {need.get(slot)}')
        rooms=home['travel'].setdefault('train_partners',{str(i):[0,0,0] for i in range(1,6)})
        if pid:
            if not any(p['partner_id']==pid for p in state['partners']):raise ValueError('Chica no encontrada')
            for r in rooms.values():
                for i,x in enumerate(r):
                    if x==pid:r[i]=0
        rooms.setdefault(tid,[0,0,0])[slot-1]=pid
    elif kind=='travel_train':
        tid=str(checked(request.get('id'),'Entrenamiento',1,5));row=ROWS['travel_train'][tid];levels=home['travel']['training'];lv=int(levels.get(tid,0))
        minimum=min(int(levels.get(str(i),1)) for i in range(1,6) if str(i)!=tid)
        requirements=pairs(DATA['misc']['travel_train_grade_limit'])
        if lv>=int(row['lv_max']) or int(requirements[str(lv+1)])>minimum:raise ValueError('Sube las otras disciplinas de entrenamiento primero')
        base=pairs(row['base_cost']);growth=[int(v) for v in row['grow_cost'].split('|')]
        cost={key:value+growth[i]*(lv-1) for i,(key,value) in enumerate(base.items())};charge(state,cost);levels[tid]=lv+1
    elif kind=='cosmos_select':
        mode=checked(request.get('mode'),'Modalidad',4,5);choice=checked(request.get('choice',757001),'Objetivo',1)
        if str(choice) not in ROWS['starry_altar']['4']['optional_award'].split('|'):raise ValueError('Objetivo inválido')
        home['cosmos'].update(mode=mode,choice=choice)
    elif kind=='cosmos_draw':
        count=checked(request.get('count',1),'Cantidad',1,10)
        if count not in (1,10):raise ValueError('Elige 1 o 10 sorteos')
        cosmos=home['cosmos'];row=ROWS['starry_altar'][str(cosmos['mode'])];charge(state,{k:n*count for k,n in pairs(row['cost']).items()})
        weights=[float(x) for x in row['wight'].split('|')];pool=DATA['dropbox'];total=sum(int(r['weight']) for r in pool);awards=[]
        for _ in range(count):
            roll=rng(1000000);reward={};partner=None
            if len(weights)>1 and roll<int(weights[1]*1000000):
                partner=cosmos['choice'];pid=state['next_partner_id'];state['next_partner_id']+=1
                state['partners'].append({'partner_id':pid,'table_id':partner,'lv':1,'grade':0,'awake':0,'equips':[],'pos':0,'show_skin':1})
            elif roll<int((weights[0]+(weights[1] if len(weights)>1 else 0))*1000000):reward=pairs(row['extra_award'])
            else:
                target=rng(total)
                for r in pool:
                    target-=int(r['weight'])
                    if target<0:reward=pairs(r['item']);break
            bonus={}
            if cosmos['mode']==5:
                cosmos['count']+=1
                if cosmos['count']>=40:bonus=pairs(row['type2_award'].split('|',1)[1]);cosmos['count']=0
            grant(state,reward);grant(state,bonus)
            entry={'at':now,'items':reward,'bonus':bonus,'partner':partner,'mode':cosmos['mode']};awards.append(entry)
        cosmos['history']=(awards+cosmos['history'])[:60];result['awards']=awards
    else:raise ValueError('Acción del menú desconocida')
    return result
