'use strict';
// Girl skins: the "Skins" tab of the girl detail (capture 2026-09-29-g/01 — carousel of skin cards with rarity,
// "Amount: N" and name, "Method:", wear / take off, show skin, chibi preview). Rules: gxb2/skins.py.
const Skins=(()=>{
 let cat=null,liveOffers=null,sel=null,note='',chibiView=null;
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const btn=(cls,text,fn)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
 const NAMES={hpP:'HP',atkP:'Attack',decDmg:'DMG Red.',crit:'Crit',critTime:'Crit DMG',hit:'Precision',miss:'Block',spd:'Speed',sklP:'Skill DMG',free:'CC Immune',unfree:'Control Rate',brk:'Armor Brk',unCrit:'Crit Resist',trueAtk:'Holy Dmg',allHarmDec:'DMG Dep.',hp:'HP',atk:'Attack'};
 // hpP/atkP are fractions (0.03 = 3%), spd/hp/atk flat, the rest per mille (crit#40 = 4%, sklP#100 = 10%)
 function attr(text){const [k,v]=String(text).split('#');const n=Number(v);return (NAMES[k]||k)+' +'+(n<1?Math.round(n*1000)/10+'%':['spd','hp','atk'].includes(k)?n:Math.round(n)/10+'%');}
 async function load(){if(!cat){try{cat=await api('/api/skins/catalog',{});}catch{cat={skins:{}};}}if(!liveOffers){try{liveOffers=(await api('/api/skin-shop/catalog',{})).offers||[];}catch{liveOffers=[];}}return cat;}
 async function act(req){note='';try{const r=await api('/api/skins/action',req);state=r.state;}catch(e){note=e.message;}if(typeof renderGirlDetail==='function')renderGirlDetail();}
 // PartnerCard:setSkinCard / setDefaultSkinCard (prefab partner_card, 160×240): card art partner_card_<model>, faction
 // img_group<n> top-left, worn check skin_icon01 top-right, "Amount:N", rarity ribbon collection_dress_new_bg_<qlt>
 // (COLLECTION_SKIN_TEXT13-16), skin name on the frame strip, frame partner_card03 (sliced 37/18/42/57).
 const RARITY=['','Common','Rare','Epic','Legendary'],U='/assets/skins/ui/';
 function baseName(hero){const st=Number(hero.stars||hero.star||0);return st>=15?'15-Star':st>=13?'13-Star':st>=10?'10-Star':st>=6?'Awaken':'Original';}
 function card(s,hero,{on,worn,own}){const c=btn('sk-card'+(on?' on':''),'',()=>{sel=s.id;previewSkinId=s.base?null:s.id;renderGirlDetail();});
  const art=el('div','sk-pic');const baseId=typeof artId==='function'?artId(hero.table_id):hero.table_id;const src=s.base?(cardIds.has(baseId)?'/assets/cards/partner_card_'+baseId+'.png':detailImage(baseId)||detailImage(hero.table_id)):'/assets/skins/cards/'+s.id+'.webp';
  art.style.backgroundImage=`url('${src}')`+(s.base?'':`,url('${detailImage(s.id)}')`);c.append(art,el('i','sk-frame'));
  const g=Number(hero.group||girlsCatalog.find(r=>r.id===hero.table_id)?.group||0);if(g){const f=el('img','sk-group');f.src=U+'img_group'+g+'.png';f.alt='';c.append(f);}
  if(worn){const w=el('img','sk-worn');w.src=U+'skin_icon01.png';w.alt='✓';c.append(w);}
  if(!s.base){c.append(el('span','sk-amount','Amount:'+own));const r=Number(s.rarity||0);if(r){const q=el('span','sk-rarity',RARITY[r]);q.style.backgroundImage=`url('${U}collection_dress_new_bg_${r}.png')`;c.append(q);}}
  c.append(el('b','sk-name',s.base?baseName(hero):s.name));return c;}
 async function detail(hero){const host=$('detail-skin-list');if(!host)return;await load();host.replaceChildren();
  const mine=Object.entries(cat.skins).filter(([,s])=>s.partners.includes(hero.table_id)).map(([id,s])=>({id:Number(id),...s}));
  const worn=Number(hero.equips?.[6]||0);if(sel&&!mine.some(s=>s.id===sel)&&sel!==hero.table_id)sel=null;const current=sel||worn||hero.table_id;
  const owned=id=>state.skins_info?.owned?.[String(id)]||0;
  const box=el('div','sk-box'),car=el('div','sk-carousel');
  for(const s of [{id:hero.table_id,base:true},...mine])car.append(card(s,hero,{on:current===s.id,worn:s.base?!worn:worn===s.id,own:owned(s.id)}));
  box.append(car);host.append(box);
  // centre the selected card by scrolling only the carousel: scrollIntoView also scrolled the girl's scene sideways
  requestAnimationFrame(()=>{const on=car.querySelector('.sk-card.on');if(on)car.scrollLeft=Math.max(0,on.offsetLeft-(car.clientWidth-on.offsetWidth)/2);});
  const s=mine.find(x=>x.id===current),bar=el('div','sk-bar'),mid=el('div','sk-mid'),side=el('div','sk-side');
  if(s){const have=owned(s.id);
   if(worn===s.id)mid.append(btn('sk-btn red','Take off',()=>act({action:'unequip',partner_id:hero.partner_id})));
   else if(have)mid.append(btn('sk-btn blue','Put on',()=>act({action:'equip',partner_id:hero.partner_id,skin:s.id})));
   else if(!s.is_wedding&&liveOffers?.some(r=>r.skin_id===s.id))mid.append(btn('sk-btn blue','Cửa Hàng Trang Phục',()=>openMenu('skin-shop','detail')));
   else mid.append(el('span','sk-method','Method: Exclusives'));
   const info=el('p','sk-attrs',s.attrs.map(attr).join(' · '));mid.prepend(info);}
  else if(worn)mid.append(btn('sk-btn blue','Put on',()=>act({action:'unequip',partner_id:hero.partner_id})));
  if(worn){const eye=btn('sk-round','',()=>act({action:'show',partner_id:hero.partner_id}));eye.title=hero.show_skin===0?"Skin hidden in battle":"Skin visible in battle";eye.style.backgroundImage=`url('${U}${hero.show_skin===0?'skin_btn01':'skin_btn02'}.png')`;side.append(eye);}
  const chibiId=s?s.id:hero.table_id;const ch=btn('sk-round','',()=>preview(chibiId));ch.title="View chibi";ch.style.backgroundImage=`url('${U}skin_show_btn.png')`;side.append(ch);
  bar.append(el('div','sk-spacer'),mid,side);host.append(bar);
  const col=state.skins_info;if(col){const t=el('p','sk-col',`Skin Collection ${col.collected.length}/${col.total} · ${number(col.points)} pts`+(col.tier?` · ${col.tier.effect.replace('hp#','HP +').replace('|atk#',' · ATK +')}`:''));host.append(t);}
  if(note)host.append(el('p','sk-err',note));}
 async function preview(id){const catc=await api('/assets/chibis/catalog.json');const meta=catc[String(id)];if(!meta)return;const ov=el('div','sk-overlay');ov.onclick=()=>{chibiView?.destroy();chibiView=null;ov.remove();};const box=el('div','sk-chibi');ov.append(box);document.body.append(ov);
  try{chibiView=await GxbSpine.mount(box,'/assets/chibis/'+meta.model,{width:420,height:420,fit:.8,y:.6,sequence:[['idle',true]]});}catch{ov.remove();}}
 // Live server-backed Skin Store. Wedding costumes are excluded on both sides.
 let storeGroup=0;
 async function store(){
  await load();
  liveOffers=(await api('/api/skin-shop/catalog',{})).offers||[];
  const {body,close}=GirlUI.win({title:'Cửa Hàng Trang Phục',cls:'sk-store-win',
    help:'Vàng và Crystal là tiền trong game. Giá do quản trị viên đặt trên máy chủ. Skin cưới là phần thưởng độc quyền kết duyên và không được bán.'});
  const tk=el('div','sk-store-top');
  for(const [id,name] of [['1','Vàng'],['2','Crystal'],['74','Vé Trang Phục']]){
    const chip=el('span','sk-store-tickets'),it=itemCatalog?.[id],src=it&&typeof itemPicture==='function'?itemPicture(it):'';
    if(src){const icon=el('img');icon.src=src;icon.alt='';chip.append(icon);}
    chip.append(el('b','',name+': '+number(state.items?.[id]||0)));tk.append(chip);
  }
  const f=el('div','sk-store-filter');
  [0,1,2,3,4,5,6,7].forEach(g=>{
   const b=btn('sk-store-f'+(storeGroup===g?' on':''),g?'':'Tất cả',()=>{storeGroup=g;close();store();});
   if(g){const i=el('img');i.src='/assets/factions/'+g+'.png';i.alt='';b.append(i);}f.append(b);
  });tk.append(f);body.append(tk);
  const grid=el('div','sk-store-grid');
  const owned=id=>Number(state.items?.[String(id)]||0)+(state.roster||[]).filter(h=>Number(h.equips?.[6]||0)===id).length;
  const rows=liveOffers.filter(o=>!o.is_wedding&&o.enabled)
   .filter(o=>!storeGroup||o.group===storeGroup).sort((a,b)=>b.skin_id-a.skin_id);
  for(const r of rows){
   const c=el('div','sk-store-card'),pic=el('div','sk-store-pic');
   pic.style.backgroundImage="url('/assets/skins/cards/"+r.skin_id+".webp')";
   const rarity=Number(r.rarity||0);
   if(rarity){const q=el('span','sk-rarity',RARITY[rarity]);q.style.backgroundImage="url('"+U+"collection_dress_new_bg_"+rarity+".png')";pic.append(q);}
   const n=owned(r.skin_id);if(n)pic.append(el('span','sk-store-own','×'+n));
   c.append(pic,el('b','sk-store-name',r.name),el('small','sk-store-girl',r.girl_name||''));
   let methods=0;
   for(const [kind,allowed,amount,key,label] of [['gold','allow_gold','price_gold','1','Vàng'],
     ['crystal','allow_crystal','price_crystal','2','Crystal'],['ticket','allow_ticket','price_ticket','74','Vé Trang Phục']]){
    if(!r[allowed]||!(Number(r[amount])>0))continue;
    methods++;
    const cost=Number(r[amount]);
    const buy=btn('sk-store-buy','',async()=>{
      if(!(await GirlUI.confirm('Mua '+r.name+' với '+number(cost)+' '+label+'?',{title:'Xác Nhận Mua',ok:'Mua'})))return;
      try{
        buy.disabled=true;
        const res=await api('/api/skins/action',{action:'buy',skin:r.skin_id,payment:kind});
        state=res.state;close();await store();CampaignUI.popup('Cửa Hàng Trang Phục',res.got);
      }catch(e){GirlUI.toast(e.message);buy.disabled=false;}
    });
    const it=itemCatalog?.[key],src=it&&typeof itemPicture==='function'?itemPicture(it):'';
    if(src){const image=el('img');image.src=src;image.alt='';buy.append(image);}
    buy.append(el('span','',number(cost)));
    buy.title='Mua bằng '+label;buy.disabled=Number(state.items?.[key]||0)<cost;
    c.append(buy);
   }
   if(methods)grid.append(c);
  }
  if(!grid.children.length)grid.append(el('p','sk-store-empty','Chưa có trang phục được mở bán ở phe này.'));
  body.append(grid);
 }
 return {detail,store};
})();
