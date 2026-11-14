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
 let pics=null,pictures=null,skipped=false,overlay=null;
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const sfx=n=>{try{GxbAudio.sfx(n);}catch{}};
 const wait=ms=>new Promise(r=>setTimeout(r,ms));
 async function assets(){if(!pics){const [q,p]=await Promise.all([api('/assets/pictures.json').catch(()=>[]),api('/assets/partner-pictures.json').catch(()=>({}))]);pics=new Set(q);pictures=p;}}
 function run(fig,name,loop=false){return new Promise(res=>{if(!fig.spineData.findAnimation(name)){res();return;}const entry=fig.state.setAnimation(0,name,loop);if(loop){res();return;}entry.listener={complete:()=>res()};});}
 async function layer(base,scale=1,oy=.5){const host=el('div','sa-layer');overlay.querySelector('.sa-stage').append(host);const h=await GxbSpine.mount(host,base,{width:720,height:1280,scale,origin:[.5,oy],className:'sa-canvas',sequence:[['__none__',false]]});return {host,h,fig:h.figure,done(){h.destroy();host.remove();}};}
 function tapOrSkip(){return new Promise(res=>{const t=overlay.querySelector('.sa-touch');t.hidden=false;const go=()=>{t.hidden=true;t.onclick=null;clearInterval(k);res();};t.onclick=go;const k=setInterval(()=>{if(skipped)go();},100);});}
 function swipe(){return new Promise(res=>{const t=overlay.querySelector('.sa-touch');const hint=overlay.querySelector('.sa-hint');t.hidden=false;hint.hidden=false;let y0=null;
  const end=()=>{t.hidden=true;hint.hidden=true;t.onpointerdown=t.onpointerup=t.onclick=null;clearInterval(k);res();};
  t.onpointerdown=e=>{y0=e.clientY;};t.onpointerup=e=>{const r=overlay.getBoundingClientRect();if(y0!=null&&(e.clientY-y0)>r.height*100/1280)end();y0=null;};
  t.onkeydown=null;hint.onclick=end;const k=setInterval(()=>{if(skipped)end();},100);});}
 // The girl's picture follows the "juese" slot (PartnerSummonEffect:replacePartner, partner_picture_xy / scale).
 async function attachGirl(fig,tableId){const i=fig.skeleton.findSlotIndex('juese');const box=fig.slotContainers?.[i];if(!box)return;
  const showId=hostChain(tableId).find(id=>pics.has(Number(id)));const full=showId!==undefined;const url=full?'/assets/pictures/'+showId+'.webp':girlIconSource(tableId);if(!url)return;
  const image=await new Promise(resolve=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>resolve(null);im.src=url;});if(!image)return;
  const p=full?(pictures?.[String(showId)]||{}):{};const sp=new PIXI.Sprite(PIXI.Texture.from(image));sp.anchor.set(.5);const scale=full?(p.summon_static_scale||1):280/Math.max(image.naturalWidth,image.naturalHeight);sp.scale.set(scale,-scale);sp.position.set(p.xy?.[0]||0,150-(p.xy?.[1]||0));box.addChild(sp);
 }

 // PartnerSummonEffect:initEffect hides zhiye/cv/name (placeholder text art) and updateStar the "Nxing" slots above the
 // girl's stars; an empty texture keeps them hidden whatever the animation keys.
 function hideStars(fig,star){const names=['zhiye','cv','name'];for(let s=star+1;s<=5;s++)names.push(s+'xing');
  for(const n of names){if(fig.skeleton.findSlotIndex(n)>=0)try{fig.hackTextureBySlotName(n,PIXI.Texture.EMPTY,{width:1,height:1});}catch{}}return ()=>{};}
 function caption(p,star){
  const c=overlay.querySelector('.sa-caption');
  c.replaceChildren(el('b','',p.name||''));
  c.hidden=false;
  const voice=overlay.querySelector('.sa-voice');
  if(voice){
    voice.hidden=typeof Dates==='undefined';
    voice.onclick=()=>{if(typeof Dates!=='undefined')void Dates.playGirlVoice(p.table_id);};
  }
  if(typeof Dates!=='undefined')void Dates.playGirlVoice(p.table_id);
  return ()=>{c.hidden=true;if(voice)voice.hidden=true;};
 }
 async function reveal(p,i,summon){const star=Number(p.star)||5;
  if(star>=5){if(summon){const m=await layer('/assets/spine/fx_ui_gacha_revision',1.2,.66);sfx('vd_egg_5star');await run(m.fig,'222');m.done();if(skipped)return;}
   const e=await layer('/assets/spine/fx_ui_newgirl_gaino');await attachGirl(e.fig,p.table_id);const unhide=hideStars(e.fig,Math.min(star,5));const uncap=caption(p,star);sfx('ui_gain_hero_5star_bg');setTimeout(()=>sfx('ui_gain_hero_5star'),1000);
   const s=Math.min(star,11);await run(e.fig,ANIM1[s]||'texiao01');if(!skipped){run(e.fig,ANIM2[s]||'texiao04',true);await tapOrSkip();}unhide();uncap();e.done();}
  else{const e=await layer('/assets/spine/fx_ui_newgirl_gainp');await attachGirl(e.fig,p.table_id);const unhide=hideStars(e.fig,star);const uncap=caption(p,star);const left=summon&&i%2===1;sfx(left?'ui_gain_hero_left':'ui_gain_hero_right');
   await run(e.fig,left?'texiao03':'texiao01');unhide();uncap();e.done();}}
 // partners: [{table_id, star, name}] in draw order. Resolves when the sequence ends or is skipped.
 function waiting(summonId){
  document.querySelector('.sa-waiting')?.remove();
  const o=el('div','sa-waiting');const box=el('div','sa-waiting-box');
  const spin=el('i','sa-waiting-spin');box.append(spin,el('b','',"Đang triệu hồi..."),el('small','',"Đang kết nối với máy chủ"));
  o.append(box);(window.GxbFrame?.root()||document.body).append(o);
  assets().catch(()=>{});
  return ()=>o.remove();
 }
 async function play(summonId,partners){document.querySelector('.sa-waiting')?.remove();if(typeof PIXI==='undefined'||!partners?.length)return;await assets();skipped=false;
  overlay=el('div','sa-overlay');const stage=el('div','sa-stage');const bg=el('img','sa-bg');bg.src='/assets/summon/summon_scene.png';bg.alt='';stage.append(bg);overlay.append(stage);
  const touch=el('div','sa-touch');touch.hidden=true;const hint=el('button','sa-hint','Vuốt xuống để tiếp tục ▼');hint.type='button';hint.hidden=true;const cap=el('div','sa-caption');cap.hidden=true;
  const skip=el('button','sa-skip','Bỏ Qua');skip.type='button';skip.onclick=()=>{skipped=true;};const voice=el('button','sa-voice','♪ Nghe giọng');voice.type='button';voice.hidden=true;voice.setAttribute('aria-label','Phát giọng Nữ Thần');overlay.append(touch,hint,cap,skip,voice);(window.GxbFrame?.root()||document.body).append(overlay);
  try{const kind=KIND[summonId];
   if(kind){const m=await layer('/assets/spine/fx_ui_gacha_revision',1.2,.66);run(m.fig,kind+'04',true);await swipe();if(!skipped){sfx('vd_egg');await run(m.fig,kind+'01');}if(!skipped)await run(m.fig,kind+'02');if(!skipped){sfx('gacha_obtain');await run(m.fig,kind+'03');}m.done();}
   for(let i=0;i<partners.length&&!skipped;i++)await reveal(partners[i],i,!!kind);
  }catch(e){console.warn("Summon animation unavailable",e);}
  finally{overlay.remove();overlay=null;}}
 return {play,waiting};
})();
