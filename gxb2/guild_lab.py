"""GuildLabWindow rules, original tables/refunds; local personal lab, no remote guild."""
import json
from pathlib import Path
DATA=json.loads((Path(__file__).resolve().parents[1]/'data/guild_lab.json').read_text())
ROWS=DATA['skills'];REFUNDS={(str(r['skill_id']),int(r['skill_lv'])):r['items'] for r in DATA['restore'].values()}

def checked(v,name,low=1,high=2147483647):
    if isinstance(v,bool) or not isinstance(v,int) or not low<=v<=high:raise ValueError(name+': valor inválido')
    return v

def pairs(text):
    result={}
    for part in str(text).split('|'):
        if '#' not in part:continue
        key,value=part.split('#',1);key=str(key)
        result[key]=result.get(key,0)+int(value)
    return result

def saved(state):return state.setdefault('guild_lab',{'levels':{},'reset_times':{}})
def level(state,sid):return int(saved(state)['levels'].get(str(sid),0))
def skills(state):return [{'skill_id':int(sid),'skill_lv':int(lv)} for sid,lv in sorted(saved(state)['levels'].items()) if int(lv)>0 and sid in ROWS]
def requirements(row):
    ids=[int(v) for v in str(row['pre_skill']).split('|')];levels=[int(v) for v in str(row['lv_req']).split('|')]
    return list(zip(ids,levels)) if ids[0]>0 else []
def unlocked(state,row):return all(level(state,sid)>=lv for sid,lv in requirements(row))
def cost(row,start,count=1):
    result={}
    for field,grow in [('base_gold','grow_gold'),('base_guild_coin','grow_guild_coin')]:
        for key,n in pairs(row[field]).items():result[key]=result.get(key,0)+sum(n+int(row[grow])*lv for lv in range(start,start+count))
    return result

def effects(row,lv):
    base=dict(v.split('#') for v in str(row['base_effect']).split('|'));grow=dict(v.split('#') for v in str(row['grow_effect']).split('|'))
    return {k:round(float(v)+(lv-1)*float(grow[k]),8) if lv>0 else 0 for k,v in base.items()}

def reset_preview(state,group):
    found=[r for r in ROWS.values() if int(r['reset'])==group];refund={}
    for row in found:
        lv=level(state,row['id'])
        if lv:
            text=REFUNDS.get((str(row['id']),lv))
            if text is None:raise ValueError('No se recuperó la devolución de este nivel')
            for k,n in pairs(text).items():refund[k]=refund.get(k,0)+n
    return refund,({} if not saved(state)['reset_times'].get(str(group),0) else pairs(DATA['reset_cost']))

def snapshot(state):
    lab=saved(state);nodes=[]
    for row in ROWS.values():
        lv=level(state,row['id']);maximum=int(row['lv_max']);nodes.append({'id':row['id'],'job':row['job'],'reset':row['reset'],'level':lv,'max':maximum,'name':DATA['text'][str(row['id'])]['name'],'icon':str(row['icon']).removesuffix('_png'),'unlocked':unlocked(state,row),'requirements':requirements(row),'cost':cost(row,lv) if lv<maximum else {},'effects':effects(row,lv),'next_effects':effects(row,min(maximum,lv+1))})
    resets={}
    for group in sorted(set(int(r['reset']) for r in ROWS.values())):
        refund,charge=reset_preview(state,group);resets[str(group)]={'refund':refund,'cost':charge,'times':lab['reset_times'].get(str(group),0)}
    return {'nodes':nodes,'resets':resets,'skills':skills(state)}

def dispatch(state,name,req):
    lab=saved(state)
    if name=='GUILD_GET_SKILLS':return {'skills':[{'skill_id':int(k),'skill_lv':level(state,k)} for k in ROWS],'reset_times':[int(lab['reset_times'].get(str(i),0)) for i in range(1,15)]}
    if name=='GUILD_UPGRADE_SKILL':
        sid=checked(req.get('skill_id'),'skill_id');n=checked(req.get('num'),'num',1,60);row=ROWS.get(str(sid))
        if not row:raise ValueError('Investigación desconocida')
        old=level(state,sid)
        if not unlocked(state,row):raise ValueError('Completa primero las investigaciones requeridas')
        if old+n>int(row['lv_max']):raise ValueError('Se supera el nivel máximo')
        charge=cost(row,old,n)
        if any(int(state['items'].get(k,0))<v for k,v in charge.items()):raise ValueError('Faltan monedas de gremio u oro')
        for k,v in charge.items():state['items'][k]=int(state['items'].get(k,0))-v
        lab['levels'][str(sid)]=old+n
        return {'skill_id':sid,'num':n}
    group=checked(req.get('job'),'job',1,14)
    if group not in {int(r['reset']) for r in ROWS.values()}:raise ValueError('Rama desconocida')
    refund,charge=reset_preview(state,group)
    if not refund:raise ValueError('Esta rama no tiene investigaciones para reiniciar')
    if any(int(state['items'].get(k,0))<v for k,v in charge.items()):raise ValueError('Faltan gemas para reiniciar')
    for k,v in charge.items():state['items'][k]-=v
    result=[]
    for row in ROWS.values():
        if int(row['reset'])==group:lab['levels'][str(row['id'])]=0;result.append({'skill_id':row['id'],'skill_lv':0})
    for k,v in refund.items():state['items'][k]=int(state['items'].get(k,0))+v
    lab['reset_times'][str(group)]=lab['reset_times'].get(str(group),0)+1
    return {'skills':result,'restore_items':[{'item_id':int(k),'item_num':v} for k,v in refund.items()]}
