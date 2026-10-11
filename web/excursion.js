'use strict';
// Excursion (ExploreWindow.lua / explore_window.prefab) and Explore adventure (ExploreAdventureWindow.lua).
// Map: explore_main_scene + travel_main Spine animations at each building's effectNode (scale 1.5).
// Buildings: Store = travel_building1 (gold), Wishing Tree = 2 (gems), Food Truck = 3 (Tasty Bread 203),
// Main Center = travel_train (5 disciplines), Explore = adventure (gxb2/explore.py).
const Excursion=(()=>{
 const A=n=>'/assets/excursion/'+n+(/^explore_(main_scene|scene_)/.test(n)?'.webp':'.png');
 const NAMES={1:'Store',2:'Wishing Tree',3:'Food Truck'};
 const EVENT_NAMES={1:'Common Enemy',2:'Elite Enemy',3:'Forgotten Chest',4:'Well-hidden Chest',5:'Help Seeker',6:'Help Seeker',7:'Food Truck',8:'Market'};
 // NGUI positions (centre origin, y up) → top-left 720×1280: x=360+X, y=640−Y.
 const P=(x,y)=>[360+x,640-y];
 const ANIMS=[['travel_main_01',0,606],['travel_main_02',-198,156],['travel_main_03',-100,-183],['travel_main_04',45,345],['travel_main_05',202,19],['travel_main_06',353,1],['travel_main_07',162,-450]];
 const SPOTS={main:[-217,232,49,-165],store:[-120,-105,-13,-208],bread:[88,419,-47,-171],tree:[198,110,6,-144],explore:[207,-360,-8,-169]};
 let origin='home',app=null,popup=null,auto=false,busyLocal=false,note='',lastEvent=null;
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const hs=()=>state.home_systems||{},ex=()=>state.explore_info||{};
 function pairs(t){return String(t||'').split('|').filter(x=>x.includes('#')).map(x=>x.split('#'));}
 function root(){let r=$('excursion-view');if(!r){r=el('section','excursion-view');r.id='excursion-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from){origin=from||view;note='';showView('excursion');render();}
 function stop(){auto=false;if(app){try{app.destroy(true,{children:true,texture:false,baseTexture:false});}catch{}app=null;}closePop();}
 function iconOf(id){id=String(id);if(['1','2','203','204','205'].includes(id))return A('icon_'+id);const it=itemCatalog?.[id];if(typeof itemPicture==='function'&&it)return itemPicture(it)||'/assets/ui/item_bg.png';return '/assets/ui/item_bg.png';}
 async function home(request,msg){if(busyLocal)return null;busyLocal=true;try{const r=await api('/api/home/action',request);state=r.state;note=msg||'';return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;render();}}
 async function exp(request){if(busyLocal)return null;busyLocal=true;try{const r=await api('/api/explore/action',request);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;}}

 // ---------------- Map ----------------
 function render(){const r=root();if(view!=='excursion'){stop();return;}const keep=app;if(!r.querySelector('.ex-map'))build(r);refreshMap();if(popup)renderPop();}
 function build(r){r.replaceChildren();const top=el('header','ex-top');for(const id of ['205','204','203']){const c=el('span','ex-cur');c.dataset.item=id;c.append(img(A('icon_'+id)),el('b','','0'));if(id==='203'){const plus=el('button','ex-plus','+');plus.type='button';plus.onclick=()=>pop('bread');c.append(plus);}top.append(c);}const back=el('button','ex-back');back.type='button';back.append(img('/assets/ui/win_back_btn.png'));back.onclick=()=>{stop();showView(origin==='excursion'?'home':origin);};top.append(back);r.append(top);
  const map=el('div','ex-map');const bg=img(A('explore_main_scene'),'ex-bg');map.append(bg);const bread=img(A('explore_main_bread'),'ex-tex bread');const adv=img(A('explore_main_adventure'),'ex-tex adv');map.append(bread,adv);const cv=el('div','ex-canvas');map.append(cv);
  for(const [key,[x,y,lx,ly]] of Object.entries(SPOTS)){const [cx,cy]=P(x,y),[nx,ny]=P(x+lx,y+ly);const hot=el('button','ex-hot '+key);hot.type='button';hot.style.left=`calc(${cx-150} * var(--u))`;hot.style.top=`calc(${cy-150} * var(--u))`;hot.onclick=()=>pop(key);map.append(hot);
   const lab=el('div','ex-label '+key);lab.style.left=`calc(${nx} * var(--u))`;lab.style.top=`calc(${ny} * var(--u))`;lab.style.backgroundImage=`url('${A('building_name_bg')}')`;lab.append(el('span','',{main:'Main Center',store:'Store',bread:'Food Truck',tree:'Wishing Tree',explore:'Explore'}[key]));lab.onclick=()=>pop(key);map.append(lab);}
  for(const [key,bid,ax,ay] of [['store',1,101,111],['bread',3,94,90],['tree',2,92,170]]){const [x,y]=SPOTS[key];const [cx,cy]=P(x+ax,y+ay);const b=el('button','ex-award '+key);b.type='button';b.dataset.bid=bid;b.style.left=`calc(${cx-53} * var(--u))`;b.style.top=`calc(${cy-53} * var(--u))`;b.style.backgroundImage=`url('${A('btn_get_img_1')}')`;b.append(img('', 'ex-award-icon'));b.onclick=()=>home({action:'travel_collect',id:bid},NAMES[bid]+": claimed.");map.append(b);}
  const all=el('button','ex-all');all.type='button';all.append(img(A('get_all_img')),el('span','','Claim All'));all.onclick=claimAll;map.append(all);
  const help=el('button','ex-help');help.type='button';help.append(img(A('help_3')));help.onclick=()=>CampaignUI.popup("Excursion: Store produces Gold, Wishing Tree produces Gems, and Food Truck produces Bread. Main Center trains disciplines to unlock upgrades. Explore costs 10 Bread per exploration: encounters, chests, and merchants.",{});map.append(help);
  r.append(map);r.append(el('p','ex-note'));mountSpines(cv);}
 async function mountSpines(cv){if(typeof PIXI==='undefined')return;try{const d=await GxbSpine.load('/assets/spine/travel_main');if(view!=='excursion')return;app=new PIXI.Application({width:720,height:1280,transparent:true,antialias:true,resolution:Math.min(2,devicePixelRatio||1),autoDensity:false});app.view.className='ex-pixi';cv.append(app.view);
  for(const [anim,x,y] of ANIMS){const s=new PIXI.spine.Spine(d);s.state.setAnimation(0,anim,true);s.scale.set(1.5);const [px,py]=P(x,y);s.x=px;s.y=py;app.stage.addChild(s);}}catch(e){console.warn('travel_main',e);}}
 function refreshMap(){const r=root();for(const c of r.querySelectorAll('.ex-cur'))c.querySelector('b').textContent=number(state.items[c.dataset.item]||0);
  const blds=hs().buildings||[];for(const b of r.querySelectorAll('.ex-award')){const x=blds.find(v=>v.id===Number(b.dataset.bid));b.hidden=!x||!x.stock;if(x){b.querySelector('img').src=iconOf(x.item);}}
  const n=r.querySelector('.ex-note');if(n){n.textContent=note||(hs().started_travel?'':"Tap a building and press Start production to begin.");}}
 async function claimAll(){let got=0;for(const b of (hs().buildings||[]))if(b.stock>0){const r=await home({action:'travel_collect',id:b.id});if(r)got++;}const ready=(ex().chests||[]).some(c=>c.ready);if(ready){const r=await exp({action:'open_ready'});if(r?.got)CampaignUI.popup('Cofres abiertos',r.got);}note=got||ready?"Claimed.":"Nothing to collect.";render();}

 // ---------------- Popups ----------------
 let popKind=null;
 function pop(kind){popKind=kind;renderPop();}
 function closePop(){popup?.remove();popup=null;popKind=null;}
 function frame(title){popup?.remove();popup=el('div','ex-pop-wrap');const box=el('div','ex-pop');const head=el('div','ex-pop-head');head.style.backgroundImage=`url('${A('title_bg1')}')`;head.append(el('b','',title));const x=el('button','ex-x','✕');x.type='button';x.onclick=()=>{closePop();auto=false;render();};head.append(x);box.append(head);popup.append(box);(window.GxbFrame?.root()||document.body).append(popup);return box;}
 function renderPop(){if(!popKind)return;({store:()=>building(1),tree:()=>building(2),bread:()=>building(3),main:training,explore:adventure,bread_buy:breadBuy,upgrade:upgrade,help:exHelp,boxes:boxes,girls:girlsList}[popKind]||(()=>{}))();}
 function building(bid){const b=(hs().buildings||[]).find(v=>v.id===bid);const box=frame(NAMES[bid]);if(!b){box.append(el('p','',"No data."));return;}
  const art=img(A({1:'explore_market',2:'explore_wishing_tree',3:'explore_bread_home'}[bid]),'ex-pop-art');box.append(art);
  const rows=el('div','ex-rows');for(const [k,v]of [['Level',b.lv],['Output / h',number(b.out)],['Storage',number(b.stock)+' / '+number(b.cap)]]){const r=el('div','ex-rowl');r.style.backgroundImage=`url('${A('label_bg')}')`;r.append(el('span','',k),el('b','',String(v)));rows.append(r);}box.append(rows);
  const act=el('div','ex-acts');if(!hs().started_travel){const s=btn("Start production",()=>home({action:'travel_start',id:bid},"Production started."));act.append(s);}else{act.append(btn('Collect',()=>home({action:'travel_collect',id:bid},"Claimed."),!b.stock));}
  const cost=el('div','ex-cost');for(const [id,n]of pairs(b.cost)){const s=el('span',Number(state.items[id]||0)<Number(n)?'short':'');s.append(img(iconOf(id)),el('b','',number(n)));cost.append(s);}act.append(el('small','','Mejora:'),cost,btn('Upgrade',()=>home({action:'travel_upgrade',id:bid},NAMES[bid]+" upgraded."),!b.cost));box.append(act);
  if(bid===3)box.append(btn('Buy Tasty Bread',()=>pop('bread_buy')));box.append(el('p','ex-pop-note',note));}
 // ExploreTrainingRoomWindow ("Main Center Lv.N" = sum of the five levels): tabs HP / Attack / Crit / Speed / Crit Resist
 // (nav_btn_1 / nav_btn_2 + nav_icon_i_2, "Lv.n"), three girl slots per discipline (misc travel_train_slot_limit
 // 1#1|11#2|21#3, btn_locked until then, chibi of the stationed girl), "Attribute Upgrade · Current · Next" (+lv × grow_effect),
 // cost = base_cost + grow_cost × (lv - 1) and Upgrade (needs the other disciplines at travel_train_grade_limit).
 let trainTab=1,trainPick=0;
 const TRAIN=['HP','Attack','Crit','Speed','Crit Resist'];
 // travel_train rows: grow_effect and value_transform (0 = fraction → %, 1 = flat, 2 = per mille → %); lv_max 30,
 // cost 1#500000|205#10 + 800000|50 per level for every discipline
 const TROWS=[[0.01,0],[0.005,0],[10,2],[2,1],[10,2]],TBASE=[['1',500000],['205',10]],TGROW=[800000,50],TMAX=30;
 const tfmt=(i,lv)=>{const [g,tr]=TROWS[i-1];const v=g*lv;return tr===1?'+'+v:tr===2?'+'+(v/10).toFixed(1)+'%':'+'+(v*100).toFixed(1)+'%';};
 function training(){const t=hs().travel?.training||{};const rooms=hs().travel?.train_partners||{};const total=[1,2,3,4,5].reduce((n,i)=>n+Number(t[i]||1),0);
  const box=frame('Main Center');box.classList.add('ex-train2');box.querySelector('.ex-pop-head b').append(el('small','',' Lv.'+total));
  const tabs=el('div','ex-ttabs');for(let i=1;i<=5;i++){const b=el('button','ex-ttab'+(trainTab===i?' on':''));b.type='button';b.style.backgroundImage=`url('${A(trainTab===i?'nav_btn_1':'nav_btn_2')}')`;b.append(img(A('nav_icon_'+i+'_2')),el('small','','Lv.'+(t[i]||1)));b.title=TRAIN[i-1];b.onclick=()=>{trainTab=i;trainPick=0;renderPop();};tabs.append(b);}box.append(tabs);
  const lv=Number(t[trainTab]||1),limits=[[1,1],[11,2],[21,3]],slots=el('div','ex-tslots');const room=rooms[String(trainTab)]||[0,0,0];
  limits.forEach(([need],k)=>{const s=el('button','ex-tslot'+(lv<need?' locked':''));s.type='button';const pid=room[k];const h=pid&&state.roster.find(x=>x.partner_id===pid);
   if(lv<need){s.append(img(A('btn_locked'),'ex-tlock'));s.title='Unlocks at Lv.'+need;s.onclick=()=>{note="Unlocks at level "+need;renderPop();};}
   else if(h){const host=el('div','ex-tchibi');s.append(host);mountChibi(host,h.table_id);s.append(el('small','ex-tname',h.name));s.onclick=()=>{trainPick=k+1;renderPop();};}
   else{s.append(el('b','ex-tadd','+'));s.onclick=()=>{trainPick=k+1;renderPop();};}slots.append(s);});box.append(slots);
  if(trainPick){const used=new Set(Object.values(rooms).flat().filter(Boolean));const pk=el('div','ex-tpick');pk.append(el('p','ex-pop-note',"Choose a Girl for slot "+trainPick+(room[trainPick-1]?" (or remove her)":'')));const grid=el('div','ex-tgrid');
   if(room[trainPick-1])grid.append(btn('Quitar',()=>home({action:'travel_train_set',id:trainTab,slot:trainPick,partner_id:0}).then(()=>{trainPick=0;renderPop();}),false,'ex-btn small'));
   for(const h of [...state.roster].sort((a,b)=>(b.stars||0)-(a.stars||0)||(b.lv||0)-(a.lv||0)).slice(0,60)){const c=el('button','ex-tcand'+(used.has(h.partner_id)?' used':''));c.type='button';if(typeof portrait==='function')c.append(portrait(h.table_id,56));c.title=h.name;c.onclick=()=>home({action:'travel_train_set',id:trainTab,slot:trainPick,partner_id:h.partner_id}).then(()=>{trainPick=0;renderPop();});grid.append(c);}pk.append(grid);box.append(pk);}
  const max=TMAX;
  const tbl=el('div','ex-tattr');tbl.append(el('b','','Attribute Upgrade'),el('b','','Current'),el('b','','Next'),el('span','',TRAIN[trainTab-1]),el('span','',tfmt(trainTab,lv)),el('span','nx',lv<max?tfmt(trainTab,lv+1):'MAX'));box.append(tbl);
  if(lv<max){const cost=el('div','ex-tcost');TBASE.forEach(([k,v],i)=>{const n=v+TGROW[i]*(lv-1);const c=el('span','',);const s2=k==='1'?'/assets/currency/icon_1_small.png':(typeof itemPicture==='function'&&itemCatalog?.[k]?itemPicture(itemCatalog[k]):'');if(s2)c.append(img(s2));c.append(el('b',Number(state.items?.[k]||0)<n?'short':'',n>=1e5?Math.round(n/1000)+'K':String(n)));cost.append(c);});box.append(cost);}
  const up=el('button','ex-tup');up.type='button';up.append(img(A('icon_level_up')),el('span','',lv<max?'Upgrade':'MAX'));up.disabled=lv>=max||busyLocal;up.onclick=()=>home({action:'travel_train',id:trainTab},TRAIN[trainTab-1]+' Lv.'+(lv+1));box.append(up);
  if(note)box.append(el('p','ex-pop-note',note));}
 async function mountChibi(host,tid){try{const cat=await ChibiBattle.catalogue();const m=cat[String(tid)]?.model;if(!m||!host.isConnected)return;await GxbSpine.mount(host,'/assets/chibis/'+m,{width:120,height:150,scale:.26,origin:[.5,.92],sequence:[[(cat[String(tid)].animations||[]).includes('idle')?'idle':cat[String(tid)].animations[0],true]]});}catch{}}
 function breadBuy(){const e=ex();const box=frame('Buy Tasty Bread');let n=1;const left=Math.max(0,e.buy_limit-e.bought);const icon=el('div','ex-bread-icon');icon.append(img(iconOf('203')),el('b','',String(e.buy?.['203']||10)));box.append(icon);
  const row=el('div','ex-stepper');const val=el('b','','1');const set=v=>{n=Math.max(1,Math.min(left||1,v));val.textContent=n;price.textContent=number(state.items['2']||0)+'/'+number(n*(e.buy?.['2']||20));};const price=el('span','ex-price');
  for(const [l,f]of [['⏮',()=>set(1)],['−',()=>set(n-1)]])row.append(btn(l,f,false,'ex-step'));row.append(val);for(const [l,f]of [['+',()=>set(n+1)],['⏭',()=>set(left)]])row.append(btn(l,f,false,'ex-step'));box.append(row);const pr=el('div','ex-price-row');pr.append(img(iconOf('2')),price);box.append(pr);set(1);
  box.append(btn('OK',async()=>{const r=await exp({action:'buy_bread',count:n});renderPop();refreshMap();},!left,'ex-ok'),el('p','ex-pop-note','Purchased: '+e.bought+'/'+e.buy_limit),el('p','ex-pop-note',note));}

 // ---------------- Explore adventure ----------------
 function btn(label,fn,disabled=false,cls='ex-btn'){const b=el('button',cls,label);b.type='button';b.disabled=disabled||busyLocal;b.onclick=fn;return b;}
 function clock(s){return [Math.floor(s/3600),Math.floor(s%3600/60),s%60].map(v=>String(v).padStart(2,'0')).join(':');}
 function adventure(){const e=ex();const box=frame('Explore');box.classList.add('adv');
  const hd=box.querySelector('.ex-pop-head');const tl=el('div','ex-head-tools');for(const [t,k]of [['?','help'],['!','boxes']]){const b=el('button','ex-head-btn',t);b.type='button';b.onclick=()=>pop(k);tl.append(b);}hd.prepend(tl);
  const mid=el('div','ex-adv-top');const bld=el('div','ex-adv-bld');bld.append(img(A('explore_adventure')));const up=el('button','ex-adv-up');up.type='button';up.append(img(A('btn_level_up_new')));up.onclick=()=>pop('upgrade');if(e.can_upgrade)up.append(img(A('alert_icon'),'ex-red'));bld.append(up);mid.append(bld);
  const labels=el('div','ex-adv-labels');for(const [k,v]of [['Level',e.lv],['Chest Slot',e.slots],['Enemy Level',e.enemy_lv]]){const r=el('div','ex-rowl');r.style.backgroundImage=`url('${A('label_bg')}')`;r.append(el('span','',k),el('b','',String(v)));labels.append(r);}mid.append(labels);box.append(mid);
  const ev=e.event||lastEvent;const scene=el('div','ex-adv-scene');scene.style.backgroundImage=`url('${A('explore_scene_'+(ev?.map||1))}')`;const who=el('div','ex-adv-chibi');scene.append(who);mountExplorer(who);
  const icons=el('div','ex-adv-icons');for(const [n,f]of [['btn_change_icon',()=>pop('girls')],['btn_open_box',async()=>{const r=await exp({action:'open_ready'});if(r?.got)CampaignUI.popup('Cofres abiertos',r.got);renderPop();}],['btn_formation',()=>{closePop();showView('girls');}]]){const b=el('button','ex-adv-icon');b.type='button';b.append(img(A(n)));b.onclick=f;icons.append(b);}scene.append(icons);
  // ExploreAdventureWindow.setBtn: a pending event puts its name over the scene and turns the bottom into Go (+ its cost) and Retreat
  const pending=e.event&&!e.event.done?e.event:null;
  if(pending){const nm=el('div','ex-ev-name',EVENT_NAMES[pending.id]||'Event');scene.append(nm);{const say=pending.id===7?"I'm hungry I'm sure the Food Truck ahead has lots of Tasty Breads!~":pending.id===8?"Great! It's the mysterious merchant!":'';if(say)scene.append(el('p','ex-ev-say',say));
   else if(pending.id===5||pending.id===6){const want=pairs(pending.consume)[0];if(want){const b=el('div','ex-ev-want');b.append(img(iconOf(want[0])));scene.append(b);}}}}
  else if(lastEvent?.done){scene.append(eventCard(lastEvent));}
  box.append(scene);
  const shelf=el('div','ex-shelf');const chests=e.chests||[];for(let i=0;i<Math.max(e.slots,chests.length)+1&&i<11;i++){const c=chests[i];const card=el('div','ex-chest'+(c?'':(i<e.slots?' empty':' locked')));card.style.backgroundImage=`url('${A('gift_bg_1')}')`;
   if(c){const t=el('div','ex-time');t.style.backgroundImage=`url('${A('time_bg')}')`;t.dataset.ready=String(Math.floor(Date.now()/1000)+c.left);t.textContent=c.ready?'Ready':clock(c.left);card.append(t,el('b','ex-chest-name','Stage '+c.box+' Chest'),img(A('icon_bx_'+c.box),'ex-box'));
    if(c.ready)card.append(btn('Open',async()=>{const r=await exp({action:'open',id:c.id});if(r?.got)CampaignUI.popup('Stage '+c.box+' Chest',r.got);renderPop();},false,'ex-open'));
    else{const o=el('button','ex-open now');o.type='button';o.append(el('small','','Open Now'));const g=el('span','');g.append(img(iconOf('2')),el('b','',String(c.gems)));o.append(g);o.onclick=async()=>{const r=await exp({action:'open',id:c.id,pay:true});if(r?.got)CampaignUI.popup('Stage '+c.box+' Chest',r.got);renderPop();};card.append(o);}}
   else if(i>=e.slots)card.append(el('span','ex-lock','🔒'));shelf.append(card);}box.append(shelf);
  if(pending){const cost=pairs(pending.consume);if(cost.length){const c=el('div','ex-bread');for(const [id,n]of cost)c.append(img(iconOf(id)),el('b',Number(state.items[id]||0)<Number(n)?'short':'',number(n)));box.append(c);}
   const go=el('button','ex-go');go.type='button';go.style.backgroundImage=`url('${A('com_btn_bg')}')`;go.append(img(A('icon_go')),el('span','','Go'));go.disabled=busyLocal;
   go.onclick=()=>pending.type===1?fight():exp({action:'resolve'}).then(r=>{if(r)note="Chest obtained!";renderPop();});box.append(go);
   const left=el('button','ex-retreat','Retreat');left.type='button';left.onclick=()=>exp({action:'resolve',skip:true}).then(renderPop);box.append(left);}
  else{const bread=el('div','ex-bread');bread.append(img(iconOf('203')),el('b',Number(e.bread)<Number(e.cost?.['203']||10)?'short':'',String(e.cost?.['203']||10)));box.append(bread);
   const go=el('button','ex-go');go.type='button';go.style.backgroundImage=`url('${A('com_btn_bg')}')`;go.append(img(A('icon_go')),el('span','','Explore'));go.disabled=busyLocal;go.onclick=goOnce;box.append(go);
   const au=el('label','ex-auto');const cb=el('input');cb.type='checkbox';cb.checked=auto;cb.onchange=()=>{auto=cb.checked;if(auto)autoLoop();};au.append(cb,el('span','ex-switch'),el('span','','Auto Explore'));box.append(au);}
  box.append(el('p','ex-pop-note',note));tickTimers();}
 function eventCard(ev){const card=el('div','ex-event');card.append(el('b','',EVENT_NAMES[ev.id]||'Evento'));
  if(ev.done){const got=Object.entries(ev.got||{});card.append(el('p','',got.length?"You obtained "+got.map(([k,n])=>n+'× '+(itemCatalog?.[k]?.name||k)).join(', '):"New chest in your slots!"));card.append(btn('OK',()=>{lastEvent=null;exp({action:'resolve'}).then(renderPop);}));return card;}
  if(ev.type===1){card.append(el('p','',ev.id===2?"An Elite enemy blocks the path.":"Enemies block your path."));card.append(btn('Fight',fight),btn('Retreat',()=>exp({action:'resolve',skip:true}).then(renderPop),false,'ex-btn alt'));}
  else{const c=pairs(ev.consume);const p=el('p','',ev.id===8?"A merchant sells a chest.":"Someone needs help and will reward you with a chest.");card.append(p);const cost=el('div','ex-cost');for(const [id,n]of c){const s=el('span',Number(state.items[id]||0)<Number(n)?'short':'');s.append(img(iconOf(id)),el('b','',number(n)));cost.append(s);}card.append(cost,btn(ev.id===8?'Buy':'Help',()=>exp({action:'resolve'}).then(r=>{if(r)note="Chest obtained!";renderPop();})),btn('Leave',()=>exp({action:'resolve',skip:true}).then(renderPop),false,'ex-btn alt'));}
  return card;}
 async function goOnce(){note='';const r=await exp({action:'go'});if(r?.event)lastEvent=r.event.done?r.event:null;renderPop();refreshMap();return r;}
 async function fight(){const r=await exp({action:'resolve'});if(r&&'win' in r){note=r.win?"Victory! Chest added.":"Defeat: upgrade your team and try again.";if(!auto)CampaignUI.result(r.win,r.got||{},{event:true,label:'Explore',report:r.report});}renderPop();return r;}
 async function autoLoop(){while(auto&&view==='excursion'&&popKind==='explore'){const e=ex();if((e.chests||[]).length>=e.slots||Number(e.bread)<Number(e.cost?.['203']||10)){note='Auto Explore detenido: '+((e.chests||[]).length>=e.slots?'ranuras llenas.':"no Bread left.");auto=false;renderPop();break;}
   const r=await goOnce();if(!r){auto=false;break;}const ev=ex().event;if(ev&&!ev.done){if(ev.type===1)await fight();else await exp({action:'resolve',skip:true});}else if(ev?.done){lastEvent=null;await exp({action:'resolve'});}renderPop();await new Promise(res=>setTimeout(res,700));}}
 // the explorer canvas is kept across re-renders: every renderPop used to open a new WebGL context and the browser
 // dropped the oldest ones (white square)
 let explorer=null;
 function explorers(){try{return JSON.parse(localStorage.getItem('gxb2.explorers')||'null')||{ids:[],random:false};}catch{return {ids:[],random:false};}}
 function explorerId(){const c=explorers();const ids=c.ids.filter(id=>state.roster.some(h=>h.table_id===id));if(ids.length){if(c.random){explorerId.pick=explorerId.pick&&ids.includes(explorerId.pick)?explorerId.pick:ids[Math.floor(Math.random()*ids.length)];return explorerId.pick;}return ids[0];}
  const f=(state.formation||[])[0];return f&&state.roster.find(x=>x.partner_id===f.partner_id)?.table_id;}
 // Girls List (xwtx_chosen_models): up to six explorers, "Random" shows one of them each time
 function girlsList(){const c=explorers();const box=frame('Girls List');box.classList.add('ex-girls');const grid=el('div','ex-glist');
  const seen=new Set();for(const h of [...state.roster].sort((a,b)=>(b.stars||0)-(a.stars||0))){if(seen.has(h.table_id))continue;seen.add(h.table_id);const b=el('button','ex-gcard'+(c.ids.includes(h.table_id)?' on':''));b.type='button';b.append(portrait(h.table_id,64),el('small','',h.name));
   b.onclick=()=>{const i=c.ids.indexOf(h.table_id);if(i>=0)c.ids.splice(i,1);else if(c.ids.length<6)c.ids.push(h.table_id);save(c);pop('girls');};grid.append(b);}box.append(grid);
  box.append(el('b','ex-gcur','◆ Current Girl'));const cur=el('div','ex-gslots');for(let i=0;i<6;i++){const s=el('div','ex-gslot');if(c.ids[i])s.append(portrait(c.ids[i],56));cur.append(s);}box.append(cur);
  const r=el('label','ex-grandom');const cb=el('input');cb.type='checkbox';cb.checked=c.random;cb.onchange=()=>{c.random=cb.checked;save(c);};r.append(cb,el('span','','Random'));box.append(r);
  box.append(btn('OK',()=>{explorerId.pick=null;pop('explore');},false,'ex-ok'));
  function save(v){try{localStorage.setItem('gxb2.explorers',JSON.stringify(v));}catch{}}}
 async function mountExplorer(host){const tid=explorerId();const h=tid&&{table_id:tid};if(!h)return;
  if(explorer?.tid===h.table_id&&explorer.canvas&&!explorer.handle?.dead){host.append(explorer.canvas);return;}explorer?.handle?.destroy?.();explorer={tid:h.table_id};try{const cat=await api('/assets/chibis/catalog.json');const m=cat[String(h.table_id)];if(!m)return;const hd=await GxbSpine.mount(host,'/assets/chibis/'+m.model,{width:300,height:300,fit:.8,y:.55,className:'ex-chibi-canvas',sequence:[['idle',true]]});if(explorer?.tid===h.table_id){explorer.handle=hd;explorer.canvas=hd.app?.view;}}catch{}}
 function tickTimers(){clearTimeout(tickTimers.t);if(!popup||popKind!=='explore')return;let reload=false;for(const t of popup.querySelectorAll('.ex-time')){const left=Number(t.dataset.ready)-Math.floor(Date.now()/1000);if(left<=0){if(t.textContent!=='Ready')reload=true;t.textContent='Ready';}else t.textContent=clock(left);}if(reload){api('/api/state').then(s=>{state=s;renderPop();});return;}tickTimers.t=setTimeout(tickTimers,1000);}
 // Sub-windows drawn over the Explore window (ExploreAdventureWindow keeps showing behind them): helpBtn → explore_help_window
 // (TRAVEL_EXPLORE_HELP_U3), tipsBtn → ExploreBoxDetailWindow (six chests, award1 at 100% + dropbox_id1 odds), btnLevelUp →
 // the level comparison (Level N · Level N+1, next values in green, "Claim Stage g Chest n Time(s)  have/n").
 const EX_HELP=['1. Players will encounter random events while exploring. Each exploration consumes 10 Tasty Breads.','2. Tasty Breads are produced by the Food Truck and can also be purchased.','3. Random events that can occur in Explore includes encountering enemies, wild chests, quest giver, food truck and store.','Enemy Encounter: A battle triggers where enemies need to be defeated to gain treasure chests. Players will encounter elite enemies after every 5th victory. Defeat elite enemies to obtain higher grade chests.','Wild Chest: Obtain a chest directly.','Quest Giver: Complete the quest giver’s request and obtain a chest.','Food Truck: Produces Tasty Breads that can be claimed.','Store: Coins can be spent to purchase chests.','4. Newly acquired chests will be locked and require time to open. Players can also spend gems to instantly obtain chest rewards.','5. Once chest slots are full, new chests cannot be acquired.','6. Upgrade Exploration level to upgrade chest grade and unlock chest slots. Exploration Level can be upgraded to maximum Lv. 10 but enemies encountered will also be stronger.','7. After your Explore Level reaches 3 you can "Skip" the battles in Enemy Encounters. You will also unlock the feature to multi-open the chests and Auto Explore at the same Explore Level.'];
 let boxSel=1;
 function subWin(title,cls){const wrap=el('div','ex-sub-wrap');const box=el('div','ex-sub '+(cls||''));const head=el('div','ex-sub-head');head.append(el('b','',title));const x=el('button','ex-sub-x','✕');x.type='button';x.onclick=()=>pop('explore');head.append(x);box.append(head);wrap.append(box);wrap.onclick=ev=>{if(ev.target===wrap)pop('explore');};popup.append(wrap);return box;}
 function exHelp(){adventure();const box=subWin('Help','help');const t=el('div','ex-help-text');for(const l of EX_HELP)t.append(el('p','',l));box.append(t);}
 function reward(k,n,p){const c=el('div','ex-rw');const i=el('div','ex-rw-icon');i.append(img(iconOf(k)),el('b','',number(Number(n))));c.append(i,el('small','',p+'%'));c.title=itemCatalog?.[k]?.name||k;return c;}
 function boxes(){adventure();const d=ex().box_detail||{};const box=subWin('Stage '+boxSel+' Chest','boxes');
  const row=el('div','ex-box-row');for(const id of Object.keys(d)){const b=el('button','ex-box-pick'+(Number(id)===boxSel?' on':''));b.type='button';b.append(img(A('icon_bx_'+id)));b.onclick=()=>{boxSel=Number(id);pop('boxes');};row.append(b);}box.append(row);
  const cur=d[String(boxSel)]||{fixed:{},random:[]};box.append(el('p','ex-box-time','Opening time: '+clock(cur.time||0)));
  box.append(el('b','ex-rw-title','Guaranteed Rewards'));const f=el('div','ex-rw-grid');for(const [k,n]of Object.entries(cur.fixed))f.append(reward(k,n,100));box.append(f);
  box.append(el('b','ex-rw-title','Random Rewards'));const r=el('div','ex-rw-grid');for(const [it,p]of cur.random){const [k,n]=it.split('#');r.append(reward(k,n||1,p));}box.append(r,el('p','ex-box-foot','Chests at or above Stage 4 provide 2 Random Rewards'));}
 function upgrade(){adventure();const e=ex();const box=subWin('Explore','up');const top=e.lv>=e.max_lv;
  const col=(title,slots,lv,rates,nx)=>{const c=el('div','ex-up-col'+(nx?' nx':''));c.append(el('b','ex-up-title',title));for(const [k,v]of [['Chest Slot',slots],['Enemy Level',lv]]){const r=el('div','ex-up-row');r.append(el('span','',k),el('b','',v?String(v):'--'));c.append(r);}
   c.append(el('div','ex-up-row q','Chest Quality'));const q=el('div','ex-up-rates');for(const [g,p]of Object.entries(rates||{}).sort((a,b)=>b[0]-a[0])){const r=el('div','');r.append(el('span','','Stage '+g+' Chest'),el('b','',p+'%'));q.append(r);}c.append(q);return c;};
  const grid=el('div','ex-up');grid.append(col('Level '+e.lv,e.slots,e.enemy_lv,e.rates),col(top?'MAX':'Level '+(e.lv+1),e.next_slots,e.next_enemy_lv,e.next_rates,true));box.append(grid);
  const need=el('div','ex-need');if(!top)for(const [g,n]of Object.entries(e.upgrade_need||{})){const have=Math.min(n,Number(e.opened?.[g]||0));const r=el('div','');r.append(el('span','',`Claim Stage ${g} Chest ${n} Time(s)`),el('b',have<n?'short':'ok',String(have)),el('span','','/'+n));need.append(r);}box.append(need);
  const up=el('button','ex-up-btn');up.type='button';up.append(img(A('icon_level_up')),el('span','',top?'MAX':'Upgrade'));up.disabled=!e.can_upgrade||busyLocal;up.onclick=async()=>{const r=await exp({action:'upgrade'});if(r)note='Explore Lv.'+ex().lv;pop('explore');};box.append(up);
  if(note)box.append(el('p','ex-pop-note',note));}
 return {open,render,stop};
})();
