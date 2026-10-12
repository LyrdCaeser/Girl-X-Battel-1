'use strict';
// Platform-specific layout shell. Android/mobile uses the real device viewport;
// desktop uses the full desktop window. Never scale the desktop layout into a phone.
(()=>{
 const ua=navigator.userAgent||'';
 const forceMobile=/GXB3-Android/i.test(ua);
 const coarse=matchMedia('(pointer:coarse)').matches;
 const narrow=matchMedia('(max-width:700px)').matches;

 function mode(){
   return forceMobile || (coarse && narrow) ? 'mobile' : 'desktop';
 }

 function fit(){
   const f=document.getElementById('app-frame');
   if(!f)return;
   const m=mode();
   document.documentElement.classList.toggle('gxb-mobile',m==='mobile');
   document.documentElement.classList.toggle('gxb-desktop',m==='desktop');
   f.dataset.platform=m;
   f.style.setProperty('--frame-scale','1');
   f.style.transform='none';
   f.style.left='0';
   f.style.top='0';
   f.style.width='100vw';
   f.style.height='100dvh';
 }

 addEventListener('resize',fit);
 addEventListener('orientationchange',()=>setTimeout(fit,50));
 document.addEventListener('DOMContentLoaded',fit);

 const nativeScroll=window.scrollTo.bind(window);
 window.scrollTo=function(a,b){
   const r=document.getElementById('game-root');
   if(!r)return nativeScroll(a,b);
   if(typeof a==='object')r.scrollTo(a);
   else r.scrollTo(a||0,b||0);
 };

 window.GxbFrame={
   root:()=>document.getElementById('app-frame')||document.body,
   fit,
   mode
 };
})();
