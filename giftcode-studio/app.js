'use strict';
(()=>{
const $=id=>document.getElementById(id);
const state={me:null,admin:false,panelUnlocked:false,panelAccess:'',gmActionKey:'',accountIdentity:'',unlockDestination:'create',skins:[],skinPage:0,catalog:[],basket:{},worlds:[],codes:[],page:0,view:'redeem'};
const limit=16;
const txt=(tag,text,cls)=>{const x=document.createElement(tag);if(cls)x.className=cls;x.textContent=String(text??'');return x;};
const api=async(path,body,gm=false,unlock=false)=>{
 const options={credentials:'same-origin',cache:'no-store',headers:{'Accept':'application/json'}};
 if(body!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(body);}
 if(gm)options.headers['X-GXB3-GM-Key']=state.gmActionKey || (state.view==='skins'?($('skin-gm-key')?.value||''):$('gm-key').value);
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
     state.panelAccess='';state.gmActionKey='';
    switchView(state.view==='skins'?'skins':'create');
   }
   throw Error(detail);
 }
 return data;
};
function notice(msg,ok=true){const el=$('global-status');el.textContent=msg;el.dataset.ok=ok?'1':'0';}
function switchView(view){
 if(!state.admin&&!['redeem','shop','gift'].includes(view))view='redeem';
 state.view=view;
 const titles={create:'Tạo Giftcode',history:'Giftcode đã phát hành',redeem:'Đổi Giftcode',skins:'Quản lý Trang Phục',shop:'Cửa Hàng Trang Phục',gift:'GiftSkin · Tặng Trang Phục'};
 $('page-title').textContent=titles[view];
 for(const el of document.querySelectorAll('.nav-btn')){el.classList.toggle('active',el.dataset.view===view);el.hidden=!['redeem','shop','gift'].includes(el.dataset.view)&&!(state.admin&&state.panelUnlocked);}
 for(const name of ['create','history','redeem','skins','shop','gift'])$(name+'-view').hidden=view!==name||(!['shop','gift'].includes(name)&&!state.me)||(!['redeem','shop','gift'].includes(name)&&!state.panelUnlocked);
 $('create-lock').hidden=!state.me||!state.admin||['redeem','shop','gift'].includes(view)||state.panelUnlocked;
 if((view==='create'||view==='skins')&&!state.panelUnlocked)state.unlockDestination=view;
 if(view==='history'&&state.admin&&state.panelUnlocked)refreshCodes().catch(e=>notice(e.message,false));
 if(view==='skins'&&state.admin&&state.panelUnlocked)loadSkins().catch(e=>notice(e.message,false));
 if(view==='shop')loadPlayerShop().catch(e=>notice(e.message,false));
 if(view==='gift')loadGiftSkin().catch(e=>notice(e.message,false));
}
function updateStats(){
 $('stat-total').textContent=state.codes.length.toLocaleString('vi-VN');
 $('stat-active').textContent=state.codes.filter(c=>c.active&&(!c.expires_at||c.expires_at>Date.now()/1000)&&c.remaining>0).length.toLocaleString('vi-VN');
 $('stat-used').textContent=state.codes.reduce((n,c)=>n+Number(c.used_count||0),0).toLocaleString('vi-VN');
}
async function bootstrap(){
 const m=await api('/api/auth/me');
 const next=m.authenticated?m.session:null;
 const nextIdentity=next?[String(next.account?.uid||''),String(next.account?.server_id||'')].join(':'):'';
 // The owner unlock must not survive a change of player identity or server.
 if(nextIdentity!==state.accountIdentity){state.panelUnlocked=false;state.panelAccess='';state.gmActionKey='';state.skins=[];}
 state.accountIdentity=nextIdentity;
 state.me=next;state.admin=Boolean(next&&m.is_super_gm);
 if(!state.admin){state.panelUnlocked=false;state.panelAccess='';state.gmActionKey='';state.skins=[];}
 $('login-panel').hidden=Boolean(state.me);
 $('account-switch').hidden=!state.me;
 $('shop-account-note').textContent=state.me?'Đang sử dụng tài khoản '+(state.me.account?.username||'')+' · '+(state.me.account?.server_id||'')+' để mua.':'Bạn có thể xem giá; vui lòng đăng nhập để đặt mua.';
 $('restricted').hidden=!state.me||state.admin;
 $('account-label').textContent=state.me?(state.me.account?.username||state.me.account?.display_uid||'Đã đăng nhập'):'Chưa đăng nhập';
 $('account-character').textContent=state.me
   ?[(state.me.character_name||'Chưa chọn nhân vật'),state.me.account?.server_id||'',state.me.account?.display_uid||''].filter(Boolean).join(' · ')
   :'Nhấn Đồng bộ để dùng đúng tài khoản đang chơi';
 $('server-status').textContent=state.me?'● GXB 3 · Đã xác thực phiên':'○ Chưa liên kết tài khoản GXB 3';
 const select=$('login-form').elements.server_id;
 for(const w of m.worlds||[]){if(!select.querySelector('[value="'+w.server_id+'"]')){const option=document.createElement('option');option.value=w.server_id;option.textContent=w.name+' · '+w.server_id;select.append(option);}const g=$('gift-server');if(g&&!g.querySelector('[value="'+w.server_id+'"]')){const option=document.createElement('option');option.value=w.server_id;option.textContent=w.name+' · '+w.server_id;g.append(option);}}
 if(!state.me){switchView('redeem');return;}
 if(state.admin&&state.panelUnlocked){
  const cat=await api('/api/giftcode/catalog');
  state.worlds=cat.worlds||[];
  state.catalog=[...(cat.catalog?.items||[]).map(x=>({...x,kind:'items'})),...(cat.catalog?.shards||[]).map(x=>({...x,kind:'shards'}))];
  state.catalog.unshift({id:999999991,name:'EXP VIP',image:'/assets/events/check_in_pop_up_vip_level_bg.png',kind:'items'});
  for(const w of state.worlds){const option=document.createElement('option');option.value=w.server_id;option.textContent=w.name+' · '+w.server_id;$('world').append(option);}
  renderCatalog();renderBasket();await refreshCodes();
 }
 switchView(['shop','gift'].includes(state.view)?state.view:(state.admin?'create':'redeem'));
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
 try{
   const actionKey=$('unlock-gm-key').value;
   const result=await api('/api/giftcode/admin/unlock',{
     admin_key:$('unlock-admin-key').value,password:$('unlock-password').value,gm_key:actionKey
   });
   state.panelAccess=result.access;state.gmActionKey=actionKey;state.panelUnlocked=true;
   $('unlock-form').reset();
   const cat=await api('/api/giftcode/catalog');
   state.worlds=cat.worlds||[];
   state.catalog=[...(cat.catalog?.items||[]).map(x=>({...x,kind:'items'})),...(cat.catalog?.shards||[]).map(x=>({...x,kind:'shards'}))];
   state.catalog.unshift({id:999999991,name:'EXP VIP',image:'/assets/events/check_in_pop_up_vip_level_bg.png',kind:'items'});
   for(const w of state.worlds){if(!$('world').querySelector('[value="'+w.server_id+'"]')){const o=document.createElement('option');o.value=w.server_id;o.textContent=w.name+' · '+w.server_id;$('world').append(o);}}
   renderCatalog();renderBasket();await refreshCodes();
   switchView(state.unlockDestination||'create');
   notice('Đã xác thực đủ 3 khóa và mở khu vực quản trị.');
 }catch(e){state.panelUnlocked=false;state.panelAccess='';state.gmActionKey='';notice(e.message,false);}finally{button.disabled=false;}
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
 await refreshBankOrders();
 await refreshGiftAdminOrders();
}
// Use Vietnamese thousands notation without interpreting 299.000 VNĐ as 299.
function parseSkinPrice(raw){
 const text=String(raw??'').trim();
 if(/^(?:0|[1-9][0-9]*)$/.test(text))return Number(text);
 if(/^[1-9][0-9]{0,2}(?:[.,\s][0-9]{3})+$/.test(text))
   return Number(text.replace(/[.,\s]/g,''));
 throw Error('Giá phải là số nguyên; dùng 299000 hoặc 299.000 (không nhập số thập phân).');
}
function skinSettings(card){
 const field=k=>card.querySelector('[data-field="'+k+'"]');
 const id=Number(card.dataset.skinId);
 const price=k=>{
   const n=parseSkinPrice(field(k).value);
   if(!Number.isSafeInteger(n)||n<0||n>2000000000)
     throw Error('Giá phải là số nguyên từ 0 đến 2 tỷ');
   return n;
 };
 const enabled=field('enabled').checked,allow_bank=field('allow_bank').checked;
 const allow_crystal=field('allow_crystal').checked,price_vnd=price('price_vnd');
 const price_crystal=price('price_crystal');
 if(allow_bank&&price_vnd<=0)throw Error('Giá chuyển khoản phải lớn hơn 0 khi bật phương thức ngân hàng');
 if(allow_crystal&&price_crystal<=0)throw Error('Giá Crystal phải lớn hơn 0 khi bật phương thức Crystal');
 if(enabled&&!((allow_bank&&price_vnd>0)||(allow_crystal&&price_crystal>0)))
   throw Error('Để bật bán, hãy chọn ngân hàng hoặc Crystal và nhập giá lớn hơn 0');
 return {skin_id:id,enabled,allow_bank,allow_crystal,price_vnd,price_crystal};
}
function skinSaveStatus(card,message,ok){
 const p=card.querySelector('.skin-save-result');
 if(p){p.textContent=message;p.dataset.ok=ok===null?'pending':ok?'1':'0';}
}
function matchesSavedSkin(saved,requested){
 return saved&&Number(saved.skin_id)===requested.skin_id&&
   saved.enabled===requested.enabled&&saved.allow_bank===requested.allow_bank&&
   saved.allow_crystal===requested.allow_crystal&&
   Number(saved.price_vnd)===requested.price_vnd&&
   Number(saved.price_crystal)===requested.price_crystal;
}
async function saveSkinRows(cards,button){
 if(!cards.length)return;
 let changes;
 try{changes=cards.map(skinSettings);}
 catch(e){cards.forEach(c=>skinSaveStatus(c,e.message,false));notice(e.message,false);return;}
 if(!(state.gmActionKey||$('skin-gm-key').value.trim())){
   const message='Cần nhập Khóa hành động QTV ở cuối danh sách trước khi lưu.';
   cards.forEach(c=>skinSaveStatus(c,message,false));
   notice(message,false);$('skin-gm-key').focus();return;
 }
 if(changes.length>1&&!confirm('Lưu thay đổi '+changes.length+' trang phục?'))return;
 if(button)button.disabled=true;
 cards.forEach(c=>skinSaveStatus(c,'Đang ghi lên máy chủ và xác minh dữ liệu…',true));
 try{
   const endpoint=changes.length===1?'/api/skin-shop/admin/update':'/api/skin-shop/admin/bulk';
   const payload=changes.length===1?changes[0]:{changes};
   const response=await api(endpoint,payload,true,true);
   if(Number(response.updated)!==changes.length)throw Error('Máy chủ chưa xác nhận đủ '+changes.length+' cấu hình');
   // Read back from a fresh API response; a successful POST alone is insufficient.
   const confirmed=await api('/api/skin-shop/admin/catalog');
   const rows=confirmed.offers||[];
   const mismatched=changes.filter(req=>!matchesSavedSkin(rows.find(r=>Number(r.skin_id)===req.skin_id),req));
   if(mismatched.length){
     const ids=new Set(mismatched.map(r=>r.skin_id));
     cards.forEach(c=>skinSaveStatus(c,ids.has(Number(c.dataset.skinId))?'Máy chủ chưa lưu đúng cấu hình này. Giữ nguyên thông tin để thử lại.':'Đã xác nhận lưu trên máy chủ.',!ids.has(Number(c.dataset.skinId))));
     throw Error('Lưu chưa đồng bộ với máy chủ: Skin #'+mismatched.map(x=>x.skin_id).join(', #')+'. Dữ liệu trong form được giữ nguyên để thử lại.');
   }
   state.skins=rows;
   cards.forEach(c=>{
     const saved=rows.find(x=>Number(x.skin_id)===Number(c.dataset.skinId));
     const heading=c.querySelector('.skin-state-label');
     if(heading&&saved)heading.textContent=saved.enabled?'● Đang mở bán':'○ Chưa mở bán';
     skinSaveStatus(c,'Đã xác minh lưu thành công. Tải lại trang sẽ giữ nguyên cấu hình.',true);
   });
   $('skin-stats').textContent=state.skins.filter(x=>x.is_saleable).length+' skin thường đủ dữ liệu · '+
     state.skins.filter(x=>x.is_wedding).length+' skin cưới khóa cứng · '+
     state.skins.filter(x=>!x.is_saleable&&!x.is_wedding).length+' bản ghi kỹ thuật bị khóa · '+
     state.skins.filter(x=>x.enabled&&x.is_saleable).length+' đang bán';
   notice('Đã xác minh '+changes.length+' trang phục được lưu bền trên máy chủ.');
   // Do not repaint cards here; keep success visible and leave input data intact.
 }catch(e){
   const message=e.message||'Không lưu được cấu hình';
   cards.forEach(c=>{const result=c.querySelector('.skin-save-result');if(result&&(!result.textContent||result.textContent.startsWith('Đang ')))skinSaveStatus(c,'Chưa lưu: '+message,false);});
   notice('Lỗi lưu Skin: '+message,false);
 }finally{if(button)button.disabled=false;}
}
async function refreshBankOrders(){
 const status=$('skin-order-state').value;
 const response=await api('/api/skin-shop/admin/bank/orders?status='+encodeURIComponent(status));
 const rows=response.orders||[];
 $('skin-order-count').textContent=rows.length+' đơn ('+status+')';
 const host=$('skin-bank-orders');host.replaceChildren();
 if(!rows.length){host.append(txt('p','Không có đơn trong trạng thái này.','muted'));return;}
 for(const order of rows){
  const wrap=txt('article','','skin-order-item'),info=txt('div','','skin-order-text');
  info.append(txt('b',order.skin_name+' · '+skinFmt(order.price_vnd)+' VNĐ'),
    txt('small',order.id+' · '+order.uid+' / '+order.server_id+' · '+order.character_name),
    txt('small',({pending:'Chờ xác nhận chuyển khoản',approved:'Đã duyệt, gửi Hòm Thư',rejected:'Đã từ chối'}[order.status]||order.status)));
  wrap.append(info);
  if(order.status==='pending'){
    for(const [ok,label] of [[true,'Đã nhận tiền · Duyệt'],[false,'Từ chối']]){
      const b=txt('button',label,ok?'primary small':'ghost small');b.type='button';
      b.onclick=async()=>{
        if(!(state.gmActionKey||$('skin-gm-key').value.trim())){notice('Nhập khóa hành động QTV trước khi duyệt đơn.',false);return;}
        if(!confirm(ok?('Chỉ DUYỆT khi đã kiểm tra ngân hàng nhận đúng '+skinFmt(order.price_vnd)+' VNĐ cho đơn '+order.id+'. Xác nhận đã nhận tiền?'):
          ('Từ chối đơn '+order.id+'?')))return;
        b.disabled=true;
        try{await api('/api/skin-shop/admin/bank/review',{order_id:order.id,approve:ok},true,true);
          notice(ok?'Đã duyệt và gửi skin vào Hòm Thư người chơi.':'Đã từ chối đơn.');await refreshBankOrders();}
        catch(e){notice(e.message,false);b.disabled=false;}
      };wrap.append(b);
    }
  }
  host.append(wrap);
 }
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
   title.append(txt('small',r.is_wedding?'♡ Độc quyền đám cưới · CẤM BÁN':!r.is_saleable?'⚠ Bản ghi kỹ thuật không bán':r.enabled?'● Đang mở bán':'○ Chưa mở bán','skin-state-label'));
   const preview=txt('button','Xem trước','ghost small');preview.type='button';
   preview.onclick=()=>{$('skin-preview-image').src=pic.src;$('skin-preview-name').textContent=(r.girl_name||'')+' — '+r.name;$('skin-preview').showModal();};
   head.append(pic,title,preview);card.append(head);
   if(r.is_wedding||!r.is_saleable){card.append(txt('p',r.is_wedding?'Skin này chỉ mở qua hệ thống kết duyên, không thể bán.':'Dữ liệu gốc chưa có tên hoặc không gắn nhân vật. Không thể tạo đơn bán.','muted mini'));grid.append(card);continue;}
   const label=(field,name,kind='checkbox',val=false)=>{
     const wrapper=txt('label','','skin-control'),input=document.createElement('input');
     input.type=kind;input.dataset.field=field;
     if(kind==='checkbox')input.checked=Boolean(val);
     else{
       // HTML number controls treat "299.000" as 299; use an explicit
       // localized integer field for Vietnamese Dong and Crystal pricing.
       input.type='text';input.inputMode='decimal';input.autocomplete='off';
       input.placeholder='Ví dụ: 299.000';
       input.value=Number(val||0).toLocaleString('vi-VN');
       input.addEventListener('blur',()=>{
         try{const parsed=parseSkinPrice(input.value);input.value=parsed.toLocaleString('vi-VN');}
         catch{ /* Keep invalid input visible for explicit validation on Save. */ }
       });
     }
     wrapper.append(input,txt('span',name));return wrapper;
   };
   const controls=txt('div','','skin-controls');
   controls.append(label('enabled','Bật bán','checkbox',r.enabled),
     label('allow_bank','Chuyển khoản ngân hàng','checkbox',r.allow_bank),
     label('price_vnd','Giá chuyển khoản (VNĐ)','number',r.price_vnd),
     label('allow_crystal','Bán bằng Crystal','checkbox',r.allow_crystal),
     label('price_crystal','Giá Crystal','number',r.price_crystal));
   card.append(controls);
   const markPending=()=>skinSaveStatus(card,'Có thay đổi chưa lưu. Nhấn “Lưu trang phục này” hoặc “Lưu tất cả trang hiện tại”.',null);
   controls.addEventListener('input',markPending);
   controls.addEventListener('change',markPending);
   const status=txt('p','','skin-save-result');status.setAttribute('role','status');status.setAttribute('aria-live','polite');
   const save=txt('button','Lưu trang phục này','primary small');save.type='button';save.onclick=()=>saveSkinRows([card],save);
   card.append(status,save);grid.append(card);
 }
 if(!filtered.length)grid.append(txt('p','Không tìm thấy trang phục phù hợp.','muted'));
}
for(const id of ['skin-search','skin-group','skin-state','skin-currency']){
 $(id).addEventListener(id==='skin-search'?'input':'change',()=>{state.skinPage=0;renderSkins();});
}
$('skin-refresh').onclick=()=>loadSkins().catch(e=>notice(e.message,false));
$('skin-prev').onclick=()=>{state.skinPage--;renderSkins();};
$('skin-next').onclick=()=>{state.skinPage++;renderSkins();};
$('skin-save-visible').onclick=()=>saveSkinRows([...document.querySelectorAll('#skin-grid .skin-item:not(.is-wedding):not(.is-locked)')],$('skin-save-visible'));
$('skin-verify-key').onclick=async()=>{try{await api('/api/admin/gm/verify-key',{},true);notice('Khóa hành động QTV hợp lệ.');}catch(e){notice(e.message,false);}};
$('skin-preview-close').onclick=()=>$('skin-preview').close();
$('skin-order-refresh').onclick=()=>refreshBankOrders().catch(e=>notice(e.message,false));
$('skin-order-state').onchange=()=>refreshBankOrders().catch(e=>notice(e.message,false));

// Player storefront is independent of privileged Studio administration.

const GAME_ORIGIN='https://180-93-111-99.sslip.io';
const SHOP_PAGE_SIZE=16;
let shopOffers=[],shopPage=0,giftVerified=null,giftRequestId='';
const giftFields=()=>({
 recipient_uid:$('gift-recipient-uid').value.trim().toUpperCase(),
 recipient_name:$('gift-recipient-name').value.trim(),
 recipient_server:$('gift-server').value,
 skin_id:Number($('gift-skin').value),
 payment:$('gift-payment').value
});
const giftSignature=data=>JSON.stringify([data.recipient_uid,data.recipient_name,data.recipient_server,data.skin_id,data.payment]);
function requireShopLogin(){
 if(state.me)return true;
 notice('Hãy đăng nhập tài khoản GXB 3 của chính bạn để mua hoặc tặng trang phục.',false);
 $('login-panel').hidden=false;
 $('login-panel').scrollIntoView({behavior:'smooth',block:'center'});
 return false;
}
async function loadPlayerShop(){
 const response=await api('/api/skin-shop/catalog');
 shopOffers=(response.offers||[]).filter(x=>x.enabled&&!x.is_wedding&&x.is_saleable!==false&&(x.allow_crystal||x.allow_bank));
 const faction=$('shop-group'),old=faction.value;
 faction.replaceChildren(new Option('Tất cả phe','all'));
 for(const g of [...new Set(shopOffers.map(x=>String(x.group||0)))].sort()){
   faction.append(new Option('Phe '+g,g));
 }
 faction.value=[...faction.options].some(x=>x.value===old)?old:'all';
 renderPlayerShop();
 if(state.me)refreshShopOrders().catch(e=>notice(e.message,false));
 else $('shop-orders').replaceChildren(txt('p','Đăng nhập để xem đơn của bạn.','muted'));
}
function renderPlayerShop(){
 const grid=$('shop-grid');grid.replaceChildren();
 const q=$('shop-search').value.trim().toLocaleLowerCase('vi-VN'),group=$('shop-group').value;
 const rows=shopOffers.filter(x=>(group==='all'||String(x.group||0)===group)&&[x.name,x.girl_name,x.skin_id].some(v=>String(v||'').toLocaleLowerCase('vi-VN').includes(q)));
 const pages=Math.max(1,Math.ceil(rows.length/SHOP_PAGE_SIZE));
 shopPage=Math.max(0,Math.min(shopPage,pages-1));
 for(const item of rows.slice(shopPage*SHOP_PAGE_SIZE,(shopPage+1)*SHOP_PAGE_SIZE)){
   const card=txt('article','','player-shop-card');
   const img=document.createElement('img');img.className='player-shop-img';img.loading='lazy';img.alt=item.name;
   img.src=GAME_ORIGIN+'/assets/skins/cards/'+Number(item.skin_id)+'.webp';
   img.onerror=()=>{img.hidden=true;};
   card.append(img,txt('strong',(item.girl_name||'Nữ thần')+' · '+item.name));
   card.append(txt('small','#'+item.skin_id+' · Phe '+(item.group||0),'muted'));
   const actions=txt('div','','player-shop-actions');
   if(item.allow_crystal){
     const buy=txt('button','Mua '+Number(item.price_crystal).toLocaleString('vi-VN')+' Crystal','primary small');buy.type='button';
     buy.onclick=async()=>{
       if(!requireShopLogin())return;
       if(!confirm('Mua '+item.name+' bằng '+Number(item.price_crystal).toLocaleString('vi-VN')+' Crystal của tài khoản '+state.me.account.username+'? Trang phục sẽ gửi Hòm Thư.'))return;
       buy.disabled=true;
       try{const result=await api('/api/skins/action',{action:'buy',skin:item.skin_id,payment:'crystal'});
         notice('Mua thành công, trang phục đã vào Hòm Thư ('+(result.mail_id||'đã xác nhận')+').');}
       catch(e){notice(e.message,false);}finally{buy.disabled=false;}
     };actions.append(buy);
   }
   if(item.allow_bank){
     const buy=txt('button','Đặt đơn '+Number(item.price_vnd).toLocaleString('vi-VN')+' VNĐ','ghost small');buy.type='button';
     buy.onclick=async()=>{
       if(!requireShopLogin())return;
       if(!confirm('Tạo đơn '+item.name+' giá '+Number(item.price_vnd).toLocaleString('vi-VN')+' VNĐ? Phải chờ QTV xác nhận đã nhận tiền.'))return;
       buy.disabled=true;
       try{const result=await api('/api/skin-shop/bank/create',{skin_id:item.skin_id});
         notice('Đã tạo đơn '+result.id+' chờ duyệt. Chưa giao trang phục.');await refreshShopOrders();}
       catch(e){notice(e.message,false);}finally{buy.disabled=false;}
     };actions.append(buy);
   }
   const give=txt('button','✧ GiftSkin · Tặng','ghost small');give.type='button';
   give.onclick=async()=>{switchView('gift');await loadGiftSkin();$('gift-skin').value=String(item.skin_id);updateGiftPrice();};
   actions.append(give);card.append(actions);grid.append(card);
 }
 if(!rows.length)grid.append(txt('p','Không tìm thấy trang phục đang bán.','muted'));
 $('shop-count').textContent=rows.length+' trang phục · Trang '+(shopPage+1)+'/'+pages;
 $('shop-prev').disabled=shopPage===0;$('shop-next').disabled=shopPage>=pages-1;
}
async function refreshShopOrders(){
 if(!state.me)return;
 const result=await api('/api/skin-shop/bank/orders');
 const root=$('shop-orders');root.replaceChildren();
 for(const order of result.orders||[]){
   const card=txt('article','','player-order');
   card.append(txt('strong',order.skin_name+' · '+Number(order.price_vnd).toLocaleString('vi-VN')+' VNĐ'));
   card.append(txt('small',order.id+' · '+({pending:'Chờ QTV duyệt',approved:'Đã duyệt · Nhận qua thư',rejected:'Từ chối'}[order.status]||order.status),'muted'));
   root.append(card);
 }
 if(!root.children.length)root.append(txt('p','Bạn chưa có đơn chuyển khoản.','muted'));
}
async function loadGiftSkin(){
 if(!shopOffers.length){
   const res=await api('/api/skin-shop/catalog');
   shopOffers=(res.offers||[]).filter(x=>x.enabled&&!x.is_wedding&&(x.allow_crystal||x.allow_bank));
 }
 const current=$('gift-skin').value;
 $('gift-skin').replaceChildren(new Option('Chọn trang phục đang bán',''));
 for(const item of shopOffers){
   $('gift-skin').append(new Option((item.girl_name||'Nữ thần')+' · '+item.name+' (#'+item.skin_id+')',String(item.skin_id)));
 }
 $('gift-skin').value=shopOffers.some(x=>String(x.skin_id)===current)?current:'';
 updateGiftPrice();
 if(state.me)refreshGiftOrders().catch(e=>notice(e.message,false));
 else $('gift-orders').replaceChildren(txt('p','Đăng nhập để xem lịch sử tặng trang phục.','muted'));
}
function updateGiftPrice(){
 const item=shopOffers.find(x=>String(x.skin_id)===$('gift-skin').value);
 const method=$('gift-payment').value;
 $('gift-price').textContent=!item?'Hãy chọn trang phục':method==='crystal'
   ?(item.allow_crystal?Number(item.price_crystal).toLocaleString('vi-VN')+' Crystal':'Không bán bằng Crystal')
   :(item.allow_bank?Number(item.price_vnd).toLocaleString('vi-VN')+' VNĐ · QTV duyệt':'Không nhận chuyển khoản');
 giftVerified=null;giftRequestId='';$('gift-verified').textContent='Chưa xác minh UID + tên nhân vật + server.';
}
for(const id of ['gift-recipient-uid','gift-recipient-name','gift-server','gift-skin','gift-payment']){
 $(id).addEventListener('input',updateGiftPrice);$(id).addEventListener('change',updateGiftPrice);
}
$('gift-verify').onclick=async()=>{
 if(!requireShopLogin())return;
 const data=giftFields();
 if(!/^GB3-[1-9][0-9]{8}$/.test(data.recipient_uid)){notice('UID nhận phải có dạng GB3-123456789.',false);return;}
 const button=$('gift-verify');button.disabled=true;
 try{const target=await api('/api/giftskin/verify',data);
   giftVerified=giftSignature(data);$('gift-verified').textContent='✓ Đã xác minh '+target.display_uid+' · '+target.character_name+' · '+target.server_id;
   notice('Người nhận hợp lệ; chỉ giao GiftSkin đến UID vừa xác minh.');}
 catch(e){giftVerified=null;$('gift-verified').textContent='Không xác minh được người nhận.';notice(e.message,false);}
 finally{button.disabled=false;}
};
$('gift-send').onclick=async()=>{
 if(!requireShopLogin())return;
 const d=giftFields();
 const item=shopOffers.find(x=>x.skin_id===d.skin_id);
 if(!item){notice('Hãy chọn trang phục đang bán.',false);return;}
 if(!giftVerified||giftVerified!==giftSignature(d)){notice('Hãy xác minh lại UID, tên nhân vật và server người nhận.',false);return;}
 if((d.payment==='crystal'&&!item.allow_crystal)||(d.payment==='bank'&&!item.allow_bank)){notice('Phương thức này chưa được mở cho trang phục.',false);return;}
 const price=d.payment==='crystal'?Number(item.price_crystal):Number(item.price_vnd);
 const payName=d.payment==='crystal'?'Crystal':'VNĐ';
 if(!confirm('Tặng '+item.name+' cho '+d.recipient_name+' · '+d.recipient_uid+' · '+d.recipient_server+' bằng '+price.toLocaleString('vi-VN')+' '+payName+' của BẠN?\n'+(d.payment==='bank'?'Đơn chờ QTV xác nhận chuyển khoản.':'Crystal bị trừ và quà gửi qua Hòm Thư.')))return;
 const button=$('gift-send');button.disabled=true;
 try{
   let result;
   if(d.payment==='crystal'){
     if(!giftRequestId)giftRequestId='GSK-'+crypto.randomUUID().replace(/-/g,'');
     result=await api('/api/giftskin/crystal',{...d,request_id:giftRequestId});
     notice('Tặng Crystal thành công! Quà đang ở Hòm Thư người nhận. Mã thư: '+result.mail_id);
     giftRequestId='';
   }else{
     result=await api('/api/giftskin/bank/create',d);
     notice('Đã tạo đơn GiftSkin '+result.id+' chờ QTV xác nhận tiền. Chưa giao quà.');
   }
   await refreshGiftOrders();
 }catch(e){notice('GiftSkin chưa hoàn tất: '+e.message,false);}
 finally{button.disabled=false;}
};
async function refreshGiftOrders(){
 if(!state.me)return;
 const data=await api('/api/giftskin/orders');
 const root=$('gift-orders');root.replaceChildren();
 for(const o of data.orders||[]){
   const card=txt('article','','player-order');
   card.append(txt('strong',o.skin_name+' → '+o.recipient_name+' ('+o.recipient_public_uid+')'));
   card.append(txt('small',o.id+' · '+Number(o.price_vnd).toLocaleString('vi-VN')+' VNĐ · '+({pending:'Chờ duyệt',approved:'Đã gửi thư',rejected:'Đã từ chối'}[o.status]||o.status),'muted'));
   root.append(card);
 }
 if(!root.children.length)root.append(txt('p','Chưa có đơn GiftSkin chuyển khoản.','muted'));
}
async function refreshGiftAdminOrders(){
 if(!state.admin||!state.panelUnlocked)return;
 const response=await api('/api/giftskin/admin/orders?status=pending');
 const root=$('gift-admin-orders');root.replaceChildren();
 for(const o of response.orders||[]){
   const card=txt('article','','player-order');
   card.append(txt('strong',o.skin_name+' · '+Number(o.price_vnd).toLocaleString('vi-VN')+' VNĐ'));
   card.append(txt('small',o.id+' · Người tặng '+o.sender_uid+' · Người nhận '+o.recipient_public_uid+' / '+o.recipient_server+' · '+o.recipient_name,'muted'));
   for(const [approve,label] of [[true,'Đã nhận tiền · Duyệt'],[false,'Từ chối']]){
     const button=txt('button',label,approve?'primary small':'ghost small');
     button.onclick=async()=>{
       if(!confirm(approve?'Xác nhận đã nhận ĐỦ '+Number(o.price_vnd).toLocaleString('vi-VN')+' VNĐ cho đơn '+o.id+' trước khi gửi quà?':'Từ chối đơn '+o.id+'?'))return;
       button.disabled=true;
       try{await api('/api/giftskin/admin/review',{order_id:o.id,approve},true,true);
         notice(approve?'Đã duyệt GiftSkin, gửi thư đúng người nhận.':'Đã từ chối đơn GiftSkin.');
         await refreshGiftAdminOrders();}
       catch(e){notice(e.message,false);button.disabled=false;}
     };card.append(button);
   }
   root.append(card);
 }
 if(!root.children.length)root.append(txt('p','Không có đơn GiftSkin chờ duyệt.','muted'));
}
$('gift-orders-refresh').onclick=()=>refreshGiftOrders().catch(e=>notice(e.message,false));
$('gift-admin-refresh').onclick=()=>refreshGiftAdminOrders().catch(e=>notice(e.message,false));
$('shop-refresh').onclick=()=>loadPlayerShop().catch(e=>notice(e.message,false));
$('shop-orders-refresh').onclick=()=>refreshShopOrders().catch(e=>notice(e.message,false));
$('shop-search').oninput=()=>{shopPage=0;renderPlayerShop();};
$('shop-group').onchange=()=>{shopPage=0;renderPlayerShop();};
$('shop-prev').onclick=()=>{shopPage--;renderPlayerShop();};
$('shop-next').onclick=()=>{shopPage++;renderPlayerShop();};
$('account-switch').onclick=async()=>{
 if(!confirm('Đăng xuất CHỈ GiftSkin/Giftcode trên website này? Tài khoản game và dữ liệu Neon không thay đổi.'))return;
 try{
   await api('/api/auth/logout',{});
   state.me=null;state.admin=false;state.panelUnlocked=false;state.panelAccess='';state.gmActionKey='';state.accountIdentity='';
   giftVerified=null;giftRequestId='';
   await bootstrap();
   switchView('redeem');
   notice('Đã ngắt tài khoản Studio. Đăng nhập tài khoản đúng bên dưới.');
 }catch(e){notice('Không thể đổi tài khoản: '+e.message,false);}
};

async function start(){
 // Hide all privileged navigation until the server confirms SUPER GM ownership.
 for(const el of document.querySelectorAll('.nav-btn'))el.hidden=!['redeem','shop','gift'].includes(el.dataset.view);
 for(const name of ['create','history','redeem','skins','shop','gift'])$(name+'-view').hidden=true;
 const ticket=new URLSearchParams(location.search).get('ticket');
 let ssoFailure='';
 if(ticket){
   // Drop the one-use bearer ticket from browser history immediately.
   history.replaceState(null,'',location.pathname);
   try{await api('/api/giftcode/sso/exchange',{ticket});}
   catch(e){ssoFailure=e.message||'Vé đăng nhập đã hết hạn';}
 }
 try{await bootstrap();
   if(ssoFailure){
     // An old Studio session must never appear to have been synced successfully.
     state.panelUnlocked=false;state.panelAccess='';state.gmActionKey='';
     notice('Không thể đồng bộ GXB 3: '+ssoFailure+'. Bấm “Đồng bộ với GXB 3” để thử lại.',false);
     if(state.me)switchView('redeem');
   }else if(ticket&&state.me){notice('Đã đồng bộ tài khoản GXB 3: '+$('account-label').textContent+'.');}
 }
 catch(err){
   $('server-status').textContent='Chưa kết nối máy chủ';
   $('login-panel').hidden=false;
   $('page-title').textContent='Liên kết tài khoản GXB 3';
   notice(err.message||'Lỗi kết nối máy chủ',false);
 }
}
start();
})();