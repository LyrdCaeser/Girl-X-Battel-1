'use strict';
// Old Campus Exploration (OldSchoolMainWindow → ActivityExploreCampusFightWindow). Rules: gxb2/old_campus.py.
// Layout from docs/references/2026-09-29-e (04 areas, 05 stage + Exploration Plan). Art: old_building_logo, old_school_bg*,
// fangan_* plan icons, stage bosses as original chibis (static snapshots to save WebGL contexts).
const OldCampus=(()=>{
 let origin='league',panel=null,note='',busyLocal=false,skipReplay=false,teams=[],tab=0,sel=null,timer=null;
 const A=n=>'/assets/old-campus/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const btn=(cls,text,fn)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
 try{skipReplay=localStorage.getItem('gxb2.oldCampus.skip')==='1';}catch{}
 function root(){let r=$('old-campus-view');if(!r){r=el('section','old-campus-view');r.id='old-campus-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from){origin=from||view;panel=null;note='';showView('old-campus');act({action:'open'});}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const row=itemCatalog?.[id];return (row&&itemPicture(row))||(row?.icon?'/assets/shops/items/'+row.icon+'.png':'');}
 function chip(k,n){const c=el('span','oc-chip');const s=icon(k);if(s)c.append(img(s));c.append(el('b','',number(n)));return c;}
 async function act(req){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/old-campus/action',req);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;if(view==='old-campus')render();}}
 let loadedAt=performance.now();const left=at=>{const s=Math.max(0,at-(state.server_time||0)-Math.floor((performance.now()-loadedAt)/1000));const d=Math.floor(s/86400),h=Math.floor(s%86400/3600);return d?`${d}D ${h}H`:[h,Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');};
 const chibis=new Map();
 function chibi(tableId){const key=String(tableId);if(chibis.has(key))return chibis.get(key).cloneNode(true);const h=el('div','oc-chibi');api('/assets/chibis/catalog.json').then(c=>{const m=c[key];if(m)GxbSpine.snapshot(h,'/assets/chibis/'+m.model,{width:260,height:260,fit:.85,y:.6,className:'oc-chibi-img',sequence:[['idle',true]]}).then(()=>{const im=h.querySelector('img');if(im)chibis.set(key,im.cloneNode(true));});}).catch(()=>{});return h;}
 function render(){const r=root();if(view!=='old-campus'){clearInterval(timer);timer=null;return;}loadedAt=performance.now();const info=state.old_campus_info;r.replaceChildren();const st=el('div','oc-stage');r.append(st);
  const head=el('div','oc-head');head.style.backgroundImage=`url('${A('old_school_bg')}')`;
  const back=btn('oc-back','',()=>showView(origin==='old-campus'?'league':origin));back.append(img('/assets/ui/win_back_btn.png'));
  const side=el('div','oc-sidebtns');side.append(btn('oc-round','?',()=>CampaignUI.popup(String(info?.help||HELP),{})),btn('oc-round','🎁',()=>{panel='score';render();}));
  head.append(back,side,img(A('old_building_logo_en_en'),'oc-logo'));st.append(head);
  if(!info){st.append(el('p','oc-note',"Loading…"));return;}
  if(!info.unlocked){st.append(el('p','oc-note oc-box',`Old Campus unlocks after clearing stage ${info.unlock_stage}.`));return;}
  head.append(el('div','oc-count',(info.open?'Countdown: ':'Results: ')+left(info.open?info.battle_end:info.season_end)),(()=>{const t=el('div','oc-total');t.append(el('small','','Total Score'),el('b','',String(info.total)));return t;})());
  // Areas, highest open first (reference capture 04).
  const list=el('div','oc-list');for(const lv of [...info.levels].filter(l=>l.open).reverse()){const card=el('div','oc-area');card.style.backgroundImage=`url('${A('old_school_bg'+(1+(lv.level-1)%4))}')`;
   const top=el('div','oc-area-top');top.append(btn('oc-small','Set Team',()=>{sel=lv.level;teams=lv.stages.map(s=>(s.team||[]).map(t=>({...t})));tab=0;panel='teams';render();}));
   const sign=el('div','oc-sign');sign.append(el('b','',`Area ${lv.level}`),el('small','',`Best Score: ${lv.best}`));top.append(sign);
   if(lv.claimable>0){const g=btn('oc-gift','🎁 '+lv.claimable,async()=>{const res=await act({action:'claim_level',level:lv.level});if(res?.got)CampaignUI.popup(`Area ${lv.level}`,res.got);});g.title='Level Reward';top.append(g);}
   card.append(top);const row=el('div','oc-stages');lv.stages.forEach((s,i)=>{const c=el('div','oc-st');c.append(el('b','oc-num',String(i+1)),chibi(s.boss),el('span','oc-cur',`Current Score: ${s.cur}`));
    const b=btn('oc-battle','Battle',()=>{sel=lv.level;tab=i;panel='stage';render();});b.disabled=!info.open;c.append(b);if(s.done)c.classList.add('done');row.append(c);});card.append(row);list.append(card);}
  st.append(list);
  if(note)st.append(el('p','oc-note oc-err',note));
  if(panel==='stage')stageWin(st,info);else if(panel==='teams')teamWin(st,info);else if(panel==='score')scoreWin(st,info);
  clearInterval(timer);timer=setInterval(()=>{const c=root().querySelector('.oc-count');if(!c||view!=='old-campus'){clearInterval(timer);return;}c.textContent=(info.open?'Countdown: ':'Results: ')+left(info.open?info.battle_end:info.season_end);},1000);}
 const HELP="1. Seasons have 13 battle days and 1 results day.\n2. There are 10 levels of 2–3 stages; clearing a stage unlocks the next level.\n3. Assign one team per stage (each Girl can only be in one team per level).\n4. Exploration Plans strengthen enemies and add points: score = base + plans.\n5. Changing a stage's team resets its current score; the level's best score is preserved.\n6. Total score is the sum of the best scores across all 10 levels.";
 function overlay(st,title){const ov=el('div','oc-overlay');ov.onclick=e=>{if(e.target===ov){panel=null;render();}};const w=el('div','oc-win');ov.append(w);w.append(el('h2','',title),btn('oc-close','✕',()=>{panel=null;render();}));st.append(ov);return w;}
 // ActivityExploreCampusFightWindow: stage score, plans (Primary / Standard), teams and Fight.
 function stageWin(st,info){const lv=info.levels.find(l=>l.level===sel);const s=lv.stages[tab];const w=overlay(st,`Area ${lv.level}, Stage ${tab+1}`);
  const byId=new Map(info.plans.map(p=>[p.id,p]));const chosen=s.plans||[];const score=s.base+chosen.reduce((a,p)=>a+(byId.get(p)?.point||0),0);
  w.append(el('h3','oc-score',`Stage Score: ${score}`));const desc=el('div','oc-desc');desc.append(el('b','',`Basic Score of Current Stage is ${s.base}`));for(const p of chosen){const d=byId.get(p);const r=el('div','oc-drow');r.append(planIcon(d),el('span','',d.desc||d.name));desc.append(r);}w.append(desc);
  const pick=el('div','oc-plans');pick.append(el('h4','','Please choose your Exploration Plan'));for(const [t,c]of info.cats.entries()){const openCat=info.total>=c.need&&lv.level>=c.floor;const h=el('h5','',c.name+(openCat?'':` 🔒 ${c.floor>1?"Level "+c.floor:'Total Score '+c.need}`));pick.append(h);const g=el('div','oc-pgrid'+(openCat?'':' locked'));for(const p of info.plans.filter(p=>p.cat===t)){const on=chosen.includes(p.id);const b=btn('oc-pbtn'+(on?' on':''),'',async()=>{if(!openCat)return;let next=on?chosen.filter(x=>x!==p.id):[...chosen.filter(x=>!p.group||byId.get(x)?.group!==p.group),p.id];await act({action:'plans',level:lv.level,index:tab,plans:next});});b.append(planIcon(p));b.title=`${p.name}: ${p.desc}`;g.append(b);}pick.append(g);}w.append(pick);
  const bar=el('div','oc-teambar');bar.append(el('b','oc-circle',String(tab+1)));const sk=btn('oc-skip'+(skipReplay?' on':''),'',()=>{skipReplay=!skipReplay;try{localStorage.setItem('gxb2.oldCampus.skip',skipReplay?'1':'0');}catch{};render();});sk.append(el('i','',skipReplay?'✓':''),el('span','','Skip'));bar.append(sk,btn('oc-small','Set Team',()=>{teams=lv.stages.map(x=>(x.team||[]).map(t=>({...t})));panel='teams';render();}));w.append(bar);
  const vs=el('div','oc-vs');const mine=el('div','oc-side');const roster=new Map((state.roster||[]).map(h=>[h.partner_id,h]));for(const t of s.team||[]){const h=roster.get(t.partner_id);if(h){const c=el('div','oc-face');c.append(typeof portrait==='function'?portrait(h.table_id,48):el('span'),el('small','',String(h.lv)));mine.append(c);}}
  const foes=el('div','oc-side');for(const e of s.enemies||[]){const c=el('div','oc-face');c.append(typeof portrait==='function'?portrait(e.table_id,48):el('span'),el('small','',String(e.lv)));foes.append(c);}vs.append(mine,el('span','oc-x','⚔'),foes);w.append(vs);
  const f=btn('oc-fight','Fight',()=>fight(lv,s));f.disabled=!(s.team||[]).length||!info.open;w.append(f);}
 function planIcon(p){const i=el('span','oc-picon');i.append(img(A(p.icon)),el('i','',String(p.point)));return i;}
 async function fight(lv,s){panel=null;const r=await act({action:'fight',level:lv.level,index:tab});if(!r)return;const label=`Area ${lv.level}, Stage ${tab+1}`;
  if(!skipReplay&&r.report&&typeof watchEventBattle==='function')await watchEventBattle({report:r.report,rewards:{}},'old-campus',label);else CampaignUI.result(r.win,{},{event:true,label:label+(r.win?` · ${r.score} points`:''),report:r.report});
  if(r.win)note=`Stage Score ${r.score} · Area ${r.level_score} (Best ${r.best}) · Total ${r.total}`;render();}
 // Set Team for all the stages of the level (a Girl only once per level).
 function teamWin(st,info){const lv=info.levels.find(l=>l.level===sel);const w=overlay(st,`Area ${lv.level} · Set Team`);while(teams.length<lv.stages.length)teams.push([]);
  const tabs=el('div','oc-tabs');lv.stages.forEach((_,i)=>tabs.append(btn('oc-tab'+(i===tab?' on':''),`Stage ${i+1}`,()=>{tab=i;render();})));w.append(tabs);
  const roster=[...(state.roster||[])].sort((a,b)=>b.lv-a.lv);const byId=new Map(roster.map(h=>[h.partner_id,h]));const used=new Map();teams.forEach((t,i)=>t.forEach(m=>used.set(m.partner_id,i)));
  const grid=el('div','oc-formation');for(const [label,poss]of [['Front',[1,2]],['Back',[3,4,5,6]]]){const line=el('div','oc-line');line.append(el('b','',label));for(const p of poss){const m=teams[tab].find(x=>x.pos===p);const slot=btn('oc-slot','',()=>{if(m){teams[tab]=teams[tab].filter(x=>x!==m);render();}});if(m&&byId.get(m.partner_id))slot.append(typeof portrait==='function'?portrait(byId.get(m.partner_id).table_id,64):el('span'));line.append(slot);}grid.append(line);}w.append(grid);
  const pool=el('div','oc-pool');for(const h of roster){const u=used.get(h.partner_id);const c=btn('oc-cand'+(u===tab?' on':u!=null?' other':''),'',()=>{if(u!=null&&u!==tab)return;if(u===tab)teams[tab]=teams[tab].filter(m=>m.partner_id!==h.partner_id);else{const free=[1,2,3,4,5,6].find(p=>!teams[tab].some(m=>m.pos===p));if(free)teams[tab].push({partner_id:h.partner_id,pos:free});}render();});c.append(typeof portrait==='function'?portrait(h.table_id,52):el('span'),el('small','',u!=null&&u!==tab?`S${u+1}`:String(h.lv)));c.title=h.name;pool.append(c);}w.append(pool);
  w.append(btn('oc-fight','Save',async()=>{if(teams.some(t=>!t.length)){note="Assign at least one Girl to each stage";render();return;}const res=await act({action:'teams',level:lv.level,teams});if(res){panel=null;render();}}));}
 function scoreWin(st,info){const w=overlay(st,`Score Rewards · Total ${info.total}`);for(const a of info.score_awards){const row=el('div','oc-srow');row.append(el('b','',String(a.point)));for(const [k,n]of Object.entries(a.awards))row.append(chip(k,n));const b=btn('oc-small',a.claimed?'Claimed':'Claim',async()=>{const res=await act({action:'claim_score',id:a.id});if(res?.got){panel=null;CampaignUI.popup('Score Reward',res.got);}});b.disabled=a.claimed||info.total<a.point;row.append(b);w.append(row);}}
 return {open,render};
})();
