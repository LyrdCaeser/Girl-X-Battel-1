'use strict';
window.GxbAuth=(()=>{
  let overlay=null,session=null,worlds=[],isSuperGM=false;
  let s4Cycle=null,s4SyncedAt=0,s4PollBusy=false,s4Kicked=false,s4Badge=null;
  let s4Trial=null,s4TrialSyncedAt=0,s4TrialPollBusy=false,s4KickedReason='';
  const s4Time=()=>s4Cycle?Math.max(0,Math.ceil(Number(s4Cycle.phase_end)-(
    Number(s4Cycle.server_now)+(performance.now()-s4SyncedAt)/1000))):0;
  function s4TrialTime(){
    if(!s4Trial?.active)return 0;
    const elapsed=(performance.now()-s4TrialSyncedAt)/1000;
    return Math.max(0,Math.ceil(Number(s4Trial.remaining_seconds)-
      (s4Cycle?.phase==='open'?elapsed:0)));
  }
  function s4Clock(seconds){
    seconds=Math.max(0,Math.floor(seconds));
    return [Math.floor(seconds/3600),Math.floor(seconds%3600/60),seconds%60]
      .map(x=>String(x).padStart(2,'0')).join(':');
  }
  function selectedS4(){
    return [...document.querySelectorAll('#auth-login-server,#auth-reg-server,#auth-account-server')]
      .some(x=>x.isConnected&&x.value==='S4');
  }
  function selectorNote(select){
    if(!select?.isConnected)return;
    let note=select.parentElement?.querySelector('.auth-s4-cycle-note');
    if(!note){
      note=el('div','auth-s4-cycle-note');
      select.insertAdjacentElement('afterend',note);
    }
    const selected=select.value==='S4';
    note.hidden=!selected;
    if(!selected)return;
    const locked=s4Cycle?.phase==='locked';
    const clock=s4Cycle?s4Clock(s4Time()):'Đang đồng bộ…';
    note.classList.toggle('locked',!!locked);
    const trialActive=s4Trial?.access_mode==='trial'&&s4TrialTime()>0;
    note.replaceChildren(
      el('strong','',locked?'🔒 S4 tạm khóa • 48 giờ':
        '★ S4 • VIP 15 hoặc Chìa Khóa Dùng Thử'),
      el('span','',locked?'Mở lại sau '+clock:
        'Khóa sau '+clock+' (chơi 72 giờ, nghỉ 48 giờ)'),
      ...(locked?[el('small','','S4 sẽ tự mở lại khi hết thời gian. Hãy chọn máy chủ khác để tiếp tục chơi.')]:[]),
      el('small','',trialActive?
        'Chìa Khóa Dùng Thử còn '+s4Clock(s4TrialTime())+
        ' giờ chơi; tạm dừng đếm khi S4 nghỉ 48 giờ.':
        'Cần VIP 15 + chìa khóa vĩnh viễn, hoặc dùng Chìa Khóa S4 Dùng Thử từ Túi Đồ.')
    );
  }
  function showS4Badge(){
    const active=session?.account?.server_id==='S4'&&!s4Kicked&&!overlay;
    if(!active||!s4Cycle||s4Cycle.phase!=='open'){
      s4Badge?.remove();s4Badge=null;return;
    }
    if(!s4Badge){
      s4Badge=el('div','auth-s4-countdown');
      s4Badge.setAttribute('aria-label','Thời gian mở cửa còn lại của S4');
      document.body.append(s4Badge);
    }
    s4Badge.textContent='S4 • Khóa sau '+s4Clock(s4Time())+
      (s4Trial?.access_mode==='trial'?
        '\nDùng thử còn '+s4Clock(s4TrialTime()):'');
  }
  function updateS4Clock(){
    for(const select of document.querySelectorAll(
      '#auth-login-server,#auth-reg-server,#auth-account-server'))selectorNote(select);
    const locked=Boolean(s4Cycle?.phase==='locked');
    for(const [id,buttonId] of [['auth-login-server','auth-login-submit'],
                               ['auth-reg-server','auth-reg-submit']]){
      const selector=document.getElementById(id),button=document.getElementById(buttonId);
      if(selector&&button&&!button.dataset.requestBusy)
        button.disabled=selector.value==='S4'&&locked;
    }
    if(session?.account?.server_id==='S4'&&!s4Kicked&&s4Trial?.access_mode==='trial'
       &&s4TrialTime()===0){
      kickToServerLobby(s4Cycle,'trial_expired');
    }
    if(session?.account?.server_id==='S4'&&!s4Kicked&&s4Cycle&&
       (locked||s4Time()===0))kickToServerLobby(s4Cycle);
    showS4Badge();
  }
  async function syncS4Cycle(){
    if(s4PollBusy)return;
    s4PollBusy=true;
    try{
      const info=await request('/api/s4/cycle');
      if(info.server_id!=='S4')return;
      s4Cycle=info;s4SyncedAt=performance.now();
      updateS4Clock();
    }catch(e){console.warn('Không cập nhật được đồng hồ S4',e);}
    finally{s4PollBusy=false;}
  }
  async function syncS4Trial(){
    if(s4TrialPollBusy||!session?.account)return;
    s4TrialPollBusy=true;
    try{
      const data=await request('/api/s4/trial');
      s4Trial=data;s4TrialSyncedAt=performance.now();
      updateS4Clock();
    }catch(e){console.warn('Không cập nhật được thời gian chìa khóa S4',e);}
    finally{s4TrialPollBusy=false;}
  }
  function kickToServerLobby(cycle,reason=''){
    if(session?.account?.server_id!=='S4'||s4Kicked)return;
    s4KickedReason=reason;
    if(cycle?.server_id==='S4'){
      s4Cycle=cycle;s4SyncedAt=performance.now();
    }
    s4Kicked=true;
    s4Badge?.remove();s4Badge=null;
    show();
  }
  function startS4Timers(){
    setInterval(()=>{
      updateS4Clock();
      if(s4Cycle&&s4Time()===0&&!s4PollBusy&&
         (session?.account?.server_id==='S4'||selectedS4()))void syncS4Cycle();
    },1000);
    setInterval(()=>{
      if(session?.account?.server_id==='S4'||selectedS4()){
        void syncS4Cycle();
        void syncS4Trial();
      }
    },15000);
  }

  const REMEMBER_KEY='gxb3:remember-login:v1';
  function remembered(){
    try {const saved=JSON.parse(localStorage.getItem(REMEMBER_KEY)||'null');
      return saved&&saved.remember===true?{
        username:String(saved.username||'').slice(0,24),
        server_id:String(saved.server_id||'S1').slice(0,30)
      }:null;
    } catch {return null;}
  }
  function storeRemember(enabled,username,server_id){
    try{if(enabled)localStorage.setItem(REMEMBER_KEY,JSON.stringify({remember:true,username,server_id}));
      else localStorage.removeItem(REMEMBER_KEY);
    }catch{}
  }
  const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  async function request(url,body){
    const r=await fetch(url,{method:body===undefined?'GET':'POST',headers:body===undefined?{}:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body),credentials:'same-origin'});
    const data=await r.json().catch(()=>({}));
    if(!r.ok)throw Error(data.error||'Không thể hoàn tất yêu cầu');
    return data;
  }
  function worldSelect(id){
    const select=document.createElement('select');select.id=id;
    for(const w of worlds.filter(x=>x.status!=='closed')){
      const special=w.server_id==='S4';
      const label=w.name+' · '+w.server_id+(special?' · VIP 15 / Dùng thử':'')+
        (w.status==='maintenance'?' · Bảo trì':'');
      const option=el('option','',label);
      option.value=w.server_id;option.disabled=w.status!=='online';select.append(option);
    }
    select.addEventListener('change',()=>{
      selectorNote(select);
      updateS4Clock();
      if(select.value==='S4')void syncS4Cycle();
    });
    queueMicrotask(()=>selectorNote(select));
    return select;
  }
  function field(parent,label,id,type='text',placeholder=''){
    const l=el('label','auth-field',label),i=document.createElement('input');i.id=id;i.type=type;i.placeholder=placeholder;i.autocomplete=type==='password'?'current-password':'username';i.addEventListener('input',()=>{l.classList.remove('typing');void l.offsetWidth;l.classList.add('typing');});l.append(i);parent.append(l);return i;
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
      const saved=remembered();if(saved)user.value=saved.username;
      const wl=el('label','auth-field','Máy Chủ');const world=worldSelect('auth-login-server');
      if(s4Kicked&&session?.account?.server_id==='S4')world.value='S4';
      else if(saved&&Array.from(world.options).some(x=>x.value===saved.server_id&&!x.disabled))world.value=saved.server_id;
      wl.append(world);body.append(wl);selectorNote(world);
      const saveLabel=el('label','auth-remember');const save=document.createElement('input');
      save.id='auth-remember-login';save.type='checkbox';save.checked=!!saved;
      saveLabel.append(save,el('span','','Lưu đăng nhập'));
      body.append(saveLabel);
      const submit=el('button','auth-primary','Đăng nhập');submit.id='auth-login-submit';
      submit.onclick=async()=>{
        if(world.value==='S4'&&s4Cycle?.phase==='locked'){selectorNote(world);return;}
        submit.disabled=true;submit.dataset.requestBusy='1';status.textContent='Đang đăng nhập…';
        try{await request('/api/auth/login',{username:user.value,password:pass.value,server_id:world.value,remember_login:save.checked});storeRemember(save.checked,user.value,world.value);location.reload();}
        catch(e){status.textContent=e.message;submit.disabled=false;}
        finally{delete submit.dataset.requestBusy;}
      };
      const forgot=el('button','auth-link','Quên mật khẩu?');forgot.onclick=renderRecovery;body.append(submit,forgot);
      if(s4Kicked&&session?.account?.server_id==='S4'){
        if(s4KickedReason==='trial_expired')
          status.textContent='Chìa Khóa S4 Dùng Thử đã hết hạn. '
            +'Hãy chọn máy chủ thường để tiếp tục chơi hoặc kích hoạt chìa khóa khác.';
        const leave=el('button','auth-s4-switch','Chọn máy chủ thường để tiếp tục chơi');
        leave.type='button';
        leave.onclick=async()=>{
          if(world.value==='S4'){status.textContent='Chọn máy chủ thường khác S4 để tiếp tục chơi.';return;}
          leave.disabled=true;
          try{await request('/api/auth/switch-server',{server_id:world.value});location.reload();}
          catch(e){status.textContent=e.message;leave.disabled=false;}
        };
        body.append(leave);
      }
      updateS4Clock();
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
      const submit=el('button','auth-primary','Tạo tài khoản');submit.id='auth-reg-submit';
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
    updateS4Clock();
  }
  async function init(){
    try{
      const data=await request('/api/auth/me');worlds=data.worlds||[];session=data.session||null;isSuperGM=!!data.is_super_gm;
      if(data.s4_cycle?.server_id==='S4'){
        s4Cycle=data.s4_cycle;s4SyncedAt=performance.now();
      }
      if(data.s4_trial){s4Trial=data.s4_trial;s4TrialSyncedAt=performance.now();}
      if(!data.authenticated){show();return false;}
      if(session?.account?.server_id==='S4'&&session?.s4_access_expired){
        s4Kicked=true;s4KickedReason='trial_expired';show();return false;
      }
      if(session?.account?.server_id==='S4'&&s4Cycle?.phase==='locked'){
        s4Kicked=true;show();return false;
      }
      remove();queueMicrotask(installAccountControls);updateS4Clock();
      return true;
    }catch(e){worlds=[];show();return false;}
  }
  function installAccountControls(){
    const settings=document.getElementById('profile-settings-page');if(!settings||settings.querySelector('.auth-account-row'))return;
    const infoPage=document.getElementById('profile-info-page');
    const oldGM=document.getElementById('gxb3-profile-supergm');oldGM?.remove();
    if(isSuperGM&&infoPage){
      const gm=el('button','profile-primary gxb3-supergm-entry','GM Tools');
      gm.id='gxb3-profile-supergm';gm.type='button';
      gm.onclick=async()=>{try{await window.AdminPanel?.open();}catch(e){window.GirlUI?.notice?.(e.message,{title:'Quản trị'});}};
      infoPage.append(gm);
    }
    const row=settings.querySelector('.profile-setting-row:not(.auth-server-row)')||el('div','profile-setting-row');const icon=row.querySelector('img');row.classList.add('auth-account-row');row.replaceChildren();if(icon)row.append(icon);const div=el('div');div.append(el('strong','','Tài khoản'),el('small','',session?.account?`${session.account.username} · ${session.account.display_uid||session.account.uid}`:''));
    const sessionsBtn=el('button','auth-small-btn','Thiết bị');sessionsBtn.onclick=openSessions;
    const recoveryBtn=el('button','auth-small-btn','Mã khôi phục');recoveryBtn.onclick=rotateRecovery;
    const out=el('button','auth-small-btn','Đăng xuất');out.onclick=async()=>{try{await request('/api/auth/logout',{});}finally{location.reload();}};row.append(div,sessionsBtn,recoveryBtn,out);if(!row.isConnected)settings.append(row);

    const serverRow=el('div','profile-setting-row auth-server-row');const host=el('div');host.append(el('strong','','Server / Nhân Vật'),el('small','',session?`${session.account.server_id} · ${session.character_name}`:''));
    const select=worldSelect('auth-account-server');select.value=session?.account?.server_id||'S1';
    const go=el('button','auth-small-btn','Chuyển');go.onclick=async()=>{try{await request('/api/auth/switch-server',{server_id:select.value});location.reload();}catch(e){GirlUI.notice(e.message,{title:'Thông Báo Tài Khoản'});}};
    const create=el('button','auth-small-btn','Tạo NV');create.onclick=async()=>{const name=await GirlUI.promptText('Tên Nhân Vật ở '+select.value+':',{title:'Tạo Nhân Vật',value:'',maxLength:24,minLength:1});if(!name)return;try{await request('/api/auth/create-character',{server_id:select.value,character_name:name});location.reload();}catch(e){GirlUI.notice(e.message,{title:'Thông Báo Tài Khoản'});}};
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
    }catch(e){GirlUI.notice(e.message,{title:'Thông Báo Tài Khoản'});}
  }
  async function openSessions(){
    try{
      const data=await request('/api/auth/sessions');
      const modal=el('div','auth-device-overlay'),box=el('section','auth-device-box');box.append(el('h3','','Thiết bị / Phiên đăng nhập'));
      const list=el('div','auth-device-list');
      for(const ss of data.sessions||[]){
        const row=el('article','auth-device-row'),info=el('div');
        info.append(el('b','',ss.current?'Thiết bị hiện tại':'Phiên đăng nhập'),el('span','',ss.user_agent||'Không rõ thiết bị'),el('small','',ss.server_id+' · '+new Date(ss.last_seen*1000).toLocaleString()));
        const revoke=el('button','auth-small-btn',ss.current?'Đăng xuất phiên này':'Thu hồi');revoke.onclick=async()=>{try{await request('/api/auth/session/revoke',{session_id:ss.session_id});if(ss.current)location.reload();else row.remove();}catch(e){GirlUI.notice(e.message,{title:'Thông Báo Tài Khoản'});}};
        row.append(info,revoke);list.append(row);
      }
      if(!(data.sessions||[]).length)list.append(el('p','auth-recovery-note','Không có phiên hoạt động.'));
      box.append(list);const close=el('button','auth-link','Đóng');close.onclick=()=>modal.remove();box.append(close);modal.append(box);document.body.append(modal);
    }catch(e){GirlUI.notice(e.message,{title:'Thông Báo Tài Khoản'});}
  }

  window.GxbAuthReady=init();
  startS4Timers();
  return{request,session:()=>session,isSuperGM:()=>isSuperGM,worlds:()=>worlds,
         kickToServerLobby,refreshS4Cycle:syncS4Cycle,refreshS4Trial:syncS4Trial,
         logout:async()=>{await request('/api/auth/logout',{});location.reload();}};
})();
