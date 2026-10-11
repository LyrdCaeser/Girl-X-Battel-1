"""Growth Diary: original 40 chapters/160 missions, local metrics (LOCAL-078).

Metrics are derived from current saves and recorded local actions. Successful
writes latch progress so retiring/unequipping Girls does not undo completion.
No fabricated history for counters absent in older saves; unsupported objectives
remain visible and unclaimable. Chapters advance only after all four task rewards
and then the chapter reward are claimed, as GrowthDiary:checkCanAward requires.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data/growth_diary.json').read_text())
MISSIONS={int(k):v for k,v in D['missions'].items()}
CHAPTERS={int(k):v for k,v in D['chapters'].items()}
GEAR=json.loads((ROOT/'data/equipment.json').read_text())['items']
UNLOCK_STAGE=5  # function 54: open_type=2, open_value=5
LEVELS={1:10,2:30,3:60,4:100,5:160,6:180,7:200,72:140}
STARS={8:5,9:6,10:7,11:9,12:10,13:11,14:13}
COUNTERS={25:'growth_echoes_gold',26:'growth_idle_gold',27:'growth_transfer',28:'growth_market',
          30:'growth_full_team',32:'growth_shard5',33:'growth_graduate5',34:'arena_win',
          39:'growth_exchange',42:'growth_bff',44:'growth_league_shop',46:'forge',48:'advanced',
          51:'sanctuary',67:'growth_high_slots',68:'gamble',69:'enroll',
          37:'growth_guild_damage',54:'growth_friend_boss',66:'growth_training',47:'growth_patrol_buy',52:'growth_sanctuary9',
          58:'growth_explore',59:'growth_chests',70:'growth_buttons',71:'growth_dorm_gold',
          63:'growth_elite_skill',65:'growth_astral',85:'tavern4',86:'tavern5',87:'tavern6',88:'tavern7'}


def checked(v):
    if isinstance(v,bool) or not isinstance(v,int) or v<=0:raise ValueError('Identificador inválido')
    return v


def saved(state):
    return state.setdefault('growth_diary',{'missions':[],'chapters':[],'progress':{},'counts':{}})


def record(state,key,count=1):
    d=saved(state);d.setdefault('counts',{})[key]=int(d.get('counts',{}).get(key,0))+count


def metric(state,r,roster,level):
    typ=int(r['type']);mid=int(r['id']);home=state.get('home_systems') or {}
    pets=list((home.get('pets') or {}).values())
    if typ in LEVELS:return sum(int(p.get('lv',1))>=LEVELS[typ] for p in roster)
    if typ in STARS:return sum(int(p.get('stars',0))>=STARS[typ] for p in roster)
    # The source reuses type 15 for mission 70 (Servant Lv15) and 157 (Girl 15★).
    if mid==157:return sum(int(p.get('stars',0))>=15 for p in roster)
    if typ in (15,23):return sum(int(p.get('lv',0))>={15:15,23:5}[typ] for p in pets)
    if typ in (16,17):return sum(int(lv)>={16:10,17:20}[typ] for lv in (state.get('guild_lab') or {}).get('levels',{}).values())
    if typ in (18,19,20,21,22):
        threshold={18:5,19:10,20:20,21:25,22:30}[typ]
        return sum(int(lv)>=threshold for p in pets for lv in p.get('skills',[]))
    if typ in COUNTERS:
        key=COUNTERS[typ]
        return int((state.get('missions') or {}).get('totals',{}).get(key,0))+int((state.get('growth_diary') or {}).get('counts',{}).get(key,0))
    if typ==38:return len(home.get('contacts') or [])
    if typ==74:return sum(int(p.get('exlv',0))>0 for p in pets)
    if typ==49:return sum(int(p.get('grade',1))>1 for p in pets)
    if typ==60:return sum(int(n) for n in (state.get('house_dress') or {}).get('bought',{}).values())
    if typ==73:return int((state.get('stellar_altar') or {}).get('draws',0))
    if typ==64:return int((state.get('shrine') or {}).get('completed',0))
    if typ==45:
        from .house_exam import STAGES
        return max([int(STAGES.get(int(i),{}).get('school_sort',0)) for i in (state.get('house_exam') or {}).get('max',{}).values()] or [0])
    if typ in (55,78):
        from .hero_challenge import STAGES, FIRST
        done=set((state.get('hero_challenge') or {}).get('first_done',[]));count=0
        for first in FIRST.values():
            stage=first
            for _ in range({55:3,78:6}[typ]-1):stage=int(STAGES.get(stage,{}).get('next_id',0))
            count+=int(stage in done and stage in STAGES)
        return count
    if typ in (56,57):
        from . import old_campus
        oc=state.get('old_campus') or {}
        if typ==57:return sum(int(v.get('best',0)) for v in oc.get('levels',{}).values())
        if not oc:return 0
        return sum(set(old_campus.stage_ids(oc['season'],int(k)))<=set(v.get('done',[])) for k,v in oc.get('levels',{}).items())
    if typ in (50,75):
        threshold={50:2,75:4}[typ]
        equipped=[i for p in roster for i in (p.get('equips') or [])]
        owned={k:int(n) for k,n in state.get('items',{}).items()}
        for i in equipped:owned[str(i)]=owned.get(str(i),0)+1
        return sum(n for i,n in owned.items() if int(GEAR.get(i,{}).get('pos',0))==6 and int(GEAR[i].get('star',0))>=threshold)
    if typ==29:return int(state.get('max_stage',0))
    if typ==35:return int((state.get('tower') or {}).get('max_stage',0))
    if typ==36:return int(bool(state.get('guild')))
    if typ==40:return level
    if typ==41:return len(pets)
    if typ==43:return int((state.get('patrol') or {}).get('max_stage',0))
    if typ==53:return sum(int(lv)>0 for lv in (state.get('echoes') or {}).get('tec',{}).values())
    if typ==61:return max([int(p.get('love_point',0)) for p in roster] or [0])
    if typ in (31,76,77,79,80,81,82,83,84):
        def gear(p):return [GEAR.get(str(i),{}) for i in (p.get('equips') or [])]
        if typ in (76,77):
            threshold={76:4,77:6}[typ]
            return sum(len((p.get('equips') or [])[:4])==4 and all(int(g.get('qlt',0))>=threshold for g in gear(p)[:4]) for p in roster)
        # Crystals occupy slot 5; Antique slot 6. Match original item_lv/quality.
        if typ==31:return sum(len(gear(p))>=5 and bool(gear(p)[4]) for p in roster)
        if typ in (79,80,81,82):
            threshold={79:3,80:5,81:8,82:11}[typ]
            return sum(len(gear(p))>=5 and int(gear(p)[4].get('item_lv',0))>=threshold for p in roster)
        threshold={83:4,84:5}[typ]
        return sum(len(gear(p))>=6 and int(gear(p)[5].get('qlt',0))>=threshold for p in roster)
    return None


def current_chapter(state):
    done=set((state.get('growth_diary') or {}).get('chapters',[]))
    return next((c for c in sorted(CHAPTERS) if c not in done),max(CHAPTERS))


def measured(state,r,roster,level):
    raw=metric(state,r,roster,level)
    if raw is None or r['special_mission']!=1:return raw
    base=(state.get('growth_diary') or {}).get('baseline',{}).get(str(r['id']))
    # Original English text 09: star-marked tasks start counting on chapter unlock.
    return max(0,raw-int(base)) if base is not None else 0


def prepare(state,roster,level):
    # Baselines only: loading a save must not latch ordinary progress.
    if int(state.get('max_stage',0))<UNLOCK_STAGE:return
    current=current_chapter(state)
    for mid,r in MISSIONS.items():
        if r['special_mission']==1 and int(r['chapter_id'])==current:
            raw=metric(state,r,roster,level)
            if raw is not None:saved(state).setdefault('baseline',{}).setdefault(str(mid),raw)


def observe(state,roster,level):
    d=saved(state);progress=d.setdefault('progress',{});base=d.setdefault('baseline',{})
    current=current_chapter(state)
    for mid,r in MISSIONS.items():
        if r['special_mission']==1:
            if int(r['chapter_id'])!=current or int(state.get('max_stage',0))<UNLOCK_STAGE:continue
            raw=metric(state,r,roster,level)
            if raw is not None:base.setdefault(str(mid),raw)
        have=measured(state,r,roster,level)
        if have is not None:progress[str(mid)]=max(int(progress.get(str(mid),0)),min(int(r['complete_value']),have))


def snapshot(state,roster,level):
    d=state.get('growth_diary') or {};claimed=set(d.get('missions',[]));chapters=set(d.get('chapters',[]))
    current=current_chapter(state)
    unlocked=int(state.get('max_stage',0))>=UNLOCK_STAGE
    pages=[]
    for c,row in sorted(CHAPTERS.items()):
        tasks=[]
        for mid in row['missions']:
            r=MISSIONS[mid];now=measured(state,r,roster,level);need=int(r['complete_value'])
            have=max(int(d.get('progress',{}).get(str(mid),0)),now or 0)
            tasks.append({'id':mid,'text':r['text'],'need':need,'have':min(need,have),'tracked':now is not None,
                          'claimed':mid in claimed,'can':unlocked and c==current and mid not in claimed and now is not None and have>=need,
                          'award':r['awards'],'special':r['special_mission']==1,'window':r['window']})
        pages.append({'id':c,'tasks':tasks,'award':row['award'],'claimed':c in chapters,'locked':not unlocked or c>current,
                      'can':unlocked and c==current and c not in chapters and all(mid in claimed for mid in row['missions'])})
    return {'current':current,'finished':len(chapters)==len(CHAPTERS),'unlocked':unlocked,'unlock_stage':UNLOCK_STAGE,
            'chapters':pages,'tracked':sum(metric(state,r,roster,level) is not None for r in MISSIONS.values()),'total':len(MISSIONS)}


def awards(text):
    got={}
    for pair in str(text).split('|'):
        iid,n=pair.split('#');got[iid]=got.get(iid,0)+int(n)
    return got


def action(state,request,roster,level):
    if not isinstance(request,dict):raise ValueError('Datos inválidos')
    snap=snapshot(state,roster,level)
    if not snap['unlocked']:raise ValueError('Growth Diary se abre tras la fase 5 de campaña')
    kind=request.get('action');got={}
    if kind=='open':
        observe(state,roster,level);return {'got':got}
    ident=checked(request.get('id'))
    if kind=='mission':
        page=next((c for c in snap['chapters'] if any(t['id']==ident for t in c['tasks'])),None)
        task=next((t for t in page['tasks'] if t['id']==ident),None) if page else None
        if not task or not task['can']:raise ValueError('Misión sin completar, bloqueada o ya reclamada')
        got=awards(task['award']);saved(state)['missions'].append(ident)
    elif kind=='chapter':
        page=next((c for c in snap['chapters'] if c['id']==ident),None)
        if not page or not page['can']:raise ValueError('Reclama las cuatro misiones del capítulo primero')
        got=awards(page['award']);saved(state)['chapters'].append(ident)
    else:raise ValueError('Acción no disponible')
    for iid,n in got.items():state['items'][iid]=int(state['items'].get(iid,0))+n
    observe(state,roster,level)
    return {'got':got}
