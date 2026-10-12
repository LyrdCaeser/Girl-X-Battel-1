'use strict';
// Platform-specific layout shell. Android/mobile uses the real device viewport;
// desktop uses the full desktop window. Never scale the desktop layout into a phone.
(()=>{
 const ua=navigator.userAgent||'';
 const forceMobile=/GXB3-Android|Android|iPhone|iPod/i.test(ua);
 const coarse=matchMedia('(pointer:coarse)').matches;
 const narrow=matchMedia('(max-width:900px)').matches;

 function mode(){
   return forceMobile || narrow || (coarse && matchMedia('(max-width:900px)').matches) ? 'mobile' : 'desktop';
 }

 function fit(){
   const f=document.getElementById('app-frame');
   if(!f)return;
   const m=mode();
   document.documentElement.classList.toggle('gxb-mobile',m==='mobile');
   document.documentElement.dataset.platform=m;
   document.documentElement.classList.toggle('gxb-desktop',m==='desktop');
   f.dataset.platform=m;
   const vv=window.visualViewport;
   const vw=Math.max(1,Math.round(vv?.width||window.innerWidth||document.documentElement.clientWidth||360));
   const vh=Math.max(1,Math.round(vv?.height||window.innerHeight||document.documentElement.clientHeight||640));
   document.documentElement.style.setProperty('--gxb-vw',vw+'px');
   document.documentElement.style.setProperty('--gxb-vh',vh+'px');
   f.style.setProperty('--frame-scale','1');
   f.style.transform='none';
   f.style.left='0';
   f.style.top='0';
   f.style.width=m==='mobile'?'var(--gxb-vw)':'100vw';
   f.style.height=m==='mobile'?'var(--gxb-vh)':'100dvh';
 }

 addEventListener('resize',fit);
 addEventListener('orientationchange',()=>setTimeout(fit,50));
 window.visualViewport?.addEventListener('resize',fit);
 window.visualViewport?.addEventListener('scroll',fit);
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
