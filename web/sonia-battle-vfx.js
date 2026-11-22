'use strict';
/* Lyr Sonia's four native battle cues. The choreography and colour motifs
 * follow the supplied "lyr_sonia_4_skills_vfx_v3" configuration. Rendering
 * is on the existing combat field; it does not deal damage or write state.
 * Render at half resolution to keep Android WebView responsive. */
const SoniaBattleVFX=(()=>{
 const ID=758001;
 const SKILLS=Object.freeze({
  75800100:{kind:'siphon',duration:1450,impact:500},
  75800101:{kind:'orb',duration:2850,impact:1350},
  75800102:{kind:'siphon',duration:1450,impact:500},
  75800103:{kind:'guard',duration:1450,impact:460},
  75800104:{kind:'collapse',duration:2750,impact:1350}
 });
 const hex=['#ffffff','#ffd97d','#d9a6ff','#ff4d94','#a84df3','#dc294f'];
 const pi=Math.PI,clamp=(v)=>Math.max(0,Math.min(1,v));
 function ease(t){t=clamp(t);return t*t*(3-2*t);}
 function polar(r,a){return [Math.cos(a)*r,Math.sin(a)*r];}
 function glow(g,x,y,r,color,alpha=1){
  if(!Number.isFinite(x+y+r)||r<=0)return;
  const grad=g.createRadialGradient(x,y,0,x,y,r);
  grad.addColorStop(0,color);grad.addColorStop(.16,color);grad.addColorStop(1,'transparent');
  g.globalAlpha=Math.max(0,Math.min(1,alpha));
  g.fillStyle=grad;g.beginPath();g.arc(x,y,r,0,pi*2);g.fill();g.globalAlpha=1;
 }
 function ring(g,x,y,r,color,width=3,a=1,aspect=1){
  if(r<1)return;
  g.beginPath();g.ellipse(x,y,r,r*aspect,0,0,pi*2);g.strokeStyle=color;
  g.globalAlpha=clamp(a);g.lineWidth=width;g.stroke();g.globalAlpha=1;
 }
 function line(g,x,y,x2,y2,color,width=4,a=1){
  g.beginPath();g.moveTo(x,y);g.lineTo(x2,y2);g.lineWidth=width;g.strokeStyle=color;
  g.globalAlpha=clamp(a);g.stroke();g.globalAlpha=1;
 }
 function petal(g,cx,cy,len,width,angle,color,alpha=1){
  g.save();g.translate(cx,cy);g.rotate(angle);g.globalAlpha=clamp(alpha);
  g.fillStyle=color;g.beginPath();g.moveTo(0,0);
  g.bezierCurveTo(-width,-len*.3,-width*.8,-len*.75,0,-len);
  g.bezierCurveTo(width*.8,-len*.75,width,-len*.3,0,0);
  g.fill();g.restore();
 }
 function star(g,x,y,r,color,alpha=1){
  g.save();g.translate(x,y);g.globalAlpha=clamp(alpha);g.fillStyle=color;
  g.beginPath();g.moveTo(0,-r);g.quadraticCurveTo(r*.18,-r*.18,r,0);
  g.quadraticCurveTo(r*.18,r*.18,0,r);g.quadraticCurveTo(-r*.18,r*.18,-r,0);
  g.quadraticCurveTo(-r*.18,-r*.18,0,-r);g.fill();g.restore();
 }
 function flower(g,x,y,r,progress,crimson=false){
  const bloom=ease(progress),palette=crimson?['#8a123b','#ff3572','#ffb9a6']:['#4bb2ed','#b279fb','#fff5d4'];
  glow(g,x,y,r*1.35,crimson?'#e33874':'#b891fc',.21*bloom);
  for(let tier=2;tier>=0;tier--){
   const count=tier===0?9:tier===1?12:16;
   for(let j=0;j<count;j++){
    const theta=2*pi*j/count+(tier===1?pi/12:tier===2?pi/7:0);
    const d=r*(.1+tier*.16)*bloom;
    petal(g,x+Math.sin(theta)*d,y-Math.cos(theta)*d,
      r*(tier===0?.9:tier===1?.74:.56)*bloom,
      r*(tier===0?.19:.14),theta,palette[tier],.86*bloom);
   }
  }
  for(let j=0;j<24;j++){
   const angle=(j/24)*2*pi;
   const d=r*(.18+(j%4)*.06)*bloom;
   line(g,x,y,x+Math.cos(angle)*d,y+Math.sin(angle)*d,'#ffeebd',1.6,bloom*.7);
  }
  star(g,x,y,13*bloom,'#fff8cf',bloom);
 }
 function petalsDrift(g,x,y,elapsed,r,count=55){
  for(let j=0;j<count;j++){
   const a=j*2.399963+elapsed*.34;
   const d=r*(.22+((j*73)%101)/101*1.75)*(.2+elapsed*.25);
   const px=x+Math.cos(a)*d,py=y+Math.sin(a)*d+elapsed*(30+j%7*11);
   petal(g,px,py,6+(j%5)*2,3,a+elapsed,'#ff5d91',Math.max(0,.76-elapsed*.18));
  }
 }
 function wing(g,x,y,angel,phase,p){
  g.save();g.translate(x,y);g.scale(angel?-1:1,1);g.rotate((angel?-1:1)*phase*.35);
  const shades=angel?['#fffaf2','#ffd97d','#caa7ff']:['#5b1b93','#d158ec','#ff4d94'];
  for(let j=0;j<13;j++){
   const a=(-1.3+j*.125)+phase*.6;
   const ox=75+j*12,oy=-25-j*13;
   petal(g,ox,oy,(165-j*5)*p,29,a,shades[j%3],p*.85);
  }
  g.restore();
 }
 function shield(g,x,y,t){
  const a=Math.min(1,t*3);
  ring(g,x,y,125+8*Math.sin(t*5),'#ffd97d',5,.85*a);
  ring(g,x,y,145+6*Math.cos(t*4),'#bd7bff',4,.55*a);
  glow(g,x,y,170,'#a778ff',.18*a);
  wing(g,x-30,y-42,true,Math.max(0,t-.2),a);
  wing(g,x+30,y-42,false,Math.max(0,t-.2),a);
  if(t>.36){
   const fade=clamp(1-(t-.36)/.64);
   for(let i=0;i<95;i++){
    const theta=i*2.4,dist=(t-.36)*(240+(i*17)%170);
    const px=x+Math.cos(theta)*dist,py=y+Math.sin(theta)*dist;
    star(g,px,py,3+i%5,hex[i%hex.length],fade);
   }
  }
 }
 function drawFx(g,fx){
  const t=clamp(fx.elapsed/fx.duration), p=ease(t),{x,y,tx,ty}=fx;
  const tail=clamp((1-t)*4);
  g.save();g.globalCompositeOperation='lighter';
  if(fx.kind==='orb'){
   if(t<.28){
    const intro=clamp(t/.28);glow(g,x,y-185,220,'#ad61ee',intro*.58);
    ring(g,x,y-185,75+intro*100,'#ffd97d',5,intro*.75);
    star(g,x,y-185,35,'#fff4cc',intro);
   }
   if(t>=.2){
    const fall=ease((t-.2)/.29);
    const bx=x+(tx-x)*fall,by=y-155+(ty-y+155)*fall;
    glow(g,bx,by,80+fall*65,'#b343dd',.7*tail);
    ring(g,bx,by,48+fall*60,'#ffe3a3',5,tail);
    for(let i=0;i<3;i++)ring(g,bx,by,64+fall*60,'#bb6cee',2,tail*.6,.26+i*.22);
   }
   if(t>.42){
    const bloom=ease((t-.42)/.27);flower(g,tx,ty,190,bloom,true);
    petalsDrift(g,tx,ty,(t-.42)*3,155,55);
    for(const [px,py]of fx.targets){ring(g,px,py,28+12*Math.sin(t*18),'#f268a3',3,tail*.8);}
   }
  }else if(fx.kind==='siphon'){
   for(let i=0;i<3;i++){
    const target=fx.targets[i%Math.max(1,fx.targets.length)]||[tx+(i-1)*125,ty];
    const a=ease(t*3);const ex=x+(target[0]-x)*a,ey=y+(target[1]-y)*a;
    line(g,x,y-80,ex,ey-65,'#ff85dc',15,tail*.4);
    line(g,x,y-80,ex,ey-65,'#fff2b0',3,tail);
    star(g,ex,ey-65,23,'#ffccf9',tail);
    for(let j=0;j<14;j++){
     const q=(j/14+t*.8)%1,px=target[0]+(x-target[0])*q;
     const py=target[1]-60+(y-target[1]-55)*q+Math.sin(q*6*pi+i)*20;
     star(g,px,py,5+j%4,'#c688ff',tail*.8);
    }
   }
   glow(g,x,y-80,95,'#b57af9',.35*tail);
  }else if(fx.kind==='guard'){
   shield(g,x,y-50,t);
  }else if(fx.kind==='collapse'){
   if(t<.27){ring(g,x,y-250,70+220*t,'#ffd97d',5,t/.27);
    star(g,x,y-250,40,'#ffe3fa',t/.27);}
   if(t>.24){
    const bloom=ease((t-.24)/.35);
    flower(g,tx,ty+105,200,bloom,false);
    for(let j=0;j<4;j++)
     ring(g,tx,ty+106,80+bloom*(90+j*54),'#c9f0ff',4,tail*(.5+j*.08),.36);
    for(let j=0;j<35;j++){
     const a=j*2.4,d=(25+(j*23)%170)*bloom;
     star(g,tx+Math.cos(a)*d,ty+105-Math.sin(a)*30-(t-.24)*110-(j%7)*8,3+j%6,'#eaffff',tail);
    }
   }
   if(t>.46){
    const q=ease((t-.46)/.22);
    glow(g,tx,ty-45,160*q,'#a63cff',.53*tail);
    ring(g,tx,ty-45,160*q,'#ffe6a3',7,tail);
    for(let j=0;j<20;j++){
     const a=j*2*pi/20+t*8,r=45+q*160;
     line(g,tx+Math.cos(a)*r,ty-45+Math.sin(a)*r,
       tx+Math.cos(a+1.3)*10,ty-45+Math.sin(a+1.3)*10,'#de9cff',3,tail);
    }
    star(g,tx,ty-45,42*q,'#fff1b4',tail);
   }
  }
  g.restore();
 }
 function mount(field,units,positions){
  const sonia=new Set((units||[]).filter(u=>Number(u.table_id)===ID).map(u=>Number(u.pos)));
  if(!sonia.size)return {timing:()=>null,play:()=>null,guard:()=>{},speed:()=>{},destroy:()=>{}};
  const canvas=document.createElement('canvas');
  canvas.className='sonia-vfx-canvas';canvas.width=540;canvas.height=960;
  Object.assign(canvas.style,{position:'absolute',inset:'0',width:'100%',height:'100%',
     pointerEvents:'none',zIndex:'1',opacity:'1'});
  field.append(canvas);
  const g=canvas.getContext('2d',{alpha:true});
  // A real Sonia cut-in portrait is already bundled with the game. It is a
  // visual-only fallback when a legacy Spine-specific cut-in is unavailable.
  const portrait=new Image();
  portrait.decoding='async';
  portrait.src='/assets/pictures/758001.webp';
  let raf=0,alive=true,rate=1,last=performance.now(),active=[];
  function xy(pos){const p=positions?.[pos]||[540,960];return [Number(p[0]),1920-Number(p[1])];}
  function start(){
   if(!alive||raf)return;
   last=performance.now();raf=requestAnimationFrame(tick);
  }
  function tick(now){
   raf=0;if(!alive)return;
   const dt=Math.min(100,Math.max(0,now-last))*rate;last=now;
   g.setTransform(.5,0,0,.5,0,0);g.clearRect(0,0,1080,1920);
   active=active.filter(f=>(f.elapsed+=dt)<f.duration);
   for(const f of active){
    // Native-style character cut-in on ultimate and Chaos Collapse only.
    if((f.kind==='orb'||f.kind==='collapse')&&f.elapsed<720&&portrait.complete&&portrait.naturalWidth){
     const alpha=clamp(Math.min(f.elapsed/190,(720-f.elapsed)/230))*.82;
     g.save();g.globalAlpha=alpha;
     g.fillStyle='rgba(35,11,77,0.55)';g.fillRect(0,250,1080,630);
     g.drawImage(portrait,15,240,460,615);
     g.fillStyle='#fff0d5';g.font='bold 45px sans-serif';
     g.fillText(f.kind==='orb'?'TINH CẦU HỖN MANG':'QUY LUẬT SỤP ĐỔ',445,660,610);
     g.restore();
    }
    drawFx(g,f);
   }
   if(active.length)raf=requestAnimationFrame(tick);
  }
  function fire(kind,cas,targets){
   if(!sonia.has(Number(cas))||!alive)return null;
   const s=typeof kind==='number'?SKILLS[kind]:Object.values(SKILLS).find(e=>e.kind===kind);
   if(!s)return null;
   const [x,y]=xy(cas);
   const pts=(targets||[]).filter(n=>Number(n)!==Number(cas)).map(xy);
   const opposite=(units||[]).filter(u=>(u.pos>6)!==(cas>6)).map(u=>xy(u.pos));
   const enemy=pts.length?pts:opposite;
   const tx=enemy.length?enemy.reduce((v,p)=>v+p[0],0)/enemy.length:540;
   const ty=enemy.length?enemy.reduce((v,p)=>v+p[1],0)/enemy.length:850;
   active.push({kind:s.kind,duration:s.duration,elapsed:0,x,y,tx,ty,targets:enemy});
   if(active.length>5)active.shift();
   start();
   return s;
  }
  function guard(){
   for(const pos of sonia)fire('guard',pos,[]);
  }
  function destroy(){alive=false;if(raf)cancelAnimationFrame(raf);raf=0;active=[];canvas.remove();}
  return {timing:(id,pos)=>sonia.has(Number(pos))?SKILLS[Number(id)]||null:null,
    play:(id,pos,targets)=>fire(Number(id),Number(pos),targets),
    guard,speed:v=>{rate=Math.min(4,Math.max(.5,Number(v)||1));},destroy,
    skillCount:sonia.size};
 }
 return Object.freeze({mount,SKILLS});
})();
