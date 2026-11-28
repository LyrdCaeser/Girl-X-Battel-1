'use strict';
/**
 * S4 Wish real screen recording (no fake static frames, no uploads).
 * Android APK: explicit MediaProjection consent, H.264 MP4 auto-saved to
 * Movies/GXB3 Wish by a foreground service.
 * Desktop browsers: getDisplayMedia + MediaRecorder WebM download.
 * Browsers cannot silently write to a phone's Photos/Gallery app.
 */
const WishRecorder=(()=>{
 let status='idle',method='',media=null,stream=null,chunks=[],busy=false;
 let message='',widget=null,recorderOwned=false;
 const native=()=>window.GXB3WishRecorder;
 const active=()=>status==='recording'||!!native()?.isRecording?.();
 const supported=()=>Boolean(native()?.isSupported?.() ||
      (window.MediaRecorder&&navigator.mediaDevices?.getDisplayMedia));
 const label=()=>({
  idle:'Quay Wish',requesting:'Đang xin quyền…',recording:'Dừng & Lưu Video',
  saving:'Đang lưu…',saved:'Đã lưu video',error:'Quay lại',cancelled:'Quay Wish'
 })[status]||'Quay Wish';
 const toast=text=>{
  if(!text)return;
  if(typeof GirlUI!=='undefined'&&GirlUI.toast)GirlUI.toast(text);
  else console.info('Wish Recorder:',text);
 };
 function update(next,description=''){
  status=next;message=description;
  if(description&&['saved','error','cancelled'].includes(next))toast(description);
  for(const button of document.querySelectorAll('.gxb-wish-record-action')){
   button.textContent=label();
   button.disabled=next==='requesting'||next==='saving';
   button.dataset.state=next;
  }
  paintWidget();
 }
 function paintWidget(){
  const root=window.GxbFrame?.root?.()||document.body;
  if(widget&&!widget.isConnected)widget=null;
  if(!active()&&status!=='saving'){
   widget?.remove();widget=null;return;
  }
  if(!widget){
   widget=document.createElement('div');
   widget.className='gxb-wish-record-widget';
   const label=document.createElement('span');
   label.className='gxb-wish-record-label';
   widget.append(label);
   const stop=document.createElement('button');
   stop.type='button';stop.className='gxb-wish-record-action';
   stop.onclick=()=>stopRecording();
   widget.append(stop);
   root.append(widget);
  }
  widget.querySelector('.gxb-wish-record-label').textContent=
    status==='saving'?'Đang lưu video…':'● REC · Wish S4';
  const button=widget.querySelector('button');
  button.disabled=status==='saving';button.textContent=
    status==='saving'?'Đang lưu…':'Dừng & Lưu';
 }
 function mimeType(){
  const choices=['video/webm;codecs=vp9,opus','video/webm;codecs=vp8,opus',
                 'video/webm;codecs=vp8','video/webm'];
  return choices.find(t=>window.MediaRecorder.isTypeSupported?.(t))||'';
 }
 function saveWebVideo(blob){
  const url=URL.createObjectURL(blob);
  const file=document.createElement('a');
  file.href=url;file.download='GXB3_Wish_S4_'+new Date().toISOString().replace(/[:.]/g,'-')+'.webm';
  file.style.display='none';
  document.body.append(file);
  file.click();
  file.remove();
  setTimeout(()=>URL.revokeObjectURL(url),60000);
 }
 function cleanupBrowser(){
  stream?.getTracks()?.forEach(track=>track.stop());
  stream=null;media=null;chunks=[];
 }
 async function startRecording(){
  if(busy||active())return active();
  if(!supported()){
   update('error','Cần bản APK GXB 3 mới để tự lưu vào Thư viện. Trình duyệt này không hỗ trợ quay màn hình.');
   return false;
  }
  busy=true;
  update('requesting','');
  if(native()?.isSupported?.()){
   method='native';
   try{
    native().start();
    // Android returns asynchronously after its screen capture permission dialog.
    busy=false;return true;
   }catch(e){
    busy=false;update('error','Không mở được chức năng quay Wish trên Android.');
    return false;
   }
  }
  method='browser';
  try{
   // The user must choose the screen/window using the browser's native UI.
   stream=await navigator.mediaDevices.getDisplayMedia({
    video:{frameRate:{ideal:24,max:30}},audio:true
   });
   const mime=mimeType();
   const options=mime?{mimeType:mime,videoBitsPerSecond:4000000}:{videoBitsPerSecond:4000000};
   media=new MediaRecorder(stream,options);
   chunks=[];
   media.ondataavailable=e=>{if(e.data?.size>0)chunks.push(e.data);};
   media.onerror=()=>{cleanupBrowser();update('error','Không ghi được video Wish.');};
   media.onstop=()=>{
    const blob=new Blob(chunks,{type:media?.mimeType||'video/webm'});
    if(blob.size>1024){
     try{saveWebVideo(blob);update('saved','Đã tải video Wish xuống thiết bị. Trên web, hãy mở Tệp tải xuống.');}
     catch(e){update('error','Không tải được video Wish.');}
    }else update('error','Video quá ngắn hoặc không có hình.');
    cleanupBrowser();
   };
   for(const track of stream.getVideoTracks()){
    track.addEventListener('ended',()=>stopRecording(),{once:true});
   }
   media.start(1000);
   recorderOwned=true;
   update('recording','');
   return true;
  }catch(e){
   cleanupBrowser();
   update(e?.name==='NotAllowedError'?'cancelled':'error',
    e?.name==='NotAllowedError'?'Bé đã hủy quyền ghi màn hình.':'Không thể ghi màn hình trên trình duyệt này.');
   return false;
  }finally{busy=false;}
 }
 function stopRecording(){
  if(status==='requesting'){
   toast('Hãy xác nhận hoặc hủy hộp thoại quyền quay màn hình trước.');
   return;
  }
  if(!active())return;
  update('saving','');
  if(method==='native'||native()?.isRecording?.()){
   try{native().stop();}catch(e){update('error','Không dừng được ghi hình trên Android.');}
  }else if(media?.state==='recording'){
   try{media.requestData();media.stop();}
   catch(e){cleanupBrowser();update('error','Không kết thúc được video.');}
  }
 }
 function finishWish(){
  // Only recordings deliberately started from this S4 Wish UI are stopped.
  // Saves automatically when the last goddess/skin reveal is closed or skipped.
  if(recorderOwned&&active())stopRecording();
  recorderOwned=false;
 }
 function mount(parent){
  // Recover an active Android foreground recording after WebView recreation.
  if(status==='idle'&&native()?.isRecording?.()){
   recorderOwned=true;method='native';update('recording');
  }
  const wrap=document.createElement('div');
  wrap.className='gxb-wish-record-controls';
  const button=document.createElement('button');
  button.type='button';button.className='gxb-wish-record-action';
  button.textContent=active()?'Dừng & Lưu Video':label();
  button.onclick=()=>active()?stopRecording():startRecording();
  const hint=document.createElement('small');
  hint.textContent=native()?.isSupported?.()?
   'Bấm Quay Wish → cấp quyền Android → nhận quà. Video MP4 tự lưu vào Thư viện khi Wish kết thúc.':
   'Dùng APK Android mới để tự lưu vào Thư viện; trên máy tính video tải xuống dạng WebM.';
  wrap.append(button,hint);parent.append(wrap);
  if(active())paintWidget();
  return wrap;
 }
 window.addEventListener('gxb3-wish-recording',e=>{
  const data=e.detail||{};
  const next=String(data.state||'error');
  if(next==='recording'){recorderOwned=true;update('recording');}
  else if(['saved','error','cancelled'].includes(next)){
   recorderOwned=false;
   update(next,String(data.message||''));
  }
 });
 // Leave no capture open when a browser tab closes or navigates away.
 window.addEventListener('pagehide',()=>{if(method==='browser'&&active())stopRecording();});
 return {startRecording,stopRecording,finishWish,mount,isRecording:active,supported,
   get status(){return status;}};
})();
