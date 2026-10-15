'use strict';
// Equipment UI: Gear tab of the girl sheet, real attributes (HeroAttr), Smithy forge and antique upgrade.
// Sources: PartnerDetailWindow.lua, SmithyWindow.lua (+ smithy_window.prefab), ArtifactUpWindow.lua.
const Equipment=(()=>{
 const SLOTS=[[1,'Vũ khí','partner_weapon'],[2,'Áo','partner_cloth'],[3,'Phụ kiện','partner_pants'],[4,'Giày','partner_shoes'],[5,'Bảo vật','partner_treasure'],[6,'Cổ vật','partner_artifact']];
 const SMITHY_TABS=[[1,'Vũ khí'],[2,'Áo'],[3,'Phụ kiện'],[4,'Giày']];
 const STAT_KEYS=[['hp','HP','attr_hp_icon'],['atk','ATK','attr_atk_icon'],['arm','DEF','attr_def_icon'],['spd','SPD','attr_spd_icon']];
 const EXTRA=['hit','crit','critTime','brk','miss','sklP','trueAtk','unCrit','decDmg','free','unfree','zs','fs','yx','ck','ms'];
 let data=null,loading=null,slot=1,pending=false,message='',attrCache={},attrKey='',smithyPos=1,smithyItem=null,smithyCount=1,feed={},artifactTarget=null,smithyBack='bag';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.loading='lazy';return i;};
 const fmt=n=>number(Math.round(Number(n)||0));
 const load=()=>data?Promise.resolve(data):(loading||=api('/assets/equipment/catalog.json').then(d=>{data=d;return d;}));
 const row=id=>data.items[String(id)];
 const have=id=>Number(state.items[String(id)]||0);
 function pairs(text){return String(text||'').split('|').filter(s=>s.includes('#')).map(s=>s.split('#'));}
 function attrText(key,value){const name=data.attr_names[key]||key;const v=Number(value);return name+' +'+(v<1&&v>0||key.endsWith('P')||['zs','fs','yx','ck','ms'].includes(key)?(v*100).toFixed(v*100%1?1:0)+'%':fmt(v));}
 function icon(id,extra=''){const r=row(id),w=el('span','eq-icon '+extra);w.style.backgroundImage=`url('/assets/ui/quality_${Math.min(r?.qlt||0,7)}.png')`;if(r)w.append(img(data.icons[String(id)]||'/assets/ui/item_bg.png','',r.name));if(r&&r.pos!==5&&r.star){const st=el('span','eq-stars');for(let i=0;i<Math.min(r.star,6);i++)st.append(img('/assets/equipment/equip_star.png'));w.append(st);}return w;}
 function lines(parent,id,partner){const r=row(id);if(!r)return;const list=el('ul','eq-lines');for(const k of ['base1','base2','base3','base4'])for(const [a,v]of pairs(r[k]))list.append(el('li','',attrText(a,v)));
  if(r.act){const ok=partner&&((r.job&&r.job===jobOf(partner))||(r.group&&r.group===groupOf(partner)));const li=el('li','eq-act'+(ok?' on':''),(r.job?'Clase '+data.jobs[r.job]:"Faction "+r.group)+': '+pairs(r.act).map(([a,v])=>attrText(a,v)).join(', '));list.append(li);}
  if(r.form){const pieces=String(r.form).split('|').map(Number),worn=partner?pieces.filter(p=>partner.equips?.includes(p)).length:0;for(const [n,k]of [[2,'suit1'],[3,'suit2'],[4,'suit3']])if(r[k])list.append(el('li','eq-suit'+(worn>=n?' on':''),'Conjunto '+n+'/4: '+pairs(r[k]).map(([a,v])=>attrText(a,v)).join(', ')));}
  if(r.suit_skill_names)list.append(el('li','eq-suit',"Set Skill: "+r.suit_skill_names.join(' / ')));
  parent.append(list);}
 function jobOf(p){return Number(data.partner_jobs[String(p.table_id)]||0);}
 function groupOf(p){return Number(data.partner_groups[String(p.table_id)]||0);}
 function cost(parent,text,label){const c=el('span','eq-cost');for(const [id,n]of pairs(text)){const ok=have(id)>=Number(n);const s=el('span',ok?'':'short');const src=id==='1'?'/assets/equipment/icon_1.png':id==='2'?'/assets/currency/icon_2_small.png':itemIconSrc(id);if(src)s.append(img(src));s.append(el('b','',fmt(n)));s.title=(itemCatalog[id]?.name||"Item "+id)+" · owned: "+fmt(have(id));c.append(s);}if(label)c.prepend(el('small','',label));parent.append(c);}
 function itemIconSrc(id){const it=itemCatalog[id];if(it&&itemIcons.has(it.icon))return '/assets/item-icons/'+it.icon+'.png';return data.icons[String(id)]||'';}
 function affordable(text){return pairs(text).every(([id,n])=>have(id)>=Number(n));}
 async function send(request,after){if(pending)return;pending=true;message='Guardando…';try{const r=await api('/api/equipment/action',request);state=r.state;message=after?after(r):'';}catch(e){message=e.message;}finally{pending=false;render();if(view==='detail'&&message&&typeof GirlUI!=='undefined')GirlUI.toast(message);}}
 function refresh(){if(view==='detail')renderGirlDetail();if(view==='smithy')renderSmithy();}
 function btn(parent,label,fn,disabled=false,cls='eq-btn'){const b=el('button',cls,label);b.type='button';b.disabled=pending||disabled;b.onclick=fn;parent.append(b);return b;}

 // ---- Gear tab (content_2 of partner_detail_window) ----
 // The board only: tapping a filled slot opens item_tips_window (Remove / Replace; the crystal: Exchange / Lv. Up;
 // antiques add Lv. Up), tapping an empty one opens choose_equip_window with the matching gear of the Bag.
 const SLOT_TITLE={1:'Weapon',2:'Clothes',3:'Accessory',4:'Shoes',5:'Crystal',6:'Antique'};
 const W=o=>GirlUI.win(o);
 function gear(hero){const host=$('detail-gear');if(!host)return;for(const c of host.children)if(!c.classList.contains('eq-root'))c.hidden=true;let root=host.querySelector('.eq-root');if(!root){root=el('div','eq-root');host.append(root);}if(!data){root.replaceChildren(el('p','detail-note',"Loading equipment…"));load().then(()=>view==='detail'&&renderGirlDetail());return;}
  const eq=(hero.equips||[]).concat([0,0,0,0,0,0,0]).slice(0,7);root.replaceChildren();
  const grid=el('div','eq-board');grid.append(img('/assets/detail/sheet/equip_bg.png','eq-board-bg'),img('/assets/detail/sheet/equip_bg.png','eq-board-bg flip'));
  for(const [s,,art]of SLOTS){const b=el('button','eq-slot s'+s);b.type='button';const id=eq[s-1];
   if(id&&row(id))b.append(icon(id));else{b.append(img('/assets/detail/sheet/item_icon_bg01.png','eq-empty-bg'),img('/assets/detail/sheet/'+art+'.png','eq-empty'));if(s===5?hero.lv>=data.treasure_open_level:bagFor(s,hero).length)b.append(img('/assets/detail/sheet/icon_add.png','eq-plus'));}
   b.title=id&&row(id)?row(id).name:SLOT_TITLE[s];b.onclick=()=>{slot=s;message='';if(id&&row(id))tip(hero,s,id);else if(s===5)treasureWin(hero,'unlock');else choose(hero,s);};grid.append(b);}
  const bar=el('div','eq-main-btns');btn(bar,'Unequip',()=>send({action:'unequip_all',partner_id:hero.partner_id}),![1,2,3,4,6].some(s=>eq[s-1]),'gs-btn red eq-big');btn(bar,'Gear Up',()=>send({action:'equip_all',partner_id:hero.partner_id}),false,'gs-btn eq-big');grid.append(bar);
  root.append(grid);}
 function bagFor(s,hero){return Object.entries(state.items).filter(([id,n])=>Number(n)>0&&row(id)?.pos===s).map(([id,n])=>({id:Number(id),n:Number(n),r:row(id)})).sort((a,b)=>b.r.item_lv-a.r.item_lv||a.id-b.id);}
 // item_tips_window
 function tip(hero,s,id){const r=row(id);const {body,close}=W({plain:true,cls:'eq-tip'});
  body.append(el('b','eq-tip-name',r.name+(s===5?'':'')));const top=el('div','eq-tip-top');top.append(icon(id));body.append(top);lines(body,id,hero);
  const acts=el('div','gs-btns');
  if(s===5){btn(acts,'Exchange',()=>{close();treasureWin(hero,'exchange');},false,'gs-btn');btn(acts,'Lv. Up',()=>{close();treasureWin(hero,'up');},!r.treasure_upgrade,'gs-btn');}
  else{btn(acts,'Remove',()=>{close();send({action:'unequip',partner_id:hero.partner_id,slot:s});},false,'gs-btn red');
   if(s===6&&r.artifact_next)btn(acts,'Lv. Up',()=>{close();openArtifact(id,hero.partner_id);},false,'gs-btn');
   btn(acts,'Replace',()=>{close();choose(hero,s);},!bagFor(s,hero).length,'gs-btn');}
  body.append(acts);}
 // choose_equip_window
 function choose(hero,s){const {body,close}=W({title:SLOT_TITLE[s],cls:'eq-choose'});const mine=jobOf(hero),list=bagFor(s,hero).sort((a,b)=>(Number(b.r.job||0)===mine)-(Number(a.r.job||0)===mine));let pick=null;
  body.append(el('p','eq-choose-label','Select the Gear to equip:'));const grid=el('div','eq-choose-grid');const info=el('div','eq-choose-info');
  const paint=()=>{info.replaceChildren();if(!pick){info.append(el('p','detail-note',list.length?"Tap a piece to view its attributes.":"You have no "+SLOT_TITLE[s].toLowerCase()+" in the Bag."+(s<=4?" Obtain them in Campaign or Forge.":'')));return;}
   const r=row(pick);info.append(el('b','',r.name));lines(info,pick,hero);const job=Number(r.job||0),bad=job&&jobOf(hero)&&job!==jobOf(hero);const a=el('div','gs-btns');btn(a,bad?'Clase '+data.jobs[job]:'Equip',()=>{close();send({action:'equip',partner_id:hero.partner_id,item_id:pick});},!!bad,'gs-btn');info.append(a);};
  for(const {id,n}of list){const b=el('button','eq-choose-item');b.type='button';b.append(icon(id));if(n>1)b.append(el('small','',String(n)));b.onclick=()=>{pick=id;grid.querySelectorAll('.on').forEach(x=>x.classList.remove('on'));b.classList.add('on');paint();};grid.append(b);}
  body.append(grid,info);paint();
  if(s<=4){const f=el('div','gs-btns');btn(f,"Forge",()=>{close();openSmithy(s,'detail');},false,'gs-btn white');body.append(f);}}
 // crystal (treasure): unlock, Exchange (treasure_change_window: new random attribute) and Lv. Up (treasure_up_window)
 function treasureWin(hero,mode){const eq=(hero.equips||[])[4];const title=mode==='up'?'Lv. Up':mode==='exchange'?'Exchange':'Crystal';const {body,close}=W({title,cls:'eq-treasure'});if(typeof ImgGuides!=='undefined'){const h=btn(body,'?',()=>ImgGuides.open('treasure_guide'),false,'ig-native-question');h.setAttribute('aria-label',"Crystal Help");}
  if(!eq){body.append(el('p','',"The Crystal unlocks for free when the Girl reaches level "+data.treasure_open_level+'. Su atributo es aleatorio.'));const a=el('div','gs-btns');btn(a,'Unlock',()=>{close();send({action:'treasure_on',partner_id:hero.partner_id},r=>"Obtained: "+row(r.treasure).name);},hero.lv<data.treasure_open_level,'gs-btn');body.append(a);return;}
  const r=row(eq),cur=el('div','eq-current');cur.append(icon(eq));const inf=el('div');inf.append(el('strong','',r.name+" · Lv. "+r.item_lv));lines(inf,eq,hero);cur.append(inf);body.append(cur);
  if(hero.tmp_treasure){const pre=el('div','eq-current eq-preview');pre.append(icon(hero.tmp_treasure));const pi=el('div');pi.append(el('strong','',"New: "+row(hero.tmp_treasure).name));lines(pi,hero.tmp_treasure,hero);pre.append(pi);body.append(pre);const b=el('div','gs-btns');btn(b,'Descartar',()=>{close();send({action:'treasure_discard',partner_id:hero.partner_id});},false,'gs-btn white');btn(b,"Save",()=>{close();send({action:'treasure_save',partner_id:hero.partner_id});},false,'gs-btn');body.append(b);return;}
  const box=el('div','eq-actions');
  if(mode==='exchange'){const rf=el('div','eq-action');rf.append(el('b','',"New random attribute at the same level"));cost(rf,r.treasure_refresh);body.append(rf);const a=el('div','gs-btns');btn(a,'Exchange',()=>send({action:'treasure_refresh',partner_id:hero.partner_id},()=>{setTimeout(()=>treasureWin(state.roster.find(h=>h.partner_id===hero.partner_id),'exchange'),0);return '';}),!affordable(r.treasure_refresh),'gs-btn');body.append(a);return;}
  if(!r.treasure_upgrade){body.append(el('p','detail-note',"Crystal is at maximum level."));return;}
  const up=el('div','eq-action');up.append(el('b','',"Level up (random attribute)"));cost(up,r.treasure_upgrade);btn(up,'Lv. Up',()=>{close();send({action:'treasure_upgrade',partner_id:hero.partner_id},x=>"New: "+row(x.treasure).name);},!affordable(r.treasure_upgrade),'gs-btn');box.append(up);
  const [target,extra]=String(r.treasure_lock_up||'').split('|');if(target&&row(target)){const lk=el('div','eq-action');lk.append(el('b','',"Upgrade while keeping the attribute → "+row(target).name));const total=pairs(r.treasure_upgrade).map(([k,v])=>[k,Number(v)+Number(pairs(extra).find(([x])=>x===k)?.[1]||0)]);for(const [k,v]of pairs(extra))if(!total.some(([x])=>x===k))total.push([k,Number(v)]);const txt=total.map(([k,v])=>k+'#'+v).join('|');cost(lk,txt);btn(lk,'Lv. Up',()=>{close();send({action:'treasure_upgrade',partner_id:hero.partner_id,lock:true});},!affordable(txt),'gs-btn');box.append(lk);}
  body.append(box);}

 // ---- Real attributes (HeroAttr) ----
 function attrs(hero){const key=JSON.stringify([hero.partner_id,hero.table_id,hero.lv,hero.grade,hero.awake,hero.equips]);const stats=$('detail-stats');if(!stats)return;
  const paint=a=>{if(!a||view!=='detail'||selectedGirlPartnerId!==hero.partner_id)return;$('detail-power-label').textContent="Power "+fmt(a.power);stats.replaceChildren();for(const [k,label,ic]of STAT_KEYS){const e=el('div','detail-stat');e.append(img('/assets/detail/'+ic+'.png'),el('span','',label+': '+fmt(a[k])));stats.append(e);}// HeroAttr gives every girl sklP = 1000 (neutral skill damage): only the part above it is an extra
  const base=k=>k==='sklP'?1000:['zs','fs','yx','ck','ms'].includes(k)?1:0;const extra=EXTRA.filter(k=>Number(a[k])>base(k));if(extra.length&&data){const x=el('div','eq-extra');for(const k of extra)x.append(el('span','',k==='sklP'?(data.attr_names[k]||'Skill DMG')+' +'+fmt(a[k]-1000)+'%':attrText(k,a[k]-base(k))));stats.append(x);}};
  if(attrCache[key]){paint(attrCache[key]);return;}attrKey=key;
  Promise.all([load(),api('/api/partner/'+hero.partner_id+'/attrs')]).then(([,a])=>{attrCache[key]=a;if(attrKey===key)paint(a);}).catch(()=>{});}

 // ---- Smithy ----
 function openSmithy(pos,from){smithyPos=pos||1;smithyItem=null;smithyCount=1;message='';smithyBack=from||view;load().then(()=>{showView('smithy');renderSmithy();});}
 function chain(){return Object.values(data.items).filter(r=>r.pos===smithyPos&&r.need_formula).sort((a,b)=>a.id-b.id);}
 function renderSmithy(){const root=$('smithy-view');if(!root||view!=='smithy'||!data)return;root.replaceChildren();
  if(artifactTarget)return artifactView(root);
  const top=el('header','eq-top');const back=el('button','eq-back');back.type='button';back.append(img('/assets/ui/win_back_btn.png'));back.onclick=()=>showView(smithyBack);top.append(back,el('h1','','Rèn'),money());root.append(top);
  const nav=el('nav','eq-nav');for(const [p,label]of SMITHY_TABS){const b=el('button',smithyPos===p?'on':'',label);b.type='button';b.onclick=()=>{smithyPos=p;smithyItem=null;smithyCount=1;message='';renderSmithy();};if(chain().length&&Object.values(data.items).some(r=>r.pos===p&&r.need_formula&&canForge(r)>0))b.append(img('/assets/equipment/alert_icon.png','eq-red'));nav.append(b);}root.append(nav);
  const list=chain();
  if(!list.length){root.append(el('p','eq-status','Không có công thức Rèn của nhà phát triển cho loại trang bị này.'));return;}
  if(!smithyItem||!list.some(r=>r.id===smithyItem))smithyItem=(list.find(r=>canForge(r)>0)||list[0]).id;const r=row(smithyItem);const [[src,per],gold]=[pairs(r.need_formula).find(([k])=>k!=='1'),Number(pairs(r.need_formula).find(([k])=>k==='1')?.[1]||0)];
  const head=el('div','sm-top');head.style.backgroundImage="url('/assets/equipment/bp_smithy_top.png')";const from=el('div','sm-from');from.append(icon(src));const pr=el('div','sm-bar');pr.style.backgroundImage="url('/assets/equipment/bp_bar_bg.png')";const fill=el('i');fill.style.width=Math.min(100,have(src)/per*100)+'%';fill.style.backgroundImage=`url('/assets/equipment/${have(src)>=per?'bp_bar_green':'bp_bar_blue'}.png')`;pr.append(fill,el('span','',fmt(have(src))+'/'+per));from.append(pr);
  head.append(from,img('/assets/equipment/mergeArrow.png','sm-arrow'),icon(r.id,'sm-result'));root.append(head);
  const info=el('div','sm-info');info.append(el('strong','',row(src).name+' ×'+per+' → '+r.name));lines(info,r.id);root.append(info);
  const max=canForge(r);smithyCount=Math.max(max?1:0,Math.min(smithyCount,max));const qty=el('div','sm-qty');btn(qty,'−',()=>{smithyCount=Math.max(1,smithyCount-1);renderSmithy();},smithyCount<=1,'sm-step');qty.append(el('b','',String(smithyCount)));btn(qty,'+',()=>{smithyCount=Math.min(max,smithyCount+1);renderSmithy();},smithyCount>=max,'sm-step');btn(qty,'Tối đa',()=>{smithyCount=max;renderSmithy();},max<=1,'sm-step');root.append(qty);
  const c=el('div','sm-cost');c.append(img('/assets/equipment/icon_1.png'),el('b',have(1)<gold*Math.max(1,smithyCount)?'short':'',fmt(gold*Math.max(1,smithyCount))));root.append(c);
  const acts=el('div','sm-actions');btn(acts,'Rèn',()=>send({action:'forge',item_id:r.id,count:smithyCount},x=>'Đã rèn: '+Object.entries(x.forged).map(([k,n])=>n+'× '+row(k).name).join(', ')),!max,'sm-btn white');btn(acts,'Tự động rèn',()=>send({action:'forge_auto',pos:smithyPos},x=>'Đã rèn: '+Object.entries(x.forged).map(([k,n])=>n+'× '+row(k).name).join(', ')),!list.some(x=>canForge(x)>0),'sm-btn blue');root.append(acts);
  const grid=el('div','sm-grid');for(const x of list){const b=el('button','sm-item'+(x.id===smithyItem?' on':''));b.type='button';b.append(icon(x.id));if(have(x.id))b.append(el('small','',fmt(have(x.id))));if(canForge(x)>0)b.append(img('/assets/equipment/alert_icon.png','eq-red'));b.title=x.name;b.onclick=()=>{smithyItem=x.id;smithyCount=1;message='';renderSmithy();};grid.append(b);}root.append(grid);
  root.append(el('p','eq-status',message));}
 function canForge(r){const need=pairs(r.need_formula);let n=Infinity;for(const [k,v]of need)n=Math.min(n,Math.floor(have(k)/Number(v)));return Number.isFinite(n)?n:0;}
 function money(){const m=el('div','eq-money');for(const id of ['1','2']){const s=el('span');s.append(img('/assets/currency/icon_'+id+'_small.png'),el('b','',fmt(state.items[id]||0)));m.append(s);}return m;}

 // ---- Antique upgrade (ArtifactUpWindow) ----
 function openArtifact(id,partnerId){artifactTarget={id,partnerId};feed={};message='';smithyBack=view;load().then(()=>{showView('smithy');renderSmithy();});}
 function artifactView(root){const {id,partnerId}=artifactTarget,r=row(id);const top=el('header','eq-top');const back=el('button','eq-back');back.type='button';back.append(img('/assets/ui/win_back_btn.png'));back.onclick=()=>{artifactTarget=null;showView(smithyBack);};top.append(back,el('h1','','Nâng cấp Cổ vật'),money());root.append(top);
  const head=el('div','sm-top art');head.append(icon(id),img('/assets/equipment/mergeArrow.png','sm-arrow'),icon(r.artifact_next,'sm-result'));root.append(head);
  const info=el('div','sm-info');info.append(el('strong','',r.name+' → '+row(r.artifact_next).name));lines(info,r.artifact_next);root.append(info);
  const exp=Object.entries(feed).reduce((s,[k,n])=>s+Number(row(k).artifact_exp)*n,0),need=Number(r.artifact_upg);const pr=el('div','sm-bar wide');pr.style.backgroundImage="url('/assets/equipment/bp_bar_bg.png')";const fill=el('i');fill.style.width=Math.min(100,exp/need*100)+'%';fill.style.backgroundImage=`url('/assets/equipment/${exp>=need?'bp_bar_green':'bp_bar_blue'}.png')`;pr.append(fill,el('span','',fmt(exp)+'/'+fmt(need)));root.append(pr);
  const acts=el('div','sm-actions');btn(acts,'Auto',()=>{feed={};let left=need;for(const m of mats(id,partnerId).sort((a,b)=>a.r.item_lv-b.r.item_lv||a.r.artifact_exp-b.r.artifact_exp)){while(left>0&&(feed[m.id]||0)<m.n){feed[m.id]=(feed[m.id]||0)+1;left-=Number(m.r.artifact_exp);}if(left<=0)break;}renderSmithy();},false,'sm-btn white');
  btn(acts,"Upgrade",()=>send({action:'artifact_upgrade',item_id:id,materials:feed,...(partnerId?{partner_id:partnerId}:{})},x=>{artifactTarget=row(x.upgraded)?.artifact_next?{id:x.upgraded,partnerId}:null;feed={};return "Upgraded to "+row(x.upgraded).name+(x.returned?" · returned: "+x.returned+'× '+row(6000).name:'');}),exp<need,'sm-btn blue');root.append(acts);
  btn(acts,"Clear",()=>{feed={};renderSmithy();},!Object.keys(feed).length,'sm-step');root.append(el('h4','',"Materials (tap to add; right-click or Clear to remove)"));const grid=el('div','sm-grid');for(const m of mats(id,partnerId)){const b=el('button','sm-item'+(feed[m.id]?' on':''));b.type='button';b.append(icon(m.id));b.append(el('small','',(feed[m.id]||0)+'/'+m.n));b.title=m.r.name+' · '+m.r.artifact_exp+' exp';b.onclick=()=>{if((feed[m.id]||0)<m.n){feed[m.id]=(feed[m.id]||0)+1;renderSmithy();}};b.oncontextmenu=e=>{e.preventDefault();if(feed[m.id]){feed[m.id]--;if(!feed[m.id])delete feed[m.id];renderSmithy();}};grid.append(b);}root.append(grid);
  if(!mats(id,partnerId).length)root.append(el('p','detail-note','Không có Cổ vật nào để dùng làm nguyên liệu.'));root.append(el('p','eq-status',message));}
 function mats(id,partnerId){return Object.entries(state.items).filter(([k,n])=>Number(n)>0&&row(k)?.pos===6&&row(k).artifact_exp).map(([k,n])=>({id:Number(k),n:Number(n)-(!partnerId&&Number(k)===id?1:0),r:row(k)})).filter(m=>m.n>0);}

 // ---- Bag hooks ----
 function bagDetail(itemId){const r=data&&row(itemId);const box=$('bag-detail');box.querySelector('.eq-bag-actions')?.remove();if(!r){if(!data)load().then(()=>bagDetail(itemId));return;}const wrap=el('div','eq-bag-actions');const info=el('div');lines(info,itemId);wrap.append(info);if(r.pos===6&&r.artifact_next)btn(wrap,'Nâng cấp',()=>openArtifact(itemId,null));if(r.pos<=4&&r.need_formula)btn(wrap,'Đến Xưởng Rèn',()=>openSmithy(r.pos,'bag'));box.append(wrap);}
 function render(){refresh();}
 document.addEventListener('DOMContentLoaded',()=>{const old=$('bag-forge');if(old){const b=old.cloneNode(true);old.replaceWith(b);b.addEventListener('click',()=>openSmithy(1,'bag'));}});
 return {gear,attrs,openSmithy,renderSmithy,bagDetail,load,icon:id=>data?.icons[String(id)]};
})();
