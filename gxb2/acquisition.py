"""Exchange and Slots reconstructed from client tables and request/response contracts.
Server-side selection and refresh generation are local weighted replacements, not recovered server code.
"""
import copy,json,secrets
from pathlib import Path
from . import clock,point_events
DATA=json.loads((Path(__file__).resolve().parents[1]/'data/acquisition.json').read_text())
PARTNERS=json.loads((Path(__file__).resolve().parents[1]/'data/partner.json').read_text())
PLAYER_EXP=json.loads((Path(__file__).resolve().parents[1]/'data/exp_player.json').read_text())
BOXES={}
for row in DATA['dropbox'].values():BOXES.setdefault(int(row['dropbox_id']),[]).append(row)

def number(v,label,low=1,high=2**31-1):
    if type(v) is not int or not low<=v<=high:raise ValueError(f'{label}: valor inválido')
    return v

def pairs(text):
    out={}
    for part in str(text or '').split('|'):
        if '#' in part:
            k,n=part.split('#')[:2];out[k]=out.get(k,0)+int(n)
    return out

def charge(state,cost):
    if any(int(state['items'].get(k,0))<n for k,n in cost.items()):raise ValueError('Faltan recursos')
    for k,n in cost.items():state['items'][k]=int(state['items'].get(k,0))-n

def grant(state,awards):
    for k,n in awards.items():
        if k!='0' and n:state['items'][k]=int(state['items'].get(k,0))+n

def pick(rows,rng):
    rows=[r for r in rows if int(r['weight'])>0]
    total=sum(int(r['weight']) for r in rows)
    if not total:raise ValueError('No quedan premios disponibles')
    roll=rng(total)
    for r in rows:
        roll-=int(r['weight'])
        if roll<0:return r
    raise ValueError('Resultado aleatorio inválido')

def prize(row,rng):
    p=str(row['item']).split('#');lo=int(p[1]);hi=int(p[2]) if len(p)>2 else lo
    return {'item_id':int(p[0]),'item_num':lo+(rng(hi-lo+1) if hi>lo else 0)}

def level(state):
    return max(int(k) for k,r in PLAYER_EXP.items() if int(r['all_exp'])<=int(state['items'].get('3',0)))

def is_locked(partner):
    flags=partner.get('flags') or []
    return any(int(v or 0) for v in flags) or any(partner.get(k,0) for k in ('lock_flags','lock_flag','locked'))

def eligible(partner):
    row=PARTNERS[str(partner['table_id'])]
    return (str(partner['table_id']) in DATA['partner_replace'] and int(row['group']) in (1,2,3,4)
            and int(row['max_star'])+int(partner.get('awake',0)) in (4,5)
            and not is_locked(partner))

def replacement_pool(partner):
    tid=partner['table_id'];row=PARTNERS[str(tid)];cfg=DATA['partner_replace'][str(tid)]
    # ReplaceProbabilityWindow explicitly excludes the current girl.
    return [r for r in BOXES.get(int(cfg['dropbox_id']),[]) if str(r['item']).split('#')[0] in PARTNERS
            and int(str(r['item']).split('#')[0])!=tid
            and int(PARTNERS[str(r['item']).split('#')[0]]['group'])==int(row['group'])
            and int(PARTNERS[str(r['item']).split('#')[0]]['max_star'])==int(row['max_star'])]

def options(state,typ,developer=False):
    cfg=DATA['gamble_config'][str(typ)];lv=level(state);vip=int(state.get('vip_level',0))
    count=[int(v) for v in cfg['times'].split('|')];cost=cfg['cost'].split('|');awards=cfg['award'].split('|')
    vips=[int(v) for v in cfg['need_vip'].split('|')];levels=[int(v) for v in cfg['need_level'].split('|')]
    opened=typ==1 or developer or lv>=levels[0] or vip>=vips[0]
    return [{'index':i+1,'times':n,'cost':pairs(cost[i]),'bonus':pairs(awards[i]),
             'available':opened and (developer or (i==0) or (i>0 and (((levels[i]>0 and lv>=levels[i]) or (vips[i]>0 and vip>=vips[i])) if typ==1 else vip>=vips[i]))),
             'level':levels[i],'vip':vips[i]} for i,n in enumerate(count)]

def create_board(state,typ,now,rng):
    cfg=DATA['gamble_config'][str(typ)];items=[]
    for row in sorted(DATA[cfg['gamble_table']].values(),key=lambda r:int(r['id'])):
        box=None
        for idx in range(1,int(row['part_num'])+1):
            lo,hi=map(int,str(row[f'lv{idx}']).split('|'))
            if lo<=level(state)<=hi:box=int(row[f'dropbox_id{idx}']);break
        if box is None:raise ValueError('No hay pool para este nivel')
        reward=prize(pick(BOXES.get(box,[]),rng),rng)
        items.append({**reward,'weight':int(row['weight']),'buy_limit':int(row['limit_buy'] or 0),'buy_times':0,'cool':int(row['cool'] or 0)})
    return {'gamble_type':typ,'items':items,'system_refresh_time':now+int(cfg['system_refresh_time']),
            'free_refresh_time':now-int(cfg['free_refresh_time']),'last_time':now,'history':[]}

def board(state,typ,now,rng):
    saved=state.setdefault('gamble',{});data=saved.get(str(typ))
    if not data or now>=int(data['system_refresh_time']):
        previous=data
        data=create_board(state,typ,now,rng)
        if previous:
            data['free_refresh_time']=previous['free_refresh_time'];data['history']=previous.get('history',[])
        saved[str(typ)]=data
    return data

def wire(data):
    return {k:copy.deepcopy(data[k]) for k in ('gamble_type','items','system_refresh_time','free_refresh_time')}

# Lucky Store is shop_type 3 in ShopConfigTable. Selection is an offline adapter;
# the client supplied weights but the original server's exact sampling is unavailable.
def create_lucky(now,rng):
    cfg=DATA['shop_config']['3'];pool=list(DATA['shop_luck'].values());items=[]
    for _ in range(int(cfg['slot_num'])):
        row=pick(pool,rng);pool=[r for r in pool if r['id']!=row['id']]
        iid,n=next(iter(pairs(row['item']).items()));cid,cost=next(iter(pairs(row['cost']).items()))
        items.append({'item':[int(iid),n],'cost':[int(cid),cost],'buy_times':0})
    return {'shop_type':3,'items':items,'refresh_time':now,'last_time':now}

def lucky_wire(data):
    return {k:copy.deepcopy(data[k]) for k in ('shop_type','items','refresh_time')}

def lucky_dispatch(state,name,request,now,developer,rng):
    number(request.get('shop_type'),'Tienda',3,3)
    cfg=DATA['shop_config']['3']
    if not developer and level(state)<int(cfg['limit_level']):raise ValueError('Lucky Store requiere nivel 14')
    data=state.setdefault('shops',{}).get('3')
    if not data:
        data=create_lucky(now,rng);state['shops']['3']=data
    now=max(now,int(data.get('last_time',data['refresh_time'])))
    if name=='GET_SHOP_INFO':return lucky_wire(data)
    if name=='REFRESH_SHOP':
        if now<int(data['refresh_time'])+int(cfg['refresh_free_time']):charge(state,pairs(cfg['refresh_cost']))
        data=create_lucky(now,rng);state['shops']['3']=data
        return lucky_wire(data)
    idx=number(request.get('index'),'Oferta',1,len(data['items']))
    qty=number(request.get('num',1),'Cantidad',1)
    entry=data['items'][idx-1];limit=int(cfg['slot_buy_time'].split('|')[idx-1])
    if entry.get('not_selling')==1 or (limit>0 and entry['buy_times']+qty>limit):raise ValueError('Oferta agotada')
    charge(state,{str(entry['cost'][0]):entry['cost'][1]*qty})
    grant(state,{str(entry['item'][0]):entry['item'][1]*qty})
    entry['buy_times']+=qty;data['last_time']=now
    return {**lucky_wire(data),'index':idx,'num':qty}

def snapshot(state,now=None,developer=False):
    now=clock.epoch(now);out={'item_icons':DATA.get('item_icons',{}),'exchange':copy.deepcopy(state.get('exchange')),'eligible':[], 'slots':{}}
    cfg=DATA['shop_config']['3'];shop=copy.deepcopy((state.get('shops') or {}).get('3'))
    out['lucky']={'board':shop,'available':developer or level(state)>=int(cfg['limit_level']),
                  'refresh_cost':pairs(cfg['refresh_cost']),'limit':int(cfg['slot_buy_time'].split('|')[0]),
                  'free_refresh_at':shop['refresh_time']+int(cfg['refresh_free_time']) if shop else now+int(cfg['refresh_free_time'])}
    for p in state['partners']:
        if eligible(p):out['eligible'].append({'partner_id':p['partner_id'],'cost':pairs(DATA['partner_replace'][str(p['table_id'])]['cost'])})
    for typ in (1,2):
        data=copy.deepcopy((state.get('gamble') or {}).get(str(typ)))
        cfg=DATA['gamble_config'][str(typ)]
        out['slots'][str(typ)]={'board':data,'options':options(state,typ,developer),
                              'free_refresh_at':(data['free_refresh_time']+int(cfg['free_refresh_time'])) if data else now,
                              'refresh_cost':pairs(cfg['refresh_cost']),'expired':bool(data and now>=data['system_refresh_time'])}
    return out

def dispatch(state,name,request,now=None,developer=False,rng=None):
    now=clock.epoch(now);rng=rng or secrets.randbelow
    if name in ('GET_SHOP_INFO','REFRESH_SHOP','BUY_SHOP_ITEM'):
        return lucky_dispatch(state,name,request,now,developer,rng)
    if name in ('PROPHET_REPLACE','PROPHET_REPLACE_SAVE'):
        pid=number(request.get('partner_id'),'Chica');partner=next((p for p in state['partners'] if p['partner_id']==pid),None)
        if not partner:raise ValueError('Chica inexistente')
        pending=state.get('exchange')
        if name=='PROPHET_REPLACE':
            if pending:raise ValueError('Guarda o descarta primero el intercambio pendiente')
            if not eligible(partner):raise ValueError('Exchange admite chicas desbloqueadas 4★/5★ de Ghost/Human/Monster/Fairy')
            pool=replacement_pool(partner)
            chosen=int(str(pick(pool,rng)['item']).split('#')[0])
            charge(state,pairs(DATA['partner_replace'][str(partner['table_id'])]['cost']))
            state['exchange']={'partner_id':pid,'replace_id':chosen,'source_id':partner['table_id']}
            return {'partner_id':pid,'replace_id':chosen}
        save=number(request.get('is_save'),'Guardar',0,1)
        if not pending or pending['partner_id']!=pid or pending['source_id']!=partner['table_id']:raise ValueError('No hay intercambio pendiente para esta chica')
        if save:
            partner['table_id']=pending['replace_id']
            equips=(list(partner.get('equips') or [])+[0]*7)[:7];equips[6]=0;partner['equips']=equips
            partner['show_skin']=1
            for k in ('is_vowed','love_point','wedding_date'):partner[k]=0
        state.pop('exchange',None)
        return {'partner_id':pid,'replace_id':pending['replace_id'],'is_save':save,'is_vowed':0,'love_point':0,'wedding_date':0}
    typ=number(request.get('gamble_type',1),'Modalidad',1,2)
    opts=options(state,typ,developer)
    if not opts[0]['available']:raise ValueError('High Stakes requiere nivel 80 o VIP 3')
    data=board(state,typ,now,rng);now=max(now,int(data.get('last_time',now)))
    cfg=DATA['gamble_config'][str(typ)]
    if name=='GAMBLE_GET_INFO':return wire(data)
    if name=='GAMBLE_REFRESH':
        free=now>=int(data['free_refresh_time'])+int(cfg['free_refresh_time'])
        if not free:charge(state,pairs(cfg['refresh_cost']))
        new=create_board(state,typ,now,rng)
        new['free_refresh_time']=now if free else data['free_refresh_time'];new['history']=data.get('history',[])
        state['gamble'][str(typ)]=new
        return wire(new)
    if name!='GAMBLE_GET_AWARD':raise ValueError('Acción no implementada')
    idx=number(request.get('index',1),'Tirada',1,len(opts));option=opts[idx-1]
    if not option['available']:raise ValueError('Cantidad bloqueada por nivel/VIP')
    charge(state,option['cost']);awards=[];received={}
    for _ in range(option['times']):
        candidates=[{**r,'slot':i+1} for i,r in enumerate(data['items']) if not r['buy_limit'] or r['buy_times']<r['buy_limit']]
        result=pick(candidates,rng);slot=result['slot'];data['items'][slot-1]['buy_times']+=1
        key=str(result['item_id']);received[key]=received.get(key,0)+result['item_num'];awards.append(slot)
    grant(state,received);grant(state,option['bonus'])
    if typ==1:point_events.add(state,'gamble',option['times'],now=now)
    data['last_time']=now
    data['history']=([{'at':now,'times':option['times'],'items':received,'bonus':option['bonus']}] +data.get('history',[]))[:50]
    return {'gamble_type':typ,'awards':awards}
