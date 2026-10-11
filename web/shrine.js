'use strict';
// Tsuruga Grand Shrine (ShrineHurdleEntranceWindow → ShrineHurdleChooseWayWindow / ChooseLevelWindow → ShrineHurdleWindow
// with ChooseBuff / Shop / SelectPartner; ShrineHurdleNoticeWindow; ShrineHurdleShopWindow; StoryWindow). Rules:
// gxb2/shrine.py. Layout from docs/references/2026-09-29-g (04 story, 05 entrance, 06 Reward Stage, 07 Battle Stage).
const Shrine=(()=>{
 let origin='league',panel='hub',note='',busyLocal=false,skipReplay=false,timer=null;
 let sel=null,pick=[],route=null,diff=1,tab=0,story=null,storyAuto=false,storyTimer=null,result=null,modal=null;
 const A=n=>'/assets/shrine/'+n;
 const TYPE_NAME={1:'Battle Stage',2:'Reward Stage',3:'Store Stage',4:'Recover Stage',5:'Boss Stage'};
 const TYPE_SPINE={1:'shrine_zhandou',2:'shrine_jiangli',3:'shrine_shangdian',4:'shrine_huifu',5:'shrine_zhandou'};
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const btn=(cls,text,fn)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
 try{skipReplay=localStorage.getItem('gxb2.shrine.skip')==='1';}catch{}
 function root(){let r=$('shrine-view');if(!r){r=el('section','shrine-view');r.id='shrine-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from){origin=from||view;note='';result=null;modal=null;const info=state.shrine_info;panel=info?.run?'run':'hub';showView('shrine');
  act({action:'open'}).then(()=>{const i=state.shrine_info;if(i?.unlocked&&!i.prologue_seen)playStory(1,1000);});}
 const SHRINE_ITEMS=['322','323','324','325','326','331','332','374'];
 function icon(id){id=String(id);if(SHRINE_ITEMS.includes(id))return A('icon_'+id+'.png');if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const row=itemCatalog?.[id];return (row&&itemPicture(row))||(row?.icon?'/assets/shops/items/'+row.icon+'.png':'');}
 function chip(k,n,cls='ts-chip'){const c=el('span',cls);const s=icon(k);if(s)c.append(img(s));c.append(el('b','',typeof n==='string'?n:number(n)));return c;}
 function tile(k,n){const t=el('span','ts-tile');const s=icon(k);if(s)t.append(img(s));t.append(el('b','',number(n)));t.title=itemCatalog?.[k]?.name||'';return t;}
 async function act(req){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/shrine/action',req);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;if(view==='shrine')render();}}
 let loadedAt=performance.now();const left=at=>{const s=Math.max(0,at-(state.server_time||0)-Math.floor((performance.now()-loadedAt)/1000));const d=Math.floor(s/86400),h=Math.floor(s%86400/3600),m=Math.floor(s%3600/60);return d?`${d}D ${h}H`:`${h}H ${m}M`;};
 const chibis=new Map();
 function chibi(tableId){const key=String(tableId);if(chibis.has(key))return chibis.get(key).cloneNode(true);const h=el('div','ts-chibi');api('/assets/chibis/catalog.json').then(c=>{const m=c[key];if(m)GxbSpine.snapshot(h,'/assets/chibis/'+m.model,{width:320,height:320,fit:.85,y:.62,className:'ts-chibi-img',sequence:[['idle',true]]}).then(()=>{const im=h.querySelector('img');if(im)chibis.set(key,im.cloneNode(true));});}).catch(()=>{});return h;}
 const typeIcons=new Map();
 function typeIcon(t){const key=TYPE_SPINE[t];if(typeIcons.has(key))return typeIcons.get(key).cloneNode(true);const h=el('div','ts-typeicon');GxbSpine.snapshot(h,'/assets/spine/'+key,{width:320,height:320,fit:.95,y:.5,className:'ts-typeicon-img',sequence:[['texiao01',true]]}).then(()=>{const im=h.querySelector('img');if(im)typeIcons.set(key,im.cloneNode(true));}).catch(()=>{});return h;}
 function top(st,{title,back,chips=[]}){const bar=el('div','ts-top');const b=btn('ts-back','',back);b.append(img('/assets/ui/win_back_btn.png'));const mid=el('div','ts-topchips');chips.forEach(c=>mid.append(c));bar.append(mid,b);st.append(bar);if(title)st.append(el('h2','ts-title',title));}
 function render(){const r=root();if(view!=='shrine'){clearInterval(timer);timer=null;clearTimeout(storyTimer);return;}loadedAt=performance.now();const info=state.shrine_info;r.replaceChildren();const st=el('div','ts-stage');r.append(st);
  if(!info){st.append(el('p','ts-note',"Loading…"));return;}
  if(!info.unlocked){top(st,{back:()=>showView(origin==='shrine'?'league':origin)});const box=el('div','ts-note ts-box');box.append(el('b','','Tsuruga Grand Shrine'),el('p','',`Unlocks after clearing Tests floor ${info.open_floor} (current: ${info.tower_floor}) and owning at least one 10★ Girl${info.has_ten_star?' ✓':''}.`));st.append(box);return;}
  if(story){storyView(st);return;}
  if(panel==='run'&&info.run)runView(st,info);else if(panel==='trials'||panel==='run')trialsView(st,info);else if(panel==='board')boardView(st,info);else if(panel==='pond')pondView(st,info);else if(panel==='chimes')chimesView(st);else if(panel==='review')reviewView(st,info);else hubView(st,info);
  if(modal)modal(st,info);
  if(result)resultView(st);
  if(note)st.append(el('p','ts-err',note));
  clearInterval(timer);timer=setInterval(()=>{if(view!=='shrine'){clearInterval(timer);return;}root().querySelectorAll('[data-at]').forEach(e=>e.textContent=e.dataset.prefix+left(Number(e.dataset.at)));},30000);}
 // ShrineHurdleEntranceWindow (capture 05): Realm of Trials, Tree of Chimes, Message Board, Pond of Prayers.
 function hubView(st,info){st.classList.add('ts-hub');st.style.backgroundImage=`url('${A('shrine_main_bg.webp')}')`;
  const plus=btn('ts-plus','+',()=>{modal=buyModal;render();});const tk=chip('322',info.tickets);tk.append(plus);
  top(st,{back:()=>showView(origin==='shrine'?'league':origin),chips:[tk]});
  const side=el('div','ts-side');side.append(btn('ts-round','?',()=>{modal=helpModal;render();}));const rv=btn('ts-round ts-img','',()=>{panel='review';render();});rv.append(img(A('shrine_hurdle_img_1.png')));rv.title='Review';side.append(rv);st.append(side);
  const spot=(cls,label,bg,fn,sub)=>{const b=btn('ts-spot '+cls,'',fn);if(bg)b.append(img(A(bg),'ts-ribbon'));b.append(el('b','',label));if(sub)b.append(sub);st.append(b);};
  const t=el('small','ts-ends');t.dataset.at=info.fighting?info.fight_end:info.season_end;t.dataset.prefix=info.fighting?'Ends in ':'Starts in ';t.textContent=t.dataset.prefix+left(Number(t.dataset.at));
  spot('trials','Realm of Trials','',()=>{panel=info.run?'run':'trials';render();},t);
  spot('tree','Tree of Chimes','shrine_tree_bg.png',()=>{if(typeof Chimes!=='undefined'){Chimes.open('shrine');return;}panel='chimes';render();});
  spot('board','Message Board','broadcast_bg_en.png',()=>{panel='board';tab=0;render();});
  spot('pond','Pond of Prayers','shrine_wish_bg.png',()=>{panel='pond';tab=0;render();});
  if(info.last_reward&&Object.keys(info.last_reward).length&&!hubView.shown){hubView.shown=true;setTimeout(()=>CampaignUI.popup("Season rewards",info.last_reward),50);}}
 function buyModal(st,info){const w=overlay(st,'Trial Invitation');w.append(el('p','',`Buy Trial Invitations for ${info.ticket_cost} Gems each. Remaining: ${info.ticket_buys_left} purchases this season.`));
  const b=btn('ts-go',"Buy 1",async()=>{modal=null;await act({action:'buy_ticket',count:1});});b.disabled=info.ticket_buys_left<1;b.append(chip('2',info.ticket_cost));w.append(b);}
 function helpModal(st,info){const w=overlay(st,'Tsuruga Grand Shrine');w.append(el('div','ts-help',String(info.help||'').replaceAll('|','\n')));}
 function overlay(st,title,cls=''){const ov=el('div','ts-overlay');ov.onclick=e=>{if(e.target===ov){modal=null;render();}};const w=el('div','ts-win '+cls);w.append(el('h3','',title),btn('ts-close','✕',()=>{modal=null;render();}));ov.append(w);st.append(ov);return w;}
 // StoryWindow (capture 04): background, picture, name tag, dialog; Auto / Recall / skip.
 async function playStory(textId,plotId){try{const r=await api('/api/shrine/story',{text_id:textId});story={lines:r.lines,i:0,plot:plotId,log:false};storyAuto=false;render();}catch(e){note=e.message;render();}}
 function storyEnd(){const pid=story?.plot;story=null;clearTimeout(storyTimer);if(pid)act({action:'plot',plot:pid});else render();}
 function storyView(st){const s=story;const line=s.lines[s.i];if(!line){storyEnd();return;}st.classList.add('ts-story');
  const bg=line.bg&&line.bg!=='battle_map_shenxi'?A(line.bg+'.webp'):A('shrine_main_bg.webp');st.style.backgroundImage=`url('${bg}')`;
  if(line.pic){const p=img(A('pic_'+line.pic+'.webp'),'ts-pic');p.onerror=()=>p.remove();st.append(p);}
  st.append(btn('ts-skip','⏭',storyEnd));
  const box=el('div','ts-dialog');if(line.name&&line.name!=='*')box.append(el('b','ts-name',line.name));else if(line.name==='*')box.append(el('b','ts-name',state.profile?.name||'Senpai'));
  box.append(el('p','',line.text||''),el('i','ts-more','▼'));box.onclick=()=>{s.i++;render();};
  const ctl=el('div','ts-storybtns');ctl.append(btn('ts-pill'+(storyAuto?' on':''),'Auto',e=>{e.stopPropagation();storyAuto=!storyAuto;render();}),btn('ts-pill','Recall',e=>{e.stopPropagation();s.log=!s.log;render();}));
  st.append(ctl,box);
  if(s.log){const w=overlay(st,'Recall');w.querySelector('.ts-close').onclick=()=>{s.log=false;render();};const list=el('div','ts-log');for(const l of s.lines.slice(0,s.i+1))list.append(el('p','',(l.name?(l.name==='*'?'Senpai':l.name)+': ':'')+l.text));w.append(list);}
  clearTimeout(storyTimer);if(storyAuto&&!s.log)storyTimer=setTimeout(()=>{if(story===s){s.i++;render();}},Math.max(1800,(line.text||'').length*55));}
 function reviewView(st,info){st.style.backgroundImage=`url('${A('shrine_main_bg.webp')}')`;top(st,{title:'Review',back:()=>{panel='hub';render();}});
  const list=el('div','ts-list');let tabName='';for(const c of info.chapters){if(c.tab!==tabName){tabName=c.tab;list.append(el('h4','ts-sub',tabName.replace('\n',' ')));}
   const b=btn('ts-row ts-chapter'+(c.open?'':' locked'),'',()=>{if(c.open)playStory(c.text_id,null);});b.append(el('b','',c.title),el('small','',c.open?'▶':"🔒 complete more trials"));list.append(b);}st.append(list);}
 // ShrineHurdleChooseWayWindow + ChooseLevelWindow: 3 Trials with their environments, highest score and difficulty.
 // shrine_hurdle_choose_way_window: three way_item panels (654×322, shrine_hurdle_select_way_bg1) at y 335 / 0 / -335, each with its
 // title, the three 196×110 boxes (shrine_hurdle_select_way_bg2) Environment (two environment icons; tap = its rule) · Highest
 // Score · Difficulty Level, and the Enter button (blue_btn_65_65 with the ticket icon_322).
 function trialsView(st,info){st.style.backgroundImage=`url('${A('shrine_hurdle_main_bg.webp')}')`;top(st,{title:'',back:()=>{panel='hub';render();},chips:[chip('322',info.tickets)]});
  const P=(e,x,y,w,h)=>{e.style.cssText+=`;position:absolute;left:calc(${360+x-w/2} * var(--tu));top:calc(${640-y-h/2} * var(--tu));width:calc(${w} * var(--tu));height:calc(${h} * var(--tu))`;return e;};
  const wrap=el('div','ts-ways');st.append(wrap);let tip=null;
  info.routes.forEach((r,i)=>{const y=[335,0,-335][i]-40;const c=P(el('div','ts-way'),0,y,654,322);c.style.backgroundImage=`url('/assets/sprite/shrine_hurdle_select_way_bg1.png')`;
   c.append(el('h4','ts-way-title',r.name));
   const box=(x,label)=>{const b=el('div','ts-way-box');b.style.cssText=`left:calc(${327+x-98} * var(--tu));top:calc(${161-15-55} * var(--tu));width:calc(196 * var(--tu));height:calc(110 * var(--tu));background-image:url('/assets/sprite/shrine_hurdle_select_way_bg2.png')`;b.append(el('small','',label));c.append(b);return b;};
   const env=box(-205,'Environment');const icons=el('div','ts-way-env');for(const e of r.env){const ib=btn('ts-way-icon','',ev=>{ev.stopPropagation();tip?.remove();tip=el('div','ts-way-tip');const ic=img('/assets/sprite/'+(e.icon||'environment_510001')+'.png');const tx=el('div');tx.append(el('b','',e.title||''),el('p','',e.desc||''));tip.append(ic,tx);tip.onclick=()=>{tip.remove();tip=null;};c.append(tip);});ib.append(img('/assets/sprite/'+(e.icon||'environment_510001')+'.png'));ib.title=e.title||'';icons.append(ib);}env.append(icons);
   box(0,'Highest Score').append(el('b','',number(r.best)));box(205,'Difficulty Level').append(el('b','',String(r.max_diff)));
   const go=btn('ts-way-go','',()=>{route=r.id;diff=r.suggest;modal=levelModal;render();});go.style.backgroundImage=`url('/assets/sprite/blue_btn_65_65.png')`;go.append(img(icon('322')),el('span','','Enter'));go.disabled=!info.fighting||info.tickets<1;c.append(go);wrap.append(c);});
  if(!info.fighting)st.append(el('p','ts-note ts-way-note',`Observing… ${left(info.season_end)}`));}
 function lantern(n,cls='ts-lantern'){const l=el('div',cls);l.append(img(A('shrine_icon1.png'),'ts-lamp'));const d=el('span','ts-digits');for(const ch of String(n))d.append(img(A(`shrine_num_${ch}.png`)));l.append(d);return l;}
 function levelModal(st,info){const r=info.routes.find(x=>x.id===route);const w=overlay(st,'Difficulty Level','ts-levelwin');
  const row=el('div','ts-level');const set=v=>{diff=Math.max(1,Math.min(r.max_diff,v));render();};
  row.append(btn('ts-arrow','«',()=>set(diff-10)),btn('ts-arrow','‹',()=>set(diff-1)),lantern(diff),btn('ts-arrow','›',()=>set(diff+1)),btn('ts-arrow','»',()=>set(diff+10)));w.append(row);
  w.append(el('p','ts-hint',`Recommended Difficulty Level: ${r.suggest}`));
  w.append(btn('ts-go','Confirm',async()=>{if(diff>r.suggest&&!confirm('This Difficult Level could be too hard for you confirm to continue?'))return;
   if(!confirm('Confirm to consume 1 Invitation Card and enter the Trial? The Girls\' attribute and status in this Trial will not be updated by your adjustments in other features.'))return;
   modal=null;const res=await act({action:'start',route,diff});if(res){panel='run';sel=null;pick=[];render();}}));}
 // ShrineHurdleWindow (captures 06-07).
 function runView(st,info){const run=info.run;st.style.backgroundImage=`url('${A('shrine_hurdle_main_bg.webp')}')`;st.classList.add('ts-run');
  top(st,{back:()=>{panel='hub';render();},chips:[chip('324',run.gold)]});
  const head=el('div','ts-runhead');const icons=el('div','ts-icons');icons.append(btn('ts-round','?',()=>{modal=helpModal;render();}));
  const bl=btn('ts-round ts-img','',()=>{modal=buffsModal;render();});bl.append(img(A('shrine_hurdle_img_2.png')));bl.title='Buff Obtained';icons.append(bl);
  const hp=btn('ts-round','♥',()=>{modal=hpModal;render();});hp.title='HP Status';icons.append(hp);
  const pts=el('div','ts-points');pts.append(img(A('shrine_hurdle_entrace_bg_1.png'),'ts-sword'),el('span','',`Points: ${number(run.score)}`));
  head.append(icons,el('div','ts-runtitle',''),lantern(run.diff,'ts-lantern ts-lantern-top'));head.querySelector('.ts-runtitle').append(el('b','',run.name),el('span','',`${run.floor}/15`));head.append(pts);st.append(head);
  const main=el('div','ts-runmain');st.append(main);
  if(run.type==null)wayView(main,run);else if(run.type===1||run.type===5)battleView(main,run,info);else if(run.type===2)rewardView(main,run,info);else if(run.type===3)storeView(main,run,info);else if(run.type===4)recoverView(main,run,info);
  if(run.can_next&&run.type!==3){const n=btn('ts-next','',next);n.append(img(A('shrine_hurdle_next_img.png')),el('b','',run.floor>=15?'Results':'Next'));main.append(n);}
  const out=btn('ts-out','',async()=>{if(!confirm('Confirm to give up the Trial?'))return;const r=await act({action:'giveup_trial'});if(r?.end){result=r.end;panel='trials';render();}});out.append(img(A('shrine_hurdle_out_btn.png')));st.append(out);}
 async function next(){const r=await act({action:'next'});if(r?.end){result=r.end;panel='trials';render();}}
 function wayView(main,run){main.append(el('p','ts-prompt','Please select'));const row=el('div','ts-ways');run.types.forEach((t,i)=>{const b=btn('ts-way','',async()=>{const msg={1:'Confirm to enter Battle Stage?',2:'Confirm to enter Reward Stage?',3:'Confirm to enter Store Stage?',4:'Confirm to enter Recover Stage?'}[t];if(msg&&!confirm(msg))return;await act({action:'way',index:i});});
   b.append(img(A('shrine_hurdle_door'+(i+1)+'.png'),'ts-door'),typeIcon(t),el('b','',TYPE_NAME[t]));row.append(b);});main.append(row);}
 function battleView(main,run,info){const e=run.enemy||[];const boss=run.type===5;const box=el('div','ts-enemy'+(boss?' boss':''));if(e[0])box.append(chibi(e[0].table_id));
  const lv=el('div','ts-enemylist');for(const u of e){const s=el('span','ts-emini');if(typeof portrait==='function')s.append(portrait(u.table_id,44));s.append(el('small','',`Lv.${u.lv}`));lv.append(s);}box.append(lv);
  if(!run.can_next){const f=btn('ts-fight','',()=>{pick=pick.filter(p=>run.partners.find(x=>x.partner_id===p&&x.hp>0));if(!pick.length)pick=autoTeam(run);modal=teamModal;render();});f.append(img(A('shrine_hurdle_battle_en_en.png')));box.append(f);}
  box.append(el('p','ts-hint',boss?"Boss Stage: 1 attempt; more damage = more points.":`Battle Stage: 15 rondas · ${number(run.points||0)} points · 90 Trial Tokens`));main.append(box);}
 function roster(){return new Map((state.roster||[]).map(h=>[h.partner_id,h]));}
 function autoTeam(run){const by=roster();return run.partners.filter(p=>p.hp>0).sort((a,b)=>(by.get(b.partner_id)?.lv||0)-(by.get(a.partner_id)?.lv||0)).slice(0,6).map(p=>p.partner_id);}
 function hpBar(hp){const b=el('span','ts-hp');const f=el('i','');f.style.width=Math.max(0,Math.min(100,hp))+'%';if(hp<=30)f.classList.add('low');b.append(f);return b;}
 function girlCard(p,on,fn){const by=roster();const h=by.get(p.partner_id);const c=btn('ts-girl'+(on?' on':'')+(p.hp<=0?' dead':''),'',fn);if(h&&typeof portrait==='function')c.append(portrait(h.table_id,56));c.append(hpBar(p.hp),el('small','',p.hp<=0?'KO':`${p.hp}%`));c.title=h?.name||'';return c;}
 function teamModal(st,info){const run=info.run;const w=overlay(st,run.type===5?'Boss Stage':'Battle Stage','ts-teamwin');
  const slots=el('div','ts-slots');for(let i=0;i<6;i++){const pid=pick[i];const p=run.partners.find(x=>x.partner_id===pid);const s=btn('ts-slot','',()=>{if(pid){pick=pick.filter(x=>x!==pid);render();}});s.append(el('small','',i<2?'Front':'Back'));if(p)s.append(girlCard(p,false,()=>{pick=pick.filter(x=>x!==pid);render();}));slots.append(s);}w.append(slots);
  const pool=el('div','ts-pool');for(const p of [...run.partners].sort((a,b)=>b.hp-a.hp)){const on=pick.includes(p.partner_id);pool.append(girlCard(p,on,()=>{if(p.hp<=0)return;if(on)pick=pick.filter(x=>x!==p.partner_id);else if(pick.length<6)pick.push(p.partner_id);render();}));}w.append(pool);
  const acts=el('div','ts-acts');const sk=el('label','ts-skipcb');const cb=el('input');cb.type='checkbox';cb.checked=skipReplay;cb.onchange=()=>{skipReplay=cb.checked;try{localStorage.setItem('gxb2.shrine.skip',skipReplay?'1':'0');}catch{}};sk.append(cb,' Skip');
  acts.append(btn('ts-small','Auto',()=>{pick=autoTeam(run);render();}),sk,btn('ts-go','Fight',()=>fight(run)));w.append(acts);}
 async function fight(run){if(!pick.length){note="Choose at least one Girl";render();return;}modal=null;const boss=run.type===5;
  const r=await act({action:'fight',team:pick.map((p,i)=>({partner_id:p,pos:i+1}))});if(!r)return;const label=boss?`Boss · ${number(r.damage||0)} damage · +${number(r.points||0)} points`:(r.win?`Victory · +${number(r.points)} points · +${r.gold} Trial Tokens`:"Defeat: Girls do not recover HP");
  if(!skipReplay&&r.report&&typeof watchEventBattle==='function')await watchEventBattle({report:r.report,rewards:{}},'shrine',run.name);else CampaignUI.result(r.win||boss,{},{event:true,label,report:r.report});
  if(r.end){result=r.end;panel='trials';}else note=boss?'':label;render();}
 function buffCard(bid,info,lv,extra){const b=info.buff_info[bid];const c=el('div','ts-buff');c.append(img(A('shrine_hurdle_shop_card_bg.png'),'ts-cardbg'));const ic=img(A(b.image+'.png'),'ts-bicon');c.append(ic);
  c.append(el('b','ts-bname',b.name+(lv>1?` +${lv-1}`:'')),el('p','ts-bdesc',b.desc.replace('{1}',b.values[Math.max(0,Math.min(2,lv-1))])));if(extra)c.append(extra);return c;}
 function rewardView(main,run,info){main.append(el('p','ts-prompt',run.can_next?'Boost Obtained':'Please select'));const row=el('div','ts-buffs');
  if(!run.can_next){(run.extra.skills||[]).forEach((bid,i)=>{const c=buffCard(String(bid),info,1);if(sel===i)c.classList.add('on');c.onclick=()=>{sel=i;render();};row.append(c);});main.append(row);
   const acts=el('div','ts-rewardacts');const g=btn('ts-white','Give Up',async()=>{if(!confirm('Confirm to give up the buff and get Trial Tokens instead?'))return;sel=null;await act({action:'pick_buff'});});g.prepend(chip('324','+'+info.giveup_gold,'ts-chip ts-gain'));
   const s=btn('ts-go','Select',async()=>{if(sel==null){note='Please select';render();return;}const i=sel;sel=null;await act({action:'pick_buff',index:i});});acts.append(g,s);main.append(acts);}
  else{const owned=Object.keys(run.skills);const last=owned[owned.length-1];if(last)row.append(buffCard(last,info,run.skills[last]));main.append(row);}}
 function storeView(main,run,info){const tabs=el('div','ts-tabs');['Purchase','Upgrade'].forEach((t,i)=>tabs.append(btn('ts-tab'+(tab===i?' on':''),t,()=>{tab=i;render();})));main.append(tabs);
  const row=el('div','ts-buffs');if(tab===0){(run.extra.buys||[]).forEach((bid,i)=>{const bought=(run.extra.bought||[]).includes(i);const b=info.buff_info[bid];
    const buy=btn('ts-go ts-buy',bought?'Purchased':'',async()=>{await act({action:'store',mode:'buy',index:i});});if(!bought)buy.append(chip('324',b.cost));buy.disabled=bought||run.gold<b.cost;row.append(buffCard(String(bid),info,1,buy));});}
  else{if(!(run.extra.upgrades||[]).length)row.append(el('p','ts-note',"You have no buffs to upgrade yet."));(run.extra.upgrades||[]).forEach((bid,i)=>{const lv=run.skills[bid]||1;const b=info.buff_info[bid];const cost=b.up[Math.min(1,lv-1)];
    const up=btn('ts-go ts-buy',lv>=3?'Max':'',async()=>{await act({action:'store',mode:'up',index:i});});if(lv<3)up.append(chip('324',cost));up.disabled=lv>=3||run.gold<cost;row.append(buffCard(String(bid),info,lv,up));});}
  main.append(row);const n=btn('ts-next','',next);n.append(img(A('shrine_hurdle_next_img.png')),el('b','','Next'));main.append(n);}
 function recoverView(main,run,info){if(run.can_next){main.append(el('p','ts-prompt','Recovered'));return;}main.append(el('p','ts-prompt','Please select'));const row=el('div','ts-recover');
  for(const k of ['1','2','3']){const t=info.restore[k];const c=btn('ts-heal'+(sel===k?' on':''),'',()=>{sel=k;render();});c.append(img(A('shrine_hurdle_case_img'+k+'.png')),el('b','',t.name),el('p','',t.desc));row.append(c);}main.append(row);
  if(sel==='3'){const pool=el('div','ts-pool');for(const p of [...run.partners].sort((a,b)=>a.hp-b.hp))pool.append(girlCard(p,pick[0]===p.partner_id,()=>{pick=[p.partner_id];render();}));main.append(pool);}
  main.append(btn('ts-go','Select',async()=>{if(!sel){note='Please select';render();return;}const req={action:'recover',choice:Number(sel)};if(sel==='3'){const p=run.partners.find(x=>x.partner_id===pick[0]);if(!p){note="Choose a Girl";render();return;}if(p.hp>60&&!confirm('The Girl you choose still has relatively high HP. Confirm to continue?'))return;req.partner_id=p.partner_id;}sel=null;pick=[];await act(req);}));}
 function buffsModal(st,info){const run=info.run;const w=overlay(st,'Buff Obtained');const row=el('div','ts-buffs ts-wrap');const ids=Object.keys(run.skills);if(!ids.length)w.append(el('p','ts-note','No Data'));for(const b of ids)row.append(buffCard(b,info,run.skills[b]));w.append(row);}
 function hpModal(st,info){const w=overlay(st,'HP Status');const pool=el('div','ts-pool');for(const p of info.run.partners)pool.append(girlCard(p,false,()=>{}));w.append(pool);}
 function resultView(st){const r=result;const ov=el('div','ts-overlay');const w=el('div','ts-win ts-result');w.append(el('h3','','Results'),el('p','ts-big',number(r.score)),el('p','',r.completed?"Trial completed!":"Trial abandoned"),el('p','',`Highest unlocked difficulty: ${r.max_diff}`));
  w.append(btn('ts-go','OK',()=>{result=null;render();}));ov.append(w);st.append(ov);}
 // ShrineHurdleNoticeWindow: Task / Ranking / Reward / Achievement.
 function boardView(st,info){st.style.backgroundImage=`url('${A('shrine_main_bg.webp')}')`;top(st,{title:'Message Board',back:()=>{panel='hub';render();}});
  const tabs=el('div','ts-tabs');['Task','Ranking','Reward','Achievement'].forEach((t,i)=>tabs.append(btn('ts-tab'+(tab===i?' on':''),t,()=>{tab=i;render();})));st.append(tabs);
  const list=el('div','ts-list');st.append(list);
  const rowOf=(a,claim,done)=>{const r=el('div','ts-mrow'+(done?' done':''));const t=el('div','ts-mtext');t.append(el('span','',a.text+' '),el('em','',`(${number(Math.min(a.value,a.need))}/${number(a.need)})`));r.append(t);
   const bot=el('div','ts-mbot');const aw=el('div','ts-tiles');for(const [k,n] of Object.entries(a.awards))aw.append(tile(k,n));bot.append(aw);
   if(done)bot.append(img('/assets/echoes/mission_awarded_en_en.png','ts-stamp','Collected'));else{const b=btn(a.claimable?'ts-go':'ts-white',a.claimable?'Claim':'Go',async()=>{if(!a.claimable){panel='trials';render();return;}const res=await act(claim);if(res?.got)CampaignUI.popup(a.text,res.got);});bot.append(b);}r.append(bot);return r;};
  if(tab===0){const t=el('p','ts-hint','');t.dataset.at=info.fighting?info.fight_end:info.season_end;t.dataset.prefix='Remaining Time: ';t.textContent=t.dataset.prefix+left(Number(t.dataset.at));list.append(t);
   for(const m of [...info.tasks].sort((a,b)=>(b.claimable-a.claimable)||(a.claimed-b.claimed)||a.id-b.id))list.append(rowOf(m,{action:'claim_task',id:m.id},m.claimed));}
  else if(tab===1){const box=el('div','ts-box');box.append(el('b','',`Total Score: ${number(info.total)}`));for(const r of info.routes)box.append(el('p','',`${r.name}: ${number(r.best)}`));
   list.append(box);if(typeof Bots!=='undefined')list.append(Bots.list('shrine'));list.append(el('p','ts-hint',"Ranking with simulated players. Season rewards still depend on your score (Reward tab)."));}
  else if(tab===2){list.append(el('p','ts-hint',"Season reward based on the total score of all 3 trials (replaces ranking without a server)."));
   for(const r of info.brackets){const row=el('div','ts-mrow');row.append(el('div','ts-mtext',`${r.show} · total ≥ ${number(r.need)}`));const aw=el('div','ts-tiles');for(const [k,n] of Object.entries(r.awards))aw.append(tile(k,n));row.append(aw);list.append(row);}}
  else for(const a of [...info.ach].sort((x,y)=>(y.claimable-x.claimable)||(x.done-y.done)||x.id-y.id))list.append(rowOf(a,{action:'claim_ach',id:a.id},a.done));}
 // ShrineHurdleShopWindow (Pond of Prayers): Current Season / Permanent, paid with Origami Cranes.
 function pondView(st,info){st.style.backgroundImage=`url('${A('shrine_main_bg.webp')}')`;top(st,{title:'Pond of Prayers',back:()=>{panel='hub';render();},chips:[chip('323',info.cranes)]});
  const tabs=el('div','ts-tabs');['Current Season','Permanent'].forEach((t,i)=>tabs.append(btn('ts-tab'+(tab===i?' on':''),t,()=>{tab=i;render();})));st.append(tabs);
  const grid=el('div','ts-shop');const rows=tab===0?info.shop.season.map(r=>({...r,shop:2})):info.shop.permanent;
  for(const r of rows){const [k,n]=String(r.item).split('#');const [ck,cn]=String(r.cost).split('#');const c=el('div','ts-good');c.append(tile(k,Number(n)),el('small','',itemCatalog?.[k]?.name||''),el('small','ts-left',`${r.buy_time-r.bought}/${r.buy_time}`));
   const b=btn('ts-go ts-buy','',async()=>{const res=await act({action:'shop',shop:r.shop,id:r.id});if(res?.got)CampaignUI.popup('Pond of Prayers',res.got);});b.append(chip(ck,Number(cn)));b.disabled=r.bought>=r.buy_time;c.append(b);grid.append(c);}
  st.append(grid);}
 function chimesView(st){st.style.backgroundImage=`url('${A('shrine_main_bg.webp')}')`;top(st,{title:'Tree of Chimes',back:()=>{panel='hub';render();}});
  st.append(el('p','ts-note ts-box',"Tree of Chimes has not been restored yet. Fantasy Dust and Fantasy Talisman remain in your Bag until it is ready."));}
 return {open,render};
})();
