'use strict';
// Explicit opt-in: no microphone capture or remote audio before user action.
const SocialVoice=(()=>{
 const el=(tag,cls,t)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(t!==undefined)e.textContent=t;return e;};
 const btn=(t,fn)=>{const b=el('button','gs-btn',t);b.type='button';b.onclick=fn;return b;};
 const endpoint='/api/social-voice/action';
 let session=null,offer=null,root=null,body=null,collapsed=true,busy=false,err='';
 let generation=0;
 function command(s,action){return api(endpoint,{kind:s.kind,room_id:s.id,action,lease:s.lease});}
 function current(s){return session===s&&s.identity===state?.uid+'|'+state?.server_id;}
 function detach(s){for(const a of s.audio.values()){a.pause();a.remove();}s.audio.clear();}
 function cleanup(s){if(!s)return;clearInterval(s.timer);detach(s);s.room.localParticipant.setMicrophoneEnabled(false).catch(()=>{});s.room.disconnect(true).catch(()=>{});}
 function leave(){
  generation++;const s=session;session=null;busy=false;
  if(s){cleanup(s);command(s,'leave').catch(()=>{});}render();
 }
 function ensure(){
  if(root?.isConnected)return;
  root=el('div','social-voice-bubble');
  const toggle=el('button','social-voice-toggle','🎙');toggle.type='button';toggle.setAttribute('aria-label','Mở Voice');toggle.onclick=()=>{collapsed=!collapsed;render();};
  body=el('div','social-voice-panel');root.append(toggle,body);
  (document.querySelector('#app-frame')||document.body).append(root);
 }
 function render(){
  if(!offer){root?.remove();root=body=null;return;}
  ensure();body.hidden=collapsed;body.replaceChildren();
  const s=session;
  body.append(el('b','',offer.label||'Voice trực tuyến'));
  if(err)body.append(el('small','social-voice-error',err));
  if(!s){const b=btn(busy?'Đang kết nối…':'Tham gia Voice',join);b.disabled=busy;body.append(b,el('small','','Mic mặc định tắt'));return;}
  const speakers=Array.from(s.room.activeSpeakers||[]).map(p=>p.name||p.identity);
  const members=1+s.room.remoteParticipants.size;
  body.append(el('small','',members+' đang kết nối · '+s.seats+' ghế Mic'),el('small','',speakers.length?'Đang nói: '+speakers.join(', '):'Chưa có người nói'));
  const mic=btn(s.mic?'Tắt Mic':'Bật Mic',()=>toggleMic(s));mic.disabled=busy;
  const audio=btn(s.speaker?'Tắt Loa':'Bật Loa',()=>toggleSpeaker(s));
  body.append(mic,audio,btn('Rời Voice',leave));
 }
 async function join(){
  if(busy||session||!offer)return;
  if(!window.LivekitClient){err='Thư viện Voice chưa tải';render();return;}
  const target={...offer},gen=++generation;busy=true;err='';render();
  let s;
  try{
   const reply=await api(endpoint,{kind:target.kind,room_id:target.id,action:'join'});
   s={...target,identity:state.uid+'|'+state.server_id,lease:reply.lease,room:new LivekitClient.Room(),audio:new Map(),mic:false,speaker:false,seats:8};
   if(gen!==generation||offer?.id!==target.id)throw Error('Đã đổi phòng');
   session=s;
   const ev=LivekitClient.RoomEvent;
   s.room.on(ev.TrackSubscribed,(track,pub,p)=>{
    if(track.kind!=='audio'||!current(s))return;
    const a=document.createElement('audio');a.muted=!s.speaker;a.autoplay=true;a.hidden=true;track.attach(a);document.body.append(a);s.audio.set(track.sid,a);
    if(s.speaker)a.play().catch(()=>{err='Chạm Bật Loa để nghe';render();});
   });
   s.room.on(ev.TrackUnsubscribed,t=>{const a=s.audio.get(t.sid);if(a){a.pause();a.remove();s.audio.delete(t.sid);}});
   for(const event of [ev.ActiveSpeakersChanged,ev.ParticipantConnected,ev.ParticipantDisconnected])s.room.on(event,()=>{if(current(s))render();});
   s.room.on(ev.Disconnected,()=>{if(session===s){err='Voice đã ngắt kết nối';leave();}});
   await s.room.connect(reply.url,reply.token,{autoSubscribe:true});
   if(!current(s))throw Error('Đã đổi phòng');
   s.timer=setInterval(()=>heartbeat(s),9000);
  }catch(e){err=e.message||'Không thể kết nối Voice';if(session===s)session=null;if(s){cleanup(s);command(s,'leave').catch(()=>{});}}
  finally{if(gen===generation){busy=false;render();}}
 }
 async function heartbeat(s){
  if(!current(s)){if(session===s)leave();return;}
  if(s.ping)return;s.ping=true;
  try{
   const r=await command(s,'heartbeat');if(!current(s))return;
   s.seats=r.seats||8;
   if(s.mic&&!r.mic){await s.room.localParticipant.setMicrophoneEnabled(false);s.mic=false;err='Quyền Mic đã bị thu hồi';}
   render();
  }catch(e){if(current(s)){err=e.message;leave();}}
  finally{s.ping=false;}
 }
 async function toggleMic(s){
  if(!current(s)||busy)return;
  busy=true;err='';render();
  try{
   if(s.mic){await s.room.localParticipant.setMicrophoneEnabled(false);s.mic=false;await command(s,'mic_off');}
   else{
    await command(s,'mic_on');
    for(let i=0;i<20&&!s.room.localParticipant.permissions?.canPublish;i++)await new Promise(r=>setTimeout(r,100));
    // Request OS permission only after a seat was granted.
    try{if(!current(s)||!s.room.localParticipant.permissions?.canPublish)throw Error('Chưa nhận được quyền Mic');await s.room.localParticipant.setMicrophoneEnabled(true,{echoCancellation:true,noiseSuppression:true,autoGainControl:true});}
    catch(e){await command(s,'mic_off').catch(()=>{});throw e;}
    if(!current(s)){await s.room.localParticipant.setMicrophoneEnabled(false);return;}
    s.mic=true;
   }
  }catch(e){err=e.message||'Không thể bật Mic';}
  finally{busy=false;render();}
 }
 async function toggleSpeaker(s){
  if(!current(s))return;
  try{
   if(!s.speaker){await s.room.startAudio();s.speaker=true;for(const a of s.audio.values()){a.muted=false;await a.play();}}
   else{s.speaker=false;for(const a of s.audio.values())a.muted=true;}
  }catch(e){s.speaker=false;err='Thiết bị chưa cho phép phát âm thanh';}
  render();
 }
 function show(kind,id,label){
  if(offer?.kind===kind&&offer?.id===id)return;
  if(session)leave();offer={kind,id,label};collapsed=true;err='';render();
 }
 function hide(kind){
  if(!offer||kind&&offer.kind!==kind)return;
  offer=null;leave();
 }
 window.addEventListener('pagehide',()=>hide());
 setInterval(()=>{if(session&&!current(session))hide();},2000);
 return {show,hide,leave};
})();
