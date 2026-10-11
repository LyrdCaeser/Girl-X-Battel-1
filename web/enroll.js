'use strict';
// Enroll (ProphetWindow.lua / ProphetSummon): pick a faction, stamp with Seals (item 20) for that faction's
// 4★/5★ shards; each Enroll also gives Portfolios (item 19). SUMMON ids = Prophet.SUMMONMID: ×1 10–14, ×10 17–21.
// Scene: prophet_bg03, teacher Spine `caopi` (girls_model 5), desk prophet_icon07, stamp prophet_icon06, fx_yinzhang.
const Enroll=(()=>{
 const GROUPS=[[1,'Ghost'],[2,'Human'],[3,'Monster'],[4,'Fairy'],[5,'Light & Dark']];
 const TALK=['Knowledge is life!','Choose a faction and stamp the form.','A new classmate is waiting~','Seals come from events, internships and the market.'];
 let tab='enroll',selectedExchange=null,exchangeModels=[],exchangeGeneration=0;
 let group=1,ten=false,origin='campus',teacher=null,stamp=null,busyLocal=false,talk=0;
 const A=n=>'/assets/enroll/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 function open(from){origin=from||view;showView('enroll');render();}
 function root(){let r=$('enroll-view');if(!r){r=el('section','enroll-view');r.id='enroll-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function stop(){exchangeGeneration++;for(const m of exchangeModels)m.destroy();exchangeModels=[];teacher?.destroy();teacher=null;stamp?.destroy();stamp=null;}
 function render(){const r=root();if(view!=='enroll'){stop();return;}for(const m of exchangeModels)m.destroy();exchangeModels=[];exchangeGeneration++;r.replaceChildren();
  const top=el('header','en-top');const seals=el('span','en-cur');seals.append(img(A('icon_20')),el('b','',number(state.items['20']||0)));const port=el('span','en-cur');port.append(img(A('icon_19')),el('b','',number(state.items['19']||0)));
  const back=el('button','en-back');back.type='button';back.append(img('/assets/ui/win_back_btn.png'));back.onclick=()=>{stop();showView(origin==='enroll'?'campus':origin);};top.append(seals,port,back);r.append(top);
  const tabs=el('nav','en-tabs');const t1=el('button',tab==='enroll'?'on':'','Enroll');t1.type='button';t1.onclick=()=>{tab='enroll';render();};const t2=el('button',tab==='exchange'?'on':'','Exchange');t2.type='button';t2.onclick=()=>{tab='exchange';stop();render();};tabs.append(t1,t2);r.append(tabs);if(tab==='exchange'){exchange(r);return;}
  const scene=el('div','en-scene');scene.style.backgroundImage=`url('${A('prophet_bg03')}')`;r.append(scene);
  const model=el('div','en-model');scene.append(model);
  const bubble=el('div','en-bubble',TALK[talk%TALK.length]);bubble.style.backgroundImage=`url('${A('prophet_bubble_bg')}')`;scene.append(bubble);
  const bulb=img(A('prophet_idea'),'en-idea');bulb.onclick=()=>{talk++;bubble.textContent=TALK[talk%TALK.length];};scene.append(bulb);
  const help=el('button','en-help','?');help.type='button';help.onclick=()=>CampaignUI.popup("1. Each Enroll costs 1 Seal (10 with the checkbox). 2. Grants 4★ or 5★ Shards from the selected faction. 3. Also grants Portfolios for Exchange. 4. Each Seal adds 1 point to Enroll Exam.",{});scene.append(help);
  const side=el('div','en-groups');for(const [g,name]of GROUPS){const b=el('button','en-group'+(g===group?' on':''));b.type='button';const ic=el('span','en-group-icon');if(g===5){ic.append(img('/assets/factions/6.png'),img('/assets/factions/5.png'));ic.classList.add('dual');}else ic.append(img('/assets/factions/'+g+'.png'));b.append(ic);if(g===group)b.append(el('span','en-group-name',name));b.onclick=()=>{group=g;render();};side.append(b);}scene.append(side);
  const desk=img(A('prophet_icon07'),'en-desk');scene.append(desk);const file=img(A('prophet_icon_group'+group),'en-file');scene.append(file);const fx=el('div','en-fx');scene.append(fx);
  const st=el('button','en-stamp');st.type='button';st.append(img(A('prophet_icon06')),el('span','en-stamp-label','Enroll'));const cost=el('div','en-cost');cost.append(img(A('icon_20')),el('b','',ten?'X10':'X 1'));
  const need=ten?10:1,have=Number(state.items['20']||0);st.disabled=busyLocal||have<need;st.title=have<need?'Not enough Seals':'';st.onclick=()=>enroll(fx);
  const chk=el('label','en-ten');const box=el('input');box.type='checkbox';box.checked=ten;box.onchange=()=>{ten=box.checked;render();};chk.append(box,el('span','','Use 10 Seals'));
  scene.append(st,cost,chk);
  mountTeacher(model);}
 async function mountTeacher(host){if(teacher){host.append(teacher.app.view);return;}try{teacher=await GxbSpine.mount(host,'/assets/spine/caopi',{width:560,height:900,fit:.98,y:.54,className:'en-teacher',sequence:[['texiao01',true]]});}catch{}}
 async function enroll(fx){if(busyLocal)return;busyLocal=true;const sid=(ten?[17,18,19,20,21]:[10,11,12,13,14])[group-1];
  try{stamp?.destroy();stamp=await GxbSpine.mount(fx,'/assets/spine/fx_yinzhang',{width:360,height:360,fit:.9,className:'en-stamp-fx',sequence:[['texiao',false]]}).catch(()=>null);GxbAudio.sfx('girl_enrol',.8);
   const before={...state.items};const res=await api('/api/action',{message:'SUMMON',data:{summon_id:sid,times:1}});state=res.state;
   const got={};for(const [k,v]of Object.entries(state.items))if(Number(v)>Number(before[k]||0))got[k]=Number(v)-Number(before[k]||0);delete got['20'];
   setTimeout(()=>CampaignUI.popup('Enroll · '+GROUPS[group-1][1],got),700);}catch(e){CampaignUI.popup(e.message,{});}finally{busyLocal=false;render();if(typeof window.render==='function')window.render();}}

 // ---- Exchange (prophet_replace.prefab 708×908, ProphetReplace in ProphetWindow.lua). Coordinates: prefab units, y up, centre (360, 454).
 // group1 (top, the result) and group2 (bottom, your girl) on prophet_bg02; each a PartnerCardLarge (195×295: partner_card_bg01,
 // partner_card00 silhouette, the card art, partner_large_card border, img_group, level, name, stars) and a model spot.
 // Effects (ProphetReplace.LoadResource): fx_guanghuan orb while nothing is chosen, fx_wenhao "?" over the unknown result,
 // fx_saomiao scan revealing the card (showCardEffect 1.333 s), fx_guangzhu pillar then fx_daiji ring under each model.
 let exFilter=0,exChoosing=false,exRevealAt=0;
 const XA=(e,x,y,w,h)=>{e.style.left=`calc(${360+x-w/2} * var(--u))`;e.style.top=`calc(${454-y-h/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;e.style.height=`calc(${h} * var(--u))`;return e;};
 async function fx(host,name,seq,w=300,h=300,oy=.5){const gen=exchangeGeneration;try{const m=await GxbSpine.mount(host,'/assets/spine/'+name,{width:w,height:h,scale:1,origin:[.5,oy],sequence:seq,className:'ex2-fx'});if(gen!==exchangeGeneration||view!=='enroll'||!host.isConnected){m.destroy();return null;}exchangeModels.push(m);return m;}catch{return null;}}
 async function exchangeModel(host,tid,generation){try{const cat=await ChibiBattle.catalogue(),meta=cat[tid];if(!meta||generation!==exchangeGeneration||view!=='enroll'||!host.isConnected)return;const m=await GxbSpine.mount(host,'/assets/chibis/'+meta.model,{width:300,height:300,scale:.7,origin:[.5,.83],sequence:[['idle',true]],className:'ex2-chibi',resolution:2});if(generation!==exchangeGeneration||view!=='enroll'||!host.isConnected){m.destroy();return;}exchangeModels.push(m);}catch{}}
 // PartnerCardLarge. mode: 'blank' (default card + "?"), 'shadow' (silhouette with group / level / stars) or 'hero' (the girl's card)
 function bigCard(tid,mode,lv,since){const reveal=since!=null;const g=tid?girlsCatalog.find(x=>x.id===Number(tid)):null;const c=el('div','ex2-card');c.append(img(A('partner_card_bg01'),'ex2-cbg'));
  if(mode==='blank'){c.append(el('div','ex2-border'),img(A('prophet_icon11'),'ex2-q'));return c;}
  if(mode==='shadow'||reveal)c.append(img(A('partner_card00'),'ex2-shadow'));
  if(mode==='hero'){const art=el('div','ex2-art'+(reveal?' reveal':''));if(reveal)art.style.animationDelay=(-since)+'s';if(cardIds.has(Number(tid)))art.append(img('/assets/cards/partner_card_'+tid+'.png'));else if(typeof portrait==='function')art.append(portrait(tid,120));c.append(art);const nm=el('div','ex2-name'+(reveal?' late':''));nm.append(el('b','',g?.name||''));c.append(nm);
   if(reveal){nm.style.animationDelay=(-since)+'s';const scan=el('div','ex2-scan');scan.style.animationDelay=(-since)+'s';c.append(scan);fx(scan,'fx_saomiao',[['texiao',false]],260,120);}}
  c.append(el('div','ex2-border'));
  if(g){c.append(img(A('img_group'+g.group),'ex2-group'),el('b','ex2-lv',String(lv||1)));const st=el('div','ex2-stars');for(let i=0;i<Math.min(5,g.stars);i++)st.append(img(A(g.stars>5?'partner_star_red_big':'partner_star_yellow')));c.append(st);}
  return c;}
 function exchange(r){const info=state.acquisition||{},pending=info.exchange;const choices=info.eligible||[];
  if(pending)selectedExchange=pending.partner_id;else if(!choices.some(x=>x.partner_id===selectedExchange))selectedExchange=null;
  const girl=state.partners.find(x=>x.partner_id===selectedExchange);const gen=exchangeGeneration;const elapsed=(Date.now()-exRevealAt)/1000,exReveal=elapsed<1.9;
  const st=el('div','ex2-stage');r.append(st);st.append(XA(img(A('prophet_bg03'),'ex2-bg'),0,0,708,908),XA(el('div','ex2-frame'),0,0,708,908));
  const help=XA(el('button','ex2-help'),-313,408,52,52);help.type='button';help.setAttribute('aria-label',"Exchange Help");help.dataset.imgGuide='prophet_window';help.append(img(A('help_2')));help.onclick=()=>ImgGuides.open('prophet_window',1);st.append(help);
  // group1: the result
  st.append(XA(img(A('prophet_bg02'),'ex2-panel'),0,260,566,358));
  const src=pending?state.partners.find(x=>x.partner_id===pending.partner_id):girl;
  const c1=XA(pending?bigCard(pending.replace_id,'hero',src?.lv,elapsed<1.333?elapsed:null):girl?bigCard(girl.table_id,'shadow',girl.lv):bigCard(0,'blank'),-142,260,195,295);st.append(c1);
  const spot1=XA(el('div','ex2-spot'),119,260,300,300);st.append(spot1);
  if(pending){const ring=el('div','ex2-ring');spot1.append(ring);const model=el('div','ex2-model');spot1.append(model);const show=()=>{if(gen!==exchangeGeneration)return;fx(ring,'fx_daiji',[['texiao',true]],300,300,.83);exchangeModel(model,String(pending.replace_id),gen);const g=girlsCatalog.find(x=>x.id===Number(pending.replace_id));
     const det=XA(el('button','ex2-detail'),246,388,52,52);det.type='button';det.append(img(A('battle_detail_icon_2')));det.title='Detalles';det.onclick=()=>CampaignUI.popup((g?.name||'')+' · '+'★'.repeat(Math.min(5,g?.stars||0))+"\nSave transforms her into this Girl, preserving level, grade, lineup, and equipment; Cancel keeps your Girl. Portfolios are not refunded.",{});st.append(det);};
    if(exReveal){const pil=el('div','ex2-ring');spot1.append(pil);setTimeout(()=>{if(gen!==exchangeGeneration)return;fx(pil,'fx_guangzhu',[['texiao',false]],300,300,.83);setTimeout(show,500);},Math.max(0,(1.333-elapsed)*1000));}else show();}
  else if(girl){const q=el('div','ex2-ring');spot1.append(q);fx(q,'fx_wenhao',[['texiao01',false],['texiao02',true]],300,300,.5);}
  st.append(XA(img(A('prophet_icon05'),'ex2-arrow'),0,42,62,62));
  // group2: your girl
  st.append(XA(img(A('prophet_bg02'),'ex2-panel'),0,-169,566,358));
  const c2=XA(src?bigCard(pending?.source_id||src.table_id,'hero',src.lv):bigCard(0,'blank'),-142,-172,195,295);st.append(c2);
  const spot2=XA(el('div','ex2-spot'),112,-188,300,300);st.append(spot2);
  if(src){const ring=el('div','ex2-ring');spot2.append(ring);fx(ring,'fx_daiji',[['texiao',true]],300,300,.83);const model=el('div','ex2-model');spot2.append(model);exchangeModel(model,String(pending?.source_id||src.table_id),gen);}
  else{st.append(XA(el('p','ex2-tip','Select a Girl to Exchange'),112,-30,300,48));const orb=el('div','ex2-ring');spot2.append(orb);fx(orb,'fx_guanghuan',[['texiao01',false],['texiao02',true]],300,300,.5);}
  if(!pending){const touch=XA(el('button','ex2-touch'),-3,-171,566,358);touch.type='button';touch.setAttribute('aria-label','Select a Girl to Exchange');touch.onclick=()=>{exChoosing=true;render();};st.append(touch);}
  // bottom buttons
  const B=(cls,label,x,fn,off)=>{const b=XA(el('button','ex2-btn '+cls),x,-402,212,65);b.type='button';b.disabled=!!off;b.onclick=fn;b.append(el('span','',label));st.append(b);return b;};
  if(pending){B('white','Cancel',-145,()=>exchangeAction('PROPHET_REPLACE_SAVE',{partner_id:pending.partner_id,is_save:0}),busyLocal);B('blue','Save',151,()=>exchangeAction('PROPHET_REPLACE_SAVE',{partner_id:pending.partner_id,is_save:1}),busyLocal);}
  else if(girl){const cost=choices.find(x=>x.partner_id===selectedExchange)?.cost||{};const n=Number(cost['19']||0);const b=B('blue','Exchange',2,()=>{const go=()=>exchangeAction('PROPHET_REPLACE',{partner_id:selectedExchange});if(girl.is_vowed){const {body,close}=GirlUI.win({title:'Exchange',cls:'ex2-confirm'});body.append(el('p','','One of these Girls has Oath status with you. The process will consume the Girl and WILL NOT return her Oath Ring. Do you wish to continue?'));const a=el('div','gs-btns');const no=el('button','gs-btn white','NO');no.type='button';no.onclick=close;const yes=el('button','gs-btn','YES');yes.type='button';yes.onclick=()=>{close();go();};a.append(no,yes);body.append(a);}else go();},busyLocal||Number(state.items['19']||0)<n);const c=el('i','ex2-cost');c.append(img(A('icon_19')),el('small','',String(n)));b.prepend(c);if(Number(state.items['19']||0)<n)b.title='Not enough Portfolios';}
  if(exChoosing&&!pending)chooser(st,choices);}
 // prophet_choose_partner_window: bottom sheet with the four factions of Exchange and the girls that can be exchanged
 function chooser(st,choices){const sheet=el('div','ex2-sheet');const fl=el('div','ex2-filters');for(const gidx of [1,2,3,4]){const b=el('button','ex2-filter'+(exFilter===gidx?' on':''));b.type='button';b.append(img('/assets/factions/'+gidx+'.png'));b.onclick=()=>{exFilter=exFilter===gidx?0:gidx;render();};fl.append(b);}
  const x=el('button','ex2-sheet-x','✕');x.type='button';x.onclick=()=>{exChoosing=false;render();};sheet.append(fl,x);const grid=el('div','ex2-grid');
  const rows=choices.map(c=>({c,p:state.partners.find(g=>g.partner_id===c.partner_id)})).filter(o=>o.p).map(o=>({...o,g:girlsCatalog.find(g=>g.id===o.p.table_id)})).filter(o=>!exFilter||o.g?.group===exFilter).sort((a,b)=>(b.g?.stars||0)-(a.g?.stars||0)||(a.g?.group||0)-(b.g?.group||0)||a.p.table_id-b.p.table_id);
  const px=Math.round(96*((root().getBoundingClientRect().width||720)/720));
  for(const o of rows){const b=el('button','ex2-pick');b.type='button';b.title=(o.g?.name||'')+' · Lv.'+o.p.lv;if(typeof portrait==='function')b.append(portrait(o.p.table_id,px,o.p));if(o.g)b.append(img(A('img_group'+o.g.group),'ex2-pgroup'));b.append(el('b','ex2-plv',String(o.p.lv)));const s=el('span','ex2-pstars');for(let i=0;i<Math.min(5,o.g?.stars||0);i++)s.append(img(A('partner_star_yellow')));b.append(s);
   b.onclick=()=>{selectedExchange=o.c.partner_id;exChoosing=false;render();};grid.append(b);}
  if(!rows.length)grid.append(el('p','ex2-empty',"No available 4★/5★ Girls from Ghost, Human, Monster, or Fairy (Girls in the lineup or locked are excluded)."));
  sheet.append(grid);st.append(sheet);}
 async function exchangeAction(message,data){if(busyLocal)return;busyLocal=true;try{const res=await api('/api/action',{message,data});state=res.state;if(message==='PROPHET_REPLACE')exRevealAt=Date.now();if(message==='PROPHET_REPLACE_SAVE'){selectedExchange=null;}}catch(e){CampaignUI.popup(e.message,{});}finally{busyLocal=false;render();if(typeof window.render==='function')window.render();}}
 return {open,render,stop};
})();
