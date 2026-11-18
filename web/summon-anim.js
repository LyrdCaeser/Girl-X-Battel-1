'use strict';
// Capsule summon animation, as the client plays it:
// 1. SummonResWindow: summon_scene + Spine fx_ui_gacha_revision. The machine loops "<kind>04" until the player swipes
//    down, then plays <kind>01 (sound vd_egg), <kind>02 and <kind>03 (sound gacha_obtain). kind = putong (normal),
//    gaoji (senior) or friend (friendship) by summon id; other summons (shards…) skip the machine (isSimple).
// 2. SummonEffectResWindow + PartnerSummonEffect, one girl at a time:
//    ≥5★: fx_ui_gacha_revision "222" (sound vd_egg_5star), then fx_ui_newgirl_gaino texiao01 → loop texiao04
//         (ui_gain_hero_5star_bg, ui_gain_hero_5star) and wait for a tap.
//    <5★: fx_ui_newgirl_gainp texiao01 / texiao03 alternating right / left (ui_gain_hero_right / _left), no wait.
//    The girl's picture hangs from the "juese" slot; the star slots beyond her stars are hidden.
const SummonAnim=(()=>{
 const KIND={1:'putong',2:'putong',3:'putong',4:'gaoji',5:'gaoji',6:'gaoji',7:'gaoji',8:'gaoji',15:'friend',16:'friend',22:'gaoji',23:'gaoji',24:'gaoji',25:'gaoji',26:'gaoji',29:'gaoji'};
 // partnerAnimationName1/2 by star (5…11) in SummonEffectResWindow.lua.
 const ANIM1={5:'texiao01',6:'texiao02',7:'texiao07',8:'texiao08',9:'texiao09',10:'texiao03',11:'texiao10'};
 const ANIM2={5:'texiao04',6:'texiao05',7:'texiao11',8:'texiao12',9:'texiao13',10:'texiao06',11:'texiao14'};
 let pics=null,pictures=null,skipped=false,overlay=null,s4Sequence=false;
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const sfx=n=>{try{GxbAudio.sfx(n);}catch{}};
 const wait=ms=>new Promise(r=>setTimeout(r,ms));
 async function assets(){
  if(pics)return;
  // Picture metadata is optional for S4; a slow API must not block the Wish sequence.
  const request=Promise.all([
   api('/assets/pictures.json').catch(()=>[]),
   api('/assets/partner-pictures.json').catch(()=>({}))
  ]);
  const [q,p]=s4Sequence?await Promise.race([
   request,new Promise(resolve=>setTimeout(()=>resolve([[],{}]),4500))
  ]):await request;
  pics=new Set(q);pictures=p;
 }
 function run(fig,name,loop=false){
  return new Promise((resolve,reject)=>{
   if(skipped){resolve();return;}
   const anim=fig.spineData?.findAnimation(name);
   if(!anim){resolve();return;}
   let entry;
   try{entry=fig.state.setAnimation(0,name,loop);}catch(e){reject(e);return;}
   if(loop){resolve();return;}
   let done=false;
   const finish=()=>{
    if(done)return;
    done=true;
    clearTimeout(timer);clearInterval(skipPoll);
    if(entry)entry.listener=null;
    resolve();
   };
   // Original 25★ sequences last ~3.1s. A missing Spine complete event
   // or WebGL context pause must not hold a player's claimed mail hostage.
   const playback=s4Sequence?Math.max(1,Number(fig.state?.timeScale)||1):1;
   const duration=Math.max(700,Math.min(9000,
    (Number(anim.duration)||2)*1000/playback+(s4Sequence?900:1400)));
   const timer=setTimeout(finish,duration);
   const skipPoll=setInterval(()=>{if(skipped)finish();},80);
   entry.listener={complete:finish,end:finish,dispose:finish};
  });
 }
 async function layer(base,scale=1,oy=.5){
  const host=el('div','sa-layer');
  const current=overlay;
  current.querySelector('.sa-stage').append(host);
  const mounting=GxbSpine.mount(host,base,{
   width:720,height:1280,scale,origin:[.5,oy],
   className:'sa-canvas',resolution:s4Sequence?1:null,
   sequence:[['__none__',false]]
  });
  let timeoutId,expired=false;
  try{
   const h=await (s4Sequence?Promise.race([
    mounting,new Promise((_,reject)=>{timeoutId=setTimeout(()=>{
     expired=true;reject(Error('Quá thời gian tải hiệu ứng Wish S4'));
    },6500);})
   ]):mounting);
   if(expired||!current.isConnected||skipped){h.destroy();host.remove();throw Error('Đã bỏ qua hiệu ứng');}
   return {host,h,fig:h.figure,done(){h.destroy();host.remove();}};
  }catch(e){
   host.remove();
   if(expired)void mounting.then(h=>h.destroy(),()=>{});
   throw e;
  }finally{clearTimeout(timeoutId);}
 }
 function tapOrSkip(){
  return new Promise(res=>{
   const t=overlay.querySelector('.sa-touch');
   const hint=overlay.querySelector('.sa-hint');
   t.hidden=false;
   // With 24 S4 rewards, each manual-only tap was mistaken for a hang.
   // Normal capsule animation stays manual; exclusive S4 advances after 3s.
   if(s4Sequence&&hint){
    hint.textContent='Chạm để tiếp tục • Tự chuyển sau 3 giây';
    hint.hidden=false;
   }
   let done=false,timer=null,poll=null;
   const go=()=>{
    if(done)return;done=true;t.hidden=true;t.onclick=null;
    clearTimeout(timer);clearInterval(poll);
    if(hint){hint.hidden=true;hint.onclick=null;hint.textContent='Vuốt xuống để tiếp tục ▼';}
    res();
   };
   t.onclick=go;
   if(s4Sequence){hint.onclick=go;timer=setTimeout(go,3000);}
   poll=setInterval(()=>{if(skipped)go();},80);
  });
 }
 function swipe(){return new Promise(res=>{const t=overlay.querySelector('.sa-touch');const hint=overlay.querySelector('.sa-hint');t.hidden=false;hint.hidden=false;let y0=null;
  const end=()=>{t.hidden=true;hint.hidden=true;t.onpointerdown=t.onpointerup=t.onclick=null;clearInterval(k);res();};
  t.onpointerdown=e=>{y0=e.clientY;};t.onpointerup=e=>{const r=overlay.getBoundingClientRect();if(y0!=null&&(e.clientY-y0)>r.height*100/1280)end();y0=null;};
  t.onkeydown=null;hint.onclick=end;const k=setInterval(()=>{if(skipped)end();},100);});}
 // The girl's picture follows the "juese" slot (PartnerSummonEffect:replacePartner, partner_picture_xy / scale).
 async function attachGirl(fig,tableId){const i=fig.skeleton.findSlotIndex('juese');const box=fig.slotContainers?.[i];if(!box)return;
  const showId=hostChain(tableId).find(id=>pics.has(Number(id)));const full=showId!==undefined;const url=full?'/assets/pictures/'+showId+'.webp':girlIconSource(tableId);if(!url)return;
  const image=await new Promise(resolve=>{
   const im=new Image();let settled=false;
   const done=value=>{if(settled)return;settled=true;im.onload=null;im.onerror=null;clearTimeout(limit);clearInterval(skipPoll);resolve(value);};
   const limit=setTimeout(()=>done(null),s4Sequence?3600:9000);
   const skipPoll=setInterval(()=>{if(skipped)done(null);},80);
   im.onload=()=>done(im);im.onerror=()=>done(null);im.src=url;
  });
  if(!image||skipped)return;
  const p=full?(pictures?.[String(showId)]||{}):{};const sp=new PIXI.Sprite(PIXI.Texture.from(image));if(s4Sequence)sp.__s4WishTexture=sp.texture;sp.anchor.set(.5);const scale=full?(p.summon_static_scale||1):280/Math.max(image.naturalWidth,image.naturalHeight);sp.scale.set(scale,-scale);sp.position.set(p.xy?.[0]||0,150-(p.xy?.[1]||0));box.addChild(sp);
 }

 // PartnerSummonEffect:initEffect hides zhiye/cv/name (placeholder text art) and updateStar the "Nxing" slots above the
 // girl's stars; an empty texture keeps them hidden whatever the animation keys.
 // Match PartnerSummonEffect: overlay the girl's name and star icons on
 // the ORIGINAL animated name/star bones, not in an unrelated bottom label.
 // The native 'name' attachment is the white nameplate and must NOT be hidden.
 function revealStarsOneByOne(icons){
  // The old sprite placement sat BELOW the CV. The native star track is
  // above the name plaque (1xing y=154 vs name y=83 in original Spine).
  // Animate each original star from left to right without relying on a
  // hidden attachment animation to keep it visible.
  icons.forEach((icon,i)=>{
   const sx=icon.scale.x, sy=icon.scale.y;
   icon.alpha=0;icon.visible=false;
   const stagger=setTimeout(()=>{
    if(icon.destroyed)return;
    icon.visible=true;
    const start=performance.now();
    const animate=(now)=>{
     if(icon.destroyed)return;
     const t=Math.min(1,(now-start)/260);
     const ease=1-Math.pow(1-t,3);
     icon.alpha=ease;
     const factor=.45+.55*ease+(.12*Math.sin(t*Math.PI));
     icon.scale.set(sx*factor,sy*factor);
     if(t<1)requestAnimationFrame(animate);
     else icon.scale.set(sx,sy);
    };
    requestAnimationFrame(animate);
   },1000+i*180);
  });
 }
 function nativeNameStars(fig,p,star){
  // A 1xing/3xing slot can be disabled by its current Spine animation;
  // attach ALL real labels to the permanently visible native 'name' slot.
  const index=fig.skeleton.findSlotIndex('name');
  const bar=index>=0?fig.slotContainers?.[index]:null;
  if(!bar)return false;
  // Original tcc_3 embeds Chinese sample text into the white plaque.
  // Cover only this sample text (not the frame), keeping the animated plaque.
  const plaque=new PIXI.Graphics();
  plaque.beginFill(0xfafcff,.98).drawRoundedRect(-94,-26,188,52,6).endFill();
  bar.addChild(plaque);
  const label=new PIXI.Text(String(p.name||''),{
   fontFamily:'Arial, sans-serif',fontSize:26,fontWeight:'bold',
   fill:0x34486b,align:'center'
  });
  label.anchor.set(.5);
  label.scale.y=-1;
  if(label.width>164)label.scale.x=164/label.width;
  bar.addChild(label);
  const starIcons=[];
  const normal=star<=5;
  if(normal){
   const count=Math.max(1,Math.min(5,star));
   const space=count===5?35:count===4?39:40;
   for(let i=0;i<count;i++){
    const x=(i-(count-1)/2)*space;
    const icon=PIXI.Sprite.from('/assets/girl-ui/partner_star_yellow.png');
    icon.anchor.set(.5);icon.position.set(x,78);icon.scale.set(1.12,-1.12);
    bar.addChild(icon);starIcons.push(icon);
   }
  }else if(star<10){
   const count=Math.min(5,star-5);
   for(let i=0;i<count;i++){
    const x=(i-(count-1)/2)*37;
    const icon=PIXI.Sprite.from('/assets/girl-ui/partner_star_red.png');
    icon.anchor.set(.5);icon.position.set(x,78);icon.scale.set(1.12,-1.12);
    bar.addChild(icon);starIcons.push(icon);
   }
  }else{
   const wing=PIXI.Sprite.from('/assets/girl-ui/potentiality_nametag_star'+(star>=15?'_max':'')+'.png');
   wing.anchor.set(.5);wing.position.set(0,78);wing.scale.set(.6,-.6);
   bar.addChild(wing);starIcons.push(wing);
   const num=new PIXI.Text(String(star),{fontFamily:'Arial, sans-serif',
      fontSize:22,fontWeight:'bold',fill:0xffffff,stroke:0x71383b,strokeThickness:3});
   num.anchor.set(.5);num.position.set(0,78);num.scale.y=-1;bar.addChild(num);
   num.alpha=0;
   setTimeout(()=>{if(!num.destroyed)num.alpha=1;},1250);
  }
  revealStarsOneByOne(starIcons);
  // Hide only the baked default star textures. Custom original star icons
  // above remain visible because they live under the stable name slot.
  for(const n of ['1xing','2xing','3xing','3xing2','3xing3','3xing4','4xing','5xing',
                  'xing6','xing7','xing8','xing9','xing10','xing11','xing12','xing13','xing14']){
   if(fig.skeleton.findSlotIndex(n)>=0)try{
    fig.hackTextureBySlotName(n,PIXI.Texture.EMPTY,{width:1,height:1});
   }catch{}
  }
  return true;
 }
 function caption(p,star,insideNative){
  const c=overlay.querySelector('.sa-caption');
  c.replaceChildren(el('b','',p.name||''));
  c.hidden=insideNative;
  const voice=overlay.querySelector('.sa-voice');
  if(voice){
    voice.hidden=typeof Dates==='undefined';
    voice.onclick=()=>{if(typeof Dates!=='undefined')void Dates.playGirlVoice(p.table_id);};
  }
  if(typeof Dates!=='undefined')void Dates.playGirlVoice(p.table_id);
  return ()=>{c.hidden=true;if(voice)voice.hidden=true;};
 }
 async function reveal(p,i,summon){const star=Number(p.star)||5;
  if(star>=5){
   if(summon){
    const m=await layer('/assets/spine/fx_ui_gacha_revision',1.2,.66);
    try{sfx('vd_egg_5star');await run(m.fig,'222');}finally{m.done();}
    if(skipped)return;
   }
   const e=await layer('/assets/spine/fx_ui_newgirl_gaino');
   let uncap=()=>{};
   try{
    await attachGirl(e.fig,p.table_id);
    if(skipped)return;
    const placed=nativeNameStars(e.fig,p,star);uncap=caption(p,star,placed);
    sfx('ui_gain_hero_5star_bg');setTimeout(()=>{if(!skipped&&overlay)sfx('ui_gain_hero_5star');},1000);
    const s=Math.min(star,11);await run(e.fig,ANIM1[s]||'texiao01');
    if(!skipped){run(e.fig,ANIM2[s]||'texiao04',true);await wait(900);if(!skipped)await tapOrSkip();}
   }finally{uncap();e.done();}
  }else{
   const e=await layer('/assets/spine/fx_ui_newgirl_gainp');let uncap=()=>{};
   try{
    await attachGirl(e.fig,p.table_id);
    if(skipped)return;
    const placed=nativeNameStars(e.fig,p,star);uncap=caption(p,star,placed);
    const left=summon&&i%2===1;sfx(left?'ui_gain_hero_left':'ui_gain_hero_right');
    await run(e.fig,left?'texiao03':'texiao01');
    if(!skipped)await wait(900);
   }finally{uncap();e.done();}
  }
 }
 // S4 native Wish: present EVERY original goddess and skin with the
 // original Spine fx_ui_gacha_revision + fx_ui_newgirl_gaino animations.
 // One canvas is reused per reward type. Never replace Wish with a 12-card grid.
 function s4Slot(fig,name){
  const id=fig.skeleton.findSlotIndex(name);
  return id<0?null:fig.slotContainers?.[id]||null;
 }
 function s4SlotChildren(fig){
  const result=[];
  for(const name of ['juese','name']){
   const slot=s4Slot(fig,name);
   if(slot)result.push({slot,original:new Set(slot.children)});
  }
  return result;
 }
 function s4CleanupArt(slots){
  for(const {slot,original} of slots){
   for(const child of [...slot.children]){
    if(original.has(child))continue;
    try{
     // Destroy only TEMPORARY WebGL textures created from this Wish image.
     // Original game star/skeleton shared sprites must retain their textures.
     const transient=child.__s4WishTexture||null;
     const ownText=typeof PIXI.Text==='function'&&child instanceof PIXI.Text;
     slot.removeChild(child);
     child.destroy({children:true,texture:ownText,baseTexture:ownText});
     if(transient)transient.destroy(true);
    }catch(e){console.warn('Wish cleanup:',e);}
   }
  }
 }
 // Use actual original Gacha effects but NEVER overlay a skin on the
 // Goddess-only 'fx_ui_newgirl_gaino' skeleton: it bakes in GIRLS, CV,
 // name plaques and star artwork (the exact screenshot regression).
 async function s4RevealSkinCinema(items,progress){
  if(!items?.length||skipped)return;
  let effect=null;
  try{
   effect=await layer('/assets/spine/fx_ui_gacha_revision',1.05,.58);
   effect.host.classList.add('sa-s4-gacha-aura');
  }catch(error){console.warn('Gacha VFX chưa tải được',error);}
  const stage=overlay.querySelector('.sa-stage');
  const scene=el('div','sa-s4-skin-scene');
  scene.setAttribute('aria-label','Trang phục Wish độc quyền S4');
  scene.append(el('div','sa-s4-skin-radiance'));
  const poster=el('img','sa-s4-skin-portrait');
  poster.alt='';poster.draggable=false;
  const title=el('div','sa-s4-skin-title');
  title.setAttribute('aria-live','off');
  scene.append(poster,title);
  stage.append(scene);
  try{
   for(let i=0;i<items.length&&!skipped;i++){
    const skin=items[i];
    const sid=Number(skin.id);
    progress.textContent='Trang phục '+(i+1)+' / '+items.length;
    // 53 skin artworks have original full-size picture resources;
    // the other verified originals retain their portrait crop.
    const model=String(skin.picture_model||'');
    const full=/^[0-9]{1,12}$/.test(model)?
      '/assets/pictures/'+model+'.webp':'';
    const card='/assets/skins/cards/'+sid+'.webp';
    const family=(skin.partners||[]).map(Number).reverse()
      .find(Number.isSafeInteger);
    const fallback=family?'/assets/cards/partner_card_'+family+'.png':'';
    let img=null;
    for(const url of [full,card,fallback].filter(Boolean)){
     img=await s4LoadImage(url);
     if(img||skipped)break;
    }
    if(skipped)break;
    scene.classList.remove('sa-s4-skin-visible');
    poster.removeAttribute('src');
    title.textContent=String(skin.name||'Trang phục Nữ Thần');
    if(img){
     // Decode/copy a loaded native image rather than a thumbnail CSS background.
     poster.src=img.src;
     poster.alt=String(skin.name||'Trang phục Nữ Thần');
     poster.hidden=false;
    }else{
     poster.hidden=true;
    }
    // The recovered publisher gacha/burst Spine, plus the original art
    // entering the central reveal stage, replaces all fake 12-card grids.
    try{
     if(effect){
      effect.fig.state.timeScale=1.8;
      await run(effect.fig,'222');
     }
    }catch(error){console.warn('Wish skin: lỗi một hiệu ứng',sid,error);}
    if(skipped)break;
    void scene.offsetWidth; // Restart entrance animation for each reward.
    scene.classList.add('sa-s4-skin-visible');
    sfx('ui_gain_hero_5star');
    await s4Pause(1800);
   }
  }finally{
   scene.remove();
   effect?.done();
  }
 }
 function s4SuppressBakedGirlHeading(fig){
  // Original visual art remains; only the baked English GIRLS heading and
  // CV placeholder are hidden in S4 cinematic, never in regular summons.
  for(const name of ['girls','cv']){
   if(fig.skeleton.findSlotIndex(name)>=0)
    try{fig.hackTextureBySlotName(name,PIXI.Texture.EMPTY,{width:1,height:1});}
    catch{}
  }
 }
 function s4Pause(ms){
  return new Promise(resolve=>{
   if(skipped){resolve();return;}
   const touch=overlay?.querySelector('.sa-touch');
   if(touch)touch.hidden=false;
   let done=false,poll=null,timer=null;
   const finish=()=>{
    if(done)return;done=true;clearTimeout(timer);clearInterval(poll);
    if(touch){touch.hidden=true;touch.onclick=null;}
    resolve();
   };
   if(touch)touch.onclick=finish;
   timer=setTimeout(finish,ms);
   poll=setInterval(()=>{if(skipped)finish();},80);
  });
 }
 async function s4RevealSequence(items,type,progress){
  if(!items?.length||skipped)return;
  progress.textContent=type==='girls'?'NỮ THẦN • TRIỆU HỒI WISH':
                                      'TRANG PHỤC • TRIỆU HỒI WISH';
  // Original gacha egg burst at each new phase; no swipe deadlock.
  try{
   const machine=await layer('/assets/spine/fx_ui_gacha_revision',1.2,.66);
   try{sfx('vd_egg_5star');await run(machine.fig,'222');}
   finally{machine.done();}
  }catch(error){console.warn('S4 Wish: bỏ qua hiệu ứng trứng lỗi',error);}
  if(skipped)return;
  if(type==='skins'){
   await s4RevealSkinCinema(items,progress);
   return;
  }
  const e=await layer('/assets/spine/fx_ui_newgirl_gaino');
  try{
   const fig=e.fig;
   s4SuppressBakedGirlHeading(fig);
   // Avoid 104+324 repeated WebGL mounts; speed up native Spine playback.
   fig.state.timeScale=1.8;
   for(let i=0;i<items.length&&!skipped;i++){
    const entry=items[i];
    const owned=s4SlotChildren(fig);
    progress.textContent=(type==='girls'?'NỮ THẦN ':'TRANG PHỤC ')+
                         (i+1)+' / '+items.length;
    let uncap=()=>{};
    try{
     if(type==='girls'){
      await attachGirl(fig,entry.table_id);
      if(skipped)break;
      const placed=nativeNameStars(fig,entry,25);
      uncap=caption(entry,25,placed);
     }
     await run(fig,'texiao10');
     s4SuppressBakedGirlHeading(fig);
     if(skipped)break;
     sfx('ui_gain_hero_5star');
     await s4Pause(900);
    }catch(error){
     console.warn('S4 Wish: lỗi một lượt hiển thị',i+1,error);
    }finally{
     uncap();s4CleanupArt(owned);
    }
   }
  }finally{e.done();}
 }
 async function playS4Rewards(partners,skins){
  const girls=Array.isArray(partners)?partners:[];
  const costumes=Array.isArray(skins)?skins:[];
  if(overlay||(!girls.length&&!costumes.length))return;
  if(typeof PIXI==='undefined'||typeof GxbSpine==='undefined')return;
  skipped=false;s4Sequence=true;
  document.querySelector('.sa-waiting')?.remove();
  try{
   await assets();
   if(skipped)return;
   document.documentElement.classList.add('gxb-s4-cinematic');
   overlay=el('div','sa-overlay sa-s4-native-wish');
   const stage=el('div','sa-stage');
   const bg=el('img','sa-bg');bg.src='/assets/summon/summon_scene.png';
   bg.alt='Máy triệu hồi Wish nguyên bản';stage.append(bg);overlay.append(stage);
   const touch=el('div','sa-touch');touch.hidden=true;
   const hint=el('button','sa-hint','Chạm để tiếp tục');hint.type='button';hint.hidden=true;
   const cap=el('div','sa-caption');cap.hidden=true;
   const skip=el('button','sa-skip','Bỏ Qua');skip.type='button';
   skip.onclick=()=>{skipped=true;};
   const voice=el('button','sa-voice','♪ Nghe giọng');voice.type='button';
   voice.hidden=true;
   const progress=el('div','sa-s4-progress','Đang mở Wish S4…');
   const instruction=el('div','sa-s4-instruction','');
   overlay.append(touch,hint,cap,skip,voice,progress,instruction);
   (window.GxbFrame?.root()||document.body).append(overlay);
   try{await s4RevealSequence(girls,'girls',progress);}
   catch(error){console.warn('S4 Wish: pha Nữ Thần gặp lỗi',error);}
   // A damaged heroine asset must not prevent skins from getting their
   // own native Wish reveals.
   if(!skipped)try{await s4RevealSequence(costumes,'skins',progress);}
   catch(error){console.warn('S4 Wish: pha Skin gặp lỗi',error);}
  }catch(error){console.warn('Không phát được một phần Wish S4',error);}
  finally{
   overlay?.remove();overlay=null;s4Sequence=false;skipped=false;
   document.documentElement.classList.remove('gxb-s4-cinematic');
  }
 }
 // partners: [{table_id, star, name}] in draw order. Resolves when the sequence ends or is skipped.
 function waiting(summonId){
  document.querySelector('.sa-waiting')?.remove();
  const o=el('div','sa-waiting');const box=el('div','sa-waiting-box');
  const spin=el('i','sa-waiting-spin');box.append(spin,el('b','',"Đang triệu hồi..."),el('small','',"Đang kết nối với máy chủ"));
  o.append(box);(window.GxbFrame?.root()||document.body).append(o);
  assets().catch(()=>{});
  return ()=>o.remove();
 }
 async function play(summonId,partners,options={}){document.querySelector('.sa-waiting')?.remove();if(typeof PIXI==='undefined'||!partners?.length)return;
  skipped=false;s4Sequence=options.s4===true;
  await assets();
  overlay=el('div','sa-overlay');const stage=el('div','sa-stage');const bg=el('img','sa-bg');bg.src='/assets/summon/summon_scene.png';bg.alt='';stage.append(bg);overlay.append(stage);
  const touch=el('div','sa-touch');touch.hidden=true;const hint=el('button','sa-hint','Vuốt xuống để tiếp tục ▼');hint.type='button';hint.hidden=true;const cap=el('div','sa-caption');cap.hidden=true;
  const skip=el('button','sa-skip','Bỏ Qua');skip.type='button';skip.onclick=()=>{skipped=true;};const voice=el('button','sa-voice','♪ Nghe giọng');voice.type='button';voice.hidden=true;voice.setAttribute('aria-label','Phát giọng Nữ Thần');overlay.append(touch,hint,cap,skip,voice);(window.GxbFrame?.root()||document.body).append(overlay);
  try{const kind=KIND[summonId];
   if(kind){const m=await layer('/assets/spine/fx_ui_gacha_revision',1.2,.66);
    try{
     run(m.fig,kind+'04',true);await swipe();
     if(!skipped){sfx('vd_egg');await run(m.fig,kind+'01');}
     if(!skipped)await run(m.fig,kind+'02');
     if(!skipped){sfx('gacha_obtain');await run(m.fig,kind+'03');}
    }finally{m.done();}
   }
   // S4 is a long 24-goddess sequence. Recover per portrait instead of
   // aborting the entire gift on one damaged image or stalled animation.
   for(let i=0;i<partners.length&&!skipped;i++){
    try{await reveal(partners[i],i,!!kind);}
    catch(e){console.warn('Wish bỏ qua lượt hiển thị lỗi:',partners[i]?.name,e);}
   }
  }catch(e){console.warn("Summon animation unavailable",e);}
  finally{overlay?.remove();overlay=null;s4Sequence=false;}}
 return {play,playS4Rewards,waiting};
})();
