"""Lyr Sonia ticket banner with stable odds and a persistent pity counter.

Each ticket is one independent draw. Non-featured results come from the
balanced Advanced Capsule pool; x5/x10 are convenience buttons, not bundles of
guaranteed native 10-star copies.
"""
from __future__ import annotations

import secrets

PARTNER_ID = 758001
TICKET_ID = 940060
SUMMON_COUNTS = {27: 1, 28: 5, 29: 10}
SUMMONS = tuple(SUMMON_COUNTS)
RATE_TOTAL = 10_000
FEATURED_WEIGHT = 50  # 0.50% per regular draw; always under 1.50%.
FIRST_GUARANTEE = 120
REPEAT_GUARANTEE = 150
GUARANTEE_HIT_PERCENT = 95


PARTNER = {
    'id': PARTNER_ID, 'name': 'Lyr Sonia', 'name2': 'Lyr Sonia', 'ver': 1,
    'group': 8, 'job': 2, 'max_grade': 6, 'max_star': 10, 'max_lv': 250,
    'base_atk': 1056.0, 'base_hp': 13680.0, 'base_arm': 60.0, 'base_spd': 312.0,
    'grow_atk': 105.6, 'grow_hp': 1368.0, 'grow_arm': 6.0, 'grow_spd': 2.0,
    'energy_base': 50, 'decompose': '7#25000|9#200000|10#25000',
    'grade_lv1': '', 'grade_exp1': '', 'grade_lv2': '', 'grade_exp2': '',
    'grade_lv3': '', 'grade_exp3': '', 'grade_lv4': '', 'grade_exp4': '',
    'grade_lv5': '', 'grade_exp5': '', 'grade_lv6': '', 'grade_exp6': '',
    'ex_skill': 0, 'star_origin': 0,
    'atk_id': 75800100, 'act_skill_id': 75800101,
    'pas_skill1_id': 75800102, 'pas_skill2_id': 75800103, 'pas_skill3_id': 75800104,
    'pas_tier1': 1, 'pas_tier2': 1, 'pas_tier3': 1,
    'host': '', 'material': '', 'avatar': 'partner_avatar_758001',
    'partner_model': 75800101, 'show_in_guide': 1, 'show_in_forge': 1,
    'show_in_guide_auditing': 0, 'show_in_forge_auditing': 0,
    # 11–15★: one native Sonia copy at each original awakening step.
    'awake_material': '|'.join([str(PARTNER_ID)] * 5),
    'awake_grow': (
        '116.69#1572.00#6#2|128.83#1800.88#6#2|142.23#2062.80#6#2|'
        '152.88#2261.18#6#2|164.32#2478.78#6#2|181.41#2840.24#6.12#2|'
        '200.27#3253.68#6.24#2|215.26#3566.88#6.36#2|231.36#3910.20#6.48#2|'
        '255.42#4479.12#6.60#2|281.98#5131.56#6.72#2|303.09#5625.36#6.84#2|'
        '325.78#6166.80#6.96#2|359.67#7065.12#7.08#2|397.06#8094.24#7.20#2'
    ),
    'awake_skill': '|'.join(['75800101#75800102#75800103#75800104'] * 5),
    'stone_material': '10#10000|10#10000|10#15000|10#15000|10#20000',
    'potential': ('100101#100102#100103|100201#100202#100203|100301#100302#100303|'
                  '100401#100402#100403|100501#100502#100503'),
    'n_id': '', 'star_10': '', 'skin_ids': '', 'wedding_skin_id': '',
    'wedding_skin_time': '', 'comment_id': 858001, 'show_ids': str(PARTNER_ID),
    'hero_list': str(PARTNER_ID), 'achievement_id': '',
    'partner_data_id': '583|584|585|586', 'gift_type1': '1000012|1000005',
    'gift_type2': '1000021|1000003', 'shenxue_table_id': 0, 'partner_shard': 0,
}


def register(tables):
    """Inject local records without rewriting the publisher's recovered tables."""
    tables['partner'][str(PARTNER_ID)] = dict(PARTNER)
    tables['names'][str(PARTNER_ID)] = PARTNER['name']  # real roster/battle label
    tables['summon']['10260'] = {
        'id':10260, 'summon_num':1,'cost':'940061#100',
        'dropbox_id':990061,'is_partner':1,'award':'','awaken_lv':0,
        'freetime_interval':0,
    }
    tables.setdefault('dropbox',{})['sonia_shard_10260'] = {
        'id':99006101,'dropbox_id':990061,'item':'758001#1',
        'weight':1,
    }
    for summon_id, count in SUMMON_COUNTS.items():
        tables['summon'][str(summon_id)] = {
            'id': summon_id, 'summon_num': count, 'cost': f'{TICKET_ID}#{count}',
            'dropbox_id': 0, 'is_partner': 1, 'award': '', 'awaken_lv': 0,
            'freetime_interval': 0,
        }


def progress(state):
    info=state.setdefault('chaos_summon', {'times':0,'total':0,'cycles':0})
    # Upgrade old state without erasing any already accumulated draws.
    # Previous saves only had times/total, and every completed pity/hit reset
    # times. Do not relabel an old already-triggered pity as someone's first.
    info.setdefault('cycles', int(int(info.get('total',0))>int(info.get('times',0))))
    return info


def snapshot(state):
    info=progress(state)
    pity=FIRST_GUARANTEE if int(info['cycles'])==0 else REPEAT_GUARANTEE
    return {
        'partner_id':PARTNER_ID,'ticket_id':TICKET_ID,
        'tickets':int(state.get('items',{}).get(str(TICKET_ID),0)),
        'counts':dict(SUMMON_COUNTS),'guaranteed':False,
        'rate':FEATURED_WEIGHT/RATE_TOTAL,
        'times':int(info['times']),'total':int(info['total']),
        'cycles':int(info['cycles']),
        'guarantee':pity,'first_guarantee':FIRST_GUARANTEE,
        'repeat_guarantee':REPEAT_GUARANTEE,
        'guaranteed_hit_percent':GUARANTEE_HIT_PERCENT,
        'guaranteed_miss_percent':100-GUARANTEE_HIT_PERCENT,
        'remaining':max(0,pity-int(info['times'])),
    }

def summon(state, summon_id, fallback_draw, rng=None,
           offbanner_draw=None, is_five_star=None):
    # All three drawing paths must be server-side; the client never supplies
    # an obtained girl or controls the RNG. Each draw is resolved separately.
    rng = rng or secrets.randbelow
    offbanner_draw=offbanner_draw or fallback_draw
    is_five_star=is_five_star or (lambda table_id:False)
    count = SUMMON_COUNTS[int(summon_id)]
    items = state.setdefault('items', {})
    have = int(items.get(str(TICKET_ID), 0))
    if have < count:
        raise ValueError('Không đủ Vé Lyr Sonia')
    items[str(TICKET_ID)] = have - count
    next_id = int(state.get('next_partner_id') or
                  (max((int(v['partner_id']) for v in state.get('partners', [])), default=0) + 1))
    new=[]
    for _ in range(count):
        info=progress(state)
        info['times']=int(info.get('times',0))+1
        info['total']=int(info.get('total',0))+1
        limit=FIRST_GUARANTEE if int(info['cycles'])==0 else REPEAT_GUARANTEE
        if info['times']>=limit:
            # Pity is a 5-star-or-higher result, not a deterministic Sonia.
            table_id=PARTNER_ID if rng(100)<GUARANTEE_HIT_PERCENT else int(offbanner_draw())
            if table_id!=PARTNER_ID and not is_five_star(table_id):
                raise ValueError('Nữ Thần bảo hiểm lệch phải từ 5★')
        elif rng(RATE_TOTAL)<FEATURED_WEIGHT:
            table_id=PARTNER_ID
        else:
            table_id=int(fallback_draw())
        # Both a featured 10★ Sonia and ANY unrelated 5★ reset pity.
        if table_id==PARTNER_ID or is_five_star(table_id):
            info['times']=0
            info['cycles']=int(info['cycles'])+1
        partner={'partner_id':next_id,'table_id':table_id,'lv':1,
                 'grade':0,'awake':0,'equips':[],'pos':0,'show_skin':1}
        state.setdefault('partners',[]).append(partner)
        new.append(partner)
        next_id+=1
    state['next_partner_id']=next_id
    return new
