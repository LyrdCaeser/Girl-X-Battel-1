'use strict';
window.AdminPanel=(()=>{
  let root=null,cfg=null,dash=null,worldCfg=null,topupCfg=null,active='overview';
  let giftCatalog=null,giftBasket={},giftKey='',recipient=null,catalogSearch='',catalogPage=0;
  const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  const field=(parent,label,id,type='text',step=null)=>{const l=el('label','admin-field',label),i=document.createElement('input');i.id=id;i.type=type;if(step)i.step=step;l.append(i);parent.append(l);return i;};
  const textarea=(parent,label,id,placeholder='')=>{const l=el('label','admin-field',label),i=document.createElement('textarea');i.id=id;i.placeholder=placeholder;l.append(i);parent.append(l);return i;};
  const btn=(text,fn,cls='')=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
  function status(t,ok=true){const n=document.getElementById('admin-status');if(n){n.textContent=t||'';n.dataset.ok=ok?'1':'0';}}
  function card(title){const c=el('section','admin-card');c.append(el('h2','',title));return c;}
  function ensure(){
    if(root)return root;
    root=el('section','admin-view');root.id='admin-view';root.hidden=true;
    const head=el('header','admin-head');head.append(btn('← Game',close),el('div','admin-title-wrap'),btn('Đóng GM Tools',close,'danger'));
    head.querySelector('.admin-title-wrap').append(el('small','','SUPER GM'),el('h1','','Hệ Thống QTV · Nữ Thần Chiến Đấu - GXB 3'));
    root.append(head);

    const nav=el('nav','admin-nav');
    [['overview','Tổng quan'],['players','Người chơi'],['mail','Gửi thư'],['currency','Tiền tệ'],['items','Vật phẩm'],['shards','Mảnh nhân vật'],['orders','Đơn nạp'],['worlds','Server'],['config','Cấu hình'],['audit','Audit']].forEach(([id,label])=>{
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
    const fn={overview:renderOverview,mail:renderMail,currency:renderCurrency,items:renderItems,shards:renderShards,orders:renderOrders,players:renderPlayers,worlds:renderWorlds,config:renderConfig,audit:renderAudit}[active]||renderOverview;fn(body);
  }
  function renderOverview(body){
    const grid=el('div','admin-grid');
    const stats=card('Trạng thái hệ thống');
    const values=[['Server',dash?.worlds?.length||0],['Online',dash?.online?.length||0],['Tài khoản',dash?.accounts?.length||0],['Đơn chờ duyệt',(dash?.orders||[]).filter(x=>x.status==='pending').length]];
    const row=el('div','admin-stats');for(const [k,v] of values){const s=el('div','admin-stat');s.append(el('b','',String(v)),el('small','',k));row.append(s);}stats.append(row,el('p','admin-note','SUPER GM có quyền quản lý server, khóa/mở tài khoản, duyệt đơn nạp và gửi vật phẩm trực tiếp qua thư theo UID + Server + Tên Nhân Vật.'));
    grid.append(stats);
    const me=card('Player đang mở');me.append(el('p','',`UID: ${state?.uid||'-'}`),el('p','',`Server: ${state?.server_id||'-'}`),el('p','',`Tên Nhân Vật: ${state?.name||'-'}`),el('p','',`Trạng thái: ${state?.account_status||'active'}`));grid.append(me);
    body.append(grid);
    const tests=card('Kiểm tra SUPER GM & Bang Hội (chỉ đọc)');
    const trigger=btn('Kiểm tra trực tiếp trên máy chủ',async()=>{
      trigger.disabled=true;
      const results=[];
      try{
        const me=await api('/api/auth/me');
        const owner=!!me.is_super_gm;
        results.push((owner?'PASS':'FAIL')+' · Quyền SUPER GM của tài khoản đăng nhập');
        if(!owner)throw Error('Máy chủ không xác nhận tài khoản SUPER GM');
        const admin=await api('/api/admin/dashboard');
        results.push('PASS · API QTV (thế giới: '+(admin.worlds||[]).length+', tài khoản: '+(admin.accounts||[]).length+')');
        const guild=await api('/api/world-guild');
        results.push('PASS · Bang Hội Online (bang hội: '+(guild.guilds||[]).length+', chiến tranh: '+(guild.wars||[]).length+')');
      }catch(e){results.push('FAIL · '+(e.message||String(e)));}
      finally{trigger.disabled=false;log.textContent=results.join('\n');}
    },'primary');
    const log=el('pre','admin-note','Chưa chạy kiểm tra.');
    log.style.whiteSpace='pre-wrap';
    tests.append(trigger,log);body.append(tests);
  }
  function amount(value) {
    const n=Number(value);
    if(!Number.isSafeInteger(n)||n<1||n>2000000)throw Error('Số lượng phải từ 1 đến 2.000.000');
    return n;
  }
  function giftPic(src,name) {
    const img=el('img','admin-gift-image');img.src=src;img.alt=name||'';
    img.loading='lazy';return img;
  }
  function basketPanel(){
    const panel=el('section','admin-basket');
    panel.append(el('h3','','Quà đã chọn'));
    const entries=Object.entries(giftBasket);
    if(!entries.length)panel.append(el('p','admin-note','Chưa chọn vật phẩm nào.'));
    for(const [id,quantity] of entries){
      const item=id==='999999991'?{name:'VIP EXP (chỉ nhận qua thư)',image:'/assets/events/check_in_pop_up_vip_level_bg.png'}:[...(giftCatalog?.items||[]),...(giftCatalog?.shards||[])].find(x=>String(x.id)===id);
      const entry=el('div','admin-basket-row');
      if(item?.image)entry.append(giftPic(item.image,item.name));
      entry.append(el('span','',(item?.name||'Vật phẩm')+' · ID '+id+' · ×'+quantity));
      entry.append(btn('Bỏ',()=>{delete giftBasket[id];render();}));
      panel.append(entry);
    }
    panel.append(btn('Xóa danh sách quà',()=>{giftBasket={};render();},'admin-secondary'));
    panel.append(btn('Đến Gửi Thư',()=>show('mail'),'primary'));
    return panel;
  }
  function addGift(row,quantity){
    try{
      const id=String(row.id),qty=amount(quantity);
      const available=[...(giftCatalog?.items||[]),...(giftCatalog?.shards||[])];
      if(!available.some(x=>String(x.id)===id))throw Error('Không tìm thấy vật phẩm trong danh mục thật');
      const next=(giftBasket[id]||0)+qty;
      if(next>2000000)throw Error('Giới hạn 2.000.000 mỗi loại quà');
      giftBasket[id]=next;
      status('Đã thêm '+qty+' × '+row.name+' vào thư.');
      render();
    }catch(e){status(e.message,false);}
  }
  function giftCards(body,kind){
    const title=kind==='shards'?'Mảnh Nhân Vật':kind==='currency'?'Tiền Tệ':'Vật Phẩm';
    const panel=card(title+' · chọn quà có ảnh gốc');
    if(!giftCatalog){panel.append(el('p','admin-note','Chưa tải danh mục quà từ máy chủ.'));body.append(panel);return;}
    const filter=el('input');filter.placeholder='Tìm theo tên hoặc ID';filter.type='search';filter.value=catalogSearch;
    filter.oninput=()=>{catalogSearch=filter.value;catalogPage=0;draw();};panel.append(filter);
    const grid=el('div','admin-gift-grid');panel.append(grid);
    const pagination=el('div','admin-pagination');panel.append(pagination);
    body.append(panel,basketPanel());
    function draw(){
      grid.replaceChildren();pagination.replaceChildren();
      const search=catalogSearch.toLocaleLowerCase('vi-VN');
      const all=(kind==='shards'?giftCatalog.shards:giftCatalog.items.filter(x=>kind==='currency'?Number(x.category)===0:Number(x.category)!==0));
      const matched=all.filter(x=>!search||String(x.id).includes(search)||String(x.name).toLocaleLowerCase('vi-VN').includes(search));
      const pageSize=24,pages=Math.max(1,Math.ceil(matched.length/pageSize));
      catalogPage=Math.max(0,Math.min(catalogPage,pages-1));
      const rows=matched.slice(catalogPage*pageSize,(catalogPage+1)*pageSize);
      if(!rows.length)grid.append(el('p','admin-note','Không có vật phẩm phù hợp có ảnh gốc.'));
      for(const row of rows){
        const tile=el('article','admin-gift-card');
        tile.append(giftPic(row.image,row.name));
        const details=el('div','admin-gift-details');
        details.append(el('b','',row.name),el('small','','ID '+row.id));
        details.append(el('small','',kind==='shards'?'Sao gốc: '+row.stars+'★ · ID nhân vật: '+row.girl_id+' · '+row.required+' mảnh để ghép':'Phẩm chất '+row.quality));
        tile.append(details);
        const qty=document.createElement('input');qty.type='number';qty.min='1';qty.max='2000000';qty.step='1';
        qty.value=kind==='shards'?'50':'1';qty.setAttribute('aria-label','Số lượng '+row.name);
        tile.append(qty,btn('Thêm vào thư',()=>addGift(row,qty.value),'primary'));grid.append(tile);
      }
      pagination.append(btn('← Trước',()=>{catalogPage--;draw();},'admin-secondary'),
        el('small','',String(catalogPage+1)+' / '+pages+' · '+matched.length+' mục'),
        btn('Tiếp →',()=>{catalogPage++;draw();},'admin-secondary'));
      pagination.firstElementChild.disabled=catalogPage===0;
      pagination.lastElementChild.disabled=catalogPage>=pages-1;
    }
    draw();
  }
  function renderCurrency(body){
    // Reserved mail-only reward. This is not spendable inventory currency.
    const vip=card('VIP EXP · chỉ cộng khi người nhận xác nhận Hòm Thư');
    const tile=el('div','admin-gift-card');
    tile.append(giftPic('/assets/events/check_in_pop_up_vip_level_bg.png','VIP'));
    const desc=el('div','admin-gift-details');
    desc.append(el('b','','Điểm VIP (EXP VIP)'),el('small','','Mã thưởng nội bộ: 999999991'),
       el('small','','Được cộng đúng một lần cho UID/Server khi nhận thư. Không cộng từ nhiệm vụ.'));
    tile.append(desc);
    const q=document.createElement('input');q.type='number';q.step='1';q.min='1';q.max='2000000';q.value='100';
    q.setAttribute('aria-label','Số VIP EXP');tile.append(q);
    tile.append(btn('Thêm VIP EXP vào thư',()=>{
      try{const count=amount(q.value);const id='999999991';
        if((giftBasket[id]||0)+count>2000000)throw Error('VIP EXP vượt giới hạn');
        giftBasket[id]=(giftBasket[id]||0)+count;
        status('Đã chọn '+count+' VIP EXP. Chỉ gửi cho UID đã xác minh qua thư.');
        render();
      }catch(e){status(e.message,false);}
    },'primary'));
    vip.append(tile);body.append(vip);giftCards(body,'currency');
  }
  const renderItems=body=>giftCards(body,'items');
  const renderShards=body=>giftCards(body,'shards');
  async function verifyGiftKey(){
    const input=document.getElementById('gm-action-key');
    const key=input?.value||'';
    if(!key){status('Vui lòng nhập khóa QTV.',false);return;}
    try{
      const r=await fetch('/api/admin/gm/verify-key',{method:'POST',credentials:'same-origin',
        headers:{'Content-Type':'application/json','X-GXB3-GM-Key':key},body:'{}'});
      const payload=await r.json();
      if(!r.ok||!payload.verified)throw Error(payload.error||'Không xác thực được khóa QTV.');
      giftKey=key;status('Đã xác thực khóa QTV.');render();
    }catch(e){giftKey='';status(e.message,false);}
  }
  // GM actions that move paid rewards or change a published package require the
  // same volatile second factor as sending player mail (never localStorage).
  async function gmAction(path,data){
    if(!giftKey)throw Error('Chưa xác thực khóa QTV. Vào tab Gửi thư để xác thực trước khi duyệt đơn hoặc sửa gói nạp.');
    const response=await fetch(path,{method:'POST',credentials:'same-origin',
      headers:{'Content-Type':'application/json','X-GXB3-GM-Key':giftKey},
      body:JSON.stringify(data)});
    const result=await response.json();
    if(!response.ok)throw Error(result.error||'Máy chủ từ chối thao tác QTV.');
    return result;
  }
  function renderMail(body){
    const c=card('Gửi quà qua Hòm Thư · xác nhận UID trước khi gửi');
    const key=field(c,'Khóa QTV (không lưu vào thiết bị)','gm-action-key','password');key.autocomplete='off';
    if(giftKey)key.placeholder='Đã xác thực, để trống nếu không đổi khóa';
    c.append(btn('Xác thực khóa QTV',verifyGiftKey,'primary'));
    c.append(el('p','admin-note',giftKey?'Đã xác thực khóa QTV. Vẫn cần đúng UID và tên nhân vật.':'Cần khóa riêng trên VPS và phiên đăng nhập SUPER GM.'));
    const uid=field(c,'UID người nhận','gm-mail-uid');
    const sid=field(c,'Máy chủ','gm-mail-server');sid.value=recipient?.server_id||state?.server_id||'S1';
    const name=field(c,'Tên nhân vật (đối chiếu UID)','gm-mail-name');
    if(recipient){uid.value=recipient.uid;name.value=recipient.character_name;uid.readOnly=true;sid.readOnly=true;name.readOnly=true;}
    const confirm=el('p','admin-note',recipient?'Đã chọn: '+recipient.character_name+' · '+recipient.uid+' · '+recipient.server_id:'Hãy chọn người nhận trong tab Người Chơi trước khi gửi.');
    c.append(confirm);
    field(c,'Tiêu đề','gm-mail-title').value='Quà từ GM';
    textarea(c,'Nội dung','gm-mail-body','Lời nhắn gửi đến người chơi...');
    c.append(basketPanel());
    c.append(btn('Xem trước thư',previewMail,'admin-secondary'));
    const send=btn('Gửi thư ngay',sendMail,'primary');send.id='gm-send-button';c.append(send);
    body.append(c);
  }
  function previewMail(){
    const matches=(dash?.players||[]).filter(p=>p.uid===val('gm-mail-uid')&&p.server_id===val('gm-mail-server'));
    if(matches.length!==1||matches[0].character_name!==val('gm-mail-name')){
      status('UID / Server / Tên Nhân Vật không khớp danh sách thật.',false);return;
    }
    const modal=el('div','admin-modal'),box=el('section','admin-modal-box');
    box.append(el('h3','','Xác nhận gửi quà đến '+matches[0].character_name),
      el('p','','UID '+matches[0].uid+' · '+matches[0].server_id),el('p','',val('gm-mail-title')),
      el('p','',val('gm-mail-body')),basketPanel());
    box.append(btn('Đóng',()=>modal.remove()));modal.append(box);document.body.append(modal);
  }
  async function sendMail(){
    const uid=val('gm-mail-uid'),server_id=val('gm-mail-server'),character_name=val('gm-mail-name');
    const target=(dash?.players||[]).find(x=>x.uid===uid&&x.server_id===server_id&&x.character_name===character_name);
    if(!target){status('Không tìm thấy chính xác UID + Server + tên nhân vật trong máy chủ.',false);return;}
    if(!giftKey){status('Chưa xác thực khóa QTV.',false);return;}
    if(!Object.keys(giftBasket).length){status('Chưa chọn quà để gửi.',false);return;}
    const button=document.querySelector('#gm-send-button');
    if(button)button.disabled=true;
    try{
      const response=await fetch('/api/admin/mail/send',{
        method:'POST',credentials:'same-origin',
        headers:{'Content-Type':'application/json','X-GXB3-GM-Key':giftKey},
        body:JSON.stringify({uid,server_id,character_name,title:val('gm-mail-title'),body:val('gm-mail-body'),attachments:giftBasket})
      });
      const result=await response.json();
      if(!response.ok)throw Error(result.error||'Máy chủ từ chối gửi thư.');
      giftBasket={};
      status('Đã gửi thư '+result.id+' đến đúng '+result.uid+' / '+result.server_id+'.');
      await refreshDashboard();render();
    }catch(e){status('Gửi thất bại: '+e.message,false);}
    finally{if(button)button.disabled=false;}
  }
  function renderOrders(body){
    if(!giftKey){const gate=card('Xác thực bảo mật trước khi quản lý nạp');gate.append(el('p','admin-note','Duyệt đơn, từ chối đơn và thay đổi gói nạp cần khóa QTV riêng trên VPS. Khóa không lưu vào thiết bị.'),btn('Đến Gửi Thư để xác thực',()=>show('mail'),'primary'));body.append(gate);}
    const catalog=card('Gói nạp trên máy chủ');
    catalog.append(el('p','admin-note','Chọn gói và chỉnh từng trường. Không cần nhập mã JSON.'));
    const pkgSelect=document.createElement('select');pkgSelect.id='gm-topup-selection';
    for(const pack of (topupCfg?.packages||[])){
      const o=el('option','',pack.name+' · '+pack.id);o.value=pack.id;pkgSelect.append(o);
    }
    const form=el('div','admin-form-row');form.append(pkgSelect);
    form.append(btn('Chỉnh sửa',()=>{
      const p=(topupCfg?.packages||[]).find(x=>x.id===pkgSelect.value);
      if(!p)return;
      document.getElementById('gm-topup-id').value=p.id;
      document.getElementById('gm-topup-name').value=p.name;
      document.getElementById('gm-topup-price').value=p.price_label||'';
      document.getElementById('gm-topup-manual').checked=!!p.manual_reward;
      packageEditId=p.id;packageRewards={...(p.reward||{})};
      document.getElementById('gm-topup-vip-exp').value=Number(packageRewards['999999991']||0);
      status('Đã chọn gói '+p.name);
    }));
    catalog.append(form);
    field(catalog,'Mã gói','gm-topup-id').placeholder='PACKAGE_ID';
    field(catalog,'Tên gói','gm-topup-name').placeholder='Gói VIP';
    field(catalog,'Giá hiển thị','gm-topup-price').placeholder='Liên hệ Zalo';
    const vipField=field(catalog,'VIP EXP theo gói (chỉ gửi thư sau khi QTV duyệt)','gm-topup-vip-exp','number');
    vipField.min='0';vipField.max='2000000';vipField.step='1';vipField.value='0';
    catalog.append(el('p','admin-note','Đặt đúng số VIP EXP của gói. Chọn “Thưởng do QTV duyệt thủ công” nếu chưa cấu hình phần thưởng tự động.'));
    const label=el('label','admin-check');const checkbox=document.createElement('input');
    checkbox.type='checkbox';checkbox.id='gm-topup-manual';
    label.append(checkbox,document.createTextNode('Thưởng do QTV duyệt thủ công'));catalog.append(label);
    catalog.append(btn('Dùng quà đã chọn làm phần thưởng gói',()=>{packageRewards={...giftBasket};status('Đã lấy '+Object.keys(packageRewards).length+' vật phẩm làm phần thưởng gói.');},'admin-secondary'));
    catalog.append(btn('Lưu gói đã chọn',saveSelectedPackage,'primary'));
    catalog.append(btn('Khôi phục danh mục mặc định',resetTopupPackages,'danger'));
    body.append(catalog);
    const c=card('Duyệt đơn nạp thật');
    const list=el('div','admin-list');const orders=dash?.orders||[];
    if(!orders.length)list.append(el('p','admin-note','Chưa có đơn nạp.'));
    for(const o of orders){
      const row=el('article','admin-row');const info=el('div','admin-row-main');
      info.append(el('b','',o.id),
        el('span','',o.server_id+' · '+o.uid+' · '+o.character_name),
        el('small','',(o.package_name||o.package||'Gói chưa đặt tên')+
          (o.price_label?' · '+o.price_label:'')+' · '+o.status));
      row.append(info);
      if(o.status==='pending'){
        if(Number(o.manual_reward||0)){
          row.append(el('p','admin-note','Gói tùy chỉnh: chọn quà ở tab Tiền Tệ / Vật Phẩm / Mảnh Nhân Vật trước khi duyệt.'));
          row.append(btn('Duyệt với quà đã chọn',()=>reviewOrder(o,'approve'),'primary'));
        }else row.append(btn('Duyệt đúng gói',()=>reviewOrder(o,'approve'),'primary'));
        row.append(btn('Từ chối',()=>reviewOrder(o,'reject'),'danger'));
      }
      list.append(row);
    }
    c.append(list);body.append(c);
  }
  let packageEditId='',packageRewards={};
  async function saveSelectedPackage(){
    try{
      const vipExp=Number(val('gm-topup-vip-exp')||0);
      if(!Number.isSafeInteger(vipExp)||vipExp<0||vipExp>2000000)
        throw Error('VIP EXP phải nằm trong khoảng 0 đến 2.000.000');
      const rewards={...packageRewards};
      if(vipExp)rewards['999999991']=vipExp;else delete rewards['999999991'];
      const pack={id:val('gm-topup-id'),name:val('gm-topup-name'),
        price_label:val('gm-topup-price'),
        manual_reward:!!document.getElementById('gm-topup-manual')?.checked,
        reward:rewards};
      if(!pack.id||!pack.name)throw Error('Cần mã gói và tên gói');
      const packages=[...(topupCfg?.packages||[])];
      const pos=packages.findIndex(x=>x.id===packageEditId);
      if(pos>=0)packages[pos]={...packages[pos],...pack};else packages.push(pack);
      topupCfg=await gmAction('/api/admin/topup-packages',{action:'save',config:{...topupCfg,packages}});
      status('Đã lưu gói '+pack.name+'.');render();
    }catch(e){status(e.message,false);}
  }
  async function resetTopupPackages(){
    try{topupCfg=await gmAction('/api/admin/topup-packages',{action:'reset'});
      packageEditId='';packageRewards={};status('Đã khôi phục danh mục gói nạp.');render();
    }catch(e){status(e.message,false);}
  }
  async function reviewOrder(order,action){
    try{
      const manual=Number(order.manual_reward||0)>0;
      const reward=action==='approve'&&manual?{...giftBasket}:{};
      if(action==='approve'&&manual&&!Object.keys(reward).length)
        throw Error('Đơn tùy chỉnh chưa có quà đã chọn.');
      const okay=await GirlUI.confirm(
        'Đơn '+order.id+' / '+order.uid+' / '+order.server_id+
        (action==='approve'?' · Xác nhận duyệt và gửi quà qua Hòm Thư?':' · Xác nhận từ chối?'),
        {title:'Xác nhận đơn nạp',ok:action==='approve'?'Duyệt':'Từ chối',danger:action!=='approve'});
      if(!okay)return;
      await gmAction('/api/admin/order/review',{order_id:order.id,action,reward});
      if(action==='approve'&&manual)giftBasket={};
      status(action==='approve'?'Đã duyệt đơn và gửi thưởng qua thư.':'Đã từ chối đơn.');
      await refreshDashboard();render();
    }catch(e){status(e.message,false);}
  }
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
      row.append(btn('Gửi quà',()=>{recipient=p;catalogSearch='';show('currency');},'primary'),
        btn('Gửi thư',()=>{recipient=p;show('mail');},'primary'),
        btn('Phiên',()=>viewSessions(p.uid)),btn('Thu hồi phiên',()=>revokeSessions(p.uid)));
      holder.append(row);
    }
  }
  async function playerStatus(p,action){try{
    const reason=action==='ban'?(await GirlUI.promptText('Lý do cấm trên máy chủ '+p.server_id+':',{title:'Cấm Người Chơi',value:'Vi phạm quy định',maxLength:160,minLength:1}) ) :'';if(action==='ban'&&!reason)return;
    await api('/api/admin/player/status',{uid:p.uid,server_id:p.server_id,action,reason});status(action==='ban'?'Đã ban nhân vật ở server này.':'Đã unban nhân vật ở server này.');await refreshDashboard();render();
  }catch(e){status(e.message,false);}}
  async function accountStatus(p,action){try{
    const reason=action==='ban'?(await GirlUI.promptText('Lý do khóa toàn tài khoản:',{title:'Khóa Tài Khoản',value:'Vi phạm nghiêm trọng',maxLength:160,minLength:1}) ) :'';if(action==='ban'&&!reason)return;
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
    const res=card('Tài nguyên & Nữ Thần khởi đầu');const starter=cfg.starting_resources||{};
    for(const [id,count] of Object.entries(starter)){
      const it=giftCatalog?.items?.find(x=>String(x.id)===String(id));
      const row=el('div','admin-config-resource');
      if(it?.image)row.append(giftPic(it.image,it.name));
      const label=el('label','admin-field',(it?.name||'Vật phẩm')+' · ID '+id);
      const input=document.createElement('input');input.type='number';input.min=0;
      input.value=String(count);input.dataset.starterItem=id;label.append(input);row.append(label);res.append(row);
    }
    field(res,'Nữ Thần khởi đầu (ID, phân cách dấu phẩy)','admin-starters').value=cfg.starter_girls.join(',');
    grid.append(res);
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
  async function saveConfig(){try{const raw={starting_resources:Object.fromEntries([...document.querySelectorAll('[data-starter-item]')].map(el=>[el.dataset.starterItem,Math.max(0,Math.trunc(Number(el.value)||0))])),starter_girls:val('admin-starters').split(',').map(x=>Number(x.trim())).filter(Boolean),summon_rate:{star_multiplier:Object.fromEntries([1,2,3,4,5,6].map(s=>[String(s),Number(val(`admin-star-${s}`))]))},shop:{price_multiplier:Number(val('admin-shop'))},rewards:{multiplier:Number(val('admin-reward'))},progression:{cost_multiplier:Number(val('admin-progress'))}};cfg=await api('/api/admin/config',raw);status('Đã lưu cấu hình.');}catch(e){status(e.message,false);}}
  async function resetConfig(){try{cfg=await api('/api/admin/config',{action:'reset'});status('Đã khôi phục mặc định.');render();}catch(e){status(e.message,false);}}
  function renderGame(){if(typeof window.render==='function')window.render();}
  function renderAudit(body){const c=card('Audit Log');const list=el('div','admin-list');for(const a of dash?.audit||[]){const row=el('article','admin-row');const info=el('div','admin-row-main');info.append(el('b','',a.action),el('span','',a.target),el('small','',new Date(a.at*1000).toLocaleString()+' · '+a.operator));row.append(info);list.append(row);}c.append(list);body.append(c);}
  const val=id=>document.getElementById(id)?.value?.trim()||'';
  async function load(){try{ensure();[cfg,dash,topupCfg,giftCatalog]=await Promise.all([api('/api/admin/config'),api('/api/admin/dashboard'),api('/api/admin/topup-packages'),api('/api/admin/gift-catalog')]);show(active);status('Hệ Thống QTV đã sẵn sàng.');}catch(e){status(e.message,false);}}
  async function open(){ensure();root.hidden=false;await load();}
  function close(){giftKey='';giftBasket={};if(root)root.hidden=true;showView('home');}
  async function logout(){developerMode=false;adminKey='';sessionStorage.setItem('gxb2-developer','0');sessionStorage.removeItem('gxb2-admin-key');if(root)root.hidden=true;state=await api('/api/state');loadFormation();showView('home');renderGame();}
  return{open,close,load,logout};
})();
