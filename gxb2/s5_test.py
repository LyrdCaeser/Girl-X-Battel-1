"""S5 test-world reward core and deterministic welcome mail.
All reward callers must supply an authenticated, transaction-locked S5 profile.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os, time, json, hashlib
from . import goddess_gifts, s4_exclusive, skins, local_config

WORLD = 'S5'
NAME = 'S5 • Thiên Hư Không - Limited'
TZ = ZoneInfo('Asia/Ho_Chi_Minh')
DAYS = (0, 5)  # Monday, Saturday
WINDOWS = ((6, 9), (20, 23))
SONIA = 758001
MONTHANH_UID = 'GB3-854365013'
RESOURCES = {
    '1': 1_000_000_000, '9': 1_000_000_000,
    '10': 10_000_000, '417': 10_000_000, '173': 10_000_000,
    '34': 10_000, '44': 500_000, '198': 10_000_000, '199': 10_000_000,
    '359': 5_000_000, '360': 5_000_000, '26': 1_000_000, '27': 1_000_000,
}
SKIN_CHOICES = 10
SKIN_BOX = "990071"
EARLY_CARD = "990072"
EARLY_NAME = "S5▪︎ THẺ TRUY CẬP SSVIP SỚM"
EARLY_OPERATOR = "S5-OWNER-EARLY"
SVIP_CARD = "990073"
SVIP_NAME = "S5▪︎ VÉ TRUY CẬP HẠN GIỜ SVIP"
SVIP_OPERATOR = "S5-MONTHANH-SVIP"
SVIP_END = int(datetime(2026,11,28,6,0,tzinfo=TZ).timestamp())


def schedule(now):
    local = datetime.fromtimestamp(int(now), TZ)
    for offset in range(8):
        day = (local + timedelta(days=offset)).date()
        if day.weekday() not in DAYS:
            continue
        for start, end in WINDOWS:
            a = datetime(day.year, day.month, day.day, start, tzinfo=TZ)
            b = a.replace(hour=end)
            if a <= local < b:
                return {'server_id': WORLD, 'phase': 'open', 'server_now': int(now),
                        'phase_end': int(b.timestamp()), 'next_open_at': int(a.timestamp())}
            if a > local:
                return {'server_id': WORLD, 'phase': 'locked', 'server_now': int(now),
                        'phase_end': int(a.timestamp()), 'next_open_at': int(a.timestamp())}
    raise RuntimeError('Không xác định được lịch S5')


def sonia_allowed(uid):
    return str(uid) in (os.environ.get('GXB3_OWNER_UID', 'GXB3-00000001'), MONTHANH_UID)


def roster(uid):
    return tuple(t for t in s4_exclusive._source_goddesses()
                 if t != SONIA or sonia_allowed(uid))


def check_scope(state):
    if state.get('server_id') != WORLD or not state.get('uid'):
        raise ValueError('Gói thử nghiệm chỉ dành cho hồ sơ S5')


def _recipe(tid, awake):
    from .engine import Engine, ASCENSION
    return ASCENSION.get(f'{tid}:{11+awake}') or Engine.awake_recipe(
        Engine.__new__(Engine), {'table_id':tid, 'awake':awake})


def _material(needed, group, allowed):
    rows = goddess_gifts.PARTNERS
    if needed == 7999 and group == 8:
        return next((t, 0) for t in allowed if int(rows[str(t)]['group']) == 7)
    if needed % 1000 != 999:
        if str(needed) not in rows or (needed == SONIA and SONIA not in allowed):
            raise ValueError('Nguyên liệu nữ thần không hợp lệ: '+str(needed))
        return (needed, 0)
    stars = needed // 10000
    faction = 0 if needed % 10000 == 9999 else (needed // 1000) % 10
    # Use existing canonical 10-star forms for 10+; native 5/6-star rows
    # for lower-star fodder. Never create fake IDs.
    for t in allowed:
        row = rows[str(t)]
        if stars >= 10 and (not faction or int(row['group']) == faction):
            return (t, stars-10)
    for g in goddess_gifts.GIRLS:
        t = int(g['id']); row = rows.get(str(t), {})
        base = int(row.get('max_star') or 0)
        if t == SONIA and SONIA not in allowed:
            continue
        if base not in (5,6) or not base <= stars <= (9 if base == 6 else 5):
            continue
        if faction and int(row.get('group') or 0) != faction:
            continue
        return (t, stars-base)
    raise ValueError('Không tìm thấy nguyên liệu gốc: '+str(needed))


def awakening_plan(uid, tid, awake):
    """One exact native 10->25 step, no direct awakening."""
    from .engine import Engine
    allowed = roster(uid)
    tid, awake = int(tid), int(awake)
    if tid not in allowed or not 0 <= awake < 15:
        raise ValueError('Nữ thần hoặc sao không thuộc gói S5')
    recipe = _recipe(tid, awake)
    if not recipe or recipe['kind'] != 'awake':
        raise ValueError('Không có công thức thức tỉnh')
    rows = goddess_gifts.PARTNERS
    if recipe.get('awake25'):
        fodder = next(t for t in allowed if Engine.awake25_valid_goddess(rows[str(t)]) and t != tid)
        mats = [(tid,0)]*recipe['copies'] + [(fodder,0)]*recipe['sacrifices']
    else:
        mats = [_material(int(n), int(recipe['group']), allowed) for n in recipe['material']]
    return {'girl_id':tid,'from_star':10+awake,'to_star':11+awake,
            'materials':mats,'cost':{str(k):local_config.scale_cost(v) for k,v in recipe.get('cost',{}).items()}}


def _add_partner(state, tid, awake=0):
    pid = int(state['next_partner_id'])
    state['next_partner_id'] = pid+1
    row = goddess_gifts.PARTNERS[str(tid)]
    p = {'partner_id':pid,'table_id':int(tid),'lv':1,'grade':int(row.get('max_grade') or 0),
         'awake':int(awake),'equips':[0]*7,'pos':0,'show_skin':1}
    state['partners'].append(p)
    return p


def grant_welcome(state, now):
    """Once per S5 character, save via authoritative profile transaction."""
    check_scope(state)
    from .engine import TABLES, TOWER
    if state.get('s5_welcome'):
        raise ValueError('Đã nhận quà S5')
    allowed = roster(state['uid'])
    items = state.setdefault('items',{})
    for k,v in RESOURCES.items():
        items[k] = int(items.get(k,0))+v
    # Character EXP juice is separate from account EXP.
    items['3'] = max(int(items.get('3',0)), int(TABLES['exp_player']['400']['all_exp']))
    last = next(int(k) for k,v in TABLES['stage'].items() if int(v['fort_id'])==50 and int(v['name'])==15)
    state['max_stage'] = max(int(state.get('max_stage',0)),last)
    state['current_stage'] = state['max_stage']
    state['cleared'] = sorted(set(state.get('cleared',[])) | {int(k) for k in TABLES['stage'] if int(k)<=last})
    state['hang'] = {'since':int(now),'drop_since':int(now)}
    state['tower'] = {'max_stage':len(TOWER),'tickets':10,'at':int(now)}
    prizes = []
    hosts = {}
    for tid in allowed:
        p = _add_partner(state,tid)
        hosts[str(tid)] = p['partner_id']
        prizes.append({'partner_id':p['partner_id'],'table_id':tid,'stars':10,'level':1,
                       'name':goddess_gifts.BY_ID[tid]['name']})
    items[SKIN_BOX] = SKIN_CHOICES
    state['s5_welcome'] = {'hosts':hosts,'kits':{},'skin_choices':SKIN_CHOICES}
    return {'goddesses':prizes,'wish_count':len(prizes),'skin_choices':SKIN_CHOICES}


def reward_hosts(state):
    """Current owned canonical S5 goddesses, independent of acquisition source."""
    check_scope(state)
    if not state.get('s5_welcome'):
        return []
    allowed=set(roster(state['uid']))
    return [p for p in state.get('partners',[]) if int(p['table_id']) in allowed]


def reward_host(state, partner_id):
    if type(partner_id) is not int:
        raise ValueError('Chọn nữ thần hợp lệ')
    host=next((p for p in reward_hosts(state) if p['partner_id']==partner_id),None)
    if host is None:
        raise ValueError('Nữ thần không thuộc danh sách quà S5 hoặc chưa nhận thư khởi đầu')
    return host


def grant_kit(state, partner_id):
    """One kit per goddess type per step, preserving native upgrade."""
    check_scope(state)
    welcome = state.get('s5_welcome') or {}
    host = reward_host(state, partner_id)
    plan = awakening_plan(state['uid'],host['table_id'],host.get('awake',0))
    key = f"{host['table_id']}:{plan['to_star']}"
    kits=welcome.setdefault('kits',{})
    if key in kits:
        raise ValueError('Đã nhận nguyên liệu cho mốc sao này')
    mats = [_add_partner(state,t,a)['partner_id'] for t,a in plan['materials']]
    for item,quantity in plan['cost'].items():
        state['items'][item] = max(int(state['items'].get(item,0)),quantity)
    kits[key] = True
    return {'material_ids':mats,'to_star':plan['to_star'],'cost':plan['cost']}


def gear_for_job(job):
    from . import equipment
    job=int(job)
    result=[]
    for slot in (1,2,3,4):
        candidates=[r for r in equipment.EQUIP.values()
                    if r['pos']==slot and int(r.get('job') or 0)==job]
        if not candidates:
            raise ValueError('Không tìm thấy trang bị đúng nghề')
        result.append(max(candidates,key=lambda r:(r['item_lv'],r.get('qlt',0),r['id']))['id'])
    return result


def grant_gear(state, partner_id):
    from . import equipment
    check_scope(state)
    welcome=state.get('s5_welcome') or {}
    host=reward_host(state,partner_id)
    received=welcome.setdefault('gear_claimed',{})
    key=str(host['table_id'])
    if key in received:
        raise ValueError('Nữ thần này đã nhận bộ trang bị')
    job=equipment.job_of(host)
    gear=gear_for_job(job)
    for item in gear:
        equipment.add(state,item,1)
    received[key]=True
    return {'partner_id':partner_id,'job':job,'gear':gear}


# Native equipment tables contain no character-specific soul restrictions.
# Select complete sets by combat role and the original Station antique advice.
_ADVANCED_ROLE = {
    1: (5100020, 3, 5750, (2,6,12,4), (3,4,8,14,6)),
    2: (5100021, 4, 5753, (1,7,8,3), (1,2,9,10,5)),
    3: (5100015, 5, 5756, (1,5,7,3), (1,2,7,9,5)),
    4: (5100015, 4, 5766, (1,5,8,3), (1,2,7,10,5)),
    5: (5100018, 9, 5768, (2,10,12,9), (3,4,11,12,14)),
}


def advanced_plan(host):
    from . import equipment, souls
    from .engine import EXSKILL, RESONATE
    tid=int(host['table_id'])
    row=equipment.PARTNERS[str(tid)]
    job=equipment.job_of(host)
    central,group,treasure,_,_=_ADVANCED_ROLE[job]
    if tid==SONIA: central,group,treasure=5100021,4,5766
    stones=[next(r['id'] for r in souls.E2.values()
                 if r['group']==group and r['pos']==slot and r['star']==6)
            for slot in range(2,6)]
    antique=_recommended_antique(tid,job)
    return {'souls':[central,*stones], 'treasure':treasure,'antique':antique,
            'elite_max':int(RESONATE['max'] if int(row['group'])==7 else EXSKILL['max']),
            'elite_display':10 if int(row['group'])==7 else int(EXSKILL['max']),
            'min_level':1}


def _recommended_antique(tid,job):
    from . import equipment
    rows=_station_girls()
    match=next((r for r in rows if tid in r.get('ids',[])),{})
    candidates=[r for r in equipment.EQUIP.values() if r['pos']==6]
    for advice in match.get('artifacts',[]):
        base=equipment.EQUIP.get(int(advice['id']),{})
        family=[r for r in candidates if r.get('name')==base.get('name')]
        if family:
            return max(family,key=lambda r:(r['item_lv'],r.get('qlt',0),r['id']))['id']
    # No Station recommendation for Sonia: role-appropriate maximum antique.
    return {1:67963,2:67903,3:67843,4:67423,5:67963}[job]


from functools import lru_cache

@lru_cache(maxsize=1)
def _station_girls():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    return tuple(json.loads((root/'web/assets/station/station.json').read_text())['girls'].values())


def grant_treasure_supplies(state):
    check_scope(state)
    welcome=state.get('s5_welcome') or {}
    if not welcome.get('treasure_supplies'):
        from . import equipment
        equipment.add(state,14,100_000)
        welcome['treasure_supplies']=True


def grant_advanced(state,partner_id):
    from . import equipment,souls
    check_scope(state)
    welcome=state.get('s5_welcome') or {}
    host=reward_host(state,partner_id)
    key=str(host['table_id'])
    claimed=welcome.setdefault('advanced_claimed',{})
    if key in claimed: raise ValueError('Nữ thần này đã nhận quà nâng cao')
    plan=advanced_plan(host)
    inventory=souls.store(state)['items']
    if len(inventory)+5>souls.LIMIT:
        raise ValueError('Túi Trang Bị Linh Hồn cần ít nhất 5 chỗ trống')
    job=equipment.job_of(host)
    _,_,_,stone_buffs,central_buffs=_ADVANCED_ROLE[job]
    ids=[]
    for tid in plan['souls']:
        sid=souls.new_soul(state,tid)
        rec=inventory[sid]
        if rec['kind']==1:
            rec['awake']=int(souls.E1[str(tid)]['max_star'])-1
            rec['lv']=souls.max_lv(rec)
            rec['attrs']=list(central_buffs[:souls.EX_NUM1[souls.star(rec)-1]])
        else:
            row=souls.E2[str(tid)]
            rec['awake']=int(row['max_qlt'])-1
            rec['lv']=souls.max_lv(rec);rec['exp']=0
            bases=[int(x) for x in str(row['base']).split('|')]
            rec['main']=next((b for b in stone_buffs if b in bases),bases[0])
            rec['attrs']=[f"{b}#{max(souls.EX_VALUE)}" for b in stone_buffs]
            rec['ex_attrs']=[]
        ids.append(int(sid))
    # Return previous soul pieces intact and equip all five new pieces.
    souls.release(state,host)
    for sid in ids:
        souls.action(state,{'action':'equip','partner_id':partner_id,'soul_id':sid})
    slots=equipment.equips_of(host)
    # Bound treasures cannot be returned to the bag. Retain an existing max-tier
    # treasure rather than destroy the user's already-maxed roll.
    if equipment.EQUIP.get(slots[4],{}).get('item_lv',0)<equipment.EQUIP[plan['treasure']]['item_lv']:
        slots[4]=plan['treasure']
        host.pop('tmp_treasure',None)
    if slots[5]:equipment.add(state,slots[5],1)
    slots[5]=plan['antique']
    old=(list(host.get('ex_skills') or [])+[0]*4)[:4]
    host['ex_skills']=[max(int(v),plan['elite_max']) for v in old]
    welcome.setdefault("advanced_soul_ids",{})[key]=ids
    welcome.setdefault("advanced_recipient",{})[key]=partner_id
    welcome.setdefault("advanced_equipment_recipient",{})[key]=partner_id
    claimed[key]=True
    grant_treasure_supplies(state)
    return {'partner_id':partner_id,'souls':ids,'treasure':slots[4],
            'antique':slots[5],'elite':host['ex_skills']}


def advanced_recipient(welcome, key):
    return welcome.get('advanced_recipient',{}).get(key,welcome.get('hosts',{}).get(key))


def advanced_equipment_recipient(welcome, key):
    return welcome.get('advanced_equipment_recipient',{}).get(key,advanced_recipient(welcome,key))


def move_advanced_equipment(state, partner_id):
    """Move the existing two equipped gifts to another copy, never mint items."""
    from . import equipment
    check_scope(state)
    if type(partner_id) is not int: raise ValueError('Chọn nữ thần hợp lệ')
    welcome=state.get('s5_welcome') or {}
    dest=reward_host(state,partner_id)
    key=str(dest['table_id'])
    if not welcome.get('advanced_claimed',{}).get(key):
        raise ValueError('Chưa nhận quà nâng cao')
    source_id=advanced_equipment_recipient(welcome,key)
    if source_id==partner_id: raise ValueError('Nữ thần này đã nhận hai trang bị')
    source=next((p for p in state['partners'] if p['partner_id']==source_id and p['table_id']==dest['table_id']),None)
    if not source: raise ValueError('Không tìm thấy bản nữ thần đã nhận quà')
    src=equipment.equips_of(source); dst=equipment.equips_of(dest)
    if equipment.EQUIP.get(src[4],{}).get('item_lv',0)!=max(equipment.TIERS) or not src[5]:
        raise ValueError('Bản nữ thần đã nhận cần đang mặc Bảo Vật tối đa và Cổ Vật')
    if equipment.EQUIP.get(dst[4],{}).get('item_lv',0)>equipment.EQUIP[src[4]]['item_lv']:
        raise ValueError('Bảo Vật hiện tại đã tốt hơn')
    src[4:6],dst[4:6]=dst[4:6],src[4:6]
    # A pending attribute roll belongs to its original treasure.
    a=source.pop('tmp_treasure',None);b=dest.pop('tmp_treasure',None)
    if a:dest['tmp_treasure']=a
    if b:source['tmp_treasure']=b
    welcome.setdefault('advanced_equipment_recipient',{})[key]=partner_id
    grant_treasure_supplies(state)
    return {'partner_id':partner_id,'source_partner_id':source_id,'treasure':dst[4],'antique':dst[5]}


def quick_souls(state, host):
    from . import souls
    check_scope(state)
    pid=int(host['partner_id'])
    welcome=state.get('s5_welcome') or {}
    key=str(host['table_id'])
    if advanced_recipient(welcome,key)!=pid or not welcome.get('advanced_claimed',{}).get(key):
        raise ValueError('Hãy nhận Quà Nâng Cao cho nữ thần này trước.')
    saved=welcome.setdefault('advanced_soul_ids',{})
    preferred=saved.get(key,[])
    reserved={int(sid) for k,ids in saved.items() if k!=key for sid in ids}
    items=souls.store(state)['items']
    plan=advanced_plan(host)['souls']
    chosen=[]
    for i,tid in enumerate(plan):
        candidates=[(int(sid),r) for sid,r in items.items()
                    if int(r['table_id'])==tid and int(r.get('owner') or 0) in (0,pid)
                    and int(sid) not in reserved and souls.star(r)==6 and r['lv']==souls.max_lv(r)]
        if not candidates:
            raise ValueError('Chưa đủ bộ Linh Hồn đúng nữ thần trong túi. Hãy tháo món đang dùng ở nữ thần khác nếu cần.')
        want=preferred[i] if i<len(preferred) else 0
        sid,_=max(candidates,key=lambda pair:(pair[0]==want,int(pair[1].get('owner') or 0)==pid,-pair[0]))
        chosen.append(sid)
    for sid in chosen:
        souls.action(state,{'action':'equip','partner_id':pid,'soul_id':sid})
    saved[key]=chosen
    return {'equipped':chosen}


def allow_skin_gift(sender_server,recipient_server):
    a,b=str(sender_server or '').upper(),str(recipient_server or '').upper()
    if 'S5' in (a,b) and a!=b:
        raise ValueError('GiftSkin S5 chỉ tặng giữa các nhân vật cùng S5')


def skin_catalog(uid):
    # Include lower-star-only wearable skins too (the 25-star roster is
    # not the complete original wearable skin catalog).
    return tuple(sorted(sid for sid,row in skins.SKINS.items()
                        if row.get('model') and row.get('partners')
                        and (sonia_allowed(uid) or SONIA not in row['partners'])))


def choose_skins(state, ids):
    check_scope(state)
    welcome=state.get('s5_welcome') or {}
    left=min(int(welcome.get('skin_choices',0)),int(state.get('items',{}).get(SKIN_BOX,0)))
    if not isinstance(ids,list) or not ids or any(type(x) is not int for x in ids):
        raise ValueError('Chọn trang phục hợp lệ')
    choices=set(ids)
    allowed=set(skin_catalog(state['uid']))
    have=skins.collected(state)
    if len(choices)!=len(ids) or len(choices)>left or not choices<=allowed or choices&have:
        raise ValueError('Trang phục trùng, không hợp lệ hoặc vượt số lượt chọn')
    state['skins']['collected']=sorted(have|choices)
    welcome['skin_choices']=left-len(choices)
    state['items'][SKIN_BOX]=welcome['skin_choices']
    return {'skin_ids':sorted(choices),'remaining':welcome['skin_choices']}

MAIL_MARKER = '__s5_welcome__'


def owner_uid():
    return os.environ.get('GXB3_OWNER_UID','GXB3-00000001').strip()


def early_mail_id(uid):
    return 'S5-SSVIP-'+hashlib.sha256(str(uid).encode()).hexdigest()[:24].upper()


def verified_owner(uid):
    if not owner_uid() or str(uid)!=owner_uid():
        return False
    from . import auth
    email=os.environ.get('GXB3_OWNER_EMAIL','trieuquangholuxury@gmail.com').strip().casefold()
    if not email:return False
    db=auth._db()
    try:
        row=db.execute("SELECT email,status FROM accounts WHERE uid=?",(str(uid),)).fetchone()
        return bool(row and row['status']=='active' and str(row['email'] or '').strip().casefold()==email)
    finally:db.close()


def early_access(uid):
    if not verified_owner(uid):return False
    from . import live_service
    db=live_service._db()
    try:
        row=db.execute("SELECT attachments FROM mail WHERE id=? AND uid=? AND server_id<>'S5' AND status='claimed' AND operator=?",
                       (early_mail_id(uid),str(uid),EARLY_OPERATOR)).fetchone()
        return bool(row and json.loads(row['attachments'])=={EARLY_CARD:1})
    finally:db.close()


def svip_mail_id(uid):
    return 'S5-SVIP-'+hashlib.sha256(str(uid).encode()).hexdigest()[:24].upper()


def verified_svip(uid):
    if str(uid)!=MONTHANH_UID:return False
    from . import auth
    db=auth._db()
    try:
        row=db.execute("SELECT username,status FROM accounts WHERE uid=?",(str(uid),)).fetchone()
        return bool(row and row['status']=='active' and str(row['username']).casefold()=='monthanh')
    finally:db.close()


def svip_access(now,uid):
    if float(now)>=SVIP_END or not verified_svip(uid):return False
    from . import live_service
    db=live_service._db()
    try:
        row=db.execute("SELECT attachments FROM mail WHERE id=? AND uid=? AND server_id<>'S5' AND status='claimed' AND operator=?",
                       (svip_mail_id(uid),str(uid),SVIP_OPERATOR)).fetchone()
        return bool(row and json.loads(row['attachments'])=={SVIP_CARD:1})
    finally:db.close()


def issue_svip_card(uid):
    if not verified_svip(uid):raise ValueError('Vé chỉ dành cho tài khoản monthanh')
    if time.time()>=SVIP_END:raise ValueError('Vé đã hết hạn')
    from . import live_service
    db=live_service._db()
    try:
        db.execute('BEGIN IMMEDIATE')
        player=db.execute("SELECT server_id,character_name FROM players WHERE uid=? AND status='active' AND server_id IN ('S1','S2','S3') ORDER BY CASE WHEN server_id='S1' THEN 0 ELSE 1 END,server_id LIMIT 1",(str(uid),)).fetchone()
        if not player:raise ValueError('Không tìm thấy nhân vật nhận vé')
        mid=svip_mail_id(uid)
        cur=db.execute("""INSERT INTO mail(id,uid,server_id,character_name,title,body,attachments,status,created_at,operator)
            VALUES(?,?,?,?,?,?,?,'pending',?,?) ON CONFLICT(id) DO NOTHING""",
            (mid,str(uid),player['server_id'],player['character_name'],SVIP_NAME,
             'Vé riêng cho monthanh. Nhận thư để vào S5 ngoài lịch công khai đến 06:00 ngày 28/11/2026 (giờ Việt Nam). Không chuyển nhượng. Hết hạn trở về lịch S5 bình thường.',
             json.dumps({SVIP_CARD:1}),int(time.time()),SVIP_OPERATOR))
        if cur.rowcount:live_service._audit(db,'s5.svip_card.issue',mid,{'uid':str(uid),'server_id':player['server_id'],'expires_at':SVIP_END},SVIP_OPERATOR)
        row=db.execute("SELECT server_id,status FROM mail WHERE id=? AND uid=? AND operator=?",(mid,str(uid),SVIP_OPERATOR)).fetchone()
        if not row:raise ValueError('Bản ghi vé không hợp lệ')
        db.commit()
        return {'server_id':row['server_id'],'status':row['status'],'issued':bool(cur.rowcount)}
    except Exception:
        db.rollback();raise
    finally:db.close()


def access_cycle(now,uid=None):
    info=schedule(now)
    early=early_access(uid)
    timed=svip_access(now,uid)
    return {**info,'early_access':early,'svip_access':timed,'svip_end':SVIP_END if timed else None,'access_allowed':early or timed or info['phase']=='open'}


def ensure_open(server_id, now=None, *, uid=None):
    if str(server_id).upper() == WORLD:
        info = access_cycle(time.time() if now is None else now,uid)
        if not info['access_allowed']:
            raise ValueError('S5 đang đóng. Mở thứ Hai và thứ Bảy, 06:00–09:00 và 20:00–23:00 (giờ Việt Nam).')


def issue_early_card(uid):
    """Issue exactly one owner-bound card to an existing active normal character."""
    if not verified_owner(uid):raise ValueError('Chỉ SUPER GM chính thức được nhận thẻ')
    from . import live_service
    db=live_service._db()
    try:
        db.execute('BEGIN IMMEDIATE')
        player=db.execute("SELECT server_id,character_name FROM players WHERE uid=? AND status='active' AND server_id IN ('S1','S2','S3') ORDER BY CASE WHEN server_id='S1' THEN 0 ELSE 1 END,server_id LIMIT 1",(str(uid),)).fetchone()
        if not player:raise ValueError('Không tìm thấy nhân vật quản trị đang hoạt động')
        mid=early_mail_id(uid)
        cur=db.execute("""INSERT INTO mail(id,uid,server_id,character_name,title,body,attachments,status,created_at,operator)
            VALUES(?,?,?,?,?,?,?,'pending',?,?) ON CONFLICT(id) DO NOTHING""",
            (mid,str(uid),player['server_id'],player['character_name'],EARLY_NAME,
             'Thẻ dành riêng cho SUPER GM. Nhận đính kèm để mở quyền vào S5 ngoài lịch công khai. Không tiêu hao, không chuyển nhượng. Các giới hạn liên server vẫn giữ nguyên.',
             json.dumps({EARLY_CARD:1}),int(time.time()),EARLY_OPERATOR))
        if cur.rowcount:live_service._audit(db,'s5.early_card.issue',mid,{'uid':str(uid),'server_id':player['server_id']},EARLY_OPERATOR)
        row=db.execute("SELECT server_id,status FROM mail WHERE id=? AND uid=? AND operator=?",(mid,str(uid),EARLY_OPERATOR)).fetchone()
        if not row:raise ValueError('Bản ghi thẻ không hợp lệ')
        db.commit()
        return {'server_id':row['server_id'],'status':row['status'],'issued':bool(cur.rowcount)}
    except Exception:
        db.rollback();raise
    finally:db.close()


def ensure_welcome(uid, server_id, name):
    if server_id != WORLD:
        return
    from . import live_service
    mid = 'S5-WELCOME-' + hashlib.sha256(str(uid).encode()).hexdigest()[:24]
    db = live_service._db()
    try:
        db.execute("""INSERT INTO mail(id,uid,server_id,character_name,title,body,attachments,status,created_at,operator)
            VALUES(?,?,?,?,?,?,?,'pending',?,'S5-TEST') ON CONFLICT(id) DO NOTHING""",
            (mid,uid,WORLD,name,'Thiên Hư Không • Quà thử đội hình',
             'Nhận toàn bộ nữ thần 10★ cấp 1, tài nguyên, tiến trình tối đa và 10 lượt chọn trang phục. Tự thức tỉnh lên 25★.',
             json.dumps({MAIL_MARKER:1}),int(time.time())))
        db.commit()
    finally:
        db.close()


def restrict_route(path):
    # World-local features retain their usual permissions. Cross PvP and
    # S5-boundary skin transfers are checked at their own authoritative routes.
    return False


def enforce_roster(state):
    if state.get('server_id') == WORLD and not sonia_allowed(state.get('uid')):
        if any(int(p.get('table_id',0)) == SONIA for p in state.get('partners',[])):
            raise ValueError('Lyr Sonia chỉ dành cho tài khoản được cấp quyền tại S5')
