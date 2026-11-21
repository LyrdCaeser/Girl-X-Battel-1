/* Lyr Sonia 10★ skill + original FX: isolated visual QA only.
 * Requires the exact asset bundles on GXB 3's same-origin static server.
 * No hero registration, no combat / DB calls, no production write operations.
 */
(function(global){
'use strict';
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
function schedule(manifest,profile){
 const cfg=manifest.quality_profiles[profile];
 if(!cfg)throw Error('Unknown render profile: '+profile);
 const steps=cfg.steps.map(index=>{
  const s={...manifest.sequence[index]};
  if(cfg.step_timings_ms?.[index]) [s.t,s.duration]=cfg.step_timings_ms[index];
  return {...s,index};
 });
 return steps;
}
function validate(manifest,profile){
 const steps=schedule(manifest,profile);
 const cfg=manifest.quality_profiles[profile],total=manifest.timing_ms;
 for(const s of steps){
  if(!cfg.atlas_resources.includes(s.res))throw Error('Unregistered FX '+s.res);
  if(!['caster_ground','staff_tip','target','target_ground'].includes(s.at))throw Error('Unsafe anchor');
  if(!['behind','front','caster'].includes(s.layer))throw Error('Unsafe layer');
  if(!(s.t>=0&&s.duration>0&&s.t+s.duration<=total))throw Error('Outside Skill length');
  if(!(s.alpha>0&&s.alpha<=1.0))throw Error('FX opacity outside approved QA range');
 }
 let peak=0;
 for(let t=0;t<=total;t+=5)peak=Math.max(peak,steps.filter(s=>t>=s.t&&t<s.t+s.duration).length);
 if(peak>cfg.max_instances)throw Error('Too many concurrent FX '+peak);
 return {peak,steps,resources:cfg.atlas_resources};
}
function alphaAt(s,ms){const dt=ms-s.t;return dt<0||dt>=s.duration?0:s.alpha*clamp(Math.min(dt/95,(s.duration-dt)/110),0,1);}
function anchors(mirror=false){return mirror?
 {caster:{x:500,y:665},target:{x:250,y:515},targetGround:{x:250,y:655}}:
 {caster:{x:220,y:665},target:{x:470,y:515},targetGround:{x:470,y:655}};}
function fxAnchor(s,mirrored,actor){
 const p=anchors(mirrored);
 if(s.at==='staff_tip'&&actor){
   const b=actor.skeleton.findBone('staff_tip');
   if(!b)throw Error('Lyr Sonia missing staff_tip anchor');
   return {x:actor.x+b.worldX*actor.scale.x,y:actor.y+b.worldY*Math.abs(actor.scale.y)};
 }
 // The fallback when no rendered actor is supplied is exclusively for geometry unit tests.
 return (s.at==='caster_ground'||s.at==='staff_tip')?
   {x:p.caster.x+15*(mirrored?-1:1),y:p.caster.y+42}:
   s.at==='target_ground'?p.targetGround:{x:p.target.x,y:p.target.y-40};
}
function getHeader(){return 'Lyr Sonia · Tinh Liên Hỏa Ấn · Motion + Lotus v2.0 (QA)';}
function maskBounds(mirrored,cut=357){return mirrored?{x:0,width:cut}:{x:cut,width:720-cut};}
async function createQA({PIXI,manifest,mount,status}){
 if(!PIXI?.spine?.Spine)throw Error('Pixi-Spine not loaded');
 const app=new PIXI.Application({width:720,height:960,resolution:1,antialias:false,autoDensity:false,autoStart:false,preserveDrawingBuffer:true,backgroundColor:0x17152c});
 mount.appendChild(app.view);
 const stage=app.stage;
 const rear=new PIXI.Container(),actorLayer=new PIXI.Container(),casterGlow=new PIXI.Container(),targetOverlay=new PIXI.Container(),front=new PIXI.Container();
 stage.addChild(rear,actorLayer,casterGlow,targetOverlay,front);
 const impactRing=new PIXI.Graphics();targetOverlay.addChild(impactRing);
 let opponent=null,opponentData=null,opponentMs=-1;
 const monsterGroup=new PIXI.Container();targetOverlay.addChild(monsterGroup);
 const staffSpark=new PIXI.Graphics();
 staffSpark.lineStyle(2,0xf8e2a4,.8).moveTo(-11,0).lineTo(11,0).moveTo(0,-11).lineTo(0,11);
 staffSpark.lineStyle(1.5,0xd3b5fa,.7).moveTo(-7,-7).lineTo(7,7).moveTo(-7,7).lineTo(7,-7);
 staffSpark.beginFill(0xf7e9cb,.9).drawCircle(0,0,3).endFill();
 casterGlow.addChild(staffSpark);
 // Feathered mask on foreground spell fragments prevents a hard vertical border
 // through the arena. Same mask on PC and Mobile; no VFX steps are removed.
 function makeSoftMask(mirror){
  const c=document.createElement('canvas');c.width=720;c.height=960;
  const ctx=c.getContext('2d');const g=ctx.createLinearGradient(245,0,475,0);
  if(mirror){g.addColorStop(0,'rgba(255,255,255,1)');g.addColorStop(1,'rgba(255,255,255,0)');}
  else {g.addColorStop(0,'rgba(255,255,255,0)');g.addColorStop(1,'rgba(255,255,255,1)');}
  ctx.fillStyle=g;ctx.fillRect(0,0,720,960);
  return PIXI.Texture.from(c);
 }
 const softMasks=[makeSoftMask(false),makeSoftMask(true)];
 const frontMask=new PIXI.Sprite(softMasks[0]);stage.addChild(frontMask);front.mask=frontMask;
 function updateFrontMask(){frontMask.texture=softMasks[mirrored?1:0];}
 // The clip is not allowed to overlap the character's face, even if an FX's
 // native atlas has oversize wide sprites or particles.
 const ground=new PIXI.Graphics();ground.lineStyle(2,0xaa9bb3,.17);ground.drawEllipse(240,710,170,29);rear.addChild(ground);
 let activeProfile='desktop',mirrored=false,playing=false,frameMs=0,lastNow=0,frames=0,meanFrame=0,playToken=0,lastStatusMs=-Infinity;
 updateFrontMask();
 let actor=null,actorData=null,actorPrevMs=-1;
 const fxData=new Map(),tracks=new Map();
 const loaderPromises=new Map();
 const absoluteFX='/assets/battle-fx/';
 function load(name,dir,key){
  if(loaderPromises.has(key))return loaderPromises.get(key);
  const p=new Promise((resolve,reject)=>{
   const loader=new PIXI.Loader();let failed=false;
   loader.onError.add(err=>{failed=true;reject(new Error('Spine '+key+': '+(err?.message||err)))});
   loader.add('skin',dir+'model.json',{metadata:{spineAtlasFile:dir+'model.atlas'}});
   loader.load((_,resources)=>{
    if(failed)return;
    const data=resources?.skin?.spineData;
    if(data)resolve(data);else reject(new Error('Missing Spine JSON/atlas: '+key));
   });
  });
  loaderPromises.set(key,p);p.catch(()=>loaderPromises.delete(key));
  return p;
 }
 function actorPose(ms){
  if(actorPrevMs<0||ms<actorPrevMs){
   actor.state.setAnimation(0,'skill',false);
   actor.update(ms/1000);
  }else if(ms>actorPrevMs){actor.update((ms-actorPrevMs)/1000);}
  actorPrevMs=ms;
 }
 function clearEffects(){
  for(const t of tracks.values()){try{t.parent.removeChild(t.fig);t.fig.destroy({children:true});}catch{}}
  tracks.clear();
 }
 function makeTrack(s){
  const dat=fxData.get(activeProfile+':'+s.res);if(!dat)throw Error('Missing '+s.res);
  const fig=new PIXI.spine.Spine(dat);fig.autoUpdate=false;
  if(s.res==='lianhua_hurt02'&&PIXI.filters?.ColorMatrixFilter){
    const f=new PIXI.filters.ColorMatrixFilter();
    f.saturate(1.05,false);f.contrast(1.06,true);
    fig.filters=[f];
  }

  const parent=s.layer==='front'?front:s.layer==='caster'?casterGlow:rear;parent.addChild(fig);
  const o={fig,parent,s,previousDt:-1};tracks.set(s.index,o);
  return o;
 }
 function instantiateProfile(){
  clearEffects();actorPrevMs=-1;
  for(const s of schedule(manifest,activeProfile))makeTrack(s);
 }
 const targetMarker=new PIXI.Graphics();targetOverlay.addChild(targetMarker);
 function targetSilhouette(ms){
  const p=anchors(mirrored),impact=Math.max(0,1-Math.abs(ms-1120)/195),recoil=impact*(mirrored?-11:11);
  targetMarker.clear();
  if(!opponent){
    targetMarker.lineStyle(2,impact>.01?0xf9e2ff:0x9dcddd,.30+impact*.5);
    targetMarker.drawEllipse(p.target.x+recoil,p.target.y,46+impact*6,106-impact*5);
  }
  targetMarker.lineStyle(2,0xc6a9f0,.14+impact*.24);
  targetMarker.drawEllipse(p.target.x,p.targetGround.y,64+impact*14,20);
 }
 function renderAt(ms){
  frameMs=clamp(ms,0,manifest.timing_ms);
  if(!actor)throw Error('Actor not initialized');
  actor.position.set(mirrored?500:220,670);
  actor.scale.set((mirrored?-1:1)*1.07,1.07);
  actorPose(frameMs);
  // Native Spine 3.6 joint telemetry, for QA assertion (not user-facing combat UI).
  const boneAngles=Object.fromEntries(['torso','right_arm','staff','hair_back','skirt_left'].map(name=>{
    const b=actor.skeleton.findBone(name);return [name,b?Number(b.rotation.toFixed(2)):null];
  }));
  mount.dataset.qaBones=JSON.stringify(boneAngles);

  if(opponent){
    const phase=frameMs>=1050?'hurt':'idle',elapsed=phase==='hurt'?Math.max(0,frameMs-1050):frameMs;
    opponent.position.set(anchors(mirrored).target.x,anchors(mirrored).targetGround.y);
    opponent.scale.set((mirrored?1:-1)*.40,.40);
    opponent.alpha=1;
    opponent.state.setAnimation(0,phase,false);
    opponent.update(elapsed/1000);
  }
  const glow=Math.max(0,Math.min(1,(frameMs-110)/175,(1150-frameMs)/180));
  if(glow>0){
   const tip=fxAnchor({at:'staff_tip'},mirrored,actor);
   staffSpark.position.set(tip.x,tip.y);
   staffSpark.scale.set((.7+glow*.45)*(1+.14*Math.sin(frameMs/85)));
  }
  staffSpark.alpha=glow*.92;
  staffSpark.visible=glow>0;
  // Impact only at target: fade and scale, caster remains unobscured.
  const impact=Math.max(0,1-Math.abs(frameMs-1120)/180);
  impactRing.clear();
  if(impact>.01){
    const t=anchors(mirrored).target;
    impactRing.lineStyle(4+impact*2,0xefb4ff,impact*.58)
     .drawEllipse(t.x,t.y-42,40+impact*52,45+impact*63);
    impactRing.lineStyle(1.5,0xffe2a9,impact*.75)
     .drawEllipse(t.x,t.y-42,35+impact*43,38+impact*45);
  }
  targetSilhouette(frameMs);
  for(const o of tracks.values()){
   const {fig,s}=o,dt=frameMs-s.t;
   const a=alphaAt(s,frameMs);
   fig.visible=a>0.001;
   if(!fig.visible){o.previousDt=-1;continue;}
   const q=fxAnchor(s,mirrored,actor);
   fig.position.set(q.x,q.y);
   fig.scale.set((mirrored?-1:1)*s.scale*1.5,s.scale*1.5);
   fig.alpha=a;
   if(o.previousDt<0||dt<o.previousDt){
    fig.state.setAnimation(0,s.clip,false);
    fig.update(dt*s.speed/1000);
   }else if(dt>o.previousDt){fig.update((dt-o.previousDt)*s.speed/1000);}
   o.previousDt=dt;
  }
  app.renderer.render(stage);
  // Avoid DOM mutation every frame while playing, but preserve each explicit seek.
  if(status&&(!playing||frameMs-lastStatusMs>=120||frameMs>=manifest.timing_ms)){
   lastStatusMs=frameMs;
   status({frame:Math.round(frameMs),live:[...tracks.values()].filter(t=>t.fig.visible).map(t=>t.s.res),profile:activeProfile,renderer:app.renderer.type===PIXI.RENDERER_TYPE.WEBGL?'WEBGL':'CANVAS',fps:meanFrame?Math.round(1000/meanFrame):null,actor:true});
  }
 }
 async function prepare(profile){
  const {resources}=validate(manifest,profile);
  const root=profile==='mobile'?'/mobile-battle-fx/':absoluteFX;
  await Promise.all([load('sonia','assets/sonia/','sonia'),...resources.map(n=>load(n,root+n+'/','fx-'+profile+'-'+n))]);
  if(!actorData)actorData=await load('sonia','assets/sonia/','sonia');
  try{opponentData=await load('opponent','/assets/chibis/monika_10/','native-target-monika10')}catch(e){console.warn('Native opponent not available',e)}
  for(const n of resources){const key=profile+':'+n;if(!fxData.has(key))fxData.set(key,await load(n,root+n+'/','fx-'+profile+'-'+n));}
  playing=false;playToken++;lastNow=0;meanFrame=0;activeProfile=profile;
  app.renderer.resolution=1;
  app.renderer.resize(720,960);
  if(!actor){actor=new PIXI.spine.Spine(actorData);actor.autoUpdate=false;actorLayer.addChild(actor);}
  if(opponent){monsterGroup.removeChild(opponent);opponent.destroy({children:true});opponent=null;}
  if(opponentData){
    opponent=new PIXI.spine.Spine(opponentData);opponent.autoUpdate=false;monsterGroup.addChild(opponent);
  }
  instantiateProfile();lastStatusMs=-Infinity;renderAt(manifest.skill_hit_event_ms);
  return {loaded:resources.length+1,profile};
 }
 function tick(now,token){
  if(!playing||token!==playToken)return;
  if(lastNow){const dt=now-lastNow;meanFrame=meanFrame?meanFrame*.85+dt*.15:dt;frameMs+=dt;frames++}
  lastNow=now;
  renderAt(frameMs);
  if(frameMs>=manifest.timing_ms){playing=false;lastNow=0;renderAt(manifest.skill_hit_event_ms);return;}
  requestAnimationFrame(t=>tick(t,token));
 }
 function play(){playToken++;playing=true;lastNow=0;meanFrame=0;frameMs=0;actorPrevMs=-1;for(const o of tracks.values())o.previousDt=-1;const token=playToken;requestAnimationFrame(t=>tick(t,token))}
 function stop(){playToken++;playing=false;lastNow=0;renderAt(manifest.skill_hit_event_ms)}
 function seek(v){playToken++;playing=false;lastNow=0;renderAt(v)}
 function flip(){mirrored=!mirrored;updateFrontMask();renderAt(frameMs)}
 function close(){playToken++;playing=false;clearEffects();monsterGroup.removeChildren();actorLayer.removeChildren();app.destroy(true,{children:true,texture:false,baseTexture:false})}
 return {prepare,play,stop,seek,flip,close,get profile(){return activeProfile},get frame(){return frameMs},get measuredFps(){return meanFrame?1000/meanFrame:null},get renderer(){return app.renderer.type}};
}
const api={schedule,validate,alphaAt,anchors,fxAnchor,maskBounds,getHeader,createQA};
global.LyrSoniaQA=api;
if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
