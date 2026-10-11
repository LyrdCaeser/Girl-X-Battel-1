"""Campaign idle income (hang-up) and loot.

Economy follows CampaignWindow.lua: the hang stage yields its `gold`, `exp_partner` and `exp_player`
every 5 seconds, capped at misc.hang_up_time_max (12 h). Item loot rolls the stage `dropbox_ids`
(dropbox.lua weights over 10000; `id#min#max` gives a random amount). The drop cadence was decided by
the server and is not in the client: locally one roll per box every DROP_INTERVAL seconds.
"""
from __future__ import annotations
import json, secrets, time
from pathlib import Path
from . import vip, local_config

ROOT = Path(__file__).resolve().parents[1]
STAGES = json.loads((ROOT / 'data/stage.json').read_text())
BOXES = {}
for _row in json.loads((ROOT / 'data/dropbox.json').read_text()).values():
    BOXES.setdefault(int(_row['dropbox_id']), []).append(_row)
TICK = 5
MAX_TIME = 43200
DROP_INTERVAL = 600


def pair(text):
    key, value = str(text).split('#')[:2]
    return key, int(value)


def hang_stage(state):
    return int(state.get('current_stage') or 0) if state.get('max_stage') else 0


def saved(state, now):
    hang = state.setdefault('hang', {})
    hang.setdefault('since', now)
    hang.setdefault('drop_since', now)
    return hang


def change_stage(state, stage, now=None):
    """Local settlement policy: completed ticks/drops belong to their historical stage.
    Keep the original 5-second tick, 12-hour cap and local 600-second loot cadence.
    Legacy saves have no stage history; bind their pending interval to the saved stage.
    """
    now=int(time.time()) if now is None else int(now)
    hang=saved(state,now)
    history=hang.setdefault('history',[{'at':min(int(hang['since']),int(hang['drop_since'])), 'stage':hang_stage(state)}])
    now=max(now,int(history[-1]['at']),int(hang['since']),int(hang['drop_since']))
    if int(history[-1]['stage'])!=stage:
        if int(history[-1]['at'])==now:history[-1]['stage']=stage
        else:history.append({'at':now,'stage':stage})
    state['current_stage']=stage


def intervals(state, since, now, cadence):
    hang=state.get('hang') or {}
    history=hang.get('history') or [{'at':since,'stage':hang_stage(state)}]
    end=min(max(now,since),since+MAX_TIME)
    out=[]
    for i,event in enumerate(history):
        start=max(since,int(event['at']))
        stop=min(end,int(history[i+1]['at']) if i+1<len(history) else end)
        # Ticks are attributed to the stage where they finish; an exact switch boundary belongs to the old stage.
        count=max(0,(stop-since)//cadence-(start-since)//cadence)
        if count and str(event['stage']) in STAGES:out.append((int(event['stage']),count))
    return out


def pending(state, now=None):
    now=int(time.time()) if now is None else int(now)
    hang=state.get('hang') or {'since':now,'drop_since':now}
    stage=STAGES.get(str(hang_stage(state)))
    secs=max(0,min(now-int(hang['since']),MAX_TIME))
    if not stage:
        return {'stage':0,'seconds':0,'economy':{},'rolls':0,'rate':{},'max_seconds':MAX_TIME}
    economy={}
    for sid,ticks in intervals(state,int(hang['since']),now,TICK):
        row=STAGES[str(sid)]
        for key,amount in (pair(row['gold']),pair(row['exp_partner']),pair(row['exp_player'])):
            economy[key]=economy.get(key,0)+amount*ticks
    # vip.extra_output: idle bonus of the current VIP level (LOCAL-050 earns the level by playing)
    bonus=1+float(vip.LEVELS[min(int(state.get('vip',0) or 0),vip.MAX_LEVEL)]['extra_output'])
    economy={k:local_config.scale_reward(int(v*bonus)) for k,v in economy.items()}
    rate={k:local_config.scale_reward(int(v*bonus)) for k,v in (pair(stage['gold']),pair(stage['exp_partner']),pair(stage['exp_player']))}
    loot=intervals(state,int(hang['drop_since']),now,DROP_INTERVAL)
    return {'stage':int(stage['id']),'seconds':secs,'max_seconds':MAX_TIME,'rate':rate,
            'economy':economy,'rolls':sum(n for _,n in loot),'drop_seconds':max(0,min(now-int(hang['drop_since']),MAX_TIME)),'drop_interval':DROP_INTERVAL,
            'drop_show':str(stage.get('dropbox_show') or '')}


def roll(box, rng=secrets.randbelow):
    rows = BOXES.get(int(box), [])
    total = sum(int(r['weight']) for r in rows)
    if total <= 0:
        return None
    pick = rng(total)
    for row in rows:
        pick -= int(row['weight'])
        if pick < 0:
            parts = str(row['item']).split('#')
            if parts[0] in ('0', ''):
                return None
            low = int(parts[1]); high = int(parts[2]) if len(parts) > 2 else low
            return parts[0], low + (rng(high - low + 1) if high > low else 0)
    return None


def collect(state, now=None, rng=secrets.randbelow):
    now = int(time.time()) if now is None else now
    saved(state, now)
    info = pending(state, now)
    if not info['stage']:
        raise ValueError('Supera la primera fase para empezar a acumular recompensas')
    got = dict(info['economy'])
    for sid,rolls in intervals(state,int(state['hang']['drop_since']),now,DROP_INTERVAL):
        for _ in range(rolls):
            for box in str(STAGES[str(sid)]['dropbox_ids']).split('|'):
                item=roll(box,rng)
                if item:got[item[0]]=got.get(item[0],0)+local_config.scale_reward(item[1])
    if not any(got.values()):
        raise ValueError('Todavía no hay recompensas acumuladas')
    for k, n in got.items():
        state['items'][k] = int(state['items'].get(k, 0)) + n
    hang = state['hang']
    capped = now - int(hang['since']) >= MAX_TIME
    hang['since'] = now if capped else int(hang['since']) + info['seconds'] // TICK * TICK
    hang['drop_since'] = now if now - int(hang['drop_since']) >= MAX_TIME else int(hang['drop_since']) + info['rolls'] * DROP_INTERVAL
    if hang.get('history'):
        cutoff=min(hang['since'],hang['drop_since']);past=[e for e in hang['history'] if int(e['at'])<=cutoff]
        hang['history']=([{'at':cutoff,'stage':past[-1]['stage']}] if past else [])+[e for e in hang['history'] if int(e['at'])>cutoff]
    return {k: v for k, v in got.items() if v}
