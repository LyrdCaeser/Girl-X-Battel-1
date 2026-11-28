'use strict';
(()=>{
 const ua=navigator.userAgent||'';
 const ios=/iPhone|iPad|iPod/i.test(ua)||(/Macintosh/i.test(ua)&&navigator.maxTouchPoints>1);
 const standalone=navigator.standalone===true||matchMedia('(display-mode: standalone)').matches;
 const eligible=ios&&standalone&&!/Android|Windows|CrOS/i.test(ua);
 // Synchronous guard runs before game scripts on /play. No game in browser tabs.
 if(location.pathname==='/play'){
  if(!eligible){location.replace('/');document.documentElement.style.display='none';}
  else document.documentElement.classList.add('gxb-ios-app');
  return;
 }
 async function launch(){
  const msg=document.getElementById('message'),retry=document.getElementById('retry');
  if(!ios||/Android|Windows|CrOS/i.test(ua)){msg.textContent='Phiên bản này chỉ dành cho iPhone và iPad.';return;}
  if(!eligible){msg.textContent='Vui lòng mở game từ biểu tượng trên màn hình chính.';document.getElementById('instructions').hidden=false;return;}
  retry.hidden=true;msg.textContent='Đang kết nối máy chủ…';
  try{
   const response=await fetch('/ios-launch',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({standalone:true,touch:navigator.maxTouchPoints})});
   if(!response.ok)throw Error('launch');
   location.replace('/play');
  }catch(e){msg.textContent='Chưa kết nối được máy chủ. Vui lòng thử lại.';retry.hidden=false;retry.onclick=launch;}
 }
 launch();
})();
