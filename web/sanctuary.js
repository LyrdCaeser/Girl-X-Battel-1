'use strict';
// Sanctuary (TrialWindow → TrialFormationWindow / ActivityNewTrialFightAwardWindow / NewTrialBossInfoWindow).
// Rules: gxb2/sanctuary.py. Original art: bg_volcano_erupt / bg_trail_sences_sea, boss_nueyan / boss_sealord,
// blessing icons. The stage path is drawn as nine nodes (the node offsets of new_trial_offset are not reproduced).
const Sanctuary=(()=>{
 let origin='league',panel=null,note='',busyLocal=false,team=[],skipReplay=false,timer=null;
 const A=n=>'/assets/sanctuary/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const btn=(cls,text,fn)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
 const TYPES={1:"Normal",2:'Elite',3:'Store',4:'Boss',5:'Blessing'};
 try{skipReplay=localStorage.getItem('gxb2.sanctuary.skip')==='1';}catch{}
 function root(){let r=$('sanctuary-view');if(!r){r=el('section','sanctuary-view');r.id='sanctuary-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from){origin=from||view;panel=null;note='';showView('sanctuary-mode');act({action:'open'});}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const row=itemCatalog?.[id];return (row&&itemPicture(row))||(row?.icon?'/assets/shops/items/'+row.icon+'.png':'');}
 function chip(k,n){const c=el('span','sn-chip');const s=icon(k);if(s)c.append(img(s));c.append(el('b','',number(n)));return c;}
 async function act(req){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/sanctuary/action',req);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;if(view==='sanctuary-mode')render();}}
 let loadedAt=performance.now();
 function left(at){const s=Math.max(0,at-(state.server_time||0)-Math.floor((performance.now()-loadedAt)/1000));const d=Math.floor(s/86400);return (d?d+'d ':'')+[Math.floor(s%86400/3600),Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');}
 const hpOf=(info,pid)=>info.hp[String(pid)]??100;
 // TrialCampaignItem.iconList by stage type; finished stages show new_trial_point_1 (post), path dots trial_normal_point.
 const ICON={1:'new_trial_point3',2:'new_trial_point2',3:'new_trial_point5',4:'new_trial_point_1',5:'new_trial_point5'};
 function at(e,x,y,w,h){e.style.left=`calc(${x} * var(--u))`;e.style.top=`calc(${y} * var(--u))`;if(w!=null)e.style.width=`calc(${w} * var(--u))`;if(h!=null)e.style.height=`calc(${h} * var(--u))`;return e;}
 function render(){const r=root();if(view!=='sanctuary-mode'){clearInterval(timer);timer=null;return;}loadedAt=performance.now();const info=state.sanctuary_info;r.replaceChildren();const st=el('div','sn-stage');r.append(st);
  if(!info){st.append(el('p','sn-note',"Loading…"));return;}
  st.append(img(A(info.scene),'sn-bg'));
  // Top bar: Sanctuary coins (item 15) and back.
  const top=at(el('div','sn-top'),0,0,720,66);const coin=el('div','sn-coin');const ci=icon('15');if(ci)coin.append(img(ci));coin.append(el('b','',number(info.coins||0)));top.append(coin);
  const back=btn('sn-back','',()=>showView(origin==='sanctuary-mode'?'league':origin));back.append(img('/assets/ui/win_back_btn.png'));top.append(back);st.append(top);
  if(!info.unlocked){st.append(at(el('p','sn-note sn-box',`Sanctuary unlocks after clearing stage ${info.unlock_stage}.`),60,560,600));return;}
  const clk=at(el('div','sn-ddl'),16,100,360,44);clk.append(el('i','sn-clockicon','🕑'),el('span','','Ending in: '),el('b','sn-clock',left(info.week_end)));st.append(clk);
  st.append(at(el('div','sn-sanctum',info.sanctum),16,146,360));
  // Round buttons: blessings, reset, help, shop.
  const bless=at(btn('sn-round','',()=>{panel='bless';render();}),440,92,56,56);bless.append(el('span','','✦'));bless.title='Blessings you have acquired this round';if(info.buffs.length)bless.append(el('i','sn-badge',String(info.buffs.length)));st.append(bless);
  const rs=at(btn('sn-round','',async()=>{if(!info.reset_ready){note='Cannot Reset';render();return;}if(await GirlUI.confirm("Quay về tầng 1? Chỉ được đặt lại một lần mỗi ngày, lượt đặt lại không cộng dồn.",{title:"Đặt Lại Thánh Địa",ok:"Đặt Lại",danger:true}))await act({action:'reset'});}),504,92,56,56);rs.append(el('span','','↺'));rs.title=info.reset_ready?'Reset available：1':'Cannot Reset';if(!info.reset_ready)rs.classList.add('off');st.append(rs);
  st.append(at(btn('sn-round','?',()=>CampaignUI.popup(String(HELP),{})),568,92,56,56));
  const shop=at(btn('sn-shopbtn','',()=>{if(typeof Shops!=='undefined')Shops.open('sanctuary-mode',13);}),632,76,82,86);shop.append(img('/assets/arena/shop.png','sn-shopimg'),el('b','','SHOP'));st.append(shop);
  // Boss medallion (NewTrialBossInfoWindow) at the top: grey until the boss stage.
  const bossNow=info.current_type===4&&!info.done;const boss=at(btn('sn-bossmed'+(bossNow?'':' grey'),'',()=>{if(bossNow){panel='stage';render();}}),250,190,220,220);boss.append(img(A(info.boss===2?'new_trial_boss2':'new_trial_boss')));boss.title=info.boss_name;st.append(boss);
  // Stage path from new_trial_offset: only reached stages and their dots are shown.
  for(const n of info.nodes){const belong=n.belong;if(!info.done&&belong>info.stage)continue;
   if(n.stage===0){const d=at(img(A('trial_normal_point'),'sn-dot'),n.x-14,n.y-8,28,16);st.append(d);continue;}
   const s=info.stages.find(x=>x.id===n.stage);const finished=info.done||n.stage<info.stage;const cur=!finished&&n.stage===info.stage;
   const name=finished?'new_trial_point_1':ICON[s?.type||1];const w=finished?57:67,h=finished?44:110;
   const node=at(btn('sn-point'+(cur?' current':''),'',()=>{if(cur){panel='stage';render();}}),n.x-w/2,n.y-h,w,h);node.append(img(A(name)));if(cur&&s?.type!==4)node.append(el('b','sn-num',String(n.stage)));st.append(node);}
  if(info.done)st.append(at(el('p','sn-note sn-box',"Round completed! Reset (once per day) or wait for the next week."),60,1120,600));
  if(note)st.append(at(el('p','sn-note sn-err',note),40,1190,640));
  if(info.pending?.length)choose(st,info);else if(panel==='fight')formation(st,info);else if(panel==='stage')stagePanel(st,info);else if(panel==='bless')blessPanel(st,info);
  clearInterval(timer);timer=setInterval(()=>{const c=root().querySelector('.sn-clock');if(!c||view!=='sanctuary-mode'){clearInterval(timer);return;}c.textContent=left(info.week_end);},1000);}
 const HELP="1. 9 stages: Normal, Elite (choose a Blessing), Blessing (healing), Store, and Boss.\n2. Girls retain HP between stages; at 0 HP they cannot fight this round.\n3. Blessings last for the whole round.\n4. The boss revives once. Rewards depend on total damage.\n5. You have 1 non-accumulating daily reset (00:00 UTC). Sanctuary changes weekly.";
 function overlay(st,title){const ov=el('div','sn-overlay');ov.onclick=e=>{if(e.target===ov){panel=null;render();}};const w=el('div','sn-win');ov.append(w);w.append(el('h2','',title),btn('sn-close','✕',()=>{panel=null;render();}));st.append(ov);return w;}
 function blessPanel(st,info){const w=overlay(st,'Blessings you have acquired this round');if(!info.buffs.length)w.append(el('p','','No Blessings'));for(const b of info.buffs){const d=info.buff_info[b];const row=el('div','sn-brow');row.append(img(A(d.icon)),(()=>{const t=el('div');t.append(el('b','',d.name),el('small','',d.desc));return t;})());w.append(row);}}
 function stagePanel(st,info){const typ=info.current_type;const s=info.stages.find(x=>x.id===info.stage);const w=overlay(st,typ===4?info.boss_name:`Stage ${info.stage} · ${TYPES[typ]}`);
  if(Object.keys(s.rewards).length){const rw=el('div','sn-rw');for(const [k,n]of Object.entries(s.rewards))rw.append(chip(k,n));w.append(rw);}
  if(typ===1||typ===2){if(info.enemy.length){const e=el('div','sn-enemy');for(const u of info.enemy){const c=el('div','sn-unit'+(u.hp<=0?' dead':''));c.append(typeof portrait==='function'?portrait(u.table_id,56):el('span'),el('small','',`Lv.${u.lv}`),bar(u.hp));e.append(c);}w.append(el('p','',"Opponents (a reflection of your team):"),e);}else w.append(el('p','',"Your opponents will reflect your strongest Girls."));w.append(btn('sn-go','Fight',openFight));}
  else if(typ===4){w.append(img(A(info.boss_image),'sn-boss'),el('p','',"Revives once and becomes stronger. Rewards depend on total damage."));const tiers=el('div','sn-tiers');info.tiers.slice(0,Math.max(info.tiers_paid+3,3)).forEach((t,i)=>{const row=el('div','sn-tier'+(i<info.tiers_paid?' paid':''));row.append(el('b','',number(t.damage)));for(const [k,n]of Object.entries(t.rewards))row.append(chip(k,n));tiers.append(row);});w.append(el('p','sn-dmg',`Total damage: ${number(info.damage)}`),tiers,btn('sn-go','Fight',openFight));}
  else if(typ===3){w.append(el('p','','Useful items on sale~'),btn('sn-go alt','Store',()=>{if(typeof Shops!=='undefined')Shops.open('sanctuary-mode',13);}),btn('sn-go','Continue',()=>{panel=null;act({action:'continue'});}));}
  else if(typ===5){w.append(el('p','',"Receive a healing Blessing."),btn('sn-go','Open',()=>{panel=null;act({action:'continue'});}));}}
 function openFight(){const info=state.sanctuary_info;const ok=(state.roster||[]).filter(h=>hpOf(info,h.partner_id)>0);team=team.filter(t=>ok.some(h=>h.partner_id===t.partner_id));
  if(!team.length)team=[...ok].sort((a,b)=>b.lv-a.lv).slice(0,6).map((h,i)=>({partner_id:h.partner_id,pos:i+1}));panel='fight';render();}
 function formation(st,info){const w=overlay(st,'Battle');
  const sk=btn('sn-skip'+(skipReplay?' on':''),'',()=>{skipReplay=!skipReplay;try{localStorage.setItem('gxb2.sanctuary.skip',skipReplay?'1':'0');}catch{};render();});sk.append(el('i','',skipReplay?'✓':''),el('span','','Skip'));w.append(sk);
  const roster=[...(state.roster||[])].sort((a,b)=>b.lv-a.lv);const byId=new Map(roster.map(h=>[h.partner_id,h]));
  const grid=el('div','sn-formation');for(const [label,poss]of [['Front',[1,2]],['Back',[3,4,5,6]]]){const line=el('div','sn-line');line.append(el('b','sn-line-name '+label.toLowerCase(),label));for(const p of poss){const t=team.find(x=>x.pos===p);const slot=btn('sn-slot','',()=>{if(t){team=team.filter(x=>x!==t);render();}});if(t){const h=byId.get(t.partner_id);slot.append(typeof portrait==='function'?portrait(h.table_id,72):el('span'),bar(hpOf(info,h.partner_id)));}line.append(slot);}grid.append(line);}w.append(grid);
  const pool=el('div','sn-pool');for(const h of roster){const hp=hpOf(info,h.partner_id);const used=team.some(t=>t.partner_id===h.partner_id);const c=btn('sn-cand'+(used?' on':'')+(hp<=0?' dead':''),'',()=>{if(hp<=0)return;if(used)team=team.filter(t=>t.partner_id!==h.partner_id);else{const free=[1,2,3,4,5,6].find(p=>!team.some(t=>t.pos===p));if(free)team.push({partner_id:h.partner_id,pos:free});}render();});c.disabled=hp<=0;c.append(typeof portrait==='function'?portrait(h.table_id,56):el('span'),bar(hp),el('small','',`Lv.${h.lv}`));c.title=h.name;pool.append(c);}
  w.append(pool,btn('sn-go','Fight',fight));}
 function bar(v){const b=el('i','sn-bar');const f=el('b');f.style.width=Math.max(0,v)+'%';b.append(f);return b;}
 async function fight(){panel=null;const info=state.sanctuary_info;const label=`${info.sanctum} · Stage ${info.stage}`;const r=await act({action:'fight',team});if(!r)return;const got={...(r.got||{})};
  if(!skipReplay&&r.report&&typeof watchEventBattle==='function')await watchEventBattle({report:r.report,rewards:got},'sanctuary-mode',label);else CampaignUI.result(r.win,got,{event:true,label:label+(r.damage!=null?` · ${number(r.damage)} damage`:''),report:r.report});render();}
 function choose(st,info){const ov=el('div','sn-overlay');const w=el('div','sn-win');ov.append(w);w.append(el('h2','','Please choose a blessing!'));const g=el('div','sn-options');
  info.pending.forEach((b,i)=>{const d=info.buff_info[b];const c=btn('sn-option','',()=>act({action:'pick',index:i}));c.append(img(A(d.icon)),el('b','',d.name),el('small','',d.desc));g.append(c);});w.append(g);st.append(ov);}
 return {open,render};
})();
