'use strict';
// Fantasy Book (battle_pass_window.prefab + battle_pass_steam_new / _mission_new / _exchange_new / _achieve_new), laid out on the
// 720×1280 canvas from the prefab coordinates (y up, centre 640). Tabs Progress / Task / Exchange / Trophies on battle_pass_b_nav_1;
// Progress: top art + logo + countdown, "Current Pages" bar, Level / Basic Book / Luxury Book rows; Task: Daily / Weekly / Extra;
// Exchange: Crystal Leaf / Floral Stamp stores and Flora Bookmark draws; Trophies: the achievements. Rules: gxb2/fantasy_book.py.
const FantasyBook=(()=>{
 let origin='home',tab=0,sub=0,shopTab=1,note='',busy=false,timer=null;
 const A=n=>'/assets/fantasy-book/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const at=(e,x,y,w,h)=>{e.style.left=`calc(${360+x-w/2} * var(--u))`;e.style.top=`calc(${640-y-(h||0)/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;if(h!=null)e.style.height=`calc(${h} * var(--u))`;return e;};
 const btn=(cls,text,fn,off)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=!!off;return b;};
 const T=k=>(window.FB_TEXT||{})[k]||'';
 const info=()=>state?.fantasy_book_info||null;
 // Two themed seasons alternate: "Fantasy Book" (Pages 223 · Floral Stamp 221 · Crystal Leaf 222, the *_new sprites) and
 // "Restart the Engine!" (Gearwheel 117 · Screws 119 · Mecha Core 120, the first battle pass skin).
 const THEMES={book:{top:'battle_pass_top_bg_new',logo:'battle_pass_logo_new_en_en',logoH:215,t:['battle_pass_title_0_new','battle_pass_title_1_new','battle_pass_title_2_new'],exTop:()=>'bp_exchange_top_bg',exLogo:()=>'bp_exchange_shop_en_en',sbg:'bp_shop_item_bg',buy:'battle_pass_buy_btn_new',names:null,title:'Sách Kỳ Ảo',draw:'Dấu Trang Hoa'},
  engine:{top:'battle_pass_top_bg',logo:'battle_pass_logo_en_en',logoH:256,t:['battle_pass_title_0','battle_pass_title_1','battle_pass_title_2'],exTop:k=>k===2?'battle_pass_exchange_top_bg_2':'battle_pass_exchange_top_bg_1',exLogo:k=>k===2?'battle_pass_shop_2_en_en':'battle_pass_shop_1_en_en',sbg:'battle_pass_shop_item_bg',buy:'battle_pass_buy_btn',names:['Ốc Vít','Lõi Cơ Giáp','Xưởng Rèn'],title:'Khởi Động Lại Động Cơ!',draw:'Lò Rèn'}};
 const TH=()=>THEMES[info()?.theme]||THEMES.book;
 const disp=id=>{id=String(id);const e=info()?.theme==='engine';return id==='117'?(info()?.page||'223'):e&&id==='221'?'119':e&&id==='222'?'120':id;};
 function pairs(t){return String(t||'').split('|').filter(x=>x.includes('#')).map(x=>x.split('#'));}
 function iconOf(id){id=disp(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';if(['117','119','120','221','222','223'].includes(id))return A('icon_'+id);const it=itemCatalog?.[id];return it&&typeof itemPicture==='function'?itemPicture(it):'';}
 function item(id,n,cls=''){const c=el('span','fb-item '+cls);const s=iconOf(id);if(s)c.append(img(s));c.append(el('b','',number(Number(n))));c.title=itemCatalog?.[disp(id)]?.name||({'117':'Bánh Răng','223':'Trang Sách'})[disp(id)]||id;return c;}
 function root(){let r=$('fantasy-book-view');if(!r){r=el('section','fantasy-book-view');r.id='fantasy-book-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function open(from){origin=from||view;tab=0;note='';root();showView('fantasy-book');render();if(!window.FB_LEVELS){try{const b=await api('/assets/fantasy-book/book.json');window.FB_TEXT=b.text||{};window.FB_LEVELS=b.levels||[];window.FB_SHOP=b.shop||[];window.FB_LOTTERY=b.lottery_cost;window.FB_ODDS=b.odds||[];}catch(e){window.FB_TEXT={};note='Không thể tải dữ liệu Sách Kỳ Ảo: '+e.message;render();return;}}await act({action:'open'});}
 async function act(req,after){if(busy)return null;busy=true;note='';try{const r=await api('/api/fantasy-book/action',req);state=r.state;if(after)after(r);return r;}catch(e){note=e.message;return null;}finally{busy=false;render();}}
 function left(){const end=Number(info()?.end||0);if(!end)return 'Đang cập nhật';const s=Math.max(0,end-Math.floor(Date.now()/1000));return Math.floor(s/86400)+' ngày '+Math.floor(s%86400/3600)+' giờ còn lại';}
 function render(){const r=root();if(view!=='fantasy-book'){clearInterval(timer);return;}r.replaceChildren();if(!info()){clearInterval(timer);const box=el('div','fb-load-error');box.append(el('h2','','Sách Kỳ Ảo'),el('p','',note||'Đang tải dữ liệu Sách Kỳ Ảo…'));const retry=btn('gs-btn','Tải Lại',()=>{window.FB_LEVELS=null;open(origin);});const back=btn('gs-btn','Quay Lại',()=>showView(origin==='fantasy-book'?'home':origin));box.append(retry,back);r.append(box);return;}const st=el('div','fb-stage');r.append(st);
  if(document.documentElement.classList.contains('gxb-mobile')){
   const bounds=r.getBoundingClientRect(),w=Math.max(1,bounds.width||window.innerWidth),h=Math.max(1,bounds.height||window.innerHeight);
   const scale=Math.min(w/720,h/1280);
   st.style.setProperty('--u',scale+'px','important');
   st.style.setProperty('width',720*scale+'px','important');
   st.style.setProperty('height',1280*scale+'px','important');
   st.style.setProperty('max-width','100%','important');
   st.style.setProperty('max-height','100%','important');
  }
  [progress,tasks,exchange,trophies][tab](st);
  // battle_pass_b_nav_1 with the four tabs (content y 16 + 522)
  const nav=at(el('div','fb-nav'),0,538,720,60);nav.style.backgroundImage=`url('${A('battle_pass_b_nav_1')}')`;
  (T('BP_TAGS')||'Tiến Độ|Nhiệm Vụ|Đổi Thưởng|Thành Tựu').split('|').forEach((n,i)=>{const b=at(btn('fb-tab'+(tab===i?' on':''),n,()=>{tab=i;sub=0;render();}),[-242.5,-77.5,77.5,232.5][i]+360-360,0,i?150:165,44);b.style.top='calc(8 * var(--u))';b.style.left=`calc(${360+[-242.5,-77.5,77.5,232.5][i]-(i?75:82.5)} * var(--u))`;b.style.backgroundImage=`url('${A(tab===i?'battle_pass_nav_select':'battle_pass_nav')}')`;nav.append(b);});st.append(nav);
  // WindowTop (gold, gems, back) and the bottom navigation
  const top=at(el('div','fb-top'),0,612,720,56);for(const id of ['1','2']){const c=el('span','fb-res');c.append(img(iconOf(id)),el('b','',number(state.items?.[id]||0)));top.append(c);}
  top.append(btn('fb-back','',()=>showView(origin==='fantasy-book'?'home':origin)));top.lastChild.append(img('/assets/ui/win_back_btn.png'));st.append(top);
  const src=document.querySelector('.menu-explorer-bottom');if(src){const n=src.cloneNode(true);n.classList.add('fb-bnav');n.querySelectorAll('button').forEach(b=>{b.classList.remove('current');b.addEventListener('click',()=>{if(b.dataset.view)showView(b.dataset.view);else if(b.dataset.menu)openMenu(b.dataset.menu,'fantasy-book');});});st.append(n);}
  if(note)st.append(at(el('p','fb-note',note),0,-420,600,null));
  clearInterval(timer);timer=setInterval(()=>{const c=root().querySelector('.fb-count');if(!c||view!=='fantasy-book'){clearInterval(timer);return;}c.textContent=left();const rf=root().querySelector('.fb-refresh b');if(rf){const s=Math.max(0,info().refresh_day-Math.floor(Date.now()/1000));rf.textContent=[Math.floor(s/3600),Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');}},1000);}
 // shared: the level strip (Lv badge, "Current Pages", bar, n/span, + buy level)
 function levelBar(st,y){const bar=at(el('div','fb-lev'),0,y,720,101);bar.style.backgroundImage=`url('${A('battle_pass_lev_bg_new')}')`;const i=info();
  const badge=el('div','fb-lvbadge');badge.style.backgroundImage=`url('${A('battle_pass_level_text_bg')}')`;badge.append(el('small','','Lv'),el('b','',String(i.level)));bar.append(badge);
  const mid=el('div','fb-levmid');const head=el('div','fb-levhead');head.append(el('span','',i.theme==='engine'?'Bánh Răng Hiện Có':(T('BP_EXP_CURRENT')||'Trang Hiện Có')),el('b','',i.span?`${i.into}/${i.span}`:'MAX'));const pb=el('div','fb-bar');const fill=el('i');fill.style.width=(i.span?Math.min(100,i.into*100/i.span):100)+'%';pb.append(fill);mid.append(head,pb);bar.append(mid);
  const plus=btn('fb-plus','+',buyLevel,i.level>=i.max);plus.title=T('BP_BUY_LEV_WINDOW')||'Mua Cấp Sách';bar.append(plus);st.append(bar);}
 function header(st,bg,logoX,logoY,tipX,tipY,tip){st.append(at(img(A(bg),'fb-abs'),0,/exchange/.test(bg)?388:433,1000,/exchange/.test(bg)?411:406));
  if(logoX!=null){st.append(at(el('h2','fb-abs fb-logo fb-logo-vi',TH().title),logoX,logoY+(TH().logoH-215)/4,285,TH().logoH));const c=at(el('div','fb-countwrap'),logoX,logoY-92-(TH().logoH-215)/2,190,28);c.style.backgroundImage=`url('${A('battle_pass_logo_bg')}')`;c.append(el('b','fb-count',left()));st.append(c);}
  if(tip)st.append(at(el('p','fb-tip',tip),tipX,tipY,300,null));}
 // ---- Progress (battle_pass_steam_new)
 function progress(st){const i=info();header(st,TH().top,158,413);if(i.theme!=='engine')st.append(at(el('p','fb-sublogo',T('BP_SUB_LOGO')||'Thu thập Trang Sách để khôi phục Sách Kỳ Ảo'),150,296,420,null));
  const buy=at(btn('fb-buy','',luxury),166,245,276,64);buy.style.backgroundImage=`url('${A(TH().buy)}')`;buy.append(img(A('battle_pass_gift_1')),el('span','',i.theme==='engine'?"Chứng Nhận Bậc Thầy":(T('BP_PUR_BUTTON_1')||'Mở Sách Cao Cấp').replace('\n',' ')));st.append(buy);
  st.append(at(btn('fb-help','',()=>CampaignUI.popup(String(T('BP_MAIN_HELP')).replace(/\|/g,'\n')+"\n\nSách Cao Cấp và Sách Sưu Tầm là nhánh phần thưởng đặc biệt; chỉ mở khi tài khoản đủ điều kiện.",{})),-318,470,52,55));st.lastChild.append(img(A('help_2')));
  levelBar(st,152);
  const eng=i.theme==='engine';const heads=[[TH().t[0],-300,120,T('BP_LEV')||'Level'],[TH().t[1],-100,280,eng?"Chứng Nhận Thợ Máy":(T('BP_BRASS_AWARD')||'Sách Cơ Bản')],[TH().t[2],200,320,eng?"Chứng Nhận Bậc Thầy":(T('BP_SILVER_AWARD')||'Sách Cao Cấp')]];
  for(const [s,x,w,t]of heads){const h=at(el('div','fb-title'),x,72,w,64);h.style.backgroundImage=`url('${A(s)}')`;h.append(el('b','',t));st.append(h);}
  const list=at(el('div','fb-rows'),0,-226,720,540);const levels=window.FB_LEVELS||[];
  for(const row of levels){const r=el('div','fb-row'+(row.lv<=i.level?' reached':''));const lv=el('div','fb-rlv');lv.style.backgroundImage=`url('${A('battle_pass_tmp3')}')`;lv.append(el('b','',String(row.lv)));r.append(lv);
   const free=el('div','fb-rfree');const claimed=i.free.includes(row.lv),can=row.lv<=i.level&&!claimed;for(const [k,n]of pairs(row.free)){const it=item(k,n,claimed?'got':can?'can':'');if(can)it.onclick=()=>act({action:'claim',lv:row.lv},r=>{if(r?.got)CampaignUI.popup(T('BP_TITLE')||'Sách Kỳ Ảo',r.got);});free.append(it);}r.append(free);
   const paid=el('div','fb-rpaid');for(const [k,n]of pairs(row.paid)){const it=item(k,n,'locked');it.append(img(A('awake_lock'),'fb-lock'));paid.append(it);}r.append(paid);list.append(r);}
  st.append(list);const can=levels.some(r=>r.lv<=i.level&&!i.free.includes(r.lv));if(can){const ca=at(btn('fb-claimall','Nhận Tất Cả',()=>act({action:'claim_all'},r=>{if(r?.got)CampaignUI.popup(T('BP_TITLE')||'Sách Kỳ Ảo',r.got);})),-190,245,170,52);st.append(ca);}
  requestAnimationFrame(()=>{const first=list.querySelector('.fb-row:not(.reached)');if(first&&!list.dataset.scrolled){list.scrollTop=Math.max(0,first.offsetTop-list.clientHeight/2);list.dataset.scrolled='1';}});}
 // ---- Task (battle_pass_mission_new)
 function tasks(st){header(st,info().theme==='engine'?'battle_pass_top_bg_b':'battle_pass_achieve_bg_new',-157,406,175,400,T('BP_MISSION_DES'));levelBar(st,228);const i=info();
  const tabs=at(el('div','fb-subtabs'),0,148,720,55);(T('BP_MISSION_TAGS')||'Hằng Ngày|Hằng Tuần|Bổ Sung').split('|').forEach((n,k)=>{const b=btn('fb-subtab'+(sub===k?' on':''),n,()=>{sub=k;render();});b.style.backgroundImage=`url('${A(sub===k?'bp_mission_yeqina_2':'bp_mission_yeqina_1')}')`;tabs.append(b);});st.append(tabs);
  if(sub===0){const rf=at(el('div','fb-refresh'),0,100,360,40);rf.append(el('span','',T('BP_MISSION_REFRESH_TIME')||'Làm mới sau:'),el('b','',''));st.append(rf);}
  const list=at(el('div','fb-tasks'),0,sub===0?-210:-190,720,sub===0?560:600);for(const t of i.tasks.filter(t=>t.type===sub+1)){const r=el('div','fb-task'+(t.claimed?' done':''));
   const d=el('div','fb-tdesc');d.append(el('b','',window.GxbLocale?.t(t.text)||t.text));const bar=el('div','fb-tbar');const f=el('i');f.style.width=Math.min(100,t.have*100/t.need)+'%';bar.append(f,el('small','',`${t.have}/${t.need}`));d.append(bar);if(!t.tracked)d.append(el('em','',"Chưa có điều kiện tương ứng"));r.append(d);
   const aw=el('div','fb-titems');for(const [k,n]of pairs(t.award))aw.append(item(k,n));for(const [k,n]of pairs(t.pages))aw.append(item(k,n));r.append(aw);
   if(t.claimed)r.append(el('span','fb-stamp fb-stamp-vi','ĐÃ NHẬN'));else{const b=btn('fb-claim','Nhận',()=>act({action:'task',id:t.id},r=>{if(r)CampaignUI.popup(t.text,{...(r.got||{}),'117':r.pages});}),t.have<t.need);b.style.backgroundImage=`url('${A('blue_btn_54_54')}')`;r.append(b);}
   list.append(r);}st.append(list);}
 // ---- Exchange (battle_pass_exchange_new): tab_2 Crystal Leaf (left), tab_1 Floral Stamp (centre), tab_3 Flora Bookmark (right)
 function exchange(st){header(st,TH().exTop(shopTab)==='bp_exchange_top_bg'?'bp_exchange_top_bg':TH().exTop(shopTab));st.append(at(el('h2','fb-abs fb-exlogo fb-exlogo-vi',shopTab===3?'Dấu Trang Hoa':'Cửa Hàng Đổi Thưởng'),-150,434,426,184));
  st.append(at(btn('fb-help','',()=>CampaignUI.popup(String(T('BP_SHOP_HELP')).replace(/\|/g,'\n'),{})),-320,282,52,55));st.lastChild.append(img(A('help_2')));
  const nav=at(el('div','fb-shopnav'),0,210,1000,53);nav.style.backgroundImage=`url('${A('bp_mission_yeqina_bg')}')`;const names=TH().names||(T('BP_SHOP_TAGS')||'Floral Stamp|Crystal Leaf|Flora Bookmark').split('|');
  for(const [k,x]of [[2,-240],[1,0],[3,240]]){const b=at(btn('fb-stab'+(shopTab===k?' on':''),names[k-1],()=>{shopTab=k;render();}),x,0,232,55);b.style.top='0';b.style.left=`calc(${500+x-116} * var(--u))`;b.style.backgroundImage=`url('${A(shopTab===k?'bp_mission_yeqina_2':'bp_mission_yeqina_1')}')`;nav.append(b);}st.append(nav);
  const cur=info().cur[shopTab===2?1:0];const cost=at(el('div','fb-cost'),0,154,226,60);cost.style.backgroundImage=`url('${A('bp_shop_cost_bg')}')`;cost.append(img(iconOf(cur)),el('b','',number(state.items?.[cur]||0)));st.append(cost);
  if(shopTab===3){st.append(at(img(A('battle_pass_exchange_flower_bg'),'fb-abs'),0,-249,1000,812),at(img(A('bp_flower'),'fb-abs'),0,94,734,628));
   const chk=at(btn('fb-check','',odds),160,31,52,52);chk.append(img(A('white_btn_check')));st.append(chk);
   const [ck,cv]=String(window.FB_LOTTERY||'221#50').split('#');for(const [n,x]of [[1,-110],[10,110]]){const b=at(btn('fb-draw','',()=>act({action:'draw',num:n},r=>{if(r?.got)CampaignUI.popup(TH().draw,r.got);})),x,-464,191,60);b.style.backgroundImage=`url('/assets/girl-ui/blue_btn_65_65.png')`;b.append(img(iconOf(ck)),el('b','',number(Number(cv)*n)),el('small','','×'+n));st.append(b);}
   return;}
  const grid=at(el('div','fb-shop'),0,-190,720,600);const s=info().shop||{};
  for(const row of (window.FB_SHOP||[]).filter(r=>r.type===shopTab)){const bought=Number(s[row.id]||0),sold=bought>=row.limit;const c=el('div','fb-sitem'+(sold?' sold':''));c.style.backgroundImage=`url('${A(TH().sbg)}')`;
   const [ik,iv]=String(row.item).split('#');const it=item(ik,iv);c.append(el('b','fb-sname',itemCatalog?.[ik]?.name||''),it,el('small','',`Đã mua: ${bought}/${row.limit}`));
   const [ck,cv]=String(row.cost).split('#');const b=btn('fb-sbuy','',()=>act({action:'buy',id:row.id},r=>{if(r?.got)CampaignUI.popup(T('BP_TITLE')||'Sách Kỳ Ảo',r.got);}),sold);b.append(img(iconOf(ck)),el('b','',number(Number(cv))));c.append(b);grid.append(c);}
  st.append(grid);}
 async function odds(){try{const o=window.FB_ODDS||[];CampaignUI.popup(TH().draw+'\n\n'+o.map(([it,p])=>{const [k,n]=it.split('#');return (itemCatalog?.[k]?.name||k)+' ×'+n+' · '+p+'%';}).join('\n'),{});}catch(e){CampaignUI.popup(e.message,{});}}
 // ---- Trophies (battle_pass_achieve_new): the achievements, claimed through /api/missions/action
 function trophies(st){header(st,info().theme==='engine'?'battle_pass_top_bg_b':'battle_pass_achieve_bg_new',-159,421,168,420,T('BP_ACHIEVEMENT_DES'));
  const list=at(el('div','fb-tasks fb-troph'),0,-81,720,760);for(const t of (state.missions_info?.trophies||[])){const r=el('div','fb-task'+(t.done?' done':''));
   const d=el('div','fb-tdesc');d.append(el('b','',(window.GxbLocale?.t(String(t.text))||String(t.text)).replace('{1}',t.need)));const need=Number(t.need)||1,have=Number(t.have||0);const bar=el('div','fb-tbar');const f=el('i');f.style.width=Math.min(100,have*100/need)+'%';bar.append(f,el('small','',`${Math.min(have,need)}/${need}`));d.append(bar);r.append(d);
   const aw=el('div','fb-titems');for(const [k,n]of pairs(t.award).slice(0,2))aw.append(item(k,n));r.append(aw);
   if(t.done)r.append(el('span','fb-stamp fb-stamp-vi','ĐÃ NHẬN'));else{const b=btn('fb-claim','Nhận',async()=>{try{const x=await api('/api/missions/action',{action:'trophy',type:t.type});state=x.state;CampaignUI.popup('Thành Tựu',x.got||{});}catch(e){note=e.message;}render();},!t.can);b.style.backgroundImage=`url('${A('blue_btn_54_54')}')`;r.append(b);}
   list.append(r);}st.append(list);}
 // BattlePassBuyLevWindow: raise the level with Gems (discount in the last 2 weeks)
 function buyLevel(){const i=info();let n=1;const {body,close}=GirlUI.win({title:T('BP_BUY_LEV_WINDOW')||'Mua Cấp Sách',cls:'fb-buylev'});
  const draw=()=>{body.replaceChildren();const lv=window.FB_LEVELS||[];const rows=lv.filter(r=>r.lv>i.level&&r.lv<=i.level+n);const prev=el('div','fb-prev');body.append(el('b','fb-ptitle',T('BP_BUY_LEV_PREAWARD')||'Xem Trước Phần Thưởng'));
   const got={};for(const r of rows)for(const [k,v]of pairs(r.free))got[k]=(got[k]||0)+Number(v);for(const [k,v]of Object.entries(got))prev.append(item(k,v));body.append(prev);
   const ctl=el('div','fb-step');ctl.append(btn('','−',()=>{n=Math.max(1,n-1);draw();}),el('b','',`Tăng cấp từ ${i.level} lên ${i.level+n}`),btn('','+',()=>{n=Math.min(i.max-i.level,n+1);draw();}));body.append(ctl);
   const gems=rows.reduce((a,r)=>a+Number(String(i.discount?r.gems_dct:r.gems).split('#')[1]||0),0);const go=btn('gs-btn fb-gembtn','',()=>{close();act({action:'buy_level',num:n});});go.append(img(iconOf('2')),el('b','',number(gems)));body.append(go);
   body.append(el('p','fb-pnote',T('BP_BUY_LEV_TIP2')||''));};draw();}
 function luxury(){const {body}=GirlUI.win({title:(T('BP_PUR_BUTTON_1')||'Mở Sách Cao Cấp').replace('\n',' '),cls:'fb-lux'});
  body.append(el('p','fb-pnote',String(T('BP_PURCHASE_WINDOW_TIP')||'').split('\n')[0]));const got={};for(const r of (window.FB_LEVELS||[]))for(const [k,v]of pairs(r.paid))got[k]=(got[k]||0)+Number(v);
  const prev=el('div','fb-prev');for(const [k,v]of Object.entries(got).slice(0,24))prev.append(item(k,v));body.append(el('b','fb-ptitle',T('BP_SILVER_AWARD')||'Sách Cao Cấp'),prev);
  body.append(el('p','fb-pnote warn',"Nhánh Sách Cao Cấp và Sách Sưu Tầm chỉ mở khi tài khoản đáp ứng điều kiện của mùa hiện tại."));}
 return {open,render};
})();
