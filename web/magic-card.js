'use strict';
// Magic Card (activity 134; captures 2026-09-29-fb/53, 112) inside the Events hub, laid out from ice_secret_content.prefab on
// its 693x997 canvas (x centred, y up from the top edge at 484): stage background, logo, the magician (skin 7085, Spine),
// Ultimate Reward pedestal, Magic Wand counter, "Round N", the 5x5 board (preview → Start → bunny cards / NEXT) and the
// Magician's Assistant missions tab. Rules: gxb2/magic_card.py. Prefix mc-.
const MagicCard=(()=>{
 let data=null,tab='card',host=null,busy=false,fresh=-1,spine=null;
 const A=n=>'/assets/magic-card/'+n+(n.endsWith('_bg1')?'.webp':'.png');
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 const T=(k,...a)=>{let s=data?.text?.[k]||'';a.forEach((v,i)=>{s=s.replace('{'+(i+1)+'}',v);});return s;};
 function at(e,x,y,w,h){e.style.left=`calc(${346.5+x-w/2} * var(--u))`;e.style.top=`calc(${484-y-h/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;e.style.height=`calc(${h} * var(--u))`;return e;}
 function iconSrc(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';if(id==='180')return A('icon_180');const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}return it&&itemIcons.has(it.icon)?'/assets/item-icons/'+it.icon+'.png':'';}
 function item(awardId,cls='mc-item'){const [k,n]=String(data.awards[awardId]?.award||'').split('#');const w=el('span',cls);const s=iconSrc(k);if(s)w.append(img(s));w.append(el('b','',number(Number(n))));w.title=itemCatalog?.[k]?.name||k;return w;}
 async function act(req){if(busy)return null;busy=true;try{const r=await api('/api/magic-card/action',req);state=r.state;return r;}catch(e){GirlUI.toast(e.message);return null;}finally{busy=false;if(host?.isConnected)draw();}}
 async function render(parent){host=parent;if(!data)data=await api('/assets/magic-card.json');draw();}
 function draw(){const s=state.magic_card_info;if(!s||!host)return;let root=host.querySelector('.mc-root');if(!root){root=el('div','mc-root');host.append(root);}
  root.querySelector('.mc-tabs')?.remove();root.querySelector('.mc-mission')?.remove();
  const tabs=el('div','mc-tabs');for(const [k,label,ic]of [['card','Magic Card','activity_ice_secret'],['mission',"Magician's Assistant",'activity_ice_secret_mission']]){const b=btn('mc-tab'+(tab===k?' on':''),'',()=>{tab=k;draw();});b.append(img(A(ic)),el('small','',label));tabs.append(b);}
  root.prepend(tabs);let stage=root.querySelector('.mc-stage');
  if(tab==='mission'){spine?.destroy?.();spine=null;stage?.remove();assistant(root,s);return;}
  if(!stage){stage=el('div','mc-stage');root.append(stage);}
  stage.querySelectorAll(':scope>:not(.mc-girl)').forEach(e=>e.remove());board(stage,s);}
 function board(st,s){st.style.backgroundImage=`url('${A('ice_secret_bg')}')`;
  if(!st.querySelector('.mc-girl')){const g=el('div','mc-girl');st.append(g);if(typeof GxbSpine!=='undefined')GxbSpine.mount(g,'/assets/lihui/zhanghe_pifu03_lihui01',{width:720,height:1280,scale:1,origin:[.5,(640+550)/1280],className:'mc-girl-canvas'}).then(v=>{spine=v;}).catch(()=>{g.append(img('/assets/skins/cards/7085.webp','mc-girl-card'));});}
  const logo=img(A('ice_secret_logo_en_en'),'mc-abs mc-logo');logo.style.left='calc(290 * var(--u))';logo.style.top='calc(4 * var(--u))';logo.style.width='calc(394 * var(--u))';st.append(logo);
  st.append(at(btn('mc-abs mc-help','',()=>CampaignUI.popup(T('ACTIVITY_ICE_SECRET_GAME_HELP').split('|').join('\n'),{})),-309,448,53,52));
  st.append(at(btn('mc-abs mc-detail','',()=>preview(s)),-310,386,53,52));
  // Ultimate Reward pedestal
  st.append(at(img(A('ice_secret_bk_qpk_2'),'mc-abs'),182,304,178,164));
  if(s.select){const it=item(s.select,'mc-abs mc-item mc-final'+(s.got_big?' got':''));at(it,182,319,96,96);st.append(it);if(!(s.status===1&&s.got_big)&&s.status===0){const ch=at(btn('mc-abs mc-change','',()=>choose(s)),217,354,41,44);ch.append(img(A('ice_secret_qiehuan_bg')));st.append(ch);}}
  else{const c=at(btn('mc-abs mc-choose','',()=>choose(s),s.status!==0),181,318,88,88);c.append(img(A('ice_secret__select_btn')));st.append(c);}
  const rib=at(el('div','mc-abs mc-ribbon',T('ACTIVITY_ICE_SECRET_MAXAWARD_TEXT')||'Ultimate Reward'),182,249,150,45);st.append(rib);
  // board area
  st.append(at(img(A('ice_secret_bg_1'),'mc-abs'),0,-90,693,631));
  const cost=at(el('div','mc-abs mc-cost'),-254,224,186,36);cost.append(img(A('icon_180'),'mc-wand'),el('b','',number(s.wands)+'/'+s.cost));st.append(cost);
  st.append(at(el('div','mc-abs mc-round',T('ACTIVITY_ICE_SECRET_ROUNDS',s.round)),0,222,200,30));
  s.board.forEach((c,i)=>{const r=Math.floor(i/5),col=i%5;const cell=at(el('button','mc-abs mc-cell'),-230+col*115,140-r*115,112,112);cell.type='button';
   if(s.status===0){if(i===12&&!s.select){cell.append(img(A('ice_secret__select_btn'),'mc-plus'));cell.onclick=()=>choose(s);}else if(c.award)cell.append(item(c.award));cell.classList.add('preview');}
   else if(c.next){cell.classList.add('next');cell.append(img(A('ice_secret_bk_3'),'mc-back'));cell.onclick=()=>act({action:'next'}).then(r=>{if(r)GirlUI.toast(T('ACTIVITY_ICE_SECRET_ROUNDS',s.round+1));});}
   else if(c.open){cell.classList.add('open');if(i===fresh){const it=item(c.award);it.classList.add('mc-reveal');cell.append(it);}}
   else{cell.append(img(A('ice_secret_bk_1'),'mc-back'));cell.onclick=()=>flip(i,s);}
   st.append(cell);});
  if(s.status===0){st.append(at(img(A('ice_secret_start_bg'),'mc-abs'),0,-300,693,213));const b=at(btn('mc-abs mc-start',T('ACTIVITY_ICE_SECRET_START')||'Start',async()=>{const r=await act({action:'start'});if(r)GirlUI.toast(T('ACTIVITY_ICE_SECRET_PARTNER_TEXT'+(1+Math.floor(Math.random()*3))));}),0,-320,246,70);st.append(b);}}
 async function flip(pos,s){if(s.wands<s.cost){GirlUI.toast('Không đủ Đũa Phép');return;}
  if(s.got_big&&!await GirlUI.confirm('Bạn đã nhận phần thưởng lớn. Tiếp tục lật thẻ của lượt này?',{title:'Xác Nhận Lật Thẻ',ok:'Tiếp Tục'}))return;
  const cell=host.querySelectorAll('.mc-cell')[pos];cell?.classList.add('flipping');await new Promise(r=>setTimeout(r,260));
  const r=await act({action:'flip',pos});if(!r)return;fresh=pos;draw();
  const [k,n]=Object.entries(r.got)[0]||[];GirlUI.toast((r.big?'★ Ultimate Reward! ':'')+number(n||0)+' '+(itemCatalog?.[k]?.name||k));
  if(r.big){const st=host.querySelector('.mc-stage');st?.classList.add('shake');setTimeout(()=>st?.classList.remove('shake'),450);}}
 function choose(s){if(s.status!==0)return;const {body,close}=GirlUI.win({title:T('ACTIVITY_ICE_SECRET_MAXAWARD_WINDOW')||'Set Ultimate Reward',cls:'mc-win'});
  const rows=Object.values(data.awards).filter(r=>r.type===1).sort((a,b)=>a.level-b.level||a.id-b.id);const used=state.magic_card_info.bigs;
  const grid=el('div','mc-choose-grid');for(const r of rows){const ok=used.includes(r.id),locked=r.level>s.round;const c=btn('mc-opt'+(r.id===s.select?' on':'')+(ok?'':' off'),'',async()=>{if(!ok){GirlUI.toast(locked?T('ACTIVITY_ICE_SECRET_MAXAWARD_TIP',r.level):'Ya usada');return;}close();await act({action:'select',id:r.id});});
   c.append(item(r.id),el('small','',locked?T('ACTIVITY_ICE_SECRET_MAXAWARD_TIP',r.level):'×'+r.limit));grid.append(c);}body.append(grid);}
 function preview(s){const {body}=GirlUI.win({title:T('ACTIVITY_ICE_SECRET_GAME_TITLE')||'Preview',cls:'mc-win'});const grid=el('div','mc-choose-grid');
  const counts={};for(const r of Object.values(data.awards).filter(r=>r.type===0))counts[r.award]=(counts[r.award]||0)+1;
  for(const r of Object.values(data.awards).filter(r=>r.type===0)){if(counts[r.award]<0)continue;const c=el('div','mc-opt');c.append(item(r.id),el('small','','×'+counts[r.award]));counts[r.award]=-1;grid.append(c);}
  body.append(el('p','mc-note',T('ACTIVITY_ICE_SECRET_ITEM_TIPS')),grid);}
 function assistant(root,s){const box=el('div','mc-mission');const head=el('div','mc-mhead');head.append(img(A('activity_ice_secret_mission'),'mc-micon'),el('b','',"Magician's Assistant"));box.append(head);
  const wand=el('div','mc-cost static');wand.append(img(A('icon_180'),'mc-wand'),el('b','',number(s.wands)));box.append(wand);
  for(const [weekly,label]of [[false,T('ACTIVITY_ICE_SECRET_MISSION_DAILY')||'Daily'],[true,T('ACTIVITY_ICE_SECRET_MISSION_WEEKLY')||'Weekly']]){box.append(el('h4','mc-sub',label));
   for(const m of s.missions.filter(x=>x.weekly===weekly)){const row=el('div','mc-mrow'+(m.claimed?' done':''));const info=el('div','mc-minfo');info.append(el('b','',data.mission_text[m.id]||''));
    const bar=el('div','mc-bar');const f=el('i');f.style.width=Math.min(100,m.have/m.need*100)+'%';bar.append(f,el('span','',Math.min(m.have,m.need)+'/'+m.need));info.append(bar);
    const [k,n]=m.award.split('#');const aw=el('span','mc-item small');aw.append(img(iconSrc(k)),el('b','',n));
    row.append(info,aw,btn('gs-btn'+(m.claimed?' white':''),m.claimed?'Claimed':'Claim',async()=>{const r=await act({action:'mission',id:m.id});if(r)GirlUI.toast('+'+n+' Magic Wand');},m.claimed||m.have<m.need));box.append(row);}}
  root.append(box);}
 return {render};
})();
