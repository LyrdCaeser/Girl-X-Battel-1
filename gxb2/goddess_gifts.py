"""SUPER GM-only configurable Goddess gifts, materialized on mail claim.

Server validates every original character form, level, star, equipment and
stellar node. No client-supplied partner instance, arbitrary table ID, or fake
assets are ever accepted. A gifted partner is born under the redeemer's own
UID/world during the same transaction as claiming that giftcode's mail.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PARTNERS=json.loads((ROOT/'data/partner.json').read_text())
GRADUATE=json.loads((ROOT/'data/graduate.json').read_text())
ASCENSION=json.loads((ROOT/'data/ascension.json').read_text())
ASTRAL=json.loads((ROOT/'data/astral.json').read_text())
GIRLS=json.loads((ROOT/'web/assets/girls-catalog.json').read_text())
BY_ID={int(g['id']):g for g in GIRLS}
COMPOSE={int(r['source']):int(r['target']) for r in (*GRADUATE.values(),*(x for x in ASCENSION.values() if x.get('kind')=='compose'))}
GEAR=(1999,2999,3999,4999)
BONUS_LIMITS={'hp':1000000000,'atk':100000000,'arm':10000000,'spd':3000}


def _int(value,field,lo,hi):
    if isinstance(value,bool):raise ValueError('Giá trị '+field+' không hợp lệ')
    try: n=int(value)
    except (TypeError,ValueError):raise ValueError('Giá trị '+field+' phải là số nguyên') from None
    if str(value).strip()!=str(n) and not isinstance(value,int):raise ValueError('Giá trị '+field+' phải là số nguyên')
    if not lo<=n<=hi:raise ValueError(f'{field}: chỉ từ {lo} đến {hi}')
    return n


def resolve(girl_id:int,stars:int)->tuple[int,int]:
    """Resolve only documented source→5★→6★→10★ form changes."""
    g=BY_ID.get(int(girl_id))
    if not g:raise ValueError('Nữ Thần không thuộc danh sách gốc')
    row=PARTNERS.get(str(girl_id))
    if not row or not row.get('show_in_guide') or not 1<=int(row.get('group') or 0)<=7:
        raise ValueError('Nữ Thần không khả dụng trong game')
    base=int(row['max_star']);stars=int(stars)
    if stars<base or stars>25:raise ValueError('Sao thấp hơn hình thái gốc hoặc vượt 25★')
    if base<=3:
        from .local_promotion import BASE
        if int(girl_id) not in BASE or stars>10:raise ValueError('Không có công thức sao này trong dữ liệu gốc')
        return int(girl_id),stars-base
    tid=int(girl_id)
    if base==4 and stars>=5:
        tid=COMPOSE.get(tid,0)
        if not tid:raise ValueError('Không có hình thái 5★ gốc')
        base=5
    if base==5 and stars>=6:
        tid=COMPOSE.get(tid,0)
        if not tid:raise ValueError('Hình thái này không có công thức 6★ gốc')
        base=6
    if base==6 and stars>=10:
        source=int(str(PARTNERS[str(tid)].get('material') or '0').split('|')[0])
        candidate=int(PARTNERS.get(str(source),{}).get('star_10') or 0)
        target=PARTNERS.get(str(candidate),{})
        if int(target.get('max_star') or 0)!=10 or int(target.get('group') or 0)!=int(row['group']):
            raise ValueError('Không có hình thái 10★ tương ứng trong dữ liệu gốc')
        tid=candidate;base=10
    if base==6 and stars>9:raise ValueError('Không có hình thái 10★ gốc')
    if base<10 and stars>base+3:raise ValueError('Không có công thức nâng sao tương ứng')
    # 10★ original forms can awaken as far as the verified 25★ progression.
    return tid,stars-base


def _image(girl_id):
    from .gm_catalog import _girl_image
    return _girl_image(int(girl_id))


def catalog():
    result=[]
    for girl in GIRLS:
        tid=int(girl['id']);image=_image(tid)
        if not image:continue
        allowed=[]
        for star in range(max(1,int(girl['stars'])),26):
            try:resolve(tid,star);allowed.append(star)
            except ValueError:pass
        if not allowed:continue
        result.append({'id':tid,'name':girl['name'],'group':int(girl['group']),
                       'image':image,'stars':allowed,'base_star':int(girl['stars'])})
    return result


def validate(config:dict)->dict:
    if not isinstance(config,dict):raise ValueError('Chưa chọn cấu hình Nữ Thần')
    girl_id=_int(config.get('girl_id'),'Nữ Thần',1,9999999)
    stars=_int(config.get('stars'),'Số sao',1,25)
    tid,awake=resolve(girl_id,stars)
    level=_int(config.get('level',1),'Cấp Nữ Thần',1,666)
    stats=config.get('stats') or {}
    if not isinstance(stats,dict) or set(stats)-set(BONUS_LIMITS):
        raise ValueError('Chỉ số chỉ gồm HP, ATK, DEF và SPD')
    values={key:_int(stats.get(key,0),key,0,limit) for key,limit in BONUS_LIMITS.items()}
    core=config.get('max_stellar',False)
    red=config.get('max_red6',False)
    if type(core)is not bool or type(red)is not bool:
        raise ValueError('Trạng thái Lõi Tinh Tú hoặc đồ đỏ không hợp lệ')
    row=PARTNERS[str(tid)]
    # Reject impossible giftcodes BEFORE issuance, not after users redeem.
    # Use the exact same native level cap as player upgrades.
    from types import SimpleNamespace
    from .engine import Engine
    expected_cap=Engine.level_cap(SimpleNamespace(developer=False),
        {'table_id':tid,'awake':awake,'grade':int(row.get('max_grade') or 0)},real=True)
    if level>expected_cap:
        raise ValueError(f'Cấp {level} vượt giới hạn {expected_cap} của {stars}★')
    if core:
        lst=ASTRAL['lists'].get(str(row.get('star_origin') or ''))
        if stars<15 or not lst:raise ValueError('Lõi Tinh Tú chỉ mở tối đa cho hình thái từ 15★ có lõi gốc')
    if red:
        from .equipment import EQUIP
        if any(int(EQUIP[i]['star'])!=6 or int(EQUIP[i]['qlt'])!=6 or int(EQUIP[i]['pos'])!=j
               for j,i in enumerate(GEAR,1)):
            raise ValueError('Không tìm thấy đủ bộ đồ đỏ 6★ trong bảng gốc')
    return {'girl_id':girl_id,'table_id':tid,'stars':stars,'awake':awake,
            'level':level,'stats':values,'max_stellar':core,'max_red6':red,
            'image':_image(girl_id),'name':str(BY_ID[girl_id]['name'])}


def grant(state:dict, config:dict,level_cap)->dict:
    """Called only inside the exact UID/world mail-claim SQL transaction."""
    c=validate(config)
    row=PARTNERS[str(c['table_id'])]
    grade=int(row.get('max_grade') or 0)
    hero={'partner_id':int(state['next_partner_id']),'table_id':c['table_id'],
          'lv':c['level'],'grade':grade,'awake':c['awake'],
          'equips':[0]*7,'pos':0,'show_skin':1,'gm_bonus':c['stats']}
    cap=level_cap(hero,real=True)
    if hero['lv']>cap:
        raise ValueError('Cấp đã chọn vượt giới hạn gốc '+str(cap)+' của hình thái '+str(c['stars'])+'★')
    if c['max_red6']:
        hero['equips'][:4]=GEAR
    if c['max_stellar']:
        lst=ASTRAL['lists'][str(row['star_origin'])]
        hero['star_origin']=[int(end)-int(start) for start,end in zip(lst['start'],lst['end'])]
    state['next_partner_id']=int(state['next_partner_id'])+1
    state['partners'].append(hero)
    return {'partner_id':hero['partner_id'],'table_id':hero['table_id'],
            'stars':c['stars'],'level':hero['lv'],'name':c['name']}
