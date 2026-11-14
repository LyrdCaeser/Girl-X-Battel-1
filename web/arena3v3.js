'use strict';
// Arena 3v3 (arena_3v3_window.prefab: same layout as Junior Varsity — title 0,495 · rank list 706×681 at 0,70 · detail
// 706×232 at 0,-395 · Awards / Record / Formation at 243,-330/-395/-460). Rules: gxb2/arena3v3.py. Three teams (team
// editor = Arena3v3BattleFormationWindow), best of three with the original battle engine. Reuses the ar- styles of
// arena.css; own pieces use the a3- prefix.
const Arena3v3=(()=>{
 let origin='arena',panel=null,note='',busyLocal=false,timer=null,draft=null,cur=0,pendingFight=null;
 const A=n=>'/assets/arena/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 function center(e,x,y,w,h){e.style.left=`calc(${360+x-w/2} * var(--u))`;e.style.top=`calc(${640-y-h/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;if(h!=null)e.style.height=`calc(${h} * var(--u))`;return e;}
 function root(){let r=$('arena3v3-view');if(!r){r=el('section','arena-view a3-view');r.id='arena3v3-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from){if(typeof NativeOnlineArenas==='undefined'){GirlUI?.notice?.('Đấu Trường Đội gốc đang tải, vui lòng thử lại.',{title:'Đấu Trường Đội'});return;}return NativeOnlineArenas.open('arena3v3',from);}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';if(id==='34')return A('icon_34');const row=itemCatalog?.[id];return (row&&itemPicture(row))||'';}
 function nameOf(id){id=String(id);return id==='1'?"Gold":id==='2'?"Gems":itemCatalog?.[id]?.name||"Item "+id;}
 function avatar(id,cls){const src=icon(id);return src?img(src,cls):el('span',cls+' empty','✦');}
 async function act(req){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/arena3v3/action',req);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;render();}}
 function clock(at){const s=Math.max(0,at-Math.floor(Date.now()/1000));const d=Math.floor(s/86400);return (d?d+'d ':'')+[Math.floor(s%86400/3600),Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');}
 function awards(parent,text){const w=el('div','ar-awards');for(const p of String(text||'').split('|')){const [k,n]=p.split('#');if(!k)continue;const c=el('span','ar-award');const s=icon(k);if(s)c.append(img(s));c.append(el('b','',number(n)));c.title=nameOf(k);w.append(c);}parent.append(w);return w;}
 const heroOf=pid=>(state.roster||[]).find(h=>h.partner_id===pid);
 const strength=h=>(h.stars||0)*1000+(h.lv||0);
 function teamsPower(teams){return (teams||[]).flat().reduce((s,x)=>{const h=heroOf(x.partner_id);return s+(h?40*(h.lv||1)+60:0);},0);} // same estimate as gxb2/arena.py power()
 function autoTeams(){const best=[...(state.roster||[])].sort((a,b)=>strength(b)-strength(a)).slice(0,18);const t=[[],[],[]];best.forEach((h,i)=>{const k=i%3;t[k].push({partner_id:h.partner_id,pos:t[k].length+1});});return t;}
 function render(){if(typeof NativeOnlineArenas!=='undefined'&&NativeOnlineArenas.isActive('arena3v3')){NativeOnlineArenas.render();return;}const r=root();if(view!=='arena3v3'){clearInterval(timer);timer=null;return;}const info=state.arena3v3_info;r.replaceChildren();const st=el('div','ar-stage');r.append(st);
  st.append(center(img(A('arena_3v3_scene'),'ar-bg'),0,1,1457,1457));
  Arena.chrome(st,()=>{if(origin==='arena')Arena.open('home');else showView(origin==='arena3v3'?'home':origin);});
  const shop=center(el('button','ar-icon-btn'),312,518,80,82);shop.type='button';shop.append(img(A('shop')));shop.title='League Store';shop.onclick=()=>Shops.open('arena3v3',5);st.append(shop);
  const help=center(el('button','ar-icon-btn'),-311,531,52,52);help.type='button';help.append(img(A('help_2')));help.onclick=()=>CampaignUI.popup(String(info?.help||'').replace(/\|/g,'\n')+"\n\nLocal opponents are simulated (Junior Varsity opponents with three teams). Each battle costs "+(info?.cost||3)+' Arena Tickets.',{});st.append(help);
  st.append(center(img(A('arena3v3_title_en_en'),'ar-title'),-10,495,364,104));
  if(!info||!info.opened){st.append(center(el('p','ar-note',"Loading…"),0,0,400,60));return;}
  const t=center(el('div','ar-ddl'),0,445,400,26);t.append(el('span','','Ending in: '),el('b','ar-clock',clock(info.season_end)));st.append(t);
  clearInterval(timer);timer=setInterval(()=>{const c=root().querySelector('.ar-clock');if(!c||view!=='arena3v3'){clearInterval(timer);return;}c.textContent=clock(info.season_end);},1000);
  const box=center(el('div','ar-rank'),0,70,706,681);box.style.borderImageSource=`url('${A('arena_bg')}')`;const list=el('div','ar-rank-list');box.append(list);
  info.board.forEach((p,i)=>list.append(Arena.rankRow(p,i,teamsPower(info.teams),q=>Arena.inspect(q))));
  if(info.rank>info.board.length){const row=el('div','ar-row me');row.append(el('span','ar-rk',String(info.rank)),el('span'),(()=>{const n=el('div','ar-name');n.append(el('b','',"You"));return n;})(),el('span','ar-pts',String(info.score)));list.append(row);}
  st.append(box);
  st.append(center(el('div','ar-detail'),0,-395,706,232));
  st.append(center(el('div','ar-me-icon'),-290,-347,114,114));st.lastChild.append(typeof portrait==='function'&&state.roster?.[0]?portrait(state.roster[0].table_id,100):el('span'));
  const pw=center(el('div','ar-power'),-194,-355,110,70);pw.append(img(A('force_icon')),el('b','',number(teamsPower(info.teams))));st.append(pw);
  for(const [label,val,y]of [['Rank',info.rank,-421],['Points',info.score,-465]]){const g=center(el('div','ar-stat'),-230,y,170,30);g.append(el('span','',label),el('b','',String(val)));st.append(g);}
  st.append(center(img(A('arena_decoration'),'ar-deco'),0,-411,270,164));
  const res=center(el('div','ar-res'),0,-334,220,36);res.append(el('span','',`Fight ×${info.cost}`),img(icon('34')),el('b','',String(info.tickets)));st.append(res);
  const fight=center(el('button','ar-fight'),0,-420,212,77);fight.type='button';fight.style.backgroundImage=`url('${A('blue_btn_65_65')}')`;fight.textContent='Fight';fight.onclick=()=>{panel='choose';render();};st.append(fight);
  for(const [label,ic,y,fn]of [['Reward','arena_award_s',-329,()=>{panel='awards';render();}],['Record','arena_record',-395,()=>{panel='record';render();}],['Defense','arena_defence',-464,()=>{draft=null;panel='teams';render();}]]){const b=center(el('button','ar-side'),243,y,168,54);b.type='button';b.style.backgroundImage=`url('${A('white_btn_65_65')}')`;b.append(img(A(ic)),el('span','',label));b.onclick=fn;st.append(b);}
  if(note)st.append(center(el('p','ar-note',note),0,-560,600,56));
  if(panel)popup(st,info);}
 function teamRow(label,units,onSlot){const row=el('div','a3-team');row.append(img(A('arena_3v3_t'+label),'a3-badge'));const slots=el('div','a3-slots');for(let p=1;p<=6;p++){const u=units.find(x=>x.pos===p);const s=el('button','a3-slot'+(u?' full':''));s.type='button';if(u){const h=u.table_id?u:heroOf(u.partner_id);if(h&&typeof portrait==='function')s.append(portrait(h.table_id,52));if(h?.lv)s.append(el('small','','Lv.'+h.lv));}if(onSlot)s.onclick=()=>onSlot(p,u);slots.append(s);}row.append(slots);return row;}
 function popup(st,info){const ov=el('div','ar-overlay');ov.onclick=e=>{if(e.target===ov){panel=null;render();}};const w=el('div','ar-win a3-win');ov.append(w);const close=el('button','ar-close','✕');close.type='button';close.onclick=()=>{panel=null;pendingFight=null;render();};
  if(panel==='choose'){w.append(el('h2','','Choose Opponent'),close);const ref=el('button','ar-small','Refresh');ref.type='button';ref.onclick=()=>act({action:'refresh'});w.append(ref);
   for(const e of info.enemies){const row=el('div','ar-enemy');row.append(avatar(e.avatar,'ar-av'));const n=el('div','ar-name');n.append(el('b','',e.name),el('small','',`Lv. ${e.lv} · Power ${number(e.power)} · ${e.sizes.join('/')} Girls`));row.append(n);const sc=el('div','ar-escore');sc.append(el('small','','Score'),el('b','',String(e.score)));row.append(sc);
    const f=el('button','ar-go');f.type='button';f.style.backgroundImage=`url('${A('blue_btn_65_65')}')`;f.append(el('span','','Fight'),img(icon('34')),el('b','',String(info.cost)));f.onclick=()=>{pendingFight=e;draft=null;panel='teams';render();};row.append(f);w.append(row);}
   if(!info.enemies.length)w.append(el('p','ar-empty',"Press Refresh to find opponents."));}
  else if(panel==='teams'){ // Arena3v3BattleFormationWindow: pick a team, tap Girls to add / slots to remove
   w.append(el('h2','',pendingFight?'Battle · vs '+pendingFight.name:'Formation'),close);if(!draft)draft=(info.teams&&info.teams.every(t=>t.length))?JSON.parse(JSON.stringify(info.teams)):autoTeams();
   const used=new Set(draft.flat().map(x=>x.partner_id));
   draft.forEach((t,k)=>{const row=teamRow(k+1,t,(p,u)=>{if(u){draft[k]=draft[k].filter(x=>x.pos!==p);}cur=k;render();});row.classList.toggle('on',cur===k);row.onclick=e=>{if(!e.target.closest('.a3-slot')){cur=k;render();}};w.append(row);});
   const tools=el('div','a3-tools');for(const [l,fn]of [['Auto',()=>{draft=autoTeams();render();}],['Clear',()=>{draft=[[],[],[]];render();}]]){const b=el('button','ar-small',l);b.type='button';b.onclick=fn;tools.append(b);}w.append(tools);
   const pool=el('div','a3-pool');for(const h of [...(state.roster||[])].sort((a,b)=>strength(b)-strength(a))){const on=used.has(h.partner_id);const c=el('button','a3-cand'+(on?' on':''));c.type='button';if(typeof portrait==='function')c.append(portrait(h.table_id,56));c.append(el('small','','Lv.'+(h.lv||1)));c.title=h.name;
    c.onclick=()=>{if(on){draft=draft.map(t=>t.filter(x=>x.partner_id!==h.partner_id));render();return;}const t=draft[cur];if(t.length>=6){note="Team "+(cur+1)+" already has 6 Girls";render();return;}let p=1;while(t.some(x=>x.pos===p))p++;t.push({partner_id:h.partner_id,pos:p});render();};pool.append(c);}w.append(pool);
   const acts=el('div','a3-acts');const save=el('button','ar-go',pendingFight?'':'Save');save.type='button';save.style.backgroundImage=`url('${A('blue_btn_65_65')}')`;
   if(pendingFight){save.append(el('span','','Fight'),img(icon('34')),el('b','',String(info.cost)));}
   save.onclick=async()=>{if(draft.some(t=>!t.length)){note="Each team needs at least 1 Girl";render();return;}if(pendingFight){const e=pendingFight;pendingFight=null;panel=null;await go(e,draft);}else{const r=await act({action:'teams',teams:draft});if(r){panel=null;note="Teams saved";render();}}};acts.append(save);w.append(acts);}
  else if(panel==='record'){w.append(el('h2','','Record'),close);for(const r of info.records){const row=el('div','ar-rec '+(r.win?'win':'lose'));row.append(el('b','',r.win?'WIN':'LOSE'),el('span','',r.name+' · '+(r.rounds||[]).map(x=>x?'✔':'✘').join(' ')),el('span','ar-delta',(r.delta>0?'+':'')+r.delta),el('small','',new Date(r.at*1000).toLocaleString()));w.append(row);}if(!info.records.length)w.append(el('p','ar-empty',"No battles yet."));}
  else if(panel==='awards'){w.append(el('h2','','Awards'),close);w.append(el('h3','','Season award (rank '+info.rank+')'));awards(w,info.season_award);w.append(el('p','ar-empty',"Distributed automatically at the end of the season."));}
  st.append(ov);}
 async function go(e,teams){const r=await act({action:'fight',id:e.id,teams});if(!r)return;const score=(r.rounds||[]).map(x=>x.win?'✔':'✘').join(' ');const last=r.reports?.[r.reports.length-1];
  CampaignUI.result(r.win,{...(r.got||{})},{event:true,label:'Arena 3v3 · '+score,report:last});note=`${r.win?"Victory":"Defeat"} (${score}) ${r.delta>0?'+':''}${r.delta} points`;render();}
 return {open,render};
})();
