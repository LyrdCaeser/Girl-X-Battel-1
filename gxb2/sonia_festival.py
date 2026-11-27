"""Three short Lyr Sonia festivals. All grants run in the player's transaction.

Dates are Vietnam-local and absolute, claims/spins are authenticated through
the game's existing serialized player state. No gifts are granted by merely
reading the event page; only verified actions can change resources.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ=ZoneInfo('Asia/Ho_Chi_Minh')
START=int(datetime(2026,11,22,tzinfo=TZ).timestamp())
ENDS={
    'stars':int((datetime(2026,11,22,tzinfo=TZ)+timedelta(days=15)).timestamp()),
    'shards':int((datetime(2026,11,22,tzinfo=TZ)+timedelta(days=7)).timestamp()),
    'missions':int((datetime(2026,11,22,tzinfo=TZ)+timedelta(days=30)).timestamp()),
}
TOWER_START=int(datetime(2026,11,27,11,40,tzinfo=TZ).timestamp())
TOWER_WEEK=7*86400
TOWER_IDS=('tower100','tower200','tower300')
SONIA=758001
SHARD='940061'
TICKET='940060'
GEMS='2'
SPIN_CAP=200
SPIN_COST={1:1200,5:5800}
DISCOUNT_MIN=1
DISCOUNT_MAX=100
# Exact probability / 10,000; no extra tickets or Diamonds from wheel.
WHEEL=(
    (300, {SHARD:2}, 'Mảnh Lyr Sonia ×2'),
    (20, {SHARD:5}, 'Mảnh Lyr Sonia ×5'),
    (2000, {'1':25000}, 'Vàng ×25.000'),
    (2000, {'9':10000}, 'EXP Nữ Thần ×10.000'),
    (2000, {'10':100}, 'Bụi Nâng Bậc ×100'),
    (3680, {'1':12000}, 'Vàng ×12.000'),
)
assert sum(p for p,_,_ in WHEEL)==10000
STAR_REWARDS={
    11:{'1':25000,'10':400},
    12:{'1':50000,'10':650},
    13:{'2':100,'10':800},
    14:{'1':100000,'10':1200},
    15:{'2':200,SHARD:5},
    16:{'2':250,SHARD:5},
    17:{'2':300,'10':1500},
    18:{'2':350,SHARD:10},
    19:{'2':400,'10':1800},
    20:{'2':450,SHARD:15},
    21:{'2':500,SHARD:10},
    22:{'2':600,SHARD:20},
    23:{'2':700,SHARD:10},
    24:{'2':850,SHARD:10},
    25:{'2':1000,SHARD:25},
}
# Each challenge is permanently claimable only before its own deadline.
# Progress is counted from real gameplay after the festival starts.
TASKS=(
    ('victory40','Thắng 40 trận Chiến Dịch','victory',40,7,5,'Khó'),
    ('victory120','Thắng 120 trận Chiến Dịch','victory',120,14,10,'Rất khó'),
    ('victory300','Thắng 300 trận Chiến Dịch','victory',300,30,15,'Cực khó'),
    ('advanced60','Triệu Hồi Cao Cấp 60 lần','advanced',60,14,10,'Rất khó'),
    ('advanced150','Triệu Hồi Cao Cấp 150 lần','advanced',150,30,15,'Cực khó'),
    ('tower100','Giai đoạn 1 · Vượt 100 tầng Thử Thách Học Viện','tower_clear',100,7,3,'Khó'),
    ('tower200','Giai đoạn 2 · Vượt 200 tầng Thử Thách Học Viện','tower_clear',200,14,5,'Rất khó'),
    ('tower300','Giai đoạn 3 · Vượt 300 tầng Thử Thách Học Viện','tower_clear',300,21,7,'Cực khó'),
    ('checkin20','Điểm Danh đủ 20 ngày','daily_checkin',20,30,20,'Cực khó'),
    ('awakening5','Thức Tỉnh Nữ Thần 5 lần','awaken',5,30,30,'Cực khó'),
)
# Each tier only grants its incremental difference. Maximum 350 paid tickets.
PAID_TIERS=(
    (30_000,10),
    (60_000,25),
    (120_000,50),
    (300_000,90),
    (600_000,150),
    (1_200_000,240),
    (1_800_000,300),
    (2_400_000,350),
)
assert sum(row[5] for row in TASKS)==120
assert PAID_TIERS[-1][1]==350



def active(now,which):
    return START<=int(now)<ENDS[which]


def _saved(state):
    saved=state.setdefault('sonia_festival',{})
    saved.setdefault('star_peak',0)
    saved.setdefault('star_claimed',[])
    saved.setdefault('star_reached',[])
    saved.setdefault('spins',0)
    saved.setdefault('clock_discount_pct',0)
    saved.setdefault('clock_discount_used',False)
    saved.setdefault('mission_claimed',[])
    saved.setdefault('paid_claimed',[])
    saved.setdefault('checked_days',[])
    saved.setdefault('progress',{})
    return saved


def record(state,kind,count=1,now=None):
    if now is None:
        import time
        now=time.time()
    if not active(now,'missions') or kind=='tower_clear' or kind not in {t[2] for t in TASKS}:
        return
    n=int(count)
    if n<=0:return
    saved=_saved(state)
    saved['progress'][kind]=int(saved['progress'].get(kind,0))+n


def record_tower_clear(state,floor,now):
    """Count unique newly cleared floors, not attempts, practice or GM skips."""
    if not TOWER_START<=int(now)<TOWER_START+3*TOWER_WEEK or not active(now,'missions'):
        return
    floor=int(floor)
    if floor<=0:return
    s=_saved(state)
    if floor<=int(s.get('tower_highest_recorded',0)):return
    s['tower_highest_recorded']=floor
    s['progress']['tower_clear']=int(s['progress'].get('tower_clear',0))+1


def mission_window(key,days):
    if key in TOWER_IDS:
        index=TOWER_IDS.index(key)
        return TOWER_START+index*TOWER_WEEK,min(ENDS['missions'],TOWER_START+(index+1)*TOWER_WEEK)
    return START,min(ENDS['missions'],START+days*86400)


def mission_snapshot(row,s,now):
    key,name,kind,target,days,tickets,difficulty=row
    start,end=mission_window(key,days)
    claimed=set(s.get('mission_claimed') or [])
    legacy=key in TOWER_IDS and 'arena30' in claimed
    received=key in claimed
    progress=int((s.get('progress') or {}).get(kind,0))
    return {'id':key,'name':name,'progress':progress,'target':target,
            'start':start,'end':end,'difficulty':difficulty,'tickets':tickets,
            'claimed':received,'legacy_covered':legacy,
            'can':active(now,'missions') and start<=now<end and progress>=target
                  and not received and not legacy}


def record_daily_checkin(state,now=None):
    """Count distinct real calendar check-ins, never claims or page refreshes."""
    if now is None:
        import time
        now=time.time()
    if not active(now,'missions'):
        return
    from . import clock
    day=clock.day(now,local=True)
    s=_saved(state)
    if day in s['checked_days']:
        return
    s['checked_days'].append(day)
    s['progress']['daily_checkin']=len(s['checked_days'])


def record_sonia_star(state,star,now=None,prior=10):
    if now is None:
        import time
        now=time.time()
    if not active(now,'stars'):
        return
    n=int(star)
    previous=int(prior)
    if n<=previous or n<11 or n>25:
        return
    saved=_saved(state)
    saved['star_peak']=max(int(saved.get('star_peak',0)),n)
    # Only the milestones actually crossed during this event can be claimed.
    # Someone awakening 24★→25★ does not receive every lower milestone.
    reached=set(saved['star_reached'])
    reached.update(star for star in STAR_REWARDS if previous<star<=n)
    saved['star_reached']=sorted(reached)


def first_discount(state):
    """Read the lifetime one-use clock coupon without modifying the profile.

    Existing participants who already have any recorded event spins cannot
    get a new first-spin discount. Snapshot never rolls a coupon.
    """
    saved=state.get('sonia_festival') or {}
    spins=int(saved.get('spins') or 0)
    used=bool(saved.get('clock_discount_used'))
    percent=int(saved.get('clock_discount_pct') or 0)
    if not 1<=percent<=100:percent=0
    eligible=spins==0 and not used
    available=eligible and percent>0
    return {
        'eligible':eligible,
        'needs_draw':eligible and percent==0,
        'percent':percent if available else 0,
        'used':used,
        'prices':{str(c): (max(0,(base*(100-percent)+99)//100) if available else base)
                  for c,base in SPIN_COST.items()},
    }


def snapshot(state,now=None,paid_vnd=0,paid_available=True):
    if now is None:
        import time
        now=time.time()
    now=int(now)
    s=state.get('sonia_festival') or {}
    claimed=set(s.get('star_claimed') or [])
    mission_claimed=set(s.get('mission_claimed') or [])
    paid_claimed=set(s.get('paid_claimed') or [])
    progress=s.get('progress') or {}
    paid_vnd=max(0,int(paid_vnd))
    highest=max((10+int(g.get('awake') or 0) for g in state.get('partners',[])
                 if int(g.get('table_id') or 0)==SONIA), default=0)
    return {
        'now':now,
        'art':'/assets/cards/partner_card_758001.png',
        'shard_id':int(SHARD),'ticket_id':int(TICKET),
        'highest_owned_star':highest,
        'highest_awakened_star':int(s.get('star_peak') or 0),
        'events':{key:{'start':START,'end':end,'active':active(now,key)}
                  for key,end in ENDS.items()},
        'stars':[
            {'star':star,'awards':awards,'claimed':star in claimed,
             'can':active(now,'stars') and star in s.get('star_reached',[]) and star not in claimed}
            for star,awards in STAR_REWARDS.items()],
        'wheel':{'spins':int(s.get('spins') or 0),'cap':SPIN_CAP,
                 'costs':dict(SPIN_COST),
                 'first_discount':first_discount(state),
                 'odds':[{'label':label,'chance':chance/100,'awards':item}
                          for chance,item,label in WHEEL],
                 'can':active(now,'shards')},
        'paid_total_vnd':paid_vnd,
        'paid_available':bool(paid_available),
        'free_ticket_cap':120,
        'paid_ticket_cap':350,
        'paid_missions':[
            {'id':index,'required_vnd':minimum,'total_tickets':total,
             'tickets':total-(PAID_TIERS[index-2][1] if index>1 else 0),
             'claimed':index in paid_claimed,
             'can':active(now,'missions') and paid_vnd>=minimum and index not in paid_claimed}
            for index,(minimum,total) in enumerate(PAID_TIERS,1)],
        'missions':[mission_snapshot(row,s,now) for row in TASKS],
    }


def _grant(state,awards):
    box=state.setdefault('items',{})
    for key,quantity in awards.items():
        q=int(quantity)
        if q<=0:raise ValueError('Phần thưởng không hợp lệ')
        box[key]=int(box.get(key,0))+q
    return {str(key):int(n) for key,n in awards.items()}


def action(state,request,now=None,rng=None,paid_vnd=0):
    if now is None:
        import time
        now=time.time()
    now=int(now)
    if not isinstance(request,dict):
        raise ValueError('Yêu cầu sự kiện không hợp lệ')
    verb=request.get('action')
    if verb=='sonia_visit':
        if now<START:
            raise ValueError('Hẹn gặp bạn tại lễ hội Lyr Sonia')
        _saved(state)
        return {'awards':{}}
    if verb=='sonia_star_claim':
        if not active(now,'stars'):
            raise ValueError('Ngày hội Thức Tỉnh đã khép lại')
        star=request.get('star')
        if type(star) is not int or star not in STAR_REWARDS:
            raise ValueError('Mốc quà không hợp lệ')
        s=_saved(state)
        if star in s['star_claimed']:
            raise ValueError('Bạn đã nhận phần quà này')
        if star not in s['star_reached']:
            raise ValueError('Hãy Thức Tỉnh Lyr Sonia đến mốc này trong mùa lễ hội để nhận quà')
        s['star_claimed'].append(star)
        return {'awards':_grant(state,STAR_REWARDS[star])}
    if verb=='sonia_discount_draw':
        if not active(now,'shards'):
            raise ValueError('Vòng Quay Kim Đồng Hồ đã khép lại')
        saved=state.get('sonia_festival') or {}
        offer=first_discount(state)
        if not offer['eligible']:
            raise ValueError('Ưu đãi đầu tiên đã được sử dụng')
        if offer['percent']:
            # Safe idempotency: a retry/refresh reveals the same coupon.
            return {'awards':{},'discount_percent':offer['percent']}
        generator=rng or secrets.randbelow
        draw=int(generator(100))
        if not 0<=draw<100:
            raise ValueError('Kim đồng hồ chưa quay đúng, hãy thử lại nhé')
        s=_saved(state)
        s['clock_discount_pct']=draw+1
        return {'awards':{},'discount_percent':draw+1}

    if verb=='sonia_spin':
        if not active(now,'shards'):
            raise ValueError('Vòng Quay Kim Đồng Hồ đã kết thúc')
        count=request.get('count')
        if type(count) is not int or count not in SPIN_COST:
            raise ValueError('Hãy chọn quay 1 lần hoặc 5 lần')
        discount=first_discount(state)
        if discount['needs_draw']:
            raise ValueError('Hãy nhận ưu đãi quay lần đầu trước nhé')
        saved=state.get('sonia_festival') or {}
        if int(saved.get('spins') or 0)+count>SPIN_CAP:
            raise ValueError('Bạn đã đạt số lượt quay của mùa này')
        price=discount['prices'][str(count)]
        items=state.setdefault('items',{})
        if int(items.get(GEMS,0))<price:
            raise ValueError('Không đủ Kim Cương để quay')
        # The first paid draw is the sole place the persistent discount can
        # be consumed. The engine commits this, the cost and awards together.
        s=_saved(state)
        items[GEMS]=int(items.get(GEMS,0))-price
        if discount['percent']:
            s['clock_discount_used']=True
        s['spins']=int(s['spins'])+count
        draws=[];awards={}
        rng=rng or secrets.randbelow
        for _ in range(count):
            hit=int(rng(10000))
            if not 0<=hit<10000:raise ValueError('Lượt quay không hợp lệ')
            for chance,reward,label in WHEEL:
                hit-=chance
                if hit<0:
                    draws.append({'name':label,'awards':reward})
                    for item,n in reward.items():awards[item]=awards.get(item,0)+n
                    break
        _grant(state,awards)
        return {'awards':awards,'draws':draws,'cost':price,'discount_percent':discount['percent']}
    if verb=='sonia_paid_claim':
        if not active(now,'missions'):
            raise ValueError('Hành trình Lyr Sonia đã khép lại')
        tier=request.get('tier')
        if type(tier) is not int or not 1<=tier<=len(PAID_TIERS):
            raise ValueError('Mốc quà nạp không hợp lệ')
        s=_saved(state)
        if tier in s['paid_claimed']:
            raise ValueError('Bạn đã nhận phần quà nạp này')
        minimum,total=PAID_TIERS[tier-1]
        if int(paid_vnd)<minimum:
            raise ValueError('Mốc quà nạp này chưa được mở')
        previous=PAID_TIERS[tier-2][1] if tier>1 else 0
        s['paid_claimed'].append(tier)
        return {'awards':_grant(state,{TICKET:total-previous})}
    if verb=='sonia_mission_claim':
        if not active(now,'missions'):
            raise ValueError('Hành trình Lyr Sonia đã khép lại')
        task=request.get('id')
        row=next((r for r in TASKS if r[0]==task),None)
        if not row:raise ValueError('Nhiệm vụ không hợp lệ')
        key,_,metric,target,days,tickets,_=row
        start,end=mission_window(key,days)
        if now<start:
            raise ValueError('Giai đoạn này chưa mở')
        if now>=end:
            raise ValueError('Nhiệm vụ đã hết hạn')
        s=_saved(state)
        if key in TOWER_IDS and 'arena30' in s['mission_claimed']:
            raise ValueError('Bạn đã nhận đủ 15 Vé từ nhiệm vụ Đấu Trường cũ')
        if key in s['mission_claimed']:
            raise ValueError('Phần thưởng đã được nhận')
        if int(s['progress'].get(metric,0))<target:
            raise ValueError('Nhiệm vụ chưa hoàn thành')
        s['mission_claimed'].append(key)
        return {'awards':_grant(state,{TICKET:tickets})}
    raise ValueError('Không tìm thấy hoạt động Lyr Sonia')
