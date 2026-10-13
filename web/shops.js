'use strict';
// Shopping Street (ShopMapWindow), Market (market_window.prefab) and tabbed stores (ShopWindow). Rules: gxb2/shops.py.
// Coordinates are prefab pixels on the 720×1280 design (--u); shelf = content 860×653 at y -217, grid 4×2 cells 162×240.
const Shops=(()=>{
 let data=null,loading=null,mode='map',sid=7,page=0,group=0,origin='home',note='',busyLocal=false,girl=null,girlKey='',timer=null;
 const A=n=>'/assets/shops/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const load=()=>data?Promise.resolve(data):(loading||=api('/assets/shops.json').then(d=>data=d));
 const MAP=[['cafe',11,-165,340,338,305,'Cafe',-47,-138],['skin',0,200,320,307,240,'Skin Store',0,-138],['market',7,-135,50,349,262,'Market',-35,-108],['exchange',13,188,-23,356,339,'Lucky Store',0,-118],['artifact',17,-152,-246,323,290,'Antique Store',-20,-100],['unopen',0,215,-315,311,280,'Coming Soon',0,-115]];
 const TABS=[2,3,13,5,6,9];
 function root(){let r=$('shops-view');if(!r){r=el('section','shops-view');r.id='shops-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from,shop){origin=from||view;note='';page=0;group=0;if(shop){mode='shop';sid=shop;}else mode='map';load().then(()=>{showView('shops');render();});}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const row=itemCatalog?.[id];const extra=state.acquisition?.item_icons?.[id];return (row&&itemPicture(row))||(extra&&'/assets/slots/'+extra+'.png')||(row?.icon?'/assets/shops/items/'+row.icon+'.png':A('prop_img'));}
 function nameOf(id){id=String(id);return id==='1'?"Gold":id==='2'?"Gems":itemCatalog?.[id]?.name||"Item "+id;}
 function px(e,x,y,w,h){e.style.left=`calc(${x} * var(--u))`;e.style.top=`calc(${y} * var(--u))`;if(w!=null)e.style.width=`calc(${w} * var(--u))`;if(h!=null)e.style.height=`calc(${h} * var(--u))`;return e;}
 function center(e,x,y,w,h){return px(e,360+x-w/2,640-y-h/2,w,h);}
 async function act(req){if(busyLocal)return;busyLocal=true;note='';try{const r=await api('/api/shops/action',req);state=r.state;if(r.got)CampaignUI.popup('Compra realizada',r.got);}catch(e){note=e.message;}finally{busyLocal=false;render();}}
 function clearGirl(){try{girl?.destroy();}catch{}girl=null;girlKey='';}
 function render(){const r=root();if(view!=='shops'){clearGirl();clearInterval(timer);timer=null;return;}if(!data){load().then(render);return;}
  const keep=r.querySelector('.sh-girl');r.replaceChildren();if(mode==='map')map(r);else shop(r,keep);}
 function top(r,cur){const t=el('header','sh-top');for(const id of cur){const c=el('span','sh-cur');c.append(img(icon(id)),el('b','',number(state.items[id]||0)));c.title=nameOf(id);t.append(c);}const b=el('button','sh-back');b.type='button';b.append(img('/assets/ui/win_back_btn.png'));b.onclick=()=>{clearGirl();if((sid===6&&origin==='menu-explorer')||origin==='house-exam'){showView(origin);return;}if(mode==='shop'&&origin!=='direct'){mode='map';render();}else showView(origin==='shops'?'home':origin);};t.append(b);r.append(t);}

 // ---- ShopMapWindow ----
 function map(r){clearGirl();const stage=el('div','sh-stage');const bg=center(img(A('shop_map_bg'),'sh-map-bg'),0,0,1280,1280);stage.append(bg);
  for(const [k,target,x,y,w,h,label,lx,ly]of MAP){const b=center(el('button','sh-building'),x,y,w,h);b.type='button';b.append(img(A('shop_'+k)));const l=el('span','sh-building-label',label);l.style.left=`calc(50% + ${lx} * var(--u))`;l.style.top=`calc(50% - ${ly} * var(--u))`;b.append(l);
   b.onclick=()=>{if(k==='skin'&&typeof Skins!=='undefined'&&Skins.store){Skins.store();return;}if(!target){CampaignUI.popup('This Store is still under construction.',{});return;}mode='shop';sid=target;page=0;group=0;render();};stage.append(b);}
  r.append(stage);top(r,['1','2']);r.querySelector('.sh-top').prepend(el('h1','','Shopping Street'));}

 // ---- MarketWindow / ShopWindow ----
 function shop(r,keep){const cfg=data.shops[sid],info=state.shops_info?.[sid];const stage=el('div','sh-stage');const M=sid===7,CY=M?-217:-194,GY=CY+(M?-46:-50)+145;
  stage.append(center(img(A(String(cfg.shop_bg||'market_scene_').replace(/_$/,'')),'sh-scene'),0,0,1559,1559));
  const gpos=el('div','sh-girl');if(keep&&girlKey===String(sid)+':'+cfg.girls_model){stage.append(keep);}else{clearGirl();const [ox,oy]=String(cfg.offset||'0|0').split('|').map(Number),fx=(M?-90:-115)+(M?0:ox),fy=CY+(M?100:90)+(M?0:oy);stage.append(px(gpos,360+fx-450,640-fy-1300,900,Math.min(1400,(640-CY+300)-(640-fy-1300))));mountGirl(gpos,cfg);}
  const shelf=center(img(A(sid===7?'market_bg':String(cfg.shop_banner||'shop_bg_type01_png').replace(/_png$/,'')),'sh-shelf'),0,CY,860,653);stage.append(shelf);
  const tabs=TABS.includes(sid);
  if(tabs){const nav=px(el('nav','sh-tabs'),10,118,700,62);TABS.forEach((t,i)=>{const b=el('button','sh-tab'+(t===sid?' on':''));b.type='button';const c=data.shops[t];const pos=i===0?'left':i===TABS.length-1?'right':'mid';b.style.borderImageSource=`url('${A('nav_btn_'+(t===sid?'blue':'white')+'_'+pos)}')`;if(c?.icon)b.append(img(A(String(c.icon).replace(/_png$/,''))));b.append(el('span','',c?.name||''));b.disabled=t===2;b.title=t===2?"Transfer inventory was generated by the server and cannot be recovered.":'';b.onclick=()=>{if(t===3){openMenu('slots','shops');return;}sid=t;page=0;render();};nav.append(b);});stage.append(nav);}
  if(!info){r.append(stage);top(r,['1','2']);return;}
  if(!info.open){stage.append(center(el('p','sh-locked',"Unlocks at level "+info.limit_level),0,CY,600,80));}
  let goods=info.goods.filter(g=>!group||g.group===group);
  if(sid===11||sid===17){const groups=[...new Set(info.goods.map(g=>g.group))].sort((a,b)=>a-b);const gb=px(el('div','sh-groups'),20,tabs?190:118,680,70);const all=el('button','sh-group'+(group?'':' on'),'All');all.type='button';all.onclick=()=>{group=0;page=0;render();};gb.append(all);
   for(const g of groups){const b=el('button','sh-group'+(group===g?' on':''));b.type='button';if(sid===11)b.append(img(A(`shop_group${g}_${group===g?2:1}`)));else b.textContent='Set '+g;b.onclick=()=>{group=g;page=0;render();};gb.append(b);}stage.append(gb);}
  const pages=Math.max(1,Math.ceil(goods.length/8));page=Math.min(page,pages-1);
  goods.slice(page*8,page*8+8).forEach((g,i)=>{const cx=-245+(i%4)*162,cy=GY-Math.floor(i/4)*240;cell(stage,g,cx,cy);});
  if(pages>1){for(const [dx,d]of [[-340,-1],[340,1]]){const a=center(el('button','sh-arrow'+(d<0?' left':'')),dx,CY-48,36,112);a.type='button';a.append(img(A('market_arrow')));a.disabled=(d<0&&page===0)||(d>0&&page>=pages-1);a.onclick=()=>{page+=d;render();};stage.append(a);}
   const dots=center(el('div','sh-dots'),0,CY+(M?-288:-295),44*pages,16);for(let i=0;i<pages;i++){const d=el('i');d.style.backgroundImage=`url('${A(i===page?'market_dot_bg2':'market_dot_bg1')}')`;d.onclick=()=>{page=i;render();};dots.append(d);}stage.append(dots);}
  if(info.refresh_at){const t=center(el('div','sh-timer'),M?180:235,CY+(M?260:290),260,70);t.append(el('small','','Làm Mới Sau'),el('b','sh-clock',clock(info.refresh_at)));stage.append(t);clearInterval(timer);timer=setInterval(()=>{const c=root().querySelector('.sh-clock');if(!c||view!=='shops'){clearInterval(timer);return;}c.textContent=clock(info.refresh_at);if(info.refresh_at*1000<=Date.now()){clearInterval(timer);api('/api/state').then(s=>{state=s;render();});}},1000);}
  const cfgR=data.shops[sid];if(Number(cfgR.is_refresh)&&cfgR.refresh_cost&&sid!==7){const [cid,cn]=String(cfgR.refresh_cost).split('#');const b=center(el('button','sh-refresh'),245,CY+225,200,60);b.type='button';b.style.backgroundImage=`url('${A('blue_btn_54_54')}')`;b.append(el('span','','Làm Mới'),img(icon(cid)),el('b','',number(cn)));b.onclick=async()=>{if(await GirlUI.confirm(`Dùng ${number(cn)} ${nameOf(cid)} để làm mới Cửa Hàng?`,{title:'Làm Mới Cửa Hàng',ok:'Làm Mới'}))act({action:'refresh',shop:sid});};stage.append(b);}
  if(note)stage.append(center(el('p','sh-note',note),0,-560,600,60));
  r.append(stage);const cur=[...new Set(String(cfg.economy_show||'').split('|').filter(Boolean))];top(r,cur.length?cur:['1','2']);r.querySelector('.sh-top').prepend(el('h1','',cfg.name||'Store'));}
 function clock(at){const s=Math.max(0,at-Math.floor(Date.now()/1000));return [Math.floor(s/3600),Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');}
 function cell(stage,g,cx,cy){const done=g.limit>=0&&g.bought>=g.limit;const bg=center(el('div','sh-cell'+(done?' done':'')),cx,cy-20,156,210);stage.append(bg);
  const it=center(el('button','sh-item'),cx,cy,108,108);it.type='button';it.style.backgroundImage=`url('${A('shop_icon_bg')}')`;it.append(img(icon(g.item[0])),el('b','',number(g.item[1])));it.title=nameOf(g.item[0])+(g.limit>0?` · limit ${g.bought}/${g.limit}`:'');it.onclick=()=>CampaignUI.popup(nameOf(g.item[0])+' ×'+number(g.item[1])+(g.limit>0?` — purchases ${g.bought}/${g.limit}`:''),{});if(done)it.append(img(A('purchased'),'sh-sold'));stage.append(it);
  const b=center(el('button','sh-buy'),cx,cy-87,120,54);b.type='button';b.style.backgroundImage=`url('${A(done?'white_btn_54_54':'blue_btn_54_54')}')`;
  if(done){b.append(el('span','sh-bought','Purchased'));b.disabled=true;}else{const short=Number(state.items[g.cost[0]]||0)<g.cost[1];b.append(img(icon(g.cost[0])),el('b',short?'short':'',number(g.cost[1])));b.onclick=()=>act({action:'buy',shop:sid,index:g.index});}
  stage.append(b);if(g.limit>1){stage.append(center(el('small','sh-limit',`${g.bought}/${g.limit}`),cx,cy+62,120,22));}}
 async function mountGirl(host,cfg){const m=data.models[String(cfg.girls_model)];if(!m)return;const key=String(sid)+':'+cfg.girls_model;girlKey=key;
  try{const idle=m.idle||'idle';const g=await GxbSpine.mount(host,'/assets/spine/'+m.resource,{width:900,height:1400,scale:Number(cfg.scale)||1,origin:[.5,1300/1400],className:'sh-girl-canvas',sequence:[[idle,true]]});if(girlKey!==key||!host.isConnected){g.destroy();return;}girl=g;
   host.onclick=()=>{const c=m.click[Math.floor(Math.random()*m.click.length)];const names=g.figure.spineData.animations.map(a=>a.name);if(c&&names.includes(c)){g.figure.state.setAnimation(0,c,false);g.figure.state.addAnimation(0,idle,true,0);}};}catch{}}
 return {open,render};
})();
