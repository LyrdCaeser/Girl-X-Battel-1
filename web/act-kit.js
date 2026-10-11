'use strict';
// Generic event panel (LOCAL-059) for the events served by gxb2/activity_kit.py: mission board + exchange shop + daily
// supply. Rows, costs, awards and limits are the original tables; the layout is generic (not the per-event prefab). Prefix ak-.
const ActKit=(()=>{
 let data=null,draw=null,loading=null,tabFor={},busy=false,host=null,current=null;
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const pairs=t=>String(t||'').split('|').filter(s=>s.includes('#')).map(s=>s.split('#'));
 const fmt=n=>typeof number==='function'?number(Number(n)):String(n);
 function load(){if(data&&draw)return Promise.resolve(data);if(!loading)loading=Promise.all([api('/assets/activity-kit.json'),api('/assets/activity-draw.json')]).then(([k,d])=>{data=k;draw=d;return k;});return loading;}
 const ids=()=>data?[...new Set([...Object.keys(data.events),...Object.keys(draw.events)])].map(Number):[];
 const has=id=>!!(data?.events?.[id]||draw?.events?.[id]);
 function name(id){return data.names[id]||draw.names?.[id]||itemCatalog?.[id]?.name||"Item "+id;}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}return it&&itemIcons?.has?.(it.icon)?'/assets/item-icons/'+it.icon+'.png':null;}
 function chip(id,n,cls='ak-item'){const w=el('span',cls);const s=icon(id);if(s)w.append(img(s));else w.append(el('em','',name(id)));w.append(el('b','',fmt(n)));w.title=name(id)+' × '+fmt(n);return w;}
 async function act(req,url='/api/act-kit/action'){if(busy)return null;busy=true;try{const r=await api(url,{event:current,...req});state=r.state;if(r.got&&typeof GirlUI!=='undefined'&&Object.keys(r.got).length)GirlUI.toast("Received: "+Object.entries(r.got).map(([k,n])=>fmt(n)+' × '+name(k)).join(', '));return r;}catch(e){if(typeof GirlUI!=='undefined')GirlUI.toast(e.message);return null;}finally{busy=false;if(host?.isConnected)paint();}}
 async function render(parent,a){await load();host=parent;current=a.id;paint(a);if(data.events[a.id]&&!state.act_kit_info?.[a.id]?.started)act({action:'open'});}
 function paint(a){const dv=draw.events[current],dinfo=state.act_draw_info?.[current],info=state.act_kit_info?.[current]||{bought:{},missions:[],supply:{},items:{},currency:null},ev=data.events[current]||{title:dv?.title||''};if(!host||(!data.events[current]&&!dv))return;host.querySelector('.ak-root')?.remove();
  const root=el('div','ak-root');host.append(root);const head=el('div','ak-head');head.append(el('h2','',ev.title));
  const cur=info.currency;if(cur)head.append(chip(cur,state.items[cur]||0,'ak-cur'));root.append(head);
  const tabs=[];if(dv)tabs.push(['game','Juego']);if(ev.missions?.length)tabs.push(['missions',"Missions"]);if(ev.shop?.length)tabs.push(['shop','Canje']);
  let tab=tabFor[current];if(!tabs.some(t=>t[0]===tab))tab=tabs[0]?.[0];tabFor[current]=tab;
  const nav=el('nav','ak-tabs');for(const [id,label] of tabs){const b=el('button','ak-tab'+(tab===id?' on':''),label);b.type='button';b.onclick=()=>{tabFor[current]=id;paint();};nav.append(b);}root.append(nav);
  const sup=Object.entries(info.supply||{});if(sup.length){const row=el('div','ak-supply');row.append(el('span','',"Daily supply"),...sup.map(([k,n])=>chip(k,n)));const b=el('button','ak-btn',"Collect");b.type='button';b.onclick=()=>act({action:'supply'});row.append(b);root.append(row);}
  const list=el('div','ak-list');root.append(list);
  if(tab==='game')gameTab(list,dv,dinfo);
  if(tab==='missions')for(const m of info.missions){const row=el('div','ak-row'+(m.claimed>=m.limit?' done':''));const txt=el('div','ak-text');txt.append(el('b','',m.text),el('small','',m.tracked?fmt(m.claimed>=m.limit?m.need:Math.max(0,Math.min(m.need,m.have-m.claimed*m.need)))+' / '+fmt(m.need)+(m.limit>1?'  ·  Reclamado '+m.claimed+'/'+m.limit:''):"Unavailable in the local version"));
   const rw=el('div','ak-rewards');for(const [k,n] of pairs(m.award))rw.append(chip(k,n));const b=el('button','ak-btn'+(m.can?' go':''),m.claimed>=m.limit?'✔':"Claim");b.type='button';b.disabled=!m.can||busy;b.onclick=()=>act({action:'claim',id:m.id});row.append(txt,rw,b);list.append(row);}
  if(tab==='shop')for(const r of ev.shop){const bought=info.bought[r.id]||0,left=r.limit?r.limit-bought:null;const row=el('div','ak-row s'+(left===0?' done':''));const rw=el('div','ak-rewards');for(const [k,n] of pairs(r.award))rw.append(chip(k,n));
   const cost=el('div','ak-cost');for(const [k,n] of pairs(r.cost)){const c=chip(k,n);if((info.items[k]??state.items[k]??0)<Number(n))c.classList.add('lack');cost.append(c);}
   const b=el('button','ak-btn'+(left===0?'':' go'),left===0?"Sold out":"Redeem");b.type='button';const locked=info.unlock_by_spent&&(r.unlock||0)>(info.spent||0);b.disabled=left===0||busy||locked||pairs(r.cost).some(([k,n])=>Number(state.items[k]||0)<Number(n));if(locked)b.textContent='🔒 '+(info.spent||0)+'/'+r.unlock;b.onclick=()=>act({action:'buy',id:r.id});
   row.append(rw,cost,el('small','ak-limit',r.limit?"Remaining: "+left+'/'+r.limit:"Unlimited"),b);list.append(row);}
  root.append(el('p','ak-note',"Original rewards and costs. Without a server, mission progress starts when you open the event. If its minigame is not restored, the event supplies its currency daily."));}
 function gameTab(list,dv,di){
  const top=el('div','ak-game');const toks=el('div','ak-toks');for(const m of dv.modes)for(const [k,n] of pairs(m.cost))if(![...toks.children].some(c=>c.dataset.k===k)){const c=chip(k,state.items[k]||0);c.dataset.k=k;toks.append(c);}top.append(el('b','',"Tokens"),toks);
  const dl=Object.entries(di.daily||{});const day=el('div','ak-row');day.append(el('span','ak-text',"Daily Tokens"),...dl.map(([k,n])=>chip(k,n)));const db=el('button','ak-btn'+(di.daily_ready?' go':''),di.daily_ready?"Collect":'✔');db.type='button';db.disabled=!di.daily_ready||busy;db.onclick=()=>act({action:'daily'},'/api/act-draw/action');day.append(db);list.append(top,day);
  dv.modes.forEach((m,mi)=>{const row=el('div','ak-row');const t=el('div','ak-text');t.append(el('b','',dv.modes.length>1?'Sorteo '+(mi+1):'Sorteo'));const c=el('div','ak-rewards');for(const [k,n] of pairs(m.cost))c.append(chip(k,n));t.append(c);row.append(t);
   for(const times of [1,10]){const can=pairs(m.cost).every(([k,n])=>Number(state.items[k]||0)>=Number(n)*times);const b=el('button','ak-btn'+(can?' go':''),'×'+times);b.type='button';b.disabled=!can||busy;b.onclick=async()=>{const r=await act({action:'draw',mode:mi,times},'/api/act-draw/action');if(r&&r.special&&typeof GirlUI!=='undefined')GirlUI.toast("Special reward!");};row.append(b);}list.append(row);});
  if(dv.pity){const row=el('div','ak-row');const t=el('div','ak-text');t.append(el('b','',"Guaranteed reward"),el('small','',di.pity+' / '+dv.pity.max));row.append(t);list.append(row);}
  if(dv.buy){const row=el('div','ak-row');const t=el('div','ak-text');t.append(el('b','',"Buy chips"),el('small','','Compradas '+di.bought+'/'+dv.buy.limit));const cst=el('div','ak-rewards');for(const [k,n] of pairs(dv.buy.cost))cst.append(chip(k,n));const get=el('div','ak-rewards');for(const [k,n] of pairs(dv.buy.get))get.append(chip(k,n));row.append(t,cst,get);const can=di.bought<dv.buy.limit&&pairs(dv.buy.cost).every(([k,n])=>Number(state.items[k]||0)>=Number(n));const b=el('button','ak-btn'+(can?' go':''),"Buy");b.type='button';b.disabled=!can||busy;b.onclick=()=>act({action:'buy'},'/api/act-draw/action');row.append(b);list.append(row);}
  if(di.last?.length){const row=el('div','ak-row');const t=el('div','ak-text');t.append(el('b','',"Last result"));const rw=el('div','ak-rewards');for(const [k,n] of di.last)rw.append(chip(k,n));t.append(rw);row.append(t);list.append(row);}
  (dv.milestones||[]).forEach((m,i)=>{const got=di.claimed.includes(i),ok=di.draws>=m.need;const row=el('div','ak-row'+(got?' done':''));const t=el('div','ak-text');t.append(el('b','',m.need+' '+dv.unit),el('small','',Math.min(di.draws,m.need)+' / '+m.need));const rw=el('div','ak-rewards');for(const [k,n] of pairs(m.awards))rw.append(chip(k,n));const b=el('button','ak-btn'+(ok&&!got?' go':''),got?'✔':"Claim");b.type='button';b.disabled=!ok||got||busy;b.onclick=()=>act({action:'claim',index:i},'/api/act-draw/action');row.append(t,rw,b);list.append(row);});}
 return {load,ids,has,render};
})();
