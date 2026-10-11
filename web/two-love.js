'use strict';
// Matching Pairs (activity 331; capture 2026-09-29-fb/88) inside the Events hub, laid out from activity_2love_window.prefab
// on the 720 canvas (x/y centred, y up; the panel spans y 560…-600): background with the cupid, logo, description, the 4x4
// cards (rewards left to find → Start → heart backs → tap one), Arrow of Love counter (opens the Recharge Task) and the
// Start / Ongoing button. Rules: gxb2/two_love.py. Prefix tl-.
const MatchingPairs=(()=>{
 let data=null,host=null,busy=false,fresh=-1;
 const A=n=>'/assets/two-love/'+n+(n==='activity_2love_bg'?'.webp':'.png');
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 const T=k=>data?.text?.[k]||'';
 function at(e,x,y,w,h){e.style.left=`calc(${360+x-w/2} * var(--u))`;e.style.top=`calc(${560-y-h/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;e.style.height=`calc(${h} * var(--u))`;return e;}
 function iconSrc(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';if(id==='427')return A('icon_427');const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}return it&&itemIcons.has(it.icon)?'/assets/item-icons/'+it.icon+'.png':'';}
 function reward(card){const [k,n]=String(data.awards[card].awards).split('#');const w=el('span','tl-item');const s=iconSrc(k);if(s)w.append(img(s));w.append(el('b','',number(Number(n))));w.title=itemCatalog?.[k]?.name||k;return w;}
 async function act(req){if(busy)return null;busy=true;try{const r=await api('/api/two-love/action',req);state=r.state;return r;}catch(e){GirlUI.toast(e.message);return null;}finally{busy=false;if(host?.isConnected)draw();}}
 async function render(parent){host=parent;if(!data)data=await api('/assets/two-love.json');draw();}
 function draw(){const s=state.two_love_info;if(!s||!host)return;host.querySelector('.tl-root')?.remove();const root=el('div','tl-root');const st=el('div','tl-stage');root.append(st);host.append(root);
  st.append(at(img(A('activity_2love_bg'),'tl-abs tl-bg'),0,0,1024,1390),at(img(A('activity_2love_text_en_en'),'tl-abs tl-logo'),-8,291,560,128));
  st.append(at(btn('tl-abs tl-help','',()=>CampaignUI.popup(T('ACTIVITY_2LOVE_HELP').split('|').join('\n'),{})),-278,473,52,52));
  st.append(at(btn('tl-abs tl-detail','',()=>detail()),-275,415,52,54));
  const time=at(el('div','tl-abs tl-time',"Always available"),-22,217,472,56);st.append(time);
  st.append(at(el('p','tl-abs tl-desc',T('ACTIVITY_2LOVE_TEXT01')),-3,168,560,60));
  // the remaining rewards are laid face up on the free places until Start (Activity2LoveWindow:showFake)
  const left=Object.keys(data.awards).map(Number).filter(c=>!s.ids.includes(c));let li=0;
  s.ids.forEach((card,i)=>{const r=Math.floor(i/4),c=i%4;const cell=at(el('button','tl-abs tl-card'),-8+(c-1.5)*132,-164+(1.5-r)*150,116,136);cell.type='button';
   if(card){cell.style.backgroundImage=`url('${A(data.awards[card].image)}')`;cell.append(reward(card));const g=data.awards[card].group;if(Object.values(data.awards).filter(x=>x.group===g).every(x=>s.ids.includes(x.id)))cell.classList.add('done');if(i===fresh)cell.classList.add('fresh');}
   else if(s.is_cost){cell.style.backgroundImage=`url('${A('activity_2love_card')}')`;cell.classList.add('back');cell.onclick=()=>flip(i);}
   else{const f=left[li++];cell.style.backgroundImage=`url('${A(data.awards[f].image)}')`;cell.append(reward(f));cell.classList.add('fake');}
   st.append(cell);});
  const res=at(btn('tl-abs tl-res','',()=>tasks()),-9,-484,133,36);res.append(img(A('icon_427'),'tl-res-icon'),el('b','',number(s.arrows)),el('span','tl-plus','+'));st.append(res);
  const over=s.over,ongoing=s.is_cost===1;const sure=at(btn('tl-abs tl-sure'+(over||ongoing?' off':''),'',()=>over?act({action:'reset'}):act({action:'start'}),ongoing),-13,-546,246,64);
  if(over)sure.append(el('span','',T('ACTIVITY_2LOVE_TEXT05')+' ↻'));else if(ongoing)sure.append(el('span','',T('ACTIVITY_2LOVE_TEXT04')||'Ongoing'));
  else if(s.free)sure.append(el('span','',T('ACTIVITY_2LOVE_TEXT02')||'Free'));else{const c=el('span','tl-cost');c.append(img(A('icon_427')),el('small','','x1'));sure.append(c,el('span','',T('ACTIVITY_2LOVE_TEXT03')||'Start'));}
  st.append(sure);}
 async function flip(i){const r=await act({action:'flip',index:i});if(!r)return;fresh=i;draw();
  if(r.pair){const [k,n]=Object.entries(r.got)[0];GirlUI.toast('♥ Pair! +'+number(n)+' '+(itemCatalog?.[k]?.name||k));}}
 function detail(){const {body}=GirlUI.win({title:T('ACTIVITY_2LOVE_TEXT06')||'Rewards',cls:'tl-win'});const grid=el('div','tl-grid');const ids=state.two_love_info.ids;
  const groups={};for(const c of Object.values(data.awards))(groups[c.group]||=[]).push(c.id);
  for(const g of Object.keys(groups).sort((a,b)=>b-a)){const got=groups[g].every(c=>ids.includes(c));const cell=el('div','tl-opt'+(got?' got':''));cell.style.backgroundImage=`url('${A(data.awards[groups[g][0]].image)}')`;cell.append(reward(groups[g][0]));grid.append(cell);}
  body.append(grid);}
 function tasks(){const s=state.two_love_info;const {body,close}=GirlUI.win({title:T('ACTIVITY_2LOVE_TEXT10')||'Recharge Task',cls:'tl-win'});
  body.append(el('p','tl-note',"Local: VIP EXP currently uses your popularity — 10 per claimed daily task and 25 per trophy — and you receive 1 Arrow of Love each day."));
  for(const m of Object.values(data.missions)){const row=el('div','tl-mrow');const info=el('div','');info.append(el('b','',T('ACTIVITY_2LOVE_TEXT07').replace('{1}',m.num)));const bar=el('div','tl-bar');const f=el('i');f.style.width=Math.min(100,s.popularity/m.num*100)+'%';bar.append(f,el('span','',Math.min(s.popularity,m.num)+'/'+m.num));info.append(bar);
   const aw=el('span','tl-aw');aw.append(img(A('icon_427')),el('b','','1'));const done=s.claimed.includes(m.id);
   row.append(info,aw,btn('gs-btn'+(done?' white':''),done?(T('ACTIVITY_2LOVE_TEXT08')||'Claimed'):'Claim',async()=>{const r=await act({action:'mission',id:m.id});if(r){close();GirlUI.toast('+1 Arrow of Love');}},done||s.popularity<m.num));body.append(row);}}
 return {render};
})();
