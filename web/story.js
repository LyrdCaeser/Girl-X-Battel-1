'use strict';
// Main story (StoryWindow + StoryListWindow / StoryMemoryWindow / StoryListUnlockWindow). Rules: gxb2/story.py.
// StoryPlayer.play(plotId) shows a scene: background, character picture, name tag ('*' = the player), dialog, CG,
// shake, voice / music / ambience; tap to go on, Auto, Recall (log) and Skip. Story.open() = Memories.
const StoryPlayer=(()=>{
 const A='/assets/story/';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 let music=null,amb=null,voice=null,onVoiceFinish=null;
 window.addEventListener('gxb-audio-mute',e=>{
  const muted=!!e.detail?.muted;
  for(const a of [music,amb,voice]){
   if(!a)continue;
   if(muted){a.pause();if(a===voice&&onVoiceFinish){const done=onVoiceFinish;onVoiceFinish=null;done();}}
   else if(a.paused&&!a.ended)a.play().catch(()=>{});
  }
 });
 function scaledVolume(channel,base){return typeof GxbAudio!=='undefined'&&GxbAudio.volume?base*GxbAudio.volume(channel)/100:base;}
 window.addEventListener('gxb-audio-volume',e=>{
  const channel=e.detail?.channel,level=Math.max(0,Math.min(100,Number(e.detail?.level)||0))/100;
  if(channel==='music'&&music)music.volume=.45*level;
  if(channel==='effects'&&amb)amb.volume=.35*level;
  if(channel==='voice'&&voice)voice.volume=.9*level;
 });
 function stopAll(){for(const a of [music,amb,voice])if(a){a.pause();}music=amb=voice=null;onVoiceFinish=null;}
 function playLoop(kind,name){if(typeof GxbAudio!=='undefined'&&GxbAudio.muted?.())return;const cur=kind==='m'?music:amb;if(cur&&cur.dataset.name===name)return;if(cur)cur.pause();const a=new Audio(A+'snd/'+name+'.ogg');a.loop=true;a.volume=kind==='m'?scaledVolume('music',.45):scaledVolume('effects',.35);a.dataset.name=name;a.play().catch(()=>{});if(kind==='m')music=a;else amb=a;}
 function playerName(){return state?.profile?.name||state?.player?.name||'Học viên';}
 async function play(plotId,opts={}){let lines=opts.lines;if(!lines){try{lines=(await api('/api/story/scene',{plot:plotId})).lines;}catch{return;}}
  if(!lines?.length)return;const muted=typeof GxbAudio!=='undefined'&&GxbAudio.pause?GxbAudio.pause():null;
  return new Promise(resolve=>{const host=el('div','story-player');const frame=el('div','sp-frame');host.append(frame);document.body.append(host);
   let i=0,auto=false,readTimer=null,nextTimer=null,log=false,lineToken=0,autoGate=null;
   const clearTimers=()=>{clearTimeout(readTimer);clearTimeout(nextTimer);readTimer=nextTimer=null;};
   const bgA=el('div','sp-bg'),bgB=el('div','sp-bg');frame.append(bgA,bgB);let front=bgA,lastBg='';
   const picBox=el('div','sp-pics');const cgBox=el('div','sp-cg');frame.append(picBox,cgBox);
   const ctl=el('div','sp-ctl');const autoB=el('button','sp-pill','Tự Động');const recallB=el('button','sp-pill','Nhật Ký');ctl.append(autoB,recallB);
   const skip=el('button','sp-skip','⏭');const box=el('div','sp-dialog');const name=el('b','sp-name');const txt=el('p','sp-text');box.append(name,txt,el('i','sp-more','▼'));
   const title=opts.title?el('div','sp-title',opts.title):null;frame.append(ctl,skip,box);if(title)frame.append(title);
   const logBox=el('div','sp-log');logBox.hidden=true;frame.append(logBox);
   function tryAuto(){clearTimeout(nextTimer);if(!auto||log||!autoGate||!autoGate.read||!autoGate.voice||autoGate.token!==lineToken)return;nextTimer=setTimeout(()=>{if(auto&&!log&&autoGate?.token===lineToken)next();},250);}
   function finish(){lineToken++;clearTimers();host.remove();stopAll();if(muted&&GxbAudio.resume)GxbAudio.resume();resolve();}
   function show(){clearTimers();const L=lines[i];if(!L){finish();return;}const token=++lineToken;
    if(L.bg&&L.bg!==lastBg){lastBg=L.bg;const back=front===bgA?bgB:bgA;back.style.backgroundImage=`url('${A}bg/${L.bg}.webp')`;back.classList.add('on');front.classList.remove('on');front=back;}
    picBox.replaceChildren();if(L.pic){const p=img(`${A}pic/${L.pic}.webp`,'sp-pic');const [x]=String(L.xy||'0|0').split('|').map(Number);p.style.setProperty('--x',(x||0)/720*100+'cqw');p.style.setProperty('--s',L.sc||1);p.onerror=()=>p.remove();picBox.append(p);}
    cgBox.replaceChildren();const memory=L.cg==='memory_mask';cgBox.classList.toggle('memory',memory);if(L.cg&&!memory){cgBox.append(img(`${A}cg/${L.cg}.webp`,'sp-cgimg'));}
    const nm=L.n==='*'?playerName():(L.n||'');name.textContent=nm;name.hidden=!nm;box.classList.toggle('narration',!nm&&L.t===1);
    txt.textContent=String(L.d||'').replaceAll('*',playerName()).replace(/\[[^\]]*\]/g,'');
    if(L.j){frame.classList.remove('shake');void frame.offsetWidth;frame.classList.add('shake');}
    if(L.m)playLoop('m',L.m);if(L.a)playLoop('a',L.a);
    if(voice){voice.pause();voice=null;}onVoiceFinish=null;
    autoGate={token,read:false,voice:true};
    if(L.v&&!(typeof GxbAudio!=='undefined'&&GxbAudio.muted?.())){
     const current=new Audio(A+'snd/'+L.v+'.ogg');voice=current;current.volume=scaledVolume('voice',.9);autoGate.voice=false;
     const done=()=>{if(token!==lineToken)return;autoGate.voice=true;if(voice===current)onVoiceFinish=null;tryAuto();};
     onVoiceFinish=done;current.addEventListener('ended',done,{once:true});current.addEventListener('error',done,{once:true});current.play().catch(done);
    }
    readTimer=setTimeout(()=>{if(autoGate?.token!==token)return;autoGate.read=true;tryAuto();},Math.max(1800,(txt.textContent.length||10)*55));}
   function next(){i++;show();}
   frame.onclick=e=>{if(e.target.closest('.sp-ctl,.sp-skip,.sp-log'))return;if(log)return;next();};
   autoB.onclick=e=>{e.stopPropagation();auto=!auto;autoB.classList.toggle('on',auto);if(auto)tryAuto();else{clearTimeout(nextTimer);nextTimer=null;}};
   recallB.onclick=e=>{e.stopPropagation();log=!log;logBox.hidden=!log;if(log){clearTimeout(nextTimer);logBox.replaceChildren(el('b','sp-logtitle','Nhật Ký'));for(const L of lines.slice(0,i+1)){const n=L.n==='*'?playerName():L.n;logBox.append(el('p','',(n?n+': ':'')+String(L.d||'').replaceAll('*',playerName())));}logBox.scrollTop=logBox.scrollHeight;}else tryAuto();};
   logBox.onclick=e=>{e.stopPropagation();log=false;logBox.hidden=true;tryAuto();};
   skip.onclick=e=>{e.stopPropagation();finish();};
   show();});}
 return {play};
})();

const Story=(()=>{
 let origin='menu-explorer',catalog=null,episode=1,fort=null,note='',busyLocal=false;
 const A='/assets/story/';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;i.onerror=()=>i.remove();return i;};
 const btn=(cls,text,fn)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
 function root(){let r=$('story-view');if(!r){r=el('section','story-view');r.id='story-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function open(from){origin=from||view;fort=null;note='';showView('story');if(!catalog){try{catalog=await api('/api/story/catalog',{});}catch(e){note=e.message;}}render();}
 async function act(req){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/story/action',req);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;if(view==='story')render();}}
 const info=()=>state.story_info||{open:[],seen:[],keys:0};
 function render(){const r=root();if(view!=='story')return;r.replaceChildren();const st=el('div','sm-stage');r.append(st);
  const top=el('div','sm-top');const back=btn('sm-back','',()=>{if(fort){fort=null;render();}else showView(origin==='story'?'menu-explorer':origin);});back.append(img('/assets/ui/win_back_btn.png'));
  const keys=el('span','sm-chip');keys.append(img('/assets/story/cg/icon_208.png'),el('b','',`Chìa Khóa Ký Ức: ${info().keys}`));top.append(keys,back);st.append(top);
  st.append(el('h2','sm-title',fort?(catalog?.forts.find(f=>f.id===fort)?.name||''):'Ký Ức'));
  if(!catalog){st.append(el('p','sm-note',note||"Đang tải…"));return;}
  const opened=new Set(info().open);
  if(!fort){const tabs=el('div','sm-tabs');for(const e of catalog.episodes)tabs.append(btn('sm-tab'+(e.id===episode?' on':''),e.name,()=>{episode=e.id;render();}));st.append(tabs);
   const grid=el('div','sm-forts');for(const f of catalog.forts.filter(f=>f.episode===episode)){const secs=catalog.sections.filter(s=>s.fort===f.id);const open=secs.some(s=>opened.has(s.id))||!secs[0]?.former||opened.has(secs[0]?.former);
    const c=btn('sm-fort'+(open?'':' locked'),'',()=>{if(!open){note='Hoàn thành chương trước để mở khóa.';render();return;}fort=f.id;render();});c.append(img(A+'cg/'+f.icon+'.png','sm-fimg'),el('b','',f.name),el('small','',f.desc));
    const done=secs.filter(s=>opened.has(s.id)).length;c.append(el('span','sm-count',`${done}/${secs.length}`));grid.append(c);}
   st.append(grid);}
  else{const list=el('div','sm-list');for(const s of catalog.sections.filter(s=>s.fort===fort)){const open=opened.has(s.id);const row=btn('sm-sec'+(open?'':' locked'),'',()=>open?replay(s):unlockModal(s,opened));
    row.append(img(A+'cg/'+s.icon+'.png','sm-simg'));const t=el('div','sm-stext');t.append(el('b','',s.name),el('small','',`Ải ${s.label}`));row.append(t,el('span','sm-state',open?'▶':'🔒'));list.append(row);}st.append(list);}
  if(note)st.append(el('p','sm-err',note));}
 async function replay(s){for(const p of s.memory.length?s.memory:[s.pre,s.post].filter(Boolean))await StoryPlayer.play(p,{title:`${s.label} ${s.name}`});}
 async function unlockModal(s,opened){const formerOk=!s.former||opened.has(s.former);const [k,n]=(s.unlock||'208#2').split('#');
  const msg=`${s.name}\n\nVượt ải Chiến Dịch ${s.label} để mở khóa` + (formerOk?`\n\n…hoặc dùng ${n} Chìa Khóa Ký Ức để mở khóa ngay.`:'\n\nHoàn thành phần cốt truyện trước để mở khóa.');
  if(!formerOk||info().keys<Number(n)){note=formerOk?`Vượt ải Chiến Dịch ${s.label} để mở khóa (hoặc dùng ${n} Chìa Khóa Ký Ức; hiện có ${info().keys}).`:'Hoàn thành phần cốt truyện trước để mở khóa.';render();return;}
  if(await GirlUI.confirm(msg+'\n\nMở khóa phần truyện này?',{title:'Mở Khóa Cốt Truyện',ok:'Mở Khóa'}))act({action:'unlock',id:s.id});}
 return {open,render};
})();
