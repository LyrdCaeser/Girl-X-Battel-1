'use strict';
// Simulated players (gxb2/bots.py, LOCAL-085): shared ranking window and chat lines. state.bots_info = {ranks, chat}.
const Bots=(()=>{
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 function avatar(a,size=40){const h=el('span','bt-av');const it=typeof itemCatalog!=='undefined'?itemCatalog?.[String(a)]:null;const src=it&&typeof itemPicture==='function'?itemPicture(it):'';if(src){const i=el('img');i.src=src;i.alt='';h.append(i);}else if(typeof portrait==='function'&&state.roster?.[0])h.append(portrait(state.roster[0].table_id,size));return h;}
 function row(r){const d=el('div','bt-row'+(r.me?' me':''));const rk=el('b','bt-rk');if(r.rank<=3){const i=el('img');i.src='/assets/arena/rank_icon0'+r.rank+'.png';i.alt=String(r.rank);rk.append(i);}else rk.textContent=String(r.rank);
  const t=el('div','bt-name');t.append(el('b','',r.name),el('small','','Lv.'+r.lv+' · S1'));d.append(rk,avatar(r.avatar),t,el('b','bt-score',typeof number==='function'?number(r.score):String(r.score)));return d;}
 function list(kind){const info=state.bots_info?.ranks?.[kind];const w=el('div','bt-list');if(!info){w.append(el('p','bt-empty','—'));return w;}w.append(el('div','bt-head',info.label));for(const r of info.rows)w.append(row(r));if(info.me.rank>info.rows.length)w.append(row(info.me));return w;}
 function open(kind,title='Rank'){const {body}=GirlUI.win({title,cls:'bt-win'});body.append(list(kind));}
 function chat(channel){const w=el('div','bt-chat');for(const m of state.bots_info?.chat?.[channel]||[]){const r=el('div','bt-msg');const t=el('div','bt-bubble');t.append(el('b','',m.name+'  Lv.'+m.lv),el('p','',m.text),el('small','',new Date(m.time*1000).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})));r.append(avatar(m.avatar,36),t);w.append(r);}requestAnimationFrame(()=>{w.scrollTop=w.scrollHeight;});return w;}
 return {open,list,chat,avatar};
})();
