'use strict';
// Servants (PetWindow.lua list, PetDetailWindow.lua detail: PetAttr = level/energy skill/evolve,
// PetPasSkill = "Servant Aura" 4 passives with their own levels). Rules live in gxb2/home_systems.py.
// Costs: level = gold + Servant Stone (26); passive = gold + Aura Stone (27); tame = pet.active_cost.
const Servant=(()=>{
 let data=null,loading=null,mode='list',current=null,tab='attr',skill=1,origin='home',spine=null,spineKey='',busyLocal=false,note='';
 const A=n=>'/assets/servant/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const load=()=>data?Promise.resolve(data):(loading||=Promise.all([api('/assets/servants.json'),api('/assets/home-systems/catalog.json')]).then(([d,c])=>{d.rows=c.pet||[];return data=d;}));
 const hs=()=>state.home_systems||{};
 const owned=id=>hs().pets?.[String(id)];
 const info=id=>hs().pet_details?.[String(id)];
 const rows=()=>Object.values(data.pets).sort((a,b)=>a.id-b.id);
 function pairs(t){return String(t||'').split('|').filter(x=>x.includes('#')).map(x=>x.split('#'));}
 function root(){let r=$('servant-view');if(!r){r=el('section','servant-view');r.id='servant-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from){origin=from||view;mode='list';note='';load().then(()=>{showView('servant');render();});}
 function stop(){spine?.destroy();spine=null;spineKey='';}
 async function act(request,msg){if(busyLocal)return;busyLocal=true;note='';try{const r=await api('/api/home/action',request);state=r.state;note=msg||'';GxbAudio?.sfx('hero_upstart',.6);}catch(e){note=e.message;}finally{busyLocal=false;render();}}
 function top(r){const t=el('header','sv-top');for(const id of ['26','27']){const c=el('span','sv-cur');c.append(img(A('icon_'+id)),el('b','',number(state.items[id]||0)));t.append(c);}const back=el('button','sv-back');back.type='button';back.append(img('/assets/ui/win_back_btn.png'));back.onclick=()=>{if(mode==='detail'){mode='list';stop();render();}else{stop();showView(origin==='servant'?'home':origin);}};t.append(back);t.append(el('span','',''));const training=el('button','sv-up-btn','Training / Ulticore');training.type='button';training.onclick=()=>openMenu('pet-training','servant');t.append(training);r.append(t);}
 function cost(parent,text){const c=el('div','sv-cost');for(const [id,n]of pairs(text)){const s=el('span',Number(state.items[id]||0)<Number(n)?'short':'');s.append(img(A('icon_'+id)),el('b','',number(n)));c.append(s);}parent.append(c);return pairs(text).every(([id,n])=>Number(state.items[id]||0)>=Number(n));}

 function render(){const r=root();if(view!=='servant'){stop();return;}if(!data){load().then(render);return;}r.replaceChildren();top(r);if(mode==='detail')detail(r);else list(r);if(note){const n=el('p','sv-note',note);r.append(n);}}

 // ---- Servant List (pet_window: 2 columns of pet_kind01 cards 290×400) ----
 function list(r){const head=el('div','sv-title');head.append(el('b','','Servant List'));const h=el('button','sv-help','?');h.type='button';h.onclick=()=>CampaignUI.popup("Tame Servants with Servant Stones, level them up, evolve them, and upgrade their 4 auras. The selected Servant accompanies your team.",{});head.append(h);r.append(head);
  const grid=el('div','sv-grid');for(const p of rows()){const mine=owned(p.id),card=el('div','sv-card'+(mine?'':' locked')+(hs().selected_pet===p.id?' chosen':''));card.style.backgroundImage=`url('${A('pet_kind01')}')`;
   const model=el('div','sv-card-model');card.append(model);mountCard(model,p,mine);
   const z=el('button','sv-zoom','🔍');z.type='button';z.onclick=()=>details(p);card.append(z);
   if(mine)card.append(el('span','sv-card-lv','Level.'+mine.lv));card.append(el('span','sv-card-name',p.name));
   const b=el('button','sv-btn');b.type='button';b.style.backgroundImage=`url('${A('blue_btn_65_65')}')`;
   if(mine){b.textContent='Train';b.onclick=()=>{current=p.id;mode='detail';tab='attr';note='';render();};}
   else{const row=home().find(x=>x.id===String(p.id));const [[cid,cn]]=pairs(row?.active_cost||'26#0');b.append(img(A('icon_'+cid)),el('b','',number(cn)),el('span','','Tame'));b.disabled=Number(state.items[cid]||0)<Number(cn);b.onclick=()=>act({action:'pet_activate',id:p.id},p.name+' domado.');}
   card.append(b);grid.append(card);}r.append(grid);}
 function home(){return data.rows||[];}
 async function mountCard(host,p,mine){const g=Number(mine?.grade||1),m=p.models[g]||p.models[1];if(!m)return;try{await GxbSpine.snapshot(host,'/assets/spine/pets/'+m.name,{width:290,height:260,fit:.8,y:.6,className:'sv-card-canvas',sequence:[['idle',true]]});}catch{}}

 // ---- Servant Details popup (PetInfoWindow): energy skill + 4 passive icons ----
 function details(p){const mine=owned(p.id),inf=info(p.id);const lv=mine?.lv||1;const b=el('div','sv-details');const ms=Object.keys(p.act_skill).map(Number).filter(n=>n<=lv).pop()||1;const sk=p.act_skill[ms]||{};
  const head=el('div','sv-skill-head');head.append(img(A(p.act_icon),'sv-skill-icon'),el('b','','Lv.'+lv+' '+(sk.name||'')));b.append(head,el('p','sv-skill-desc',clean(sk.desc)));
  const ps=el('div','sv-pas');(inf?.skill_details||p.passives.map((x,i)=>({slot:i+1,lv:0,open:false}))).forEach((s,i)=>{const c=el('div','sv-pas-icon'+(s.open?'':' lock'));c.append(img(A(p.passives[i].icon)),el('small','',s.lv>=s.max?'LV.MAX':'LV.'+(s.lv||0)));c.title=p.passives[i].name||'';ps.append(c);});b.append(ps);
  CampaignUI.popup('Servant Details',{});const box=document.querySelector('.cr-overlay .cr-box');box?.querySelector('.cr-rewards')?.replaceWith(b);}
 function clean(t){return String(t||'').replace(/\[c\]\[[0-9a-f]+\]|\[-\]\[\/c\]/gi,'');}

 // ---- Detail (pet_detail_window) ----
 function detail(r){const p=data.pets[current],mine=owned(current),inf=info(current);if(!p||!mine){mode='list';return list(r);}
  const scene=el('div','sv-scene');scene.style.backgroundImage="url('/assets/servant/pet_scene1.webp')";r.append(scene);
  const name=el('div','sv-name');name.style.backgroundImage=`url('${A('pet_name_bg')}')`;name.append(el('b','',p.name),el('small','',p.weapon||''));scene.append(name);
  const ids=rows().filter(x=>owned(x.id)).map(x=>x.id),i=ids.indexOf(current);
  for(const [dir,cls]of [[-1,'l'],[1,'r']]){const a=el('button','sv-arrow '+cls);a.type='button';a.append(img(A('partner_detail_arrow')));a.disabled=ids.length<2;a.onclick=()=>{current=ids[(i+dir+ids.length)%ids.length];render();};scene.append(a);}
  const reborn=el('button','sv-reborn');reborn.type='button';reborn.append(img(A('pet_btn_reborn')));reborn.onclick=()=>CampaignUI.popup("Reborn (returning Servant resources) has not been restored yet.",{});scene.append(reborn);
  const sel=el('button','sv-select'+(hs().selected_pet===current?' on':''),hs().selected_pet===current?"In the team":"Add to team");sel.type='button';sel.onclick=()=>act({action:'pet_select',id:current},p.name+" will accompany the team.");scene.append(sel);
  const model=el('div','sv-model');scene.append(model);mountDetail(model,p,mine);
  const tabs=el('nav','sv-tabs');for(const [k,l,pos]of [['attr','Attribute','left'],['aura','Servant Aura','right']]){const b=el('button','sv-tab '+pos+(tab===k?' on':''),l);b.type='button';b.onclick=()=>{tab=k;note='';render();};tabs.append(b);}r.append(tabs);
  const panel=el('div','sv-panel');r.append(panel);if(tab==='attr')attr(panel,p,mine,inf);else aura(panel,p,mine,inf);}
 async function mountDetail(host,p,mine){const m=p.models[Number(mine.grade)]||p.models[1];const key=current+':'+m?.name;if(spine&&spineKey===key){host.append(spine.app.view);return;}stop();spineKey=key;if(!m)return;try{const v=await GxbSpine.mount(host,'/assets/spine/pets/'+m.name,{width:600,height:600,fit:.85,y:.55,className:'sv-model-canvas',sequence:[['idle',true]]});if(spineKey!==key){v.destroy();return;}spine=v;}catch{}}
 function attr(panel,p,mine,inf){const lv=mine.lv,cap=inf.cap;const head=el('div','sv-row');head.append(el('span','sv-label','Lv.'),el('b','sv-lv',lv+'/'+cap));const stars=el('span','sv-stars');const maxG=Number(home().find(x=>x.id===String(p.id))?.max_grade||4);for(let g=1;g<=maxG;g++)stars.append(el('i',g<=mine.grade?'on':'','★'));head.append(stars);panel.append(head);
  const ms=Object.keys(p.act_skill).map(Number).filter(n=>n<=lv).pop()||1;const sk=p.act_skill[ms]||{};const skb=el('div','sv-energy');skb.append(img(A(p.act_icon),'sv-skill-icon'));const t=el('div');t.append(el('b','','LV.'+lv+' '+(sk.name||'')),el('p','',clean(sk.desc)));skb.append(t);panel.append(skb);
  const up=el('div','sv-up');if(inf.level_cost){up.append(el('span','sv-label','Lv. Up'));const ok=cost(up,inf.level_cost);const b=el('button','sv-up-btn','⇧');b.type='button';b.disabled=!ok||busyLocal;b.onclick=()=>act({action:'pet_level',id:current});up.append(b);}
  else if(inf.grade_cost){up.append(el('span','sv-label','Evolve'));const ok=cost(up,inf.grade_cost);const b=el('button','sv-up-btn','★');b.type='button';b.disabled=!ok||busyLocal;b.onclick=()=>act({action:'pet_grade',id:current},p.name+' ha evolucionado.');up.append(b);}
  else up.append(el('b','sv-max','MAX'));panel.append(up);}
 function aura(panel,p,mine,inf){const sd=inf.skill_details;const s=sd[skill-1];const up=el('div','sv-up');up.append(el('span','sv-label','Lv. Up'));
  if(!s.open)up.append(el('small','sv-lock-note',"Unlocks at evolution grade "+(skill)));else if(s.lv>=s.max)up.append(el('b','sv-max','MAX'));else{const ok=cost(up,s.cost);const b=el('button','sv-up-btn','⇧');b.type='button';b.disabled=!ok||busyLocal;b.onclick=()=>act({action:'pet_skill',id:current,slot:skill});up.append(b);}panel.append(up);
  const tot={};for(const x of sd)if(x.lv>0)for(const [k,v]of pairs(x.effect))tot[k]=(tot[k]||0)+Number(v);
  const box=el('div','sv-attrs');const NAMES={hp:'HP',atk:'Attack',arm:'Armor',brk:'Armor Brk',hit:'Precision',crit:'Crit',miss:'Block',spd:'Speed',sklP:'Skill DMG',critTime:'Crit DMG',unCrit:'Crit Resist',decDmg:'DMG Red.',trueAtk:'Holy Dmg'};
  for(const [k,v]of Object.entries(tot)){const r=el('div','sv-attr');r.append(el('span','sv-label',NAMES[k]||k),el('b','',(k.endsWith('P')||k==='arm'||v<1?'+'+(v*100).toFixed(1)+'%':'+'+number(v))));box.append(r);}if(!Object.keys(tot).length)box.append(el('p','sv-empty',"Upgrade an aura to view its bonuses."));panel.append(box);
  const row=el('div','sv-skills');sd.forEach((x,i)=>{const b=el('button','sv-skill'+(skill===i+1?' on':'')+(x.open?'':' lock'));b.type='button';b.append(img(A(p.passives[i].icon)),el('small','',x.open?'LV.'+x.lv:'🔒'));b.title=(p.passives[i].name||'')+' — '+clean(p.passives[i].desc||'');b.onclick=()=>{skill=i+1;render();};row.append(b);});panel.append(row);
  const pn=p.passives[skill-1];panel.append(el('p','sv-skill-desc',(pn.name||'')+': '+String(pn.desc||'').replace(/\{(\d)\}/g,(_,n)=>pairs(s.effect)[Number(n)-1]?.[1]??'?')));}
 return {open,render,stop};
})();
