'use strict';
// House Exam (AcademyAssessmentWindow → AcademyAssessmentDetailWindow2 → battle_formation_window / SweepWindow).
// Rules: gxb2/house_exam.py. Layout follows docs/references/2026-09-29-b/07-demon-exam-list.webp.
const HouseExam=(()=>{
 let origin='league',fort=0,panel=null,note='',busyLocal=false,data=null,team=[],enemies=null,sweepStage=0,sweepTimes=1,skipReplay=false,timer=null;
 let rankFort=0,rankingRows=null,rankingBusy=false,rankingError='';
 async function fetchRanking(f=rankFort){
  rankFort=f;rankingRows=null;rankingBusy=true;rankingError='';
  try{const r=await api('/api/house-exam/ranking',{fort:f});
      if(rankFort===f)rankingRows=r.ranking||[];
  }catch(e){if(rankFort===f)rankingError=e.message||'Không tải được bảng xếp hạng.';}
  finally{if(rankFort===f){rankingBusy=false;if(view==='house-exam'&&panel==='ranking')render();}}
 }

 const A=n=>'/assets/house-exam/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const btn=(cls,text,fn)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
 const TEXT_VI={"SCHOOL_PRACTICE_TITLE_01":"Hệ U Linh Ma","SCHOOL_PRACTICE_TITLE_02":"Hệ Nhân Tộc","SCHOOL_PRACTICE_TITLE_03":"Hệ Ma Thú","SCHOOL_PRACTICE_TITLE_04":"Hệ Tinh Linh","SCHOOL_PRACTICE_TITLE_05":"Hệ Bóng Tối","SCHOOL_PRACTICE_TITLE_06":"Hệ Ánh Sáng","SCHOOL_PRACTICE_TEXT_01":"Tìm ra bí mật là đã đi được nửa chặng đường.","SCHOOL_PRACTICE_TEXT_02":"Chiến đấu như một chiến binh thực thụ!","SCHOOL_PRACTICE_TEXT_03":"Cẩn thận! Những học viên này ẩn chứa sức mạnh Ma Thú.","SCHOOL_PRACTICE_TEXT_04":"Bé đã sẵn sàng đón nhận thử thách của Tinh Linh chưa?","SCHOOL_PRACTICE_TEXT_05":"Cảnh báo! Nguy hiểm đang đến!","SCHOOL_PRACTICE_TEXT_06":"Ánh sáng thiêng liêng vừa có thể chiến đấu vừa có thể chữa lành.","ACADEMY_ASSESSMENT_TEXT01":"Bắt được ta thì hãy bắt!","ACADEMY_ASSESSMENT_TEXT02":"Sức mạnh đến từ trật tự và kỷ luật!","ACADEMY_ASSESSMENT_TEXT03":"Chào đón những ai tìm kiếm tự do chân chính!","ACADEMY_ASSESSMENT_TEXT04":"Chỉ những người ưu tú mới vượt qua thử thách!","ACADEMY_ASSESSMENT_TEXT05":"Sức mạnh là điều duy nhất chúng ta coi trọng!","ACADEMY_ASSESSMENT_TEXT06":"Đừng sợ thử thách, ánh sáng sẽ bảo vệ bé!","ACADEMY_ASSESSMENT_CURRENT_TEXT":"Tiến độ hiện tại: {1}/{2}","ACADEMY_ASSESSMENT_END_TIME":"Thời gian còn lại:","SCHOOL_PRACTICE_DISPLAY":"Đang tổng kết:","ACADEMY_ASSESSMENT_BATTLE_FORMATION_WINDOW":"Đội hình chiến đấu","ACADEMY_ASSESSMENT_SWEEP_WINDOW":"Quét ải","ACADEMY_ASSESSMENT_SWEEP_TIPS":"Bé muốn quét ải này bao nhiêu lượt?","ACADEMY_ASSESSMENT_WINDOW_HELP_NEW_2":"1. Kỳ Thi Nhà gồm 13 ngày thi và 1 ngày tổng kết.|2. Trong kỳ thi, cả 6 hệ đều mở. Chỉ Nữ Thần đúng hệ mới được tham gia.|3. Mỗi ải mới tiêu hao một Vé Dự Thi, vé được làm mới hằng ngày; có thể mua thêm bằng Kim Cương.|4. Vượt ải nhận Điểm Thi, Chứng Chỉ và phần thưởng. Những ải đã vượt có thể quét bằng Chứng Chỉ.|5. Điểm và tiến độ được tính theo mùa.","SCHOOL_PRACTICE_SWEEP_TICKETS_NOT_ENOUGH":"Không đủ Chứng Chỉ","SCHOOL_PRACTICE_CHALLENGE_TICKETS_NOT_ENOUGH":"Không đủ Vé Dự Thi","ACADEMY_ASSESSMENT_FIRST_PASS_AWARD":"Phần thưởng:","ACADEMY_ASSESSMENT_MISC":"Hoàn thành kỳ thi\nGia tăng sức mạnh","ACADEMY_ASSESSMENT_WINDOW_HELP":"Chỉ Nữ Thần đúng hệ mới được tham gia. Vé Dự Thi dùng khi đánh ải mới; quét ải đã qua bằng Chứng Chỉ. Mở phần thưởng mùa để xem kết quả.","ACADEMY_ASSESSMENT_FINAL_RANK_WINDOW_HELP":"Hướng dẫn kỳ thi","ACADEMY_ASSESSMENT_FINAL_SHOW_TIP":"Kết quả kỳ thi:","ACADEMY_ASSESSMENT_END_TIPS":"Kỳ thi đã kết thúc","ACADEMY_ASSESSMENT_WINDOW_HELP_NEW":"Kỳ Thi Nhà có 13 ngày thi và 1 ngày tổng kết, gồm 6 hệ riêng biệt.","ACADEMY_ASSESSMENT_ONE_CAMP_RANK_AWARD_HELP":"Bảng xếp hạng tính theo Điểm Thi thực trong mùa, đồng điểm xét thời gian vượt ải.","SCHOOL_PRACTICE_NEW_SEASON":"Đã mở mùa mới","SCHOOL_PRACTICE_FINISH":"Sắp kết thúc","SCHOOL_PRACTICE_NOT_OPEN_YET":"Sắp mở","SCHOOL_PRACTICE_RETRY_CONFIRM":"Đấu lại với cùng đội hình?","SCHOOL_PRACTICE_RETRY":"Đấu lại","ACADEMY_ASSESSMENT_FORMATION_TIPS":"Chạm ảnh Nữ Thần để xem chi tiết."};
 const T=k=>TEXT_VI[k]??data?.text?.[k]??k;
 try{skipReplay=localStorage.getItem('gxb2.houseExam.skip')==='1';}catch{}
 function root(){let r=$('house-exam-view');if(!r){r=el('section','house-exam-view');r.id='house-exam-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function open(from){origin=from||view;fort=0;panel=null;note='';if(!data)data=await api('/assets/house-exam.json').catch(()=>null);showView('house-exam');act({action:'open'});}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';if(id==='63'||id==='64')return A('icon_'+id);const row=itemCatalog?.[id];return (row&&itemPicture(row))||(row?.icon?'/assets/shops/items/'+row.icon+'.png':'');}
 function nameOf(id){id=String(id);return ({'1':'Coins','2':'Gems','63':'Chứng Chỉ','64':'Vé Dự Thi'})[id]||itemCatalog?.[id]?.name||'Item '+id;}
 function pairs(t,times=1){const o={};for(const p of String(t||'').split('|')){const [k,n]=p.split('#');if(k&&n)o[k]=(o[k]||0)+Number(n)*times;}return o;}
 function chip(k,n,cls='he-chip'){const c=el('span',cls);const s=icon(k);if(s)c.append(img(s));c.append(el('b','',number(n)));c.title=nameOf(k);return c;}
 async function act(req){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/house-exam/action',req);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;if(view==='house-exam')render();}}
 function left(at){const s=Math.max(0,at-(state.server_time||Math.floor(Date.now()/1000))-Math.floor((performance.now()-loadedAt)/1000));const d=Math.floor(s/86400);return (d?d+'d ':'')+[Math.floor(s%86400/3600),Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');}
 let loadedAt=performance.now();
 function topBar(st,info){const bar=el('div','he-top');
  for(const [id,val,fn]of [['63',info.certs,()=>{panel='buy-cert';render();}],['64',info.tickets,()=>{panel='buy-ticket';render();}]]){const r=el('div','he-res');r.append(img(icon(id)),el('b','',String(val)),btn('he-plus','+',fn));r.title=nameOf(id);bar.append(r);}
  const back=btn('he-back','',()=>{if(fort){fort=0;panel=null;render();}else showView(origin==='house-exam'?'league':origin);});back.append(img('/assets/ui/win_back_btn.png'));bar.append(back);st.append(bar);}
 function render(){const r=root();if(view!=='house-exam'){clearInterval(timer);timer=null;return;}loadedAt=performance.now();const info=state.house_exam_info;r.replaceChildren();const st=el('div','he-stage');r.append(st);st.append(img(A('academy_assessment_bg'),'he-bg'));
  if(!info||!data){st.append(el('p','he-note',"Đang tải…"));return;}
  if(!info.unlocked){topBar(st,info);st.append(el('p','he-note he-box',`Kỳ Thi Nhà mở sau khi vượt ải ${info.unlock_stage}.`));return;}
  topBar(st,info);
  if(fort)detail(st,info);else list(st,info);
  if(note)st.append(el('p','he-note he-err',note));
  if(panel)popup(st,info);
  clearInterval(timer);timer=setInterval(()=>{const c=root().querySelector('.he-clock');if(!c||view!=='house-exam'){clearInterval(timer);return;}c.textContent=fort?left(info.open?info.exam_end:info.season_end):clock(info);},1000);}
 // AcademyAssessmentWindow (prefab academy_assessment_window, capture 2026-09-29-k/01): header group1 720×260 — help /
 // rank / award on the left, logo between the mirrored academy_assessment_title_bg_new halves with "Time Remaining:",
 // shop + dress-show buff on the right — then the scroller of academy_assessment_item (682×214): house art
 // btn_academy_assessment_N_new + academy_assessment_right_bg_new, title, tagline, "Current Progress: X/100", DONE stamp and
 // the chevron that unfolds groupExtra (the current stage with its fight / raid button).
 let open_=0;
 function clock(info){const s=Math.max(0,(info.open?info.exam_end:info.season_end)-(state.server_time||Math.floor(Date.now()/1000))-Math.floor((performance.now()-loadedAt)/1000));const d=Math.floor(s/86400),h=Math.floor(s%86400/3600);return d?`${d}D ${h}H`:[h,Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');}
 function list(st,info){const head=el('div','he-head');
  const side=el('div','he-side l');side.append(btn('he-ico','',help),btn('he-ico','',()=>{rankFort=0;panel='ranking';void fetchRanking(0);render();}),btn('he-ico award','',()=>{panel='season';render();}));
  [['help_2','Hướng dẫn'],['btn_rank_2','Xếp hạng'],['btn_award','Thưởng mùa']].forEach(([n,t],i)=>{const b=side.children[i];b.title=t;b.append(img(A(n)));});
  const title=el('div','he-title');title.append(img(A('academy_assessment_title_bg_new'),'he-tbg l'),img(A('academy_assessment_title_bg_new'),'he-tbg r'),el('h1','he-logo-vi','Kỳ Thi Nhà'));
  const tm=el('div','he-time');tm.append(el('span','',info.open?T('ACADEMY_ASSESSMENT_END_TIME'):T('SCHOOL_PRACTICE_DISPLAY')+':'),el('b','he-clock',clock(info)));title.append(tm);
  const rs=el('div','he-side r');const shop=btn('he-shop','',()=>{if(typeof Shops!=='undefined')Shops.open('house-exam',9);});shop.title='Cửa Hàng Kỳ Thi';shop.append(img(A('shop')));
  const star=btn('he-star','',()=>{panel='season';render();});star.title='Điểm Thi';star.append(img(A('dress_show_score_icon')));rs.append(shop,star);
  head.append(side,title,rs);st.append(head);
  const w=el('div','he-list');
  if(info.last_award&&Object.keys(info.last_award.got).length){const la=el('p','he-note he-last',"Mùa "+info.last_award.season+" kết thúc với "+info.last_award.score+" điểm: ");for(const [k,n]of Object.entries(info.last_award.got))la.append(chip(k,n));w.append(la);}
  for(const f of info.forts){const item=el('div','he-item-wrap'+(open_===f.fort?' open':''));const b=btn('he-house','',()=>{fort=f.fort;panel=null;render();setTimeout(()=>root().querySelector('.he-row.current')?.scrollIntoView({block:'center'}),50);});
   b.append(img(A('btn_academy_assessment_'+f.fort+'_new'),'he-house-bg'),img(A('academy_assessment_right_bg_new'),'he-house-right'),el('b','he-house-title',T('SCHOOL_PRACTICE_TITLE_0'+f.fort)),el('span','he-house-desc',T('SCHOOL_PRACTICE_TEXT_0'+f.fort)));
   b.append(el('span','he-prog',(T('ACADEMY_ASSESSMENT_CURRENT_TEXT')||'Current Progress: {1}/{2}').replace('{1}',f.done).replace('{2}',f.total)));
   if(f.current===-1)b.append(el('span','he-done-vi','HOÀN THÀNH'));
   const chev=btn('he-chev','',e=>{e.stopPropagation();open_=open_===f.fort?0:f.fort;render();});chev.append(img(A('activity_popularity_vote_up')));b.append(chev);item.append(b);
   if(open_===f.fort){const ex=el('div','he-extra');const stages=data.stages.filter(s=>s.fort_id===f.fort);const cur=f.current===-1?stages.length-1:Math.max(0,stages.findIndex(s=>s.id===f.current));
    const prev=fort;fort=f.fort;for(const i of [cur-1,cur].filter(i=>i>=0))ex.append(stageRow(stages[i],i,f,info));fort=prev;
    ex.append(btn('he-all',"Xem "+stages.length+" ải ›",()=>{fort=f.fort;open_=0;panel=null;render();setTimeout(()=>root().querySelector('.he-row.current')?.scrollIntoView({block:'center'}),50);}));item.append(ex);}
   w.append(item);}
  st.append(w);}
 function help(){CampaignUI.popup(T('ACADEMY_ASSESSMENT_WINDOW_HELP_NEW_2').split('|').join('\n'),{});}
 // AcademyAssessmentDetailWindow2: house banner with arrows, then the 100 stages.
 function detail(st,info){const f=info.forts.find(x=>x.fort===fort);const w=el('div','he-detail');
  const ban=el('div','he-banner');ban.append(img(A('academy_assessment_'+fort),'he-ban-img'),el('b','he-ban-logo-vi',T('SCHOOL_PRACTICE_TITLE_0'+fort)),el('div','he-quote',T('ACADEMY_ASSESSMENT_TEXT0'+fort)));
  ban.append(btn('he-arrow l','‹',()=>{fort=fort===1?6:fort-1;render();}),btn('he-arrow r','›',()=>{fort=fort===6?1:fort+1;render();}),btn('he-help','?',()=>CampaignUI.popup(T('ACADEMY_ASSESSMENT_WINDOW_HELP_NEW_2').split('|').join('\n'),{})));
  const tm=el('div','he-ban-time');tm.append(el('span','',info.open?'':T('SCHOOL_PRACTICE_DISPLAY')+' '),el('b','he-clock',left(info.open?info.exam_end:info.season_end)));ban.append(tm);w.append(ban);
  const rows=el('div','he-rows');const stages=data.stages.filter(s=>s.fort_id===fort);
  stages.forEach((s,i)=>rows.append(stageRow(s,i,f,info)));
  w.append(rows);st.append(w);}
 // one stage of AcademyAssessmentDetailWindow2 (also used by the list's unfolded groupExtra)
 function stageRow(s,i,f,info){const idx=i+1,cur=f.current,passed=cur===-1||cur>s.id,isCur=cur===s.id,first=!info.first_done.includes(s.id);
   const row=el('div','he-row'+(passed?' passed':isCur?' current':' locked'));
   const badge=el('div','he-badge');badge.style.backgroundImage=`url('${A('boss_award_bg_'+Math.min(8,Math.ceil(idx/10)))}')`;badge.append(el('b','',String(idx)));if(!passed&&!isCur)badge.append(img(A('academy_assessment_lock'),'he-lock'));row.append(badge);
   const rew=el('div','he-rewards');rew.style.backgroundImage=`url('${A(passed?'academy_assessment_award_bg':isCur&&first?'academy_assessment_award_bg_first':isCur?'academy_assessment_award_bg':'academy_assessment_award_bg_lock')}')`;
   const rw=passed?pairs(s.sweep_reward):first?pairs(s.first_reward):pairs(s.non_first_reward);for(const [k,n]of Object.entries(rw))rew.append(chip(k,n,'he-item'));if(isCur&&first)rew.append(el('small','he-first','Lần đầu'));row.append(rew);
   const go=btn('he-go','',()=>{fort=s.fort_id;passed?openSweep(s.id):openFight(s.id);});go.append(img(A(passed?'icon_63_small':'icon_64_small')),el('span','',passed?'Quét':'Chiến Đấu'));go.disabled=!info.open||(!passed&&!isCur);row.append(go);
   row.append(btn('he-info','!',()=>{fort=s.fort_id;showEnemies(s.id);}));return row;}
 async function showEnemies(stage){const r=await act({action:'enemies',stage});if(!r)return;enemies=r;panel='enemies';render();}
 function openSweep(stage){sweepStage=stage;sweepTimes=1;panel='sweep';render();}
 function openFight(stage){const info=state.house_exam_info;const f=info.forts.find(x=>x.fort===fort);team=(f.formation||[]).map(t=>({...t}));
  if(!team.length){const mine=(state.roster||[]).filter(h=>h.group===fort).sort((a,b)=>b.lv-a.lv).slice(0,6);team=mine.map((h,i)=>({partner_id:h.partner_id,pos:i+1}));}
  panel='fight:'+stage;render();}
 async function fight(stage){if(!team.length){note="Hãy chọn ít nhất một Nữ Thần";render();return;}panel=null;const r=await act({action:'fight',stage,team});if(!r)return;
  const label=`${T('SCHOOL_PRACTICE_TITLE_0'+fort)} · ${stage%1000}`;const got={...(r.got||{})};
  if(!skipReplay&&r.report&&typeof watchEventBattle==='function')await watchEventBattle({report:r.report,rewards:got},'house-exam',label);
  else CampaignUI.result(r.win,got,{event:true,label:label+(r.win?` · +${r.points} Điểm Thi`:''),report:r.report});
  if(r.cert_up)note=`Đã nhận ${r.cert_up} Chứng Chỉ mỗi ngày!`;
  if(!r.win){note="Đấu lại: bấm Chiến Đấu và giữ nguyên đội hình.";}render();}
 function popup(st,info){const ov=el('div','he-overlay');ov.onclick=e=>{if(e.target===ov){panel=null;render();}};const w=el('div','he-win');ov.append(w);const close=btn('he-close','✕',()=>{panel=null;render();});
  if(panel==='ranking'){
   w.classList.add('he-rankwin');
   w.append(el('h2','','Bảng Xếp Hạng Kỳ Thi · Mùa '+info.season),close);
   const tabs=el('div','he-ranktabs');
   for(let f=0;f<=6;f++){
     const name=f?T('SCHOOL_PRACTICE_TITLE_0'+f):'Tổng Điểm';
     tabs.append(btn('he-ranktab'+(rankFort===f?' on':''),name,()=>{void fetchRanking(f);render();}));
   }
   w.append(tabs);
   const board=el('div','he-rankrows');
   if(rankingBusy)board.append(el('p','','Đang tải bảng xếp hạng…'));
   else if(rankingError)board.append(el('p','he-rankerror',rankingError));
   else if(!rankingRows?.length)board.append(el('p','he-rankempty','Chưa có kết quả thi đấu ở mục này trong mùa hiện tại.'));
   else for(const p of rankingRows){
      const row=el('div','he-rankrow'+(p.me?' mine':'')),badge=el('strong','he-rankplace','#'+p.rank);
      const avatar=img('/assets/profile/'+(String(p.avatar||'head_1001').replace(/[^a-zA-Z0-9_-]/g,''))+'.png','he-rankavatar');
      avatar.onerror=()=>{avatar.onerror=null;avatar.src='/assets/profile/head_1001.png';};
      const name=el('div','he-rankname');name.append(el('b','',p.character_name),el('small','','Cấp '+p.level+' · Lực Chiến '+number(p.power)));
      const score=el('div','he-rankscore');
      score.append(el('b','',rankFort? p.progress+'/100':number(p.score)),
                   el('small','',rankFort?'Ải đã vượt':'Điểm Thi'));
      row.append(badge,avatar,name,score);board.append(row);
   }
   w.append(board);
  }
  else if(panel.startsWith('fight:')){const stage=Number(panel.slice(6));w.append(el('h2','',T('ACADEMY_ASSESSMENT_BATTLE_FORMATION_WINDOW')+' · '+T('SCHOOL_PRACTICE_TITLE_0'+fort)),close);
   const mine=(state.roster||[]).filter(h=>h.group===fort).sort((a,b)=>b.lv-a.lv);const byId=new Map(mine.map(h=>[h.partner_id,h]));team=team.filter(t=>byId.has(t.partner_id));
   const opts=el('div','he-fopts');const sk=btn('he-skip'+(skipReplay?' on':''),'',()=>{skipReplay=!skipReplay;try{localStorage.setItem('gxb2.houseExam.skip',skipReplay?'1':'0');}catch{};render();});sk.append(el('i','',skipReplay?'✓':''),el('span','','Bỏ qua'));opts.append(sk);w.append(opts);
   const grid=el('div','he-formation');for(const [label,poss]of [['Hàng trước',[1,2]],['Hàng sau',[3,4,5,6]]]){const line=el('div','he-line');line.append(el('b','he-line-name '+label.toLowerCase(),label));for(const p of poss){const t=team.find(x=>x.pos===p);const slot=btn('he-slot','',()=>{if(t){team=team.filter(x=>x!==t);render();}});if(t){const h=byId.get(t.partner_id);slot.append(typeof portrait==='function'?portrait(h.table_id,72):el('span'),el('small','',String(h.lv)));}line.append(slot);}grid.append(line);}w.append(grid);
   const pool=el('div','he-pool');if(!mine.length)pool.append(el('p','he-empty',"Không có Nữ Thần thuộc hệ này."));
   for(const h of mine){const used=team.some(t=>t.partner_id===h.partner_id);const c=btn('he-cand'+(used?' on':''),'',()=>{if(used)team=team.filter(t=>t.partner_id!==h.partner_id);else{const free=[1,2,3,4,5,6].find(p=>!team.some(t=>t.pos===p));if(free)team.push({partner_id:h.partner_id,pos:free});}render();});c.append(typeof portrait==='function'?portrait(h.table_id,64):el('span'),el('small','',`${h.lv} · ${h.stars}★`));c.title=h.name;pool.append(c);}
   w.append(pool);const go=btn('he-fight','Chiến Đấu',()=>fight(stage));go.prepend(img(A('icon_64_small')));w.append(go);}
  else if(panel==='sweep'){const info2=state.house_exam_info;w.append(el('h2','',T('ACADEMY_ASSESSMENT_SWEEP_WINDOW')+` · ${sweepStage%1000}`),close,el('p','',T('ACADEMY_ASSESSMENT_SWEEP_TIPS')));
   const s=data.stages.find(x=>x.id===sweepStage);const row=el('div','he-rewards-line');for(const [k,n]of Object.entries(pairs(s.sweep_reward,sweepTimes)))row.append(chip(k,n));w.append(row);
   const sel=el('div','he-times');sel.append(btn('he-small','−',()=>{sweepTimes=Math.max(1,sweepTimes-1);render();}),el('b','',String(sweepTimes)),btn('he-small','+',()=>{sweepTimes=Math.min(Math.max(1,info2.certs),sweepTimes+1);render();}),btn('he-small','Tối đa',()=>{sweepTimes=Math.max(1,info2.certs);render();}));w.append(sel);
   const go=btn('he-fight','Quét',async()=>{panel=null;const r=await act({action:'sweep',stage:sweepStage,times:sweepTimes});if(r?.got)CampaignUI.popup(`Quét ×${r.times}`,r.got);});go.prepend(img(A('icon_63_small')));go.append(el('small','',` −${sweepTimes}`));w.append(go);}
  else if(panel==='enemies'&&enemies){w.append(el('h2','',`Địch · ${enemies.stage%1000}`),close,el('p','',`Lực chiến ${number(enemies.power)}`));const g=el('div','he-enemies');for(const e of enemies.enemies.sort((a,b)=>a.pos-b.pos)){const c=el('div','he-cand');c.append(typeof portrait==='function'?portrait(e.table_id,64):el('span'),el('small','',`Lv.${e.lv}`));c.title=e.name;g.append(c);}w.append(g);}
  else if(panel==='season'){w.append(el('h2','',`Mùa ${info.season}`),close,el('p','',`Điểm thi: ${info.score} · Kỷ lục: ${info.history_score||0}`),el('p','',"Phần thưởng cuối mùa:"));const row=el('div','he-rewards-line');for(const [k,n]of Object.entries(info.season_award))row.append(chip(k,n));w.append(row);}
  else if(panel==='buy-ticket'){w.append(el('h2','','Vé Dự Thi'),close,el('p','',`Giá: ${info.ticket_cost['2']} Kim Cương/vé.`));const sel=el('div','he-times');for(const n of [1,5,10])sel.append(btn('he-small',`×${n} · ${n*info.ticket_cost['2']}💎`,async()=>{panel=null;await act({action:'buy_tickets',count:n});}));w.append(sel);}
  else if(panel==='buy-cert'){w.append(el('h2','','Chứng Chỉ'),close);if(!info.cert_cost)w.append(el('p','',"Đã mua đủ 10 Chứng Chỉ hôm nay."));else{w.append(el('p','',`Còn ${info.cert_left} lượt mua hôm nay. Lượt tiếp theo: ${info.cert_cost['2']} Kim Cương (giá tăng dần).`));w.append(btn('he-fight',"Mua 1",async()=>{panel=null;await act({action:'buy_certs',count:1});}));}}
  st.append(ov);}
 return {open,render};
})();
