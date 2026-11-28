'use strict';
// Basic room UI used by the voice feature. All membership is server-authorized.
const SocialBar=(()=>{
 const el=(tag,cls,t)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(t!==undefined)e.textContent=t;return e;};
 const btn=(t,fn)=>{const e=el('button','gs-btn',t);e.type='button';e.onclick=fn;return e;};
 const endpoint='/api/social-bar/action';
 let panel=null,identity='',origin='',rid='',scope='',busy=false,voice=false,rooms=[],messageBox=null,membersBox=null,entry=null,error=null,rendered='',epoch=0;
 const call=(action,opts={})=>api(endpoint,{action,room_id:rid,...opts});
 const current=()=>panel?.win.isConnected&&identity===state?.uid+'|'+state?.server_id&&view===origin;
 const notice=e=>{if(error)error.textContent=e?.message||String(e);};
 async function leave(){
  const old=rid;rid='';epoch++;SocialVoice.hide('bar');
  if(old)await api(endpoint,{action:'leave',room_id:old}).catch(()=>{});
 }
 async function open(){
  if(!state?.social_bar_enabled||!['home','settings-menu'].includes(view))return;
  await leave();identity=state.uid+'|'+state.server_id;origin=view;scope=state.server_id;
  panel=GirlUI.win({title:'Quán Bar',cls:'social-bar-win world-rank-win'});
  await refreshRooms();
 }
 async function refreshRooms(){
  if(!current())return;
  try{const r=await api('/api/social-bar/rooms');if(!current())return;rooms=r.rooms||[];voice=!!r.voice_enabled;roomList();}
  catch(e){panel.body.replaceChildren(el('p','',e.message));}
 }
 function roomList(){
  const b=panel.body;b.replaceChildren();
  const tabs=el('div','wr-tabs');
  for(const [k,l] of [[state.server_id,'Phòng Server'],['CROSS','Phòng Liên Server']]){const x=btn(l,()=>{scope=k;roomList();});if(scope===k)x.classList.add('on');tabs.append(x);}
  b.append(tabs);error=el('small','social-bar-error');b.append(error);
  for(const r of rooms.filter(x=>x.scope===scope)){
   const row=el('div','social-bar-row');row.append(el('b','',r.name),el('small','',(r.locked?'🔒 · ':'')+r.online+'/32'),btn('Vào phòng',()=>enter(r)));b.append(row);
  }
  const f=el('div','social-bar-create');const name=el('input');name.placeholder='Tên phòng mới';name.maxLength=48;
  const type=el('select');for(const [value,label] of [['public','Công khai'],['private','Riêng tư'],['guild','Bang Hội'],['friends','Bạn Bè']]){const o=el('option','',label);o.value=value;type.append(o);}
  const pw=el('input');pw.type='password';pw.placeholder='Mật khẩu phòng (nếu riêng tư)';pw.maxLength=64;
  f.append(name,type,pw,btn('Tạo phòng',async()=>{if(busy)return;busy=true;try{const r=await call('create',{name:name.value,scope,kind:type.value,password:pw.value});if(current())await enterRoom(r.room_id,pw.value);}catch(e){notice(e);}finally{busy=false;}}));b.append(f);
 }
 async function enter(r){
  if(busy)return;busy=true;try{let pw='';if(r.locked){pw=await GirlUI.promptText('Nhập mật khẩu hoặc để trống nếu đã được mời',{title:'Vào phòng',minLength:0,maxLength:64});if(pw===null||pw===undefined)return;}await enterRoom(r.id,pw);}catch(e){notice(e);}finally{busy=false;}
 }
 async function enterRoom(id,pw){
  const r=await call('enter',{room_id:id,password:pw});if(!current())return;
  rid=r.room.id;epoch++;rendered='';roomView(r.room);await poll();
 }
 function portraitLayer(key,cls,fallback){
  const image=el('img',cls);image.alt='';image.draggable=false;
  image.src=profileAsset(key);
  image.onerror=()=>{image.onerror=null;image.src='/assets/profile/'+fallback+'.png';};
  return image;
 }
 function avatarNode(m){
  const wrap=el('span','social-bar-avatar');
  const avatar=/^(?:(?:head|partner_avatar)_\d{4,9}|custom_[0-9a-f]{32})$/.test(m.avatar||'')?m.avatar:'head_1001';
  const frame=/^frame_\d{4,9}$/.test(m.frame||'')?m.frame:'frame_8007';
  wrap.append(portraitLayer(avatar,'social-bar-face','head_1001'),portraitLayer(frame,'social-bar-frame','frame_8007'));
  wrap.dataset.avatar=avatar;wrap.dataset.frame=frame;return wrap;
 }
 function roomView(room){
  const b=panel.body;b.replaceChildren();
  const top=el('div','social-bar-row');top.append(el('b','',room.name),btn('Rời phòng',async()=>{await leave();await refreshRooms();}));b.append(top);
  membersBox=el('small','social-bar-members');error=el('small','social-bar-error');messageBox=el('div','social-bar-messages');b.append(membersBox,error,messageBox);
  const form=el('form','social-bar-compose');entry=el('input');entry.placeholder='Nhắn tin…';entry.maxLength=500;
  const send=btn('Gửi',()=>sendText());const picture=el('input');picture.type='file';picture.accept='image/png,image/jpeg,image/webp';picture.hidden=true;
  const pic=btn('Ảnh',()=>picture.click());
  picture.onchange=async()=>{const file=picture.files?.[0];if(!file)return;if(file.size>450000){notice('Chọn ảnh dưới 450 KB');picture.value='';return;}try{const raw=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(String(reader.result).split(',')[1]);reader.onerror=reject;reader.readAsDataURL(file);});await sendText(raw);}catch(e){notice(e);}finally{picture.value='';}};
  form.onsubmit=e=>{e.preventDefault();sendText();};form.append(entry,send,pic,picture);b.append(form);
 }
 async function sendText(image=''){
  if(busy||!rid)return;busy=true;try{await call('send',{text:entry.value,image});entry.value='';rendered='';}catch(e){notice(e);}finally{busy=false;poll();}
 }
 let polling=false;
 async function poll(){
  if(!current()){if(rid)await leave();return;}
  if(!rid||polling)return;polling=true;const gen=epoch;
  try{
   const data=await call('poll');if(!current()||gen!==epoch)return;
   if(data.voice_enabled)SocialVoice.show('bar',rid,'Voice · '+data.room.name);else SocialVoice.hide('bar');
   membersBox.textContent=data.members.length+'/32 · '+data.members.map(x=>x.name+' ('+x.world+')').join(', ');
   const fingerprint=data.messages.map(m=>m.id).join('|');
   if(fingerprint===rendered){
    for(const [i,m] of data.messages.entries()){
     const old=messageBox.children[i]?.querySelector('.social-bar-avatar');
     if(old&&(old.dataset.avatar!==(m.avatar||'head_1001')||old.dataset.frame!==(m.frame||'frame_8007')))old.replaceWith(avatarNode(m));
    }
    return;
   }
   rendered=fingerprint;
   messageBox.replaceChildren();
   for(const m of data.messages){
    const row=el('article','social-bar-msg'),content=el('div','social-bar-content');content.append(el('b','',m.name+' · '+m.world),el('p','',m.text));row.append(avatarNode(m),content);
    if(m.kind==='image'){const load=btn('Xem ảnh',async()=>{try{const r=await call('image',{message_id:m.id});if(!current()||gen!==epoch)return;const i=el('img');i.src='data:image/webp;base64,'+r.image;i.alt='Ảnh chia sẻ';load.replaceWith(i);}catch(e){notice(e);}});content.append(load);}
    messageBox.append(row);
   }
   messageBox.scrollTop=messageBox.scrollHeight;
  }catch(e){if(current()&&gen===epoch){notice(e);await leave();await refreshRooms();}}
  finally{polling=false;}
 }
 setInterval(poll,2000);
 return {open};
})();
