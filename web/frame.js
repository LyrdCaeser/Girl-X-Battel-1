'use strict';
// Fixed-size app frame (GXB2-UI-FRAME-001): every screen is laid out on one 480×853 (9:16) canvas, like the
// original fixed-resolution client, and the whole canvas is scaled to fit the window. Fixed-position bars and
// overlays inside #app-frame are anchored to the canvas because the frame has a transform (containing block).
(()=>{
 const W=480,H=853;
 function fit(){const f=document.getElementById('app-frame');if(!f)return;const s=Math.min(innerWidth/W,innerHeight/H);f.style.setProperty('--frame-scale',s);f.style.left=Math.max(0,(innerWidth-W*s)/2)+'px';f.style.top=Math.max(0,(innerHeight-H*s)/2)+'px';}
 addEventListener('resize',fit);document.addEventListener('DOMContentLoaded',fit);
 // Screens used window.scrollTo; the scrolling element is now #game-root.
 const nativeScroll=window.scrollTo.bind(window);
 window.scrollTo=function(a,b){const r=document.getElementById('game-root');if(!r)return nativeScroll(a,b);if(typeof a==='object')r.scrollTo(a);else r.scrollTo(a||0,b||0);};
 window.GxbFrame={root:()=>document.getElementById('app-frame')||document.body,fit};
})();
