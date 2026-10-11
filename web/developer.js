function refreshDeveloper(){
  const enabled=!!state.developer;
  $('developer-status').textContent=enabled?'Đã đăng nhập QTV.':'Nhập khóa QTV để mở bảng quản trị Local.';
  $('developer-toggle').textContent=enabled?'Mở Bảng QTV':'Đăng nhập QTV';
  $('developer-key-wrap').hidden=enabled;
  $('developer-key').value=adminKey;
  $('developer-message').textContent='';
}

$('dev-open').addEventListener('click',async()=>{
  if(developerMode&&state&&state.developer){
    if(window.AdminPanel)await AdminPanel.open();
    return;
  }
  refreshDeveloper();
  $('developer-dialog').showModal();
});
$('developer-close').addEventListener('click',()=>$('developer-dialog').close());

$('developer-toggle').addEventListener('click',async()=>{
  try{
    if(!developerMode){
      const candidate=$('developer-key').value.trim();
      if(!candidate)throw Error('Vui lòng nhập khóa QTV.');
      adminKey=candidate;
      sessionStorage.setItem('gxb2-admin-key',adminKey);
      await api('/api/admin/check',{});
      developerMode=true;
      sessionStorage.setItem('gxb2-developer','1');
      state=await api('/api/state');
      dailyQuizResult=towerResult=null;
      loadFormation();
      selectedStage=Math.min(state.next_stage,30);
      render();
    }
    $('developer-dialog').close();
    if(window.AdminPanel)await AdminPanel.open();
  }catch(e){
    developerMode=false;
    adminKey='';
    sessionStorage.removeItem('gxb2-admin-key');
    sessionStorage.setItem('gxb2-developer','0');
    $('developer-message').textContent=(e.message==='QTV_KEY_INVALID'||e.message==='QTV_KEY_REQUIRED')?'Khóa QTV không đúng.':e.message;
  }
});

// Load the Vietnamese translation layer after the game modules are ready.
if (!document.querySelector('script[data-gxb2-i18n]')) {
  const viScript = document.createElement('script');
  viScript.src = '/i18n-vi.js';
  viScript.defer = true;
  viScript.dataset.gxb2I18n = '1';
  document.head.appendChild(viScript);
}
