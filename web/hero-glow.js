'use strict';
// HeroIcon.lua: hero_frame2 and shiziui_touxiang from 10★; Cosmos uses the tianyi variant.
// One shared renderer copies the original animation into visible icons, avoiding a WebGL context per card.
const HeroGlow=(()=>{
 const entries=new Set(),buckets=new Map();let renderer=null,last=0;
 const observer=new IntersectionObserver(rows=>{for(const r of rows){const e=r.target._heroGlow;if(e)e.visible=r.isIntersecting;}},{threshold:0});
 async function bucket(key){if(buckets.has(key))return buckets.get(key);const promise=(async()=>{
  const [group,rank]=key.split(':');const profile=group==='profile';const data=await GxbSpine.load('/assets/spine/'+(profile?rank:'shiziui_touxiang'+(group==='7'?'_tianyi':'')));
  const stage=new PIXI.Container();const figures=[];
  for(const anim of (profile?['texiao01']:['texiao03',rank==='10'?'texiao01':'texiao02'])){const f=new PIXI.spine.Spine(data);f.autoUpdate=false;f.scale.set(profile&&rank==='frame_qianhezi'?1.35:1.5);f.position.set(96,profile?96:96+(rank==='10'?3:-7));f.state.setAnimation(0,anim,true);f.update(0);stage.addChild(f);figures.push(f);}return {stage,figures};})();buckets.set(key,promise);return promise;}
 function frame(host,stars){for(const side of ['l','r']){const im=new Image();im.src='/assets/summon-result/'+(stars>=10?'hero_frame2':'hero_frame')+'.png';im.alt='';im.className='hg-frame '+side;host.append(im);}}
 function attach(host,stars,group,{frames=true}={}){if(frames)frame(host,stars);if(stars<10)return;
  const canvas=document.createElement('canvas');canvas.width=canvas.height=192;canvas.className='hg-glow';canvas.setAttribute('aria-hidden','true');host.append(canvas);
  const e={host,canvas,ctx:canvas.getContext('2d'),key:(Number(group)===7?'7':'0')+':'+(stars===10?'10':'11'),visible:false,model:null};host._heroGlow=e;entries.add(e);observer.observe(host);bucket(e.key).then(b=>e.model=b).catch(()=>{});
 }
 let frameEffects=null;const profileHosts=new WeakMap();
 async function profile(host,frame){if(!host)return;const id=String(frame||'frame_8007').replace('frame_','');const current=profileHosts.get(host);if(current?.id===id)return;if(current?.entry){observer.unobserve(host);entries.delete(current.entry);current.entry.canvas.remove();host.classList.remove('hg-profile-animated');delete host._heroGlow;}const record={id,entry:null};profileHosts.set(host,record);
  try{frameEffects=frameEffects||await api('/assets/spine/frame-effects.json');if(profileHosts.get(host)!==record)return;const name=frameEffects[id];if(!name)return;
   const model=await bucket('profile:'+name);if(profileHosts.get(host)!==record)return;const canvas=document.createElement('canvas');canvas.width=canvas.height=192;canvas.className='hg-glow hg-profile';canvas.setAttribute('aria-hidden','true');host.append(canvas);host.classList.add('hg-profile-animated');const e={host,canvas,ctx:canvas.getContext('2d'),key:'profile:'+name,visible:false,model};record.entry=e;host._heroGlow=e;entries.add(e);observer.observe(host);
  }catch{profileHosts.delete(host);}
 }
 function tick(time){requestAnimationFrame(tick);if(time-last<50)return;const dt=Math.min(.1,(time-last)/1000||.05);last=time;
  const active=new Map();for(const e of entries){if(!e.host.isConnected){observer.unobserve(e.host);entries.delete(e);delete e.host._heroGlow;continue;}if(e.visible&&e.model&&!document.hidden){if(!active.has(e.key))active.set(e.key,[]);active.get(e.key).push(e);}}
  if(!active.size)return;if(!renderer)renderer=PIXI.autoDetectRenderer({width:192,height:192,transparent:true,antialias:true,preserveDrawingBuffer:true,resolution:1});
  for(const list of active.values()){const b=list[0].model;for(const f of b.figures)f.update(dt);renderer.render(b.stage);for(const e of list){e.ctx.clearRect(0,0,192,192);e.ctx.drawImage(renderer.view,0,0);}}
 }
 requestAnimationFrame(tick);return {attach,profile};
})();

// WindowManager:initClick / playClickAction: buttons use texiao02, background texiao01.
(()=>{
 let figure,renderer,layer,frame=0,last=0,remaining=0;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const ready=GxbSpine.load('/assets/spine/fx_dianji').then(data=>{
  figure=new PIXI.spine.Spine(data);figure.autoUpdate=false;figure.position.set(160,160);
  renderer=PIXI.autoDetectRenderer({width:320,height:320,transparent:true,antialias:true,resolution:1});
  layer=document.createElement('div');layer.className='game-click-magic';layer.setAttribute('aria-hidden','true');
  layer.setAttribute('popover','manual');layer.append(renderer.view);document.body.append(layer);
 }).catch(error=>console.warn('Click effect unavailable',error.message));
 function hide(){if(layer?.matches(':popover-open'))layer.hidePopover();if(layer)layer.style.display='none';}
 function tick(time){frame=0;if(document.hidden){hide();return;}const dt=Math.min(.1,(time-last)/1000);last=time;remaining-=dt;
  figure.update(dt);renderer.render(figure);if(remaining>0)frame=requestAnimationFrame(tick);else hide();
 }
 document.addEventListener('click',event=>{
  if(event.button!==0||!figure)return;
  const target=event.target instanceof Element?event.target:null;
  // Ignore the browser margins surrounding the portrait game. Dialogs remain part of the game.
  if(!target?.closest('main,dialog,button'))return;
  const action=target.closest('button,a,input,select,textarea,[role="button"],[data-coming],[tabindex]');
  const anim=action?'texiao02':'texiao01';
  const bounds=document.querySelector('main')?.getBoundingClientRect();const scale=Math.min(2,Math.max(.5,(bounds?.width||720)/720));
  const rect=target.getBoundingClientRect();const x=event.detail===0?rect.x+rect.width/2:event.clientX;
  const y=event.detail===0?rect.y+rect.height/2:event.clientY;
  layer.style.cssText=`display:block;left:${x}px;top:${y}px;width:${320*scale}px;height:${320*scale}px;`;
  if(layer.matches(':popover-open'))layer.hidePopover();if(layer.showPopover)layer.showPopover();
  figure.state.clearTracks();figure.skeleton.setToSetupPose();const track=figure.state.setAnimation(0,anim,false);figure.update(0);
  remaining=reduced.matches ? .12 : track.animation.duration;renderer.render(figure);
  if(frame)cancelAnimationFrame(frame);last=performance.now();frame=requestAnimationFrame(tick);
 },true);
 document.addEventListener('visibilitychange',()=>{if(document.hidden){if(frame)cancelAnimationFrame(frame);frame=0;hide();}});
})();
