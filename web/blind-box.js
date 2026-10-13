'use strict';
// Blind Box Frenzy (activity 338): 3x3 boxes (8 chosen rewards + the round's Grand Reward), x1 / x5 open, tier selection window.
// Layout from the promo image (docs/references/2026-09-30-user/01) and ActivityBlindBoxItem (cell -> slot / colour tables). Rules: gxb2/blind_box.py. Prefix bb-.
const BlindBox=(()=>{
 let data=null,loading=null,host=null,busy=false,picking=null,note='',last=null;
 const A=n=>'/assets/blind-box/'+n+'.png';
 const CELL_COLOR=[5,2,2,3,1,2,3,3,4],CELL_SLOT=[8,1,2,4,0,3,5,6,7];   // ActivityBlindBoxItem.awardType / awardOrder
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis||busy;return b;};
 const fmt=n=>typeof number==='function'?number(Number(n)):String(n);
 const info=()=>state.blind_box_info;
 const T=k=>data.text[k]||'';
 function load(){if(data)return Promise.resolve(data);if(!loading)loading=api('/assets/blind-box.json').then(d=>{data=d;});return loading;}
 const row=id=>data.rows.find(r=>r.id===id);
 function name(id){return itemCatalog?.[id]?.name||data.names[id]||"Item "+id;}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}return null;}
 function reward(id,cls='bb-item'){const [k,n]=String(row(id).awards).split('|')[0].split('#');const w=el('span',cls);const s=icon(k);if(s)w.append(img(s));else w.append(el('em','',name(k)));w.append(el('b','',fmt(n)));w.title=name(k)+' × '+fmt(n);return w;}
 async function act(req){if(busy)return null;busy=true;note='';try{const r=await api('/api/blind-box/action',req);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busy=false;}}
 async function render(parent){await load();host=parent;picking=null;paint();}
 function paint(){if(!host)return;host.querySelector('.bb-root')?.remove();const s=info(),root=el('div','bb-root');host.append(root);
  root.style.backgroundImage=`url('${A('activity_blind_box_bg')}')`;
  const head=el('div','bb-head');head.append(img(A('activity_blind_box_bg_title_en_en'),'bb-logo'),el('b','bb-round','Round '+s.round+'/'+s.rounds));root.append(head);
  const tk=el('div','bb-tickets');tk.append(el('span','','Cupones: '),el('b','',fmt(s.tickets)),btn('bb-mini'+(s.daily_ready?' go':''),s.daily_ready?'+'+s.daily+' diarios':'✔',async()=>{await act({action:'daily'});paint();},!s.daily_ready),btn('bb-mini','?',()=>CampaignUI.popup(T('ACTIVITY_BLIND_BOX_HELP').split('|').join('\n'),{})));root.append(tk);
  const grid=el('div','bb-grid');CELL_SLOT.forEach((slot,c)=>{const color=CELL_COLOR[c];const cell=el('div','bb-cell c'+color);cell.style.backgroundImage=`url('${A('activity_blind_box_add_card_'+color)}')`;
   const it=s.ready?s.slots[slot]:(slot===0?s.slots[0]:null);
   if(it){cell.append(reward(it.id));cell.append(el('small','bb-left','x'+it.left+(it.left===0?' ✔':'')));if(it.chance!=null&&it.left>0)cell.append(el('small','bb-chance',it.chance+'%'));if(it.left===0)cell.classList.add('empty');if(slot===0)cell.append(el('em','bb-grand','Grand'));
    if(!s.locked&&slot>0)cell.append(btn('bb-swap','⇄',()=>choose()));}
   else{cell.classList.add('blank');cell.append(el('span','bb-add','+'));cell.onclick=()=>choose();}
   grid.append(cell);});root.append(grid);
  const acts=el('div','bb-acts');
  acts.append(btn('bb-open','x1',()=>open(1),!s.ready||s.tickets<1||s.total_left<1),btn('bb-open','x5',()=>open(5),!s.ready||s.tickets<5||s.total_left<5));
  if(!s.ready)acts.append(btn('bb-open pick',"Choose rewards",()=>choose()));
  if(s.grand_taken&&s.round<s.rounds)acts.append(btn('bb-open next','Ir a la ronda '+(s.round+1),async()=>{if(await GirlUI.confirm(T('ACTIVITY_BLIND_BOX_TEXT08')||'Chuyển sang vòng tiếp theo?',{title:'Xác Nhận',ok:'Tiếp Tục'})){await act({action:'next'});paint();}}));
  root.append(acts,el('small','bb-info',"Guaranteed jackpot in "+Math.max(0,data.guarantee+1-s.draws)+" opens · Remaining: "+s.total_left+" boxes"));
  if(last?.got&&Object.keys(last.got).length){const g=el('div','bb-last');g.append(el('b','',"Received:"));for(const [k,n] of Object.entries(last.got)){const w=el('span','bb-item');const src=icon(k);if(src)w.append(img(src));w.append(el('b','',fmt(n)));w.title=name(k);g.append(w);}root.append(g);}
  root.append(el('p','bb-note',note));
  if(typeof ActKit!=='undefined'&&ActKit.has(338)){const box=el('div','bb-missions');root.append(box);ActKit.render(box,{id:338});}
  if(picking)root.append(picker(s));}
 function choose(){const s=info();picking={chosen:s.selects.slice(),round:s.round};paint();}
 function picker(s){const ov=el('div','bb-overlay'),w=el('div','bb-win');ov.append(w);w.append(el('h3','',T('ACTIVITY_BLIND_BOX_TITLE')||'Blind Box Frenzy'));
  [2,3,4,5].forEach((t,i)=>{const need=data.select_num[i];const sec=el('div','bb-tier');const have=()=>s.pool[t].filter(id=>picking.chosen.includes(id)).length;
   sec.append(el('b','',(T('ACTIVITY_BLIND_BOX_TEXT04')||'Please select {2} reward(s) for tier {1}').replace('{1}',t-1).replace('{2}',need)));const list=el('div','bb-pool');
   for(const id of s.pool[t]){const c=btn('bb-choice'+(picking.chosen.includes(id)?' on':''),'',()=>{if(picking.chosen.includes(id))picking.chosen=picking.chosen.filter(x=>x!==id);else{if(have()>=need)return;picking.chosen.push(id);}paint();});c.append(reward(id),el('small','','x'+row(id).num));list.append(c);}
   sec.append(list);w.append(sec);});
  w.append(el('p','bb-note',picking.chosen.length+'/8'),btn('bb-open',"Confirm",async()=>{const r=await act({action:'select',ids:picking.chosen});if(r)picking=null;paint();},picking.chosen.length!==8),btn('bb-open cancel',"Cancel",()=>{picking=null;paint();}));return ov;}
 async function open(n){const s=info();if(!s.locked&&!(await GirlUI.confirm(T('ACTIVITY_BLIND_BOX_TEXT07')||'Mở hộp ngay?',{title:'Xác Nhận Mở Hộp',ok:'Mở'})))return;const r=await act({action:'open',num:n});last=r;paint();if(r?.grand&&typeof GirlUI!=='undefined')GirlUI.toast("Round jackpot!");}
 return {render,has:id=>id===338};
})();
