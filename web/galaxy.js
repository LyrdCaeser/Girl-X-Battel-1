'use strict';
// Galaxy Voyage (GalaxyTripMainWindow → GalaxyTripEnterWindow / GalaxyTripMapWindow / FightWindow / FormationWindow,
// GalaxyBattlePassWindow, store). Rules: gxb2/galaxy.py. Layout from docs/references/2026-09-29-e (06 systems, 07 System
// window, 08 Galaxy Tyrant, 09 battle). Art: galaxy_trip_* sprites, system maps, event icons, cell masks.
const Galaxy=(()=>{
 let origin='home',panel='main',note='',busyLocal=false,skipReplay=false,timer=null,modal=null,mapId=null,sel=null,route=null,team=[],tab=0,teamEdit=null,tyrantLv=1;
 const A=n=>'/assets/galaxy/'+n;
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const btn=(cls,text,fn)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
 try{skipReplay=localStorage.getItem('gxb2.galaxy.skip')==='1';}catch{}
 const OWN=['356','358','359','360','396','397','398','402'];
 function icon(id){id=String(id);if(OWN.includes(id))return A('icon_'+id+'.png');if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const row=itemCatalog?.[id];return (row&&itemPicture(row))||(row?.icon?'/assets/shops/items/'+row.icon+'.png':'');}
 function chip(k,n){const c=el('span','gv-chip');const s=icon(k);if(s)c.append(img(s));c.append(el('b','',typeof n==='string'?n:number(n)));return c;}
 function tile(k,n){const t=el('span','gv-tile');const s=icon(k);if(s)t.append(img(s));t.append(el('b','',number(n)));t.title=itemCatalog?.[k]?.name||'';return t;}
 function root(){let r=$('galaxy-view');if(!r){r=el('section','galaxy-view');r.id='galaxy-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from){origin=from||view;panel='main';note='';modal=null;route=null;showView('galaxy');act({action:'open'});}
 async function act(req){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/galaxy/action',req);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;if(view==='galaxy')render();}}
 let loadedAt=performance.now();const now=()=>(state.server_time||0)+Math.floor((performance.now()-loadedAt)/1000);
 const dh=s=>{s=Math.max(0,s);const d=Math.floor(s/86400),h=Math.floor(s%86400/3600);return d?`${d}D ${h}H`:hms(s);};
 const hms=s=>{s=Math.max(0,Math.floor(s));return [Math.floor(s/3600),Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');};
 function render(){const r=root();if(view!=='galaxy'){clearInterval(timer);timer=null;return;}loadedAt=performance.now();const info=state.galaxy_info;r.replaceChildren();const st=el('div','gv-stage');r.append(st);
  if(!info){st.append(el('p','gv-note',"Loading…"));return;}
  if(!info.unlocked){top(st,'Galaxy Voyage');st.append(el('p','gv-note gv-box',`Galaxy Voyage unlocks after clearing stage ${info.unlock_stage} of Campaign (16-4) and owning a 10★ Girl.`));return;}
  if(panel==='map'&&mapId)mapView(st,info);else if(panel==='hole')holeView(st,info);else if(panel==='team')teamView(st,info);else if(panel==='pass')passView(st,info);else if(panel==='shop')shopView(st,info);else mainView(st,info);
  if(modal)modal(st,info);
  if(note)st.append(el('p','gv-err',note));
  clearInterval(timer);timer=setInterval(tick,1000);}
 function tick(){if(view!=='galaxy'){clearInterval(timer);return;}const info=state.galaxy_info;root().querySelectorAll('[data-end]').forEach(e=>{const left=Number(e.dataset.end)-now();e.textContent=(e.dataset.prefix||'')+(e.dataset.fmt==='d'?dh(left):hms(left));});
  const ex=info?.explore;if(ex&&panel==='map'){let t=ex.start,done=0;for(const d of ex.times){t+=d;if(t<=now())done++;}if(done!==ex.done){clearInterval(timer);act({action:'open'});}}}
 function top(st,title,extra=[]){const bar=el('div','gv-top');const b=btn('gv-back','',()=>{if(panel==='main')showView(origin==='galaxy'?'home':origin);else{panel='main';modal=null;route=null;render();}});b.append(img('/assets/ui/win_back_btn.png'));
  const chips=el('div','gv-chips');extra.forEach(x=>chips.append(x));bar.append(chips,b);st.append(bar);if(title)st.append(el('h2','gv-title',title));}
 // GalaxyTripMainWindow (capture 06): 9 Systems with their progress, Exploration Period, Passport, SHOP, Return, Team.
 const POS=[[18,16],[48,22],[78,16],[18,42],[48,48],[78,42],[18,68],[48,74],[78,68]];
 function mainView(st,info){st.classList.add('gv-main');top(st,'',[chip('402',`${info.coupons}/${info.coupon_max}`),chip('398',info.stones)]);
  const head=el('div','gv-head');head.append(img(A('galaxy_trip_text_logo_en_en.png'),'gv-logo'));const per=el('div','gv-period');per.dataset.end=info.exploring?info.explore_end:info.season_end;per.dataset.fmt='d';per.dataset.prefix=info.exploring?'Exploration Period ':'Result phase · new season in ';per.textContent=per.dataset.prefix+dh(Number(per.dataset.end)-now());head.append(per);st.append(head);
  const side=el('div','gv-side');side.append(btn('gv-round','!',()=>{modal=helpModal;render();}),btn('gv-round','📊',()=>{modal=rankModal;render();}));st.append(side);
  const right=el('div','gv-rightbtns');const pass=btn('gv-imgbtn','',()=>{panel='pass';tab=0;render();});pass.append(img(A('galaxy_trip_btn_txz.png')));pass.title='Voyager Passport';const shop=btn('gv-imgbtn','',()=>{panel='shop';tab=0;render();});shop.append(img(A('galaxy_trip_btn_sd.png')));right.append(pass,shop);st.append(right);
  const field=el('div','gv-field');const list=[...info.systems,{id:999,name:info.hole.name,icon:info.hole.icon,big:info.hole.big,open:info.hole.open,available:true,progress:null,hole:true}];
  list.forEach((s,i)=>{const [x,y]=POS[i]||[50,90];const b=btn('gv-planet'+(s.open?'':' locked')+(s.current?' current':''),'',()=>{if(!s.open){note=s.hole?"Unlocks after meeting the requirements of System 4.":(s.available?"Meet the requirements of the previous system (Progress).":"Available in later seasons.");render();return;}sel=s.id;modal=enterModal;render();});
   b.style.left=x+'%';b.style.top=y+'%';b.append(img(A((s.open?s.icon:'galaxy_trip_ball_lock')+'.png'),'gv-ball'));const lab=el('div','gv-plabel');if(s.progress!=null){const p=el('span','gv-pct',s.progress+'%');lab.append(p);}lab.append(el('b','',s.name));if(s.current)lab.append(el('small','gv-exploring',info.explore?'⚠ Exploring...':'◉ Current'));b.append(lab);field.append(b);});
  st.append(field);
  const bottom=el('div','gv-bottom');const ret=btn('gv-imgbtn big','',()=>showView(origin==='galaxy'?'home':origin));ret.append(img(A('galaxy_trip_btn_fh.png')),el('b','','Return'));const tm=btn('gv-imgbtn big','',()=>{panel='team';teamEdit=info.teams.map(t=>[...t.members]);render();});tm.append(img(A('galaxy_trip_btn_bd.png')),el('b','','Team'));bottom.append(ret,tm);st.append(bottom);
  if(info.last_reward&&!mainView.shown){mainView.shown=true;setTimeout(()=>CampaignUI.popup(`Season reward · ${info.last_reward.bracket}`,info.last_reward.got),50);}}
 function overlay(st,title,cls=''){const ov=el('div','gv-overlay');ov.onclick=e=>{if(e.target===ov){modal=null;render();}};const w=el('div','gv-win '+cls);const h=el('div','gv-winhead');h.append(el('b','',title),btn('gv-close','✕',()=>{modal=null;render();}));w.append(h);ov.append(w);st.append(ov);return w;}
 function helpModal(st,info){const w=overlay(st,'Galaxy Voyage');w.append(el('div','gv-help',info.help.join('\n\n').replaceAll('|','\n').replaceAll('%%','%')));}
 function rankModal(st,info){const w=overlay(st,'Ranking');w.append(el('p','',`Exploration Points this season: ${number(info.points)}`),el('p','gv-hint',"Without a server, there is no player ranking: when the results phase starts, you receive the reward tier matching your points."));}
 // GalaxyTripEnterWindow (capture 07).
 function enterModal(st,info){const s=sel===999?{id:999,name:info.hole.name,intro:info.hole.intro,big:info.hole.big}:info.systems.find(x=>x.id===sel);const w=overlay(st,s.name,'gv-enter');
  const body=el('div','gv-enterbody');body.append(img(A(s.big+'.png'),'gv-bigball'));const t=el('p','gv-diary');t.append(el('span','',s.intro),el('i','','---Voyager\'s Diary'));body.append(t);w.append(body);
  if(s.req){const r=el('div','gv-req');r.append(el('b','','Requirement:'));r.append(el('span',s.req.ruler?'ok':'',`Defeat Boss (${s.req.ruler?1:0}/1)`),el('span',s.req.crates[0]>=s.req.crates[1]?'ok':'',`Supply Crates Discovered (${s.req.crates[0]}/${s.req.crates[1]})`),el('span',s.req.end?'ok':'',`Connect Entrance and Exit (${s.req.end?1:0}/1)`));w.append(r);}
  w.append(btn('gv-go','Enter',async()=>{if(sel!==999&&info.current&&info.current!==sel){if(info.explore){note='You need to Recall your current Exploration before moving to another System.';modal=null;render();return;}if(!confirm('The Exploration Progress in this System will be reset if you move to another System confirm to continue?'))return;}
   modal=null;const r=await act({action:'enter',map:sel});if(r){if(sel===999){panel='hole';}else{panel='map';mapId=sel;}render();}}));}
 // GalaxyTripMapWindow: the grid (row 1 = start at the bottom), fog masks, event icons, route planning, timers.
 // Capture 2026-09-29-h/04-06: dark cells on the System art, cyan edge on explorable ones, explored ones clear,
 // numbered route pins, "Exploring…" panel with Time Remaining, and Return · Route · Progress · Recall · Team.
 function mapView(st,info){const s=info.systems.find(x=>x.id===mapId);const m=info.maps[String(mapId)];st.classList.add('gv-mapstage');st.style.backgroundImage=`url('${A(s.bg+'.webp')}')`;
  mapTop(st,info,s.name);
  if(!m){st.append(el('p','gv-note',"Loading…"));return;}
  const ex=info.explore&&info.explore.map===mapId?info.explore:null;
  const W=m.w,H=m.h;const wrap=el('div','gv-gridwrap');const grid=el('div','gv-grid');grid.style.setProperty('--w',W);grid.style.setProperty('--h',H);
  const types=info.types;
  for(let row=H-1;row>=0;row--)for(let col=0;col<W;col++){const i=row*W+col;const c=m.cells[i];if(!c||c.a!==i)continue;const drawRow=H-1-row;
   const t=types[c.t];const [sw,sh]=t.size;const cell=btn('gv-cell s-'+c.s+' t'+c.t,'',()=>cellClick(info,m,i,c));
   cell.style.gridColumn=`${col+1} / span ${sw}`;cell.style.gridRow=`${drawRow-sh+2} / span ${sh}`;
   if(c.s!=='done'&&(c.t!==10))cell.append(img(A(t.icon+'.png'),'gv-ev'));
   if(c.hp!=null&&c.s!=='done'){const hp=el('span','gv-hp');const f=el('i');f.style.width=Math.round(c.hp*100)+'%';hp.append(f);cell.append(hp);}
   const n=route&&route.includes(i)?route.indexOf(i)+1:c.n;if(n)cell.append(pin(n,c.s==='ready'));
   grid.append(cell);}
  wrap.append(grid);st.append(wrap);
  // keep the scroll between re-renders; the first time a System opens, show the start row (bottom)
  mapView.pos=mapView.pos||{};const key=String(mapId);wrap.onscroll=()=>{mapView.pos[key]=wrap.scrollTop;};requestAnimationFrame(()=>{wrap.scrollTop=key in mapView.pos?mapView.pos[key]:wrap.scrollHeight;});
  if(ex&&ex.done<ex.ids.length){const pan=el('div','gv-exploring');const ring=el('div','gv-ring');ring.append(el('b','','Exploring...'));const t=el('p','gv-remain');t.dataset.end=ex.end;t.dataset.prefix='Time Remaining：';t.textContent=t.dataset.prefix+hms(ex.end-now());pan.append(ring,t);st.append(pan);}
  if(ex&&ex.done>0&&!modal&&!mapView.claimShown){mapView.claimShown=true;modal=claimModal;}
  if(!ex)mapView.claimShown=false;
  const bottom=el('div','gv-bottom gv-mapbottom');const ret=btn('gv-imgbtn big','',()=>{panel='main';route=null;render();});ret.append(img(A('galaxy_trip_btn_fh.png')),el('b','','Return'));
  if(route){const ok=btn('gv-imgbtn big on','',async()=>{if(!route.length){route=null;render();return;}const r=await act({action:'route',cells:route});if(r)route=null;render();});ok.append(img(A('galaxy_trip_btn_xl.png')),el('b','',`OK ${route.length}/${info.route_limit}`));bottom.append(ret,ok);st.append(bottom);return;}
  const rt=btn('gv-imgbtn big','',()=>{if(ex){note='Cannot do this during an ongoing Exploration';render();return;}route=[];render();});rt.append(img(A('galaxy_trip_btn_xl.png')),el('b','','Route'));
  const pr=btn('gv-progressbtn','',()=>{modal=progressModal;render();});const dial=el('div','gv-dial');dial.append(el('b','',String(m.progress).padStart(2,'0')),el('small','','%'));pr.append(dial,el('b','','Progress'));if(m.weaken>0)pr.title=`Ruler −${Math.round(m.weaken*100)}%`;
  const rc=btn('gv-imgbtn big','',async()=>{if(!ex){note="No exploration in progress";render();return;}if(!confirm("Recall? You will receive rewards already earned and cancel the remaining route."))return;const r=await act({action:'recall'});if(r?.got&&Object.keys(r.got).length)CampaignUI.popup('Exploration Reward',r.got);});rc.append(img(A('galaxy_trip_btn_zh.png')),el('b','','Recall'));rc.disabled=!ex;
  const tm=btn('gv-imgbtn big','',()=>{panel='team';teamEdit=info.teams.map(t=>[...t.members]);render();});tm.append(img(A('galaxy_trip_btn_bd.png')),el('b','','Team'));
  bottom.append(ret,rt,pr,rc,tm);st.append(bottom);}
 function pin(n,ready){const p=el('span','gv-pin'+(ready?' ready':''));p.append(el('b','',String(n)));return p;}
 function mapTop(st,info,title){const bar=el('div','gv-top');const b=btn('gv-back','',()=>{panel='main';route=null;modal=null;render();});b.append(img('/assets/ui/win_back_btn.png'));const chips=el('div','gv-chips');chips.append(chip('402',`${info.coupons}/${info.coupon_max}`),chip('397',info.points));bar.append(chips,b);st.append(bar);
  const head=el('div','gv-maphead');const left=el('div','gv-lbtns');left.append(btn('gv-round','!',()=>{modal=helpModal;render();}),btn('gv-round','📊',()=>{modal=rankModal;render();}));if(mapId&&info.maps[String(mapId)]?.buffs?.length)left.append(btn('gv-round','✦',()=>{modal=buffModal;render();}));
  const right=el('div','gv-lbtns');const pass=btn('gv-imgbtn','',()=>{panel='pass';tab=0;render();});pass.append(img(A('galaxy_trip_btn_txz.png')));const shop=btn('gv-imgbtn','',()=>{panel='shop';tab=0;render();});shop.append(img(A('galaxy_trip_btn_sd.png')));right.append(pass,shop);
  head.append(left,el('h2','gv-maptitle',title),right);st.append(head);}
 // "Details" (capture 2026-09-29-h/02): explored areas of the route ready to claim.
 function claimModal(st,info){const ex=info.explore;if(!ex){modal=null;return;}const s=info.systems.find(x=>x.id===ex.map);const w=overlay(st,'Details','gv-claim');
  const body=el('div','gv-claimbody');const ok=el('div','gv-okmark');ok.append(img(A('galaxy_trip_ts_dui1.png')),el('b','',String(ex.done)));body.append(ok,img(A(s.big+'.png'),'gv-bigball'),el('p','',`Explore System: ${s.name}`),el('p','',`Explored Area: ${ex.done}`));w.append(body);
  const m=info.maps[String(ex.map)];const got={};for(const a of ex.ids.slice(0,ex.done)){const e=info.events[String(m.cells[a].e)];if(!e)continue;got['397']=(got['397']||0)+e.points;for(const [k,n] of Object.entries(e.awards))got[k]=(got[k]||0)+n;}
  const tl=el('div','gv-tiles gv-claimtiles');for(const [k,n] of Object.entries(got))tl.append(tile(k,n));w.append(tl);
  w.append(btn('gv-go','Claim',async()=>{modal=null;const r=await act({action:'claim'});if(r?.got&&Object.keys(r.got).length)CampaignUI.popup('Exploration Reward',r.got);}));}
 function cellClick(info,m,i,c){if(c.s==='done')return;const enemy=[1,2,3].includes(c.t);
  if(route&&!enemy){if(c.s==='exploring'||c.s==='ready')return;const k=route.indexOf(i);if(k>=0)route.splice(k);else if(route.length<info.route_limit)route.push(i);render();return;}
  sel={i,c};modal=eventModal;render();}
 function eventModal(st,info){const {i,c}=sel;const t=info.types[c.t];const ev=info.events[String(c.e||info.maps[String(mapId)].cells[c.a].e)];const w=overlay(st,t.name,'gv-event');
  const body=el('div','gv-enterbody');body.append(img(A(t.big+'.png'),'gv-bigev'));body.append(el('p','gv-diary',t.intro));w.append(body);
  const aw=el('div','gv-awards');aw.append(el('b','','Exploration Reward'));const tl=el('div','gv-tiles');tl.append(tile('397',ev.points));for(const [k,n] of Object.entries(ev.awards))tl.append(tile(k,n));aw.append(tl);w.append(aw);
  const enemy=[1,2,3].includes(c.t);
  if(enemy){if(c.t===3&&info.maps[String(mapId)].weaken>0)w.append(el('p','gv-hint',`Decay / Frustration: Ruler HP y Attack −${Math.round(info.maps[String(mapId)].weaken*100)}%`));
   w.append(el('p','gv-hint',c.t===3?"Ruler: defeat it in a single attempt.":"Enemy HP does not recover between attempts."));
   const go=btn('gv-go','',()=>{modal=teamPick;render();});go.append(el('span','','Challenge'),chip('402',1));go.disabled=c.s==='fog'||info.coupons<1;w.append(go);if(c.s==='fog')w.append(el('p','gv-hint',"Explore an adjacent area first."));}
  else{w.append(el('p','gv-hint',`Tiempo: ${hms(t.time)}`));const go=btn('gv-go','Explore',async()=>{modal=null;await act({action:'route',cells:[i]});});go.disabled=c.s!=='open'||!!info.explore;w.append(go);if(c.s==='fog')w.append(el('p','gv-hint',"Explore an adjacent area first (or an area in the starting row)."));}}
 // BattleFormationWindow (capture 2026-09-29-h/03): power, Skip, Servant, Front / Back, faction auras
 // (GroupBuffTable:getBuffIds, group_buff_on/off_N), Fight, faction filter and the Girls grid.
 let powers=null,buffs=null,faction=0;
 function loadFormationData(){if(!powers)api('/api/partners/power').then(p=>{powers=p;if(modal===teamPick)render();}).catch(()=>{powers={};});if(!buffs)api('/assets/group-buff/buffs.json').then(b=>{buffs=b;if(modal===teamPick)render();}).catch(()=>{buffs={};});}
 function activeBuffs(groups){if(!buffs)return new Set();const n=[0,0,0,0,0,0,0,0];for(const g of groups)n[g]=(n[g]||0)+1;const out=new Set();
  const sorted=Object.values(buffs).sort((a,b)=>a.rank-b.rank);
  for(const b of sorted){let ok=true,need7=0;
   if(b.type===1){for(const part of b.config.split('|')){const [g,k]=part.split('#').map(Number);if(n[g]>k){ok=false;break;}if(n[g]<k)need7+=k-n[g];}}
   else if(b.type===2){const hi=n[5]+n[6],lo=n[1]+n[2]+n[3]+n[4];if(hi>3||lo>3)ok=false;if(hi<3)need7+=3-hi;if(lo<3)need7+=3-lo;if(n[1]>1||n[2]>1||n[3]>1||n[4]>1)ok=false;}else ok=false;
   if(need7>0&&need7!==n[7])ok=false;if(ok){out.add(b.id);break;}}
  if(n[7]>0){const cos=Object.values(buffs).find(b=>b.type===3);if(cos)out.add(cos.id);}return out;}
 function girlCard(h,cls,fn){const c=btn('gv-gcard '+cls,'',fn);if(typeof portrait==='function')c.append(portrait(h.table_id,72));const top=el('span','gv-gtop');top.append(img(`/assets/factions/${h.group}.png`,'gv-gfac'),el('b','',String(h.lv)));c.append(top);
  const st=el('span','gv-gstar',h.stars>=10?String(h.stars-10||''):'★'.repeat(Math.min(5,h.stars)));if(h.stars>=10)st.classList.add('wing');c.append(st);c.title=h.name;return c;}
 function teamPick(st,info){loadFormationData();const w=overlay(st,'Battle','gv-teamwin gv-formation');const by=new Map((state.roster||[]).map(h=>[h.partner_id,h]));
  w.querySelector('.gv-winhead').prepend(btn('gv-round gv-info','!',()=>{modal=helpModal;render();}));
  const head=el('div','gv-fhead');const pw=team.reduce((a,p)=>a+(powers?.[String(p)]||0),0);const power=el('div','gv-power');power.append(el('i','','⚔'),el('b','',powers?number(pw):'…'));
  const sk=btn('gv-toggle'+(skipReplay?' on':''),'',()=>{skipReplay=!skipReplay;try{localStorage.setItem('gxb2.galaxy.skip',skipReplay?'1':'0');}catch{}render();});sk.append(el('span','gv-check',skipReplay?'✓':''),el('b','','Skip'));
  const pet=state.home_systems?.selected_pet;const sv=btn('gv-toggle gv-servant','',()=>{note=pet?`Servant ${pet} accompanies the team (change in Servant).`:"No Servant selected (Home → Servant).";render();});sv.append(el('span','','🐾'),el('b','','Servant'));
  head.append(power,sk,sv);w.append(head);
  const lines=el('div','gv-lines');for(const [label,slots,cls] of [['Front',[0,1],'front'],['Back',[2,3,4,5],'back']]){const row=el('div','gv-line');row.append(el('b','gv-linelabel '+cls,label));
   for(const k of slots){const pid=team[k];const h=pid&&by.get(pid);if(h)row.append(girlCard(h,'set',()=>{team=team.filter(x=>x!==pid);render();}));else row.append(el('span','gv-gempty'));}lines.append(row);}w.append(lines);
  const act=activeBuffs(team.map(p=>by.get(p)?.group).filter(Boolean));const brow=el('div','gv-buffrow');
  const list=buffs?Object.values(buffs).sort((a,b)=>(act.has(b.id)-act.has(a.id))||a.id-b.id):[];for(const b of list){const on=act.has(b.id);const i=img(`/assets/group-buff/group_buff_${on?'on':'off'}_${b.id}.png`,'gv-buff'+(on?' on':''));i.title=b.name+': '+b.desc.replace(/\[[^\]]*\]/g,'');brow.append(i);}w.append(brow);
  w.append(btn('gv-go gv-fight','Fight',()=>doFight()));
  const pool=el('div','gv-poolbox');const fac=el('div','gv-facrow');for(let g=1;g<=7;g++){const f=btn('gv-fac'+(faction===g?' on':''),'',()=>{faction=faction===g?0:g;render();});f.append(img(`/assets/factions/${g}.png`));fac.append(f);}pool.append(fac);
  const grid=el('div','gv-ggrid');for(const h of [...(state.roster||[])].filter(h=>!faction||h.group===faction).sort((a,b)=>b.lv-a.lv||b.stars-a.stars)){const on=team.includes(h.partner_id);grid.append(girlCard(h,on?'picked':'',()=>{if(on)team=team.filter(x=>x!==h.partner_id);else if(team.length<6)team.push(h.partner_id);render();}));}
  pool.append(grid);w.append(pool);}
 async function doFight(){if(!team.length){note="Choose at least one Girl";render();return;}const req={action:'fight',team:team.map((p,i)=>({partner_id:p,pos:i+1}))};const hole=panel==='hole';
  if(hole){if(sel?.pirate!=null)req.pirate=sel.pirate;else req.level=tyrantLv;req.map=999;}else{req.map=mapId;req.cell=sel.c.a;}
  modal=null;const r=await act(req);if(!r)return;const label=r.win?"Victory":"Defeat";
  if(!skipReplay&&r.report&&typeof watchEventBattle==='function')await watchEventBattle({report:r.report,rewards:r.got||{}},'galaxy','Galaxy Voyage');else CampaignUI.result(r.win,r.got||{},{event:true,label:'Galaxy Voyage · '+label,report:r.report});render();}
 function progressModal(st,info){const m=info.maps[String(mapId)];const w=overlay(st,'Current Progress');w.append(el('p','gv-big',m.progress+'%'));
  const r=el('div','gv-req');r.append(el('b','','Requirement:'),el('span',m.req.ruler?'ok':'',`Defeat Boss (${m.req.ruler?1:0}/1)`),el('span',m.req.crates[0]>=m.req.crates[1]?'ok':'',`Supply Crates Discovered (${m.req.crates[0]}/${m.req.crates[1]})`),el('span',m.req.end?'ok':'',`Connect Entrance and Exit (${m.req.end?1:0}/1)`));w.append(r);
  w.append(el('p','gv-hint',"From 30% progress, each explored area reduces the Ruler's HP and Attack by 1% (up to 40%)."));}
 function buffModal(st,info){const m=info.maps[String(mapId)];const w=overlay(st,'Battle Buffs');for(const b of m.buffs)w.append(el('p','',`Mystery Planet buff · skill ${b}`));w.append(el('p','gv-hint',"Only applies in battles within this system."));}
 // System of Eternity: Galaxy Tyrant (capture 08) and Space Pirates.
 function holeView(st,info){st.classList.add('gv-mapstage');st.style.backgroundImage=`url('${A(info.hole.bg+'.webp')}')`;top(st,info.hole.name,[chip('397',info.points)]);
  const m=info.maps['999'];if(!m){st.append(el('p','gv-note',"Loading…"));return;}
  const W=m.w,H=m.h;const grid=el('div','gv-grid gv-holegrid');grid.style.setProperty('--w',W);grid.style.setProperty('--h',H);
  const anchor=m.cells.findIndex(c=>c&&c.t===12);if(anchor>=0){const r=Math.floor(anchor/W),c0=anchor%W;const b=btn('gv-cell gv-tyrant','',()=>{sel=null;tyrantLv=Math.min(info.boss.max,Math.max(1,tyrantLv));modal=tyrantModal;render();});b.style.gridColumn=`${c0+1} / span 3`;b.style.gridRow=`${H-r-2} / span 3`;b.append(img(A('galaxy_trip_icon_12.png'),'gv-ev'));grid.append(b);}
  for(const p of info.pirates){if(p.done)continue;const r=Math.floor(p.cell/W),c0=p.cell%W;const b=btn('gv-cell gv-pirate','',()=>{sel={pirate:p.cell};modal=pirateModal;render();});b.style.gridColumn=`${c0+1}`;b.style.gridRow=`${H-r}`;b.append(img(A('galaxy_trip_icon_11.png'),'gv-ev'));const t=el('small','gv-exp');t.dataset.end=p.expire;t.textContent=hms(p.expire-now());b.append(t);grid.append(b);}
  const wrap=el('div','gv-gridwrap');wrap.append(grid);st.append(wrap);
  const bottom=el('div','gv-bottom');const ret=btn('gv-imgbtn big','',()=>{panel='main';render();});ret.append(img(A('galaxy_trip_btn_fh.png')),el('b','','Return'));const tm=btn('gv-imgbtn big','',()=>{panel='team';teamEdit=info.teams.map(t=>[...t.members]);render();});tm.append(img(A('galaxy_trip_btn_bd.png')),el('b','','Team'));bottom.append(ret,tm);st.append(bottom);}
 function tyrantModal(st,info){const t=info.types['12'];const w=overlay(st,t.name,'gv-event');const lv=info.boss.levels[tyrantLv-1];
  const body=el('div','gv-enterbody');body.append(img(A(t.big+'.png'),'gv-bigev'));const d=el('p','gv-diary');d.append(el('span','',t.intro),el('i','','---Voyager\'s Diary'));body.append(d);w.append(body);
  const en=el('div','gv-awards');en.append(el('b','','Enemy Details'));const et=el('div','gv-tiles');for(const u of lv.enemy||[]){const s=el('span','gv-emini');if(typeof portrait==='function')s.append(portrait(u.table_id,64));s.append(el('small','',String(u.lv)));et.append(s);}en.append(et);w.append(en);
  const aw=el('div','gv-awards');aw.append(el('b','','Exploration Reward'));const tl=el('div','gv-tiles');tl.append(tile('397',lv.points));for(const [k,n] of Object.entries(lv.awards))tl.append(tile(k,n));aw.append(tl);if(info.boss.paid.includes(tyrantLv))aw.append(el('small','gv-hint',"This level's reward has already been claimed this season"));w.append(aw);
  const row=el('div','gv-diff');row.append(el('b','gv-choose','Choose Difficulty'));const ctl=el('div','gv-diffctl');ctl.append(btn('gv-pm','−',()=>{tyrantLv=Math.max(1,tyrantLv-1);render();}),el('span','gv-lv',String(tyrantLv)),btn('gv-pm','+',()=>{tyrantLv=Math.min(info.boss.max,tyrantLv+1);render();}));row.append(ctl);w.append(row);
  w.append(el('p','gv-hint',`Maximum level disponible: ${info.boss.max}/${info.boss.top}. Defeat it in a single attempt.`));w.append(btn('gv-go','Challenge',()=>{modal=teamPick;render();}));}
 function pirateModal(st,info){const t=info.types['11'];const w=overlay(st,t.name,'gv-event');const body=el('div','gv-enterbody');body.append(img(A(t.big+'.png'),'gv-bigev'),el('p','gv-diary',t.intro));w.append(body);
  const ev=info.events['11001'];const tl=el('div','gv-tiles');tl.append(tile('397',ev.points));for(const [k,n] of Object.entries(ev.awards))tl.append(tile(k,n));w.append(tl);w.append(el('p','gv-hint',"One attempt. They leave after 72 hours."));w.append(btn('gv-go','Challenge',()=>{modal=teamPick;render();}));}
 // GalaxyTripFormationWindow: 3 Voyage Teams; the sum of (stars - 10) sets each bonus tier.
 function teamView(st,info){top(st,'Team Setup');const by=new Map((state.roster||[]).map(h=>[h.partner_id,h]));
  info.teams.forEach((t,i)=>{const box=el('div','gv-teambox');const members=teamEdit?.[i]||[];const total=members.reduce((a,p)=>a+Math.max(0,(by.get(p)?.stars||0)-10),0);
   const tier=[...info.team_tiers].filter(r=>r.type===i+1&&total>=r.star_limit).pop();const pct=v=>Math.round(Number(v||0)*100)+'%';let text=t.text||'';if(tier){const [a,b]=i===0?[pct(tier.hpP),pct(tier.atkP)]:i===1?[pct(tier.explore_time_cut),String(tier.explore_place_add||0)]:[pct(tier.award1_add),pct(tier.award2_add)];text=text.replace('{1}',a).replace('{2}',b);}
   box.append(el('b','',`Team ${i+1} · Limit Break ${total}`),el('p','gv-hint',tier?text:"No bonus (total Limit Break < 5)"));
   const row=el('div','gv-slots');for(let k=0;k<6;k++){const pid=members[k];const s=btn('gv-slot','',()=>{if(pid){teamEdit[i]=members.filter(x=>x!==pid);render();}});if(pid&&by.get(pid)&&typeof portrait==='function')s.append(portrait(by.get(pid).table_id,52));row.append(s);}box.append(row);
   box.append(btn('gv-small',"+ Add",()=>{sel={team:i};modal=teamAdd;render();}));st.append(box);});
  st.append(btn('gv-go gv-save','Save Team',async()=>{const r=await act({action:'teams',teams:teamEdit});if(r){note='Saved';panel='main';render();}}));}
 function teamAdd(st,info){const i=sel.team;const w=overlay(st,`Team ${i+1}`,'gv-teamwin');const used=new Set(teamEdit.flat());const pool=el('div','gv-pool');
  for(const h of [...(state.roster||[])].filter(h=>h.stars>10||teamEdit[i].includes(h.partner_id)).sort((a,b)=>b.stars-a.stars)){const on=teamEdit[i].includes(h.partner_id);const busy=used.has(h.partner_id)&&!on;const c=btn('gv-cand'+(on?' on':'')+(busy?' busy':''),'',()=>{if(busy)return;if(on)teamEdit[i]=teamEdit[i].filter(x=>x!==h.partner_id);else if(teamEdit[i].length<6)teamEdit[i].push(h.partner_id);render();});if(typeof portrait==='function')c.append(portrait(h.table_id,52));c.append(el('small','',`${h.stars}★ (+${h.stars-10})`));pool.append(c);}
  if(!pool.children.length)w.append(el('p','gv-hint',"Only Girls above 10★ count."));w.append(pool);}
 // GalaxyBattlePassWindow (free track) + Tasks.
 function passView(st,info){top(st,'Voyager Passport',[chip('397',info.points)]);const tabs=el('div','gv-tabs');['Passport','Tasks'].forEach((t,i)=>tabs.append(btn('gv-tab'+(tab===i?' on':''),t,()=>{tab=i;render();})));st.append(tabs);const list=el('div','gv-list');st.append(list);
  if(tab===0){list.append(el('p','gv-hint',"The paid reward track is unavailable without a server."));for(const p of info.pass){const row=el('div','gv-row'+(p.claimed?' done':''));row.append(el('b','gv-need',String(p.need)));const f=el('div','gv-tiles');for(const [k,n] of Object.entries(p.free))f.append(tile(k,n));const pay=el('div','gv-tiles locked');for(const [k,n] of Object.entries(p.pay))pay.append(tile(k,n));
    const b=btn(p.claimed?'gv-small':'gv-go gv-mini',p.claimed?'✓':'Claim',async()=>{const r=await act({action:'claim_pass',id:p.id});if(r?.got)CampaignUI.popup('Voyager Passport',r.got);});b.disabled=p.claimed||info.points<p.need;row.append(f,pay,b);list.append(row);}}
  else for(const t of [...info.tasks].sort((a,b)=>(b.claimable-a.claimable)||(a.claimed-b.claimed)||a.id-b.id)){const row=el('div','gv-row'+(t.claimed?' done':''));const tx=el('div','gv-ttext');tx.append(el('span','',t.text),el('em','',` (${Math.min(t.value,t.need)}/${t.need})`));row.append(tx,tile('397',t.points));
   const b=btn(t.claimable?'gv-go gv-mini':'gv-small',t.claimed?'✓':t.claimable?'Claim':'—',async()=>{const r=await act({action:'claim_task',id:t.id});if(r?.got)CampaignUI.popup('Tasks',r.got);});b.disabled=!t.claimable;row.append(b);list.append(row);}}
 function shopView(st,info){top(st,'Shop',[chip('398',info.stones)]);const tabs=el('div','gv-tabs');['Season','Permanent'].forEach((t,i)=>tabs.append(btn('gv-tab'+(tab===i?' on':''),t,()=>{tab=i;render();})));st.append(tabs);
  const grid=el('div','gv-shop');const rows=tab===0?info.store.season:info.store.permanent;
  for(const r of rows){const [k,n]=String(r.item).split('#');const [ck,cn]=String(r.cost).split('#');const c=el('div','gv-good'+(r.ok?'':' locked'));c.append(tile(k,Number(n)),el('small','',itemCatalog?.[k]?.name||''),el('small','gv-left',`${r.buy_limit-r.bought}/${r.buy_limit}`));
   if(!r.ok){const [ns,np]=String(r.trip_limit||'').split('|');c.append(el('small','gv-lock',tab===0?`Obtain ${r.point_limit} Exploration Points in this season`:`Obtain ${np} Exploration Points in ${ns} season(s)`));}
   const b=btn('gv-go gv-mini','',async()=>{const res=await act({action:'store',store:tab===0?1:2,id:r.id});if(res?.got)CampaignUI.popup('Shop',res.got);});b.append(chip(ck,Number(cn)));b.disabled=!r.ok||r.bought>=r.buy_limit;c.append(b);grid.append(c);}
  st.append(grid);}
 return {open,render};
})();
