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
  'No event data.':'Chưa có dữ liệu sự kiện.','Saved.':'Đã lưu.','Guardando…':'Đang lưu…',
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
 let publicGemPacks=null,publicGemPacksLoading=false;
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
 function itemName(id){return NAMES[id]||catalog.item_names[id]||itemCatalog?.[id]?.name||"Item "+id;}
 function itemIcon(id){if(catalog.item_icons[id])return catalog.item_icons[id];if(typeof itemPicture==='function'&&itemCatalog?.[id]){const pic=itemPicture(itemCatalog[id]);if(pic)return pic;}const icon=itemCatalog?.[id]?.icon;if(icon&&itemIcons?.has(icon))return '/assets/item-icons/'+icon+'.png';if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';return null;}
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
 function calendarWin(){const c=cal();if(!c||typeof GirlUI==='undefined')return;const {body}=GirlUI.win({title:'Lịch Sự Kiện',cls:'ev-cal'});const sec=(t)=>{body.append(el('h4','ev-cal-h',t));};const row=(a,b)=>{const r=el('div','ev-cal-row');r.append(el('span','',a),el('b','',b));body.append(r);};
  sec('Đặt lại');for(const r of c.resets)row(r.label,leftText(r.at));
  sec('Đang diễn ra');for(const e of c.events)row((e.kind==='month'?'[Tháng] ':'[Tuần] ')+vi(e.title),'còn '+leftText(e.end));
  sec('Sắp diễn ra');for(const e of c.next)row((e.kind==='month'?'[Tháng] ':'[Tuần] ')+vi(e.title),'sau '+leftText(e.start));
  body.append(el('p','ev-cal-note',"Lịch game: tuần tính từ Thứ Hai đến Chủ Nhật, tháng bắt đầu từ ngày 1. Sự kiện tạm đóng vẫn giữ nguyên tiến độ cho lần mở tiếp theo."));}
 function list(){const all=catalog.activities.filter(a=>inTab(a,tab)&&!(a.id===116&&hub().sevenday.done));const rows=[...all]; // Full original catalog visibility. Rewards still require server implementations.if(pinnedId){const original=catalog.activities.find(a=>a.id===pinnedId);if(original&&!rows.some(a=>a.id===pinnedId))rows.unshift(original);}return rows.sort((a,b)=>(a.id===pinnedId?1:0)-(b.id===pinnedId?1:0)?(b.id===pinnedId?1:0)-(a.id===pinnedId?1:0):(WORKING.has(b.id)-WORKING.has(a.id))||(b.rank-a.rank)||(b.id-a.id));}
 function listAll(){return catalog.activities.filter(a=>inTab(a,tab)&&!(a.id===116&&hub().sevenday.done)).sort((a,b)=>(WORKING.has(b.id)-WORKING.has(a.id))||(b.rank-a.rank)||(b.id-a.id));}

 function open(from){origin=from||'home';message='';showView('events');if(!catalog&&!loading)loading=Promise.all([api('/assets/events/catalog.json'),typeof ActKit!=='undefined'?ActKit.load():null]).then(([c])=>{catalog=c;if(typeof ActKit!=='undefined')ActKit.ids().forEach(i=>WORKING.add(i));render();}).catch(e=>{message=e.message;loading=null;render();});if(!visited){visited=true;send({action:'visit'},true);}}
 async function send(request,quiet=false){if(pending)return;pending=true;if(!quiet){message='Đang lưu…';render();}try{const r=await api('/api/events/action',request);state=r.state;const got=Object.entries(r.awards||{});message=got.length?"Đã nhận: "+got.map(([k,n])=>fmt(n)+' × '+itemName(k)).join(', '):(quiet?'':"Đã lưu.");if(got.length&&!quiet&&typeof GirlUI!=='undefined')GirlUI.toast(message);}catch(e){message=e.message;}finally{pending=false;render();if(typeof window.render==='function')window.render();}}

 function render(){
  const root=$('events-view');if(!root||view!=='events')return;root.replaceChildren();
  const top=el('header','ev-top');const back=el('button','ev-back');back.type='button';back.setAttribute('aria-label',"Quay Lại");back.append(img('/assets/ui/win_back_btn.png'));back.onclick=()=>showView(origin==='events'?'home':origin);
  const money=el('div','ev-money');for(const id of ['1','2']){const s=el('span');s.append(img('/assets/currency/icon_'+id+'_small.png'),el('b',undefined,fmt(state.items[id]||0)));money.append(s);}
  top.append(back,el('h1',undefined,"Sự Kiện"),money);root.append(top);
  if(!catalog||!hub()){root.append(el('p','ev-note',message||"Đang tải sự kiện…"));return;}
  const win=el('div','ev-window');root.append(win);const tabs=el('nav','ev-tabs');for(const [id,pos]of TABS){const b=el('button','ev-tab '+pos+(tab===id?' on':''),tabLabel(id));b.type='button';b.onclick=()=>{if(tab===id)return;tab=id;selected=null;pinnedId=null;message='';if(typeof GxbAudio!=='undefined')GxbAudio.sfx('ui_switch_page',.6);render();};if(catalog.activities.some(a=>inTab(a,id)&&claimable(a.id)))b.append(img(A('alert_icon'),'ev-tab-red'));tabs.append(b);}win.append(tabs);{const cb=el('button','ev-cal-btn','📅 Lịch');cb.type='button';cb.onclick=calendarWin;win.append(cb);}const panel=el('div','ev-panel');win.append(panel);
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
  const items=list();if(!items.some(a=>a.id===selected))selected=items[0]?.id??null;
  const strip=el('div','ev-strip');for(const a of items){const b=el('button','ev-title'+(a.id===selected?' on':''));b.type='button';b.title=vi(a.title.replace(/\n/g,' '));b.append(img(A(a.id===selected?'activity_icon_1_middle':'activity_icon_0_middle'),'ev-title-bg'),img(A('icon_'+a.icon),'ev-title-icon'),el('span','ev-title-label',vi(a.title)));if(slot(a.id))b.append(el('small','ev-title-left',leftText(slot(a.id).end)));if(claimable(a.id))b.append(img(A('person_icon_red_point'),'ev-title-red'));b.onclick=()=>{selected=a.id;message='';render();};strip.append(b);}panel.append(strip);
  requestAnimationFrame(()=>strip.querySelector('.on')?.scrollIntoView({block:'nearest',inline:'nearest'}));
  const body=el('div','ev-body');panel.append(body);
  const a=items.find(x=>x.id===selected);
  if(!a)body.append(el('p','ev-note',"Không có sự kiện trong mục này."));else if(a.id===1)checkIn(body);else if(a.id===116)sevenDay(body,a);else if(POINT[a.id])pointEvent(body,a);else if(a.id===64&&typeof Jackpot!=='undefined')Jackpot.render(body);else if(a.id===196&&typeof FireworkProject!=='undefined')FireworkProject.render(body);else if((a.id===37||a.id===189)&&typeof PuzzleEvents!=='undefined')PuzzleEvents.render(body,a.id);else if(a.id===338&&typeof BlindBox!=='undefined')BlindBox.render(body);else if(a.id===329&&typeof Pirate!=='undefined')Pirate.render(body);else if(a.id===330&&typeof Pirate!=='undefined')Pirate.vaults(body);else if(typeof ActKit!=='undefined'&&ActKit.has(a.id))ActKit.render(body,a);else if(a.id===309&&typeof SandHunt!=='undefined')SandHunt.render(body);else if(a.id===140&&typeof WishCapsule!=='undefined')WishCapsule.panel(body);else if(a.id===134&&typeof MagicCard!=='undefined')MagicCard.render(body);else if(a.id===331&&typeof MatchingPairs!=='undefined')MatchingPairs.render(body);else if(a.id===292&&typeof LostSpace!=='undefined')LostSpace.panel(body);else if(a.id===150&&typeof PumpkinPatch!=='undefined')PumpkinPatch.render(body);else archived(body,a);
  if(a?.id===184)gemOffers(body);
  const status=el('p','ev-status',message);status.setAttribute('role','status');panel.append(status);
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
 function pointEvent(parent,a){const cfg=POINT[a.id],info=state.point_events_info?.[a.id];if(!info){parent.append(el('p','ev-note',"No event data."));return;}
  const ban=el('div','pe-banner');ban.style.backgroundImage=`url('${A(cfg.bg)}')`;ban.append(el('h2','pe-title pe-title-vi',({13:'Thưởng Điểm Triệu Hồi',16:'Thưởng Điểm Chiêu Mộ',20:'Thưởng Điểm Máy Quay'})[a.id]||vi(a.title)),el('p','pe-desc',a.id===20?'Mỗi lần quay Máy Quay nhận 1 điểm. Có thể hoàn thành '+info.times+' vòng thưởng trong sự kiện!':cfg.desc));
  const strip=el('div','pe-strip');strip.append(el('b','','Đã hoàn thành ('+info.rounds+'/'+info.times+')'),el('span','pe-left',left(info)),el('span','pe-left-label','Còn lại'));ban.append(strip);
  const go=el('button','pe-go',cfg.go);go.type='button';go.style.backgroundImage=`url('${A('house_icon_1')}')`;go.disabled=!cfg.route;go.title=cfg.route?'':"Máy Quay hiện chưa khả dụng";go.onclick=()=>{if(cfg.route==='capsule')showView('capsule');else if(cfg.route==='enroll'&&typeof Enroll!=='undefined')Enroll.open('events');else if(cfg.route==='slots'&&typeof Slots!=='undefined')Slots.open('events');};ban.append(go);parent.append(ban);
  const list=el('div','pe-list');for(const t of info.tiers){const row=el('div','pe-row');const l=el('div','pe-left-col');l.append(el('b','','Đạt '+t.point+' điểm'));const bar=el('div','pe-bar');bar.style.backgroundImage=`url('${A('activity_bar_bg')}')`;const fill=el('i');fill.style.width=Math.min(100,(t.got?t.point:info.point)/t.point*100)+'%';fill.style.backgroundImage=`url('${A('activity_bar_thumb')}')`;bar.append(fill,el('span','',(t.got?t.point:Math.min(info.point,t.point))+'/'+t.point));l.append(bar);row.append(l);
   const rw=el('div','pe-rewards');for(const [id,n]of pairs(t.awards)){const r=rewardIcon(id,n,'pe-item');if(t.got)r.append(img(A('icon_check'),'pe-check'));rw.append(r);}row.append(rw);list.append(row);}
  parent.append(list);parent.append(el('p','ev-note',"Phần thưởng được cộng trực tiếp vào Túi Đồ khi đạt từng mốc. Đặt lại hằng tuần vào 00:00 Thứ Hai."));}

 function archived(parent,a){
  const c=el('div','ev-archive');c.append(img(A('icon_'+a.icon),'ev-archive-icon'),el('h2',undefined,vi(a.title.replace(/\n/g,' '))));
  if(a.desc&&a.desc!=='-1')c.append(el('p',undefined,vi(a.desc)));
  const packages={2:'MONTHLY_GIFT',3:'WEEKLY_GIFT',6:'MONTHLY_CARD',24:'WEEKLY_CARD',39:'MONTHLY_GIFT',40:'WEEKLY_GIFT'};
  const paid=Boolean(packages[a.id]||a.type1===1||/giftbag|recharge|month_card|week_card/i.test(a.icon||''));
  if(paid){
    // Gift windows remain the original events. Only show the package actually
    // published by the server; never invent a price, reward, or VIP EXP.
    const packageId=packages[a.id];
    if(packageId&&publicGemPacks===null)loadPublicGemPacks();
    const published=packageId&&publicGemPacks?.find(p=>p.id===packageId);
    if(published){
      const offer=el('article','ev-gems-offer');
      offer.append(img(A('icon_'+a.icon),'ev-item',published.name));
      const details=el('div','ev-gems-data');
      details.append(el('b',undefined,published.name));
      if(published.price_label)details.append(el('span',undefined,published.price_label));
      if(published.vip_exp)details.append(el('span',undefined,fmt(published.vip_exp)+' EXP VIP khi nhận thư đã duyệt'));
      if(published.instant_gems)details.append(el('span',undefined,fmt(published.instant_gems)+' Kim Cương'));
      if(published.manual_reward)details.append(el('small',undefined,'Quà cụ thể do QTV xác nhận trước khi giao qua Hòm Thư.'));
      offer.append(details);c.append(offer);
    }else if(packageId){
      c.append(el('p','ev-note',publicGemPacks===null?'Đang tải gói quà từ máy chủ…':'Gói này chưa được QTV công bố trên máy chủ.'));
    }
    c.append(el('p','ev-note','Thanh toán và quà tặng theo danh mục đang được QTV công bố; không dùng giá cũ hoặc tạo vật phẩm giả.'));
    const contact=el('div','ev-original-payment');
    contact.append(el('span','', 'Thanh toán: Zalo 0856848557'));
    const z=el('button','ev-native-pay','Liên hệ Zalo / Đặt gói');z.type='button';
    z.onclick=()=>window.GxbPayment?.open(packages[a.id]||'CUSTOM',
      vi(a.title.replace(/\n/g,' '))+' · Sự Kiện #'+a.id);
    contact.append(z);c.append(contact);
  }else c.append(el('p','ev-note',"Sự kiện có trong dữ liệu nhà phát triển. Chức năng nhận thưởng chưa được xác thực trên máy chủ."));
  parent.append(c);
 }
 function gemOffers(parent){
    const original=el('section','ev-original-gems');
    original.append(el('h3',undefined,'Các Gói Kim Cương Gốc'));
    if(publicGemPacks===null){
      original.append(el('p','ev-note','Đang tải các gói nạp đã công bố…'));
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

 function openPoint(id,from){tab='ex';selected=id;pinnedId=id;open(from);}
 function openOriginalEvent(id,from){const entry={166:'ex',167:'ex',191:'ex',279:'ex'};tab=entry[id]||'ex';selected=id;pinnedId=id;open(from);}
 return {open,openPoint,openOriginalEvent,render};
})();
