'use strict';
// Outfits (DressMainWindow: Locker Room / Closet, DressItemUpWindow, DressSummonWindow, SenpaiModel). Rules:
// gxb2/dress.py. Layout from docs/references/2026-09-29-i (01-03) and 2026-09-29-j (01 Closet Gallery, 02 Outfit
// Upgrade, 03 Locker Room). The chibi is SenpaiModel: head / body / legs Spines playing the same animation (head in
// front, legs behind) + headwear / accessory images on slots of the head / body skeleton.
const SenpaiDoll=(()=>{
 // Unity splits each skeleton at its "*_layer" slots (SkeletonRenderSeparator) and interleaves the parts; this is the
 // back-to-front order of those parts (head / body / legs share the same bones and animation).
 const ORDER=[['head',''],['head','hair_layer02'],['body',''],['body','Lhand_layer'],['foot',''],['foot','foot_layer'],['body','body_layer02'],['body','body_layer'],
  ['body','body_layer01'],['head','face_layer'],['head','hair_layer01'],['body','Rhand_layer']];
 async function mount(host,styles,cat,{width=360,height=420,anim='idle',fit=.92}={}){
  const parts=[['head',cat.styles[String(styles[0])]],['body',cat.styles[String(styles[1])]],['foot',cat.styles[String(styles[2])]]].filter(([,s])=>s);if(!parts.length)return null;
  const datas=await Promise.all(parts.map(([,s])=>GxbSpine.load('/assets/dress/spine/'+s.res)));
  const app=new PIXI.Application({width,height,transparent:true,antialias:true,resolution:Math.min(2,devicePixelRatio||1),autoDensity:false});app.view.className='dr-doll-canvas';host.append(app.view);
  const root=new PIXI.Container();const layers=new Map(ORDER.map(k=>{const c=new PIXI.Container();root.addChild(c);return [k.join(':'),c];}));const figs={};
  parts.forEach(([kind],i)=>{const d=datas[i];const f=new PIXI.spine.Spine(d);if(d.findAnimation(anim))f.state.setAnimation(0,anim,true);f.update(0);f.visible=true;root.addChild(f);figs[kind]=f;});
  // move every slot container into its layer (draw order within a layer is kept)
  const segOf={};for(const [kind,fig] of Object.entries(figs)){let seg='';for(const slot of fig.skeleton.drawOrder){const name=slot.data.name;if(/_layer\d*$/.test(name))seg=name;segOf[kind+':'+name]=seg;const target=layers.get(kind+':'+seg)||layers.get(kind+':');const c=fig.slotContainers[slot.data.index];if(c&&target)target.addChild(c);}}
  // headwear on the head skeleton, accessory on the body skeleton (SenpaiModel:initSlot: slot image + offset / scale /
  // rotation). The slot usually has no attachment (pixi-spine hides it), so a holder follows the slot's bone each frame.
  const holders=[];
  for(const [pos,kind] of [[4,'head'],[5,'body']]){const st=cat.styles[String(styles[pos-1])];const fig=figs[kind];if(!st||!st.slot||!fig)continue;const slot=fig.skeleton.findSlot(st.slot);if(!slot)continue;
   const holder=new PIXI.Container();const sp=PIXI.Sprite.from('/assets/dress/slot/'+st.res+'.png');sp.anchor.set(.5);sp.position.set(st.offset[0]||0,st.offset[1]||0);sp.scale.set(st.scale[0]||1,-(st.scale[1]||1));sp.rotation=-(st.rotation||0)*Math.PI/180;/* Spine data is y-up, pixi-spine bones are y-down: flip the image and the angle *//* same convention as pixi-spine region attachments (yDown) */holder.addChild(sp);
   const layer=layers.get(kind+':'+(segOf[kind+':'+st.slot]||''))||root;const idx=fig.slotContainers[slot.data.index];layer.addChildAt(holder,Math.min(layer.children.length,idx&&idx.parent===layer?layer.getChildIndex(idx)+1:layer.children.length));holders.push([holder,slot]);}
  const follow=()=>{for(const [h,slot] of holders){const m=slot.bone.matrix||new PIXI.Matrix(slot.bone.a,slot.bone.c,slot.bone.b,slot.bone.d,slot.bone.worldX,slot.bone.worldY);h.transform.setFromMatrix(m);}};
  app.ticker.add(follow);follow();
  const frame=()=>{root.scale.set(1);root.position.set(0,0);follow();const b=root.getLocalBounds();const s=Math.min(width*fit/Math.max(1,b.width),height*fit/Math.max(1,b.height));root.scale.set(s);root.x=width/2-(b.x+b.width/2)*s;root.y=height*.97-(b.y+b.height)*s;};
  frame();app.stage.addChild(root);for(const [h] of holders){const t=h.children[0].texture;if(!t.baseTexture.valid)t.baseTexture.once('loaded',frame);}
  const handle={app,dead:false,idle:0,figures:figs,destroy(){if(handle.dead)return;handle.dead=true;GxbSpine.live.delete(handle);try{app.destroy(true,{children:true,texture:false,baseTexture:false});}catch{}}};GxbSpine.live.add(handle);return handle;}
return {mount};
})();

const Dress=(()=>{
 let origin='campus',tab='locker',cat=null,note='',busyLocal=false,edit=null,filter=0,modal=null,sel=null,doll=null,gallery=false,results=null,shopKind=1;
 const A=n=>'/assets/dress/ui/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;i.onerror=()=>i.style.visibility='hidden';return i;};
 const btn=(cls,text,fn)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
 function root(){let r=$('dress-view');if(!r){r=el('section','dress-view');r.id='dress-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function open(from,t){origin=from||view;tab=t||'locker';edit=null;modal=null;note='';showView('dress');if(!cat){try{cat=await api('/api/dress/catalog',{});}catch(e){note=e.message;}}render();}
 async function act(req){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/dress/action',req);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;if(view==='dress')render();}}
 const info=()=>state.dress_info;
 const ATTR=[['Courage','#e0556e'],['Charisma','#3aa35b'],['Knowledge','#3b7fd1']];
 function owned(){return new Map((info()?.owned||[]).map(p=>[p.dress,p]));}
 function pieceName(did){return cat.pieces[String(did)]?.name||'';}
 function styleOf(did){const p=cat.pieces[String(did)];const chosen=info().style?.[String(did)];return chosen||p.styles[0];}
 function itemFor(did,star){const p=cat.pieces[String(did)];return cat.items[String(p.items[Math.max(1,Math.min(star,p.items.length))-1])];}
 function card(did,{star=0,cls='',style=null,onClick=null,check=false}={}){const p=cat.pieces[String(did)];const it=itemFor(did,star||1);const st=style||styleOf(did);
  const c=btn('dr-card q'+it.qlt+' '+cls,'',onClick);c.style.backgroundImage=`url('${A('lead_skin_border_'+Math.min(7,it.qlt))}')`;c.append(img(A(cat.styles[String(st)]?.image||it.icon[0]),'dr-cimg'));
  if(p.styles.length>1){const b=el('span','dr-badge');b.append(el('i','','👤'),el('b','',`${p.styles.length}/${p.styles.length}`));c.append(b);}
  if(star){const s=el('span','dr-stars');for(let i=0;i<p.items.length;i++)s.append(el('i',i<star?'on':'','★'));c.append(s);}
  if(check)c.append(el('span','dr-check','✓'));c.title=pieceName(did);return c;}
 function render(){const r=root();if(view!=='dress'){doll?.destroy();doll=null;return;}r.replaceChildren();const st=el('div','dr-stage');r.append(st);
  const top=el('div','dr-top');const back=btn('dr-back','',()=>{if(edit){edit=null;render();return;}showView(origin==='dress'?'campus':origin);});back.append(img('/assets/ui/win_back_btn.png'));top.append(back);st.append(top);
  const tabs=el('div','dr-tabs');for(const [k,label] of [['locker','Locker Room'],['closet','Closet'],['shop','Outfit Store']])tabs.append(btn('dr-tab'+(tab===k?' on':''),label,()=>{tab=k;edit=null;gallery=false;render();}));st.append(tabs);
  if(!cat||!info()){st.append(el('p','dr-note',note||"Loading…"));return;}
  if(tab==='locker')locker(st);else if(tab==='closet')closet(st);else shop(st);
  if(modal)modal(st);if(note)st.append(el('p','dr-err',note));}
 // Locker Room (capture 2026-09-29-j/03): chibi, the 5 slots, Set, Attribute bonus triangle, Special Bonus.
 function locker(st){const I=info();const styles=edit||I.equipped;const room=el('div','dr-room');room.style.backgroundImage=`url('/assets/dress/ui/dress_main_bg.webp')`;
  const left=el('div','dr-slots left'),right=el('div','dr-slots right');
  for(const pos of [1,2,3,4,5]){const sid=styles[pos-1];const s=cat.styles[String(sid)];const slot=btn('dr-slot','',()=>{if(!edit)edit=[...I.equipped];filter=pos;render();});
   if(s){const did=s.dress;const star=owned().get(did)?.star||1;const it=itemFor(did,star);slot.style.backgroundImage=`url('${A('lead_skin_border_'+Math.min(7,it.qlt))}')`;slot.append(img(A(s.image),'dr-cimg'));if(cat.pieces[String(did)].styles.length>1){const b=el('span','dr-badge');b.append(el('b','',`${cat.pieces[String(did)].styles.length}/${cat.pieces[String(did)].styles.length}`));slot.append(b);}}
   else slot.append(el('span','dr-empty',cat.slots[String(pos)].name));
   const box=el('div','dr-slotbox');box.append(slot,el('small','dr-slotname',s?pieceName(s.dress):cat.slots[String(pos)].name));(pos<=3?left:right).append(box);}
  const set=btn('dr-set','',()=>{modal=setModal;render();});set.append(img('/assets/dress/ui/icon_258.png','dr-seticon'),el('b','','Set'));right.append(set);
  const stage=el('div','dr-dollbox');room.append(left,stage,right);st.append(room);
  doll?.destroy();doll=null;SenpaiDoll.mount(stage,styles,cat).then(h=>{if(!stage.isConnected){h?.destroy();return;}doll=h;}).catch(()=>{});
  if(edit){const acts=el('div','dr-editacts');acts.append(btn('dr-btn','Cancel',()=>{edit=null;render();}),btn('dr-btn blue','Save',async()=>{const r=await act({action:'save',styles:edit});if(r)edit=null;render();}));room.append(acts);
   const f=el('div','dr-filters');[['ALL',0],['Head',1],['Body',2],['Legs',3],['Headwear',4],['Accessories',5]].forEach(([n,p])=>f.append(btn('dr-filter'+(filter===p?' on':''),n,()=>{filter=p;render();})));st.append(f);
   const grid=el('div','dr-grid');const own=owned();for(const [did,p] of own){const pc=cat.pieces[String(did)];if(filter&&pc.pos!==filter)continue;const cur=edit[pc.pos-1];const worn=pc.styles.includes(cur);
    grid.append(el('div','dr-cell',undefined));const cell=grid.lastChild;cell.append(card(did,{star:p.star,check:worn,style:worn?cur:null,onClick:()=>{if(worn&&pc.styles.length>1){const i=pc.styles.indexOf(cur);edit[pc.pos-1]=pc.styles[(i+1)%pc.styles.length];}else if(worn&&cat.slots[String(pc.pos)].can_rm){edit[pc.pos-1]=0;}else edit[pc.pos-1]=styleOf(did);render();}}),el('small','dr-cname',pieceName(did)));}
   if(!grid.children.length)grid.append(el('p','dr-note',"You have no pieces of this type. Obtain them in the Outfit Store."));st.append(grid);return;}
  const panel=el('div','dr-panel');const at=el('div','dr-attr');at.append(el('b','dr-ph','Attribute bonus'));at.append(triangle(I.attrs));at.append(btn('dr-btn blue','Attribute Boost',()=>{tab='closet';gallery=false;render();}));
  const sk=el('div','dr-skills');sk.append(el('b','dr-ph','Special Bonus'));if(!I.skills.length){sk.append(el('p','dr-note','No Special Boost yet'));}
  for(const id of I.skills){const t=(cat.skill_text[String(id)]||'').replace(/%%/g,'%');const row=el('div','dr-skill');row.append(el('span','',t),btn('dr-info','!',()=>{note=t;render();}));sk.append(row);}
  panel.append(at,sk);st.append(panel);}
 function triangle(v){const w=el('div','dr-tri');const [c,ch,k]=v;const max=Math.max(1,...v);const pt=(i,val)=>{const a=[-90,150,30][i]*Math.PI/180,r=60*val/max;return [80+r*Math.cos(a),78+r*Math.sin(a)];};
  const svg=`<svg viewBox="0 0 160 150"><polygon points="80,18 28,108 132,108" fill="rgba(120,170,230,.18)" stroke="#8fb3e0" stroke-width="2"/><polygon points="${[0,1,2].map(i=>pt(i,v[i]).join(',')).join(' ')}" fill="rgba(90,150,225,.65)"/></svg>`;w.innerHTML=svg;
  const lab=(i,cls)=>{const d=el('div','dr-tv '+cls);d.append(el('b','',number(v[i])),el('small','',ATTR[i][0]));d.querySelector('b').style.color=ATTR[i][1];return d;};w.append(lab(0,'top'),lab(1,'left'),lab(2,'right'));return w;}
 function setModal(st){const w=overlay(st,'Set');const own=owned();w.append(el('p','dr-hint',"Equip all owned pieces of a set at once."));const list=el('div','dr-sets');
  for(const [gid,g] of Object.entries(cat.groups)){const have=g.unit.filter(d=>own.has(d));if(!have.length)continue;const row=btn('dr-setrow','',async()=>{const next=[...info().equipped];for(const d of have){const p=cat.pieces[String(d)];next[p.pos-1]=styleOf(d);}modal=null;await act({action:'save',styles:next});});
   row.append(el('b','',g.name||`Set ${gid}`),el('small','',`${have.length}/${g.unit.length}`));list.append(row);}w.append(list);}
 function overlay(st,title,cls=''){const ov=el('div','dr-overlay');ov.onclick=e=>{if(e.target===ov){modal=null;render();}};const w=el('div','dr-win '+cls);const h=el('div','dr-winhead');h.append(el('b','',title),btn('dr-close','✕',()=>{modal=null;render();}));w.append(h);ov.append(w);st.append(ov);return w;}
 // Closet (capture 2026-09-29-j/01): owned pieces with their stars; Gallery = every piece (faded if missing).
 function closet(st){const own=owned();const f=el('div','dr-filters');[['ALL',0],['Head',1],['Body',2],['Legs',3],['Headwear',4],['Accessories',5]].forEach(([n,p])=>f.append(btn('dr-filter'+(filter===p?' on':''),n,()=>{filter=p;render();})));
  f.append(btn('dr-btn blue dr-gal'+(gallery?' on':''),gallery?'Closet':'Gallery',()=>{gallery=!gallery;render();}));st.append(f);
  const grid=el('div','dr-grid');const list=gallery?Object.keys(cat.pieces).map(Number):[...own.keys()];
  for(const did of list){const pc=cat.pieces[String(did)];if(filter&&pc.pos!==filter)continue;const p=own.get(did);const cell=el('div','dr-cell'+(p?'':' missing'));
   cell.append(card(did,{star:p?.star||0,onClick:()=>{if(!p){note=pieceName(did)+": obtain it in the Outfit Store.";render();return;}sel=did;modal=upgradeModal;render();}}),el('small','dr-cname',pieceName(did)));
   if(p?.cost&&canPay(p.cost))cell.classList.add('can-up');grid.append(cell);}
  st.append(grid);}
 function have(k){const I=info();if(k.startsWith('qlt'))return I.common[k.slice(3)]||0;if(k==='260'||k==='261')return I.silk[k];return state.items?.[k]||0;}
 function canPay(cost){return Object.entries(cost).every(([k,n])=>have(k)>=n);}
 // Outfit Upgrade (capture 2026-09-29-j/02): silk counters, attributes before → after, fragments n/need, silk cost.
 function upgradeModal(st){const did=sel;const p=owned().get(did);const pc=cat.pieces[String(did)];const w=overlay(st,'Outfit Upgrade','dr-upwin');
  const silk=el('div','dr-silk');for(const k of ['260','261']){const c=el('span','dr-chip');c.append(img(A('icon_'+k)),el('b','',number(info().silk[k])));silk.append(c);}w.append(silk);
  const cmp=el('div','dr-cmp');const box=(star)=>{const it=itemFor(did,star);const b=el('div','dr-cmpbox');b.append(card(did,{star}));for(let i=0;i<3;i++)b.append(el('p','',`+${it.base[i]} ${ATTR[i][0]}`));return b;};
  cmp.append(box(p.star));if(p.cost){cmp.append(el('span','dr-arrow','➜'),box(p.star+1));}w.append(cmp);
  if(!p.cost){w.append(el('p','dr-hint','Reached Max Level!'));return;}
  const mats=el('div','dr-mats');const silkCost=el('div','dr-silkcost');
  for(const [k,n] of Object.entries(p.cost)){if(k==='260'||k==='261'){const c=el('span','dr-chip');c.append(img(A('icon_'+k)),el('b','',number(n)));silkCost.append(c);continue;}
   const m=el('div','dr-mat');const q=k.startsWith('qlt')?k.slice(3):null;const icon=q?A('icon_'+cat.common[Number(q)-1]):A(cat.styles[String(styleOf(did))].image);
   const t=el('span','dr-matimg'+(q?' q'+q:''));t.append(img(icon));if(q)t.append(el('i','dr-q','?'));m.append(t);const ok=have(k)>=n;m.append(el('b',ok?'ok':'no',`${number(have(k))}/${number(n)}`));m.title=q?`Common Shards of quality ${q}`:(cat.shard_names[k]||"Shards");mats.append(m);}
  w.append(mats,silkCost);const up=btn('dr-btn blue big','Lv. Up',async()=>{const r=await act({action:'upgrade',dress:did});if(r)note=`${pieceName(did)} ★${r.star}`;render();});up.disabled=!canPay(p.cost);w.append(up);}
 // Outfit Store / Outfit Sale (DressSummonWindow): 1× / 10× with Plain / Fancy Buttons, free draw, orange counter.
 function shop(st){const I=info();const box=el('div','dr-shop');box.style.backgroundImage=`url('/assets/dress/ui/${shopKind===1?'dress_summon_normal_bg':'dress_summon_limit_bg'}.webp')`;
  const tabs=el('div','dr-shoptabs');tabs.append(btn('dr-filter'+(shopKind===1?' on':''),'Outfit Store',()=>{shopKind=1;render();}),btn('dr-filter'+(shopKind===2?' on':''),'Outfit Sale',()=>{shopKind=2;render();}));box.append(tabs);
  box.append(img(A(shopKind===1?'dress_summon_logo_en_en':'dress_summon_limit_logo_en_en'),'dr-logo'));
  const k=String(shopKind),cost=shopKind===1?'258':'259';const left=Math.max(0,I.max_drop-(I.pity[k]||0));
  box.append(el('p','dr-pity',`Orange Outfit guaranteed in ${left} draw(s)`));
  const bar=el('div','dr-draws');const one=btn('dr-drawbtn','',()=>draw(shopKind,1));one.append(el('b','','Draw 1'));const free=(I.free[k]||0)===0;if(free)one.append(el('small','dr-free','FREE'));else{const c=el('span','dr-chip');c.append(img(A('icon_'+cost)),el('b','','1'));one.append(c);}
  const ten=btn('dr-drawbtn','',()=>draw(shopKind,10));ten.append(el('b','','Draw 10'));const c10=el('span','dr-chip');c10.append(img(A('icon_'+cost)),el('b','','10'));ten.append(c10);bar.append(one,ten);box.append(bar);
  const own=el('div','dr-own');const c=el('span','dr-chip');c.append(img(A('icon_'+cost)),el('b','',number(I.buttons[cost]||0)));own.append(c);if(!free)own.append(el('small','',`Free draw in ${Math.ceil((I.free[k]||0)/3600)}h`));box.append(own);
  box.append(el('p','dr-hint dr-light',"Duplicate pieces become Shards. Orange probability is 1.5%, increases after 50 draws, and is guaranteed at 100."));st.append(box);
  if(results){const w=overlay(st,'Rewards');modal=null;const grid=el('div','dr-grid dr-results');for(const x of results){const cell=el('div','dr-cell'+(x.orange?' orange':''));cell.append(card(x.dress,{star:1}),el('small','dr-cname',x.new?'NEW · '+pieceName(x.dress):`+${Object.values(x.shards||{})[0]||0} Shards`));grid.append(cell);}w.append(grid);
   w.querySelector('.dr-close').onclick=()=>{results=null;render();};}}
 async function draw(kind,count){const r=await act({action:'summon',kind,count});if(r?.results){results=r.results;render();}}
 return {open,render};
})();
