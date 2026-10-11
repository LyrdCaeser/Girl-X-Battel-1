'use strict';
// Wish Capsule (activity 140; capture 2026-09-29-fb/47). Two faces: the Wish page added to the Capsule view (the chosen
// Wish Girl on the arcade pedestal, progress to the guaranteed draw with the current rate, Switch, Free / ×1 / ×10 with
// Advanced Capsules or gems → summons 22-26) and the event panel (activity/WishCapsule: banner, "Capsule" button and the
// draw-count rewards). Rules: gxb2/wish.py. Prefix wc-.
const WishCapsule=(()=>{
 let data=null;
 const A=n=>'/assets/wish/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 const T=(k,...a)=>{let s=data?.text?.[k]||'';a.forEach((v,i)=>{s=s.replace('{'+(i+1)+'}',v);});return s;};
 const girl=id=>girlsCatalog.find(g=>g.id===Number(id));
 function picture(id,cls){const i=img('/assets/pictures/'+id+'.webp',cls);i.onerror=()=>{i.onerror=null;i.src='/assets/cards/partner_card_'+id+'.png';i.classList.add('card');};return i;}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}return it&&itemIcons.has(it.icon)?'/assets/item-icons/'+it.icon+'.png':'';}
 function chips(text){const w=el('span','wc-chips');for(const p of String(text||'').split('|')){if(!p.includes('#'))continue;const [k,v]=p.split('#');const c=el('span','wc-chip');const s=icon(k);if(s)c.append(img(s));c.append(el('b','',number(Number(v))));c.title=itemCatalog?.[k]?.name||k;w.append(c);}return w;}
 async function load(){if(!data)data=await api('/assets/wish.json');return data;}
 async function act(req,msg){try{const r=await api('/api/wish/action',req);state=r.state;if(msg)GirlUI.toast(msg);return r;}catch(e){GirlUI.toast(e.message);return null;}finally{if(typeof render==='function')render();}}
 const hms=s=>{const h=Math.floor(s/3600),m=Math.floor(s%3600/60);return h+'h '+String(m).padStart(2,'0')+'m';};
 // --- Capsule page: Advanced ⇄ Wish share the middle slot (SummonWindow groupMiddle, btnLeft_ / btnRight_, dotGroup) ----
 let page=0;
 function arrow(dir){const b=btn('wc-arrow '+dir,'',()=>{page=dir==='right'?1:0;capsule();});b.append(img(A('wish_capsule_arrow_'+dir)));b.setAttribute('aria-label',dir==='right'?'Wish Capsule':'Advanced Capsules');return b;}
 function dots(){const d=el('div','wc-dots');for(let i=0;i<2;i++)d.append(img(A('wish_capsule_dot'+(i===page?1:0))));return d;}
 async function capsule(){await load();const s=state.wish_info;if(!s)return;const adv=document.querySelector('#capsule-view .capsule-banner.advanced');if(!adv)return;
  adv.querySelectorAll(':scope>.wc-arrow,:scope>.wc-dots').forEach(e=>e.remove());adv.append(arrow('right'),dots());adv.hidden=page!==0;
  let box=$('wish-banner');if(!box){box=el('div','capsule-banner wc-banner');box.id='wish-banner';adv.after(box);}box.replaceChildren();box.hidden=page!==1;
  const art=el('div','capsule-banner-art wc-art');
  if(s.select)art.append(picture(s.select,'wc-girl'));else art.append(btn('wc-empty',T('WISH_GACHA_TIPS_2')||'Tap to choose the girl you wish to get',()=>select()));
  const g=girl(s.select);if(g)art.append(el('b','wc-name',g.name));art.append(btn('wc-help','?',()=>tips()));
  const ctl=el('div','capsule-banner-controls wc-controls');ctl.append(img(A('wish_capsule_summon_text01_en_en'),'wc-logo'));
  const prog=el('div','wc-progress');const rate=el('span','wc-rate');rate.append(img(A('wish_capsule_icon2')),el('b','',(s.rate*100).toFixed(s.rate<0.001?3:2)+'%'));
  const bar=el('div','wc-bar');const fill=el('i');fill.style.width=Math.min(100,s.times/data.odds.guarantee*100)+'%';bar.append(fill,el('span','',s.times+'/'+data.odds.guarantee));
  prog.append(rate,bar,btn('wc-switch',T('WISH_GACHA_TEXT9')||'Switch',()=>select()));ctl.append(prog);
  const cnt=el('div','capsule-count');cnt.append(img('/assets/currency/icon_36.png','capsule-token'),el('b','',number(state.items?.['36']||0)));ctl.append(cnt);
  ctl.append(el('p','capsule-free',s.free_in<=0?"Free summon available":"Free in "+hms(s.free_in)));
  const buttons=el('div','capsule-buttons');const scroll=Number(state.items?.['36']||0),gems=Number(state.items?.['2']||0);
  const draw=(sid,label,cost,dis,cls='')=>{const b=btn('capsule-draw'+cls,label,()=>{if(!s.select){select();return;}action('SUMMON',{summon_id:sid,times:1});},dis);const st=el('strong');st.append(cost);b.append(st);return b;};
  const tk=n=>{const f=document.createDocumentFragment();f.append(n+' ');f.append(img('/assets/currency/icon_36.png','cost-token'));return f;};
  const gm=n=>{const f=document.createDocumentFragment();f.append(n+' ');f.append(img('/assets/currency/icon_2_small.png','cost-token'));return f;};
  buttons.append(draw(26,"Free",'1',s.free_in>0),draw(24,"Summon 1",tk(1),scroll<1),draw(25,"Summon 10",tk(10),scroll<10),draw(22,"With Gems ×1",gm(250),gems<250,' gem-draw'),draw(23,"With Gems ×10",gm(2200),gems<2200,' gem-draw'));
  ctl.append(buttons);box.append(art,ctl,arrow('left'),dots());}
 function select(){const s=state.wish_info;const {body,close}=GirlUI.win({title:T('WISH_GACHA_SELECT_PARTNER_WINDOW')||'Choose your Wish Girl',cls:'wc-select'});
  body.append(el('p','wc-note',T('WISH_GACHA_TIPS_3')));const grid=el('div','wc-grid');
  for(const id of data.partners){const g=girl(id);const c=btn('wc-card'+(id===s.select?' on':''),'',async()=>{if(id===s.select){close();return;}if(s.select&&!confirm(T('WISH_GACHA_TEXT12')||'Confirm to switch your Wish Girl?'))return;close();await act({action:'select',partner:id});capsule();});
   c.append(img('/assets/cards/partner_card_'+id+'.png'),el('small','',g?.name||String(id)));if(g?.group)c.append(img('/assets/factions/group'+g.group+'.png','wc-faction'));grid.append(c);}
  body.append(grid);}
 function tips(){const s=state.wish_info;const {body}=GirlUI.win({title:T('WISH_GACHA_TEXT6')||'Current Progress',cls:'wc-tips'});
  const rows=el('div','wc-tiers');for(let i=1;i<=5;i++){const r=el('div','wc-tier'+(s.times>=Number(T('WISH_GACHA_NUM'+i))?' on':''));r.append(el('b','',T('WISH_GACHA_NUM'+i)+' '+(T('WISH_GACHA_NUM')||'Draws')),el('span','',i<5?T('WISH_GACHA_NUM'+(i+5)):(T('WISH_GACHA_TEXT5')||'Guaranteed').replace('\n',' ')));rows.append(r);}
  body.append(rows,el('p','wc-note',T('WISH_GACHA_TIPS_3')),el('p','wc-note',T('WISH_GACHA_TEXT10')));}
 // --- Event panel (activity 140) -------------------------------------------------------------------------------------
 async function panel(parent){await load();const s=state.wish_info;parent.replaceChildren();const w=el('div','wc-event');
  const top=el('div','wc-top');top.style.backgroundImage=`url('${A('wish_capsule_bg')}')`;top.append(img(A('wish_capsule_text01_en_en'),'wc-title'));const tx=el('div','wc-text');tx.append(el('p','',T('WISH_GACHA_TIPS_1')));top.append(tx);
  top.append(btn('wc-go gs-btn white',T('WISH_GACHA_GOTOGACHA')||'Capsule',()=>showView('capsule')));w.append(top);
  const list=el('div','wc-list');const rows=Object.values(data.rows).sort((a,b)=>{const da=done(a),db=done(b);return da-db||a.id-b.id;});
  function done(r){return r.type!==1&&Number(s.claimed[r.id]||0)>0?1:0;}
  for(const r of rows){const rep=r.type===1,got=Number(s.claimed[r.id]||0);const have=rep?s.total-got*r.limit:s.total;const row=el('div','wc-row'+(done(r)?' done':''));
   const info=el('div','wc-info');info.append(el('b','',T(rep?'WISH_GACHA_TEXT_1':'WISH_GACHA_TEXT_2',r.limit).replace('\n',' ')));const bar=el('div','wc-rbar');const f=el('i');f.style.width=Math.min(100,have/r.limit*100)+'%';bar.append(f,el('span','',Math.min(have,r.limit)+'/'+r.limit));info.append(bar);
   row.append(info,chips(r.awards));const can=s.can_claim.includes(r.id);row.append(btn('gs-btn'+(done(r)?' white':''),done(r)?'Claimed':'Claim',async()=>{const x=await act({action:'claim',id:r.id},"Obtained");if(x)panel(parent);},!can));list.append(row);}
  w.append(list);parent.append(w);}
 return {capsule,panel,select};
})();
