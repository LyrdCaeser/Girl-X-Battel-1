'use strict';
// Character Challenge (HeroChallengeWindow → fort detail → formation / HeroChallengeFightAwardWindow). Rules:
// gxb2/hero_challenge.py. Original art: btn_h_challenge_N (forts), hero_challenge_N, blessing_icon_N, pet avatars.
const HeroChallenge=(()=>{
 let origin='league',fort=0,panel=null,note='',busyLocal=false,team=[],pet=0,stage=0,skipReplay=false,timer=null;
 const A=n=>'/assets/hero-challenge/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const btn=(cls,text,fn)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
 try{skipReplay=localStorage.getItem('gxb2.heroChallenge.skip')==='1';}catch{}
 function root(){let r=$('hero-challenge-view');if(!r){r=el('section','hero-challenge-view');r.id='hero-challenge-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from){origin=from||view;fort=0;panel=null;note='';showView('hero-challenge');act({action:'open'});}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const row=itemCatalog?.[id];return (row&&itemPicture(row))||(row?.icon?'/assets/shops/items/'+row.icon+'.png':'');}
 function nameOf(id){id=String(id);return id==='1'?'Vàng':id==='2'?'Kim Cương':itemCatalog?.[id]?.name||'Vật phẩm '+id;}
 function chip(k,n){const c=el('span','hc-chip');const s=icon(k);if(s)c.append(img(s));c.append(el('b','',number(n)));c.title=nameOf(k);return c;}
 async function act(req){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/hero-challenge/action',req);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;if(view==='hero-challenge')render();}}
 let loadedAt=performance.now();
 function clock(at){const s=Math.max(0,at-(state.server_time||0)-Math.floor((performance.now()-loadedAt)/1000));return [Math.floor(s/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');}
 const face=(g,size)=>typeof portrait==='function'?portrait(g.show_id,size):el('span');
 function top(st,info){const bar=el('div','hc-top');const c=el('div','hc-res');c.append(img(A('icon_55')),el('b','',`${info.coupons}/${info.cap}`));if(info.next_coupon)c.append(el('small','hc-clock',clock(info.next_coupon)));c.title="Phiếu Thử Thách: hồi 1 phiếu mỗi 30 phút, tối đa 10 phiếu";bar.append(c);
  bar.append(btn('hc-help','?',()=>{
    const {body}=GirlUI.win({title:'Hướng Dẫn Thử Thách Nhân Vật',cls:'hc-help-modal'});
    const parts=String(info.help||'').split('|').map(t=>t.trim()).filter(Boolean);
    const list=document.createElement('div');list.className='hc-help-body';
    for(const part of parts){const line=document.createElement('p');line.textContent=part;list.append(line);}
    body.append(list);
  }));
  const back=btn('hc-back','',()=>{if(fort){fort=0;panel=null;render();}else showView(origin==='hero-challenge'?'league':origin);});back.append(img('/assets/ui/win_back_btn.png'));bar.append(back);st.append(bar);}
 function render(){const r=root();if(view!=='hero-challenge'){clearInterval(timer);timer=null;return;}loadedAt=performance.now();const info=state.hero_challenge_info;r.replaceChildren();const st=el('div','hc-stage');r.append(st);
  if(!info){st.append(el('p','hc-note',"Đang tải…"));return;}
  top(st,info);
  if(!info.unlocked){st.append(el('p','hc-note hc-box',`Thử Thách Nhân Vật mở khi vượt ải ${info.unlock_stage}.`));return;}
  if(fort)detail(st,info,info.forts.find(f=>f.fort===fort));else list(st,info);
  if(note)st.append(el('p','hc-note hc-err',note));
  if(panel)popup(st,info,info.forts.find(f=>f.fort===fort));
  else{const f=fort&&info.forts.find(x=>x.fort===fort);if(f?.pending?.length){panel='pick';popup(st,info,f);}}
  clearInterval(timer);timer=setInterval(()=>{const c=root().querySelector('.hc-clock');if(!c||view!=='hero-challenge'){clearInterval(timer);return;}c.textContent=clock(info.next_coupon);},1000);}
 function list(st,info){const w=el('div','hc-list');w.append(el('h1','hc-logo-vi','Thử Thách Nhân Vật'));
  for(const f of info.forts){const b=btn('hc-fort','',()=>{fort=f.fort;panel=null;render();});b.append(img(A(f.img||('btn_h_challenge_'+f.fort)),'hc-fort-bg'));
   const t=el('div','hc-fort-text');t.append(el('b','',f.name),el('span','',`${f.done}/${f.total}`+(f.puzzle?' · Giải Đố':'')));b.append(t);if(f.current===-1)b.classList.add('done');w.append(b);}
  st.append(w);}
 function detail(st,info,f){const w=el('div','hc-detail');
  const head=el('div','hc-head');head.append(img(A(f.img||('btn_h_challenge_'+f.fort)),'hc-head-bg'),el('b','hc-head-name',f.name+(f.puzzle?' · Giải Đố':'')));w.append(head);
  // Team of this run: live / fallen Girls, Blessings and Servants won.
  const box=el('div','hc-run');const girls=el('div','hc-girls');for(const g of f.live){const c=el('div','hc-girl');c.append(face(g,64),el('small','',`Cấp ${g.lv}`));c.title=g.name;girls.append(c);}
  for(const g of f.dead){const c=el('div','hc-girl dead');c.append(face(g,64),el('small','','✝'));c.title=g.name+" (đã bị loại)";girls.append(c);}box.append(girls);
  const extras=el('div','hc-extras');for(const b of f.buffs){const i=info.buff_info[b];const c=el('span','hc-buff');c.append(img(A(i.icon)));c.title=`${i.name}: ${i.desc}`;extras.append(c);}
  for(const p of f.pets){const i=info.pet_info[p];const c=el('span','hc-pet');c.append(img('/assets/servant/'+i.avatar+'.png'));c.title=i.name;extras.append(c);}
  if(!f.puzzle)extras.append(btn('hc-small alt','Đặt Lại',async()=>{if(await GirlUI.confirm("Đặt lại thử thách? Tiến độ và phần thưởng tạm thời của lượt này sẽ mất. Tiêu hao 1 Phiếu Thử Thách.",{title:"Đặt Lại Thử Thách",ok:"Đặt Lại",danger:true}))await act({action:'reset',fort:f.fort});}));
  box.append(extras);w.append(box);
  const rows=el('div','hc-rows');f.stages.forEach((s,i)=>{const passed=f.current===-1||s.id<f.current,cur=s.id===f.current;const row=el('div','hc-row'+(passed?' passed':cur?' current':' locked'));
   row.append(el('b','hc-num',String(i+1)));const txt=el('div','hc-txt');txt.append(el('b','',s.name),el('small','',s.desc));row.append(txt);
   const rw=el('div','hc-rw');if(s.first)for(const [k,n]of Object.entries(s.reward1))rw.append(chip(k,n));if(s.reward2)rw.append(el('span','hc-pick','🎁 '+String(s.reward2).split('|').map(p=>{const [k,n]=p.split('#');return n+'× '+({1:"Nữ Thần",2:"Hiệu ứng",3:"Linh Thú"})[k];}).join(' + ')));row.append(rw);
   const go=btn('hc-go',passed?'Đánh Lại':'Chiến Đấu',()=>openFight(f,s.id));go.disabled=!passed&&!cur;row.append(go);rows.append(row);});
  w.append(rows);st.append(w);}
 function openFight(f,sid){stage=sid;const pool=f.puzzle?f.live:f.live;const keep=(f.team||[]).filter(t=>pool.some(g=>g.uid===t.uid));team=keep.map(t=>({...t}));for(const g of pool){if(team.length>=6)break;if(team.some(t=>t.uid===g.uid))continue;const free=[1,2,3,4,5,6].find(p=>!team.some(t=>t.pos===p));team.push({uid:g.uid,pos:free});}pet=f.pets.includes(f.pet)?f.pet:0;panel='fight';render();}
 async function fight(f){if(!team.length){note="Hãy chọn ít nhất một Nữ Thần";render();return;}panel=null;const r=await act({action:'fight',fort:f.fort,stage,team,pet});if(!r)return;const got={...(r.got||{})};const label=`${f.name} · ${f.stages.findIndex(s=>s.id===stage)+1}`;
  if(!skipReplay&&r.report&&typeof watchEventBattle==='function')await watchEventBattle({report:r.report,rewards:got},'hero-challenge',label);else CampaignUI.result(r.win,got,{event:true,label,report:r.report});
  if(r.replay)note="Đánh lại: không nhận phần thưởng và không mất tài nguyên.";else if(!r.win)note=f.puzzle?"Thất bại: trừ 1 Phiếu Thử Thách.":"Thất bại: trừ 1 Phiếu Thử Thách; Nữ Thần tham gia bị loại khỏi lượt này.";render();}
 function popup(st,info,f){const ov=el('div','hc-overlay');const w=el('div','hc-win');ov.append(w);const close=btn('hc-close','✕',()=>{panel=null;render();});
  if(panel==='pick'&&f?.pending?.length){const p=f.pending[0];w.append(el('h2','','Hãy chọn phần thưởng'));const g=el('div','hc-options');
   p.options.forEach((id,i)=>{const c=btn('hc-option','',async()=>{panel=null;await act({action:'pick',fort:f.fort,index:i});});
    if(p.kind===1){const m=p.girls[i];c.append(face(m,96),el('b','',m.name),el('small','',`Cấp ${m.lv}`));}
    else if(p.kind===2){const b=info.buff_info[id];c.append(img(A(b.icon)),el('b','',b.name),el('small','',b.desc));}
    else{const s=info.pet_info[id];c.append(img('/assets/servant/'+s.avatar+'.png'),el('b','',s.name),el('small','','Linh Thú cấp 90'));}g.append(c);});
   w.append(g);ov.onclick=null;st.append(ov);return;}
  if(panel==='fight'){w.append(el('h2','','Chiến Đấu'),close);const pool=f.live;const byUid=new Map(pool.map(g=>[g.uid,g]));
   const sk=btn('hc-skip'+(skipReplay?' on':''),'',()=>{skipReplay=!skipReplay;try{localStorage.setItem('gxb2.heroChallenge.skip',skipReplay?'1':'0');}catch{};render();});sk.append(el('i','',skipReplay?'✓':''),el('span','','Bỏ qua'));w.append(sk);
   const grid=el('div','hc-formation');for(const [label,poss]of [['Hàng trước',[1,2]],['Hàng sau',[3,4,5,6]]]){const line=el('div','hc-line');line.append(el('b','hc-line-name '+label.toLowerCase(),label));for(const p of poss){const t=team.find(x=>x.pos===p);const slot=btn('hc-slot','',()=>{if(t){team=team.filter(x=>x!==t);render();}});if(t&&byUid.get(t.uid)){slot.append(face(byUid.get(t.uid),72));}line.append(slot);}grid.append(line);}w.append(grid);
   const poolEl=el('div','hc-pool');for(const g of pool){const used=team.some(t=>t.uid===g.uid);const c=btn('hc-cand'+(used?' on':''),'',()=>{if(used)team=team.filter(t=>t.uid!==g.uid);else{const free=[1,2,3,4,5,6].find(p=>!team.some(t=>t.pos===p));if(free)team.push({uid:g.uid,pos:free});}render();});c.append(face(g,60),el('small','',g.name));poolEl.append(c);}w.append(poolEl);
   if(f.pets.length){const pets=el('div','hc-pets');pets.append(el('span','','Linh Thú:'));for(const id of [0,...f.pets]){const b=btn('hc-petbtn'+(pet===id?' on':''),'',()=>{pet=id;render();});if(id){const s=info.pet_info[id];b.append(img('/assets/servant/'+s.avatar+'.png'));b.title=s.name;}else b.textContent='—';pets.append(b);}w.append(pets);}
   if(f.buffs.length){const bl=el('p','hc-bless','Hiệu ứng: '+f.buffs.map(b=>info.buff_info[b].name).join(', '));w.append(bl);}
   w.append(btn('hc-fight','Chiến Đấu',()=>fight(f)));}
  ov.onclick=e=>{if(e.target===ov){panel=null;render();}};st.append(ov);}
 return {open,render};
})();
