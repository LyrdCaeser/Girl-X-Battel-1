'use strict';
// Alchemy (MidasWindow v2): free daily claim + escalating gem purchases. Rules: gxb2/midas.py. Sprites midas_*.
const Midas=(()=>{
 let busyLocal=false,note='';
 const A=n=>'/assets/midas/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 async function act(req){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/midas/action',req);state=r.state;if(typeof render==='function')render();return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;draw();}}
 let ov=null;
 function close(){ov?.remove();ov=null;}
 function open(){close();ov=el('div','md-overlay');ov.onclick=e=>{if(e.target===ov)close();};(window.GxbFrame?.root()||document.body).append(ov);draw();}
 function draw(){if(!ov)return;const info=state.midas_info;ov.replaceChildren();const w=el('div','md-win');ov.append(w);
  w.append(el('h2','','Alchemy'),(()=>{const b=el('button','md-close','✕');b.type='button';b.onclick=close;return b;})());
  if(!info){w.append(el('p','',"Loading…"));return;}
  const row=el('div','md-row');
  const free=el('div','md-card');free.append(img(A('midas_icon01')),el('b','','× '+number(info.base)),el('small','',info.free_ready?"Free 1/1":"Free 0/1"));
  const fb=el('button','md-btn','Free');fb.type='button';fb.disabled=!info.free_ready;fb.onclick=async()=>{const r=await act({action:'free'});if(r?.got)CampaignUI.popup('Alchemy',r.got);};free.append(fb);
  const buy=el('div','md-card');buy.append(img(A(info.buys>=2?'midas_icon03':'midas_icon02')),el('b','','× '+number(info.next_gold||0)),el('small','',`Purchases ${info.times-info.buys}/${info.times}`));
  const bb=el('button','md-btn gold','');bb.type='button';bb.disabled=!info.next_cost;if(info.next_cost){const g=img('/assets/currency/icon_2_small.png');bb.append(g,el('span','',String(info.next_cost['2']||0)));}else bb.textContent="Sold out";
  bb.onclick=async()=>{const c=info.next_cost?.['2'];if(c&&!confirm(`Spend ${c} Gems in ${number(info.next_gold)} Gold?`))return;const r=await act({action:'buy'});if(r?.got)CampaignUI.popup('Alchemy',r.got);};buy.append(bb);
  row.append(free,buy);w.append(row,el('p','md-note',note||"Resets daily at midnight (local time). Gold depends on your level."));}
 return {open};
})();
