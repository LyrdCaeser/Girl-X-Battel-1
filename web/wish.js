'use strict';
// Wish Capsule (activity 140; capture 2026-09-29-fb/47). Two faces: the Wish page added to the Capsule view (the chosen
// Wish Girl on the arcade pedestal, progress to the guaranteed draw with the current rate, Switch, Free / ×1 / ×10 with
// Advanced Capsules or gems → summons 22-26) and the event panel (activity/WishCapsule: banner, "Capsule" button and the
// draw-count rewards). Rules: gxb2/wish.py. Prefix wc-.
const WishCapsule=(()=>{
 let data=null,chaos=null;
 // Keep at most one living Spine model; repeated capsule renders must not
 // accumulate WebGL contexts or leave a ghost chibi after switching pages.
 let wishChibi=null,wishChibiGeneration=0;
 function releaseWishChibi(){
  wishChibiGeneration++;
  if(wishChibi){wishChibi.destroy();wishChibi=null;}
 }
 async function mountWishChibi(host,id,portrait){
  const generation=++wishChibiGeneration;
  try{
   const catalog=await ChibiBattle.catalogue();
   const model=catalog?.[String(id)];
   if(!model||generation!==wishChibiGeneration||!host.isConnected)return;
   const idle=model.animations?.includes('idle')?'idle':model.animations?.includes('houseidle')?'houseidle':null;
   if(!idle)return;
   const spine=await GxbSpine.mount(host,'/assets/chibis/'+model.model,{
    width:340,height:420,fit:.9,y:.61,className:'wc-chibi-canvas',
    sequence:[[idle,true]]
   });
   if(generation!==wishChibiGeneration||!host.isConnected){spine.destroy();return;}
   wishChibi=spine;
   portrait.hidden=true;
  }catch(error){
   // Keep the authentic portrait if a device cannot allocate a WebGL context.
   if(generation===wishChibiGeneration)console.warn('Wish chibi unavailable',error);
  }
 }
 const A=n=>'/assets/wish/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 const LOCAL_WISH_VI={"WISH_GACHA_TEXT_1":"Triệu Hồi Ước Nguyện {1} lần\n(Có thể nhận lại)","WISH_GACHA_TEXT_2":"Triệu Hồi Ước Nguyện {1} lần","WISH_GACHA_GOTOGACHA":"Đến Triệu Hồi","WISH_GACHA_TIPS_1":"Trong thời gian sự kiện, hãy Triệu Hồi Ước Nguyện đủ số lần yêu cầu để nhận phần thưởng tương ứng.","WISH_GACHA_TIPS_2":"Chạm để chọn Nữ Thần Ước Nguyện","WISH_GACHA_TIPS_3":"Bạn có thể tự do chọn hoặc thay đổi Nữ Thần Ước Nguyện bất cứ lúc nào trong thời gian sự kiện. Tỷ lệ nhận được Nữ Thần Ước Nguyện sẽ tăng dần sau mỗi lần Triệu Hồi Ước Nguyện. (Việc đổi Nữ Thần Ước Nguyện không làm thay đổi tỷ lệ nhận được Nữ Thần hiện tại hoặc tiến độ tăng tỷ lệ.)","WISH_GACHA_SELECT_PARTNER_WINDOW":"Chọn Nữ Thần Ước Nguyện","WISH_GACHA_SELECT_PARTNER_TIPS_1":"Hãy chọn Nữ Thần Ước Nguyện của bạn.","WISH_GACHA_SELECT_PARTNER_TIPS_2":"Xác nhận chọn Nữ Thần này làm Nữ Thần Ước Nguyện?","WISH_GACHA_PS":"Lưu ý: Lượt Triệu Hồi Ước Nguyện không tính vào Nhiệm Vụ Hằng Ngày và Cúp Thành Tích.","WISH_GACHA_TEXT3":"Tỷ lệ hiện tại","WISH_GACHA_TEXT4":"Sắp tăng tỷ lệ!","WISH_GACHA_TEXT5":"Đảm bảo nhận\nNữ Thần mới","WISH_GACHA_TEXT6":"Tiến Độ Hiện Tại","WISH_GACHA_NUM":"Lượt triệu hồi","WISH_GACHA_CHANCE":"Tỷ lệ","WISH_GACHA_TEXT9":"Thay Đổi","WISH_GACHA_TEXT10":"Lượt Triệu Hồi Ước Nguyện không tính vào Nhiệm Vụ Hằng Ngày và Cúp Thành Tích.","WISH_GACHA_TEXT11":"Thay Đổi","WISH_GACHA_TEXT12":"Xác nhận thay đổi Nữ Thần Ước Nguyện?"};
 const T=(k,...a)=>{let s=LOCAL_WISH_VI[k]||data?.text?.[k]||'';a.forEach((v,i)=>{s=s.replace('{'+(i+1)+'}',v);});return s;};
 const girl=id=>girlsCatalog.find(g=>g.id===Number(id));
 function picture(id,cls){const i=img('/assets/pictures/'+id+'.webp',cls);i.onerror=()=>{i.onerror=null;i.src='/assets/cards/partner_card_'+id+'.png';i.classList.add('card');};return i;}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}return it&&itemIcons.has(it.icon)?'/assets/item-icons/'+it.icon+'.png':'';}
 function chips(text){const w=el('span','wc-chips');for(const p of String(text||'').split('|')){if(!p.includes('#'))continue;const [k,v]=p.split('#');const c=el('span','wc-chip');const s=icon(k);if(s)c.append(img(s));c.append(el('b','',number(Number(v))));c.title=itemCatalog?.[k]?.name||k;w.append(c);}return w;}
 async function load(){if(!data)data=await api('/assets/wish.json?v=20261117-wish-localization-r3');return data;}
 async function loadChaos(){if(!chaos)chaos=await api('/assets/chaos/lyr_sonia.json?v=20261122-sonia-control-r1');return chaos;}
 async function act(req,msg){try{const r=await api('/api/wish/action',req);state=r.state;if(msg)GirlUI.toast(msg);return r;}catch(e){GirlUI.toast(e.message);return null;}finally{if(typeof render==='function')render();}}
 const hms=s=>{const h=Math.floor(s/3600),m=Math.floor(s%3600/60);return h+' giờ '+String(m).padStart(2,'0')+' phút';};
 // ≡ opens the actual live odds for this server, not hardcoded demo rates.
 async function oddsDetails(kind){
  const names={regular:'Triệu Hồi Thường',advanced:'Triệu Hồi Cao Cấp',wish:'Wish Ước Nguyện',sonia:'Wish Lyr Sonia'};
  const {body}=GirlUI.win({title:'≡ Phần Thưởng & Tỷ Lệ · '+names[kind],cls:'wc-odds-window'});
  body.append(el('p','wc-note','Đang mở danh sách Nữ Thần và tỷ lệ Triệu Hồi…'));
  try{
   const response=await api('/api/summon/rates');
   const pool=response.pools[kind==='sonia'?'advanced':kind];
   if(!pool)throw Error('Chưa tìm thấy danh sách Triệu Hồi');
   body.replaceChildren();
   if(kind==='sonia'){
     const si=state.chaos_summon_info||{};
     body.append(el('h3','','Nữ Thần Hỗn Độn · Lyr Sonia'));
     const feature=el('div','wc-odds-hero');
     feature.append(img('/assets/cards/partner_card_758001.png'),el('div','',
      'Tỷ lệ nhận Lyr Sonia mỗi lượt thường: '+(Number(si.rate||0)*100).toFixed(2)+'%.'));
     body.append(feature);
     body.append(el('p','wc-note',
       'Bảo hiểm đầu tiên: '+(si.first_guarantee||120)+' lượt. Các lần sau: '+(si.repeat_guarantee||150)+' lượt.'));
     body.append(el('p','wc-note','Tiến độ hiện tại: '+Number(si.times||0)+'/'+Number(si.guarantee||120)+
       ' · Còn '+Number(si.remaining||0)+' lượt.'));
     body.append(el('p','wc-note',
       'Khi đạt bảo hiểm: 98,5% Lyr Sonia · 1,5% Nữ Thần 5★ khác. Ra bất kỳ Nữ Thần từ 5★ trở lên sẽ làm mới lượt bảo hiểm.'));
     body.append(el('p','wc-note','Nếu chưa trúng Sonia, lượt thường sử dụng bảng Triệu Hồi Cao Cấp dưới đây, giảm theo tỷ lệ Sonia xuất hiện.'));
   }else if(kind==='wish'){
     const wi=state.wish_info||{};
     const selected=pool.girls.find(g=>g.id===Number(wi.select));
     const baseline=Number(selected?.probability||0)/100;
     const extra=Number(wi.rate||0);
     const actual=baseline+(1-baseline)*extra;
     body.append(el('p','wc-note','Nữ Thần đã chọn: '+(selected?.name||'Chưa chọn')+' · Tỷ lệ hiện tại '+(actual*100).toFixed(3)+'% (bao gồm cơ hội gốc và lượt Ước Nguyện).'));
     body.append(el('p','wc-note','Đảm bảo ra Nữ Thần đã chọn vào lượt Wish thứ 500 nếu chưa trúng. Khi trúng Nữ Thần đã chọn, lượt tích lũy bắt đầu lại.'));
   }else{
     body.append(el('p','wc-note','Tỷ lệ từng Nữ Thần được tính theo danh sách Triệu Hồi đang hoạt động trên máy chủ.'));
   }
   const stars=el('div','wc-odds-stars');
   for(const tier of pool.stars){
    const rarity=el('div','wc-odds-tier');
    rarity.append(el('b','',tier.star+'★'),el('span','',Number(tier.probability).toLocaleString('vi-VN',{maximumFractionDigits:4})+'%'));stars.append(rarity);
   }
   if(kind==='sonia')body.append(el('h3','','Danh sách khi không ra Sonia'));
   body.append(stars);
   const scroll=el('div','wc-odds-list');
   for(const entry of pool.girls){
    const row=el('div','wc-odds-row');
    row.append(el('span','',entry.name),el('small','',entry.star+'★'),
      el('b','',Number(entry.probability).toLocaleString('vi-VN',{maximumFractionDigits:5})+'%'));
    scroll.append(row);
   }
   body.append(el('h3','','Chi tiết Nữ Thần có thể nhận'),scroll,
     el('p','wc-note','Đây là tỷ lệ theo từng lượt. Phần thưởng đã nhận được đưa vào đội hình của bạn.'));
  }catch(e){body.replaceChildren(el('p','wc-note',e.message||'Không xem được tỷ lệ, hãy thử lại.'));}
 }
 const oddsButton=kind=>btn('wc-odds-button','≡',()=>oddsDetails(kind));
 // --- Capsule page: Advanced → Wish → Lyr Sonia share the middle slot. -----------------------------------------------
 let page=0;
 function arrow(dir,target,label){const b=btn('wc-arrow '+dir,'',()=>{page=target;capsule();});b.append(img(A('wish_capsule_arrow_'+dir)));b.setAttribute('aria-label',label);return b;}
 function dots(){const d=el('div','wc-dots');for(let i=0;i<3;i++)d.append(img(A('wish_capsule_dot'+(i===page?1:0))));return d;}
 async function capsule(){await Promise.all([load(),loadChaos()]);const s=state.wish_info;if(!s){releaseWishChibi();return;}
 const adv=document.querySelector('#capsule-view .capsule-banner.advanced');if(!adv){releaseWishChibi();return;}
 releaseWishChibi();
  const regular=document.querySelector('#capsule-view .capsule-banner.regular');
  if(regular&&!regular.querySelector(':scope > .wc-odds-button'))regular.append(oddsButton('regular'));
  adv.querySelectorAll(':scope>.wc-arrow,:scope>.wc-dots,:scope>.wc-odds-button').forEach(e=>e.remove());adv.append(arrow('right',1,'Triệu Hồi Ước Nguyện'),dots(),oddsButton('advanced'));adv.hidden=page!==0;
  let box=$('wish-banner');if(!box){box=el('div','capsule-banner wc-banner');box.id='wish-banner';adv.after(box);}box.replaceChildren();box.hidden=page!==1;
  const art=el('div','capsule-banner-art wc-art');
  let chibiHost=null,portrait=null;
  if(s.select){
   chibiHost=el('div','wc-chibi');
   portrait=picture(s.select,'wc-girl wc-fallback');
   art.append(chibiHost,portrait);
  }else art.append(btn('wc-empty',T('WISH_GACHA_TIPS_2')||'Chạm để chọn Nữ Thần Ước Nguyện',()=>select()));
  const g=girl(s.select);if(g)art.append(el('b','wc-name',g.name));art.append(btn('wc-help','?',()=>tips()));
  const ctl=el('div','capsule-banner-controls wc-controls');ctl.append(img(A('wish_capsule_summon_text01_en_en'),'wc-logo'));
  const prog=el('div','wc-progress');const rate=el('span','wc-rate');rate.append(img(A('wish_capsule_icon2')),el('b','',(s.rate*100).toFixed(s.rate<0.001?3:2)+'%'));
  const bar=el('div','wc-bar');const fill=el('i');fill.style.width=Math.min(100,s.times/data.odds.guarantee*100)+'%';bar.append(fill,el('span','',s.times+'/'+data.odds.guarantee));
  prog.append(rate,bar,btn('wc-switch',T('WISH_GACHA_TEXT9')||'Thay Đổi',()=>select()));ctl.append(prog);
  const cnt=el('div','capsule-count');cnt.append(img('/assets/currency/icon_36.png','capsule-token'),el('b','',number(state.items?.['36']||0)));ctl.append(cnt);
  ctl.append(el('p','capsule-free',s.free_in<=0?"Có lượt miễn phí":"Miễn phí sau "+hms(s.free_in)));
  const buttons=el('div','capsule-buttons');const scroll=Number(state.items?.['36']||0),gems=Number(state.items?.['2']||0);
  const draw=(sid,label,cost,dis,cls='')=>{const b=btn('capsule-draw'+cls,label,()=>{if(!s.select){select();return;}action('SUMMON',{summon_id:sid,times:1});},dis);const st=el('strong');st.append(cost);b.append(st);return b;};
  const tk=n=>{const f=document.createDocumentFragment();f.append(n+' ');f.append(img('/assets/currency/icon_36.png','cost-token'));return f;};
  const gm=n=>{const f=document.createDocumentFragment();f.append(n+' ');f.append(img('/assets/currency/icon_2_small.png','cost-token'));return f;};
  buttons.append(draw(26,"Miễn Phí",'1',s.free_in>0),draw(24,"Triệu Hồi 1",tk(1),scroll<1),draw(25,"Triệu Hồi 10",tk(10),scroll<10),draw(22,"Dùng Kim Cương ×1",gm(250),gems<250,' gem-draw'),draw(23,"Dùng Kim Cương ×10",gm(2200),gems<2200,' gem-draw'));
  ctl.append(buttons);box.append(art,ctl,arrow('left',0,'Triệu Hồi Cao Cấp'),arrow('right',2,'Banner Lyr Sonia'),dots(),oddsButton('wish'));
  let cb=$('chaos-banner');if(!cb){cb=el('div','capsule-banner chaos-banner');cb.id='chaos-banner';box.after(cb);}cb.replaceChildren();cb.hidden=page!==2;
  const ca=el('div','capsule-banner-art chaos-art');ca.style.backgroundImage="url('"+chaos.banner+"')";
  const cc=el('div','capsule-banner-controls chaos-controls');
  cc.append(el('small','chaos-kicker',chaos.faction.name),el('h3','chaos-title',chaos.name),el('p','chaos-copy','Nữ Thần Hỗn Độn nguyên bản 10★ · có thể Thức Tỉnh đến 25★'));
  const ci=state.chaos_summon_info||{};
  const chaosRate=(Number(ci.rate||0)*100).toFixed(2);
  const chaosRemaining=Math.max(0,Number(ci.remaining??ci.guarantee??100));
  cc.append(el('p','chaos-copy','Tỷ lệ Lyr Sonia: '+chaosRate+'% · Bảo hiểm sau tối đa '+chaosRemaining+' lượt nữa'));
  cc.append(el('p','chaos-copy','Bảo hiểm lần đầu 120 lượt, từ lần sau 150 lượt. Trúng bảo hiểm: 98,5% Sonia · 1,5% Nữ Thần 5★ khác.'));
  const ticket=el('div','chaos-ticket');ticket.append(img(chaos.ticket.icon),el('span','',chaos.ticket.name),el('b','',number(state.items?.[String(chaos.ticket.id)]||0)));cc.append(ticket);
  const cbts=el('div','capsule-buttons chaos-buttons'),have=Number(state.items?.[String(chaos.ticket.id)]||0);
  for(const drawInfo of chaos.summons){const b=btn('capsule-draw','Triệu Hồi ×'+drawInfo.count,()=>action('SUMMON',{summon_id:drawInfo.id,times:1}),have<drawInfo.count);const cost=el('strong');cost.append(drawInfo.count+' ',img(chaos.ticket.icon,'cost-token'));b.append(cost);cbts.append(b);}
  cc.append(cbts);cb.append(ca,cc,arrow('left',1,'Triệu Hồi Ước Nguyện'),dots(),oddsButton('sonia'));
  if(s.select&&chibiHost&&page===1)void mountWishChibi(chibiHost,s.select,portrait);
 }
 function select(){const s=state.wish_info;const {body,close}=GirlUI.win({title:T('WISH_GACHA_SELECT_PARTNER_WINDOW')||'Chọn Nữ Thần Ước Nguyện',cls:'wc-select'});
  body.append(el('p','wc-note',T('WISH_GACHA_TIPS_3')));const grid=el('div','wc-grid');
  for(const id of data.partners){const g=girl(id);const c=btn('wc-card'+(id===s.select?' on':''),'',async()=>{if(id===s.select){close();return;}if(s.select&&!await GirlUI.confirm('Đổi Nữ Thần Ước Nguyện đã chọn?',{title:'Đổi Nữ Thần',ok:'Đổi'}))return;close();await act({action:'select',partner:id});capsule();});
   c.append(img('/assets/cards/partner_card_'+id+'.png'),el('small','',g?.name||String(id)));if(g?.group)c.append(img('/assets/factions/group'+g.group+'.png','wc-faction'));grid.append(c);}
  body.append(grid);}
 function tips(){const s=state.wish_info;const {body}=GirlUI.win({title:T('WISH_GACHA_TEXT6')||'Tiến Độ Hiện Tại',cls:'wc-tips'});
  const rows=el('div','wc-tiers');for(let i=1;i<=5;i++){const r=el('div','wc-tier'+(s.times>=Number(T('WISH_GACHA_NUM'+i))?' on':''));r.append(el('b','',T('WISH_GACHA_NUM'+i)+' '+(T('WISH_GACHA_NUM')||'Lượt triệu hồi')),el('span','',i<5?T('WISH_GACHA_NUM'+(i+5)):(T('WISH_GACHA_TEXT5')||'Đảm bảo nhận').replace('\n',' ')));rows.append(r);}
  body.append(rows,el('p','wc-note',T('WISH_GACHA_TIPS_3')),el('p','wc-note',T('WISH_GACHA_TEXT10')));}
 // --- Event panel (activity 140) -------------------------------------------------------------------------------------
 async function panel(parent){await load();const s=state.wish_info;parent.replaceChildren();const w=el('div','wc-event');
  const top=el('div','wc-top');top.style.backgroundImage=`url('${A('wish_capsule_bg')}')`;top.append(img(A('wish_capsule_text01_en_en'),'wc-title'));const tx=el('div','wc-text');tx.append(el('p','',T('WISH_GACHA_TIPS_1')));top.append(tx);
  top.append(btn('wc-go gs-btn white',T('WISH_GACHA_GOTOGACHA')||'Triệu Hồi',()=>showView('capsule')));w.append(top);
  const list=el('div','wc-list');const rows=Object.values(data.rows).sort((a,b)=>{const da=done(a),db=done(b);return da-db||a.id-b.id;});
  function done(r){return r.type!==1&&Number(s.claimed[r.id]||0)>0?1:0;}
  for(const r of rows){const rep=r.type===1,got=Number(s.claimed[r.id]||0);const have=rep?s.total-got*r.limit:s.total;const row=el('div','wc-row'+(done(r)?' done':''));
   const info=el('div','wc-info');info.append(el('b','',T(rep?'WISH_GACHA_TEXT_1':'WISH_GACHA_TEXT_2',r.limit).replace('\n',' ')));const bar=el('div','wc-rbar');const f=el('i');f.style.width=Math.min(100,have/r.limit*100)+'%';bar.append(f,el('span','',Math.min(have,r.limit)+'/'+r.limit));info.append(bar);
   row.append(info,chips(r.awards));const can=s.can_claim.includes(r.id);row.append(btn('gs-btn'+(done(r)?' white':''),done(r)?'Đã Nhận':'Nhận',async()=>{const x=await act({action:'claim',id:r.id},"Đã nhận phần thưởng");if(x)panel(parent);},!can));list.append(row);}
  w.append(list);parent.append(w);}
 return {capsule,panel,select};
})();
