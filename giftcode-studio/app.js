'use strict';
(()=>{
const $=id=>document.getElementById(id);
const state={me:null,admin:false,panelUnlocked:false,panelAccess:'',unlockDestination:'create',skins:[],skinPage:0,catalog:[],basket:{},worlds:[],codes:[],page:0,view:'redeem'};
const limit=16;
const txt=(tag,text,cls)=>{const x=document.createElement(tag);if(cls)x.className=cls;x.textContent=String(text??'');return x;};
const api=async(path,body,gm=false,unlock=false)=>{
 const options={credentials:'same-origin',headers:{'Accept':'application/json'}};
 if(body!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(body);}
 if(gm)options.headers['X-GXB3-GM-Key']=state.view==='skins'?($('skin-gm-key')?.value||''):$('gm-key').value;
 if(unlock)options.headers['X-GXB3-Giftcode-Access']=state.panelAccess;
 // The Vercel deployment uses one static /api/bridge function. Avoid
 // framework-dependent catch-all routing (which returned [object Object]).
 let requestPath=path;
 if(location.origin!=='https://180-93-111-99.sslip.io'){
   const target=new URL(path,location.origin);
   const bridgeUrl=new URL('/api/bridge',location.origin);
   bridgeUrl.searchParams.set('route',target.pathname.startsWith('/api/')?target.pathname.slice(5):'');
   for(const [k,v] of target.searchParams)bridgeUrl.searchParams.append(k,v);
   requestPath=bridgeUrl.pathname+bridgeUrl.search;
 }
 const r=await fetch(requestPath,options),data=await r.json().catch(()=>({}));
 if(!r.ok){
   const err=data?.error;
   const detail=typeof err==='string'?err:(typeof err?.message==='string'?err.message:'Kết nối API thất bại (HTTP '+r.status+')');
   // Admin unlock tokens expire server-side. Reopen the real unlock form
   // instead of leaving an apparently active screen that can never save.
   if(r.status===403&&state.panelUnlocked&&/mở khóa|unlock/i.test(detail)){
     state.panelUnlocked=false;
     state.panelAccess='';
     switchView(state.view==='skins'?'skins':'create');
   }
   throw Error(detail);
 }
 return data;
};
function notice(msg,ok=true){const el=$('global-status');el.textContent=msg;el.dataset.ok=ok?'1':'0';}
function switchView(view){
 if(!state.admin&&view!=='redeem')view='redeem';
 state.view=view;
 const titles={create:'Tạo Giftcode',history:'Giftcode đã phát hành',redeem:'Đổi Giftcode',skins:'Quản lý Trang Phục'};
 $('page-title').textContent=titles[view];
 for(const el of document.querySelectorAll('.nav-btn')){el.classList.toggle('active',el.dataset.view===view);el.hidden=!state.admin&&el.dataset.view!=='redeem';}
 for(const name of ['create','history','redeem','skins'])$(name+'-view').hidden=view!==name||!state.me||((name==='create'||name==='skins')&&!state.panelUnlocked);
 $('create-lock').hidden=!state.me||!state.admin||(view!=='create'&&view!=='skins')||state.panelUnlocked;
 if((view==='create'||view==='skins')&&!state.panelUnlocked)state.unlockDestination=view;
 if(view==='history'&&state.admin)refreshCodes().catch(e=>notice(e.message,false));
 if(view==='skins'&&state.admin&&state.panelUnlocked)loadSkins().catch(e=>notice(e.message,false));
}
function updateStats(){
 $('stat-total').textContent=state.codes.length.toLocaleString('vi-VN');
 $('stat-active').textContent=state.codes.filter(c=>c.active&&(!c.expires_at||c.expires_at>Date.now()/1000)&&c.remaining>0).length.toLocaleString('vi-VN');
 $('stat-used').textContent=state.codes.reduce((n,c)=>n+Number(c.used_count||0),0).toLocaleString('vi-VN');
}
async function bootstrap(){
 const m=await api('/api/auth/me');state.me=m.authenticated?m.session:null;state.admin=Boolean(m.is_super_gm);
 if(!state.admin){state.panelUnlocked=false;state.panelAccess='';state.skins=[];}
 $('login-panel').hidden=Boolean(state.me);
 $('restricted').hidden=!state.me||state.admin;
 $('account-label').textContent=state.me?(state.me.account?.username||state.me.account?.uid||'Đã đăng nhập'):'Chưa đăng nhập';
 $('server-status').textContent='● Máy chủ online · '+(state.me?.account?.server_id||'GXB 3');
 const select=$('login-form').elements.server_id;
 for(const w of m.worlds||[]){if(select.querySelector('[value="'+w.server_id+'"]'))continue;const option=document.createElement('option');option.value=w.server_id;option.textContent=w.name+' · '+w.server_id;select.append(option);}
 if(!state.me){switchView('redeem');return;}
 if(state.admin){
  const cat=await api('/api/giftcode/catalog');
  state.worlds=cat.worlds||[];
  state.catalog=[...(cat.catalog?.items||[]).map(x=>({...x,kind:'items'})),...(cat.catalog?.shards||[]).map(x=>({...x,kind:'shards'}))];
  state.catalog.unshift({id:999999991,name:'EXP VIP',image:'/assets/events/check_in_pop_up_vip_level_bg.png',kind:'items'});
  for(const w of state.worlds){const option=document.createElement('option');option.value=w.server_id;option.textContent=w.name+' · '+w.server_id;$('world').append(option);}
  renderCatalog();renderBasket();await refreshCodes();
 }
 switchView(state.admin?'create':'redeem');
}
async function refreshCodes(){const res=await api('/api/giftcode/list');state.codes=res.codes||[];updateStats();renderCodes();}
function renderCatalog(){
 const search=$('item-search').value.trim().toLocaleLowerCase('vi-VN');
 const kind=$('item-kind').value;
 const results=state.catalog.filter(x=>(kind==='all'||kind===x.kind)&&(String(x.name).toLocaleLowerCase('vi-VN').includes(search)||String(x.id).includes(search)));
 const pages=Math.max(1,Math.ceil(results.length/limit));state.page=Math.min(state.page,pages-1);
 $('page-count').textContent=(state.page+1)+' / '+pages+' · '+results.length+' loại';
 const panel=$('catalog');panel.replaceChildren();
 for(const row of results.slice(state.page*limit,(state.page+1)*limit)){
  const b=txt('button','','catalog-item');b.type='button';b.title='Thêm '+row.name;
  const img=document.createElement('img');img.src=row.image;img.alt='';img.loading='lazy';
  const info=document.createElement('span');info.append(txt('b',row.name),txt('small','#'+row.id+' · '+(row.kind==='shards'?'Mảnh nhân vật':'Vật phẩm')));
  b.append(img,info);b.onclick=()=>{const id=String(row.id);state.basket[id]=(state.basket[id]||0)+1;renderBasket();notice('Đã thêm '+row.name);};panel.append(b);
 }
 if(!results.length)panel.append(txt('p','Không tìm thấy vật phẩm.','muted'));
 $('prev-page').disabled=state.page===0;$('next-page').disabled=state.page>=pages-1;
}
function renderBasket(){
 const parent=$('basket');parent.replaceChildren();
 const entries=Object.entries(state.basket);if(!entries.length){parent.append(txt('p','Chưa chọn vật phẩm.','muted'));return;}
 for(const [id,quantity] of entries){
  const row=state.catalog.find(x=>String(x.id)===id);const box=txt('div','','basket-row');
  if(row?.image){const img=document.createElement('img');img.src=row.image;img.alt='';box.append(img);}
  const desc=txt('span',(row?.name||'Vật phẩm')+' · #'+id);box.append(desc);
  const input=document.createElement('input');input.type='number';input.min='1';input.max='2000000';input.value=quantity;
  input.setAttribute('aria-label','Số lượng '+(row?.name||id));input.onchange=()=>{const n=Number(input.value);if(Number.isSafeInteger(n)&&n>=1&&n<=2000000){state.basket[id]=n;}else{input.value=state.basket[id];notice('Số lượng phải từ 1 đến 2.000.000',false);}};box.append(input);
  const remove=txt('button','✕','ghost small');remove.onclick=()=>{delete state.basket[id];renderBasket();};box.append(remove);parent.append(box);
 }
}
function statusTag(code){
 if(!code.active)return 'Đã khóa';
 if(code.expires_at&&code.expires_at<=Date.now()/1000)return 'Hết hạn';
 if(!code.remaining)return 'Hết lượt';
 return 'Đang hoạt động';
}
function renderCodes(){
 const box=$('codes');box.replaceChildren();
 if(!state.codes.length){box.append(txt('p','Chưa có giftcode.','muted'));return;}
 for(const data of state.codes){
  const row=txt('article','','code-row'),detail=txt('div','','detail');
  detail.append(txt('b',data.code));
  const date=data.expires_at?new Date(data.expires_at*1000).toLocaleString('vi-VN'):'Không giới hạn';
  detail.append(txt('small',data.title+' · '+data.server_id+' · '+statusTag(data)));
  detail.append(txt('small','Đã sử dụng '+data.used_count+'/'+data.max_uses+' · Hết hạn: '+date));
  const actions=txt('div','','actions');
  const copy=txt('button','Sao chép','ghost');copy.onclick=()=>copyText(data.code);actions.append(copy);
  const see=txt('button','Lịch sử','ghost');see.onclick=async()=>{
   const old=row.querySelector('.redemptions');if(old){old.remove();return;}
   try{const res=await api('/api/giftcode/redemptions?code='+encodeURIComponent(data.code));
     const info=txt('div','','redemptions');if(!res.redemptions.length)info.append(txt('p','Chưa có tài khoản đổi mã'));
     for(const r of res.redemptions){info.append(txt('div',r.uid+' · '+r.server_id+' · '+new Date(r.redeemed_at*1000).toLocaleString('vi-VN')+' · '+r.mail_id));}row.append(info);
   }catch(e){notice(e.message,false);}
  };actions.append(see);
  if(data.active){const revoke=txt('button','Khóa mã','danger');revoke.onclick=async()=>{
   if(!confirm('Vô hiệu hóa '+data.code+'? Người chơi sẽ không đổi mã này được nữa.'))return;
   try{await api('/api/giftcode/admin/revoke',{code:data.code},true,true);notice('Đã khóa '+data.code);await refreshCodes();}catch(e){notice(e.message,false);}
  };actions.append(revoke);}
  row.append(detail,actions);box.append(row);
 }
}
async function copyText(s){try{await navigator.clipboard.writeText(s);notice('Đã sao chép '+s);}catch{notice('Không thể tự sao chép. Mã: '+s,false);}}
$('login-form').onsubmit=async e=>{e.preventDefault();const form=e.currentTarget,submit=form.querySelector('button');submit.disabled=true;try{await api('/api/auth/login',{username:form.elements.username.value,password:form.elements.password.value,server_id:form.elements.server_id.value});form.reset();await bootstrap();notice('Đăng nhập thành công');}catch(err){$('login-status').textContent=err.message;notice(err.message,false);}finally{submit.disabled=false;}};
document.querySelectorAll('.nav-btn').forEach(x=>x.onclick=()=>switchView(x.dataset.view));
$('item-search').oninput=()=>{state.page=0;renderCatalog();};$('item-kind').onchange=()=>{state.page=0;renderCatalog();};
$('prev-page').onclick=()=>{state.page--;renderCatalog();};$('next-page').onclick=()=>{state.page++;renderCatalog();};
$('clear-basket').onclick=()=>{state.basket={};renderBasket();};
$('refresh-history').onclick=()=>refreshCodes().catch(e=>notice(e.message,false));
$('unlock-form').onsubmit=async event=>{
 event.preventDefault();
 const button=event.currentTarget.querySelector('button');button.disabled=true;
 try{const result=await api('/api/giftcode/admin/unlock',{password:$('unlock-password').value});
   state.panelAccess=result.access;state.panelUnlocked=true;
   $('unlock-password').value='';switchView(state.unlockDestination||'create');notice('Đã mở khóa khu vực quản trị.');
 }catch(e){notice(e.message,false);}finally{button.disabled=false;}
};
$('verify-key').onclick=async()=>{try{await api('/api/admin/gm/verify-key',{},true);notice('Khóa QTV hợp lệ.');}catch(e){notice(e.message,false);}};
const CODE_PATTERN=/^[A-Z0-9][A-Z0-9_-]{5,23}$/;
$('code').addEventListener('input',()=>{
  const code=$('code');
  code.value=code.value.toUpperCase().replace(/[^A-Z0-9_-]/g,'').slice(0,24);
  $('code-check-status').textContent=code.value?'Chưa kiểm tra mã trên máy chủ.':'Để trống nếu muốn máy chủ tự sinh mã.';
});
$('random-code').onclick=()=>{
 const chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
 const random=new Uint8Array(12);
 crypto.getRandomValues(random);
 $('code').value='GXB3-'+Array.from(random,n=>chars[n%chars.length]).join('');
 $('code-check-status').textContent='Đã tạo gợi ý ngẫu nhiên. Hãy kiểm tra trùng hoặc phát hành trực tiếp.';
};
$('check-code').onclick=async()=>{
 const code=$('code').value.trim().toUpperCase();
 if(!CODE_PATTERN.test(code)){notice('Mã phải có 6–24 ký tự A–Z, 0–9, dấu _ hoặc -.',false);return;}
 const btn=$('check-code');btn.disabled=true;
 try{
   const r=await api('/api/giftcode/check?code='+encodeURIComponent(code));
   $('code-check-status').textContent=r.exists?'✕ Mã đã tồn tại. Hãy chọn mã khác.':'✓ Chưa có mã này trên server (sẽ kiểm tra lại lúc phát hành).';
   $('code-check-status').dataset.ok=r.exists?'0':'1';
 }catch(e){notice(e.message,false);}finally{btn.disabled=false;}
};

$('create-code').onclick=async()=>{
 const b=$('create-code');const requested=$('code').value.trim().toUpperCase();if(requested&&!CODE_PATTERN.test(requested)){notice('Mã Giftcode phải gồm 6–24 ký tự A–Z, số, _ hoặc -.',false);return;}
 if(!Object.keys(state.basket).length){notice('Hãy chọn ít nhất một vật phẩm.',false);return;}
 const expiry=$('expiry').value;
 const payload={code:requested,title:$('title').value,message:$('message').value,server_id:$('world').value,max_uses:Number($('max-uses').value),expires_at:expiry?Math.floor(new Date(expiry).getTime()/1000):0,rewards:state.basket};
 b.disabled=true;
 try{const res=await api('/api/giftcode/admin/create',payload,true,true);$('new-code').hidden=false;$('created-code').textContent=res.code;notice('Đã tạo giftcode thật trên máy chủ!');$('code').value='';await refreshCodes();}catch(e){notice(e.message,false);}finally{b.disabled=false;}
};
$('copy-code').onclick=()=>copyText($('created-code').textContent);
$('redeem-form').onsubmit=async e=>{
 e.preventDefault();const btn=e.currentTarget.querySelector('button');btn.disabled=true;
 try{const r=await api('/api/giftcode/redeem',{code:$('redeem-code').value});notice(r.message);$('redeem-code').value='';}
 catch(err){notice(err.message,false);}finally{btn.disabled=false;}
};


const SKIN_PAGE_SIZE=16;
const skinFmt=n=>Number(n||0).toLocaleString('vi-VN');
function skinFiltered(){
 const q=$('skin-search').value.trim().toLocaleLowerCase('vi-VN'),group=$('skin-group').value;
 const status=$('skin-state').value,currency=$('skin-currency').value;
 return state.skins.filter(r=>{
   if(status==='wedding'){if(!r.is_wedding)return false;}
   else if(status==='incomplete'){if(r.is_saleable||r.is_wedding)return false;}
   else {if(r.is_wedding||!r.is_saleable)return false;
     if(status==='enabled'&&!r.enabled||status==='disabled'&&r.enabled)return false;}
   if(group!=='all'&&String(r.group)!==group)return false;
   if(currency!=='all'&&!r['allow_'+currency])return false;
   return !q||[r.name,r.girl_name,String(r.skin_id),...(r.girl_ids||[]).map(String)]
      .some(x=>String(x).toLocaleLowerCase('vi-VN').includes(q));
 });
}
async function loadSkins(){
 const response=await api('/api/skin-shop/admin/catalog');
 state.skins=response.offers||[];
 if(!$('skin-group').dataset.filled){
   const factions=[...new Set(state.skins.map(r=>r.group).filter(Boolean))].sort((a,b)=>a-b);
   for(const id of factions){const option=document.createElement('option');option.value=String(id);option.textContent='Phe '+id;$('skin-group').append(option);}
   $('skin-group').dataset.filled='1';
 }
 renderSkins();
}
function skinSettings(card){
 const value=k=>card.querySelector('[data-field="'+k+'"]');
 const id=Number(card.dataset.skinId);
 const price=k=>{const raw=value(k).value.trim();if(!/^\d+$/.test(raw))throw Error('Giá phải là số nguyên không âm');return Number(raw);};
 for(const field of ['price_gold','price_crystal']){
   const el=value(field),num=price(field);
   if(!Number.isSafeInteger(num)||num<0||num>2000000000)throw Error('Giá phải là số nguyên từ 0 đến 2 tỷ');
 }
 return {skin_id:id,enabled:value('enabled').checked,
  allow_gold:value('allow_gold').checked,allow_crystal:value('allow_crystal').checked,
  allow_ticket:value('allow_ticket').checked,
  price_gold:price('price_gold'),price_crystal:price('price_crystal')};
}
async function saveSkinRows(cards){
 const changes=cards.map(skinSettings);
 if(!changes.length)return;
 if(!$('skin-gm-key').value.trim()){notice('Nhập Khóa hành động QTV bên dưới danh sách trước khi lưu.',false);$('skin-gm-key').focus();return;}
 if(changes.length>1&&!confirm('Lưu thay đổi '+changes.length+' trang phục?'))return;
 const button=document.activeElement;
 if(button)button.disabled=true;
 try{
   const endpoint=changes.length===1?'/api/skin-shop/admin/update':'/api/skin-shop/admin/bulk';
   const payload=changes.length===1?changes[0]:{changes};
   const response=await api(endpoint,payload,true,true);
   notice('Máy chủ đã lưu cấu hình '+response.updated+' trang phục.');
   await loadSkins();
 }catch(e){notice(e.message,false);}finally{if(button)button.disabled=false;}
}
function renderSkins(){
 const filtered=skinFiltered(), pages=Math.max(1,Math.ceil(filtered.length/SKIN_PAGE_SIZE));
 state.skinPage=Math.max(0,Math.min(state.skinPage,pages-1));
 const canSell=state.skins.filter(x=>x.is_saleable).length;
 const wedding=state.skins.filter(x=>x.is_wedding).length;
 $('skin-stats').textContent=canSell+' skin thường đủ dữ liệu · '+wedding+' skin cưới khóa cứng · '+state.skins.filter(x=>!x.is_saleable&&!x.is_wedding).length+' bản ghi kỹ thuật bị khóa · '+state.skins.filter(x=>x.enabled&&x.is_saleable).length+' đang bán';
 $('skin-page-count').textContent=(state.skinPage+1)+' / '+pages+' · '+filtered.length+' trang phục';
 $('skin-prev').disabled=state.skinPage===0;
 $('skin-next').disabled=state.skinPage>=pages-1;
 const grid=$('skin-grid');grid.replaceChildren();
 for(const r of filtered.slice(state.skinPage*SKIN_PAGE_SIZE,(state.skinPage+1)*SKIN_PAGE_SIZE)){
   const card=txt('article','','skin-item'+(r.is_wedding?' is-wedding':!r.is_saleable?' is-locked':''));
   card.dataset.skinId=r.skin_id;
   const head=txt('div','','skin-item-head');
   const pic=document.createElement('img');pic.src='/assets/skins/cards/'+r.skin_id+'.webp';pic.alt=r.name;pic.loading='lazy';
   pic.onerror=()=>{pic.hidden=true;};
   const title=txt('div','','skin-head-title');
   title.append(txt('b',r.name),txt('small',(r.girl_name||'Nữ Thần')+' · #'+r.skin_id+' · Phe '+r.group));
   title.append(txt('small',r.is_wedding?'♡ Độc quyền đám cưới · CẤM BÁN':!r.is_saleable?'⚠ Bản ghi kỹ thuật không bán':r.enabled?'● Đang mở bán':'○ Chưa mở bán'));
   const preview=txt('button','Xem trước','ghost small');preview.type='button';
   preview.onclick=()=>{$('skin-preview-image').src=pic.src;$('skin-preview-name').textContent=(r.girl_name||'')+' — '+r.name;$('skin-preview').showModal();};
   head.append(pic,title,preview);card.append(head);
   if(r.is_wedding||!r.is_saleable){card.append(txt('p',r.is_wedding?'Skin này chỉ mở qua hệ thống kết duyên, không thể bán.':'Dữ liệu gốc chưa có tên hoặc không gắn nhân vật. Không thể tạo đơn bán.','muted mini'));grid.append(card);continue;}
   const label=(field,name,kind='checkbox',val=false)=>{
     const wrapper=txt('label','','skin-control'),input=document.createElement('input');
     input.type=kind;input.dataset.field=field;
     if(kind==='checkbox')input.checked=Boolean(val);
     else{input.min='0';input.max='2000000000';input.step='1';input.value=String(val);}
     wrapper.append(input,txt('span',name));return wrapper;
   };
   const controls=txt('div','','skin-controls');
   controls.append(label('enabled','Bật bán','checkbox',r.enabled),
     label('allow_gold','Bán bằng Vàng','checkbox',r.allow_gold),
     label('price_gold','Giá Vàng','number',r.price_gold),
     label('allow_crystal','Bán bằng Crystal','checkbox',r.allow_crystal),
     label('price_crystal','Giá Crystal','number',r.price_crystal));
   const ticket=label('allow_ticket','Vé Trang Phục gốc: '+skinFmt(r.price_ticket),'checkbox',r.allow_ticket);
   if(!r.price_ticket)ticket.querySelector('input').disabled=true;
   controls.append(ticket);card.append(controls);
   const save=txt('button','Lưu trang phục này','primary small');save.type='button';save.onclick=()=>saveSkinRows([card]);
   card.append(save);grid.append(card);
 }
 if(!filtered.length)grid.append(txt('p','Không tìm thấy trang phục phù hợp.','muted'));
}
for(const id of ['skin-search','skin-group','skin-state','skin-currency']){
 $(id).addEventListener(id==='skin-search'?'input':'change',()=>{state.skinPage=0;renderSkins();});
}
$('skin-refresh').onclick=()=>loadSkins().catch(e=>notice(e.message,false));
$('skin-prev').onclick=()=>{state.skinPage--;renderSkins();};
$('skin-next').onclick=()=>{state.skinPage++;renderSkins();};
$('skin-save-visible').onclick=()=>saveSkinRows([...document.querySelectorAll('#skin-grid .skin-item:not(.is-wedding):not(.is-locked)')]);
$('skin-verify-key').onclick=async()=>{try{await api('/api/admin/gm/verify-key',{},true);notice('Khóa hành động QTV hợp lệ.');}catch(e){notice(e.message,false);}};
$('skin-preview-close').onclick=()=>$('skin-preview').close();

async function start(){
 // Hide all privileged navigation until the server confirms SUPER GM ownership.
 for(const el of document.querySelectorAll('.nav-btn'))el.hidden=true;
 for(const name of ['create','history','redeem','skins'])$(name+'-view').hidden=true;
 const ticket=new URLSearchParams(location.search).get('ticket');
 if(ticket){
   // Drop bearer ticket from address bar before making any other request.
   history.replaceState(null,'',location.pathname);
   try{await api('/api/giftcode/sso/exchange',{ticket});notice('Đã liên kết đăng nhập từ GXB 3.');}
   catch(e){notice('Liên kết đăng nhập: '+e.message,false);}
 }
 try{await bootstrap();}
 catch(err){
   $('server-status').textContent='Chưa kết nối máy chủ';
   $('login-panel').hidden=false;
   $('page-title').textContent='Liên kết tài khoản GXB 3';
   notice(err.message||'Lỗi kết nối máy chủ',false);
 }
}
start();
})();