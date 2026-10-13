'use strict';
// Game Assistant (game_assistant_window.prefab / GameAssistantWindow.lua / GameAssistantResultWindow): the daily routine in
// one tap. Window 680×1127 (gameAssistant_bg_yxzs), four tabs Daily / Challenges / Growth / Guild (gameAssistant_btn_yxzs_*),
// parts with a title between gf12 lines, groups with the gf1 bar and 602×70 rows (9gongge48 + the part's illustration)
// holding YES / NO radios (setting_up_lan1/2) or − n + steppers; "Initiate this page" and "Initiate All", then the Overview.
// Rules: Engine.assistant_run (each step is the player's own action). Settings are this viewer's (localStorage).
const GameAssistant=(()=>{
 const A=n=>'/assets/assistant/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const TABS=[['Hằng Ngày','rc'],['Thử Thách','tz'],['Phát Triển','py'],['Bang Hội','zt']];
 const HOUSES=['Trí Tuệ','Dũng Cảm','Huyền Bí','Phong','U Linh','Thiên Thần'];
 // page → parts → groups → rows: [key, kind ('yn' | 'step'), label, illustration]
 const PAGES=[
  [['Alchemy',[['Dùng lượt miễn phí',['midas','yn','','djs1']],['Mua bằng Kim Cương',['midas_buy','step','Giới hạn lượt mua','djs12']]]],
   ['Nhận thưởng Chiến Dịch',[[null,['campaign','yn','','gj']]]],
   ['Nhận tài nguyên Ký Túc Xá',[[null,['dorm','yn','','ss']]]],
   ['Câu Hỏi Hằng Ngày',[['Dùng lượt miễn phí',['quiz','yn','','djs1']]]],
   ['Triệu Hồi',[['Triệu Hồi Cao Cấp',['senior','yn','','nd1']],['Triệu Hồi Thường',['capsule','yn','','nd2']]]],
   ['Đấu Trường Sơ Cấp',[['Hoàn thành 3 trận',['arena','yn','','xyls']]]],
   ['Thực Tập',[['Nhận thưởng Thực Tập hoàn tất',['internship','yn','','xzsp']]]],
   ['Hòm Thư và Nhiệm Vụ',[['Nhận tất cả thư',['mail','yn','','cc']],['Nhận nhiệm vụ hằng ngày',['daily','yn','','xzsp1']]]]],
  [['Khảo Thí Học Viện',[['Chọn Hệ',['house','houses']],['Số lượt quét bằng Giấy Chứng Nhận',['house_raids','step','','tz_gmsp1']],[null,['exam','yn','Raid','tz_xykh']]]]],
  [['Thám Hiểm Học Viện',[['Nhận tài nguyên',['excursion','yn','','py_yz1']],['Mua Bánh Mì',['bread','step','Chọn số lượng','py_yz2']]]]],
  [['Văn Phòng',[['Điểm Danh',['guild_sign','yn','','st_qd']]]],['Nhà Ăn',[['Bắt đầu đơn hàng',['guild_order','yn','','st_ct']]]]]];
 const KEYS=PAGES.map(p=>p.flatMap(([,groups])=>groups.map(([,r])=>r).filter(r=>r[1]==='yn').map(r=>r[0])));
 let cfg;try{cfg=JSON.parse(localStorage.getItem('gxb2.assistant2')||'null');}catch{}
 if(!cfg){let old=null;try{old=JSON.parse(localStorage.getItem('gxb2.assistant')||'null');}catch{}cfg={on:Object.fromEntries(KEYS.flat().map(k=>[k,old?old.includes(k):!k.startsWith('guild')&&k!=='exam'])),opts:{midas_buy:0,house:1,house_raids:0,bread:0}};}
 const save=()=>{try{localStorage.setItem('gxb2.assistant2',JSON.stringify(cfg));}catch{}};
 let tab=0,wrap=null,busy=false;
 function icon(id){const it=itemCatalog?.[id];if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}return it&&itemIcons.has(it.icon)?'/assets/item-icons/'+it.icon+'.png':'';}
 const at=(e,x,y,w,h)=>{e.style.left=`calc(${360+x-w/2} * var(--u))`;e.style.top=`calc(${640-y-h/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;if(h!=null)e.style.height=`calc(${h} * var(--u))`;return e;};
 function limits(){const m=state.midas_info||{},x=state.explore_info||{},h=state.house_exam_info||{};return {midas_buy:Math.max(0,(m.times||0)-(m.buys||0)),house_raids:h.certs||0,bread:Math.max(0,(x.buy_limit||0)-(x.bought||0))};}
 function open(){tab=0;render();}
 function close(){wrap?.remove();wrap=null;}
 function render(){wrap?.remove();wrap=el('div','ga2-wrap');wrap.onclick=e=>{if(e.target===wrap)close();};const st=el('div','ga2-stage');wrap.append(st);
  st.append(at(el('div','ga2-bg'),0,0,680,1127));
  const title=at(el('b','ga2-title','Trợ Lý Trò Chơi'),0,457,350,40);const x=at(el('button','ga2-x'),307,456,40,40);x.type='button';x.setAttribute('aria-label',"Đóng Trợ Lý Trò Chơi");x.style.backgroundImage=`url('${A('close_btn_2')}')`;x.onclick=close;
  const help=at(el('button','ga2-help'),-306,456,42,42);help.type='button';help.setAttribute('aria-label',"Hướng Dẫn Trợ Lý Trò Chơi");help.style.backgroundImage=`url('${A('btn_tips')}')`;help.onclick=()=>CampaignUI.popup("Trợ Lý Trò Chơi\n\nHằng ngày: Luyện Kim, nhận thưởng Chiến Dịch, Câu Hỏi Hằng Ngày, Triệu Hồi, Đấu Trường, Thực Tập, Hòm Thư và Nhiệm Vụ.\nThử Thách: Khảo Thí Học Viện bằng Giấy Chứng Nhận (quét ải cao nhất đã vượt).\nPhát Triển: nhận tài nguyên Thám Hiểm và mua Bánh Mì.\nBang Hội: điểm danh và nhận nhiệm vụ Nhà Ăn khi hệ thống hỗ trợ.\n\nMỗi bước gửi yêu cầu thật tới máy chủ. Thao tác chưa hỗ trợ sẽ được ghi rõ là bỏ qua.",{});
  st.append(title,x,help);
  TABS.forEach(([n,ic],i)=>{const b=at(el('button','ga2-tab'+(tab===i?' on':'')),-243+162*i,373,164,116);b.type='button';b.style.backgroundImage=`url('${A(tab===i?'gameAssistant_btn_yxzs_gl':'gameAssistant_btn_yxzs_glzc')}')`;b.append(img(A('gameAssistant_btn_yxzs_'+ic)));b.title=n;b.onclick=()=>{tab=i;render();};st.append(b);});
  st.append(at(el('div','ga2-bg2'),0,-71,630,744),at(el('b','ga2-page',TABS[tab][0]),2,269,300,40));
  const sc=at(el('div','ga2-scroll'),0,-58,630,610);const lim=limits();
  for(const [part,groups]of PAGES[tab]){const pt=el('div','ga2-part');pt.append(img(A('gameAssistant_bg_yxzs_gf12'),'l'),el('b','',part),img(A('gameAssistant_bg_yxzs_gf12'),'r'));sc.append(pt);
   for(const [gname,row]of groups){if(gname){const gt=el('div','ga2-gtitle',gname);gt.style.backgroundImage=`url('${A('gameAssistant_bg_yxzs_gf1')}')`;sc.append(gt);}sc.append(rowOf(row,lim));}}
  st.append(sc);
  const cur=at(el('button','ga2-btn white','Thực Hiện Trang Này'),-124,-497,211,65);cur.type='button';cur.style.backgroundImage=`url('${A('white_btn70_70')}')`;cur.onclick=()=>run(KEYS[tab]);
  const all=at(el('button','ga2-btn blue','Thực Hiện Tất Cả'),149,-497,211,65);all.type='button';all.style.backgroundImage=`url('${A('blue_btn70_70')}')`;all.onclick=()=>run(KEYS.flat());
  cur.disabled=all.disabled=busy;st.append(cur,all);(window.GxbFrame?.root()||document.body).append(wrap);}
 function rowOf([key,kind,label,pic],lim){const r=el('div','ga2-row'+(kind==='step'?' tall':''));
  if(pic)r.append(img(A('gameAssistant_bg_'+(pic.includes('_')&&!pic.startsWith('rc')?pic:'rc_'+pic)),'ga2-pic'));
  if(kind==='yn'){for(const [v,t,x]of [[true,label||'CÓ',0],[false,'KHÔNG',1]]){const b=el('button','ga2-radio'+(Boolean(cfg.on[key])===v?' on':''));b.type='button';b.append(img(A(Boolean(cfg.on[key])===v?'setting_up_lan1':'setting_up_lan2')),el('span','',t));b.onclick=()=>{cfg.on[key]=v;save();render();};r.append(b);}}
  else if(kind==='step'){const max=lim[key]??99;const v=Math.min(Number(cfg.opts[key]||0),max);if(label)r.append(el('b','ga2-slabel',label));const s=el('div','ga2-step');
   const set=n=>{cfg.opts[key]=Math.max(0,Math.min(max,n));save();render();};for(const [t,f]of [['⏮',()=>set(0)],['−',()=>set(v-1)]]){const b=el('button','',t);b.type='button';b.onclick=f;s.append(b);}
   s.append(el('b','ga2-num',String(v)));for(const [t,f]of [['+',()=>set(v+1)],['⏭',()=>set(max)]]){const b=el('button','',t);b.type='button';b.onclick=f;s.append(b);}r.append(s);
   const lim2=el('small','ga2-limit',key==='bread'?`Giới hạn: ${v}/${max}`:key==='house_raids'?`Giấy chứng nhận: ${max}`:`Giới hạn: ${v}/${max}`);r.append(lim2);}
  else if(kind==='houses'){const hs=el('div','ga2-houses');HOUSES.forEach((n,i)=>{const b=el('button','ga2-house'+(Number(cfg.opts.house||1)===i+1?' on':''));b.type='button';b.title='Hệ '+n;b.append(img('/assets/factions/'+(i+1)+'.png'));b.onclick=()=>{cfg.opts.house=i+1;save();render();};hs.append(b);});r.append(hs);}
  return r;}
 async function run(keys){const steps=keys.filter(k=>cfg.on[k]);const o=cfg.opts;if(o.midas_buy>0&&cfg.on.midas!==undefined&&keys.includes('midas'))steps.includes('midas')||steps.push('midas');
  if(keys.includes('exam')&&cfg.on.exam&&!o.house_raids){CampaignUI.popup("Chọn số lượt quét bằng Giấy Chứng Nhận.",{});return;}
  if(!steps.length){CampaignUI.popup('Hiện chưa có thao tác nào có thể thực hiện',{});return;}
  busy=true;render();try{const r=await api('/api/assistant/run',{steps,opts:{midas_buy:keys.includes('midas_buy')||keys.includes('midas')?o.midas_buy:0,house:o.house,house_raids:o.house_raids,bread:keys.includes('excursion')?o.bread:0}});state=r.state;if(typeof render==='function'&&window.render)window.render();busy=false;close();overview(r.report);}
  catch(e){busy=false;render();CampaignUI.popup(e.message,{});}}
 // GameAssistantResultWindow: "Overview · Completed", one titled block per step with its rewards
 function overview(report){const w=el('div','ga2-wrap');const box=el('div','ga2-over');w.append(box);box.append(el('b','ga2-otitle','Tổng Kết'),el('p','ga2-done','⌛ Hoàn tất'));const list=el('div','ga2-olist');
  for(const s of report){const b=el('div','ga2-res'+(s.ok?'':' skip'));b.append(el('b','',s.label));
   if(s.ok){const g=el('div','ga2-items');for(const [k,v]of Object.entries(s.got||{})){if(k==='battles'||k==='orders'){g.append(el('small','',v+(k==='battles'?' battle(s)':' order(s)')));continue;}const c=el('span','ga2-item');const ic=icon(k);if(ic)c.append(img(ic));c.append(el('small','',number(v)));c.title=itemCatalog?.[k]?.name||k;g.append(c);}if(!g.childElementCount)g.append(el('small','','Hoàn tất'));b.append(g);}
   else b.append(el('small','ga2-skip',s.error||'Đã bỏ qua'));list.append(b);}
  box.append(list);const ok=el('button','ga2-btn blue','Xác Nhận');ok.type='button';ok.style.backgroundImage=`url('${A('blue_btn70_70')}')`;ok.onclick=()=>w.remove();box.append(ok);(window.GxbFrame?.root()||document.body).append(w);}
 document.addEventListener('DOMContentLoaded',()=>{const side=document.querySelector('#home-view .home-stage');if(side&&!$('ga-open')){const b=el('button','ga-open');b.id='ga-open';b.type='button';b.title='Trợ Lý Trò Chơi';b.setAttribute('aria-label','Trợ Lý Trò Chơi');b.append(img('/assets/assistant/gameAssistant_icon_yxzs.png'),el('small','','Trợ Lý'));b.onclick=open;side.append(b);}});
 function homeSignals(s){
  const h=s.home_systems||{},m=s.missions_info||{},items=s.items||{};
  const affords=cost=>{const pairs=String(cost||'').split('|').filter(x=>x.includes('#'));return pairs.length>0&&pairs.every(x=>{const [k,n]=x.split('#');return Number(items[k]||0)>=Number(n);});};
  const tasks=(m.daily||[]).some(t=>t.tracked&&!t.claimed&&Number(s.level)>=Number(t.lv||0))||(m.trophies||[]).some(t=>t.can);
  const mail=(h.mail||[]).some(t=>!t.read||(!t.claimed&&t.awards));
  const book=(h.missions||[]).some(t=>!t.claimed&&t.progress>=t.goal);
  const servant=Object.values(h.pet_details||{}).some(p=>affords(p.level_cost)||affords(p.grade_cost)||(p.skill_details||[]).some(t=>t.open&&t.lv<t.max&&affords(t.cost)));
  const excursion=(s.explore_info?.chests||[]).some(t=>t.ready)||(h.buildings||[]).some(t=>t.stock>0);
  const assistant=mail||book||(m.daily||[]).some(t=>!t.claimed&&t.have>=t.need&&Number(s.level)>=Number(t.lv||0))||s.midas_info?.free_ready||s.summon?.free_ready||s.summon?.senior_free_ready||excursion;
  return {tasks,mail,book,servant,excursion,assistant};
 }
 function updateHome(){const flags=homeSignals(state);for(const [selector,key]of [['.ms-home-btn','tasks'],['.home-mail','mail'],['.home-right [data-coming="Libro"]','book'],['.home-right [data-coming="Servant"]','servant'],[".home-right [data-coming=\"Excursion\"]",'excursion'],['#ga-open','assistant']]){const b=document.querySelector(selector);if(!b)continue;let dot=b.querySelector('.home-pending');if(!dot){dot=el('span','home-pending');dot.setAttribute('aria-hidden','true');b.append(dot);}dot.hidden=!flags[key];b.dataset.pending=String(Boolean(flags[key]));}}
 return {open,updateHome,homeSignals};
})();
