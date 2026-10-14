'use strict';
(()=>{
const $=id=>document.getElementById(id);
const state={me:null,admin:false,catalog:[],basket:{},worlds:[],codes:[],page:0,view:'redeem'};
const limit=16;
const txt=(tag,text,cls)=>{const x=document.createElement(tag);if(cls)x.className=cls;x.textContent=String(text??'');return x;};
const api=async(path,body,gm=false)=>{
 const options={credentials:'same-origin',headers:{'Accept':'application/json'}};
 if(body!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(body);}
 if(gm)options.headers['X-GXB3-GM-Key']=$('gm-key').value;
 const r=await fetch(path,options),data=await r.json().catch(()=>({}));
 if(!r.ok)throw Error(data.error||'Máy chủ gặp lỗi, vui lòng thử lại');
 return data;
};
function notice(msg,ok=true){const el=$('global-status');el.textContent=msg;el.dataset.ok=ok?'1':'0';}
function switchView(view){
 if(!state.admin&&view!=='redeem')view='redeem';
 state.view=view;
 const titles={create:'Tạo Giftcode',history:'Giftcode đã phát hành',redeem:'Đổi Giftcode'};
 $('page-title').textContent=titles[view];
 for(const el of document.querySelectorAll('.nav-btn')){el.classList.toggle('active',el.dataset.view===view);el.hidden=!state.admin&&el.dataset.view!=='redeem';}
 for(const name of ['create','history','redeem'])$(name+'-view').hidden=view!==name||!state.me;
 if(view==='history'&&state.admin)refreshCodes().catch(e=>notice(e.message,false));
}
function updateStats(){
 $('stat-total').textContent=state.codes.length.toLocaleString('vi-VN');
 $('stat-active').textContent=state.codes.filter(c=>c.active&&(!c.expires_at||c.expires_at>Date.now()/1000)&&c.remaining>0).length.toLocaleString('vi-VN');
 $('stat-used').textContent=state.codes.reduce((n,c)=>n+Number(c.used_count||0),0).toLocaleString('vi-VN');
}
async function bootstrap(){
 const m=await api('/api/auth/me');state.me=m.authenticated?m.session:null;state.admin=Boolean(m.is_super_gm);
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
   try{await api('/api/giftcode/admin/revoke',{code:data.code},true);notice('Đã khóa '+data.code);await refreshCodes();}catch(e){notice(e.message,false);}
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
$('verify-key').onclick=async()=>{try{await api('/api/admin/gm/verify-key',{},true);notice('Khóa QTV hợp lệ.');}catch(e){notice(e.message,false);}};
$('create-code').onclick=async()=>{
 const b=$('create-code');if(!Object.keys(state.basket).length){notice('Hãy chọn ít nhất một vật phẩm.',false);return;}
 const expiry=$('expiry').value;
 const payload={code:$('code').value,title:$('title').value,message:$('message').value,server_id:$('world').value,max_uses:Number($('max-uses').value),expires_at:expiry?Math.floor(new Date(expiry).getTime()/1000):0,rewards:state.basket};
 b.disabled=true;
 try{const res=await api('/api/giftcode/admin/create',payload,true);$('new-code').hidden=false;$('created-code').textContent=res.code;notice('Đã tạo giftcode thật trên máy chủ!');$('code').value='';await refreshCodes();}catch(e){notice(e.message,false);}finally{b.disabled=false;}
};
$('copy-code').onclick=()=>copyText($('created-code').textContent);
$('redeem-form').onsubmit=async e=>{
 e.preventDefault();const btn=e.currentTarget.querySelector('button');btn.disabled=true;
 try{const r=await api('/api/giftcode/redeem',{code:$('redeem-code').value});notice(r.message);$('redeem-code').value='';}
 catch(err){notice(err.message,false);}finally{btn.disabled=false;}
};
bootstrap().catch(err=>{notice(err.message,false);$('server-status').textContent='Không kết nối được';});
})();