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


def grant_kit(state, partner_id):
    """One kit per original welcome host per step, preserving native upgrade."""
    check_scope(state)
    welcome = state.get('s5_welcome') or {}
    host = next((p for p in state.get('partners',[]) if p['partner_id']==int(partner_id)),None)
    if not host or welcome.get('hosts',{}).get(str(host['table_id'])) != host['partner_id']:
        raise ValueError('Chỉ cấp nguyên liệu cho nữ thần quà S5')
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
    if type(partner_id) is not int:
        raise ValueError('Chọn nữ thần hợp lệ')
    host=next((p for p in state['partners'] if p['partner_id']==partner_id),None)
    if not host or welcome.get('hosts',{}).get(str(host['table_id']))!=partner_id:
        raise ValueError('Chỉ cấp trang bị cho nữ thần quà S5')
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


def access_cycle(now,uid=None):
    info=schedule(now)
    early=early_access(uid)
    return {**info,'early_access':early,'access_allowed':early or info['phase']=='open'}


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
