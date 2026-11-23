'use strict';
// Events hub (ActivityWindow.lua). Check-in follows windows/activity/CheckIn.lua + prefabs/windows/activity/check_in.prefab.
const EventsHub=(()=>{
 // ActivityWindow for xyd.EventType.LIMIT: tab_1 Exclusives (type2 1), tab_3 Monthly Events (type2 3). The unused middle
 // tab hosts the newbie list (EventType.NEWBIE, which had its own entry in the original client).
 const TABS=[['ex','left'],['new','mid'],['month','right']];
 const WORKING=new Set([196,37,189,1,116,13,16,20,309,140,134,331,292,64,338,329,330,150]); // + every id of ActKit (generic kit) once loaded
 const POINT={13:{bg:'summon_giftbag_bg01',text:'summon_giftbag_text01_en_en',desc:'Trong thời gian sự kiện, hãy Triệu Hồi Cao Cấp để tích điểm nhận thưởng!',go:'Triệu Hồi',route:'capsule'},16:{bg:'prophet_summon_giftbag_bg01',text:'prophet_summon_giftbag_text01_en_en',desc:"Mỗi Ấn đã dùng nhận 1 điểm. Có thể nhận đủ các mốc thưởng nhiều vòng trong sự kiện!",go:'Chiêu Mộ',route:'enroll'},20:{bg:'wishing_pool_giftbag_bg01',text:'wishing_pool_giftbag_text01_en_en',desc:'Mỗi lần quay Máy Quay nhận 1 điểm. Hãy tích điểm để nhận toàn bộ mốc thưởng!',go:'Máy Quay',route:'slots'}};      // activity ids with a local implementation
 const NAMES={'1':"Vàng",'2':"Kim Cương",'3':'EXP'};
 const VI_EVENT={
  'Events':'Sự Kiện','Calendar':'Lịch Sự Kiện','Resets':'Đặt lại','Open now':'Đang diễn ra','Coming next':'Sắp diễn ra',
  'Monthly Events':'Sự Kiện Tháng','Exclusives':'Độc Quyền','Novato':'Tân Thủ','Back':'Quay Lại',
  'Loading events…':'Đang tải sự kiện…','There are no events in this tab.':'Không có sự kiện trong mục này.',
  'Sự kiện chưa mở.':'Sự kiện đang tạm nghỉ.','Saved.':'Đã lưu.','Guardando…':'Đang lưu…',
  'Capsule':'Triệu Hồi','Enroll':'Chiêu Mộ','Slot Machine':'Máy Quay','Left':'Còn lại',
  'Completed':'Đã hoàn thành','Claimed':'Đã nhận','Day':'Ngày','Item':'Vật phẩm',
  'Check In':'Điểm Danh','Seven Day':'Đăng Nhập 7 Ngày','Seven-day':'Đăng Nhập 7 Ngày',
  'Summon Gift Pack':'Gói Quà Triệu Hồi','Prophet Summon Gift Pack':'Gói Quà Chiêu Mộ',
  'Wishing Pool Gift Pack':'Gói Quà Máy Quay','Daily Login':'Đăng Nhập Hằng Ngày',
  'Limited Event':'Sự Kiện Giới Hạn','Newbie Event':'Sự Kiện Tân Thủ',
  'Anniversary':'Kỷ Niệm','Birthday':'Sinh Nhật','Exchange':'Đổi Thưởng',
  'Mission':'Nhiệm Vụ','Shop':'Cửa Hàng','Gift Pack':'Gói Quà','Login':'Đăng Nhập',
  'Purchase':'Mua','Draw':'Quay','Ranking':'Xếp Hạng','Rewards':'Phần Thưởng',
  'Guardando…':'Đang lưu…','Received: ':'Đã nhận: ','Saved.':'Đã lưu.',
  'Sign In':'Điểm Danh','Resets':'Làm mới','Monthly':'Hằng Tháng',
  'Refresh':'Làm Mới','Collection':'Bộ Sưu Tập','Point':'Điểm','Points':'Điểm',
  'Gift':'Quà Tặng','Event':'Sự Kiện','Reward':'Phần Thưởng','Current':'Hiện Có'
 };
 const vi=text=>{const raw=String(text??'');const direct=VI_EVENT[raw];if(direct)return direct;if(window.GxbLocale){const t=GxbLocale.t(raw);if(t!==raw)return t;}return raw
  .replace(/\bEvents?\b/g,'Sự Kiện').replace(/\bMonthly\b/g,'Tháng').replace(/\bWeekly\b/g,'Tuần')
  .replace(/\bExclusive(s)?\b/g,'Độc Quyền').replace(/\bNewbie\b/g,'Tân Thủ')
  .replace(/\bCheck[ -]?in\b/gi,'Điểm Danh').replace(/\bLogin\b/g,'Đăng Nhập')
  .replace(/\bSummon\b/g,'Triệu Hồi').replace(/\bGift Pack\b/g,'Gói Quà')
  .replace(/\bMission(s)?\b/g,'Nhiệm Vụ').replace(/\bShop\b/g,'Cửa Hàng')
  .replace(/\bExchange\b/g,'Đổi Thưởng').replace(/\bRanking\b/g,'Xếp Hạng')
  .replace(/\bDay\s+(\d+)/g,'Ngày $1').replace(/\bClaimed\b/g,'Đã nhận').replace(/\bReward(s)?\b/g,'Phần Thưởng')
  .replace(/\bGet\s+(\d+)\s+point\(s\)/g,'Đạt $1 điểm').replace(/\bPurchased:\s*/g,'Đã mua: ')
  .replace(/\bLeft\b/g,'Còn lại').replace(/\bCompleted\b/g,'Đã hoàn thành');
 };
 let catalog=null,loading=null,tab='ex',selected=null,pinnedId=null,origin='home',pending=false,message='',visited=false;
 let publicGemPacks=null,publicGemPacksLoading=false,soniaView=null,soniaDraws=[],soniaMissionTab='free',soniaClockSpinning=false,soniaClockIndex=-1,soniaDiscountSpinning=false;
 function loadPublicGemPacks(){
   if(publicGemPacks!==null||publicGemPacksLoading)return;
   publicGemPacksLoading=true;
   api('/api/payment/packages').then(r=>{
     publicGemPacks=Array.isArray(r?.packages)?r.packages:[];
   }).catch(()=>{
     publicGemPacks=[];
   }).finally(()=>{
     publicGemPacksLoading=false;
     if(view==='events'&&[2,3,6,24,39,40,184].includes(Number(selected)))render();
   });
 }
 const A=name=>'/assets/events/'+name+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=vi(text);return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const hub=()=>state.event_hub;
 const fmt=n=>typeof number==='function'?number(n):String(n);
 function itemName(id){if(String(id)==='940060')return 'Vé Lyr Sonia';if(String(id)==='940061')return 'Mảnh Lyr Sonia';return NAMES[id]||catalog.item_names[id]||itemCatalog?.[id]?.name||'Phần thưởng';}
 function itemIcon(id){if(String(id)==='940060')return '/assets/factions/8.png';if(String(id)==='940061')return '/assets/item-icons/partner_avatar_758001.png';if(catalog.item_icons[id])return catalog.item_icons[id];if(typeof itemPicture==='function'&&itemCatalog?.[id]){const pic=itemPicture(itemCatalog[id]);if(pic)return pic;}const icon=itemCatalog?.[id]?.icon;if(icon&&itemIcons?.has(icon))return '/assets/item-icons/'+icon+'.png';if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';return null;}
 function pairs(text){return String(text||'').split('|').filter(s=>s.includes('#')).map(s=>s.split('#'));}
 function claimable(id){const h=hub();if(id===1)return h.checkin.grid.some(d=>d.can);if(id===116)return h.sevenday.days.some(d=>d.can);return false;}
 function inTab(a,t){if(t==='new')return a.type1===3;if(t==='month')return (a.type1===2||a.type1===7)&&a.type2===3;return (a.type1===2||a.type1===7)&&a.type2!==3;}
 function tabLabel(t){return t==='new'?'Tân Thủ':t==='month'?'Sự Kiện Tháng':'Độc Quyền';}
 // The original server opened a handful of limited events at a time. Locally: every working event, plus a
 // deterministic weekly rotation of ROTATION archived ones per tab (ISO week number as seed).
 const ROTATION=5;
 function week(){const d=new Date();const t=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()));const day=t.getUTCDay()||7;t.setUTCDate(t.getUTCDate()+4-day);const y=new Date(Date.UTC(t.getUTCFullYear(),0,1));return t.getUTCFullYear()*100+Math.ceil(((t-y)/864e5+1)/7);}
 function rotation(items){const arch=items.filter(a=>!WORKING.has(a.id)).sort((a,b)=>a.id-b.id);if(arch.length<=ROTATION)return arch;const seed=week();const out=[];for(let i=0;i<ROTATION;i++)out.push(arch[(seed*7919+i*Math.floor(arch.length/ROTATION))%arch.length]);return [...new Set(out)];}
 // Game calendar (gxb2/game_calendar.py): of the playable limited events only the ones scheduled for this week / month are
 // offered, with the time they have left; "Calendar" lists the countdowns and what opens next.
 const cal=()=>state.calendar_info;
 const slot=id=>cal()?.events.find(e=>e.id===id);
 const openNow=id=>!cal()||!cal().scheduled.includes(id)||!!slot(id);
 const leftText=at=>{const s=Math.max(0,at-Math.floor(Date.now()/1000));const d=Math.floor(s/86400),h=Math.floor(s%86400/3600),m=Math.floor(s%3600/60);return d?d+' ngày '+h+' giờ':h?h+' giờ '+m+' phút':m+' phút';};
 const CAL_VI={'Daily reset (Daily Tasks, free draws, Hearts)':'Làm mới hằng ngày · Nhiệm vụ, lượt miễn phí, Tim','Tuần reset (weekly tasks, stores, weekly events)':'Làm mới hằng tuần · Nhiệm vụ, cửa hàng, sự kiện','House Exams season ends':'Khảo Thí Học Viện kết thúc mùa','Fantasy Book season ends':'Sách Kỳ Ảo kết thúc mùa','Junior Varsity season ends':'Đấu Trường Học Viện kết thúc mùa','Tháng reset (Tháng Sự Kiện)':'Làm mới Sự Kiện Tháng'};
 function calendarWin(){const c=cal();if(!c||typeof GirlUI==='undefined')return;const {body}=GirlUI.win({title:'Lịch Sự Kiện',cls:'ev-cal'});const sec=(t,ic)=>{const h=el('h4','ev-cal-h');h.append(el('span','ev-cal-sec-icon',ic),el('span','',t));body.append(h);};const row=(a,b,kind='')=>{const r=el('div','ev-cal-row '+kind);r.append(el('span','ev-cal-name',CAL_VI[a]||a),el('b','ev-cal-time',b));body.append(r);};
  if(c.exclusive_s4){
   sec('S4 • Thời Không Sai Lệch · VIP 15','★');
   body.append(el('p','ev-cal-note','Toàn bộ sự kiện gốc đang mở trên S4. Mỗi ngày có 3 sự kiện tiêu điểm được xếp ngẫu nhiên theo lịch 30 ngày; sự kiện khác vẫn mở.'));
   sec('Lịch tiêu điểm 30 ngày','✦');
   for(const d of c.featured_30_days||[]){
    const date=new Date(d.start*1000).toLocaleDateString('vi-VN',{day:'2-digit',month:'2-digit',year:'numeric'});
    row(date,d.names.map(vi).join(' · '),d.start<=c.now&&d.end>c.now?'open':'future');
   }
  }
  const soniaCalendar=state.sonia_festival_info?.events;
  if(soniaCalendar){
   sec('Lễ Hội Lyr Sonia','✦');
   for(const [kind,label]of [['stars','Thức Tỉnh nhận quà'],['shards','Vòng Quay Kim Đồng Hồ'],['missions','Hành trình Vé Lyr Sonia']]){
    const info=soniaCalendar[kind];if(info)row(label,info.active?'Còn '+leftText(info.end):info.end<=Date.now()/1000?'Đã kết thúc':'Sắp diễn ra',info.active?'open':'future');
   }
  }
  sec('Lịch làm mới','↻');for(const r of c.resets)row(r.label,leftText(r.at),'reset');
  if(!c.exclusive_s4){
   sec('Đang diễn ra','●');for(const e of c.events)row((e.kind==='month'?'Sự Kiện Tháng · ':'Sự Kiện Tuần · ')+vi(e.title),'Còn '+leftText(e.end),'open');
   sec('Sắp diễn ra','◆');for(const e of c.next)row((e.kind==='month'?'Sự Kiện Tháng · ':'Sự Kiện Tuần · ')+vi(e.title),'Mở sau '+leftText(e.start),'next');
   body.append(el('p','ev-cal-note',"Tuần mới bắt đầu vào Thứ Hai, tháng mới bắt đầu vào ngày 1. Tiến độ sự kiện được giữ nguyên khi sự kiện tạm nghỉ."));
  }}
 function list(){const all=catalog.activities.filter(a=>inTab(a,tab)&&!(a.id===116&&hub().sevenday.done&&!cal()?.exclusive_s4));const rows=[...all]; /* Full event catalog. */if(pinnedId){const original=catalog.activities.find(a=>a.id===pinnedId);if(original&&!rows.some(a=>a.id===pinnedId))rows.unshift(original);}return rows.sort((a,b)=>(a.id===pinnedId?1:0)-(b.id===pinnedId?1:0)?(b.id===pinnedId?1:0)-(a.id===pinnedId?1:0):(WORKING.has(b.id)-WORKING.has(a.id))||(b.rank-a.rank)||(b.id-a.id));}
 function listAll(){return catalog.activities.filter(a=>inTab(a,tab)&&!(a.id===116&&hub().sevenday.done&&!cal()?.exclusive_s4)).sort((a,b)=>(WORKING.has(b.id)-WORKING.has(a.id))||(b.rank-a.rank)||(b.id-a.id));}

 function open(from){origin=from||'home';soniaView=null;message='';showView('events');if(!catalog&&!loading)loading=Promise.all([api('/assets/events/catalog.json'),typeof ActKit!=='undefined'?ActKit.load():null]).then(([c])=>{catalog=c;if(typeof ActKit!=='undefined')ActKit.ids().forEach(i=>WORKING.add(i));render();}).catch(e=>{message=e.message;loading=null;render();});if(!visited){visited=true;send({action:'visit'},true);}}
 async function send(request,quiet=false){
  if(pending)return;
  pending=true;
  if(!quiet){
    message=request.action==='sonia_spin'?'Kim đồng hồ đang xoay…':
      request.action==='sonia_discount_draw'?'Kim đồng hồ đang chọn ưu đãi cho bạn…':'Đang lưu…';
    render();
  }
  try{
    const r=await api('/api/events/action',request);
    if(request.action==='sonia_discount_draw'&&!quiet){
      // The free welcome dial spins once. Its result comes exclusively from
      // the server, and the pause is only for the original-style animation.
      await new Promise(resolve=>setTimeout(resolve,900));
    }
    state=r.state;
    const got=Object.entries(r.awards||{});
    if(request.action==='sonia_spin'){
      // The server chooses every prize. The clock merely points at the last
      // confirmed prize; it never makes or modifies a draw on the client.
      soniaDraws=Array.isArray(r.draws)?r.draws:[];
      const odds=state.sonia_festival_info?.wheel?.odds||[];
      soniaClockIndex=odds.findIndex(o=>o.label===soniaDraws[soniaDraws.length-1]?.name);
    }
    message=request.action==='sonia_discount_draw'?
      'Chúc mừng! Kim Đồng Hồ tặng bạn giảm '+fmt(r.discount_percent)+'% cho lần quay đầu tiên.':
      got.length?"Đã nhận: "+got.map(([k,n])=>fmt(n)+' × '+itemName(k)).join(', '):(quiet?'':"Đã lưu.");
    if(got.length&&!quiet&&typeof GirlUI!=='undefined')GirlUI.toast(message);
  }catch(e){message=e.message||'Chưa thể quay. Hãy thử lại nhé!';}
  finally{
    if(request.action==='sonia_spin')soniaClockSpinning=false;
    if(request.action==='sonia_discount_draw')soniaDiscountSpinning=false;
    pending=false;render();if(typeof window.render==='function')window.render();
  }
}

 function render(){
  const root=$('events-view');if(!root||view!=='events')return;root.replaceChildren();
  const top=el('header','ev-top');const back=el('button','ev-back');back.type='button';back.setAttribute('aria-label',"Quay Lại");back.append(img('/assets/ui/win_back_btn.png'));back.onclick=()=>showView(origin==='events'?'home':origin);
  const money=el('div','ev-money');for(const id of ['1','2']){const s=el('span');s.append(img('/assets/currency/icon_'+id+'_small.png'),el('b',undefined,fmt(state.items[id]||0)));money.append(s);}
  top.append(back,el('h1',undefined,"Sự Kiện"),money);root.append(top);
  if(!catalog||!hub()){root.append(el('p','ev-note',message||"Đang tải sự kiện…"));return;}
  const win=el('div','ev-window');root.append(win);const tabs=el('nav','ev-tabs');for(const [id,pos]of TABS){const b=el('button','ev-tab '+pos+(tab===id?' on':''),tabLabel(id));b.type='button';b.onclick=()=>{if(tab===id&&!soniaView)return;soniaView=null;tab=id;selected=null;pinnedId=null;message='';if(typeof GxbAudio!=='undefined')GxbAudio.sfx('ui_switch_page',.6);render();};if(catalog.activities.some(a=>inTab(a,id)&&claimable(a.id)))b.append(img(A('alert_icon'),'ev-tab-red'));tabs.append(b);}win.append(tabs);{const cb=el('button','ev-cal-btn','📅 Lịch');cb.type='button';cb.onclick=calendarWin;win.append(cb);}const panel=el('div','ev-panel');win.append(panel);
  if([2,3,6,24,39,40,184].includes(Number(pinnedId||selected))){
    const offers=el('nav','ev-native-pack-tabs');
    for(const [id,label] of [[2,'Gói Tháng'],[3,'Gói Tuần'],[6,'Thẻ Tháng'],[24,'Thẻ Tuần'],[184,'Nạp Kim Cương']]){
      const chip=el('button','ev-tab'+(id===selected?' on':''),label);
      chip.type='button';
      chip.onclick=()=>{pinnedId=id;selected=id;render();};
      offers.append(chip);
    }
    panel.append(offers);
  }
  // Three live Lyr Sonia events use the same original ActivityWindow card
  // strips and reward/mission boards as the other featured celebrations.
  const sf=state.sonia_festival_info;
  if(tab==='ex'&&sf){
    const menu=el('nav','ev-strip sf-strip');
    for(const [id,label] of [['stars','Lễ Hội Thức Tỉnh'],['shards','Vòng Quay Kim Đồng Hồ'],['missions','Chinh Phục Nhiệm Vụ']]){
      const open=sf.events[id];
      const button=el('button','ev-title'+(soniaView===id?' on':'')+(id==='shards'?' sf-clock-tab':''));
      button.type='button';button.title=label;
      const miniArt={
        stars:'/assets/girl-ui/potentiality_nametag_star_max.png',
        shards:'/assets/events/icon_activity_clock.png',
        missions:'/assets/factions/8.png'
      };
      button.append(img(A(soniaView===id?'activity_icon_1_middle':'activity_icon_0_middle'),'ev-title-bg'),
        img(miniArt[id],'ev-title-icon sf-event-art',label),
        el('span','ev-title-label',label));
      if(open?.active)button.append(el('small','ev-title-left',leftText(open.end)));
      button.onclick=()=>{
        soniaView=id;message='';soniaDraws=[];soniaClockIndex=-1;
        soniaClockSpinning=false;render();
        // New participants get one complimentary DISCOUNT draw automatically;
        // it does not count toward prize spins and never spends Diamonds.
        if(id==='shards'&&!pending&&state.sonia_festival_info?.wheel?.first_discount?.needs_draw){
          soniaDiscountSpinning=true;
          send({action:'sonia_discount_draw'});
        }
      };
      menu.append(button);
    }
    panel.append(menu);
    if(soniaView){
      const festivalBody=el('div','ev-body sf-body');
      panel.append(festivalBody);soniaFestival(festivalBody,soniaView,sf);
      const result=el('p','ev-status',message);result.setAttribute('role','status');panel.append(result);
      return;
    }
  }
  const items=list();if(!items.some(a=>a.id===selected))selected=items[0]?.id??null;
  const strip=el('div','ev-strip');for(const a of items){const b=el('button','ev-title'+(a.id===selected?' on':''));b.type='button';b.title=vi(a.title.replace(/\n/g,' '));b.append(img(A(a.id===selected?'activity_icon_1_middle':'activity_icon_0_middle'),'ev-title-bg'),img(A('icon_'+a.icon),'ev-title-icon'),el('span','ev-title-label',vi(a.title)));if(slot(a.id))b.append(el('small','ev-title-left',leftText(slot(a.id).end)));if(claimable(a.id))b.append(img(A('person_icon_red_point'),'ev-title-red'));b.onclick=()=>{soniaView=null;selected=a.id;message='';render();};strip.append(b);}panel.append(strip);
  requestAnimationFrame(()=>strip.querySelector('.on')?.scrollIntoView({block:'nearest',inline:'nearest'}));
  const body=el('div','ev-body');panel.append(body);
  const a=items.find(x=>x.id===selected);
  if(!a)body.append(el('p','ev-note',"Không có sự kiện trong mục này."));else if(a.id===1)checkIn(body);else if(a.id===116)sevenDay(body,a);else if(POINT[a.id])pointEvent(body,a);else if(a.id===64&&typeof Jackpot!=='undefined')Jackpot.render(body);else if(a.id===196&&typeof FireworkProject!=='undefined')FireworkProject.render(body);else if((a.id===37||a.id===189)&&typeof PuzzleEvents!=='undefined')PuzzleEvents.render(body,a.id);else if(a.id===338&&typeof BlindBox!=='undefined')BlindBox.render(body);else if(a.id===329&&typeof Pirate!=='undefined')Pirate.render(body);else if(a.id===330&&typeof Pirate!=='undefined')Pirate.vaults(body);else if(typeof ActKit!=='undefined'&&ActKit.has(a.id))ActKit.render(body,a);else if(a.id===309&&typeof SandHunt!=='undefined')SandHunt.render(body);else if(a.id===140&&typeof WishCapsule!=='undefined')WishCapsule.panel(body);else if(a.id===134&&typeof MagicCard!=='undefined')MagicCard.render(body);else if(a.id===331&&typeof MatchingPairs!=='undefined')MatchingPairs.render(body);else if(a.id===292&&typeof LostSpace!=='undefined')LostSpace.panel(body);else if(a.id===150&&typeof PumpkinPatch!=='undefined')PumpkinPatch.render(body);else archived(body,a);
  if(a?.id===184)gemOffers(body);
  const status=el('p','ev-status',message);status.setAttribute('role','status');panel.append(status);
 }

 // The 12-hour face is a visual celebration, not a uniform-odds wheel.
 // Prize probabilities are shown separately and come unchanged from Neon.
 function soniaClockFace(odds){
  const stage=el('section','sf-clock-stage');
  stage.append(el('h3','sf-clock-heading','✦ Vòng Quay Kim Đồng Hồ ✦'),
    el('p','sf-clock-kicker','Mỗi vòng kim xoay, một điều ước được gửi tới Sonia'));
  const dial=el('div','sf-clock-dial'+(soniaClockSpinning?' is-spinning':'')+
    (soniaClockIndex>=0&&!soniaClockSpinning?' is-landed':''));
  dial.setAttribute('role','img');
  dial.setAttribute('aria-label','Đồng hồ Lyr Sonia với sáu phần thưởng và kim đồng hồ');
  const marks=el('div','sf-clock-marks');
  for(let i=0;i<12;i++){
    const mark=el('i','sf-clock-mark'+(i%3===0?' major':''));
    mark.style.setProperty('--hour',i);
    marks.append(mark);
  }
  dial.append(marks);
  for(let i=0;i<odds.length;i++){
    const award=odds[i]?.awards||{};
    const id=Object.keys(award)[0];
    const item=el('div','sf-clock-prize'+(i===soniaClockIndex&&!soniaClockSpinning?' selected':''));
    item.style.setProperty('--prize-index',i);
    item.title=odds[i].label;
    item.append(img(eventPrizeImage(id),'sf-clock-prize-icon',odds[i].label));
    dial.append(item);
  }
  const hand=el('div','sf-clock-hand');
  const angle=soniaClockIndex>=0?soniaClockIndex*60:0;
  hand.style.setProperty('--clock-angle',angle+'deg');
  hand.append(el('span','sf-clock-pointer'),el('span','sf-clock-tail'));
  dial.append(hand);
  const center=el('div','sf-clock-center');
  center.append(img('/assets/item-icons/partner_avatar_758001.png','', 'Lyr Sonia'),
    el('b','','SONIA'));
  dial.append(center);
  const crown=el('div','sf-clock-crown');
  crown.append(img('/assets/events/icon_activity_clock.png','','Kim Đồng Hồ'));
  stage.append(dial,crown);
  return stage;
 }
 function eventPrizeImage(id){
  id=String(id);
  const fixed={'940061':'/assets/item-icons/partner_avatar_758001.png',
   '1':'/assets/currency/icon_1_small.png',
   '9':'/assets/item-icons/icon_9.png',
   '10':'/assets/item-icons/icon_10.png'};
  return fixed[id]||(typeof itemPicture==='function'&&itemCatalog?.[id]?
    itemPicture(itemCatalog[id]):catalog?.item_icons?.[id])||'/assets/item-icons/icon_10.png';
 }
 function soniaDiscountOffer(first){
  const box=el('section','sf-clock-welcome');
  const heading=el('div','sf-clock-welcome-title');
  heading.append(el('span','','✦ Đặc Quyền Lần Đầu ✦'),
    el('b','','Một vòng quay ưu đãi miễn phí'));
  box.append(heading);
  const dial=el('div','sf-sale-dial'+(soniaDiscountSpinning?' is-rolling':'')+
    (first.percent&&!soniaDiscountSpinning?' is-revealed':''));
  dial.setAttribute('role','img');
  dial.setAttribute('aria-label','Kim Đồng Hồ quay ngẫu nhiên để chọn mức giảm giá từ 1% đến 100%');
  for(let i=0;i<12;i++){
    const mark=el('i','sf-sale-mark');
    mark.style.setProperty('--sale-hour',i);
    dial.append(mark);
  }
  dial.append(el('span','sf-sale-needle','◆'));
  const center=el('div','sf-sale-value');
  center.append(el('span','',soniaDiscountSpinning?'✦':first.percent?fmt(first.percent)+'%':'?'),
    el('small','',soniaDiscountSpinning?'Đang chọn…':'GIẢM GIÁ'));
  dial.append(center);
  box.append(dial);
  if(first.percent&&!soniaDiscountSpinning){
    box.append(el('p','sf-sale-notice','Chúc mừng! Bạn được giảm '+fmt(first.percent)+
      '% cho một lần quay nhận quà đầu tiên. Ưu đãi sẽ tự áp dụng khi bạn chọn quay.'));
  }else{
    box.append(el('p','sf-sale-notice',soniaDiscountSpinning?
      'Đồng hồ đang xoay để tìm mức giảm giá may mắn của bạn…':
      'Chỉ một lần duy nhất! Kim đồng hồ sẽ chọn ngẫu nhiên mức giảm từ 1% đến 100%.'));
    if(!pending&&!soniaDiscountSpinning&&first.needs_draw){
      const retry=el('button','sf-btn sf-sale-retry','Quay Ưu Đãi Miễn Phí');
      retry.type='button';
      retry.onclick=()=>{
        if(pending)return;
        soniaDiscountSpinning=true;send({action:'sonia_discount_draw'});
      };
      box.append(retry);
    }
  }
  return box;
 }
 function soniaFestival(parent,kind,festival){
  const info=festival.events[kind];
  const title={stars:'Lễ Hội Thức Tỉnh',shards:'Vòng Quay Kim Đồng Hồ',missions:'Chinh Phục Nhiệm Vụ'}[kind];
  const section=el('div','sf-banner'+(kind==='shards'?' sf-clock-banner':''));
  section.append(img('/assets/cards/partner_card_758001.png','sf-hero','Lyr Sonia'));
  const text=el('div','sf-banner-copy');
  text.append(el('h2','',title),el('p','',kind==='stars'?'Thức Tỉnh Lyr Sonia · Rinh quà theo từng mốc sao':kind==='shards'?'Kim đồng hồ xoay · Vận may ghé thăm · Sưu tầm mảnh Sonia':'Vượt thử thách để nhận Vé Lyr Sonia'));
  text.append(el('b','sf-time',info.active?'Còn '+leftText(info.end):Date.now()/1000>=info.end?'Sự kiện đã khép lại':'Sắp mở cửa'));
  section.append(text);parent.append(section);
  const rows=el('div','pe-list sf-list'+(kind==='shards'?' sf-clock-reward-grid':''));
  const icon=(id,n)=>{id=String(id);const node=el('div','sf-reward');
    const kind={'940060':'Vé Sonia','940061':'Mảnh Sonia','10':'Hộp cơm','2':'Kim cương','1':'Vàng'};
    const path={'940060':'/assets/factions/8.png','940061':'/assets/item-icons/partner_avatar_758001.png',
      '10':'/assets/item-icons/icon_10.png','2':'/assets/currency/icon_2_small.png',
      '1':'/assets/currency/icon_1_small.png'};
    const item=itemCatalog?.[id];
    const image=img(path[id]||(item&&typeof itemPicture==='function'?itemPicture(item):'')||
      (catalog?.item_icons?.[id]||'/assets/item-icons/icon_10.png'),'sf-reward-img',kind[id]||itemName(id));
    node.title=(kind[id]||itemName(id))+' ×'+fmt(n);
    node.append(image,el('small','',('×'+fmt(n))));
    if(kind[id])node.append(el('span','sf-reward-name',kind[id]));
    return node;};
  if(kind!=='shards')parent.append(rows);
  if(kind==='stars'){
    parent.append(el('p','ev-note','Mỗi mốc Thức Tỉnh nhận quà một lần trong mùa. Ảnh Sonia trong phần thưởng là MẢNH, không phải Nữ Thần nguyên con; đủ 100 mảnh mới ghép được một Lyr Sonia.'));
    parent.append(el('p','sf-progress','Sonia cao nhất đang sở hữu: '+festival.highest_owned_star+'★ · Đã nâng trong mùa: '+festival.highest_awakened_star+'★'));
    for(const r of festival.stars){
      const row=el('div','pe-row sf-row');const left=el('div','sf-row-copy');
      left.append(el('b','',r.star+'★ · Quà Thức Tỉnh'),el('small','',r.claimed?'Đã nhận':r.can?'Có thể nhận':'Hãy nâng Sonia đến mốc này'));
      row.append(left);
      const rewards=el('div','sf-rewards');for(const [id,n]of Object.entries(r.awards))rewards.append(icon(id,n));row.append(rewards);
      const take=el('button','sf-btn',r.claimed?'Đã nhận':'Nhận quà');take.type='button';take.disabled=pending||!r.can;take.onclick=()=>send({action:'sonia_star_claim',star:r.star});row.append(take);rows.append(row);
    }
  }else if(kind==='shards'){
    const w=festival.wheel;
    const first=w.first_discount||{};
    if(first.eligible||soniaDiscountSpinning)parent.append(soniaDiscountOffer(first));
    parent.append(soniaClockFace(w.odds));
    const progress=el('div','sf-clock-progress');
    progress.append(
      el('span','','Lượt kim đã xoay '),el('b','',fmt(w.spins)+' / '+fmt(w.cap)),
      el('span','','Mảnh Sonia '),el('b','',fmt(state.items['940061']||0)+' / 100')
    );
    parent.append(progress);
    const actions=el('div','sf-spin-buttons sf-clock-spin-buttons');
    for(const count of [1,5]){
      const b=el('button','sf-btn sf-clock-spin-btn');
      b.type='button';
      const price=Number(first.prices?.[count]??w.costs[count]);
      b.append(el('strong','',count===1?'Quay 1 lượt':'Quay 5 lượt'),
        el('span','sf-clock-cost',price===0?'✧ Miễn phí':'✧ '+fmt(price)+' Kim Cương'));
      if(first.eligible&&first.percent&&!soniaDiscountSpinning){
        b.append(el('small','sf-clock-discount',
          'Giảm '+fmt(first.percent)+'% · Giá gốc '+fmt(w.costs[count])));
      }
      b.disabled=pending||!w.can||!!first.needs_draw||soniaDiscountSpinning||
        w.spins+count>w.cap||Number(state.items['2']||0)<price;
      b.onclick=()=>{
        if(pending)return;
        soniaDraws=[];soniaClockIndex=-1;soniaClockSpinning=true;
        send({action:'sonia_spin',count});
      };
      actions.append(b);
    }
    parent.append(actions);
    if(soniaDraws.length){
      const won=el('div','sf-won sf-clock-won');
      won.append(el('h3','','✦ Quà Kim Đồng Hồ vừa mang tới ✦'));
      const batch=el('div','sf-clock-result-list');
      for(const reward of soniaDraws){
        const id=Object.keys(reward.awards||{})[0];
        const prize=el('div','sf-clock-result');
        prize.append(img(eventPrizeImage(id),'',reward.name),el('span','',reward.name));
        batch.append(prize);
      }
      won.append(batch);parent.append(won);
    }
    parent.append(el('h3','sf-clock-subtitle','✦ Kho báu của Kim Đồng Hồ ✦'));
    for(const r of w.odds){
      const row=el('div','sf-clock-odds-card');
      const id=Object.keys(r.awards||{})[0];
      row.append(img(eventPrizeImage(id),'sf-clock-odds-icon',r.label),
       el('b','',r.label),el('strong','sf-clock-odds-number',r.chance.toLocaleString('vi-VN')+'%'));
      rows.append(row);
    }
    parent.append(rows);
    parent.append(el('p','sf-clock-footnote',
      'Kim đồng hồ minh họa các phần quà; cơ hội nhận từng quà được ghi rõ bên dưới. Mỗi lượt đều có quà. Đủ 100 mảnh có thể ghép một Lyr Sonia 10★.'));
  }else{
    parent.append(el('p','ev-note','Nhiệm vụ khó và cực khó · Chỉ tính chiến công trong mùa lễ hội. Hoàn thành và nhận quà trước giờ kết thúc từng nhiệm vụ.'));
    parent.append(el('p','sf-progress','120 Vé Lyr Sonia qua thử thách · Tối đa 350 Vé qua quà nạp đã duyệt trong 30 ngày.'));
    const tabs=el('nav','sf-mission-tabs');
    for(const [key,label] of [['free','Thử Thách · 120 Vé'],['paid','Quà Nạp · 350 Vé']]){
      const tabButton=el('button','ev-tab'+(soniaMissionTab===key?' on':''),label);
      tabButton.type='button';tabButton.onclick=()=>{soniaMissionTab=key;render();};tabs.append(tabButton);
    }
    parent.insertBefore(tabs,rows);
    if(soniaMissionTab==='paid'){
      parent.append(el('p','ev-note','Quà riêng dành cho người ủng hộ. Chỉ các gói Kim Cương có giá công khai, được QTV duyệt trong thời gian lễ hội mới được tính. Gói nạp chưa xác nhận không được cộng.'));
      parent.append(el('p','sf-progress',
        festival.paid_available===false?'Chưa xem được lịch sử nạp. Hãy mở lại sự kiện sau nhé.':
        'Đã nạp hợp lệ trong lễ hội: '+fmt(festival.paid_total_vnd||0)+' VNĐ'));
      for(const m of festival.paid_missions||[]){
        const row=el('div','pe-row sf-row');const left=el('div','sf-row-copy');
        left.append(el('b','','Tích lũy '+fmt(m.required_vnd)+' VNĐ'),
          el('small','',m.claimed?'Đã nhận quà':'Tổng nhận đến mốc này: '+m.total_tickets+' Vé Lyr Sonia'));
        row.append(left,icon('940060',m.tickets));
        const b=el('button','sf-btn',m.claimed?'Đã nhận':'Nhận vé');b.type='button';
        b.disabled=pending||festival.paid_available===false||!m.can;b.onclick=()=>send({action:'sonia_paid_claim',tier:m.id});
        row.append(b);rows.append(row);
      }
      parent.append(el('p','ev-note','Mỗi mốc quà chỉ nhận một lần. Tổng quà nạp tối đa 350 Vé, không cộng 350 Vé ở mỗi mốc.'));
      return;
    }
    for(const m of festival.missions){const row=el('div','pe-row sf-row');const left=el('div','sf-row-copy');
      left.append(el('b','',m.name),el('small','',m.difficulty+' · '+(m.claimed?'Đã nhận':festival.now>=m.end?'Đã hết hạn':'Còn '+leftText(m.end))));
      const bar=el('div','pe-bar');bar.style.backgroundImage=`url('${A('activity_bar_bg')}')`;
      const fill=el('i','sf-progress-fill');fill.style.width=Math.round(Math.min(1,m.progress/m.target)*100)+'%';
      bar.append(fill,el('span','',fmt(Math.min(m.progress,m.target))+'/'+fmt(m.target)));left.append(bar);row.append(left);
      row.append(icon('940060',m.tickets));
      const b=el('button','sf-btn',m.claimed?'Đã nhận':'Nhận vé');b.type='button';b.disabled=pending||!m.can;b.onclick=()=>send({action:'sonia_mission_claim',id:m.id});
      row.append(b);rows.append(row);
    }
  }
 }
 function rewardIcon(id,n,cls='ev-item'){const w=el('span',cls);const src=itemIcon(id);if(src)w.append(img(src,undefined,itemName(id)));else w.append(el('em',undefined,itemName(id)));w.append(el('b',undefined,fmt(n)));w.title=itemName(id)+' × '+fmt(n);return w;}

 function checkIn(parent){
  const h=hub(),t=catalog.text,st=el('div','ci-stage');parent.append(st);
  st.append(img(A('check_in_pop_up_background'),'ci-bg'),img(A('partner_picture_11001'),'ci-partner'));
  const sign=el('div','ci-sign');sign.append(img(A('check_in_pop_up_check_in_location')),el('span',undefined,t.CHECKIN_POPUP_TITLE));st.append(sign);
  const canAny=h.checkin.grid.some(d=>d.can);
  const talk=el('div','ci-talk');talk.append(img(A('check_in_pop_up_talk_bubble')),el('p',undefined,canAny?t.CHECKIN_POPUP_TEXT1:t.CHECKIN_POPUP_TEXT2));st.append(talk);
  const board=el('div','ci-board');board.append(img(A('check_in_pop_up_blackboard'),'ci-board-img'));st.append(board);
  for(let r=1;r<=3;r++)board.append(img(A('check_in_pop_up_line_'+r),'ci-line ci-line'+r));
  for(let r=0;r<3;r++){const row=el('div','ci-row ci-row'+(r+1));board.append(row);
   for(const d of h.checkin.grid.slice(r*5,r*5+5)){const [id,n]=pairs(d.award)[0];const cell=el('button','ci-cell'+(d.can?' can':'')+(d.got?' got':''));cell.type='button';
    const frame=d.can?'frame_can_get':d.got?'frame_has_gotten':'frame_'+Math.ceil(d.pos/5),num='num_'+d.pos+(d.can?'_1':d.got?'_2':'');
    cell.append(img(A('check_in_pop_up_'+frame),'ci-frame'),rewardIcon(id,n,'ci-icon'),img(A('check_in_pop_up_'+num),'ci-num'));
    if(d.got)cell.append(img(A('check_in_pop_up_item_mask'),'ci-mask'),img(A('check_in_pop_up_circle'),'ci-circle'));
    cell.title="Ngày "+d.day+': '+itemName(id)+' × '+fmt(n);cell.disabled=pending||!d.can;cell.onclick=()=>send({action:'checkin'});row.append(cell);}}
  parent.append(el('p','ev-note',"Ngày đăng nhập "+h.online_days+" · đã nhận: "+h.checkin.count+". Mỗi ngày đăng nhập mở một ô phần thưởng."));
 }

 function sevenDay(parent,a){
  const h=hub(),box=el('div','sd-stage');parent.append(box);
  box.append(img(A('activity_bg03'),'sd-bg'),el('h2','sd-title sd-title-vi','Đăng Nhập 7 Ngày'));
  const grid=el('div','sd-grid');box.append(grid);
  for(const d of h.sevenday.days){const c=el('button','sd-day'+(d.can?' can':'')+(d.got?' got':''));c.type='button';c.append(img(A('day_'+d.day+'_'+(d.got?2:1)),'sd-day-bg'));const rw=el('div','sd-rewards');for(const [id,n]of pairs(d.award))rw.append(rewardIcon(id,n));c.append(rw);c.disabled=pending||!d.can;c.onclick=()=>send({action:'sevenday'});grid.append(c);}
  parent.append(el('p','ev-note',(a.desc&&a.desc!=='-1'?a.desc+' · ':'')+"Mỗi ngày đăng nhập mở một mốc. Đã nhận "+h.sevenday.count+'/7.'));
 }

 // Point events (SummonGiftBag / ProphetSummonGiftBag / WishingPoolGiftBag): banner, loop counter, tiers.
 function left(info){const secs=Math.max(0,info.ends_at-(state.server_time||Date.now()/1000));return Math.floor(secs/86400)+' ngày '+Math.floor(secs%86400/3600)+' giờ';}
 function pointEvent(parent,a){const cfg=POINT[a.id],info=state.point_events_info?.[a.id];if(!info||info.open===false){parent.append(el('p','ev-note',"Sự kiện đang tạm nghỉ. Hãy xem Lịch Sự Kiện để biết lần mở tiếp theo."));return;}
  const ban=el('div','pe-banner');ban.style.backgroundImage=`url('${A(cfg.bg)}')`;ban.append(el('h2','pe-title pe-title-vi',({13:'Thưởng Điểm Triệu Hồi',16:'Thưởng Điểm Chiêu Mộ',20:'Thưởng Điểm Máy Quay'})[a.id]||vi(a.title)),el('p','pe-desc',a.id===20?'Mỗi lần quay Máy Quay nhận 1 điểm. Có thể hoàn thành '+info.times+' vòng thưởng trong sự kiện!':cfg.desc));
  const strip=el('div','pe-strip');strip.append(el('b','','Đã hoàn thành ('+info.rounds+'/'+info.times+')'),el('span','pe-left',left(info)),el('span','pe-left-label','Còn lại'));ban.append(strip);
  const go=el('button','pe-go',cfg.go);go.type='button';go.style.backgroundImage=`url('${A('house_icon_1')}')`;go.disabled=!cfg.route;go.title=cfg.route?'':"Máy Quay hiện chưa khả dụng";go.onclick=()=>{if(cfg.route==='capsule')showView('capsule');else if(cfg.route==='enroll'&&typeof Enroll!=='undefined')Enroll.open('events');else if(cfg.route==='slots'&&typeof Slots!=='undefined')Slots.open('events');};ban.append(go);parent.append(ban);
  const list=el('div','pe-list');for(const t of info.tiers){const row=el('div','pe-row');const l=el('div','pe-left-col');l.append(el('b','','Đạt '+t.point+' điểm'));const bar=el('div','pe-bar');bar.style.backgroundImage=`url('${A('activity_bar_bg')}')`;const fill=el('i');fill.style.width=Math.min(100,(t.got?t.point:info.point)/t.point*100)+'%';fill.style.backgroundImage=`url('${A('activity_bar_thumb')}')`;bar.append(fill,el('span','',(t.got?t.point:Math.min(info.point,t.point))+'/'+t.point));l.append(bar);row.append(l);
   const rw=el('div','pe-rewards');for(const [id,n]of pairs(t.awards)){const r=rewardIcon(id,n,'pe-item');if(t.got)r.append(img(A('icon_check'),'pe-check'));rw.append(r);}row.append(rw);list.append(row);}
  parent.append(list);parent.append(el('p','ev-note',"Phần thưởng được cộng trực tiếp vào Túi Đồ khi đạt từng mốc. Đặt lại hằng tuần vào 00:00 Thứ Hai."));}

 function archived(parent,a){
  const c=el('div','ev-archive ev-original-card');
  const art=img(A('icon_'+a.icon),'ev-archive-icon');
  c.append(art,el('h2',undefined,vi(a.title.replace(/\\n/g,' '))));
  if(a.desc&&a.desc!=='-1')c.append(el('p',undefined,vi(a.desc)));
  c.append(el('p','ev-note','Sự kiện đang tạm nghỉ. Hẹn gặp lại ở lần mở tiếp theo.'));
  parent.append(c);
 }

 function gemOffers(parent){
    const original=el('section','ev-original-gems');
    original.append(el('h3',undefined,'Các Gói Kim Cương'));
    if(publicGemPacks===null){
      original.append(el('p','ev-note','Đang tải các gói nạp đang mở…'));
      loadPublicGemPacks();
    }else{
      for(const p of publicGemPacks.filter(p=>/^GEMS_/.test(String(p.id)))){
        const offer=el('article','ev-gems-offer');
        offer.append(img('/assets/currency/icon_2_small.png','ev-item','Kim Cương'));
        const info=el('div','ev-gems-data');
        info.append(el('b',undefined,p.name));
        if(p.vip_exp)info.append(el('span',undefined,fmt(p.vip_exp)+' EXP VIP khi nhận thư nạp đã duyệt'));
        if(p.instant_gems)info.append(el('span',undefined,fmt(p.instant_gems)+' Kim Cương'));
        if(p.price_label)info.append(el('small',undefined,p.price_label));
        offer.append(info);
        const btn=el('button','ev-native-pay','Zalo · Đặt Gói');btn.type='button';
        btn.onclick=()=>window.GxbPayment?.open(p.id,p.name);
        offer.append(btn);original.append(offer);
      }
    }
    parent.append(original);
 }

 function openPoint(id,from){tab='ex';selected=id;pinnedId=id;soniaView=null;open(from);}
 function openOriginalEvent(id,from){const entry={166:'ex',167:'ex',191:'ex',279:'ex'};tab=entry[id]||'ex';selected=id;pinnedId=id;soniaView=null;open(from);}
 return {open,openPoint,openOriginalEvent,render};
})();
