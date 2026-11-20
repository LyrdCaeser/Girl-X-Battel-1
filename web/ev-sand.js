'use strict';
// Beach Treasure Hunt (activity 309; capture 2026-09-29-fb/61) inside the Events hub: tabs Beach Treasure Hunt / Midsummer
// Task / Ocean Coin Exchange. The castle (50 parts), the round bar with its three rewards (160 / 320 / 640), Ocean Coins and
// Sand Shovels, Auto (from round 3). Rules: gxb2/ev_sand.py. Prefix bs-.
const SandHunt=(()=>{
 let tab='hunt',data=null,busy=false,last=[];
 const A=n=>'/assets/ev-sand/'+n;
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 function icon(id){id=String(id);if(id==='390'||id==='391')return A('icon_'+id+'.png');if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}if(Number(id)>=7000&&Number(id)<8000)return '/assets/skins/cards/'+id+'.webp';return it&&itemIcons.has(it.icon)?'/assets/item-icons/'+it.icon+'.png':'';}
 function chips(text){const w=el('span','bs-chips');for(const p of String(text||'').split('|')){if(!p.includes('#'))continue;const [k,v]=p.split('#');const c=el('span','bs-chip');const s=icon(k);if(s)c.append(img(s));c.append(el('b','',number(Number(v))));c.title=itemCatalog?.[k]?.name||data?.names?.[k]||k;w.append(c);}return w;}
 async function act(req){if(busy)return null;busy=true;try{const r=await api('/api/events/sand',req);state=r.state;return r;}catch(e){GirlUI.toast(e.message);return null;}finally{busy=false;if(typeof EventsHub!=='undefined'&&view==='events')EventsHub.render?.();else if(host?.isConnected)render(host);}}
 let host=null;
 async function render(parent){host=parent;if(!data){data=await api('/assets/ev-sand.json');}parent.replaceChildren();const s=state.ev_sand_info;if(!s)return;const w=el('div','bs-root');parent.append(w);
  const tabs=el('div','bs-tabs');for(const [k,label,ic]of [['hunt','Beach Treasure Hunt','activity_sand_search_rk_icon.png'],['task','Midsummer Task','activity_sand_mission.png'],['shop','Ocean Coin Exchange','activity_sand_shop_icon_rk.png']]){const b=btn('bs-tab'+(tab===k?' on':''),'',()=>{tab=k;render(parent);});b.append(img(A(ic)),el('small','',label));tabs.append(b);}w.append(tabs);
  if(tab==='hunt')hunt(w,s);else if(tab==='task')task(w,s);else shop(w,s);}
 function counters(s){const c=el('div','bs-counters');for(const [id,n]of [['391',s.coins],['390',s.shovels]]){const x=el('span','bs-count');x.append(img(A('icon_'+id+'.png')),el('b','',number(n)));x.title=data.names[id]||'';c.append(x);}return c;}
 function hunt(w,s){const box=el('div','bs-hunt');box.style.backgroundImage=`url('${A('activity_sand_search_bg.webp')}')`;
  box.append(img(A('activity_sand_search_logo_en_en.png'),'bs-logo'));
  const head=el('div','bs-head');const round=el('div','bs-round');round.append(img(A('activity_sand_search_round.png')),el('b','',String(s.round)));head.append(round);
  const bar=el('div','bs-bar');const max=s.marks[2];const fill=el('i');fill.style.width=Math.min(100,s.points/max*100)+'%';bar.append(fill,el('span','bs-pts',String(s.points)));
  s.marks.forEach((m,i)=>{const mk=el('div','bs-mark'+(s.claimed.includes(i)?' done':''));mk.style.left=(m/max*100)+'%';mk.append(chips(s.awards[i]),el('small','',String(m)));bar.append(mk);});head.append(bar,counters(s));box.append(head);
  const auto=btn('bs-auto','Auto',async()=>{const n=await GirlUI.promptNumber('Chọn số Xẻng Cát để đào tự động',{title:'Đào Tự Động',value:Math.min(10,s.shovels),min:1,max:s.shovels})||0;if(n<=0)return;const r=await act({action:'auto',times:n});if(r)after(r);},!s.auto||s.shovels<1);auto.title=s.auto?'Auto dig':'Auto dig available after entering Round 3';box.append(auto);
  const grid=el('div','bs-grid');let i=0;s.rows.forEach((n,r)=>{const row=el('div','bs-row');for(let c=0;c<n;c++,i++){const k=i,open=s.open[k];const cell=btn('bs-cell'+(open?' open':'')+(last.includes(k)?' fresh':''),'',async()=>{if(open)return;const r2=await act({action:'dig',index:k});if(r2)after(r2);},open||s.shovels<1&&!open);
    if(open){cell.append(img(A('activity_sand_search_item_icon5.png'),'bs-hole'),img(A('activity_sand_search_type_'+({5:6,6:5}[s.cells[k]]||s.cells[k])+'.png'),'bs-found'));}else cell.append(img(A('activity_sand_search_item_icon1.png')));row.append(cell);}grid.append(row);});box.append(grid);
  box.append(btn('bs-help','?',()=>CampaignUI.popup((data.text.ACTIVITY_SAND_HELP01||'')+'\n'+(data.text.ACTIVITY_SAND_HELP02||'')+'\n'+(data.text.ACTIVITY_SAND_HELP03||''),{})));w.append(box);}
 function after(r){last=r.opened||[];if(r.got&&Object.keys(r.got).length)GirlUI.toast("Round reward: "+Object.entries(r.got).map(([k,v])=>number(v)+' '+(itemCatalog?.[k]?.name||data.names[k]||k)).join(', '));if(r.new_round)GirlUI.toast("New round!");}
 function task(w,s){const box=el('div','bs-task');box.style.backgroundImage=`url('${A('activity_sand_mission_bg.webp')}')`;box.append(img(A('activity_sand_mission_logo_en_en.png'),'bs-logo'));
  for(const [daily,label]of [[true,data.text.ACTIVITY_SAND_MISSION_TAB01||'Daily'],[false,data.text.ACTIVITY_SAND_MISSION_TAB02||'Event']]){box.append(el('h4','bs-sub',label));
   for(const m of s.missions.filter(x=>x.daily===daily)){const row=el('div','bs-mission');row.append(el('span','bs-mtext',data.mission_text[m.id]||''),el('small','',Math.min(m.have,m.need)+'/'+m.need),chips(m.award));
    const can=!m.claimed&&m.have>=m.need;row.append(btn('gs-btn'+(m.claimed?' white':''),m.claimed?'Claimed':'Claim',async()=>{const r=await act({action:'mission',id:m.id});if(r)GirlUI.toast("Obtained");},!can));box.append(row);}}
  w.append(box);}
 function shop(w,s){const box=el('div','bs-shop');box.append(counters(s));const grid=el('div','bs-sgrid');
  for(const row of Object.values(data.shop).sort((a,b)=>a.type-b.type||a.id-b.id)){const bought=Number(s.shop[row.id]||0),lim=row.limit===''?null:Number(row.limit);const c=el('div','bs-item');c.append(chips(row.awards));const [,cost]=row.cost.split('#');
   c.append(el('small','',lim!=null?'Limit '+(lim-bought)+'/'+lim:'∞'),btn('gs-btn bs-buy','',async()=>{const r=await act({action:'buy',id:row.id});if(r)GirlUI.toast("Purchased");},(lim!=null&&bought>=lim)||s.coins<Number(cost)));c.lastChild.append(img(A('icon_391.png')),el('b','',cost));grid.append(c);}
  box.append(grid);w.append(box);}
 return {render};
})();
