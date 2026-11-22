/* Archived Spine 3.6 skeletons decoded without changing their animations. */
const ChibiBattle=(()=>{
 let cataloguePromise;const dataCache=new Map();
 async function catalogue(){return cataloguePromise||(cataloguePromise=fetch('/assets/chibis/catalog.json?v=20261014-nephilim3').then(r=>{if(!r.ok)throw Error("Chibi catalog unavailable");return r.json();}));}
 async function load(name){if(dataCache.has(name))return dataCache.get(name);const promise=new Promise((resolve,reject)=>{const loader=new PIXI.Loader();loader.add(name,`/assets/chibis/${name}/model.json${name==='lyr_sonia'?'?v=20261122-motion-r1':''}`,{metadata:{spineAtlasFile:`/assets/chibis/${name}/model.atlas`}});loader.onError.add(e=>reject(e));loader.load((_,resources)=>{const data=resources[name]?.spineData;if(data)resolve(data);else reject(Error("Could not read "+name));});});dataCache.set(name,promise);try{return await promise;}catch(e){dataCache.delete(name);throw e;}}
 // The archived Spine models use different native bone/attachment dimensions.
 // Fit BOTH axes into one 1080 x 1920 battle footprint, instead of sizing by
 // height alone (which made wide/tall skins enormous on portrait phones).
 function fitScaleForBounds(bounds,{boss=false,bossScene=false,bossScale=1}={}){
  // The archived skeleton's exported width/height describe the intended actor
  // footprint.  Animated attachment bounds may contain invisible/off-screen FX;
  // using them to normalize a skin makes that specific actor look miniature.
  const width=Math.max(1,Number(bounds?.width)||1),height=Math.max(1,Number(bounds?.height)||1);
  if(bossScene){
   const requested=Number(bossScale);
   return Math.min(Number.isFinite(requested)&&requested>0?requested*1.5:1.5,760/width,850/height);
  }
  if(boss)return Math.min(2.25,310/width,365/height);
  // Preserve actors that were already a readable size.  Only wide or unusually
  // narrow rigs that collapsed under the 250 x 285 footprint get restored.
  const original=Math.min(2.6,250/width,285/height);
  if(width*original>=150&&height*original>=260)return original;
  return Math.min(2.6,320/width,330/height);
 }
 // Only characters with verified model metadata override the automatic
 // dual-axis fit. Broad wing/FX bounds otherwise make their bodies tiny.
 function fitScaleForModel(bounds,meta={},opts={}){
  const standard=fitScaleForBounds(bounds,opts);
  const height=Number(meta.battleHeight);
  if(opts.boss||opts.bossScene||!Number.isFinite(height)||height<120||height>330)return standard;
  return Math.min(2.6,height/Math.max(1,Number(bounds?.height)||1));
 }
 function modelFacing(spineData,visualBounds,meta={}){
  // Optional asset-specific orientation overrides, never inferred from team.
  if(meta.facing==='left'||meta.facing===-1)return -1;
  if(meta.facing==='right'||meta.facing===1)return 1;
  const bones=(spineData?.bones||[]).filter(b=>/^Pattack\d*$/i.test(b.name)&&Number.isFinite(b.x));
  // Most archived models face right. Flip a native left-facing model only when
  // at least two independently exported projectile origins are far to the
  // LEFT of its idle silhouette, avoiding false positives on melee fighters.
  if(bones.length<2)return 1;
  const center=(Number(visualBounds?.x)||0)+(Number(visualBounds?.width)||0)/2;
  const width=Math.max(1,Number(spineData?.width)||Number(visualBounds?.width)||1);
  const margin=Math.max(40,width*.2);
  const left=bones.filter(b=>b.x<center-margin).length;
  const right=bones.filter(b=>b.x>center+margin).length;
  return left>=2&&left>=right*2?-1:1;
 }
 // HP/status HUD belongs to the actual animated figure, not to the invisible
 // formation slot. Exported/animated PIXI getBounds() may include huge hidden
 // attack VFX (and may change with animation), so it is not a valid head anchor.
 function headAnchorForFigure(figure, rigHeight, scale, boss=false){
  const maxHeight=boss?850:370;
  const h=Math.max(95,Math.min(maxHeight,(Number(rigHeight)||200)*Math.abs(Number(scale)||1)));
  return [Math.max(0,Math.min(1080,Number(figure.x)||0)),
          Math.max(0,Math.min(1920,(Number(figure.y)||0)-h-18))];
 }
 // Nephilim's base ultimate FX has a built-in negative-X parent bone
 // (bone19.scaleX=-1). The awakened/advanced FX are native positive-X.
 // Correct only that imported FX, not the entire fighter or hit effects.
 function effectFlipForSide(resource,enemySide){
  const nativeMirrored=resource==='spmijiale_hurt02_skill01';
  return Boolean(enemySide)!==nativeMirrored;
 }
 let fxTable=null;const fxCache=new Map();
 function fxSkills(){return fxTable||(fxTable=fetch('/assets/battle-fx/skills.json').then(r=>r.ok?r.json():{}).catch(()=>({})));}
 function fxLoad(res){if(fxCache.has(res))return fxCache.get(res);const p=new Promise((resolve,reject)=>{const loader=new PIXI.Loader();loader.add('fx_'+res,`/assets/battle-fx/${res}/model.json`,{metadata:{spineAtlasFile:`/assets/battle-fx/${res}/model.atlas`}});loader.onError.add(e=>reject(e));loader.load((_,r)=>{const d=r['fx_'+res]?.spineData;if(d)resolve(d);else reject(Error('fx '+res));});});fxCache.set(res,p);p.catch(()=>fxCache.delete(res));return p;}
 async function create(field,units,positions,{bossScene=false}={}){
  const catalogueData=await catalogue();let cancelled=false;
  const app=new PIXI.Application({width:1080,height:1920,transparent:true,antialias:true,resolution:1,autoDensity:false});
  app.view.className='chibi-canvas';app.view.dataset.models='0';app.view.setAttribute('aria-label',"Girls animated with the original skeletons");field.prepend(app.view);
  const figures=new Map(),missing=[],anchors=new Map(),headAnchors=new Map(),deadPositions=new Set(),deathTokens=new Map();
  const soniaBlinkTimers=new Set();
  function blinkSonia(figure,ms=3900){
   let timer=setTimeout(()=>{
    soniaBlinkTimers.delete(timer);
    if(cancelled)return;
    const current=figure.state.getCurrent(0)?.animation?.name;
    if(figure.visible&&(current==='idle'||current==='battle_idle')&&figure.state.hasAnimation('blink')){
      figure.state.setAnimation(1,'blink',false);
      let stop=setTimeout(()=>{soniaBlinkTimers.delete(stop);
        if(!cancelled)figure.state.clearTrack(1);
      },260);
      soniaBlinkTimers.add(stop);
    }
    blinkSonia(figure,4500);
   },ms);
   soniaBlinkTimers.add(timer);
  }
  await Promise.all(units.map(async u=>{const meta=(u.skin_id&&catalogueData[u.skin_id])||catalogueData[u.table_id];if(!meta){missing.push(u.table_id);return;}try{const data=await load(meta.model);if(cancelled)return;const figure=new PIXI.spine.Spine(data);
const idle=Number(u.table_id)===758001&&data.animations.some(a=>a.name==='battle_idle')
 ?'battle_idle':data.animations.some(a=>a.name==='idle')?'idle':data.animations[0]?.name;
if(idle)figure.state.setAnimation(0,idle,true);figure.stateData.defaultMix=.08;figure.update(0);const bounds=figure.getLocalBounds();const nativeBounds={width:data.width||bounds.width,height:data.height||bounds.height};
// Some exported skins contain attack VFX in their setup bounds. Do not let
// these invisible attachments shrink the entire character.
const cleanWidth=Number(data.width),cleanHeight=Number(data.height);
const rigBounds=(cleanWidth>0&&cleanHeight>0)?{width:cleanWidth,height:cleanHeight}:bounds;let scale=fitScaleForModel(rigBounds,meta,{boss:!!u.boss,bossScene:!!u.boss&&bossScene,bossScale:u.boss?.scale});const facing=modelFacing(data,bounds,meta);let xy=positions[u.pos];let dx=0,dy=0;if(u.boss){/* Boss footprint is bounded separately; is_boss stands between pos and pos+1. */if(u.boss.center){const o=positions[u.pos%6===0?u.pos-1:u.pos+1];if(o)xy=[(xy[0]+o[0])/2,(xy[1]+o[1])/2];}dx=(u.boss.offset?.[0]||0)*1.5*(u.pos>6?1:-1)*.35;dy=-(u.boss.offset?.[1]||0)*1.5;}figure.scale.set((u.pos>6?-1:1)*facing*scale,scale);figure.x=xy[0]+dx;figure.y=1920-xy[1]+110+dy;anchors.set(u.pos,xy);if(u.boss&&bossScene){/* Layout of the reference capture (Sanctuary boss): feet near 80 % of the height, centred in its half. */const sx=(u.pos>6?-1:1)*facing*scale;figure.y=1920*.8-(bounds.y+bounds.height)*scale;figure.x=(u.pos>6?1080*.72:1080*.28)-(bounds.x+bounds.width/2)*sx;}figure.zIndex=figure.y;app.stage.addChild(figure);
  // One deterministic head anchor per unique formation position. This stays
  // aligned with the model even for mirrored rigs / oversized skill attachments.
  headAnchors.set(u.pos,headAnchorForFigure(figure,cleanHeight>0?cleanHeight:bounds.height,
                                            scale,!!u.boss&&bossScene));
  figures.set(u.pos,{figure,idle,meta});app.view.dataset.models=String(figures.size);
  if(Number(u.table_id)===758001)blinkSonia(figure);}catch(e){missing.push(u.table_id);console.warn("Chibi not loaded",u.table_id,e.message);}}));
  app.stage.sortableChildren=true;app.stage.sortChildren();
  // Four Sonia skills now have dedicated Spine 3.6.37 visual copies: one
  // original skill each from Monica, Izanami, Nymphaea and Apollis. Only
  // these copies are recolored; source goddesses and combat math are unchanged.
  // No extra HTML/Canvas layers or composite effects on Mobile or PC.
  const soniaSlots=new Set(units.filter(u=>Number(u.table_id)===758001).map(u=>Number(u.pos)));
  const soniaNative={
    // Basic attack also needs its own cue. Live Lua battle frames frequently
    // use 75800100, not an awakening/passive skill ID.
    75800100:{impact:340,duration:850},
    75800101:{impact:910,duration:1590},
    75800102:{impact:450,duration:1180},
    75800103:{impact:350,duration:1150},
    75800104:{impact:390,duration:1050}
  };
  if(soniaSlots.size){
    // First hit and primary active skill are available before the first
    // damaging frame, with a bounded warm-up for slow Android networks.
    const preload=Promise.allSettled(
      ['lianhua_hurt01','sonia_chaos_orb','sonia_chaos_siphon',
       'sonia_chaos_guard','sonia_chaos_collapse'].map(name=>fxLoad(name)));
    await Promise.race([preload,new Promise(resolve=>setTimeout(resolve,2800))]);
  }
  function play(pos,kind){
   const unit=figures.get(pos);if(!unit||cancelled)return;
   const {figure,idle}=unit;
   if(kind==='revive'){
    const token=(deathTokens.get(pos)||0)+1;deathTokens.set(pos,token);
    deadPositions.delete(pos);figure.visible=true;
    if(idle&&figure.state.hasAnimation(idle))figure.state.setAnimation(0,idle,true);
    return;
   }
   if(deadPositions.has(pos))return; // cannot idle/attack/hurt after death unless revived
   if(kind==='dead'){
    deadPositions.add(pos);
    const token=(deathTokens.get(pos)||0)+1;deathTokens.set(pos,token);
    const death=['dead','die','death'].find(anim=>figure.state.hasAnimation(anim));
    if(!death){figure.visible=false;return;}
    figure.state.setAnimation(0,death,false);
    const finish={complete:entry=>{
      if(entry?.animation?.name!==death||deathTokens.get(pos)!==token)return;
      figure.visible=false;
      try{figure.state.removeListener(finish);}catch{}
    }};
    figure.state.addListener(finish);
    // Some archived death tracks never send completion; do not leave a corpse standing.
    setTimeout(()=>{if(!cancelled&&deathTokens.get(pos)===token)figure.visible=false;},2500/Math.max(.25,rate));
    return;
   }
   const name=kind==='skill'&&figure.state.hasAnimation('skill')?'skill':kind;
   if(!figure.state.hasAnimation(name))return;
   figure.state.setAnimation(0,name,false);
   if(idle)figure.state.addAnimation(0,idle,true,0);
  }
  // Skill effects (assets/battle-fx/skills.json, fx*.lua): "h" on every target (layer 1 = under the girl, position 1 = at her feet),
  // "c" at a point of the 720×1280 field (mirrored for the enemy side). One-shot Spine clips, removed when they end.
  let rate=1;const live=new Set(),fxConfigs=new WeakMap(),fxTimers=new Set();
  async function spawn(res,anim,scale,x,y,flip,z,options={}){try{
   const data=await fxLoad(res);if(cancelled)return;
   const f=new PIXI.spine.Spine(data);
   const name=data.animations.some(a=>a.name===anim)?anim:data.animations[0]?.name;
   if(!name)return;
   f.scale.set((flip?-1:1)*scale*1.5,scale*1.5);
   f.x=x;f.y=y;f.zIndex=z;f.alpha=options.alpha??1;
   const effectSpeed=Number(options.speed)||1;
   f.state.timeScale=rate*effectSpeed;
   f.state.setAnimation(0,name,false);
   fxConfigs.set(f,effectSpeed);
   const done=()=>{if(!live.has(f))return;live.delete(f);f.visible=false;
    requestAnimationFrame(()=>{try{if(!cancelled){app.stage.removeChild(f);f.destroy({children:true});}}catch{}});};
   f.state.addListener({complete:done});
   live.add(f);app.stage.addChild(f);
   setTimeout(done,(Number(options.maxMs)||4000)/Math.max(.25,rate));
  }catch(e){console.warn('Battle Spine FX unavailable',res,e?.message||e);}}
  // Sonia's four skill IDs use the original GXB3 PIXI/Spine stage and
  // timing. One recolored native Spine clip per skill on both Mobile and PC:
  // no stitched visual layers, and never any new HTML/Canvas renderer.
  function soniaNativeFx(skillId,caster,targets){
   if(!soniaSlots.has(Number(caster))||!soniaNative[Number(skillId)]||cancelled)return false;
   const source=figures.get(Number(caster))?.figure;
   if(!source)return true;
   let opponents=(targets||[]).filter(pos=>(Number(pos)>6)!==(Number(caster)>6))
     .map(pos=>figures.get(Number(pos))?.figure).filter(Boolean);
   if(!opponents.length){
     opponents=[...figures.entries()].filter(([pos])=>(pos>6)!==(caster>6))
       .map(([,value])=>value.figure).filter(Boolean);
   }
   const x=opponents.length?opponents.reduce((sum,f)=>sum+f.x,0)/opponents.length:540;
   const y=opponents.length?opponents.reduce((sum,f)=>sum+f.y,0)/opponents.length:890;
   const flip=(x<source.x);
   const at=(res,scale,place,speed,alpha,delay=0,clip='texiao01')=>{
    // Sonia's lotus guard is a front-facing shield around her torso, not a
    // ground decal hidden behind her legs at the sprite's foot anchor.
    const onCaster=place==='caster'||place==='caster-front';
    const figure=onCaster?source:null;
    const px=figure?figure.x:x;
    const py=figure?figure.y-(place==='caster-front'?100:0):y;
    const z=figure?(place==='caster-front'?figure.y+3:py-1):py+1;
    let timer=null;
    const fire=()=>{if(timer!==null)fxTimers.delete(timer);
      if(!cancelled)void spawn(res,clip,scale,px,py,flip,z,{speed,alpha,maxMs:2300});};
    if(delay>0){timer=setTimeout(fire,delay/Math.max(.25,rate));fxTimers.add(timer);}
    else fire();
   };
   switch(Number(skillId)){
    case 75800100: // Native light attack, preserved as a distinct fifth cue
     at('lianhua_hurt01',.72,'target',1.6,.96);
     break;
    case 75800101: // Monica's orb, shifted violet-pink
     at('sonia_chaos_orb',.56,'target',2.1,.96);
     break;
    case 75800102: // Izanami's siphon, shifted lavender
     at('sonia_chaos_siphon',.72,'target',1.3,.98);
     break;
    case 75800103: // Nymphaea's lotus, shifted mauve-violet
     at('sonia_chaos_guard',.72,'caster-front',1.35,1,0,'texiao02');
     break;
    case 75800104: // Apollis's radiance, shifted cosmic purple
     at('sonia_chaos_collapse',.76,'target',1.05,1);
     break;
   }
   return true;
  }
  async function fx(skillId,caster,targets){
   if(cancelled||deadPositions.has(caster))return;
   if(soniaNativeFx(skillId,caster,targets))return;
   const table=await fxSkills(),row=table[String(skillId)];if(!row||cancelled)return;
   // The native side transform faces the enemy. Derive the side from the
   // opposing, actual target figures rather than from an arbitrary animation list.
   const casterFigure=figures.get(caster)?.figure;
   const hostile=(targets||[]).filter(pos=>(Number(pos)>6)!==(Number(caster)>6))
     .map(pos=>figures.get(pos)?.figure).filter(Boolean);
   const targetX=hostile.length?hostile.reduce((sum,f)=>sum+f.x,0)/hostile.length:null;
   const fromRight=targetX!==null&&casterFigure?targetX<casterFigure.x:caster>6;
   for(const [res,anim,scale,layer,x,y]of row.c||[])
     spawn(res,anim,scale,fromRight?1080-x*1.5:x*1.5,1920-y*1.5,
           effectFlipForSide(res,fromRight),layer===1?-1:5000);
   if(live.size>40)return;
   for(const pos of targets){const u=figures.get(pos);if(!u||deadPositions.has(pos))continue;
    for(const [res,anim,scale,layer,position]of row.h||[])
      spawn(res,anim,scale,u.figure.x,u.figure.y-(position===1?0:90),pos>6,
            layer===1?u.figure.y-1:u.figure.y+1);
   }
  }
  function speed(value){rate=value;
   for(const {figure} of figures.values())figure.state.timeScale=value;
   for(const f of live)f.state.timeScale=value*(fxConfigs.get(f)||1);
  }
  function destroy(){cancelled=true;
   for(const timer of soniaBlinkTimers)clearTimeout(timer);soniaBlinkTimers.clear();
   for(const timer of fxTimers)clearTimeout(timer);fxTimers.clear();
   for(const f of live){try{app.stage.removeChild(f);f.destroy({children:true});}catch{}}
   live.clear();app.destroy(true,{children:true,texture:false,baseTexture:false});
  }
  return {play,speed,destroy,fx,
    timing:(id,pos)=>soniaSlots.has(Number(pos))?soniaNative[Number(id)]||null:null,
    anchors,headAnchors,has:pos=>figures.has(pos),missing};
 }
 return {create,catalogue,fitScaleForBounds,fitScaleForModel,modelFacing,effectFlipForSide,headAnchorForFigure};
})();

// BattleWindow + BaseFighter: 0/1 add, 2 work, 3/4 remove one matching name/sign.
const BattleStates=(()=>{
 let metadata;
 function change(active,buff){const mode=Number(buff.buffOn);if(mode===0||mode===1)active.push({...buff});
  else if(mode===3||mode===4){const i=active.findIndex(b=>b.name===buff.name&&Number(b.value||0)*Number(buff.value||0)>=0);if(i>=0)active.splice(i,1);}
 }
 async function create(units){metadata=metadata||fetch('/assets/spine/battle-status.json').then(r=>r.ok?r.json():{}).catch(()=>({}));const meta=await metadata,states=new Map();
  for(const [pos,u]of units){const row=document.createElement('div');row.className='unit-buffs';row.setAttribute('aria-label','Active status effects');u.element.append(row);states.set(pos,{active:[],row});}
  function draw(s){s.row.replaceChildren();const groups=new Map();for(const b of s.active){const m=meta[b.name];if(!m)continue;const icon=Number(b.value)<0?m.negative:m.positive;if(!icon)continue;
    const g=groups.get(icon)||{icon,label:m.label,count:0};g.count=b.name==='weak'?1:g.count+1;groups.set(icon,g);}
   const all=[...groups.values()];s.row.title=all.map(g=>g.label+(g.count>1?' ×'+g.count:'')).join(', ');
   for(const g of all.slice(-4)){const badge=document.createElement('span');badge.className='unit-buff';const label=g.label+(g.count>1?' ×'+g.count:'');badge.title=label;badge.setAttribute('aria-label',label);
    const icon=new Image();icon.src='/assets/spine/status-icons/'+g.icon+'.png';icon.alt=g.label;badge.append(icon);if(g.count>1){const n=document.createElement('b');n.textContent=g.count;badge.append(n);}s.row.append(badge);}
  }
  return {apply(buff){const s=states.get(buff.pos);if(!s)return;change(s.active,buff);draw(s);},clear(pos){const s=states.get(pos);if(s){s.active=[];draw(s);}}};
 }
 return {create,change};
})();
