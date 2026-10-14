'use strict';
// Campaign window rebuilt from campaign_window.prefab + CampaignWindow.lua (720-unit layout):
// hang_group (idle scene with the hang team chibis fighting the stage monsters), hang_top_group (help, rank,
// campaign_resource counters, Collect), stage_scroller (zig-zag StageItem: odd stages s_group1 +27, even s_group2 −42,
// 153 px apart, route_bg between them) and hang_bottom_group (map/chapters, Fight, hang rewards).
const CampaignMap=(()=>{
 let lastMax=null,data=null,loading=null,root=null,chapter=null,sceneKey='',app=null,figures=[],loop=null,timer=null,popup=null,lastTick=0,lootFigure=null,lootMode=0;
 const A=n=>'/assets/campaign/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const load=()=>data?Promise.resolve(data):(loading||=Promise.all([api('/assets/campaign.json'),api('/assets/chibis/catalog.json?v=20261014-nephilim2')]).then(([c,k])=>{data={...c,chibis:k};return data;}));
 const stageLabel=s=>s?s.chapter+'-'+s.chapter_stage:'';
 const compact=n=>{const v=Number(n)||0;return v>=1e6?(Math.round(v/1e5)/10)+'M':v>=1e4?(Math.round(v/100)/10)+'K':number(v);};
 function hangStage(){return state.hang_info?.stage||state.next_stage||1;}

 function mount(){const panel=document.querySelector('.panel.campaign');if(!panel)return null;if(!root){root=el('div','cmp');root.id='cmp';panel.classList.add('cmp-on');panel.querySelector('.campaign-topbar')?.after(root);}return root;}

 function render(){if(view!=='campaign')return stop();if(!mount())return;if(!data){load().then(render);return;}
  const next=state.next_stage,stages=state.stages;const cur=stages.find(s=>s.id===hangStage())||stages[0];
  if(lastMax!==state.max_stage){lastMax=state.max_stage;chapter=null;}if(chapter==null)chapter=(stages.find(s=>s.id===Math.min(next,stages.length))||cur).chapter;
  $('campaign-gold').textContent=compact(state.items['1']);$('campaign-gems').textContent=compact(state.items['9']);
  lastTick=Math.floor((state.hang_info?.seconds||0)/5);
  root.replaceChildren();
  // --- idle scene ---
  const scene=el('div','cmp-scene');const shown=stages.find(s=>s.id===hangStage())||cur;scene.style.backgroundImage=`url('/assets/campaign/maps/${shown.map||'battle_map_26_1'}.webp')`;
  const title=el('div','cmp-title',stageLabel(shown)+(data.stages[shown.id]?.name?' '+data.stages[shown.id].name:''));scene.append(title);
  const stageBox=el('div','cmp-canvas');scene.append(stageBox);const fx=el('div','cmp-fx');scene.append(fx);root.append(scene);
  buildScene(stageBox,fx,shown);
  scene.onclick=e=>{if(e.target===scene&&typeof CampaignFlow!=='undefined')CampaignFlow.hangTeam();};entrances(scene);
  // --- map group ---
  const map=el('div','cmp-map');map.append(img(A('campaign_ground'),'cmp-ground'));root.append(map);
  const top=el('div','cmp-top');const help=el('button','cmp-round');help.type='button';help.append(img(A('btn_help')));help.onclick=()=>info("Campaign",["Clear stages with your lineup to advance through chapters and earn first-clear rewards.","Meanwhile, your team farms the selected stage: Gold, Girl EXP, and Player EXP accumulate every 5 s (up to 12 h), along with stage loot.","Tap a cleared stage to farm there. Collect claims accumulated rewards."]);
  const rank=el('button','cmp-round');rank.type='button';rank.append(img(A('btn_rank')));rank.onclick=()=>info("Ranking",["Campaign ranking relied on the original server and is unavailable in the local version.","Your progress: "+(state.max_stage||0)+" stages cleared."]);
  const res=el('div','cmp-res');res.style.backgroundImage=`url('${A('campaign_resource')}')`;for(const [id,key] of [['1','idle-gold'],['9','idle-gem'],['3','idle-exp']]){const g=el('span','cmp-res-item');g.append(img(A('icon_'+id)),el('b','','0'));g.dataset.item=id;res.append(g);}
  const collect=el('button','cmp-collect','Collect');collect.type='button';collect.style.backgroundImage=`url('${A('blue_btn_65_65')}')`;collect.onclick=()=>CampaignUI.collect();
  top.append(help,rank,res,collect);map.append(top);
  const strip=el('div','cmp-strip');const list=stages.filter(s=>s.chapter===chapter);
  list.forEach((s,i)=>{const up=s.id%2===0;const it=el('button','cmp-stage '+(up?'up':'down')+(s.id===hangStage()?' current':'')+(s.id===next?' next':'')+(!s.unlocked?' locked':''));it.type='button';
   const hex=el('span','cmp-hex');hex.append(img(A(data.stages[s.id]?.img||'stage_img'),'cmp-hex-img'),img(A(s.id===hangStage()||s.id===next?'stage_frame02':'stage_frame01'),'cmp-hex-frame'));if(!s.unlocked)hex.append(img(A('stage_lock'),'cmp-hex-lock'));
   it.append(hex,el('span','cmp-stage-label',stageLabel(s)));
   it.disabled=busy;it.title=(data.stages[s.id]?.name||("Stage "+stageLabel(s)))+(s.cleared?" · cleared":s.id===next?" · next":'');
   it.onclick=()=>{if(typeof CampaignFlow==='undefined'){if(s.id<=state.max_stage&&s.id!==hangStage())action('STAGE_HANG',{stage_id:s.id});else if(s.id===next)fight();return;}CampaignFlow.stageDetail(s,{onHang:s.id<=state.max_stage&&s.id!==hangStage()?()=>action('STAGE_HANG',{stage_id:s.id}):null,onFight:s.id===next?fight:null});};strip.append(it);});
  const ns='http://www.w3.org/2000/svg',route=document.createElementNS(ns,'svg');route.classList.add('cmp-road');route.setAttribute('aria-hidden','true');route.setAttribute('viewBox','0 0 '+(list.length*153)+' 260');route.style.width='calc('+list.length*153+' * var(--u))';
  for(let i=0;i<list.length-1;i++){const x=i*153+76.5,y=list[i].id%2===0?88:157,ny=list[i+1].id%2===0?88:157,mid=x+76.5,sign=Math.sign(ny-y),path=document.createElementNS(ns,'path');path.setAttribute('d',`M${x},${y} H${mid-8} Q${mid},${y} ${mid},${y+sign*8} V${ny-sign*8} Q${mid},${ny} ${mid+8},${ny} H${x+153}`);route.append(path);}strip.prepend(route);
  map.append(strip);requestAnimationFrame(()=>{const c=strip.querySelector('.next')||strip.querySelector('.current');if(c)strip.scrollLeft=Math.max(0,c.offsetLeft-strip.clientWidth/2+c.offsetWidth/2);});
  const bottom=el('div','cmp-bottom');const book=el('button','cmp-side');book.type='button';book.append(img(A('campaign_icon_map')));book.title="Chapters";book.onclick=chapters;
  const done=next>stages.length;const f=el('button','cmp-fight'+(done?' done':''));f.type='button';f.append(img(A('recover_bg'),'cmp-fight-bg1'),img(A('recover'),'cmp-fight-bg'),img(A(done?'campaign_battle_02':'campaign_battle_01'),'cmp-fight-art'),el('span','cmp-fight-label',done?"Cleared":'Fight'));f.disabled=done||busy;f.onclick=fight;
  const nextStage=stages.find(s=>s.id===next);if(nextStage&&!done)f.append(el('small','cmp-fight-stage',stageLabel(nextStage)+(state.level<nextStage.level_required?" · Lv. "+nextStage.level_required:'')));
  const gift=el('button','cmp-side');gift.type='button';gift.append(img(A('campaign_icon_gift')));gift.title="Idle rewards";gift.setAttribute('aria-label',"Idle loot");gift.onclick=rewards;if(state.hang_info?.rolls)gift.append(img(A('alert_icon'),'cmp-alert'));
  bottom.append(book,f,gift);map.append(bottom);
  tick();clearInterval(timer);timer=setInterval(tick,1000);}

 function fight(){const next=state.stages.find(s=>s.id===state.next_stage);if(!next)return;selectedStage=next.id;if(state.level<next.level_required){info("Level too low",["Requires Player Level "+next.level_required+" for stage "+stageLabel(next)+'.',"Collect idle rewards to earn Player EXP."]);return;}if(typeof CampaignFlow!=='undefined'){CampaignFlow.formation().then(async team=>{if(!team)return;try{const r=await api('/api/action',{message:'SET_HANG_TEAM',data:{partners:team}});state=r.state;}catch(e){GirlUI.toast(e.message);return;}action('MAP_FIGHT',{map_type:1,stage_id:next.id,partners:team});});return;}const team=formation();action('MAP_FIGHT',{map_type:1,stage_id:next.id,partners:team});}
 function tick(){if(view!=='campaign'||!root){clearInterval(timer);return;}const info=state.hang_info;if(!info)return;const extra=Math.floor((Date.now()-(info._t||(info._t=Date.now())))/1000);const secs=Math.min(info.max_seconds,info.seconds+(info.stage?extra:0)),ticks=Math.floor(secs/5);
  for(const g of root.querySelectorAll('.cmp-res-item'))g.querySelector('b').textContent=compact((info.economy?.[g.dataset.item]??(info.rate?.[g.dataset.item]||0)*Math.floor(info.seconds/5))+(info.rate?.[g.dataset.item]||0)*(ticks-Math.floor(info.seconds/5)));
  const c=root.querySelector('.cmp-collect');if(c){c.disabled=busy||!info.stage||ticks<1;c.classList.toggle('glow',ticks>=12*60);}
  const dropSecs=info.drop_seconds??info.seconds,interval=info.drop_interval||600,rolls=(info.rolls||0)+Math.floor(Math.min(info.max_seconds,dropSecs+extra)/interval)-Math.floor(dropSecs/interval);const gift=root.querySelector('.cmp-side:last-child');if(gift){gift.title=rolls?"Available loot: "+rolls+" draws":"Idle rewards";let badge=gift.querySelector('.cmp-alert');if(rolls&&!badge){badge=img(A('alert_icon'),'cmp-alert');gift.append(badge);}if(!rolls)badge?.remove();}
  showLoot(secs>21600?3:secs>10800?2:secs>1800?1:0);
  if(ticks>lastTick){lastTick=ticks;coin();}}

 // --- chibi scene (PIXI + original Spine chibis) ---
 function chibiFor(id){return data.chibis[String(id)]||data.chibis[String(id%100000)]||data.chibis[String(id%10000+50000)];}
 // The 720×627 campaign scene is independent from the 1080×1920 battle view.
 // Wide wing/FX rigs need a model-specific height, without changing other girls.
 function chibiScale(bounds,meta={}){
  const nativeHeight=Math.max(1,Number(bounds?.height)||1);
  const requested=Number(meta.mapHeight);
  const custom=Number.isFinite(requested)&&requested>=190&&requested<=330;
  return Math.min(custom?1.65:1.05,(custom?requested:190)/nativeHeight);
 }
 function chibiFacing(meta={}){
  return meta.facing==='left'||meta.facing===-1?-1:1;
 }
 async function buildScene(box,fx,stage){box.onclick=()=>typeof CampaignFlow!=='undefined'&&CampaignFlow.hangTeam();box.title="Tap to change your idle lineup";const team=(typeof CampaignFlow!=='undefined'?CampaignFlow.hangList():state.formation||[]).map(f=>({pos:f.pos,hero:state.roster.find(h=>h.partner_id===f.partner_id)})).filter(x=>x.hero);const monsters=(data.stages[stage.id]?.monsters||[]).slice(-2);
  const key=stage.id+'|'+team.map(t=>t.hero.table_id+':'+t.pos).join(',')+'|'+monsters.join(',');
  if(key===sceneKey&&app){box.append(app.view);return;}stop(true);sceneKey=key;
  if(typeof PIXI==='undefined')return;app=new PIXI.Application({width:720,height:627,transparent:true,antialias:true,resolution:Math.min(2,devicePixelRatio||1),autoDensity:false});app.view.className='cmp-pixi';box.append(app.view);app.stage.sortableChildren=true;figures=[];
  // Team on the left half (front row 1–2 ahead), monsters on the right, as in the hang scene.
  const spotsA=typeof CampaignFlow!=='undefined'?{1:[360,410],2:[185,300],3:[160,505]}:{1:[350,420],2:[320,500],3:[215,380],4:[170,450],5:[150,520],6:[250,535]},spotsB=[[560,300],[565,500],[620,415]];
  const add=async(id,x,y,flip,side)=>{const meta=chibiFor(id);if(!meta)return;try{const d=await GxbSpine.load('/assets/chibis/'+meta.model);if(!app)return;const f=new PIXI.spine.Spine(d);const idle=d.animations.some(a=>a.name==='idle')?'idle':d.animations[0]?.name;f.state.setAnimation(0,idle,true);f.state.timeScale=.9+Math.random()*.2;f.update(0);const b=f.getLocalBounds();const s=chibiScale(b,meta);const direction=(flip?-1:1)*chibiFacing(meta);f.scale.set(direction*s,s);f.x=x-(b.x+b.width/2)*s*direction;f.y=y-(b.y+b.height)*s;f.zIndex=y;app.stage.addChild(f);figures.push({f,idle,side,x,y});}catch{}};
  await Promise.all([...team.map(t=>add(t.hero.table_id,...(spotsA[t.pos]||[250,450]),false,'a')),...monsters.map((m,i)=>add(m,...spotsB[i],true,'b'))]);
  clearInterval(loop);loop=setInterval(()=>{if(!app||document.hidden)return;try{const a=figures.filter(x=>x.side==='a'),b=figures.filter(x=>x.side==='b');if(!a.length)return;const actor=a[Math.floor(Math.random()*a.length)];const kind=Math.random()<.2&&actor.f.state.hasAnimation('skill')?'skill':'attack';if(actor.f.state.hasAnimation(kind)){actor.f.state.setAnimation(0,kind,false);actor.f.state.addAnimation(0,actor.idle,true,0);}
   setTimeout(()=>{const t=b[Math.floor(Math.random()*b.length)];if(t&&t.f.state&&t.f.state.hasAnimation('hurt')){t.f.state.setAnimation(0,'hurt',false);t.f.state.addAnimation(0,t.idle,true,0);}},350);}catch{}},1500);}
 function campaignTrophy(){return state.missions_info?.trophies?.find(t=>t.type===25);}
 function entrances(scene){const dog=el('button','cmp-entrance cmp-dog');dog.type='button';dog.setAttribute('aria-label','Protect the Doggy');dog.append(img(A('dog_mini_game_enter_btn')),el('span','','Protect the Doggy'));dog.onclick=()=>info('Protect the Doggy',["The original shortcut opens dog_mini_game_choice_level_window. This minigame has not been restored yet."]);scene.append(dog);
  const t=campaignTrophy(),goal=state.stages.filter(s=>Number(s.chapter)===Number(t?.need)).at(-1),left=Math.max(0,(goal?.id||0)-(state.max_stage||0));
  const award=el('button','cmp-entrance cmp-award');award.type='button';award.setAttribute('aria-label',"Campaign rewards");award.append(img(A(t?.can?'campaign_award_icon2':'campaign_award_icon1')),el('span','',t?.can?'Claim':t?.done?'Cleared':left?'Reward after '+left+' Stages':'Campaign Rewards'));
  if(t?.can)award.append(img(A('alert_icon'),'cmp-alert'));
  if(t?.award){const preview=GrowthDiary.rewards(t.award.split('|').slice(0,2).join('|'));preview.classList.add('cmp-award-preview');award.append(preview);}
  award.onclick=campaignAwards;scene.append(award);
 }
 function campaignAwards(){const t=campaignTrophy();const b=box("Campaign rewards");if(!t){b.append(el('p','cr-sub',"No reward data."));ok(b);return;}b.append(el('p','cr-sub',t.text.replace('{1}',t.need)),el('p','cr-sub',"This reward unlocks after completing chapter "+t.need+". Reward after shows how many stages remain; inspect each stage for idle loot."),GrowthDiary.rewards(t.award));const claim=el('button','cr-btn',t.done?"Claimed":t.can?'Claim':"Not available yet");claim.type='button';claim.disabled=!t.can||busy;claim.onclick=async()=>{claim.disabled=true;try{const res=await api('/api/missions/action',{action:'trophy',type:25});state=res.state;close();render();CampaignUI.popup("Reward",res.got||{});}catch(e){claim.disabled=false;CampaignUI.popup(e.message,{});}};b.append(claim);ok(b);}
 async function showLoot(mode){if(!app)return;if(!mode){if(lootFigure)lootFigure.visible=false;lootMode=0;return;}if(lootFigure){lootFigure.visible=true;if(lootMode!==mode){lootFigure.state.setAnimation(0,['','num_3_state_down','num_2_state_down','num_1_state_down'][mode],true);lootMode=mode;}return;}const target=app;try{const d=await GxbSpine.load('/assets/campaign/loot');if(app!==target||lootFigure)return;const f=new PIXI.spine.Spine(d);f.state.setAnimation(0,['','num_3_state_down','num_2_state_down','num_1_state_down'][mode],true);f.update(0);const b=f.getLocalBounds(),s=900/Math.max(1,b.width);f.scale.set(s);f.x=360-(b.x+b.width/2)*s;f.y=598-(b.y+b.height)*s;f.zIndex=1000;f.interactive=false;target.stage.addChild(f);lootFigure=f;lootMode=mode;}catch{}}
 function coin(){const fx=root?.querySelector('.cmp-fx');if(!fx)return;for(const id of ['1','9']){const c=img(A('icon_'+id),'cmp-coin');c.style.left=(58+Math.random()*25)+'%';c.style.top=(55+Math.random()*20)+'%';fx.append(c);setTimeout(()=>c.remove(),1600);}}
 function stop(keepRoot){clearInterval(loop);loop=null;if(!keepRoot){clearInterval(timer);}if(app){try{app.destroy(true,{children:true,texture:false,baseTexture:false});}catch{}app=null;}figures=[];lootFigure=null;lootMode=0;if(!keepRoot)sceneKey='';}

 // --- popups ---
 function box(title){close();popup=el('div','cr-overlay');const b=el('div','cr-box small cmp-pop');b.append(el('h2','cr-title',title));popup.append(b);popup.onclick=e=>{if(e.target===popup)close();};(window.GxbFrame?.root()||document.body).append(popup);return b;}
 function close(){popup?.remove();popup=null;}
 function ok(b){const o=el('button','cr-btn',"OK");o.type='button';o.onclick=close;b.append(o);}
 function info(title,lines){const b=box(title);const u=el('ul','cr-tips');for(const l of lines)u.append(el('li','',l));b.append(u);ok(b);}
 // CampaignFortWindow (captures fb/94-95): difficulty tabs FORT_BTN_LABEL_1-5 (fort.lv: Normal 1-10, Hard 11-20, Extreme 21-30,
 // Fantasy 31-40, Nightmare 41-50); each chapter row shows its fort_img banner, "Chapter N" and the fort text; a locked chapter
 // is grey with "???" and the lock; the current one carries the crossed swords; "Unlock at Lv.{1}" uses the first stage level.
 let fortTab=0;
 function chapters(){const b=box('Map');b.classList.add('cmp-fort-box');const all=[...new Set(state.stages.map(s=>s.chapter))].sort((x,y)=>x-y);const tabs=["Normal",'Hard','Extreme','Fantasy','Nightmare'];
  if(!fortTab)fortTab=Math.ceil(chapter/10)||1;const nav=el('div','cmp-fort-tabs');tabs.forEach((t,i)=>{const d=i+1,open=state.stages.some(s=>Math.ceil(s.chapter/10)===d&&s.unlocked);const x=el('button',(fortTab===d?'on':'')+(open?'':' off'),t);x.type='button';x.onclick=()=>{fortTab=d;close();chapters();};nav.append(x);});b.append(nav);
  const list=el('div','cmp-forts');const cur=Math.ceil((state.next_stage&&state.stages.find(s=>s.id===state.next_stage)?.chapter)||chapter);
  for(const c of all.filter(c=>Math.ceil(c/10)===fortTab)){const ss=state.stages.filter(s=>s.chapter===c),open=ss.some(s=>s.unlocked),n=(c-1)%10+1,f=data.forts[c]||{};const row=el('button','cmp-fort'+(open?'':' locked')+(c===chapter?' on':''));row.type='button';
   const art=el('span','cmp-fort-art');art.style.backgroundImage=`url('${A('fort_img_'+n)}')`;row.append(art);
   if(open){row.append(el('b','',f.name||'Chapter '+n),el('span','',f.desc||''));if(c===cur)row.append(img(A('arena_sword'),'cmp-fort-sword'));}
   else{row.append(el('b','',f.name||'Chapter '+c),el('span','',"Preview · Lv. "+(ss[0]?.level_required||0)),img(A('lock'),'cmp-fort-lock'));}
   row.onclick=()=>{const need=ss[0]?.level_required||0;chapter=c;close();render();};list.append(row);}
  b.append(list);ok(b);requestAnimationFrame(()=>list.querySelector('.on')?.scrollIntoView({block:'center'}));}
 function rewards(){const i=state.hang_info||{};const b=box('Patrulla · '+(stageLabel(state.stages.find(s=>s.id===i.stage))||'—'));
  b.append(el('p','cr-sub',"Per hour: "+number((i.rate?.['1']||0)*720)+" Gold · "+number((i.rate?.['9']||0)*720)+" Girl EXP · "+number((i.rate?.['3']||0)*720)+" Player EXP"));
  b.append(el('p','cr-sub',"Possible loot (one roll every "+Math.round((i.drop_interval||600)/60)+' min):'));const g=el('div','cr-rewards');for(const id of String(i.drop_show||'').split('|').filter(Boolean)){const c=el('div','cr-reward');const it=itemCatalog?.[id];c.style.backgroundImage=`url('/assets/ui/quality_${Math.min(it?.quality||1,7)}.png')`;const src=it&&itemIcons.has(it.icon)?'/assets/item-icons/'+it.icon+'.png':(typeof Equipment!=='undefined'&&Equipment.icon?.(id))||'/assets/ui/item_bg.png';c.append(img(src));c.title=it?.name||"Item "+id;g.append(c);}b.append(g);
  b.append(el('p','cr-sub',"Pending draws: "+(i.rolls||0)));const col=el('button','cr-btn','Collect');col.type='button';col.onclick=()=>{close();CampaignUI.collect();};b.append(col);}
 return {render,stop,compact,chibiScale,chibiFacing};
})();
