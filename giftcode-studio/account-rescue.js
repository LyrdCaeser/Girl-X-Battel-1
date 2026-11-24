'use strict';
(()=>{
const form=document.getElementById('rescue'), f=form.elements, feedback=document.getElementById('feedback'), result=document.getElementById('result'), code=document.getElementById('new-code'), target=document.getElementById('target');
function clear(){result.hidden=true;code.textContent='';code.hidden=true;target.textContent='';}
function fields(){const player=f.action.value.startsWith('player_');document.getElementById('player-fields').hidden=!player;for(const key of ['uid','username','verified']){f[key].disabled=!player;f[key].required=player;}clear();}
f.action.addEventListener('change',fields);fields();
document.getElementById('hide').onclick=clear;
window.addEventListener('pagehide',()=>{clear();form.reset();});
form.onsubmit=async e=>{
 e.preventDefault();clear();feedback.textContent='';
 const data=Object.fromEntries(new FormData(form));
 if(!window.confirm('Xác nhận thao tác cứu hộ cho đúng tài khoản?'))return;
 const button=form.querySelector('button[type=submit]');button.disabled=true;
 try{
  const response=await fetch('/api/bridge?route=owner-security%2Faccount-rescue',{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(data)});
  const out=await response.json();
  if(!response.ok||!out.ok)throw Error(typeof out.error==='string'?out.error:'Không thể cứu hộ (HTTP '+response.status+')');
  target.textContent='Đã xử lý: '+out.username+' · '+out.uid;
  if(out.recovery_code){code.textContent='Mã khôi phục mới (chỉ hiển thị lần này): '+out.recovery_code;code.hidden=false;}
  result.hidden=false;feedback.textContent='Thành công.';
 }catch(err){feedback.textContent=err.message||'Không thể kết nối máy chủ';}
 finally{for(const k of ['admin_key','panel_key','gm_key','code'])f[k].value='';button.disabled=false;}
};
})();
