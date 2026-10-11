'use strict';
window.GxbAuth=(()=>{
  let overlay=null,session=null,worlds=[];
  const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  async function request(url,body){
    const r=await fetch(url,{method:body===undefined?'GET':'POST',headers:body===undefined?{}:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body),credentials:'same-origin'});
    const data=await r.json().catch(()=>({}));
    if(!r.ok)throw Error(data.error||'Không thể hoàn tất yêu cầu');
    return data;
  }
  function worldSelect(id){
    const s=document.createElement('select');s.id=id;
    for(const w of worlds.filter(x=>x.status!=='closed')){const o=el('option','',`${w.name} · ${w.server_id}${w.status==='maintenance'?' · Bảo trì':''}`);o.value=w.server_id;o.disabled=w.status!=='online';s.append(o);}
    return s;
  }
  function field(parent,label,id,type='text',placeholder=''){
    const l=el('label','auth-field',label),i=document.createElement('input');i.id=id;i.type=type;i.placeholder=placeholder;i.autocomplete=type==='password'?'current-password':'off';l.append(i);parent.append(l);return i;
  }
  function remove(){overlay?.remove();overlay=null;document.documentElement.classList.remove('auth-locked');}
  function show(){
    remove();document.documentElement.classList.add('auth-locked');overlay=el('div','auth-overlay');
    const panel=el('section','auth-panel');
    const brand=el('div','auth-brand');brand.append(el('small','','GXB 3'),el('h1','','Nữ Thần Chiến Đấu'),el('p','','Đăng nhập để tiếp tục vào game.'));
    panel.append(brand);
    const tabs=el('nav','auth-tabs'),loginTab=el('button','on','Đăng nhập'),registerTab=el('button','','Đăng ký');tabs.append(loginTab,registerTab);panel.append(tabs);
    const body=el('div','auth-body');panel.append(body);
    const status=el('p','auth-status','');panel.append(status);

    function renderLogin(){
      loginTab.classList.add('on');registerTab.classList.remove('on');body.replaceChildren();
      const user=field(body,'Tên đăng nhập','auth-login-user','text','Tên đăng nhập');
      const pass=field(body,'Mật khẩu','auth-login-pass','password','Mật khẩu');
      pass.autocomplete='current-password';
      const wl=el('label','auth-field','Server');wl.append(worldSelect('auth-login-server'));body.append(wl);
      const submit=el('button','auth-primary','Đăng nhập');submit.onclick=async()=>{submit.disabled=true;status.textContent='Đang đăng nhập…';try{await request('/api/auth/login',{username:user.value,password:pass.value,server_id:document.getElementById('auth-login-server').value});location.reload();}catch(e){status.textContent=e.message;submit.disabled=false;}};body.append(submit);
      pass.onkeydown=e=>{if(e.key==='Enter')submit.click();};
    }
    function renderRegister(){
      registerTab.classList.add('on');loginTab.classList.remove('on');body.replaceChildren();
      const user=field(body,'Tên đăng nhập','auth-reg-user','text','4–24 ký tự');
      const email=field(body,'Email (không bắt buộc)','auth-reg-email','email','email@example.com');
      const name=field(body,'Tên Nhân Vật','auth-reg-name','text','Tên hiển thị trong game');
      const pass=field(body,'Mật khẩu','auth-reg-pass','password','Ít nhất 8 ký tự');pass.autocomplete='new-password';
      const confirm=field(body,'Nhập lại mật khẩu','auth-reg-confirm','password','Nhập lại mật khẩu');confirm.autocomplete='new-password';
      const wl=el('label','auth-field','Server đầu tiên');wl.append(worldSelect('auth-reg-server'));body.append(wl);
      const submit=el('button','auth-primary','Tạo tài khoản');
      submit.onclick=async()=>{if(pass.value!==confirm.value){status.textContent='Mật khẩu nhập lại không khớp.';return;}submit.disabled=true;status.textContent='Đang tạo tài khoản…';try{await request('/api/auth/register',{username:user.value,email:email.value,character_name:name.value,password:pass.value,server_id:document.getElementById('auth-reg-server').value});location.reload();}catch(e){status.textContent=e.message;submit.disabled=false;}};body.append(submit);
    }
    loginTab.onclick=renderLogin;registerTab.onclick=renderRegister;renderLogin();
    overlay.append(panel);document.body.append(overlay);
  }
  async function init(){
    try{
      const data=await request('/api/auth/me');worlds=data.worlds||[];session=data.session||null;
      if(!data.authenticated){show();return false;}
      remove();
      queueMicrotask(installAccountControls);
      return true;
    }catch(e){worlds=[];show();return false;}
  }
  function installAccountControls(){
    const settings=document.getElementById('profile-settings-page');if(!settings||settings.querySelector('.auth-account-row'))return;
    const row=el('div','profile-setting-row auth-account-row');const div=el('div');div.append(el('strong','','Tài khoản'),el('small','',session?.account?`${session.account.username} · ${session.account.uid}`:''));
    const out=el('button','auth-small-btn','Đăng xuất');out.onclick=async()=>{try{await request('/api/auth/logout',{});}finally{location.reload();}};row.append(div,out);settings.append(row);

    const serverRow=el('div','profile-setting-row auth-server-row');const host=el('div');host.append(el('strong','','Server / Nhân Vật'),el('small','',session?`${session.account.server_id} · ${session.character_name}`:''));
    const select=worldSelect('auth-account-server');select.value=session?.account?.server_id||'S1';
    const go=el('button','auth-small-btn','Chuyển');go.onclick=async()=>{try{await request('/api/auth/switch-server',{server_id:select.value});location.reload();}catch(e){alert(e.message);}};
    const create=el('button','auth-small-btn','Tạo NV');create.onclick=async()=>{const name=prompt('Tên Nhân Vật ở '+select.value+':','');if(!name)return;try{await request('/api/auth/create-character',{server_id:select.value,character_name:name});location.reload();}catch(e){alert(e.message);}};
    serverRow.append(host,select,go,create);settings.append(serverRow);
  }
  window.GxbAuthReady=init();
  return{request,session:()=>session,worlds:()=>worlds,logout:async()=>{await request('/api/auth/logout',{});location.reload();}};
})();
