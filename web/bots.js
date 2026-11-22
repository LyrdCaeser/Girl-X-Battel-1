'use strict';
// Shared ranking window: Soul Land reads verified live player results; other legacy modes retain their existing snapshots.
const Bots=(()=>{
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 function avatar(a,size=40){const h=el('span','bt-av');const it=typeof itemCatalog!=='undefined'?itemCatalog?.[String(a)]:null;const src=it&&typeof itemPicture==='function'?itemPicture(it):'';if(src){const i=el('img');i.src=src;i.alt='';h.append(i);}else if(typeof portrait==='function'&&state.roster?.[0])h.append(portrait(state.roster[0].table_id,size));return h;}
 function row(r){const d=el('div','bt-row'+(r.me?' me':''));const rk=el('b','bt-rk');if(r.rank<=3){const i=el('img');i.src='/assets/arena/rank_icon0'+r.rank+'.png';i.alt=String(r.rank);rk.append(i);}else rk.textContent=String(r.rank);
  const t=el('div','bt-name');t.append(el('b','',r.name),el('small','',(r.real?'Cấp ':'Lv.')+r.lv+' · '+(r.server_id||'S1')));
  const face=r.real?realAvatar(r.avatar):avatar(r.avatar);
  d.append(rk,face,t,el('b','bt-score',typeof number==='function'?number(r.score):String(r.score)));return d;}
 function realAvatar(value){
  const h=el('span','bt-av');const name=String(value||'head_1001');
  const safe=/^(?:head|partner_avatar)_\d{4,9}$/.test(name)||/^custom_[0-9a-f]{32}$/.test(name)?name:'head_1001';
  const i=el('img');i.src=typeof profileAsset==='function'?profileAsset(safe):'/assets/profile/head_1001.png';
  i.alt='';i.onerror=()=>{i.onerror=null;i.src='/assets/profile/head_1001.png';};
  h.append(i);return h;
 }
 function list(kind){const info=state.bots_info?.ranks?.[kind];const w=el('div','bt-list');if(!info){w.append(el('p','bt-empty','—'));return w;}w.append(el('div','bt-head',info.label));for(const r of info.rows)w.append(row(r));if(info.me.rank>info.rows.length)w.append(row(info.me));return w;}
 function open(kind,title='Rank'){
  const {body}=GirlUI.win({title,cls:'bt-win'});
  if(kind!=='soul_land'){body.append(list(kind));return;}
  body.append(el('p','bt-empty','Đang tải thành tích người chơi...'));
  // Request only on opening this board. Never reuse simulated ranking rows.
  api('/api/soul-land/ranking').then(data=>{
   if(!body.isConnected)return;
   body.replaceChildren();
   const board=el('div','bt-list');
   board.append(el('div','bt-head','Số ải đã vượt · '+String(data.server_id||'')));
   const players=Array.isArray(data.ranking)?data.ranking:[];
   if(!players.length)board.append(el('p','bt-empty','Chưa có người chơi nào vượt ải. Hãy trở thành người đầu tiên!'));
   for(const p of players)board.append(row({name:p.character_name,lv:p.level,
    score:p.score,rank:p.rank,avatar:p.avatar,server_id:p.server_id,me:p.me,real:true}));
   body.append(board);
  }).catch(()=>{
   if(body.isConnected){body.replaceChildren();body.append(el('p','bt-empty',
     'Chưa tải được bảng xếp hạng. Vui lòng thử lại.'));}
  });
 }
 function chat(channel){const w=el('div','bt-chat');for(const m of state.bots_info?.chat?.[channel]||[]){const r=el('div','bt-msg');const t=el('div','bt-bubble');t.append(el('b','',m.name+'  Lv.'+m.lv),el('p','',m.text),el('small','',new Date(m.time*1000).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})));r.append(avatar(m.avatar,36),t);w.append(r);}requestAnimationFrame(()=>{w.scrollTop=w.scrollHeight;});return w;}
 return {open,list,chat,avatar};
})();
