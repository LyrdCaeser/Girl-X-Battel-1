function refreshDeveloper(){
  const enabled=!!state.developer;
  $('developer-status').textContent=enabled?"Separate test save. Your regular save is preserved.":"Activate a separate test save to experiment.";
  $('developer-toggle').textContent=enabled?"Back to my save":"Enable Developer Mode";
  $('developer-tools').hidden=!enabled;
  $('developer-key-wrap').hidden=enabled;
  $('developer-key').value=adminKey;
  $('developer-message').textContent='';
  const select=$('developer-girl');
  if(!select.childElementCount)for(const girl of girlsCatalog){
    const option=node('option','',`${girl.name} · ${girl.stars}★ · ${girl.id}`);
    option.value=girl.id;select.append(option);
  }
}

$('dev-open').addEventListener('click',()=>{refreshDeveloper();$('developer-dialog').showModal();});
$('developer-close').addEventListener('click',()=>$('developer-dialog').close());

$('developer-toggle').addEventListener('click',async()=>{
  const wasDeveloper=developerMode;
  try{
    if(!wasDeveloper){
      const candidate=$('developer-key').value.trim();
      if(!candidate)throw Error('Vui lòng nhập khóa QTV.');
      adminKey=candidate;
      sessionStorage.setItem('gxb2-admin-key',adminKey);
      await api('/api/admin/check',{});
      developerMode=true;
      sessionStorage.setItem('gxb2-developer','1');
    }else{
      developerMode=false;
      sessionStorage.setItem('gxb2-developer','0');
    }
    state=await api('/api/state');
    dailyQuizResult=towerResult=null;
    loadFormation();
    selectedStage=Math.min(state.next_stage,30);
    showView('home');render();refreshDeveloper();
  }catch(e){
    developerMode=wasDeveloper;
    sessionStorage.setItem('gxb2-developer',developerMode?'1':'0');
    if(!wasDeveloper){adminKey='';sessionStorage.removeItem('gxb2-admin-key');}
    $('developer-message').textContent=e.message==='QTV_KEY_INVALID'?'Khóa QTV không đúng.':e.message;
  }
});

for(const button of document.querySelectorAll('[data-dev-action]'))button.addEventListener('click',async()=>{
  button.disabled=true;
  try{
    const data=await api('/api/developer',{
      action:button.dataset.devAction,
      table_id:Number($('developer-girl').value),
      count:Number($('developer-count').value),
      level:Number($('developer-level').value),
      floor:Number($('developer-floor').value)
    });
    state=data.state;loadFormation();render();
    $('developer-message').textContent="Applied to the developer save.";
  }catch(e){
    if(e.message==='QTV_KEY_REQUIRED'||e.message==='QTV_KEY_INVALID'){
      developerMode=false;adminKey='';
      sessionStorage.removeItem('gxb2-admin-key');
      sessionStorage.setItem('gxb2-developer','0');
      $('developer-message').textContent='Phiên QTV đã hết hoặc khóa không hợp lệ. Hãy nhập lại khóa.';
      refreshDeveloper();
    }else $('developer-message').textContent=e.message;
  }finally{button.disabled=false;}
});

// Load the Vietnamese translation layer after the game modules are ready.
if (!document.querySelector('script[data-gxb2-i18n]')) {
  const viScript = document.createElement('script');
  viScript.src = '/i18n-vi.js';
  viScript.defer = true;
  viScript.dataset.gxb2I18n = '1';
  document.head.appendChild(viScript);
}
