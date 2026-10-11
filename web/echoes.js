'use strict';
// Echoes of Time (TimeCloisterMainWindow → TimeCloisterProbeWindow / TechWindow / BattleWindow / AchievementWindow).
// Rules: gxb2/echoes.py. Layout from docs/references/2026-09-29-e/03 (world clock) and 2026-09-29-f (board, decks,
// Planetarium, tech tree, achievements). Art: time_cloister_* sprites (turntable, cards, buttons, tec nodes).
const Echoes=(()=>{
 let textBox=null;
 function say(title,text){textBox={title,text,back:panel};panel='text';render();}
 let origin='league',panel=null,note='',busyLocal=false,detail=null,world=1,pick=[],pickFor=null,tecGroup=1,tecSel=null,timer=null,skipReplay=false;
 const A=n=>'/assets/echoes/'+n+'.png';
 const ROMAN=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII'];
 const ATTR=[['Courage','#e0763a'],['Charisma','#3aa35b'],['Knowledge','#3b7fd1']];
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const btn=(cls,text,fn)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
 try{skipReplay=localStorage.getItem('gxb2.echoes.skip')==='1';}catch{}
 function root(){let r=$('echoes-view');if(!r){r=el('section','echoes-view');r.id='echoes-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from){origin=from||view;panel=null;note='';detail=null;showView('echoes');act({action:'open',world:state.echoes_info?.obs?.world||world});}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';if(['287','288','289','307','337'].includes(id)&&id!=='307')return A('icon_'+id);const row=itemCatalog?.[id];return (row&&itemPicture(row))||(row?.icon?'/assets/shops/items/'+row.icon+'.png':'');}
 function chip(k,n){const c=el('span','ec-chip');const s=icon(k);if(s)c.append(img(s));c.append(el('b','',typeof n==='string'?n:number(n)));return c;}
 async function act(req){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/echoes/action',{world,...req});state=r.state;if(r.detail){detail=r.detail;world=r.detail.world;}return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;if(view==='echoes')render();}}
 let loadedAt=performance.now();const now=()=>(state.server_time||0)+Math.floor((performance.now()-loadedAt)/1000);
 const hms=s=>{s=Math.max(0,Math.floor(s));return [Math.floor(s/3600),Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');};
 const W=()=>state.echoes_info?.worlds.find(w=>w.id===world);
 function attrs(vals,green){const w=el('div','ec-attrs');ATTR.forEach(([n,c],i)=>{const a=el('span','ec-attr');a.title=n;a.append(el('i','',''),el('b','',String(vals[i]-(green||0))));a.querySelector('i').style.background=c;if(green)a.append(el('em','','+'+green));w.append(a);});return w;}
 function obsLeft(o){return Math.max(0,o.left-(o.ended?0:Math.floor((performance.now()-loadedAt)/1000)));}
 const chibis=new Map();
 function chibi(tableId){const key=String(tableId);if(chibis.has(key))return chibis.get(key).cloneNode(true);const h=el('div','ec-chibi');api('/assets/chibis/catalog.json').then(c=>{const m=c[key];if(m)GxbSpine.snapshot(h,'/assets/chibis/'+m.model,{width:260,height:260,fit:.85,y:.6,className:'ec-chibi-img',sequence:[['idle',true]]}).then(()=>{const im=h.querySelector('img');if(im)chibis.set(key,im.cloneNode(true));});}).catch(()=>{});return h;}
 function render(){const r=root();if(view!=='echoes'){clearInterval(timer);timer=null;return;}loadedAt=performance.now();const info=state.echoes_info;r.replaceChildren();const st=el('div','ec-stage');r.append(st);
  const back=btn('ec-back','',()=>{if(panel){panel=null;render();return;}showView(origin==='echoes'?'league':origin);});back.append(img('/assets/ui/win_back_btn.png'));
  const top=el('div','ec-top');top.append(back,btn('ec-round','?',()=>say('Echoes of Time',(info?.help||[]).join('\n\n').replaceAll('|','\n'))));st.append(top);
  if(!info){st.append(el('p','ec-note',"Loading…"));return;}
  if(!info.unlocked){st.append(el('p','ec-note ec-box',`Echoes of Time unlocks after clearing stage ${info.unlock_stage}.`));return;}
  const o=info.obs;
  if(o&&o.world===world&&panel!=='clock')board(st,info,o);else clock(st,info,o);
  if(note)st.append(el('p','ec-note ec-err',note));
  if(panel==='tec')planetarium(st,info);else if(panel==='stages')stages(st,info);else if(panel==='ach')achievements(st);else if(panel==='pick')picker(st);else if(panel&&panel.startsWith('deck'))deck(st,Number(panel.slice(4)));else if(panel==='record')record(st,o);else if(panel==='speed')speed(st,info,o);else if(panel==='text'&&textBox){const w=overlay(st,textBox.title);w.classList.add('ec-textwin');w.append(el('p','ec-text',textBox.text));w.querySelector('.ec-close').onclick=()=>{panel=textBox.back;render();};}
  clearInterval(timer);timer=setInterval(tick,1000);tick();}
 function tick(){if(view!=='echoes'){clearInterval(timer);return;}const o=state.echoes_info?.obs;if(!o)return;const left=obsLeft(o);root().querySelectorAll('.ec-left').forEach(e=>e.textContent=o.ended?'Observation ended':(o.world===world?'Observing… ':'')+hms(left));
  const el2=root().querySelector('.ec-next');if(el2&&!o.ended){const n=o.next_card-Math.floor((performance.now()-loadedAt)/1000);el2.textContent='Next card '+hms(n);if(n<=0||left<=0){clearInterval(timer);act({action:'open'});}}}
 // TimeCloisterMainWindow: turntable with the Worlds of Time (I–VI), Achievements, Stages, Progress and Continue.
 function clock(st,info,o){const w=W();const main=el('div','ec-main');main.style.backgroundImage=`url('${A('time_cloister_main_bg_1')}')`;
  const dial=el('div','ec-dial');dial.append(img(A('time_cloister_turntable'),'ec-plate'));
  for(let i=1;i<=6;i++){const row=info.worlds.find(x=>x.id===i);const a=180-(i-1)*60;const s=btn('ec-seg'+(i===world?' on':'')+(row?.open?'':' locked'),'',()=>{if(!row)return;world=i;panel=null;act({action:'detail',world:i});});
   s.style.setProperty('--a',a+'deg');const n=img(A(`time_cloister_${i}_${i===world?1:0}`),'ec-num');s.append(n);if(!row||!row.open)s.append(img(A('time_cloister_lock'),'ec-lock'));s.title=row?row.name:'Coming soon';dial.append(s);}
  dial.append(img(A('time_cloister_energy'),'ec-hub'));main.append(dial);
  const card=el('div','ec-info');card.append(el('h2','',w?.name||''),el('p','',w?.desc||''));
  const row=el('div','ec-row');const ach=btn('ec-icon','',()=>{panel='ach';render();});ach.append(img(A('time_cloister_btn_ach')),el('b','','Achievements'));const stg=btn('ec-icon','',()=>{panel='stages';render();});stg.append(img(A('time_cloister_btn_battle')),el('b','','Stages'));
  const mid=el('div','ec-mid');mid.append(el('small','ec-prog',`Progress:${detail?.progress??w?.progress??0} %`));
  if(!w?.open)mid.append(el('p','ec-note',"Reach 85% progress in the previous world to unlock this one."));
  else if(o&&o.world!==world)mid.append(el('p','ec-note',`An observation is in progress in ${info.worlds.find(x=>x.id===o.world)?.name}.`),btn('ec-go','Continue',()=>{world=o.world;panel=null;act({action:'detail',world});}));
  else if(o){mid.append(btn('ec-go','Continue',()=>{panel=null;render();}));const t=el('div','ec-timer');t.append(el('b','ec-left',''),btn('ec-x','✕',async()=>{if(confirm("Finish observation now?"))await act({action:'stop'});}));mid.append(t);}
  else mid.append(btn('ec-go','Observe',()=>{pickFor='obs';pick=(o?.partners)||[];panel='pick';render();}));
  row.append(ach,mid,stg);card.append(row);main.append(card);
  const tec=btn('ec-tec ec-tec-main','',()=>{panel='tec';render();});tec.append(img(A('time_cloister_btn_tec')),el('b','','Planetarium'));main.append(tec);st.append(main);}
 // TimeCloisterProbeWindow: board of triggered cards, I–XII bar, decks, Record, Planetarium and the team's attributes.
 function board(st,info,o){const w=W();const b=el('div','ec-board');b.style.backgroundImage=`url('${A('time_cloister_bg_1')}')`;
  const head=el('div','ec-bhead');const en=el('div','ec-energy');en.append(img(A('time_cloister_energy')),el('b','',`${Math.ceil(obsLeft(o)/info.energy_time)}/${o.clockwork}`));en.title='Clockwork of Memory';
  const title=el('div','ec-title');title.append(btn('ec-name',w?.name||'',()=>{panel='clock';render();}),el('small','ec-left',''));head.append(en,title);
  const sp=btn('ec-speed','',()=>{panel='speed';render();});sp.append(img(A('time_cloister_btn_speed_up')));sp.title='Speed Up';sp.disabled=o.ended;head.append(sp);b.append(head);
  const total=o.clockwork*info.energy_time,done=o.clockwork*info.energy_time-obsLeft(o);const lit=Math.min(12,Math.ceil(total/3600));const cur=Math.min(11,Math.floor(done/3600));
  const bar=el('div','ec-hours');ROMAN.forEach((n,i)=>bar.append(el('span',(i<lit?'lit':'')+(i<=cur&&i<lit?' past':''),n)));b.append(bar);
  const grid=el('div','ec-cards');const shown=o.cards.slice(-11);for(let i=0;i<12;i++){const slot=el('div','ec-slot');const c=shown[i-(i>1?1:0)];
   if(i===1){slot.classList.add('walker');const who=(state.roster||[]).find(h=>h.partner_id===o.partners[0]);if(who)slot.append(chibi(who.table_id));slot.append(el('small','ec-next',''));}
   else if(c)slot.append(cardFace(c));else slot.append(img(A('time_cloister_card'),'ec-back'));grid.append(slot);}
  b.append(grid);
  const decks=el('div','ec-decks');[[1,'supply','Supply Card'],[2,'challenge','Challenge Card'],[3,'event','Encounter Card']].forEach(([k,n,label])=>{const d=btn('ec-deck','',()=>{panel='deck'+k;render();});d.append(img(A('time_cloister_btn_'+n)),el('b','',label));decks.append(d);});
  const rec=btn('ec-record','',()=>{panel='record';render();});rec.append(img(A('time_cloister_btn_record')),el('b','',`Record (${o.cards.length})`));decks.append(rec);b.append(decks);
  const foot=el('div','ec-foot');const tec=btn('ec-tec','',async()=>{panel='tec';render();});tec.append(img(A('time_cloister_btn_tec')),el('b','','Planetarium'));
  const team=el('div','ec-team');team.append(attrs(o.attrs,o.green));const faces=el('div','ec-faces');for(const pid of o.partners){const h=(state.roster||[]).find(x=>x.partner_id===pid);if(h&&typeof portrait==='function')faces.append(portrait(h.table_id,56));}team.append(faces);foot.append(tec,team);b.append(foot);
  const end=el('div','ec-endrow');if(o.ended)end.append(btn('ec-go','Claim',claim));else end.append(btn('ec-small','End Observation',async()=>{if(confirm("Finish observation now? You can claim rewards already earned."))await act({action:'stop'});}));b.append(end);st.append(b);}
 async function claim(){const r=await act({action:'claim'});if(r?.got)CampaignUI.popup(`Observation complete · ${r.cards} cards · ${r.points} points`,r.got);}
 function cardFace(c){const f=el('div','ec-face t'+c.type);const lv=c.level>1?'_level_'+Math.min(3,c.level):'';f.append(img(A('time_cloister_card_bg'+(c.type===1?lv:'')),'ec-fbg'),img(A(c.img),'ec-fimg'),el('b','ec-fname',c.name));f.title=c.name+'\n'+c.desc;f.onclick=e=>{e.stopPropagation();say(c.name,c.desc);};return f;}
 function overlay(st,title,cls){const ov=el('div','ec-overlay');ov.onclick=e=>{if(e.target===ov){panel=null;render();}};const w=el('div','ec-win '+(cls||''));w.append(el('h2','',title),btn('ec-close','✕',()=>{panel=null;render();}));ov.append(w);st.append(ov);return w;}
 // TimeCloisterCardPreivewWindow: every card of this World for Supply (1) / Challenge (2) / Encounter (3,6,7).
 function deck(st,k){const w=overlay(st,['','Supply Cards','Challenge Cards','Encounter Cards'][k]);const cards=(detail?.cards||[]).filter(c=>k===1?c.type===1:k===2?c.type===2:[3,6,7].includes(c.type));
  if(!cards.length)w.append(el('p','ec-note',"Loading…"));const list=el('div','ec-list');for(const c of cards){const row=el('div','ec-crow'+(c.unlocked?'':' locked'));row.append(cardFace(c));const t=el('div','');t.append(el('b','',c.name),el('p','',c.desc));if(c.base)t.append(attrs(c.base));if(!c.unlocked)t.append(el('small','ec-lockt',c.unlock||"Locked: upgrade the Planetarium"));row.append(t);list.append(row);}w.append(list);}
 function record(st,o){const w=overlay(st,'Record');if(!o)return;const list=el('div','ec-list');[...o.cards].reverse().forEach(c=>{const row=el('div','ec-crow');row.append(cardFace(c));const t=el('div','');t.append(el('b','',c.name),el('p','',c.desc));row.append(t);list.append(row);});if(!o.cards.length)list.append(el('p','ec-note',"No cards have been activated yet (1 every 5 min)."));w.append(list);}
 function speed(st,info,o){const w=overlay(st,'Speed Up');w.append(el('p','',`Each Time Essence advances ${info.essence_s/60} min (also consumes the corresponding Memory Clockwork).`));w.append(chip('287',info.essence));
  const max=Math.max(1,Math.min(info.essence,Math.ceil(obsLeft(o)/info.essence_s)));let n=Math.min(1,max);const inp=el('input','ec-num-in');inp.type='number';inp.min=1;inp.max=max;inp.value=n;w.append(inp);
  w.append(btn('ec-go','Use',async()=>{n=Math.max(1,Math.min(max,Number(inp.value)||1));panel=null;await act({action:'speed',count:n});}));}
 // TimeCloisterTechWindow: Planetarium I / II; nodes at the table xy, lines to their prerequisites.
 function planetarium(st,info){const w=overlay(st,'Planetarium','ec-tecwin');w.style.backgroundImage=`url('${A('time_cloister_bg_5')}')`;const tabs=el('div','ec-tabs');[1,2].forEach(g=>tabs.append(btn('ec-tab'+(g===tecGroup?' on':''),'Technology '+ROMAN[g-1],()=>{tecGroup=g;tecSel=null;render();})));w.append(tabs);
  if(!detail){w.append(el('p','ec-note',"Loading…"));return;}const nodes=detail.tecs.filter(t=>t.group===tecGroup);const xs=nodes.map(t=>t.xy[0]),ys=nodes.map(t=>t.xy[1]);const x0=Math.min(...xs)-60,x1=Math.max(...xs)+60,y0=Math.min(...ys)-60,y1=Math.max(...ys)+60;
  const map=el('div','ec-tree');const P=t=>[(t.xy[0]-x0)/(x1-x0)*100,(y1-t.xy[1])/(y1-y0)*100];const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 100 100');svg.setAttribute('preserveAspectRatio','none');
  const byId=new Map(detail.tecs.map(t=>[t.id,t]));for(const t of nodes)for(const p of t.pre){const q=byId.get(p);if(!q||q.group!==t.group)continue;const [a,b]=P(t),[c,d]=P(q);const l=document.createElementNS('http://www.w3.org/2000/svg','line');l.setAttribute('x1',a);l.setAttribute('y1',b);l.setAttribute('x2',c);l.setAttribute('y2',d);l.setAttribute('class',q.lv>0?'on':'');svg.append(l);}
  map.append(svg);for(const t of nodes){const [x,y]=P(t);const s=t.lv>0?1:!t.why||t.why==="Maximum level"?2:3;const n=btn('ec-node s'+s+(tecSel===t.id?' sel':''),'',()=>{tecSel=t.id;render();});n.style.left=x+'%';n.style.top=y+'%';n.append(img(A('time_cloister_tec_bg_'+s),'ec-nbg'),img(A(t.img+'_'+s),'ec-nimg'));if(t.lv)n.append(el('small','',`${t.lv}/${t.max}`));n.title=t.name;map.append(n);}
  w.append(map);const shard=W()?.shard;w.append(chip(String(shard),W()?.shards||0));
  const t=detail.tecs.find(x=>x.id===tecSel);if(t){const d=el('div','ec-tecd');d.append(el('b','',`${t.name} (${t.lv}/${t.max})`),el('p','',t.desc));if(t.why&&t.why!=="Maximum level")d.append(el('small','ec-lockt',t.unlock||t.why));
   if(t.cost){const c=el('div','ec-cost');for(const [k,n] of Object.entries(t.cost))c.append(chip(k,n));const up=btn('ec-go','Upgrade',async()=>{await act({action:'upgrade',tec:t.id});});up.disabled=!!t.why;c.append(up);d.append(c);}
   if(state.echoes_info?.obs)d.append(el('small','',"Upgrades made during an observation take effect in the next one."));w.append(d);}
  else w.append(el('p','ec-hint',`Use 「Time Shard: ${W()?.name}」 to upgrade the Planetarium in Echoes of Time.`));}
 // TimeCloisterBattleWindow: 10 Stages with attribute references + Time Vortex (damage record).
 function stages(st,info){const w=overlay(st,'Checkpoint: '+(W()?.name||''));w.append(el('div','ec-chips'));w.lastChild.append(chip('289',`${info.chips}/${info.chip_max}`));if(info.chips<info.chip_max)w.lastChild.append(el('small','ec-left2',"+1 every 30 min"));
  if(!detail){w.append(el('p','ec-note',"Loading…"));return;}const list=el('div','ec-list');
  for(const s of [...detail.stages].sort((a,b)=>b.special-a.special)){const row=el('div','ec-srow'+(s.open?'':' locked')+(s.special?' vortex':''));const t=el('div','');t.append(el('b','',s.special?'Time Vortex':`Stage ${s.n}`));
   if(s.special)t.append(el('small','',`Best damage: ${number(detail.best_damage||0)}`));else{t.append(attrs(s.base));const aw=el('div','ec-aw');for(const [k,n] of Object.entries(s.awards))aw.append(chip(k,n));t.append(aw);}
   row.append(t);const b=btn('ec-go',s.passed?'Passed':'Battle',()=>{pickFor='stage:'+s.n;pick=[];panel='pick';render();});b.disabled=!s.open||(s.passed&&!s.special)||info.chips<1;row.append(b);if(!s.open)row.title="Clear the previous stage and upgrade Stage Unlock in the Planetarium";list.append(row);}w.append(list);}
 // TimeCloisterAchievementWindow (capture 2026-09-29-g/03): Total Progress = claimed steps; rows with the current step's
 // text (value/need in green), item tiles, and Go / Claim / "Collected" stamp. Claimable first, finished last.
 function achievements(st){const w=overlay(st,'Achievement: '+(W()?.name||''),'ec-achwin');if(!detail){w.append(el('p','ec-note',"Loading…"));return;}
  const head=el('div','ec-achhead');head.append(el('p','','Complete the following achievements by Observing in this World of Time to increase the Observation Progress, a new World of Time will be unlocked once the Observation Progress reaches 85%.'));
  const [d,t]=detail.progress_steps||[0,0];const tp=el('div','ec-achtotal');tp.append(el('b','','Total Progress'),el('span','',`${detail.progress}% (${d}/${t})`));head.append(tp);w.append(head);
  const rank=a=>a.done?-10:a.claimable?10:0;const list=el('div','ec-list');
  for(const a of [...detail.ach].sort((x,y)=>rank(y)-rank(x)||x.id-y.id)){const row=el('div','ec-arow'+(a.done?' done':''));const top=el('div','ec-atext');top.append(el('span','',a.text+' '),el('em','',`(${number(a.value)}/${number(a.need)})`));
   const info=btn('ec-ainfo','!',()=>say(a.text,`Step ${Math.min(a.claimed+1,a.steps)}/${a.steps} · Progress ${number(a.value)}/${number(a.need)}`));top.append(info);row.append(top);
   const bot=el('div','ec-abot');const aw=el('div','ec-tiles');for(const [k,n] of Object.entries(a.awards)){const tile=el('span','ec-tile');const src=icon(k);if(src)tile.append(img(src));tile.append(el('b','',number(n)));aw.append(tile);}bot.append(aw);
   if(a.done)bot.append(img(A('mission_awarded_en_en'),'ec-stamp','Collected'));
   else if(a.claimable)bot.append(btn('ec-go','Claim',async()=>{const r=await act({action:'claim_ach',ach:a.id});if(r?.got)CampaignUI.popup('Achievement',r.got);}));
   else bot.append(btn('ec-gobtn','Go',()=>{if(a.go==='tec'||a.go==='stages'){panel=a.go;render();}else{panel=null;const o=state.echoes_info?.obs;if(o){world=o.world;render();}else{pickFor='obs';pick=[];panel='pick';render();}}}));
   row.append(bot);list.append(row);}w.append(list);}
 // Girl picker for the Observation (attributes) and for Stages (positions 1-6 in order).
 function picker(st){const isObs=pickFor==='obs';const w=overlay(st,isObs?'Send Girls to Observe':'Stage team');const slots=el('div','ec-pslots');for(let i=0;i<6;i++){const pid=pick[i];const h=(state.roster||[]).find(x=>x.partner_id===pid);const s=btn('ec-pslot','',()=>{if(pid){pick=pick.filter(x=>x!==pid);render();}});if(h&&typeof portrait==='function')s.append(portrait(h.table_id,56));slots.append(s);}w.append(slots);
  if(isObs){const lv=pick.reduce((a,p)=>a+((state.roster||[]).find(h=>h.partner_id===p)?.lv||0),0);w.append(el('p','ec-hint',`Green Boost from assigned Girls: +${Math.round(lv/3)} a Courage / Charisma / Knowledge`));}
  const pool=el('div','ec-pool');for(const h of [...(state.roster||[])].sort((a,b)=>b.lv-a.lv||b.stars-a.stars)){const on=pick.includes(h.partner_id);const c=btn('ec-cand'+(on?' on':''),'',()=>{if(on)pick=pick.filter(x=>x!==h.partner_id);else if(pick.length<6)pick.push(h.partner_id);render();});if(typeof portrait==='function')c.append(portrait(h.table_id,52));c.append(el('small','',`Lv.${h.lv}`));c.title=h.name;pool.append(c);}w.append(pool);
  const acts=el('div','ec-acts');acts.append(btn('ec-small','Auto',()=>{pick=[...(state.roster||[])].sort((a,b)=>b.lv-a.lv).slice(0,6).map(h=>h.partner_id);render();}));
  if(!isObs){const sk=el('label','ec-skip');const cb=el('input');cb.type='checkbox';cb.checked=skipReplay;cb.onchange=()=>{skipReplay=cb.checked;try{localStorage.setItem('gxb2.echoes.skip',skipReplay?'1':'0');}catch{}};sk.append(cb,' Skip');acts.append(sk);}
  acts.append(btn('ec-go',isObs?'Observe':'Fight',async()=>{if(!pick.length){note="Choose at least one Girl";render();return;}if(isObs){panel=null;await act({action:'start',partners:pick});return;}
   const n=Number(pickFor.split(':')[1]);panel='stages';const r=await act({action:'fight',stage:n,team:pick.map((p,i)=>({partner_id:p,pos:i+1}))});if(!r)return;const label=n===11||r.damage!==undefined?`Time Vortex · ${number(r.damage||0)} damage`:`Echoes of Time · Stage ${n}`;
   if(!skipReplay&&r.report&&typeof watchEventBattle==='function')await watchEventBattle({report:r.report,rewards:r.got||{}},'echoes',label);else CampaignUI.result(r.win,r.got||{},{event:true,label,report:r.report});}));w.append(acts);}
 return {open,render};
})();
