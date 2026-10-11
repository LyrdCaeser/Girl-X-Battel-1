'use strict';
// Shared Spine mounting, music, campaign idle bar and the battle result window.
// Sources: BattleWinWindow.lua / BattleFailWindow.lua (Spine shengli_new / shibai_new: texiao01 then texiao02),
// CampaignWindow.lua (idle income), sounds from hotres/sounds (converted to MP3 by tools/extract_visuals.py).

const GxbSpine=(()=>{
 const cache=new Map();
 function load(base){if(cache.has(base))return cache.get(base);const key='spine:'+base;const p=new Promise((resolve,reject)=>{const loader=new PIXI.Loader();loader.add(key,base+'/model.json',{metadata:{spineAtlasFile:base+'/model.atlas'}});loader.onError.add(reject);loader.load((_,res)=>res[key]?.spineData?resolve(res[key].spineData):reject(Error('Spine '+base)));});cache.set(base,p);p.catch(()=>cache.delete(base));return p;}
 // Mounts a skeleton centred in `host`; sequence = [[anim,loop],...]. Returns {destroy, figure}.
 async function mount(host,base,{width=720,height=720,sequence=null,fit=.9,y=.5,className='gxb-spine',scale=null,origin=null,preserve=false,resolution=null}={}){
  const data=await load(base);const app=new PIXI.Application({width,height,transparent:true,antialias:true,preserveDrawingBuffer:!!preserve,resolution:resolution||Math.min(2,devicePixelRatio||1),autoDensity:false});app.view.className=className;host.append(app.view);
  const fig=new PIXI.spine.Spine(data);const names=data.animations.map(a=>a.name);const seq=(sequence||[[names.find(n=>/idle|animation|daiji/i.test(n))||names[0],true]]).filter(([n])=>names.includes(n));
  if(seq.length){fig.state.setAnimation(0,seq[0][0],seq[0][1]);let delay=seq[0][1]?0:(data.findAnimation(seq[0][0])?.duration||0);for(const [n,l,track]of seq.slice(1)){if(track)fig.state.addAnimation(track,n,l,delay);else fig.state.addAnimation(0,n,l,0);}}fig.update(0);
  if(scale){fig.scale.set(scale);fig.x=width*(origin?.[0]??.5);fig.y=height*(origin?.[1]??.5);}else{const b=fig.getLocalBounds();const s=Math.min(width*fit/Math.max(1,b.width),height*fit/Math.max(1,b.height));fig.scale.set(s);fig.x=width/2-(b.x+b.width/2)*s;fig.y=height*y-(b.y+b.height/2)*s;}app.stage.addChild(fig);
  const handle={figure:fig,app,dead:false,idle:0,destroy(){if(handle.dead)return;handle.dead=true;live.delete(handle);try{app.destroy(true,{children:true,texture:false,baseTexture:false});}catch{}}};live.add(handle);
  return handle;
 }
 // Browsers keep ~16 live WebGL contexts and silently drop the oldest (battle chibis vanished). Every mount is
 // registered; canvases that stay detached from the page for two sweeps are destroyed.
 const live=new Set();
 function sweep(){for(const h of [...live]){if(h.app.view.isConnected){h.idle=0;continue;}if(++h.idle>=2)h.destroy();}}
 setInterval(sweep,1500);
 // Static frame for lists (Servant cards): renders once, keeps a PNG and frees the context. Serialized.
 let queue=Promise.resolve();
 function snapshot(host,base,opts={}){queue=queue.then(async()=>{if(!host.isConnected)return;let h;try{h=await mount(document.createElement('div'),base,{...opts,preserve:true});h.app.render();const im=new Image();im.src=h.app.view.toDataURL();im.className=opts.className||'gxb-spine';im.alt='';im.draggable=false;host.append(im);}catch{}finally{h?.destroy();}});return queue;}
 // One-shot UI effect of the original client over the game frame (level up, grade up, forge…): /assets/spine/<name>, converted on
 // demand by the server. Plays its first animation once and removes itself.
 async function burst(name,{scale=1,y=.45}={}){const frame=window.GxbFrame?.root()||document.body;const host=document.createElement('div');host.className='gxb-burst';frame.append(host);
  try{const h=await mount(host,'/assets/spine/'+name,{width:720,height:1280,scale,origin:[.5,y],className:'gxb-burst-canvas'});const a=h.figure.spineData.animations[0];if(!a){h.destroy();host.remove();return;}h.figure.state.setAnimation(0,a.name,false);setTimeout(()=>{h.destroy();host.remove();},Math.min(4000,Math.max(600,a.duration*1000+100)));}catch{host.remove();}}
 return {load,mount,snapshot,sweep,live,burst};
})();

const GxbAudio=(()=>{
 const TRACKS={home:'home_bg_music',campaign:'campaign_bg_music',battle:'battle_bg_music_1',campus:'main_story_campus'};
 let muted=false,current='',music=null,unlocked=false,wanted='home';
 try{muted=localStorage.getItem('gxb2-muted')==='1';}catch{}
 function src(name){return '/assets/sounds/'+name+'.mp3';}
 function play(track){wanted=track;if(!unlocked||muted){if(music)music.pause();return;}if(track==='home'&&homeTrack)track=homeTrack;if(current===track&&music&&!music.paused)return;if(music){music.pause();}current=track;music=new Audio(src(TRACKS[track]||track));music.loop=true;music.volume=.45;music.play().catch(()=>{});}
 function sfx(name,volume=.8){if(muted||!unlocked)return;const a=new Audio(src(name));a.volume=Math.max(0,Math.min(1,volume));a.play().catch(()=>{});lastSfx=performance.now();}
 // Game sound ids (xyd.SoundID / sound1-2 → assets/sounds/sounds.json) and skill sounds (skill.sound → skills.json).
 let table=null,skills=null,lastSfx=0,homeTrack='';const recent=new Map();
 try{homeTrack=localStorage.getItem('gxb2-bgm')||'';}catch{}
 const ready=fetch('/assets/sounds/sounds.json').then(r=>r.json()).then(j=>{table=j;}).catch(()=>{table={ids:{},songs:[],tracks:[]};});
 fetch('/assets/sounds/skills.json').then(r=>r.json()).then(j=>{skills=j;}).catch(()=>{skills={};});
 function id(n,scale=1){const row=table?.ids?.[String(n)];if(!row)return false;const now=performance.now();if(now-(recent.get(row.f)||0)<60)return true;recent.set(row.f,now);if(row.d)setTimeout(()=>sfx(row.f,row.v*scale),row.d*1000);else sfx(row.f,row.v*scale);return true;}
 function skill(skillId){const n=skills?.[String(skillId)];return n?id(n,1.6):false;}
 function bgm(name){homeTrack=name||'';try{localStorage.setItem('gxb2-bgm',homeTrack);}catch{}current='';play(wanted);}
 // Interface sounds as in the client: BACKWARD 2007 on back buttons, CLOSED 2008 on ✕, TAB 2009 on tabs, BUTTON 2006 otherwise.
 // A handler that plays its own sound within the same click wins (nothing is added on top).
 document.addEventListener('click',e=>{const b=e.target.closest?.('button,[role="button"]');if(!b||b.disabled||b.classList.contains('gxb-mute')||b.dataset.nosound!==undefined)return;const t0=performance.now();
  const c=(b.className||'')+' '+(b.id||'');const kind=/back/i.test(c)?2007:/(^|[-_ ])(x|close)($|[-_ ])|win-x/i.test(c)?2008:/tab|nav/i.test(c)?2009:2006;
  setTimeout(()=>{if(lastSfx<t0)id(kind,.7);},0);},true);
 function view(next){play(({home:'home','home-systems':'home',events:'home',campaign:'campaign','event-battle':'battle',tower:'campaign','daily-quiz':'campaign',patrol:'campaign','house-exam':'campaign','hero-challenge':'campaign','sanctuary-mode':'campaign','old-campus':'campaign',echoes:'campaign',shrine:'campaign',galaxy:'campaign',dress:'campus',campus:'campus',graduate:'campus',league:'campaign'})[next]||'home');}
 function toggle(){muted=!muted;try{localStorage.setItem('gxb2-muted',muted?'1':'0');}catch{}button.textContent=muted?'🔇':'🔊';if(muted)music?.pause();else{current='';play(wanted);}}
 const button=document.createElement('button');button.type='button';button.className='gxb-mute';button.title="Music";button.setAttribute('aria-label',"Toggle music");button.textContent=muted?'🔇':'🔊';button.addEventListener('click',e=>{e.stopPropagation();toggle();});
 document.addEventListener('DOMContentLoaded',()=>(window.GxbFrame?.root()||document.body).append(button));
 document.addEventListener('pointerdown',()=>{if(unlocked)return;unlocked=true;current='';play(wanted);},{capture:true});
 // pause()/resume(): the story player (story.js) plays its own music. muted(): story sounds follow the mute button.
 function pause(){if(music&&!music.paused){music.pause();return true;}return false;}
 function resume(){if(music&&!muted&&unlocked)music.play().catch(()=>{});}
 return {play,sfx,view,battle:()=>play('battle'),pause,resume,muted:()=>muted,id,skill,bgm,ready,table:()=>table,homeTrack:()=>homeTrack};
})();

const CampaignUI=(()=>{
 let timer=null,busy=false,overlay=null,spine=null;
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const clock=s=>[Math.floor(s/3600),Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');
 function iconFor(id){if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';if(typeof itemPicture==='function'&&itemCatalog?.[id]){const pic=itemPicture(itemCatalog[id]);if(pic)return pic;}const it=itemCatalog?.[id];if(it&&itemIcons?.has(it.icon))return '/assets/item-icons/'+it.icon+'.png';if(typeof Equipment!=='undefined'){const eq=Equipment.icon?.(id);if(eq)return eq;}const n=Number(id);if(n>20000000&&n<20010000)return '/assets/profile/head_'+(n-20000000)+'.png';if(n>=8001&&n<9000)return '/assets/profile/frame_'+n+'.png';if(n>=1010000&&n<1100000)return '/assets/original-ui/house-dress/img_'+n+'.png';return '/assets/ui/item_bg.png';} // avatars 2000xxxx, frames 8xxx, furniture 10xxxxx
 function nameFor(id){return ({'1':"Gold",'2':"Gems",'3':"Player EXP",'9':"Girl EXP"})[id]||itemCatalog?.[id]?.name||"Item "+id;}
 function norm(a){if(!Array.isArray(a))return a||{};const o={};for(const x of a){const id=String(x.item_id??x.id??x[0]),n=Number(x.item_num??x.num??x.count??x[1]??0);o[id]=(o[id]||0)+n;}return o;}
 function rewardGrid(awards){awards=norm(awards);const g=el('div','cr-rewards');for(const [id,n]of Object.entries(awards||{})){if(!n)continue;const c=el('div','cr-reward');const q=Math.min(itemCatalog?.[id]?.quality||1,7);c.style.backgroundImage=`url('/assets/ui/quality_${q}.png')`;const i=el('img');i.src=iconFor(id);i.alt='';c.append(i,el('b','',number(n)));c.title=nameFor(id)+' × '+number(n);g.append(c);}return g;}
 // ---- Idle bar (CampaignWindow) ----
 function idle(){if(view!=='campaign'||!state?.hang_info)return;const info=state.hang_info,start=Date.now()-0;paint(info,0);clearInterval(timer);timer=setInterval(()=>{if(view!=='campaign'){clearInterval(timer);timer=null;return;}paint(info,Math.floor((Date.now()-start)/1000));},1000);}
 function paint(info,extra){const secs=Math.min(info.max_seconds,info.seconds+(info.stage?extra:0)),ticks=Math.floor(secs/5);const r=info.rate||{};const set=(id,v)=>{const e=$(id);if(e)e.textContent=number(v);};set('idle-gold',(r['1']||0)*ticks);set('idle-gem',(r['9']||0)*ticks);set('idle-exp',(r['3']||0)*ticks);
  const chips=document.querySelector('.idle-counters');if(chips&&!chips.dataset.gxb){chips.dataset.gxb='1';const gem=chips.querySelector('.idle-chip.gem');if(gem)gem.firstChild.textContent='✦ ';gem?.setAttribute('title',"Girl EXP");}
  let t=document.querySelector('.idle-timer');if(!t){t=el('div','idle-timer');document.querySelector('.idle-bar')?.after(t);}const rolls=info.rolls+Math.floor(Math.max(0,extra)/info.drop_interval||0);t.textContent=info.stage?"Stage "+info.stage+' · '+clock(secs)+" / 12:00:00 · loot: "+rolls+" draw"+(rolls===1?'':'s'):"Clear stage 1 to accumulate rewards";
  const b=$('idle-collect');if(b){b.disabled=busy||!info.stage||ticks<1;b.title="Collect accumulated rewards";}}
 async function collect(){if(busy)return;busy=true;try{const r=await api('/api/campaign/action',{action:'collect'});state=r.state;GxbAudio.sfx('gain_window_sound');popup("Idle rewards",r.awards);}catch(e){popup(e.message,{});}finally{busy=false;render();}}
 function popup(title,awards){close();overlay=el('div','cr-overlay');const box=el('div','cr-box small');box.append(el('h2','cr-title',title),rewardGrid(awards));const ok=el('button','cr-btn',"OK");ok.type='button';ok.onclick=close;box.append(ok);overlay.append(box);overlay.onclick=e=>{if(e.target===overlay)close();};(window.GxbFrame?.root()||document.body).append(overlay);}
 // ---- Result window ----
 async function result(win,awards,opts={}){close();GxbAudio.sfx(win?'battle_win':'battle_lose');GxbAudio.play(opts.event?'battle':'campaign');
  overlay=el('div','cr-overlay '+(win?'win':'lose'));const box=el('div','cr-box');const stage=el('div','cr-anim');box.append(stage);
  const banner=el('img','cr-result-banner');banner.src='/assets/original-ui/battle-result/battle_result_text'+(win?'01':'02')+'_en_en.png';banner.alt=win?'VICTORY':'DEFEAT';box.append(banner);
  box.append(el('h2','cr-title',win?"Victory!":"Defeat"),el('p','cr-sub',opts.label||''));
  if(win){box.append(Object.keys(norm(awards)).length?rewardGrid(awards):el('p','cr-note',"Stage already cleared: no first-clear reward. Loot is earned through idle farming."));}
  else{const tips=el('ul','cr-tips');for(const t of ["Level up and promote your Girls","Equip them or forge better gear","Change your lineup: 2 in front, 4 in back"])tips.append(el('li','',t));box.append(tips);}
  if(opts.report?.hurts){const d=el('button','cr-detail');d.type='button';d.title="Battle statistics";const di=el('img');di.src='/assets/campaign/battle_detail_icon_2.png';di.alt='';d.append(di);d.onclick=()=>stats(opts.report);box.append(d);}
  const row=el('div','cr-actions');const ok=el('button','cr-btn',"Continue");ok.type='button';ok.onclick=()=>{close();if(opts.event){leaveEventBattle();}else{const a=$('arena');if(a)a.hidden=true;if(view==='campaign')window.scrollTo({top:0,behavior:'smooth'});}};row.append(ok);
  if(!win&&!opts.event){const up=el('button','cr-btn alt',"Upgrade Girls");up.type='button';up.onclick=()=>{close();showView('girls');};row.append(up);}box.append(row);overlay.append(box);(window.GxbFrame?.root()||document.body).append(overlay);
  try{spine=await GxbSpine.mount(stage,'/assets/spine/'+(win?'shengli_new':'shibai_new'),{width:720,height:520,scale:.65,origin:[.5,1.24],sequence:[['texiao01',false],['texiao02',true,1]],className:'cr-canvas'});}catch(e){stage.classList.add('fallback');stage.textContent=win?'VICTORY':'DEFEAT';}}
 // BattleStatisticsWindow: Ally | Enemy columns, Damage / Damage Taken / Heal (report.hurts: hurt, tank, heal per pos).
 function stats(report,mode='hurt'){let panel=document.querySelector('.cr-stats');if(!panel){panel=el('div','cr-stats');overlay.append(panel);}panel.replaceChildren();
  const head=el('div','cr-stats-head');const sword=el('img');sword.src='/assets/campaign/arena_sword.png';sword.alt='';const x=el('button','cr-stats-x','×');x.type='button';x.onclick=()=>panel.remove();head.append(el('b','','Ally'),sword,el('b','','Enemy'),x);panel.append(head);
  const tabs=el('div','cr-stats-tabs');for(const [k,l]of [['hurt','Damage'],['tank','Damage Taken'],['heal','Heal']]){const b=el('button',k===mode?'on':'',l);b.type='button';b.onclick=()=>stats(report,k);tabs.append(b);}panel.append(tabs);
  const units=new Map((report.display_units||[]).map(u=>[u.pos,u]));const vals=new Map((report.hurts||[]).map(h=>[h.pos,Number(h[mode]||0)]));const max=Math.max(1,...vals.values());
  const grid=el('div','cr-stats-grid');const al=[...units.keys()].filter(p=>p<=6).sort((a,b)=>a-b),en=[...units.keys()].filter(p=>p>6).sort((a,b)=>a-b);for(let i=0;i<Math.max(al.length,en.length);i++){for(const [side,pos] of [[0,al[i]],[1,en[i]]]){const u=units.get(pos);const cell=el('div','cr-stat'+(side?' enemy':''));if(u){const face=typeof portrait==='function'?portrait(u.table_id,52):el('span');face.classList?.add('cr-stat-face');const lv=el('span','cr-stat-lv',String(u.level||u.lv||''));const v=vals.get(pos)||0;const bar=el('div','cr-stat-bar');const f=el('i');f.style.width=(v/max*100)+'%';bar.append(f);const info=el('div','cr-stat-info');info.append(el('b','',number(v)),bar);const fw=el('div','cr-stat-facebox');fw.append(face,lv);if(side)cell.append(info,fw);else cell.append(fw,info);}grid.append(cell);}}panel.append(grid);}
 function close(){spine?.destroy();spine=null;overlay?.remove();overlay=null;}
 document.addEventListener('DOMContentLoaded',()=>{const b=$('idle-collect');if(b){const c=b.cloneNode(true);b.replaceWith(c);c.addEventListener('click',collect);}});
 return {idle,result,popup,close,collect};
})();
