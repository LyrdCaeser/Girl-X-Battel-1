'use strict';
// Campaign fight flow, as the client plays it (user captures 2026-09-30):
// Fight → BattleFormationWindow ("Battle": power, Servant, Front 2 / Back 4, faction filter, Battle Start) → BattleLoadingWindow
// (a loading picture battle_loading_1-10 with its text art, "Now loading... N%") → the stage story → the Spine `switch` sweep
// (StoryWindow, xyd.Battle.effect_switch) → the battle. Also CampaignStageDetailWindow (tap a stage: Output per 5 s, Loot,
// Auto-Battle) and CampaignHangFormationWindow (tap the idle scene: the 3 hang chibis, 1 front + 2 back). Prefix cf-.
const CampaignFlow=(()=>{
 let loadData=null,campaign=null;
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 const host=()=>window.GxbFrame?.root()||document.body;
 const wait=ms=>new Promise(r=>setTimeout(r,ms));
 const R=n=>'/assets/summon-result/'+n+'.png';
 // --- BattleLoadingWindow -----------------------------------------------------------------------------------------------
 async function loading(work){if(!loadData)loadData=await api('/assets/battle-loading/loading.json').catch(()=>null);
  const n=1+Math.floor(Math.random()*10),o=el('div','cf-loading');const bg=img('/assets/battle-loading/battle_loading_'+n+'.webp','cf-load-bg');o.append(bg);
  const T=k=>loadData?.text?.[k]||'',C=loadData?.colors||{};const tint=(e,k)=>{const c=C[k]?.[n-1];if(c)e.style.setProperty('--c',c);};
  if(n===1)o.append(el('p','cf-load-top',T('BATTLE_TIPS_DESC1').replace(/\[c\]\[\w+\]|\[-\]\[\/c\]|%%/g,m=>m==='%%'?'%':'')));
  else if([3,7,8,9].includes(n)){const g=el('div','cf-load-g1');g.append(img('/assets/battle-loading/battle_loading_'+n+'_en_en.png','cf-load-title'));const l=el('p','cf-load-desc',T('BATTLE_LOADING_'+n));tint(l,'rect');l.style.color=C.label?.[n-1]||'';g.append(l);o.append(g);}
  else{const g=el('div','cf-load-g2 p'+n);g.append(img('/assets/battle-loading/battle_loading_'+n+'_en_en.png','cf-load-title'));const cv=el('span','cf-load-cv',T('BATTLE_LOADING_CV_'+n));tint(cv,'rect');g.append(cv,el('p','cf-load-quote',T('BATTLE_LOADING_'+n)));o.append(g);}
  const bot=el('div','cf-load-bot');const lab=el('b','cf-load-label','Now loading...  0%');const bar=el('div','cf-load-bar');const fill=el('i');bar.append(fill);bot.append(img('/assets/battle-loading/scene_bottom.png','cf-load-fade'),lab,bar);o.append(bot);host().append(o);
  let p=0,done=false;const set=v=>{p=v;fill.style.width=v+'%';lab.textContent='Now loading...  '+Math.floor(v)+'%';};
  const t0=Date.now();const tick=setInterval(()=>{if(!done)set(Math.min(90,p+(90-p)*.08+.6));},60);
  try{const r=await work;await wait(Math.max(0,1100-(Date.now()-t0)));done=true;for(let v=p;v<=100;v+=6){set(Math.min(100,v));await wait(25);}set(100);await wait(180);return r;}
  finally{clearInterval(tick);o.classList.add('out');setTimeout(()=>o.remove(),260);}}
 // --- StoryWindow → battle sweep (Spine `switch`, texiao01; the battle shows 1 s in) --------------------------------------
 function sweep(){return new Promise(res=>{const o=el('div','cf-sweep');host().append(o);let settled=false;const mid=()=>{if(!settled){settled=true;res();}};
  if(typeof GxbSpine==='undefined'){mid();o.remove();return;}
  GxbSpine.mount(o,'/assets/spine/switch',{width:720,height:1280,scale:1.2,origin:[(360+10)/720,.5],sequence:[['texiao01',false]],className:'cf-sweep-canvas'}).then(h=>{const dur=(h.figure.spineData.findAnimation('texiao01')?.duration||2)*1000;setTimeout(mid,Math.min(1000,dur*.5));setTimeout(()=>{h.destroy();o.remove();},dur+50);}).catch(()=>{mid();o.remove();});
  setTimeout(mid,2500);});}
 // --- hero icons (HeroIcon: avatar, hero_frame halves, faction, level, stars) -------------------------------------------
 function heroIcon(h,cls='cf-hero'){const g=girlsCatalog.find(x=>x.id===h.table_id);const w=el('div',cls);const star=Number(h.stars)||g?.stars||1;
  const av=img('/assets/avatar-hd/profile/partner_avatar_'+h.table_id+'.webp?v=1.1.2','cf-av');av.onerror=()=>{const a2=typeof artId==='function'?artId(h.table_id):h.table_id;if(av.dataset.f){av.onerror=null;av.src='/assets/cards/partner_card_'+a2+'.png';return;}av.dataset.f=1;av.src='/assets/avatar-hd/profile/partner_avatar_'+a2+'.webp?v=1.1.2';};
  w.append(av,img(R('hero_frame'),'cf-frame l'),img(R('hero_frame'),'cf-frame r'));
  if(g?.group){const b=el('span','cf-group');b.append(img(R('img_group'+g.group)));w.append(b);}
  w.append(el('b','cf-lv',String(h.lv||1)));
  // Use the SAME original star artwork/Limit Break emblem as the Girl detail,
  // instead of truncating every 9–25★ girl to four red stars (= false 9★).
  const st=el('span','cf-stars'+(star>5?' red':''));
  if(typeof GirlUI!=='undefined')st.append(GirlUI.stars(star,'card'));
  else if(star>=10)st.append(el('b','cf-star-count',star+'★'));
  else for(let i=0;i<(star>5?star-5:star);i++)st.append(img(R(star>5?'star_red':'star')));
  st.setAttribute('aria-label',star+'★');st.title=star+'★';w.append(st);
  w.title=(h.name||g?.name||'')+' · '+star+'★';return w;}
 let servants=null;
 // BattleFormationWindow → Servant: choose the Servant that fights with the team (home_systems.selected_pet), or none.
 async function pickServant(){if(!servants)servants=await api('/assets/servants.json').catch(()=>({pets:{}}));const hs=state.home_systems||{};
  return new Promise(res=>{const {body,close,win}=GirlUI.win({title:'Servant',cls:'cf-sv',stack:true});const grid=el('div','cf-sv-grid');
   const choose=async id=>{try{const r=await api('/api/home/action',{action:'pet_select',id});state=r.state;}catch(e){GirlUI.toast(e.message);}close();res();};
   for(const p of Object.values(servants.pets).sort((a,b)=>a.id-b.id)){const mine=hs.pets?.[String(p.id)];const c=btn('cf-sv-card'+(mine?'':' locked')+(hs.selected_pet===p.id?' on':''),'',()=>mine?choose(p.id):GirlUI.toast("You do not own "+p.name+" (Menu → Servant)."));
    c.append(img('/assets/servant/'+p.avatar+Math.min(4,mine?.grade||1)+'.png'),el('b','',p.name),el('small','',mine?'Lv. '+(mine.lv||1):'🔒'));grid.append(c);}
   body.append(grid);if(hs.selected_pet)body.append(btn('gs-btn white',"No Servant",()=>choose(0)));
   const obs=new MutationObserver(()=>{if(!win.isConnected){obs.disconnect();res();}});obs.observe(document.body,{childList:true,subtree:true});});}
 let powers={};const power=h=>Number(powers[h.partner_id]||0);
 // Shared picker: `slots` = positions offered ([1..6] battle, [1..3] hang), `front` = how many of them are front row.
 function picker({title,slots,front,initial,confirm,note,servant}){return new Promise(res=>{const {body,close,win}=GirlUI.win({title,cls:'cf-form'});let finished=false;
   const pick=new Map();for(const f of initial||[]){if(slots.includes(f.pos)&&state.roster.some(h=>h.partner_id===f.partner_id))pick.set(f.pos,f.partner_id);}let faction=0;
   const top=el('div','cf-form-top');const grid=el('div','cf-form-grid');const filter=el('div','cf-form-filter');
   const draw=()=>{top.replaceChildren();const pw=el('div','cf-power');pw.append(img('/assets/campaign/arena_sword.png','cf-power-icon'),el('b','',number([...pick.values()].reduce((a,id)=>a+power(state.roster.find(h=>h.partner_id===id)||{}),0))));
     if(servant){const cur=state.home_systems?.selected_pet;const sb=btn('gs-btn cf-servant','',()=>pickServant().then(draw));if(cur&&servants?.pets?.[cur]){const g=state.home_systems.pets[String(cur)]?.grade||1;sb.append(img('/assets/servant/'+servants.pets[cur].avatar+Math.min(4,g)+'.png','cf-sv-mini'));}sb.append(el('span','','🐾 Servant'));pw.append(sb);}top.append(pw);
     for(const [label,pos] of [['Front',slots.slice(0,front)],['Back',slots.slice(front)]]){const row=el('div','cf-row');row.append(el('span','cf-row-label',label));
      for(const p of pos){const slot=el('button','cf-slot');slot.type='button';const id=pick.get(p);const h=id&&state.roster.find(x=>x.partner_id===id);if(h){slot.append(heroIcon(h));slot.onclick=()=>{pick.delete(p);draw();};}row.append(slot);}top.append(row);}
     if(note)top.append(el('p','cf-note',note));
     top.append(btn('gs-btn cf-start',confirm,()=>{if(!pick.size){GirlUI.toast("Choose at least one Girl");return;}finished=true;close();res([...pick].map(([pos,partner_id])=>({partner_id,pos})).sort((a,b)=>a.pos-b.pos));}));
     grid.replaceChildren();const chosen=new Set(pick.values());
     const list=[...state.roster].filter(h=>!faction||girlsCatalog.find(g=>g.id===h.table_id)?.group===faction).sort((a,b)=>chosen.has(b.partner_id)-chosen.has(a.partner_id)||(b.lv||0)-(a.lv||0)||(b.stars||0)-(a.stars||0));
     for(const h of list){const c=heroIcon(h,'cf-hero pick'+(chosen.has(h.partner_id)?' on':''));c.onclick=()=>{const at=[...pick].find(([,id])=>id===h.partner_id);if(at){pick.delete(at[0]);draw();return;}const free=slots.find(p=>!pick.has(p));if(free===undefined){GirlUI.toast("The lineup is full");return;}pick.set(free,h.partner_id);draw();};grid.append(c);}};
   for(let f=1;f<=6;f++){const b=btn('cf-fbtn','',()=>{faction=faction===f?0:f;filter.querySelectorAll('.cf-fbtn').forEach((x,i)=>x.classList.toggle('on',faction===i+1));draw();});b.append(img(R('img_group'+f)));filter.append(b);}
   body.append(top,filter,grid);draw();if(servant&&!servants)api('/assets/servants.json').then(d=>{servants=d;if(win.isConnected)draw();}).catch(()=>{});api('/api/partners/power').then(p=>{powers=p||{};if(win.isConnected)draw();}).catch(()=>{});
   const obs=new MutationObserver(()=>{if(!win.isConnected){obs.disconnect();if(!finished)res(null);}});obs.observe(document.body,{childList:true,subtree:true});});}
 function formation(){return picker({title:'Battle',slots:[1,2,3,4,5,6],front:2,initial:state.formation,confirm:'Battle Start',servant:true});}
 async function hangTeam(){const team=await picker({title:'Auto-Battle',slots:[1,2,3],front:1,initial:hangList(),confirm:'Save Team',note:"Girls patrolling the stage (up to 3). This does not change your battle lineup."});
  if(!team)return;try{const r=await api('/api/campaign/hang-team',{partners:team});state=r.state;GirlUI.toast("Patrol lineup saved");if(typeof render==='function')render();}catch(e){GirlUI.toast(e.message);}}
 function hangList(){const own=h=>state.roster.some(x=>x.partner_id===h.partner_id);const t=(state.campaign_hang||[]).filter(own);return t.length?t:(state.formation||[]).filter(own).slice(0,3).map((f,i)=>({partner_id:f.partner_id,pos:i+1}));}
 // --- CampaignStageDetailWindow --------------------------------------------------------------------------------------------
 async function stageDetail(stage,{onFight,onHang}={}){if(!campaign)campaign=await api('/assets/campaign.json');const d=campaign.stages[stage.id]||{};
  const {body,close}=GirlUI.win({title:'Stage '+stage.chapter+'-'+stage.chapter_stage+(d.name?' · '+d.name:''),cls:'cf-stage'});
  body.append(el('h4','cf-sub','Output'));const out=el('div','cf-output');
  (d.rate||[]).forEach((r,i)=>{const [id,n]=String(r||'').split('#');const c=el('div','cf-out');c.append(i===2?el('b','cf-exp','EXP'):img(id==='1'?'/assets/currency/icon_1_small.png':'/assets/campaign/icon_9.png','cf-out-icon'),el('span','','+'+number(Number(n)||0)+'/5s'));out.append(c);});body.append(out);
  body.append(el('h4','cf-sub','Loot'));const loot=el('div','cf-loot');for(const id of String(d.drops||'').split('|').filter(Boolean).sort((a,b)=>b-a)){const it=itemCatalog?.[id];const c=el('div','cf-item');c.style.backgroundImage=`url('/assets/ui/quality_${Math.min(it?.quality||1,7)}.png')`;const src=it&&typeof itemPicture==='function'?itemPicture(it):'';c.append(img(src||(typeof Equipment!=='undefined'&&Equipment.icon?.(id))||'/assets/ui/item_bg.png'));c.title=it?.name||("Item "+id);loot.append(c);}body.append(loot);
  const b=el('div','gs-btns cf-stage-actions');if(onHang)b.append(btn('gs-btn','Change',()=>{close();onHang();}));if(onFight)b.append(btn('gs-btn','Fight',()=>{close();onFight();}));if(b.children.length)body.append(b);body.append(el('p','cf-note',onHang?"Change selects this stage for idle farming and preserves accumulated rewards.":stage.id===state.hang_info?.stage?"This is your current idle stage.":"Preview: clear this stage to unlock idle farming here."));if(d.reward){const awards=GrowthDiary.rewards(d.reward);String(d.reward).split('|').forEach((v,i)=>{const id=v.split('#')[0];if(['1','3','9'].includes(id)&&awards.children[i]){awards.children[i].title={'1':"Gold",'3':"Player EXP",'9':"Girl EXP"}[id];awards.children[i].querySelector('img').src='/assets/campaign/icon_'+id+'.png';}});body.append(el('h4','cf-sub',"First victory"),awards);}}
 return {loading,sweep,formation,hangTeam,hangList,stageDetail,heroIcon};
})();
