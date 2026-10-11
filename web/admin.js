'use strict';
window.AdminPanel=(()=>{
  let root=null,cfg=null,dash=null,worldCfg=null,active='overview';
  const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  const field=(parent,label,id,type='text',step=null)=>{const l=el('label','admin-field',label),i=document.createElement('input');i.id=id;i.type=type;if(step)i.step=step;l.append(i);parent.append(l);return i;};
  const textarea=(parent,label,id,placeholder='')=>{const l=el('label','admin-field',label),i=document.createElement('textarea');i.id=id;i.placeholder=placeholder;l.append(i);parent.append(l);return i;};
  const btn=(text,fn,cls='')=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
  function status(t,ok=true){const n=document.getElementById('admin-status');if(n){n.textContent=t||'';n.dataset.ok=ok?'1':'0';}}
  function card(title){const c=el('section','admin-card');c.append(el('h2','',title));return c;}
  function ensure(){
    if(root)return root;
    root=el('section','admin-view');root.id='admin-view';root.hidden=true;
    const head=el('header','admin-head');head.append(btn('← Game',close),el('div','admin-title-wrap'),btn('Thoát QTV',logout,'danger'));
    head.querySelector('.admin-title-wrap').append(el('small','','SUPER GM'),el('h1','','Hệ Thống QTV · Nữ Thần Chiến Đấu - GXB 3'));
    root.append(head);

    const nav=el('nav','admin-nav');
    [['overview','Tổng quan'],['mail','Gửi thư'],['orders','Đơn nạp'],['players','Người chơi'],['worlds','Server'],['config','Cấu hình'],['tools','GM Tools'],['audit','Audit']].forEach(([id,label])=>{
      const b=btn(label,()=>show(id),'admin-tab');b.dataset.tab=id;nav.append(b);
    });
    root.append(nav);

    const body=el('div','admin-body');body.id='admin-body';root.append(body);
    const footer=el('div','admin-footer');footer.append(el('p','admin-status',''));footer.firstChild.id='admin-status';root.append(footer);
    document.getElementById('game-root').append(root);
    return root;
  }
  async function refreshDashboard(){dash=await api('/api/admin/dashboard');}
  function show(id){active=id;for(const b of root.querySelectorAll('.admin-tab'))b.classList.toggle('on',b.dataset.tab===id);render();}
  function render(){const body=document.getElementById('admin-body');if(!body)return;body.replaceChildren();
    const fn={overview:renderOverview,mail:renderMail,orders:renderOrders,players:renderPlayers,worlds:renderWorlds,config:renderConfig,tools:renderTools,audit:renderAudit}[active]||renderOverview;fn(body);
  }
  function renderOverview(body){
    const grid=el('div','admin-grid');
    const stats=card('Trạng thái hệ thống');
    const values=[['Server',dash?.worlds?.length||0],['Online',dash?.online?.length||0],['Tài khoản',dash?.accounts?.length||0],['Đơn chờ duyệt',(dash?.orders||[]).filter(x=>x.status==='pending').length]];
    const row=el('div','admin-stats');for(const [k,v] of values){const s=el('div','admin-stat');s.append(el('b','',String(v)),el('small','',k));row.append(s);}stats.append(row,el('p','admin-note','SUPER GM có quyền quản lý server, khóa/mở tài khoản, duyệt đơn nạp và gửi vật phẩm trực tiếp qua thư theo UID + Server + Tên Nhân Vật.'));
    grid.append(stats);
    const me=card('Player đang mở');me.append(el('p','',`UID: ${state?.uid||'-'}`),el('p','',`Server: ${state?.server_id||'-'}`),el('p','',`Tên Nhân Vật: ${state?.name||'-'}`),el('p','',`Trạng thái: ${state?.account_status||'active'}`));grid.append(me);
    body.append(grid);
  }
  function renderMail(body){
    const c=card('GM Mail · gửi bất kỳ vật phẩm qua UID + Server + Tên Nhân Vật');
    field(c,'UID','gm-mail-uid');field(c,'Server','gm-mail-server').value='S1';field(c,'Tên Nhân Vật','gm-mail-name');
    field(c,'Tiêu đề','gm-mail-title').value='Quà từ GM';
    textarea(c,'Nội dung','gm-mail-body','Thông báo gửi người chơi...');
    textarea(c,'Vật phẩm JSON','gm-mail-items','{"2":1000,"1":500000}');
    c.append(btn('Gửi thư ngay',sendMail,'primary'));body.append(c);
  }
  async function sendMail(){try{
    const payload={uid:val('gm-mail-uid'),server_id:val('gm-mail-server'),character_name:val('gm-mail-name'),title:val('gm-mail-title'),body:val('gm-mail-body'),attachments:JSON.parse(val('gm-mail-items')||'{}')};
    const r=await api('/api/admin/mail/send',payload);status('Đã gửi '+r.id);await refreshDashboard();
  }catch(e){status(e.message,false);}}
  function renderOrders(body){
    const c=card('Duyệt đơn nạp');
    const list=el('div','admin-list');const orders=dash?.orders||[];
    if(!orders.length)list.append(el('p','admin-note','Chưa có đơn nạp.'));
    for(const o of orders){const row=el('article','admin-row');const info=el('div','admin-row-main');
      info.append(el('b','',o.id),el('span','',`${o.server_id} · ${o.uid} · ${o.character_name}`),el('small','',`${o.package||'(chưa ghi gói)'} · ${o.status}`));
      row.append(info);
      if(o.status==='pending'){const reward=document.createElement('input');reward.placeholder='Reward JSON, vd {"2":1000}';reward.className='admin-inline-json';
        row.append(reward,btn('Duyệt',()=>reviewOrder(o.id,'approve',reward.value),'primary'),btn('Từ chối',()=>reviewOrder(o.id,'reject',''),'danger'));
      }else row.append(el('small','',o.reviewed_at?'Đã xử lý':''));
      list.append(row);
    }c.append(list);body.append(c);
  }
  async function reviewOrder(id,action,rewardText){try{
    const reward=action==='approve'?JSON.parse(rewardText||'{}'):{};
    await api('/api/admin/order/review',{order_id:id,action,reward});status(action==='approve'?'Đã duyệt đơn và gửi thưởng qua thư.':'Đã từ chối đơn.');await refreshDashboard();render();
  }catch(e){status(e.message,false);}}
  function renderPlayers(body){
    const c=card('Quản lý tài khoản');
    const search=field(c,'Tìm UID / Server / Tên Nhân Vật','gm-player-search');search.oninput=()=>drawPlayers(c,search.value);
    const holder=el('div','admin-list');holder.id='gm-player-list';c.append(holder);body.append(c);drawPlayers(c,'');
  }
  function drawPlayers(c,q){
    const holder=c.querySelector('#gm-player-list');if(!holder)return;holder.replaceChildren();
    const needle=String(q||'').toLowerCase();
    for(const p of (dash?.players||[]).filter(x=>!needle||[x.uid,x.server_id,x.character_name].some(v=>String(v).toLowerCase().includes(needle)))){
      const row=el('article','admin-row');const info=el('div','admin-row-main');info.append(el('b','',p.character_name),el('span','',`${p.server_id} · ${p.uid}`),el('small','',p.status+(p.ban_reason?' · '+p.ban_reason:'')));row.append(info);
      if(p.status==='banned')row.append(btn('Unban Server',()=>playerStatus(p,'unban'),'primary'));
      else row.append(btn('Ban Server',()=>playerStatus(p,'ban'),'danger'));
      const account=(dash?.accounts||[]).find(a=>a.uid===p.uid);
      if(account?.status==='banned')row.append(btn('Unban Account',()=>accountStatus(p,'unban'),'primary'));
      else row.append(btn('Ban Account',()=>accountStatus(p,'ban'),'danger'));
      row.append(btn('Phiên',()=>viewSessions(p.uid)),btn('Thu hồi phiên',()=>revokeSessions(p.uid)));
      holder.append(row);
    }
  }
  async function playerStatus(p,action){try{
    const reason=action==='ban'?(prompt('Lý do ban ở server '+p.server_id+':','Vi phạm quy định')||'Vi phạm quy định'):'';
    await api('/api/admin/player/status',{uid:p.uid,server_id:p.server_id,action,reason});status(action==='ban'?'Đã ban nhân vật ở server này.':'Đã unban nhân vật ở server này.');await refreshDashboard();render();
  }catch(e){status(e.message,false);}}
  async function accountStatus(p,action){try{
    const reason=action==='ban'?(prompt('Lý do khóa toàn tài khoản:','Vi phạm nghiêm trọng')||'Vi phạm nghiêm trọng'):'';
    await api('/api/admin/account/status',{uid:p.uid,action,reason});status(action==='ban'?'Đã khóa toàn tài khoản và thu hồi phiên đăng nhập.':'Đã mở khóa tài khoản.');await refreshDashboard();render();
  }catch(e){status(e.message,false);}}
  async function revokeSessions(uid){try{
    const r=await api('/api/admin/account/revoke-sessions',{uid});status('Đã thu hồi '+(r.revoked||0)+' phiên đăng nhập của '+uid+'.');await refreshDashboard();
  }catch(e){status(e.message,false);}}
  async function viewSessions(uid){try{
    const data=await api('/api/admin/account/sessions',{uid});
    const modal=el('div','admin-modal'),box=el('section','admin-modal-box');box.append(el('h3','','Phiên đăng nhập · '+uid));
    const list=el('div','admin-list');
    for(const ss of data.sessions||[]){const row=el('article','admin-row');const info=el('div','admin-row-main');
      info.append(el('b','',ss.session_id||'Session'),el('span','',ss.user_agent||'Không rõ thiết bị'),el('small','',ss.server_id+' · '+(ss.remote_addr||'-')+' · '+new Date(ss.last_seen*1000).toLocaleString()));row.append(info);list.append(row);}
    if(!(data.sessions||[]).length)list.append(el('p','admin-note','Không có phiên hoạt động.'));
    box.append(list,btn('Thu hồi tất cả',async()=>{await revokeSessions(uid);modal.remove();},'danger'),btn('Đóng',()=>modal.remove()));
    modal.append(box);document.body.append(modal);
  }catch(e){status(e.message,false);}}
  function renderWorlds(body){
    const c=card('World / Multi-server');
    const create=el('div','admin-form-row');const sid=document.createElement('input');sid.id='gm-world-id';sid.placeholder='S2';const name=document.createElement('input');name.id='gm-world-name';name.placeholder='Server 2';create.append(sid,name,btn('Tạo server',createWorld,'primary'));c.append(create);
    const list=el('div','admin-list');for(const w of dash?.worlds||[]){const row=el('article','admin-row admin-world-row');const info=el('div','admin-row-main');info.append(el('b','',w.name),el('span','',w.server_id),el('small','',w.status+(w.message?' · '+w.message:'')));row.append(info);
      const select=document.createElement('select');for(const st of ['online','maintenance','closed']){const o=el('option','',st);o.value=st;o.selected=st===w.status;select.append(o);}select.onchange=()=>worldStatus(w.server_id,select.value);row.append(select);
      const reg=document.createElement('label');reg.className='admin-check';const regCb=document.createElement('input');regCb.type='checkbox';regCb.checked=!!Number(w.registration_open??1);reg.append(regCb,document.createTextNode('Đăng ký'));row.append(reg);
      const createCbWrap=document.createElement('label');createCbWrap.className='admin-check';const createCb=document.createElement('input');createCb.type='checkbox';createCb.checked=!!Number(w.character_creation_open??1);createCbWrap.append(createCb,document.createTextNode('Tạo NV'));row.append(createCbWrap);
      const msg=document.createElement('input');msg.className='admin-world-message';msg.placeholder='Thông báo / lý do';msg.value=w.message||'';row.append(msg);
      row.append(btn('Lưu policy',()=>worldPolicy(w.server_id,regCb.checked,createCb.checked,msg.value),'primary'));list.append(row);}c.append(list);body.append(c);
  }
  async function createWorld(){try{await api('/api/admin/world',{action:'create',server_id:val('gm-world-id'),name:val('gm-world-name')});status('Đã tạo server.');await refreshDashboard();render();}catch(e){status(e.message,false);}}
  async function worldStatus(server_id,statusValue){try{await api('/api/admin/world',{action:'status',server_id,status:statusValue});status('Đã cập nhật '+server_id+'.');await refreshDashboard();render();}catch(e){status(e.message,false);}}
  async function worldPolicy(server_id,registration_open,character_creation_open,message){try{
    await api('/api/admin/world',{action:'policy',server_id,registration_open,character_creation_open,message});status('Đã lưu policy '+server_id+'.');await refreshDashboard();render();
  }catch(e){status(e.message,false);}}
  function renderConfig(body){
    const grid=el('div','admin-grid');
    const res=card('Tài nguyên & Nữ Thần khởi đầu');const ta=textarea(res,'starting_resources (JSON)','admin-resources');ta.value=JSON.stringify(cfg.starting_resources,null,2);field(res,'Starter Girls (ID)','admin-starters').value=cfg.starter_girls.join(',');grid.append(res);
    const summon=card('Tỷ lệ Triệu Hồi toàn game');for(const star of [1,2,3,4,5,6]){const i=field(summon,`${star}★ multiplier`,`admin-star-${star}`,'number','0.1');i.value=cfg.summon_rate.star_multiplier[String(star)]??1;}grid.append(summon);
    const economy=card('Kinh tế toàn game');field(economy,'Giá Shop ×','admin-shop','number','0.1').value=cfg.shop.price_multiplier;field(economy,'Phần thưởng ×','admin-reward','number','0.1').value=cfg.rewards.multiplier;field(economy,'Chi phí progression ×','admin-progress','number','0.1').value=cfg.progression.cost_multiplier;grid.append(economy);
    const actions=card('Áp dụng cấu hình toàn game');actions.append(btn('Lưu cấu hình',saveConfig,'primary'),btn('Khôi phục mặc định',resetConfig,'danger'));grid.append(actions);

    const world=card('World Live Config · Shop / Event Shop / Event / Summon');
    const select=document.createElement('select');select.id='admin-world-live-server';
    for(const w of dash?.worlds||[]){const o=el('option','',w.server_id+' · '+w.name);o.value=w.server_id;select.append(o);}
    select.onchange=()=>loadWorldConfig(select.value);world.append(select);
    field(world,'Shop giá ×','admin-world-shop','number','0.1').value='1';
    field(world,'Event Shop giá ×','admin-world-event-shop','number','0.1').value='1';
    field(world,'Event reward ×','admin-world-event-reward','number','0.1').value='1';
    field(world,'Shop ID tạm đóng (cách nhau dấu phẩy)','admin-world-disabled-shops').value='';
    const flags=el('div','admin-form-row');
    const checkin=document.createElement('label');checkin.className='admin-check';const checkinCb=document.createElement('input');checkinCb.type='checkbox';checkinCb.id='admin-world-checkin';checkinCb.checked=true;checkin.append(checkinCb,document.createTextNode('Điểm danh'));
    const seven=document.createElement('label');seven.className='admin-check';const sevenCb=document.createElement('input');sevenCb.type='checkbox';sevenCb.id='admin-world-seven';sevenCb.checked=true;seven.append(sevenCb,document.createTextNode('Quà 7 ngày'));flags.append(checkin,seven);world.append(flags);
    const stars=el('div','admin-form-row');for(const star of [1,2,3,4,5,6]){const wrap=el('label','admin-field',star+'★ ×');const input=document.createElement('input');input.type='number';input.step='0.1';input.id='admin-world-star-'+star;input.value='1';wrap.append(input);stars.append(wrap);}world.append(stars);
    world.append(btn('Lưu World Live Config',saveWorldConfig,'primary'),btn('Reset World Config',resetWorldConfig,'danger'));
    grid.append(world);body.append(grid);
    if(select.value)loadWorldConfig(select.value);
  }
  async function loadWorldConfig(serverId){try{
    const out=await api('/api/admin/world-config?server_id='+encodeURIComponent(serverId));
    worldCfg=out.config||{};
    const shop=worldCfg.shop||{},eventShop=worldCfg.event_shop||{},eventRewards=worldCfg.event_rewards||{},stars=(worldCfg.summon_rate||{}).star_multiplier||{};
    const set=(id,v)=>{const n=document.getElementById(id);if(n)n.value=String(v??'');};
    set('admin-world-shop',shop.price_multiplier??1);
    set('admin-world-event-shop',eventShop.price_multiplier??1);
    set('admin-world-event-reward',eventRewards.multiplier??1);
    set('admin-world-disabled-shops',(shop.disabled_shop_ids||[]).join(','));
    const ci=document.getElementById('admin-world-checkin');if(ci)ci.checked=eventRewards.checkin_enabled!==false;
    const sv=document.getElementById('admin-world-seven');if(sv)sv.checked=eventRewards.sevenday_enabled!==false;
    for(const star of [1,2,3,4,5,6])set('admin-world-star-'+star,stars[String(star)]??1);
    status('Đã tải World Live Config '+out.server_id+'.');
  }catch(e){status(e.message,false);}}
  async function saveWorldConfig(){try{
    const server_id=val('admin-world-live-server')||'S1';
    const config={
      shop:{price_multiplier:Number(val('admin-world-shop')||1),disabled_shop_ids:val('admin-world-disabled-shops').split(',').map(x=>Number(x.trim())).filter(x=>Number.isInteger(x)&&x>0)},
      event_shop:{price_multiplier:Number(val('admin-world-event-shop')||1)},
      event_rewards:{multiplier:Number(val('admin-world-event-reward')||1),checkin_enabled:!!document.getElementById('admin-world-checkin')?.checked,sevenday_enabled:!!document.getElementById('admin-world-seven')?.checked},
      summon_rate:{star_multiplier:Object.fromEntries([1,2,3,4,5,6].map(star=>[String(star),Number(val('admin-world-star-'+star)||1)]))}
    };
    const out=await api('/api/admin/world-config',{action:'save',server_id,config});
    worldCfg=out.config;status('Đã áp dụng Live Config riêng cho '+out.server_id+'.');
  }catch(e){status(e.message,false);}}
  async function resetWorldConfig(){try{
    const server_id=val('admin-world-live-server')||'S1';
    const out=await api('/api/admin/world-config',{action:'reset',server_id});
    worldCfg=out.config;await loadWorldConfig(server_id);status('Đã reset World Live Config '+out.server_id+'.');
  }catch(e){status(e.message,false);}}
  async function saveConfig(){try{const raw={starting_resources:JSON.parse(val('admin-resources')),starter_girls:val('admin-starters').split(',').map(x=>Number(x.trim())).filter(Boolean),summon_rate:{star_multiplier:Object.fromEntries([1,2,3,4,5,6].map(s=>[String(s),Number(val(`admin-star-${s}`))]))},shop:{price_multiplier:Number(val('admin-shop'))},rewards:{multiplier:Number(val('admin-reward'))},progression:{cost_multiplier:Number(val('admin-progress'))}};cfg=await api('/api/admin/config',raw);status('Đã lưu cấu hình.');}catch(e){status(e.message,false);}}
  async function resetConfig(){try{cfg=await api('/api/admin/config',{action:'reset'});status('Đã khôi phục mặc định.');render();}catch(e){status(e.message,false);}}
  function renderTools(body){
    const tools=card('SUPER GM Tools');const grid=el('div','admin-tools');
    const girl=el('div','admin-tool');const sel=document.createElement('select');sel.id='admin-girl';for(const g of girlsCatalog){const o=el('option','',`${g.name} · ${g.stars}★ · ${g.id}`);o.value=g.id;sel.append(o);}girl.append(sel);const count=field(girl,'Số lượng','admin-count','number','1');count.value=1;const level=field(girl,'Cấp','admin-level','number','1');level.value=80;girl.append(btn('Thêm Nữ Thần',()=>act('girl'),'primary'));grid.append(girl);
    const misc=el('div','admin-tool');[['all_girls','Thêm toàn bộ Nữ Thần'],['max_stars','Nữ Thần đã chọn → 15★'],['levels','Áp cấp cho toàn bộ'],['campaign','Mở 30 ải']].forEach(([a,t])=>misc.append(btn(t,()=>act(a))));const floor=field(misc,'Tầng Tests','admin-floor','number','1');floor.value=1;misc.append(btn('Đặt tầng Tests',()=>act('tower')));grid.append(misc);

    const live=el('div','admin-tool');
    live.append(el('h3','','Live Service · Quyền tối thượng'));
    field(live,'UID','admin-live-uid');
    field(live,'Server','admin-live-server').value='S1';
    const mode=document.createElement('select');mode.id='admin-live-mode';for(const m of ['arena','team','cross']){const o=el('option','',m);o.value=m;mode.append(o);}live.append(mode);
    field(live,'PvP Rating','admin-live-rating','number','1').value=1000;
    live.append(btn('Đặt PvP Rating',()=>liveServiceAct('pvp_rating'),'primary'));
    field(live,'Guild EXP +','admin-live-guild-exp','number','1').value=0;
    field(live,'Contribution +','admin-live-contribution','number','1').value=0;
    live.append(btn('Cộng Guild Progress',()=>liveServiceAct('guild_progress'),'primary'));
    field(live,'Guild War ID','admin-live-war');
    live.append(btn('Force Settle Guild War',()=>liveServiceAct('force_settle_war'),'danger'));
    live.append(btn('Chạy Maintenance ngay',()=>liveServiceAct('maintenance')));
    grid.append(live);

    tools.append(grid);body.append(tools);
  }
  async function act(action){try{const data=await api('/api/developer',{action,table_id:Number(val('admin-girl')),count:Number(val('admin-count')),level:Number(val('admin-level')),floor:Number(val('admin-floor'))});state=data.state;loadFormation();renderGame();status('Đã áp dụng vào save QTV.');}catch(e){status(e.message,false);}}
  async function liveServiceAct(action){try{
    const payload={action,uid:val('admin-live-uid'),server_id:val('admin-live-server')||'S1',
      mode:val('admin-live-mode')||'arena',rating:Number(val('admin-live-rating')||0),
      exp_gain:Number(val('admin-live-guild-exp')||0),contribution_gain:Number(val('admin-live-contribution')||0),
      war_id:val('admin-live-war')};
    const result=await api('/api/admin/live-service',payload);
    status('SUPER GM đã áp dụng: '+action+'.');await refreshDashboard();
    return result;
  }catch(e){status(e.message,false);}}
  function renderGame(){if(typeof window.render==='function')window.render();}
  function renderAudit(body){const c=card('Audit Log');const list=el('div','admin-list');for(const a of dash?.audit||[]){const row=el('article','admin-row');const info=el('div','admin-row-main');info.append(el('b','',a.action),el('span','',a.target),el('small','',new Date(a.at*1000).toLocaleString()+' · '+a.operator));row.append(info);list.append(row);}c.append(list);body.append(c);}
  const val=id=>document.getElementById(id)?.value?.trim()||'';
  async function load(){try{ensure();[cfg,dash]=await Promise.all([api('/api/admin/config'),api('/api/admin/dashboard')]);show(active);status('Hệ Thống QTV đã sẵn sàng.');}catch(e){status(e.message,false);}}
  async function open(){ensure();root.hidden=false;await load();}
  function close(){if(root)root.hidden=true;showView('home');}
  async function logout(){developerMode=false;adminKey='';sessionStorage.setItem('gxb2-developer','0');sessionStorage.removeItem('gxb2-admin-key');if(root)root.hidden=true;state=await api('/api/state');loadFormation();showView('home');renderGame();}
  return{open,close,load,logout};
})();
