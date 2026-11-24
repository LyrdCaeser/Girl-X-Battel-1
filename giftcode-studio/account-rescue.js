'use strict';
(()=>{
const $=id=>document.getElementById(id);
const form=$('rescue'), f=form.elements, feedback=$('feedback'), result=$('result'), code=$('new-code'), target=$('target');
const picker=$('profile-picker'), list=$('profile-list'), pickerStatus=$('picker-status');
let selected=null,page=0,query='',requestId=0,busy=false;
function clear(){result.hidden=true;code.textContent='';code.hidden=true;target.textContent='';}
function resetSelection(){selected=null;f.verified.checked=false;$('profile-selected').replaceChildren();$('profile-selected').hidden=true;$('profile-open').textContent='Chọn hồ sơ game';$('profile-feedback').textContent='';}
function fields(){const player=f.action.value.startsWith('player_');$('player-fields').hidden=!player;f.verified.disabled=!player;f.verified.required=player;resetSelection();clear();}
function avatarURL(key){key=String(key||'');if(/^custom_[0-9a-f]{32}$/.test(key))return 'https://180-93-111-99.sslip.io/api/profile/photo/'+key+'.webp';if(/^(head|partner_avatar)_\d+$/.test(key))return '/assets/avatar-hd/profile/'+key+'.webp';return '/assets/profile/head_1001.png';}
function el(tag,cls,value){const e=document.createElement(tag);if(cls)e.className=cls;if(value!==undefined)e.textContent=value;return e;}
function profileCard(p,clickable){
 const card=el(clickable?'button':'div','rescue-profile');if(clickable)card.type='button';
 const av=el('span','rescue-avatar'), img=el('img'), frame=el('img');img.alt='';img.src=avatarURL(p.avatar);img.onerror=()=>{img.onerror=null;img.src='/assets/profile/head_1001.png';};frame.alt='';frame.src='/assets/profile/'+(/^frame_\d+$/.test(p.frame||'')?p.frame:'frame_8007')+'.png';frame.onerror=()=>{frame.hidden=true;};av.append(img,frame);
 const info=el('span','rescue-profile-info');info.append(el('strong','',p.character_name),el('small','',p.display_uid+' · '+p.server_id),el('small','','Cấp '+Number(p.level||1)+' · Lực chiến '+Number(p.power||0).toLocaleString('vi-VN')));
 const banned=p.account_status==='banned', charBanned=p.character_status==='banned';
 info.append(el('small',banned||charBanned?'banned':'',banned?'Tài khoản bị khóa':charBanned?'Nhân vật bị khóa · tài khoản hoạt động':'Tài khoản hoạt động'));
 card.append(av,info);if(clickable)card.onclick=()=>{selected=p;f.verified.checked=false;$('profile-selected').replaceChildren(profileCard(p,false));$('profile-selected').hidden=false;$('profile-open').textContent='Đổi hồ sơ';$('profile-feedback').textContent='';picker.close();};return card;
}
async function loadProfiles(nextPage){
 const id=++requestId;list.replaceChildren();pickerStatus.textContent='Đang tải hồ sơ…';$('profile-prev').disabled=true;$('profile-next').disabled=true;
 try{
  const url=new URL('/api/bridge',location.origin);url.searchParams.set('route','owner-security/rescue-profiles');url.searchParams.set('q',query);url.searchParams.set('page',String(nextPage));
  const r=await fetch(url,{credentials:'same-origin',cache:'no-store'}),out=await r.json();if(id!==requestId)return;
  if(!r.ok)throw Error(r.status===401||r.status===403?'Đăng nhập đúng tài khoản SUPER GM tại trang chủ để chọn hồ sơ.':(out.error||'Không tải được hồ sơ'));
  page=nextPage;for(const p of out.profiles||[])list.append(profileCard(p,true));pickerStatus.textContent=list.childElementCount?'Trang '+(page+1)+' · '+list.childElementCount+' hồ sơ':'Không tìm thấy hồ sơ phù hợp.';
  $('profile-prev').disabled=page===0;$('profile-next').disabled=!out.more;
 }catch(err){if(id===requestId)pickerStatus.textContent=err.message;}
}
$('profile-open').onclick=()=>{if(busy)return;query='';$('profile-query').value='';picker.showModal();loadProfiles(0);};
$('profile-close').onclick=()=>picker.close();
$('profile-search').onsubmit=e=>{e.preventDefault();query=$('profile-query').value.trim();loadProfiles(0);};
$('profile-prev').onclick=()=>loadProfiles(Math.max(0,page-1));$('profile-next').onclick=()=>loadProfiles(page+1);
f.action.addEventListener('change',fields);fields();$('hide').onclick=clear;
window.addEventListener('pagehide',()=>{clear();resetSelection();form.reset();});
form.onsubmit=async e=>{
 e.preventDefault();if(busy)return;clear();feedback.textContent='';
 const data=Object.fromEntries(new FormData(form));const player=data.action.startsWith('player_');
 if(player&&!selected){$('profile-feedback').textContent='Hãy chọn hồ sơ game trước khi cứu hộ.';return;}
 if(player){data.uid=selected.uid;data.server_id=selected.server_id;}
 const targetLabel=player?selected.character_name+' · '+selected.display_uid+' · '+selected.server_id:'SUPER GM';
 if(!window.confirm('Xác nhận cứu hộ: '+targetLabel+'?'))return;
 const button=form.querySelector('button[type=submit]');busy=true;button.disabled=true;f.action.disabled=true;$('profile-open').disabled=true;
 try{
  const response=await fetch('/api/bridge?route=owner-security%2Faccount-rescue',{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(data)});
  const out=await response.json();if(!response.ok||!out.ok)throw Error(typeof out.error==='string'?out.error:'Không thể cứu hộ (HTTP '+response.status+')');
  target.textContent='Đã xử lý: '+targetLabel;
  if(out.recovery_code){code.textContent='Mã khôi phục mới (chỉ hiển thị lần này): '+out.recovery_code;code.hidden=false;}
  result.hidden=false;feedback.textContent='Thành công.';resetSelection();
 }catch(err){feedback.textContent=err.message||'Không thể kết nối máy chủ';}
 finally{for(const k of ['admin_key','panel_key','gm_key','code'])f[k].value='';busy=false;button.disabled=false;f.action.disabled=false;$('profile-open').disabled=false;}
};
})();
