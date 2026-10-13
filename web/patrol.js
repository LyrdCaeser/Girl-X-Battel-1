'use strict';
// Patrol (DungeonWindow / DungeonSelectHerosWindow / DungeonShopWindow / DungeonBuyItemWindow). Rules: gxb2/patrol.py.
// Layout follows the original groups (top bar, Stationery top-left, enemy group, merchant, girls + Rice Balls at the
// bottom) on the 720×1280 frame; positions are approximate, the prefab coordinates were not recovered.
const Patrol=(()=>{
 let origin='league',panel=null,note='',busyLocal=false,timer=null,selected=1,picks=[],preview=false;
 const A=n=>'/assets/patrol/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const btn=(cls,text,fn)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
 function root(){let r=$('patrol-view');if(!r){r=el('section','patrol-view');r.id='patrol-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from){origin=from||view;panel=null;note='';preview=false;showView('patrol');}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const row=itemCatalog?.[id];return (row&&itemPicture(row))||(row?.icon?'/assets/shops/items/'+row.icon+'.png':'');}
 function nameOf(id){id=String(id);return id==='1'?'Coins':id==='2'?'Gems':itemCatalog?.[id]?.name||'Item '+id;}
 function chip(k,n){const c=el('span','pt-chip');const s=icon(k);if(s)c.append(img(s));c.append(el('b','',number(n)));c.title=nameOf(k);return c;}
 // Countdowns use the server clock (state.server_time), so a shifted local clock or QA offset stays consistent.
 let skew=0;const nowS=()=>Math.floor(Date.now()/1000)+skew;
 function clock(at){const s=Math.max(0,at-nowS());const d=Math.floor(s/86400);return (d?d+'d ':'')+[Math.floor(s%86400/3600),Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');}
 function bar(cls,value,max=100){const b=el('div','pt-bar '+cls);const f=el('i');f.style.width=Math.max(0,Math.min(100,value/max*100))+'%';b.append(f);return b;}
 async function act(req){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/patrol/action',req);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;if(view==='patrol')render();}}
 // Chibis/effects survive re-renders: the same host nodes are re-attached while the girl/enemy/merchant stays the same.
 const hosts={};
 async function catalog(){if(!catalog.c)catalog.c=await api('/assets/chibis/catalog.json').catch(()=>({}));return catalog.c;}
 function fx(parent,name,x,y,size,anim='texiao01',ms=1800){const h=at(el('div','pt-fx'),x,y,size,size);parent.append(h);GxbSpine.mount(h,'/assets/spine/'+name,{width:size,height:size,fit:.95,sequence:[[anim,false]],className:'pt-canvas'}).catch(()=>{});setTimeout(()=>h.remove(),ms);}
 function actor(slot,key,build){if(hosts[slot]?.key===key)return hosts[slot].node;const node=build();hosts[slot]={key,node};return node;}
 function chibi(tableId,flip,appear){const h=el('div','pt-chibi'+(flip?' flip':''));catalog().then(c=>{const m=c[String(tableId)];if(m)GxbSpine.mount(h,'/assets/chibis/'+m.model,{width:380,height:380,fit:.85,y:.62,className:'pt-canvas',sequence:[['idle',true]]}).catch(()=>{});});if(appear)h.classList.add('appear');return h;}
 // Positions in 720×1280 design pixels (top-left), taken from the reference capture (DungeonWindow, Fantasy 5).
 function at(e,x,y,w,h){e.style.left=`calc(${x} * var(--u))`;e.style.top=`calc(${y} * var(--u))`;if(w!=null)e.style.width=`calc(${w} * var(--u))`;if(h!=null)e.style.height=`calc(${h} * var(--u))`;return e;}
 function hms(at){const s=Math.max(0,at-nowS());return [Math.floor(s/3600),Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');}
 function render(){const r=root();if(view!=='patrol'){clearInterval(timer);timer=null;return;}const info=state.patrol_info;r.replaceChildren();if(state.server_time)skew=state.server_time-Math.floor(Date.now()/1000);const st=el('div','pt-stage');r.append(st);
  st.append(img(A('dungeon_bg'),'pt-bg'));
  // Stage map: DungeonTable map_source / map_scale / map_position (NGUI: centre origin, y up).
  if(info?.started&&info.open){const m=img('/assets/battle-maps/'+info.map+'.png','pt-map');const size=1024*(info.map_scale||1);at(m,360+(info.map_position?.[0]||0)-size/2,640+(info.map_position?.[1]||0)-size/2,size,size);st.append(m);}
  const back=at(btn('pt-back','',()=>showView(origin==='patrol'?'league':origin)),14,14,70,70);back.append(img('/assets/ui/win_back_btn.png'));st.append(back);
  const help=at(btn('pt-help','?',()=>CampaignUI.popup(help_(),{})),640,40,62,62);st.append(help);
  if(!info){st.append(at(el('p','pt-note',"Loading…"),40,600,640));return;}
  const banner=at(el('div','pt-banner'),200,40,320,64);banner.textContent=!info.unlocked?'Patrol':info.all_pass?'Cleared':`${info.phase} ${info.phase_stage}`;st.append(banner);
  if(!info.unlocked){st.append(at(el('p','pt-note pt-box',`Patrol unlocks after clearing stage ${info.unlock_stage}.`),60,560,600));return;}
  const ddl=at(el('div','pt-ddl'),160,112,400);ddl.append(el('span','',info.open?'Ending in: ':'Starts in: '),el('b','pt-clock',hms(info.open?info.window_end:info.window_start)));st.append(ddl);
  clearInterval(timer);timer=setInterval(()=>{const c=root().querySelector('.pt-clock');if(!c||view!=='patrol'){clearInterval(timer);return;}const left=(info.open?info.window_end:info.window_start)-nowS();if(left<=0){clearInterval(timer);api('/api/state').then(x=>{state=x;if(view==='patrol')render();}).catch(()=>{});return;}c.textContent=hms(info.open?info.window_end:info.window_start);},1000);
  // Stationery (drugs 4-6): permanent buffs, n / 20.
  info.drugs.filter(d=>d.type===1).forEach((d,i)=>{const g=at(el('div','pt-st'),12,168+i*40,200,36);g.title=`${d.name}: ${d.desc}`;g.append(img(A('dungeon_drug_'+d.id)));const b=bar('st',d.count,d.max);b.append(el('small','',`${Math.min(d.count,d.max)} / ${d.max}`));g.append(b);st.append(g);});
  if(!info.open){st.append(at(el('p','pt-note pt-box',"Patrol is closed. It opens for 48 h and rests for 48 h."),60,560,600));return;}
  if(!info.started){const a=at(el('div','pt-assemble'),90,420,540);a.append(el('h2','',info.max_stage?`Best stage: ${info.max_stage}`:'Assemble!'),el('p','','Neutralize Threat.'));if(info.smash_to>1)a.append(el('p','',`Auto Smash: you will start at stage ${info.smash_to}.`));a.append(btn('pt-go','Deploy Girls',()=>{panel='select';picks=[];render();}));st.append(a);if(panel)popup(st,info);return;}
  const cur=info.partners.find(p=>p.index===selected);if(!cur||cur.hp<=0){const next=info.partners.find(p=>p.hp>0);if(next)selected=next.index;}
  const girl=info.partners.find(p=>p.index===selected)||info.partners[0];
  // Selected girl: idle chibi on the left with her HP bar (chuchangtongyong when she changes).
  const gHost=actor('girl',girl.table_id,()=>{fx(st,'chuchangtongyong',20,440,340);return chibi(girl.table_id,false,true);});at(gHost,0,400,380,380);st.append(gHost);
  const gBar=at(el('div','pt-headbar'),95,440,190,30);if(girl.group)gBar.append(img(A('img_group'+girl.group),'pt-gicon'));gBar.append(bar('hp big',girl.hp));st.append(gBar);
  if(info.curr_shop_item){
   // Merchant (chuansongmen portal + tier model) with the offer; the fight button buys/skips first.
   const o=info.curr_shop_item;const model=['zhanghongpifu','shengdanxueqiao','mizhubaozang'][info.shop_tier-1]||'zhanghongpifu';
   const mHost=actor('right','m'+o.id,()=>{fx(st,'chuansongmen',380,420,340,'texiao01',1600);const h=el('div','pt-chibi appear');GxbSpine.mount(h,'/assets/spine/'+model,{width:320,height:320,fit:.85,y:.6,className:'pt-canvas',sequence:[['idle',true]]}).catch(()=>{});return h;});at(mHost,340,420,380,380);st.append(mHost);
   const m=at(el('div','pt-merchant'),330,300,370);m.append(el('p','pt-say','Well if it isn\'t Senpai! Take a look at my merchandise!'));const row=el('div','pt-offer');for(const [k,n]of Object.entries(o.item))row.append(chip(k,n));row.append(el('span','pt-arrow','→'));for(const [k,n]of Object.entries(o.cost))row.append(chip(k,n));m.append(row);
   const acts=el('div','pt-acts');acts.append(btn('pt-go','Buy',async()=>{const k=Object.keys(o.cost)[0],n=o.cost[k];if(!await GirlUI.confirm(`Dùng ${number(n)} ${nameOf(k)} để mua ${Object.entries(o.item).map(([i,c])=>c+'× '+nameOf(i)).join(', ')}?`,{title:'Mua Vật Phẩm',ok:'Mua'}))return;const res=await act({action:'merchant'});if(res?.got)CampaignUI.popup('Compra',res.got);}),btn('pt-go alt','Skip',()=>act({action:'merchant',skip:true})));m.append(acts);st.append(m);}
  else if(!info.all_pass&&info.enemies.length){
   // Enemy: the first enemy model (DungeonWindow:initEnemyModel) after the difangchuchang smoke; tap = preview of all.
   const e0=info.enemies.find(e=>e.hp>0)||info.enemies[0];const key='e'+info.stage+':'+e0.table_id;
   const eHost=actor('right',key,()=>{fx(st,'difangchuchang',380,440,340,'texiao01',1500);return chibi(e0.table_id,true,true);});at(eHost,340,400,380,380);eHost.onclick=()=>{preview=!preview;render();};st.append(eHost);
   if(preview){const g=at(el('div','pt-preview'),60,250,600);g.append(el('h3','','Enemy'));const row=el('div','pt-prev-row');for(const e of info.enemies){const c=el('div','pt-unit'+(e.hp<=0?' dead':''));c.append(typeof portrait==='function'?portrait(e.table_id,72):el('span'),el('small','','Lv.'+e.lv),bar('hp',e.hp));c.title=e.name;row.append(c);}g.append(row);g.onclick=()=>{preview=false;render();};st.append(g);}
  }
  else if(info.all_pass)st.append(at(img(A('dungeon_has_pass_en_en'),'pt-passimg'),380,560,280));
  // Rice Balls: vertical column on the left.
  info.drugs.filter(d=>d.type===0).forEach((d,i)=>{const b=at(btn('pt-drug','',()=>useDrug(d)),14,800+i*74,66,66);b.disabled=!d.count;b.title=`${d.name}: ${d.desc}`;b.append(img(A('dungeon_drug_'+d.id)),el('b','',String(d.count)));st.append(b);});
  // Skip checkbox (Quick Combat) + fight button + shop.
  const skip=at(btn('pt-skip'+(info.skip_report?' on':''),'',()=>act({action:'skip_report'})),300,900,130,44);skip.append(el('i','pt-box-check',info.skip_report?'✓':''),el('span','','Skip'));st.append(skip);
  const fight=at(btn('pt-fight','',fightNow),258,954,204,82);fight.append(img(A('dungeon_fight')));fight.disabled=!info.alive||info.all_pass||!!info.curr_shop_item;st.append(fight);
  const shop=at(btn('pt-shop','',()=>{panel='shop';render();}),630,956,76,76);shop.append(img(A('btn_dungeon_shop')));if(info.shop_items.length)shop.append(el('i','pt-badge',String(info.shop_items.length)));st.append(shop);
  // The five Patrol girls: level, stars, faction, HP and energy; the selected card is raised.
  info.partners.forEach((p,i)=>{const c=at(btn('pt-girl'+(p.index===selected?' on':'')+(p.hp<=0?' dead':''),'',()=>{selected=p.index;render();}),10+i*141,1080,134,176);
   const face=el('div','pt-face');face.append(typeof portrait==='function'?portrait(p.table_id,104):el('span'));if(p.group)face.append(img(A('img_group'+p.group),'pt-gicon'));face.append(el('b','pt-lv',String(p.lv)),el('span','pt-stars','★'.repeat(Math.min(p.stars,6))));
   c.append(face,bar('hp',p.hp),bar('mp',Math.min(p.mp,100)));c.title=`${p.name} · HP ${p.hp}% · Energy ${p.mp}`;st.append(c);});
  if(!info.alive)st.append(at(el('p','pt-note pt-box',"All Girls on the team have been eliminated. The round ends here."),60,780,600));
  if(note)st.append(at(el('p','pt-note pt-err',note),60,800,600));
  if(panel)popup(st,info);}
 async function useDrug(d){const info=state.patrol_info,p=info.partners.find(x=>x.index===selected);if(!p)return;if(!await GirlUI.confirm(`Sử dụng ${d.name} cho ${p.name}?`,{title:'Dùng Thuốc',ok:'Sử Dụng'}))return;await act({action:'use_drug',index:selected,drug_id:d.id});}
 async function fightNow(){const info=state.patrol_info;const p=info.partners.find(x=>x.index===selected);if(!p||p.hp<=0){note="Choose a Girl with HP";render();return;}
  const label=`Patrol · ${info.phase} ${info.phase_stage}`;const r=await act({action:'fight',index:selected});if(!r)return;const got={...(r.award?.got||{})};
  // Victory result (1 of 3): chest → rewards grid; item/merchant → a line in the label and on the Patrol screen.
  const d=r.award?.kind==='item'?state.patrol_info.drugs.find(x=>x.id===r.award.drug):null;
  const extra=d?"Item obtained: "+d.name:r.award?.kind==='merchant'?"A merchant has appeared!":'';
  if(!state.patrol_info.skip_report&&r.report&&typeof watchEventBattle==='function')await watchEventBattle({report:r.report,rewards:got},'patrol',label);
  else CampaignUI.result(r.win,got,{event:true,label:extra?label+' · '+extra:label,report:r.report});
  if(extra){note=extra;render();}}
 function popup(st,info){const ov=el('div','pt-overlay');ov.onclick=e=>{if(e.target===ov){panel=null;render();}};const w=el('div','pt-win');ov.append(w);const close=btn('pt-close','✕',()=>{panel=null;render();});
  if(panel==='select'){w.append(el('h2','',`Choose up to ${info.max_girls} Girls`),close);const list=el('div','pt-pick');
   const roster=[...(state.roster||[])].sort((a,b)=>(b.lv-a.lv)||(b.stars-a.stars));
   for(const h of roster){const on=picks.includes(h.partner_id);const c=btn('pt-cand'+(on?' on':''),'',()=>{if(on)picks=picks.filter(x=>x!==h.partner_id);else if(picks.length<info.max_girls)picks.push(h.partner_id);else{note='Maximum Deployed Girls!';}render();});c.append(typeof portrait==='function'?portrait(h.table_id,70):el('span'),el('small','',`Lv.${h.lv} · ${h.stars}★`));c.title=h.name;list.append(c);}
   w.append(list);const go=btn('pt-go',`Fight (${picks.length}/${info.max_girls})`,async()=>{if(!picks.length){note="You haven't deployed any Girls!";render();return;}panel=null;const r=await act({action:'start',partner_ids:picks});if(r?.smashed){const s=r.smashed;CampaignUI.popup(`Auto Smash: ${s.stages} stages cleared`,s.items);}});w.append(go);}
  else if(panel==='shop'){w.append(el('h2','',`Merchant · ${['Primary','Medium','Senior'][info.shop_tier-1]||''}`),close);
   if(!info.shop_items.length)w.append(el('p','pt-empty','No items to buy'));
   info.shop_items.forEach((o,i)=>{const row=el('div','pt-shop-row');for(const [k,n]of Object.entries(o.item))row.append(chip(k,n));const cost=el('span','pt-cost');for(const [k,n]of Object.entries(o.cost))cost.append(chip(k,n));row.append(cost,btn('pt-small','Buy',async()=>{const res=await act({action:'buy',index:i});if(res?.got)CampaignUI.popup('Compra',res.got);}));w.append(row);});}
  st.append(ov);}
 function help_(){return "1. Patrol opens for 48 h and reopens after 48 h.\n2. Choose up to 5 Girls; the team's levels and equipment remain fixed until the next round.\n3. Tap enemies to inspect them and choose 1 Girl for each battle.\n4. Quick Combat shows results; Normal Combat plays the battle.\n5. Both sides retain HP between battles; Girls with no HP cannot fight.\n6. Battles last 15 rounds; failing to eliminate all enemies is a defeat.\n7. Each victory grants a Chest (Gold or Gems), a Merchant, or an Item.\n8. Rice Balls heal; Stationery grants permanent bonuses (up to 20 each).\n9. Six areas of 100 stages: Easy, Normal, Hard, Extreme, Fantasy, and Nightmare.\n10. After clearing 50 stages in an area, previous areas are cleared automatically next time (Auto Smash).";}
 return {open,render};
})();
