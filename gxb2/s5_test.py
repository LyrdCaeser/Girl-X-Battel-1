"""S5 test-world reward core. Not registered as a live world until isolation QA.
All callers must supply an authenticated, transaction-locked S5 profile.
No HTTP endpoints, SQL mutations, or automatic production grants in this module.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
from . import goddess_gifts, s4_exclusive, skins, local_config

WORLD = 'S5'
NAME = 'S5 • Thiên Hư Không'
TZ = ZoneInfo('Asia/Ho_Chi_Minh')
DAYS = (0, 5)  # Monday, Saturday
WINDOWS = ((6, 9), (20, 23))
SONIA = 758001
MONTHANH_UID = 'GB3-854365013'
RESOURCES = {
    '1': 1_000_000_000, '9': 1_000_000_000,
    '10': 10_000_000, '417': 10_000_000, '173': 10_000_000,
    '44': 500_000, '198': 10_000_000, '199': 10_000_000,
    '359': 5_000_000, '360': 5_000_000, '26': 1_000_000, '27': 1_000_000,
}
SKIN_CHOICES = 10


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


def skin_catalog(uid):
    # Include lower-star-only wearable skins too (the 25-star roster is
    # not the complete original wearable skin catalog).
    return tuple(sorted(sid for sid,row in skins.SKINS.items()
                        if row.get('model') and row.get('partners')
                        and (sonia_allowed(uid) or SONIA not in row['partners'])))


def choose_skins(state, ids):
    check_scope(state)
    welcome=state.get('s5_welcome') or {}
    left=int(welcome.get('skin_choices',0))
    if not isinstance(ids,list) or not ids or any(type(x) is not int for x in ids):
        raise ValueError('Chọn trang phục hợp lệ')
    choices=set(ids)
    allowed=set(skin_catalog(state['uid']))
    have=skins.collected(state)
    if len(choices)!=len(ids) or len(choices)>left or not choices<=allowed or choices&have:
        raise ValueError('Trang phục trùng, không hợp lệ hoặc vượt số lượt chọn')
    state['skins']['collected']=sorted(have|choices)
    welcome['skin_choices']=left-len(choices)
    return {'skin_ids':sorted(choices),'remaining':welcome['skin_choices']}
