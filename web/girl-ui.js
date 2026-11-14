'use strict';
// Girl sheet visuals and advanced growth (PartnerDetailWindow.lua):
// college_scene{group} background, animated portrait (partner_picture.dragon_bone -> girls_model -> picture_web Spine),
// grade hexagons + grade up (PARTNER_GRADEUP), Awake tab for 6–15★ (AWAKE_PARTNER) and unique skills (UPGRADE_PARTNER_EX_SKILL).
const GirlUI=(()=>{
 let pictures=null,lihui=null,loading=null,pots={skills:{},lv_cap:[260,270,290,310,330],attr_up:[0.14,0.1]},mounted={key:'',view:null},awakeSel={};
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=typeof GxbVi!=='undefined'?GxbVi.t(text):text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;return i;};
 let pics=new Set();
 function load(){return loading||=Promise.all([api('/assets/partner-pictures.json'),api('/assets/lihui.json').catch(()=>[]),api('/assets/pictures.json').catch(()=>[]),api('/assets/potentials.json').catch(()=>null)]).then(([p,l,q,t])=>{pictures=p;lihui=new Set(l);pics=new Set(q);if(t)pots=t;});}
 function picture(id){if(!pics.has(Number(id))){const chain=typeof hostChain==='function'?hostChain(id):[Number(id)];id=chain.find(x=>pics.has(x))??id;}return pics.has(Number(id))?'/assets/pictures/'+id+'.webp':'';}
 const NAMES={'1':"Gold",'2':"Gems",'9':"Girl EXP",'10':"Grade Dust",'198':"Skill Book",'199':"Skill Crystal"};
 function cost(parent,obj){const c=el('span','gu-cost');for(const [id,n]of Object.entries(obj||{})){const ok=Number(state.items[id]||0)>=n;const s=el('span',ok?'':'short');const it=itemCatalog?.[id];const src=id==='1'||id==='2'?'/assets/currency/icon_'+id+'_small.png':it&&itemIcons.has(it.icon)?'/assets/item-icons/'+it.icon+'.png':'';if(src)s.append(img(src));s.append(el('b','',number(n)));s.title=(NAMES[id]||it?.name||"Item "+id)+" · owned: "+number(state.items[id]||0);c.append(s);}parent.append(c);return Object.entries(obj||{}).every(([id,n])=>Number(state.items[id]||0)>=n);}

 function detail(hero){if(!pictures){load().then(()=>view==='detail'&&renderGirlDetail());return;}
  const scene=document.querySelector('#girl-detail-view .detail-scene');if(scene)scene.style.backgroundImage=`url('/assets/scenes/college_scene${hero.group||1}.png')`;
  portrait(hero);grade(hero);exSkills(hero);awake(hero);loveButton(hero);astralTab(hero);if(typeof Souls!=='undefined')Souls.load().then(()=>view==='detail'&&Souls.sheet(state.roster.find(h=>h.partner_id===hero.partner_id)||hero));}
 // PartnerDetailWindow cvInfoGroup: "CV: <name>" top-right (partner_text.cv_name; re-issues use their base girl).
 let cvNames=null;
 async function cvTag(hero){const scene=document.querySelector('#girl-detail-view .detail-scene');if(!scene)return;if(!cvNames){try{cvNames=await api('/assets/dates/cv.json');}catch{cvNames={};}}
  const ids=typeof hostChain==='function'?hostChain(hero.table_id):[hero.table_id];const name=ids.map(x=>cvNames[String(x)]).find(Boolean);let t=scene.querySelector('.gu-cv');
  if(!name){t?.remove();return;}if(!t){t=el('div','gu-cv');scene.append(t);}t.textContent='CV: '+name;}
 function loveButton(hero){cvTag(hero);const scene=document.querySelector('#girl-detail-view .detail-scene');if(!scene||typeof Dates==='undefined')return;let b=scene.querySelector('.gu-love');if(!b){b=el('button','gu-love');b.type='button';scene.append(b);}b.replaceChildren(img('/assets/dates/'+(hero.is_vowed?'love_point_icon6':'love_point_icon'+Math.max(1,Math.min(5,1+Math.floor((hero.love_point||0)/2500))))+'.png'));b.title='Hẹn Hò · Kết Duyên · Thân mật: '+(hero.love_point||0);b.setAttribute('aria-label','Hẹn Hò và Kết Duyên với '+hero.name);b.onclick=()=>Dates.open('detail',hero.partner_id);}

 function portrait(hero){const wrap=document.querySelector('#girl-detail-view .detail-art-wrap'),art=$('detail-art');if(!wrap||!art)return;let showId=(typeof previewSkinId!=='undefined'&&previewSkinId)||hero.equips?.[6]||hero.table_id;if(!pictures[String(showId)]&&typeof hostChain==='function')showId=hostChain(showId).find(x=>pictures[String(x)])??showId;{const own=pictures[String(showId)];const m=/\/assets\/pictures\/(\d+)\.webp/.exec(art.src||'');if(!(own?.spine&&lihui.has(own.spine))&&m&&pictures[m[1]])showId=Number(m[1]);} // place the picture actually shown (a skin without its own art falls back to the girl's)
  const pic=pictures[String(showId)];
  // PartnerDetailWindow: partnerImg at the screen centre, SetLocalPosition(x, -y) and SetLocalScale(scale) with the texture at
  // its native size (MakePixelPerfect) — 1024×2048 / 2048×2048 pictures, so the girl fills the screen and the panel covers her legs
  const native=pic&&art.src.includes('/assets/pictures/');art.classList.toggle('gu-native',!!native);art.style.transform='';
  if(native){const put=()=>{art.style.setProperty('--pw',art.naturalWidth*pic.scale);art.style.setProperty('--px',pic.xy[0]);art.style.setProperty('--py',pic.xy[1]);};if(art.complete&&art.naturalWidth)put();else art.onload=put;}
  else if(pic){art.style.transform=`translate(${pic.xy[0]/7.2}%, ${-pic.xy[1]/12}%) scale(${Math.min(1.25,pic.scale/0.8)})`;}
  const name=pic?.spine,key=hero.partner_id+':'+name;
  if(mounted.key===key)return;mounted.view?.destroy();mounted={key,view:null};wrap.querySelector('.gu-lihui')?.remove();art.hidden=false;
  if(!name||!lihui.has(name))return;
  const host=el('div','gu-lihui');wrap.append(host);
  // GirlsModelLite:setModelInfo puts the Spine at SetLocalPosition(0, -200) inside the partnerImg (scaled by it)
  GxbSpine.mount(host,'/assets/lihui/'+name,{width:720,height:1280,scale:pic.scale,origin:[(360+pic.xy[0])/720,(640+pic.xy[1]+200*pic.scale)/1280],className:'gu-lihui-canvas'}).then(v=>{if(mounted.key!==key){v.destroy();return;}mounted.view=v;art.hidden=true;}).catch(()=>host.remove());}

 function grade(hero){const pips=$('detail-grade-pips');if(!pips)return;pips.replaceChildren();for(let i=0;i<hero.max_grade;i++)pips.append(img('/assets/girl-ui/'+(i<hero.grade?'partner_grade_icon':'partner_grade_icon_bg')+'.png','gu-hex'+(i<hero.grade?' on':'')));
  const box=document.querySelector('#detail-attribute .detail-cost');document.querySelector('.gu-grade')?.remove();
  if(hero.grade<hero.max_grade&&hero.lv>=hero.level_cap){const g=el('div','gu-grade');g.append(el('b','',"Promote"));const ok=cost(g,hero.grade_cost);const b=el('button','gu-btn','Grade Up');b.type='button';b.disabled=!ok;b.onclick=()=>action('PARTNER_GRADEUP',{partner_id:hero.partner_id});g.append(b);box?.after(g);}
  if(hero.lv>=hero.level_cap&&hero.grade>=hero.max_grade){const t=$('detail-cost-text');if(t){t.textContent='MAX';t.classList.add('gu-max');}}}

 // Elite Skills (exskill_grade_up_window): opened from the sheet's left button, no longer inside the Attribute tab
 function exSkills(hero){document.querySelector('.gu-ex')?.remove();}
 function eliteSkills(hero){if(!hero.has_ex_skills){toast("This Girl has no Elite Skills.");return;}const {body}=win({title:'Elite Skills',cls:'gu-ex-win'});const skills=(hero.ex_skills||[0,0,0,0]).concat([0,0,0,0]).slice(0,4);
  const icons=[...document.querySelectorAll('#detail-skills .detail-skill img')].map(i=>i.src),names=[...document.querySelectorAll('#detail-skills .detail-skill')].map(i=>i.title);const row=el('div','gu-ex-row');
  skills.forEach((lv,i)=>{const b=el('button','gu-ex-skill');b.type='button';if(icons[i])b.append(img(icons[i]));b.append(el('span','gu-ex-lv',lv+'/5'));b.disabled=lv>=5;b.title=(names[i]||'Habilidad '+(i+1))+(lv>=5?" · maxed":" · upgrade");b.onclick=async()=>{await action('UPGRADE_PARTNER_EX_SKILL',{partner_id:hero.partner_id,index:i+1});const h=state.roster.find(x=>x.partner_id===hero.partner_id);if(h){sheetRoot().querySelector('.gs-overlay')?.remove();eliteSkills(h);}};row.append(b);});
  body.append(row);const low=Math.min(...skills);if(low<5){const c=el('div','gu-grade');c.append(el('small','',"Next level cost:"));cost(c,hero.ex_skill_cost);body.append(c);}else body.append(el('p','detail-note',"All Elite Skills are maxed."));}

 // ---- Native evolution / awakening: 4★→5★→6★ and 6★→25★ ----
 function starOf(g){return g.stars;}
 function matches(code,g,host){if(g.partner_id===host.partner_id)return false;if(code===g.table_id)return true;if(code%1000!==999)return false;const star=Math.floor(code/10000),group=code%10000===9999?0:Math.floor(code/1000)%10;return starOf(g)===star&&(!group||g.group===group);}
 function materialAvailable(g,host){return g.partner_id!==host.partner_id&&!g.flags?.some(Boolean)&&state.acquisition?.exchange?.partner_id!==g.partner_id;}
 function awake25SameCharacter(a,b){
   if(Number(a.group)!==Number(b.group))return false;
   const ai=a.awake25_identity||[[],[]],bi=b.awake25_identity||[[],[]],ah=ai[0]||[],bh=bi[0]||[];
   if(ah.length||bh.length)return !!ah.length&&!!bh.length&&JSON.stringify(ah)===JSON.stringify(bh);
   const ad=ai[1]||[],bd=bi[1]||[];
   return !!ad.length&&!!bd.length&&JSON.stringify(ad)===JSON.stringify(bd);
  }
  const materialOrder=(a,b)=>(a.pos?1:0)-(b.pos?1:0)||a.lv-b.lv||a.stars-b.stars;
  function pick(recipe,host){
   if(recipe?.awake25){
    const pool=state.roster.filter(g=>materialAvailable(g,host)).sort(materialOrder);
    const sacrificeEligible=g=>Number(g.stars)>=8&&Number(g.stars)<=15&&Number(g.group)>=1&&Number(g.group)<=6&&g.awake25_valid_goddess===true;
    const copies=pool.filter(g=>(Number(g.stars)===9||Number(g.stars)===10)&&awake25SameCharacter(g,host)).sort((a,b)=>Number(sacrificeEligible(a))-Number(sacrificeEligible(b))||materialOrder(a,b)).slice(0,Number(recipe.copies)||0);
    const used=new Set(copies.map(g=>g.partner_id));
    const sacrifices=pool.filter(g=>!used.has(g.partner_id)&&sacrificeEligible(g)).slice(0,Number(recipe.sacrifices)||0);
    return {awake25:true,copies,sacrifices};
   }
   const used=new Set(),out=[];
   for(const code of (recipe?.material||[])){
    const pool=state.roster.filter(g=>!used.has(g.partner_id)&&materialAvailable(g,host)&&matches(code,g,host)).sort(materialOrder);
    const g=pool[0];if(g){used.add(g.partner_id);out.push(g);}else out.push(null);
   }
   return out;
  }
  function selectedMaterials(recipe,picked){return recipe?.awake25?[...picked.copies,...picked.sacrifices]:picked;}
  function materialsReady(recipe,picked){
   if(!recipe||!picked)return false;
   if(recipe.awake25)return picked.copies.length===Number(recipe.copies)&&picked.sacrifices.length===Number(recipe.sacrifices);
   return Array.isArray(recipe.material)&&picked.length===recipe.material.length&&picked.every(Boolean);
  }
  function codeLabel(code){if(code%1000===999){const star=Math.floor(code/10000),group=code%10000===9999?0:Math.floor(code/1000)%10;return star+'★ '+(group?"of the faction":'cualquiera');}return (girlsCatalog?.find?.(g=>g.id===code)?.name||"Girl "+code)+" (copy)";}
 // Limit-Break tab (potentiality_component, 672×381): star banner (potentiality_bg02), the five potential nodes in a W
 // (stage i opens at Limit-Break i), Reverse / Replace / Switch. The star opens the Limit-Break window (capture l/04):
 // next emblem, MAX LVL, the nodes, the girls used as material (1/1), the cost and the Limit-Break button.
 const S='/assets/detail/sheet/',CAPS=[260,270,290,310,330,350,375,400,430,460,495,535,575,620,666];
 // PotentialityComponent:initSkill: stage i is open when stars ≥ 10+i; an open slot shows the chosen skill (or "?"),
 // the next one opens the Limit-Break window, the rest say "Unlocks at Limit-Break Stage i".
 // potentiality_component2: the wings (partner_potential_bg_big, mirrored on the right), the five nodes (skill_icon_bg, 86×86)
 // in a W at (-228,88) (-132,-16) (0,30) (131,-17) (231,88) and the gold / dark lines between them (partner_potential_*_big).
 const LB_POS=[[-228,88],[-132,-16],[0,30],[131,-17],[231,88]];
 function nodes(hero,cls,live=true){const box=el('div','lb-nodes '+cls);const done=Math.max(0,hero.stars-10);const chosen=hero.potentials||[];
  box.append(img(S+'partner_potential_bg_big.png','lb-wing l'),img(S+'partner_potential_bg_big.png','lb-wing r'));
  for(let i=0;i<4;i++){const [x1,y1]=LB_POS[i],[x2,y2]=LB_POS[i+1];const len=Math.hypot(x2-x1,y2-y1),ang=Math.atan2(-(y2-y1),x2-x1)*180/Math.PI;const ln=img(S+(done>i+1?'partner_potential_light_big':'partner_potential_dark_big')+'.png','lb-line');
   ln.style.cssText=`left:calc(${340+(x1+x2)/2-len/2} * var(--u));top:calc(${150-(y1+y2)/2-5} * var(--u));width:calc(${len} * var(--u));transform:rotate(${ang}deg)`;box.append(ln);}
  for(let i=1;i<=5;i++){const pick=chosen[i-1]||0,skill=pick&&hero.potential_options?.[i-1]?.[pick-1],info=skill&&pots.skills[String(skill)];
   const n=el(live?'button':'span','lb-node n'+i+(i<=done?' open':i===done+1?' next':''));if(live)n.type='button';const [px,py]=LB_POS[i-1];n.style.left=`calc(${340+px} * var(--u))`;n.style.top=`calc(${150-py} * var(--u))`;
   if(info?.icon)n.append(img('/assets/skills/'+info.icon+'.png','lb-skill'));else if(i<=done)n.append(el('b','','?'));else n.append(img(S+'academy_assessment_lock.png','lb-lock'));
   n.title=info?info.name:i<=done?"Choose a Potential":'Unlocks at Limit-Break Stage '+i;
   if(live)n.onclick=()=>{if(i<=done)choosePotential(hero,i);else if(i===done+1)limitBreak(hero);else toast('Unlocks at Limit-Break Stage '+i);};box.append(n);}
  return box;}
 // PotentialityChooseWindow ("Select Potential" / Activate)
 function choosePotential(hero,stage){const opts=hero.potential_options?.[stage-1]||[];let sel=(hero.potentials||[])[stage-1]||0;const {body,close}=win({title:'Select Potential',cls:'lb-choose'});
  const list=el('div','lb-choose-list');const paint=()=>{list.replaceChildren();opts.forEach((id,k)=>{const info=pots.skills[String(id)]||{};const b=el('button','lb-opt'+(sel===k+1?' on':''));b.type='button';
   if(info.icon)b.append(img('/assets/skills/'+info.icon+'.png'));const t=el('div');t.append(el('b','',info.name||('Potencial '+id)),rich('p','',info.desc||''));b.append(t);if((hero.potentials||[])[stage-1]===k+1)b.append(el('span','lb-active','Activo'));b.onclick=()=>{sel=k+1;paint();};list.append(b);});};
  paint();body.append(list);const a=el('div','gs-btns');const ok=el('button','gs-btn','Activate');ok.type='button';ok.onclick=async()=>{if(!sel)return;close();await action('CHOOSE_PARTNER_POTENTIAL',{partner_id:hero.partner_id,awake_index:stage,index:sel});};a.append(ok);body.append(a);}
 function awake(hero){const box=$('detail-awake-status');if(!box)return;box.replaceChildren();const tab=document.querySelector('[data-detail-tab=awake]');if(tab)tab.textContent='Thức Tỉnh';
  if(hero.local_promotion&&hero.stars>=10&&!hero.next_awake){box.className='lb-low';box.append(el('p','gu-awake-head',hero.stars+'★'),el('p','detail-note','Nữ Thần này hiện chưa có công thức Thức Tỉnh tiếp theo trên máy chủ.'));return;}
  if(hero.stars<10&&!hero.next_awake){box.className='lb-low';box.append(el('p','gu-awake-head',hero.stars+'★'),el('p','detail-note',"Chưa có công thức nâng sao tiếp theo trong dữ liệu gốc của Nữ Thần này. Có thể xem Học Viện → Tiến Hóa để kiểm tra tiến trình phù hợp."));return;}
  box.className='lb-tab';const r=hero.next_awake;
  if(hero.stars<10&&r){
   box.classList.add('lb-progress-preview');
   // 4–5★ use original GRADUATE/COMPOSE_PARTNER; 6–9★ use native
   // AWAKE_PARTNER. Potentiality belongs ONLY to the 11★+ window.
   const top=el('button','lb-banner');top.type='button';top.append(stars(hero.stars,'tag'));
   top.onclick=()=>limitBreak(hero);top.title='Xem nguyên liệu Thức Tỉnh '+r.star+'★';box.append(top);
   box.append(el('p','detail-note',(r.kind==='compose'?'Tiến Hóa ':'Thức Tỉnh ')+hero.stars+'★ → '+r.star+'★'));
   // This tab must show the ORIGINAL server recipe, not a blank card or a
   // generic link. Every existing/future girl uses her own next_awake data.
   const picked=pick(r,hero),materials=selectedMaterials(r,picked);
   const req=el('div','lb-inline-materials');req.setAttribute('aria-label','Nguyên liệu Thức Tỉnh theo bảng gốc');
   (r.material||[]).forEach((code,i)=>{
    const g=materials[i],tile=el('span','lb-inline-material'+(g?' ok':''));
    const id=g?.table_id||(Number(code)%1000===999?0:Number(code));
    if(id)tile.append(card(Number(id)));else tile.append(el('b','lb-inline-star',Math.floor(Number(code)/10000)+'★'));
    tile.append(el('small','',g?'1/1':'0/1'));
    tile.title=g?g.name+' · '+g.stars+'★':codeLabel(Number(code));req.append(tile);
   });
   box.append(req);
   const expenses=el('div','lb-inline-cost');const enough=cost(expenses,r.cost||{});box.append(expenses);
   const go=el('button','gs-btn',(r.kind==='compose'?'Tiến Hóa':'Thức Tỉnh')+' · '+(materialsReady(r,picked)&&enough?'Đủ nguyên liệu':'Xem nguyên liệu'));
   go.type='button';go.onclick=()=>limitBreak(hero);box.append(go);return;
  }
  const top=el('button','lb-banner');top.type='button';top.append(stars(hero.stars,'tag'));if(r&&materialsReady(r,pick(r,hero))&&cost(el('span'),r.cost||{}))top.append(img(S+'alert_icon.png','lb-red'));top.onclick=()=>limitBreak(hero);top.title='Mở giao diện Thức Tỉnh gốc';top.setAttribute('aria-label','Mở công thức và vật liệu Thức Tỉnh Nữ Thần');box.append(top);
  box.append(nodes(hero,'tab'));
  const bar=el('div','lb-btns');for(const [label,fn]of [['Reverse',()=>reverse(hero)],['Replace',()=>exchange(hero)],['Switch',()=>switchPotentials(hero)]]){const b=el('button','gs-btn lb-small',label);b.type='button';b.onclick=fn;bar.append(b);}box.append(bar);}
 function limitBreak(hero){
   const r=hero.next_awake,{body,close}=win({title:'Thức Tỉnh',cls:'lb-win'});
   const picked=r?pick(r,hero):null,chosen=r?selectedMaterials(r,picked):[];
   const head=el('div','lb-head');head.append(stars(r?Number(r.star||hero.stars+1):hero.stars,'tag'));body.append(head);
   if(!r){body.append(el('p','lb-max',hero.stars>=25?"Đã đạt giới hạn 25★ · cấp 666.":"Chưa có dữ liệu Đột Phá tiếp theo cho Nữ Thần này."));return;}
   const targetStar=Number(r.star||hero.stars+1);
   const cap=r.kind==='compose'?'Theo hình thái gốc':targetStar<10?Number(hero.level_cap||0)+20:
     targetStar===10?Number(r.target_level_cap||250):
     CAPS[Math.max(0,Math.min(CAPS.length-1,targetStar-11))];
   const hpCycle=[14.56,14.56,9.62,9.62],atkCycle=[10.40,10.40,7.49,7.49];
   const hp=targetStar>=16?hpCycle[(targetStar-16)%4]:Number(pots.attr_up[0]||0)*100;
   const atk=targetStar>=16?atkCycle[(targetStar-16)%4]:Number(pots.attr_up[1]||0)*100;
   const pct=v=>Number(v).toFixed(2).replace(/\.?0+$/,'');
   const rows=el('div','lb-rows'),row=(k,v)=>{const d=el('div','lb-row');d.append(el('b','',k),el('span','',v));rows.append(d);};
   row('MAX LVL',String(cap));
   if(targetStar<11)row('Chỉ số','Tăng theo dữ liệu Thức Tỉnh gốc');
   else{row('HP','+'+pct(hp)+'%');row('ATK','+'+pct(atk)+'%');}
   if(targetStar>=16)row('DEF',String(100+(targetStar-15)*2)+'% so với 15★');body.append(rows);
   if(targetStar>=11){const un=el('div','lb-unlock');un.append(el('b','','Mở Khóa'));un.append(nodes({...hero,stars:targetStar},'win',false));body.append(un);}
   if(r.awake25){
    const addGroup=(label,items,required,emptyText)=>{
     body.append(el('p','detail-note',label+' · '+items.length+'/'+required));
     const grid=el('div','lb-mats wrap');
     for(let i=0;i<required;i++){
      const g=items[i],c=el('div','lb-mat'+(g?' ok':'')),pic=el('span','lb-pic');
      if(g)pic.append(card(Number(g.table_id)));else pic.append(el('i','',emptyText));
      c.append(pic,el('small','',(g?'1':'0')+'/1'));c.title=g?g.name+' · '+g.stars+'★ Lv. '+g.lv:label+' · thiếu '+(i+1);grid.append(c);
     }
     body.append(grid);
    };
    addGroup('Bản sao đúng Nữ Thần',picked.copies,Number(r.copies)||0,'Bản sao');
    addGroup('Nữ Thần hiến tế · hệ 1–6',picked.sacrifices,Number(r.sacrifices)||0,'Hiến tế');
   }else{
    const mats=el('div','lb-mats');
    (r.material||[]).forEach((code,i)=>{const g=chosen[i],c=el('div','lb-mat'+(g?' ok':'')),pic=el('span','lb-pic');
     const id=g?g.table_id:(code%1000===999?0:code);
     if(id&&cardIds.has(id))pic.append(img('/assets/cards/partner_card_'+id+'.png'));else pic.append(el('i','',Math.floor(code/10000)+'★'));
     c.append(pic,el('small','',(g?1:0)+'/1'));c.title=g?g.name+' · '+g.stars+"★ Lv. "+g.lv:codeLabel(code);mats.append(c);
    });body.append(mats);
   }
   const c=el('div','lb-cost'),ok=cost(c,r.cost||{});body.append(c);
   const compose=r.kind==='compose';
   const acts=el('div','gs-btns'),btn=el('button','gs-btn',compose?'Tiến Hóa Nữ Thần':'Thức Tỉnh');btn.type='button';btn.disabled=!ok||!materialsReady(r,picked);
   btn.onclick=async()=>{
    if(!materialsReady(r,picked))return;
    const involved=chosen.filter(g=>g?.pos);
    if(involved.length&&!await confirmGame('Có '+involved.length+' Nữ Thần nguyên liệu đang trong đội hình. Tiếp tục?',{title:'Xác Nhận Tiến Hóa',ok:'Tiếp tục',danger:true}))return;
    const ids=chosen.map(g=>g.partner_id);
    const message=compose?'COMPOSE_PARTNER':'AWAKE_PARTNER';
    const data=compose?{table_id:r.target,material_ids:[hero.partner_id,...ids]}:{partner_id:hero.partner_id,material_ids:ids};
    btn.disabled=true;
    try{const result=await action(message,data);if(result?.state){close();}else{btn.disabled=false;}}
    catch(err){btn.disabled=false;toast(err.message||'Không thể nâng sao');}
   };
   acts.append(btn);body.append(acts);
  }

  // ---- Reverse (PotentialityBackWindow), Exchange (TenStarExchangeWindow), Switch (PotentialitySwitchWindow) ----
 let ret=null;
 const card=(tid,cls='')=>{const c=el('span','lb-card '+cls);if(cardIds.has(tid))c.append(img('/assets/cards/partner_card_'+tid+'.png'));else{/* house dolls (561001…766001) share partner_avatar_661001 */const i=img('/assets/original-ui/portraits/partner_avatar_'+tid+'.png');i.onerror=()=>{i.onerror=null;i.src='/assets/original-ui/portraits/partner_avatar_661001.png';};c.append(i);}return c;};
 async function reverse(hero){if(!ret)ret=await api('/assets/partner-return.json');const rule=ret.rules[String(hero.stars)];const {body,close}=win({title:'Reverse',cls:'lb-rev',help:"Rebirth returns the Girl as faction Dolls and named 5★ copies, along with equipment and part of her EXP. This cannot be undone."});
  if(!rule||hero.group===7||hero.stars===6){body.append(el('p','',"This Girl cannot be reborn."));return;}
  body.append(el('b','lb-sub','Preview'));const grid=el('div','lb-mats');
  for(const part of String(rule['group_'+hero.group]||'').split('|')){if(!part.includes('#'))continue;const [tid,rest]=part.split('#');const [n,aw]=rest.split('@');const c=el('div','lb-mat ok');c.append(card(Number(tid)),el('small','','×'+n+' · '+(girlsCatalog.find(g=>g.id===Number(tid))?'':'')+(Number(aw||0)+Number(String(tid).startsWith('7')?10:String(tid).startsWith('6')?6:5))+'★'));grid.append(c);}
  const self=Number(rule.award_self||0);if(self){const c=el('div','lb-mat ok');c.append(card(hero.namesake||hero.table_id),el('small','','×'+self+' · 5★'));grid.append(c);}
  body.append(grid,el('p','detail-note',"Equipment, Antique, and 65% of spent Girl EXP are also returned to the Bag."));const c=el('div','lb-cost');const ok=cost(c,Object.fromEntries(String(rule.cost||'').split('|').filter(x=>x.includes('#')).map(x=>x.split('#').map(Number))));body.append(c);
  const a=el('div','gs-btns');const b=el('button','gs-btn red','Reverse');b.type='button';b.disabled=!ok||hero.flags?.[0];if(hero.flags?.[0])body.append(el('p','detail-note',"Unlock the Girl first (padlock)."));b.onclick=async()=>{if(!await confirmGame('Thao tác này không thể hoàn tác. Bạn có chắc muốn Hoàn Nguyên Nữ Thần này không?',{title:'Xác Nhận Hoàn Nguyên',ok:'Hoàn Nguyên',danger:true}))return;close();await action('ROLLBACK_PARTNER',{partner_id:hero.partner_id});const r=state.last_rollback;if(r){toast('Revertida: '+r.partner_ids.length+" Girls returned");const next=state.roster[0];if(next){selectedGirlPartnerId=next.partner_id;showView('girls');}}};a.append(b);body.append(a);}
 async function exchange(hero){if(!ret)ret=await api('/assets/partner-return.json');if(hero.group===7){toast("Cosmos Girls cannot be exchanged.");return;}
  const need=ret.replace_cost_hero[Math.min(ret.replace_cost_hero.length,hero.stars-9)-1];let pick=null;
  const options=[...new Map(state.roster.filter(g=>g.stars===5&&g.group===hero.group&&g.star_10&&g.star_10!==hero.table_id&&!g.flags?.some(Boolean)).map(g=>[g.table_id,g])).values()];
  const paint=()=>{const {body,close}=win({title:'Exchange',cls:'lb-ex',help:"Exchange a Girl of 10★ or higher for another 10★ Girl from the same faction. Level, grade, equipment, Crystal, Antique, and Limit Break are preserved. Costs 5 Diplomas and "+need+" identical copies of the 5★ Girl."});
   const box=el('div','lb-exbox');box.append(el('b','lb-sub','Please select required materials'));const row=el('div','lb-exrow');row.append(card(hero.table_id,'big'),el('span','lb-plus','+'));
   const copies=pick?state.roster.filter(g=>g.table_id===pick&&g.stars===5&&!g.flags?.some(Boolean)&&g.partner_id!==hero.partner_id):[];const m=el('button','lb-mat'+(copies.length>=need?' ok':''));m.type='button';m.append(pick?card(pick):el('span','lb-card empty','?'),el('small','',copies.length+'/'+need));m.onclick=()=>{close();choose();};row.append(m,el('span','lb-arrow','➜'));
   const target=pick&&girlsCatalog.find(g=>g.id===state.roster.find(x=>x.table_id===pick)?.star_10);row.append(target?card(target.id,'big'):el('span','lb-card big empty','?'));box.append(row);body.append(box);
   const a=el('div','gs-btns');const b=el('button','gs-btn','Replace');b.type='button';b.prepend(img('/assets/item-icons/'+(itemCatalog['47']?.icon||'icon_47')+'.png','lb-btn-icon'));b.disabled=!pick||copies.length<need||Number(state.items['47']||0)<5;b.onclick=async()=>{if(!await confirmGame('Đổi thành Nữ Thần 10★ '+(target?.name||'')+'?',{title:'Xác Nhận Chuyển Đổi',ok:'Chuyển Đổi'}))return;close();await action('REPLACE_10_STAR',{partner_id:hero.partner_id,material_ids:copies.slice(0,need).map(g=>g.partner_id)});toast("Exchange completed");};a.append(b);body.append(a,el('p','detail-note','Diplomas: '+number(state.items['47']||0)+' / 5'));};
  const choose=()=>{const {body,close}=win({title:'Please select the same girl',cls:'lb-ex'});if(!options.length)body.append(el('p','',"You have no eligible 5★ Girls from this faction with a 10★ form."));const g=el('div','lb-mats wrap');for(const o of options){const c=el('button','lb-mat ok');c.type='button';const n=state.roster.filter(x=>x.table_id===o.table_id&&x.stars===5).length;c.append(card(o.table_id),el('small','',o.name+' ×'+n));c.onclick=()=>{pick=o.table_id;close();paint();};g.append(c);}body.append(g);};
  paint();}
 // PotentialitySwitchWindow (capture fb/119): one row per Limit-Break stage (star badge + its 3 skills, the active one lit),
 // the tapped skill's detail at the bottom and Activate
 function switchPotentials(hero,sel){const done=Math.max(0,hero.stars-10);const {body,close}=win({title:'Switch',cls:'lb-switch',help:"1. After each Limit Break, activate one of three Potentials.\n2. Tap a Potential to see its details and press Activate; only one is active per stage."});
  sel=sel||(()=>{for(let i=1;i<=done;i++){const p=(hero.potentials||[])[i-1];if(p)return [i,p];}return done?[1,1]:null;})();
  const grid=el('div','sw-grid');for(let i=1;i<=5;i++){const row=el('div','sw-row'+(i<=done?'':' locked'));row.append(el('b','sw-star',String(i)));
   (hero.potential_options?.[i-1]||[]).forEach((id,k)=>{const info=pots.skills[String(id)]||{};const b=el('button','sw-skill'+((hero.potentials||[])[i-1]===k+1?' on':'')+(sel&&sel[0]===i&&sel[1]===k+1?' sel':''));b.type='button';if(info.icon)b.append(img('/assets/skills/'+info.icon+'.png'));b.title=info.name||'';
    b.onclick=()=>{if(i>done){toast('Unlocks at Limit-Break Stage '+i);return;}close();switchPotentials(hero,[i,k+1]);};row.append(b);});grid.append(row);}
  body.append(grid);
  const det=el('div','sw-detail');if(sel){const id=hero.potential_options?.[sel[0]-1]?.[sel[1]-1],info=pots.skills[String(id)]||{};if(info.icon)det.append(img('/assets/skills/'+info.icon+'.png'));const t=el('div');t.append(el('b','',info.name||''),rich('p','',info.desc||''));det.append(t);}else det.append(el('p','',"No Limit Break stages unlocked yet."));body.append(det);
  const a=el('div','gs-btns');const ok=el('button','gs-btn','Activate');ok.type='button';const active=sel&&(hero.potentials||[])[sel[0]-1]===sel[1];ok.disabled=!sel||active;if(active)ok.textContent='Activo';
  ok.onclick=async()=>{close();await action('CHOOSE_PARTNER_POTENTIAL',{partner_id:hero.partner_id,awake_index:sel[0],index:sel[1]});const h=state.roster.find(x=>x.partner_id===hero.partner_id);if(h)switchPotentials(h,sel);};a.append(ok);body.append(a);}

 // ---- Astral Core (tab_5, StarOriginDetailWindow; capture fb/54): 15★ girls with partner.star_origin; 10 nodes placed with
 // star_origin_node xy (Unity y up), lines to their unlock node, "Node Upgrade" window (level, effect now → next, cost).
 let astral=null;
 const ROMAN=['I','II','III','IV','V','VI','VII','VIII','IX','X'],AN={hp:'HP',atk:'Attack',arm:'Armor',spd:'Speed',hpP:'HP %',atkP:'Attack %',crit:'Crit',critTime:'Crit DMG',hit:'Precision',miss:'Block',sklP:'Skill DMG',trueAtk:'Holy DMG',decDmg:'DMG Red.',free:'CC Immune',unfree:'Control Rate',brk:'Armor Brk',unCrit:'Crit Resist'};
 const effOf=t=>Object.fromEntries(String(t||'').split('|').filter(x=>x.includes('#')).map(x=>{const [k,v]=x.split('#');return [k,Number(v)];}));
 const fmtA=(k,v)=>k.endsWith('P')?(v*100).toFixed(1)+'%':number(Math.round(v));
 async function astralTab(hero){const nav=document.querySelector('#girl-detail-view>.detail-tabs');let tab=nav.querySelector('[data-detail-tab=astral]');
  if(!hero.astral_list){tab?.remove();document.getElementById('detail-astral')?.remove();nav.classList.remove('five');if(detailTab==='astral'){detailTab='attribute';renderGirlDetail();}return;}
  if(!tab){tab=el('button','','Astral Core');tab.dataset.detailTab='astral';tab.type='button';tab.onclick=()=>{detailTab='astral';renderGirlDetail();};nav.append(tab);}nav.classList.add('five');tab.classList.toggle('active',detailTab==='astral');
  let sec=document.getElementById('detail-astral');if(!sec){sec=el('section');sec.id='detail-astral';document.querySelector('#girl-detail-view>.detail-panel').append(sec);}sec.hidden=detailTab!=='astral';if(sec.hidden)return;
  if(!astral)astral=await api('/assets/astral.json');const lst=astral.lists[String(hero.astral_list)];const levs=(hero.star_origin||[]).concat(Array(10).fill(0)).slice(0,10);sec.replaceChildren();
  sec.append(constellation(hero,'tab',-1,k=>nodeUpgrade(hero,k)));
  {const emp=el('button','gs-btn as-empower','Empower');emp.type='button';emp.onclick=()=>{const lst2=astral.lists[String(hero.astral_list)];const lv=(hero.star_origin||[]).concat(Array(10).fill(0));const k=lst2.limits.findIndex(([p,need],i)=>(p<1||lv[p-1]>=need)&&lv[i]<lst2.end[i]-lst2.start[i]);nodeUpgrade(hero,k<0?0:k);};sec.append(emp);}const tot={};levs.forEach((v,k)=>{for(const [a,x]of Object.entries(effOf(astral.levels[String(lst.start[k]+v)]?.effect)))tot[a]=(tot[a]||0)+x;});
  const sum=el('div','as-sum');for(const [a,x]of Object.entries(tot))if(x)sum.append(el('span','',(AN[a]||a)+' +'+fmtA(a,x)));if(!sum.childElementCount)sum.append(el('span','',"Upgrade nodes with Brilliant / Tarnished Spheres."));sec.append(sum);
  const rs=el('button','gs-btn white as-reset','Reset');rs.type='button';rs.onclick=async()=>{if(!await confirmGame("Đặt lại Lõi Tinh Tú với "+astral.reset_cost.split('#')[1]+" Kim Cương? Nguyên liệu sẽ được trả về Túi Đồ.",{title:"Đặt Lại Lõi Tinh Tú",ok:"Đặt Lại",danger:true}))return;await action('RESET_STAR_ORIGIN',{partner_id:hero.partner_id});};sec.append(rs);}
 // StarOriginNodeItem states: 1 locked (…_zh), 2 open at Lv.0 (…_kq), levelled / max (…_dl); lines use the same name + "_1".
 function nodeState(lst,levs,k){const [pre,need]=lst.limits[k];if(pre>=1&&levs[pre-1]<need)return 'zh';return levs[k]>0?'dl':'kq';}
 function groupImg(hero,n){const g=girlsCatalog.find(x=>x.id===hero.table_id)?.group||hero.group;const k=n===1?'':'2';return g===7?(astral['group7_img'+k]||{})[String(hero.table_id)]:(astral['group_img'+k]||{})[String(g)];}
 // Constellation: tab (content_6, 710×426, nodes xy×0.66, 48 u) or window (StarOriginDetailWindow mainContent, nodes xy, 70 u).
 function constellation(hero,mode,sel,onPick){const lst=astral.lists[String(hero.astral_list)];const levs=(hero.star_origin||[]).concat(Array(10).fill(0)).slice(0,10);
  const win_=mode==='win',W=win_?660:672,H=win_?540:400,cx=W/2,cy=win_?280:H/2+10,sc=win_?1:.66,size=win_?70:48,pre=win_?'star_origin_bg_xy_sj_':'star_origin_bg_xy_';
  const [lx,ly]=(astral.list_xy||{})[String(hero.astral_list)]||[0,0];const map=el('div','as-map2 '+mode);map.style.width=`calc(${W} * var(--u))`;map.style.height=`calc(${H} * var(--u))`;
  const art=groupImg(hero,win_?2:1);if(art){const g=img(S+art+'.png','as-group');if(win_){g.style.cssText=`left:0;width:calc(660 * var(--u));top:calc(${cy-97-436} * var(--u));height:calc(872 * var(--u))`;}else{g.style.cssText=`left:calc(${cx-116} * var(--u));top:calc(${cy-42-107} * var(--u));width:calc(232 * var(--u));height:calc(214 * var(--u))`;}map.append(g);}
  const pos=lst.nodes.map(n=>astral.nodes[String(n)]||[0,0]).map(([x,y])=>[cx+lx+x*sc,cy-(ly+y*sc)]);
  lst.limits.forEach(([p],k)=>{if(p<1)return;const [x1,y1]=pos[p-1],[x2,y2]=pos[k];const len=Math.hypot(x2-x1,y2-y1),ang=Math.atan2(y2-y1,x2-x1)*180/Math.PI+90;const st=nodeState(lst,levs,k);
   const ln=img(S+pre+st+'_1.png','as-line');ln.style.cssText=`left:calc(${(x1+x2)/2-(win_?3:2)} * var(--u));top:calc(${(y1+y2)/2-len/2} * var(--u));width:calc(${win_?6:4} * var(--u));height:calc(${len} * var(--u));transform:rotate(${ang}deg)`;map.append(ln);});
  lst.limits.forEach(([p,need],k)=>{const [x,y]=pos[k],top=lst.end[k]-lst.start[k],st=nodeState(lst,levs,k);const b=el('button','as-star '+st+(sel===k?' sel':''));b.type='button';
   b.style.cssText=`left:calc(${x-size/2} * var(--u));top:calc(${y-size/2} * var(--u));width:calc(${size} * var(--u));height:calc(${size} * var(--u))`;b.append(img(S+pre+st+'.png'));
   if(win_){if(sel===k)b.append(img(S+'star_origin_bg_xy_sj_xz.png','as-choose'));const lb=el('span','as-lab',levs[k]+'/'+top);b.append(lb);}
   b.title='Node '+ROMAN[k]+' · Lv.'+levs[k]+'/'+top+(st==='zh'?' · requires node '+ROMAN[p-1]+' Lv.'+need:'');b.onclick=()=>st==='zh'?toast("Upgrade node "+ROMAN[p-1]+" to level "+need):onPick(k);map.append(b);});
  return map;}
 function nodeUpgrade(hero,k){const lst=astral.lists[String(hero.astral_list)];const v=((hero.star_origin||[])[k]||0),top=lst.end[k]-lst.start[k];const cur=effOf(astral.levels[String(lst.start[k]+v)]?.effect),nxt=v<top?effOf(astral.levels[String(lst.start[k]+v+1)]?.effect):null;
  const {body,close}=win({title:'Node Upgrade',cls:'as-win'});body.append(constellation(hero,'win',k,i=>{close();nodeUpgrade(hero,i);}));const info=el('div','as-info');info.append(el('b','as-name','Astral Core Node '+ROMAN[k]),el('span','as-lv','lv.'+v+'/'+top));body.append(info);
  const rows=el('div','lb-rows');for(const a of new Set([...Object.keys(cur),...Object.keys(nxt||{})])){const d=el('div','lb-row');d.append(el('b','',AN[a]||a),el('span','',fmtA(a,cur[a]||0)+(nxt?' ▸ '+fmtA(a,nxt[a]||0):'')));rows.append(d);}body.append(rows);
  if(!nxt){body.append(el('p','detail-note',"Node is at maximum level."));return;}const c=el('div','lb-cost');const ok=cost(c,effOf(astral.levels[String(lst.start[k]+v+1)].cost));body.append(c);
  const a=el('div','gs-btns');for(const [t,label]of [[1,'Upgrade'],[10,'×10']]){const b=el('button','gs-btn'+(t>1?' white':''),label);b.type='button';b.disabled=!ok;b.onclick=async()=>{close();await action('UPGRADE_STAR_ORIGIN',{partner_id:hero.partner_id,node:k+1,times:t});const h=state.roster.find(x=>x.partner_id===hero.partner_id);if(h&&(h.star_origin||[])[k]>v)nodeUpgrade(h,k);};a.append(b);}body.append(a);}

 // ---- Skill-Synchronize (SkillResonateWindow, Cosmic girls): ring with the 4 elite skills (bg2 nodes at 0/90/180/270°),
 // "Synchronize Level" = Σ skill levels (1-10 each) and the cumulative skill_resonate_effect bonuses; a skill opens its detail
 // (current / next level text, cost skill_resonate_cost, upgrade).
 let reso=null;
 // NGUI rich text: [c][rrggbb]text[-][/c] → coloured span (text escaped first)
 function rich(tag,cls,text){const e=el(tag,cls);const safe=String(text||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'})[c]);e.innerHTML=safe.replace(/\[c\]\[([0-9a-fA-F]{6})\]([\s\S]*?)\[-\]\[\/c\]/g,'<span style="color:#$1">$2</span>').replace(/\[\/?[a-z-]*\]/g,'');return e;}
 const RN={crit:'Crit',critTime:'Crit DMG',hit:'Precision'};
 async function resonate(hero){if(!reso)reso=await api('/assets/resonate.json');const host=sheetRoot();host.querySelector('.gs-overlay')?.remove();const ov=el('div','gs-overlay rs-ov');ov.onclick=e=>{if(e.target===ov)ov.remove();};
  const w=el('div','rs-win');ov.append(w);host.append(ov);const skills=(hero.ex_skills||[0,0,0,0]).concat([0,0,0,0]).slice(0,4);const level=skills.reduce((a,b)=>a+b,0)+4;
  w.append(img('/assets/souls/skill_resonate_effect_bg4.png','rs-ring'));
  const icons=[...document.querySelectorAll('#detail-skills .detail-skill img')].map(i=>i.src);
  skills.forEach((lv,i)=>{const n=el('button','rs-node n'+(i+1));n.type='button';if(icons[i])n.append(img(icons[i],'rs-icon'));n.append(el('b','rs-lv',String(lv+1)));n.onclick=()=>skillDetail(hero,i);w.append(n);});
  const info=el('div','rs-info');info.append(el('span','rs-title','Synchronize Level'),el('b','rs-level',String(level)));const effs=reso.effects[String(hero.table_id)]||[];const cur=[...effs].reverse().find(x=>level>=x.level);
  const list=el('div','rs-attrs');for(const part of String(cur?.effect||'').split('|')){const [k,v]=part.split('#');if(!k)continue;const d=el('div','rs-attr');d.append(el('b','',RN[k]||k),el('span','',(Number(v)/20).toFixed(1)+'%'));list.append(d);}info.append(list);
  const next=effs.find(x=>x.level>level);if(next){const [k,v]=String(next.show).split('#');info.append(el('small','rs-next',"Level "+next.level+': '+(RN[k]||k)+' +'+(Number(v)/20).toFixed(1)+'%'));}
  w.append(info);}
 function skillDetail(hero,i){const lv=((hero.ex_skills||[])[i]||0);const base=hero.table_id*1000+(i+1)*100;const cur=reso.skills[String(base+lv+1)]||["Skill",''],nxt=reso.skills[String(base+lv+2)];
  const {body}=win({title:cur[0],cls:'rs-detail'});const a=el('div','rs-box');a.append(el('b','',"Current level · "+(lv+1)+'/'+(reso.max+1)),rich('p','',cur[1]));body.append(a);
  if(nxt){body.append(img('/assets/souls/skill_resonate_effect_arrow.png','rs-arrow'));const b=el('div','rs-box');b.append(el('b','',"Next level · "+(lv+2)),rich('p','',nxt[1]));body.append(b);
   const c=el('div','gu-grade');const ok=cost(c,hero.resonate?.costs?.[i]||{});body.append(c);const acts=el('div','gs-btns');const up=el('button','gs-btn','Lv. Up');up.type='button';up.disabled=!ok;up.onclick=async()=>{await action('UPGRADE_PARTNER_EX_SKILL',{partner_id:hero.partner_id,index:i+1});const h=state.roster.find(x=>x.partner_id===hero.partner_id);if(h){await resonate(h);skillDetail(h,i);}};acts.append(up);body.append(acts);}
  else body.append(el('p','detail-note',"Skill is at maximum level."));}

 // ---- common window over the sheet (9gongge21 frame: blue title bar, close_btn_2, help_2) and toast ----
 function sheetRoot(){return view==='detail'?$('girl-detail-view'):(document.querySelector('#game-root>section:not([hidden])')||window.GxbFrame?.root()||$('game-root')||document.body);}
 function win({title='',help=null,cls='',plain=false,stack=false}={}){const host=sheetRoot();if(!stack)host.querySelector('.gs-overlay')?.remove();const ov=el('div','gs-overlay');const w=el('div','gs-win'+(plain?' plain':'')+(cls?' '+cls:''));ov.append(w);
  const close=()=>ov.remove();ov.onclick=e=>{if(e.target===ov)close();};
  if(!plain){const bar=el('div','gs-win-bar');bar.append(el('b','',title));const x=el('button','gs-win-x');x.type='button';x.onclick=close;bar.append(x);if(help){const h=el('button','gs-win-help');h.type='button';h.onclick=()=>CampaignUI.popup(help,{});bar.append(h);}w.append(bar);}
  const body=el('div','gs-win-body');w.append(body);host.append(ov);return {body,close,win:w};}
 function notice(message,{title="Thông Báo"}={}){const {body,close}=win({title,cls:"gs-notice"});body.append(el("p","gs-confirm-text",String(message||"")));const actions=el("div","gs-btns");const ok=el("button","gs-btn","Đóng");ok.type="button";ok.onclick=close;actions.append(ok);body.append(actions);return close;}
 function toast(text){const host=sheetRoot();if(!host||!text)return;host.querySelector('.gs-toast')?.remove();const t=el('div','gs-toast',text);host.append(t);setTimeout(()=>t.remove(),2200);}
 function confirmGame(message,{title='Xác Nhận',ok='Đồng Ý',cancel='Hủy',danger=false}={}){return new Promise(resolve=>{const host=sheetRoot();host.querySelector('.gs-confirm-overlay')?.remove();const ov=el('div','gs-overlay gs-confirm-overlay');const w=el('div','gs-win gs-confirm');const bar=el('div','gs-win-bar');bar.append(el('b','',title));w.append(bar);const body=el('div','gs-win-body');body.append(el('p','gs-confirm-text',message));const actions=el('div','gs-btns');const no=el('button','gs-btn white',cancel);const yes=el('button','gs-btn'+(danger?' red':''),ok);no.type=yes.type='button';let done=false;const finish=value=>{if(done)return;done=true;ov.remove();resolve(value);};no.onclick=()=>finish(false);yes.onclick=()=>finish(true);actions.append(no,yes);body.append(actions);w.append(body);ov.append(w);ov.onclick=e=>{if(e.target===ov)finish(false);};host.append(ov);yes.focus();});}
 // Star display as in the client: 1–5 yellow stars, 6–9 red stars (stars−5), 10 winged emblem, 11–15 emblem with number.
 function promptText(message,{title='Nhập Nội Dung',value='',maxLength=100,minLength=1,ok='Xác Nhận',cancel='Hủy'}={}){
    return new Promise(resolve=>{
      const host=sheetRoot(),ov=el('div','gs-overlay gs-text-overlay'),w=el('div','gs-win gs-number'),bar=el('div','gs-win-bar');
      bar.append(el('b','',title));w.append(bar);
      const body=el('div','gs-win-body'),label=el('label','gs-number-label',String(message||'Nhập nội dung'));
      const input=el('input','gs-number-input');input.type='text';input.autocomplete='off';
      input.maxLength=maxLength;input.value=String(value||'').slice(0,maxLength);
      label.append(input);body.append(label);const actions=el('div','gs-btns');
      const no=el('button','gs-btn white',cancel),yes=el('button','gs-btn',ok);no.type=yes.type='button';
      let done=false;const finish=v=>{if(done)return;done=true;ov.remove();resolve(v);};
      no.onclick=()=>finish(null);
      yes.onclick=()=>{const v=input.value.trim();if(v.length<minLength||v.length>maxLength){input.focus();return;}finish(v);};
      input.onkeydown=e=>{if(e.key==='Enter')yes.click();if(e.key==='Escape')finish(null);};
      actions.append(no,yes);body.append(actions);w.append(body);ov.append(w);ov.onclick=e=>{if(e.target===ov)finish(null);};
      host.append(ov);input.focus();
    });
  }
 function promptNumber(message,{title='Chọn Số Lượng',value=1,min=1,max=999,ok='Xác Nhận',cancel='Hủy'}={}){
    return new Promise(resolve=>{
      const host=sheetRoot(),ov=el('div','gs-overlay gs-number-overlay'),w=el('div','gs-win gs-number'),bar=el('div','gs-win-bar');
      bar.append(el('b','',title));w.append(bar);
      const body=el('div','gs-win-body'),label=el('label','gs-number-label',String(message||'Nhập số lượng'));
      const input=el('input','gs-number-input');input.type='number';input.inputMode='numeric';input.step='1';
      input.min=String(min);input.max=String(max);input.value=String(Math.min(max,Math.max(min,Number(value)||min)));
      label.append(input);body.append(label);const actions=el('div','gs-btns');
      const no=el('button','gs-btn white',cancel),yes=el('button','gs-btn',ok);no.type=yes.type='button';
      let done=false;const finish=n=>{if(done)return;done=true;ov.remove();resolve(n);};
      no.onclick=()=>finish(null);
      yes.onclick=()=>{const n=Number(input.value);if(!Number.isFinite(n)||!Number.isInteger(n)||n<min||n>max){input.focus();return;}finish(n);};
      input.onkeydown=e=>{if(e.key==='Enter')yes.click();if(e.key==='Escape')finish(null);};
      actions.append(no,yes);body.append(actions);w.append(body);ov.append(w);ov.onclick=e=>{if(e.target===ov)finish(null);};
      host.append(ov);input.focus();
    });
  }
 function stars(n,kind='card'){n=Number(n)||0;const w=el('span','gu-stars '+kind);if(n>=10){const base=kind==='tag'?'potentiality_nametag_star':'potentiality_card_star';w.append(img('/assets/girl-ui/'+base+(n>=15?'_max':'')+'.png','gu-emblem'));if(n>10)w.append(el('b','gu-emblem-num',String(n-10)));}else{const red=n>5;for(let i=0;i<(red?n-5:n);i++)w.append(img('/assets/girl-ui/partner_star_'+(red?'red':'yellow')+'.png','gu-star'));}w.title=n+'★';return w;}
 return {detail,load,picture,stars,win,toast,notice,promptNumber,promptText,confirm:confirmGame,eliteSkills,resonate,reverse,rich};
})();
