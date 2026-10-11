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
      const submit=el('button','auth-primary','Đăng nhập');submit.onclick=async()=>{submit.disabled=true;status.textContent='Đang đăng nhập…';try{await request('/api/auth/login',{username:user.value,password:pass.value,server_id:document.getElementById('auth-login-server').value});location.reload();}catch(e){status.textContent=e.message;submit.disabled=false;}};
      const forgot=el('button','auth-link','Quên mật khẩu?');forgot.onclick=renderRecovery;body.append(submit,forgot);
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
      submit.onclick=async()=>{if(pass.value!==confirm.value){status.textContent='Mật khẩu nhập lại không khớp.';return;}submit.disabled=true;status.textContent='Đang tạo tài khoản…';try{
        const result=await request('/api/auth/register',{username:user.value,email:email.value,character_name:name.value,password:pass.value,server_id:document.getElementById('auth-reg-server').value});
        body.replaceChildren();loginTab.classList.remove('on');registerTab.classList.remove('on');
        body.append(el('h3','auth-recovery-title','Mã khôi phục tài khoản'));
        body.append(el('p','auth-recovery-note','Lưu mã này ở nơi an toàn. Mã chỉ hiển thị ở bước này và dùng để đặt lại mật khẩu.'));
        const code=el('code','auth-recovery-code',result.recovery_code||'');body.append(code);
        const copy=el('button','auth-primary','Sao chép mã');copy.onclick=async()=>{try{await navigator.clipboard.writeText(code.textContent);status.textContent='Đã sao chép mã khôi phục.';}catch{status.textContent='Hãy sao chép mã thủ công.';}};
        const go=el('button','auth-link','Tôi đã lưu mã · Vào game');go.onclick=()=>location.reload();body.append(copy,go);status.textContent='Tài khoản đã được tạo thành công.';
      }catch(e){status.textContent=e.message;submit.disabled=false;}};body.append(submit);
    }
    function renderRecovery(){
      loginTab.classList.remove('on');registerTab.classList.remove('on');body.replaceChildren();
      body.append(el('h3','auth-recovery-title','Khôi phục mật khẩu'));
      body.append(el('p','auth-recovery-note','Nhập tên đăng nhập và mã khôi phục đã lưu khi tạo tài khoản.'));
      const user=field(body,'Tên đăng nhập','auth-reset-user');
      const code=field(body,'Mã khôi phục','auth-reset-code','text','XXXX-XXXX-XXXX-XXXX');
      const pass=field(body,'Mật khẩu mới','auth-reset-pass','password','Ít nhất 8 ký tự');pass.autocomplete='new-password';
      const confirm=field(body,'Nhập lại mật khẩu','auth-reset-confirm','password');confirm.autocomplete='new-password';
      const reset=el('button','auth-primary','Đặt lại mật khẩu');reset.onclick=async()=>{if(pass.value!==confirm.value){status.textContent='Mật khẩu nhập lại không khớp.';return;}reset.disabled=true;try{await request('/api/auth/reset-password',{username:user.value,recovery_code:code.value,new_password:pass.value});status.textContent='Đã đổi mật khẩu. Các phiên cũ đã bị đăng xuất.';setTimeout(renderLogin,900);}catch(e){status.textContent=e.message;reset.disabled=false;}};
      const back=el('button','auth-link','← Quay lại đăng nhập');back.onclick=renderLogin;body.append(reset,back);
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
    const sessionsBtn=el('button','auth-small-btn','Thiết bị');sessionsBtn.onclick=openSessions;
    const recoveryBtn=el('button','auth-small-btn','Mã khôi phục');recoveryBtn.onclick=rotateRecovery;
    const out=el('button','auth-small-btn','Đăng xuất');out.onclick=async()=>{try{await request('/api/auth/logout',{});}finally{location.reload();}};row.append(div,sessionsBtn,recoveryBtn,out);settings.append(row);

    const serverRow=el('div','profile-setting-row auth-server-row');const host=el('div');host.append(el('strong','','Server / Nhân Vật'),el('small','',session?`${session.account.server_id} · ${session.character_name}`:''));
    const select=worldSelect('auth-account-server');select.value=session?.account?.server_id||'S1';
    const go=el('button','auth-small-btn','Chuyển');go.onclick=async()=>{try{await request('/api/auth/switch-server',{server_id:select.value});location.reload();}catch(e){alert(e.message);}};
    const create=el('button','auth-small-btn','Tạo NV');create.onclick=async()=>{const name=prompt('Tên Nhân Vật ở '+select.value+':','');if(!name)return;try{await request('/api/auth/create-character',{server_id:select.value,character_name:name});location.reload();}catch(e){alert(e.message);}};
    serverRow.append(host,select,go,create);settings.append(serverRow);
  }

  async function rotateRecovery(){
    try{
      const r=await request('/api/auth/recovery-code',{});
      const code=r.recovery_code||'';
      const modal=el('div','auth-device-overlay'),box=el('section','auth-device-box');
      box.append(el('h3','','Mã khôi phục mới'),el('p','auth-recovery-note','Mã cũ đã hết hiệu lực. Hãy lưu mã mới này ngay.'));
      const c=el('code','auth-recovery-code',code);box.append(c);
      const copy=el('button','auth-primary','Sao chép mã');copy.onclick=()=>navigator.clipboard.writeText(code).catch(()=>{});
      const close=el('button','auth-link','Đóng');close.onclick=()=>modal.remove();box.append(copy,close);modal.append(box);document.body.append(modal);
    }catch(e){alert(e.message);}
  }
  async function openSessions(){
    try{
      const data=await request('/api/auth/sessions');
      const modal=el('div','auth-device-overlay'),box=el('section','auth-device-box');box.append(el('h3','','Thiết bị / Phiên đăng nhập'));
      const list=el('div','auth-device-list');
      for(const ss of data.sessions||[]){
        const row=el('article','auth-device-row'),info=el('div');
        info.append(el('b','',ss.current?'Thiết bị hiện tại':'Phiên đăng nhập'),el('span','',ss.user_agent||'Không rõ thiết bị'),el('small','',ss.server_id+' · '+new Date(ss.last_seen*1000).toLocaleString()));
        const revoke=el('button','auth-small-btn',ss.current?'Đăng xuất phiên này':'Thu hồi');revoke.onclick=async()=>{try{await request('/api/auth/session/revoke',{session_id:ss.session_id});if(ss.current)location.reload();else row.remove();}catch(e){alert(e.message);}};
        row.append(info,revoke);list.append(row);
      }
      if(!(data.sessions||[]).length)list.append(el('p','auth-recovery-note','Không có phiên hoạt động.'));
      box.append(list);const close=el('button','auth-link','Đóng');close.onclick=()=>modal.remove();box.append(close);modal.append(box);document.body.append(modal);
    }catch(e){alert(e.message);}
  }

  window.GxbAuthReady=init();
  return{request,session:()=>session,worlds:()=>worlds,logout:async()=>{await request('/api/auth/logout',{});location.reload();}};
})();
