'use strict';
// Junior Varsity arena (arena_window.prefab: title 0,480 · rank list 706×681 at 0,71 · detail 706×232 at 0,-395).
// Rules: gxb2/arena.py. Fights run the original battle engine; the result reuses CampaignUI.result.
const Arena=(()=>{
 let origin='home',panel=null,note='',busyLocal=false,timer=null;
 const A=n=>'/assets/arena/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 function center(e,x,y,w,h){e.style.left=`calc(${360+x-w/2} * var(--u))`;e.style.top=`calc(${640-y-h/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;if(h!=null)e.style.height=`calc(${h} * var(--u))`;return e;}
 function root(){let r=$('arena-view');if(!r){r=el('section','arena-view');r.id='arena-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from,mode='arena'){if(typeof NativeOnlineArenas==='undefined'){GirlUI?.notice?.('Đấu Trường gốc đang tải, vui lòng thử lại.',{title:'Đấu Trường'});return;}return NativeOnlineArenas.open(mode,from);}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const row=itemCatalog?.[id];return (row&&itemPicture(row))||(row?.icon?'/assets/shops/items/'+row.icon+'.png':'');}
 function nameOf(id){id=String(id);return id==='1'?"Gold":id==='2'?"Gems":itemCatalog?.[id]?.name||"Item "+id;}
 function avatar(id,cls){
  const key=String(id||'').trim();
  if(/^(?:head|partner_avatar)_\d{4,9}$/.test(key)||/^custom_[0-9a-f]{32}$/.test(key)){
   const src=/^custom_[0-9a-f]{32}$/.test(key)?'/api/profile/photo/'+key+'.webp':'/assets/avatar-hd/profile/'+key+'.webp?v=1.1.2';
   const face=img(src,cls);
   face.onerror=()=>{face.onerror=null;face.src='/assets/profile/head_1001.png';};
   return face;
  }
  const src=icon(id);return src?img(src,cls):el('span',cls+' empty','✦');
 }
 async function act(req){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/arena/action',req);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;render();}}
 function clock(at){const s=Math.max(0,at-Math.floor(Date.now()/1000));const d=Math.floor(s/86400);return (d?d+'d ':'')+[Math.floor(s%86400/3600),Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');}
 function awards(parent,text){const w=el('div','ar-awards');for(const p of String(text||'').split('|')){const [k,n]=p.split('#');if(!k)continue;const c=el('span','ar-award');const s=icon(k);if(s)c.append(img(s));c.append(el('b','',number(n)));c.title=nameOf(k);w.append(c);}parent.append(w);return w;}
 function render(){if(typeof NativeOnlineArenas!=='undefined'&&NativeOnlineArenas.isActive('arena')){NativeOnlineArenas.render();return;}const r=root();if(view!=='arena'){clearInterval(timer);timer=null;return;}const info=state.arena_info;r.replaceChildren();const st=el('div','ar-stage');r.append(st);
  st.append(center(img(A('arena_scene'),'ar-bg'),0,7,1457,1457));
  chrome(st,()=>showView(origin==='arena'?'home':origin));
  const shop=center(el('button','ar-icon-btn'),312,516,80,82);shop.type='button';shop.append(img(A('shop')));shop.title='League Store';shop.onclick=()=>Shops.open('arena',5);st.append(shop);
  const help=center(el('button','ar-icon-btn'),-323,531,52,52);help.type='button';help.append(img(A('help_2')));help.onclick=()=>CampaignUI.popup("Junior Varsity: 2 free battles per day, then 1 Arena Ticket per battle (20 Gems each). Wins award points based on the opponent's score difference; daily ranks grant rewards. At season end (15 days), season rewards are distributed and scores reset to 1,000.",{});st.append(help);
  st.append(center(img(A('arena_title_en_en'),'ar-title'),0,500,356,104));
  {const e3=center(el('button','ar-3v3-entry'),-250,452,165,59);e3.type='button';e3.title='Arena 3v3';e3.append(img(A('btn_arena_3v3')));e3.onclick=()=>{if(typeof Arena3v3!=='undefined')Arena3v3.open('arena');};st.append(e3);} // Arena 3v3 entrance (btn_arena_3v3)
  if(!info){st.append(center(el('p','ar-note',"Loading…"),0,0,400,60));return;}
  const t=center(el('div','ar-ddl'),0,441,400,26);t.append(el('span','','Ending in: '),el('b','ar-clock',clock(info.season_end)));st.append(t);
  clearInterval(timer);timer=setInterval(()=>{const c=root().querySelector('.ar-clock');if(!c||view!=='arena'){clearInterval(timer);return;}c.textContent=clock(info.season_end);},1000);
  // Rank list
  const box=center(el('div','ar-rank'),0,71,706,681);box.style.borderImageSource=`url('${A('arena_bg')}')`;const list=el('div','ar-rank-list');box.append(list);
  info.board.forEach((p,i)=>list.append(rankRow(p,i,teamPower(),q=>inspect(q))));
  if(info.rank>info.board.length){const row=el('div','ar-row me');row.append(el('span','ar-rk',String(info.rank)),el('span'),(()=>{const n=el('div','ar-name');n.append(el('b','',"You"));return n;})(),el('span','ar-pts',String(info.score)));list.append(row);}
  st.append(box);
  // Detail group
  const d=center(el('div','ar-detail'),0,-395,706,232);st.append(d);
  st.append(center(el('div','ar-me-icon'),-290,-347,114,114));st.lastChild.append(typeof portrait==='function'&&state.roster?.[0]?portrait(state.roster[0].table_id,100):el('span'));
  const pw=center(el('div','ar-power'),-194,-355,110,70);pw.append(img(A('force_icon')),el('b','',number(teamPower())));st.append(pw);
  for(const [label,val,y]of [['Rank',info.rank,-421],['Points',info.score,-465]]){const g=center(el('div','ar-stat'),-230,y,170,30);g.append(el('span','',label),el('b','',String(val)));st.append(g);}
  st.append(center(img(A('arena_decoration'),'ar-deco'),0,-411,270,164));
  const res=center(el('div','ar-res'),0,-334,220,36);res.append(el('span','',info.free>0?`Free ×${info.free}`:''),img(icon('34')),el('b','',String(info.tickets)));const plus=el('button','ar-plus','+');plus.type='button';plus.onclick=async()=>{if(await GirlUI.confirm(`Mua 1 Vé Đấu Trường với ${info.ticket_price} Kim Cương?`,{title:'Xác Nhận Mua Vé',ok:'Mua'}))act({action:'buy_ticket',count:1});};res.append(plus);st.append(res);
  const fight=center(el('button','ar-fight'),0,-420,212,77);fight.type='button';fight.style.backgroundImage=`url('${A('blue_btn_65_65')}')`;fight.textContent='Fight';fight.onclick=()=>{panel='choose';render();};st.append(fight);
  for(const [label,ic,y,fn]of [['Reward','arena_award_s',-329,()=>{panel='awards';render();}],['Record','arena_record',-397,()=>{panel='record';render();}],['Defense','arena_defence',-464,()=>CampaignUI.popup("Defense uses your current lineup (there are no other players offline).",{})]]){const b=center(el('button','ar-side'),243,y,168,54);b.type='button';b.style.backgroundImage=`url('${A('white_btn_65_65')}')`;b.append(img(A(ic)),el('span','',label));b.onclick=fn;st.append(b);}
  if(note)st.append(center(el('p','ar-note',note),0,-560,600,56));
  if(panel)popup(st,info);}
 function teamPower(){const ids=new Set((state.formation||[]).map(f=>f.partner_id));return (state.roster||[]).filter(h=>ids.has(h.partner_id)).reduce((s,h)=>s+40*(h.lv||1)+60,0);} // same estimate as gxb2/arena.py power()
 function popup(st,info){const ov=el('div','ar-overlay');ov.onclick=e=>{if(e.target===ov){panel=null;render();}};const w=el('div','ar-win');ov.append(w);const close=el('button','ar-close','✕');close.type='button';close.onclick=()=>{panel=null;render();};
  if(panel==='choose'){w.append(el('h2','','Choose Opponent'),close);const ref=el('button','ar-small','Refresh');ref.type='button';ref.onclick=()=>act({action:'refresh'});w.append(ref);
   for(const e of info.enemies){const row=el('div','ar-enemy');row.append(avatar(e.avatar,'ar-av'));const n=el('div','ar-name');n.append(el('b','',e.name),el('small','',`Lv. ${e.lv} · Power ${number(e.power)}`));row.append(n);const sc=el('div','ar-escore');sc.append(el('small','','Score'),el('b','',String(e.score)));row.append(sc);
    const f=el('button','ar-go');f.type='button';f.style.backgroundImage=`url('${A('blue_btn_65_65')}')`;f.append(el('span','','Fight'),img(icon('34')),el('b','',info.free>0?'0':'1'));f.onclick=()=>go(e);row.append(f);w.append(row);}
   if(!info.enemies.length)w.append(el('p','ar-empty',"Press Refresh to find opponents."));}
  else if(panel==='record'){w.append(el('h2','','Record'),close);for(const r of info.records){const row=el('div','ar-rec '+(r.win?'win':'lose'));row.append(el('b','',r.win?'WIN':'LOSE'),el('span','',r.name),el('span','ar-delta',(r.delta>0?'+':'')+r.delta),el('small','',new Date(r.at*1000).toLocaleString()));w.append(row);}if(!info.records.length)w.append(el('p','ar-empty',"No battles yet."));}
  else if(panel==='awards'){w.append(el('h2','','Awards'),close);w.append(el('h3','','Daily rank award (rank '+info.rank+')'));awards(w,info.daily_award);const c=el('button','ar-small',info.daily_claimed?'Claimed':'Claim');c.type='button';c.disabled=info.daily_claimed;c.onclick=async()=>{const r=await act({action:'daily'});if(r?.got)CampaignUI.popup('Daily award',r.got);};w.append(c);w.append(el('h3','','Season award'));awards(w,info.season_award);w.append(el('p','ar-empty',"Distributed automatically at the end of the season."));}
  st.append(ov);}
 async function go(e){panel=null;const r=await act({action:'fight',id:e.id});if(!r)return;const got={...(r.got||{})};CampaignUI.result(r.win,got,{event:true,label:'Junior Varsity',report:r.report});note=`${r.win?"Victory":"Defeat"} ${r.delta>0?'+':''}${r.delta} points`;render();}
 // ArenaWindowItem (arena_window_item.prefab 656×103): 9gongge17 row (9gongge30/31/32 for the top three), rank_icon0n or the
 // number, PlayerIcon ×0.64 with its level, name, force_icon + power, the server tag (trial_bg07 + trial_icon13; one local
 // server) and "Points". Tapping the icon opens the rival's defence (ArenaFormationWindow / Arena3v3FormationWindow).
 const curStage=()=>document.querySelector('#'+(view==='arena3v3'?'arena3v3-view':'arena-view')+' .ar-stage');
 const scale=()=>(curStage()?.getBoundingClientRect().width||720)/720;
 function rankRow(p,i,me,onInspect){const top=i<3;const row=el('div','ar-row2'+(p.me?' me':''));row.style.borderImageSource=`url('${A(top?'9gongge3'+i:'9gongge17')}')`;
  const at=(e,x,y,w,h)=>{e.style.left=`calc(${328+x-w/2} * var(--u))`;e.style.top=`calc(${51.5-y-h/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;e.style.height=`calc(${h} * var(--u))`;return e;};
  if(top)row.append(at(img(A('rank_icon0'+(i+1)),'ar2-rk'),-271,2,86,62));else row.append(at(el('b','ar2-num',String(i+1)),-269,0,70,40));
  const ic=at(el('button','ar2-icon'),-177,1,64,64);ic.type='button';const px=Math.round(64*scale());
  ic.append(avatar(p.me?(state?.profile?.avatar||p.avatar):p.avatar,'ar2-av'));if(p.lv)ic.append(el('small','ar2-lv',String(p.lv)));
  if(!p.me&&onInspect)ic.onclick=()=>onInspect(p);row.append(ic);
  const nm=el('b','ar2-name',p.name);nm.style.left='calc(202 * var(--u))';nm.style.top='calc(14 * var(--u))';row.append(nm);
  const pw=el('span','ar2-power');pw.style.left='calc(208 * var(--u))';pw.style.top='calc(50 * var(--u))';pw.append(img(A('force_icon')),el('b','',number(p.me?me:p.power||0)));row.append(pw);
  const sv=at(el('span','ar2-server'),146,0,108,34);sv.style.backgroundImage=`url('${A('trial_bg07')}')`;sv.append(img(A('trial_icon13')),el('b','',p.server_id||'—'));row.append(sv);
  row.append(at(el('small','ar2-plabel','Points'),264,23.5,80,20),at(el('b','ar2-points',String(p.score)),264,-17.5,100,30));return row;}
 // ArenaFormationWindow: the rival's card and defence line-up(s)
 function inspect(p,title){const ov=el('div','ar-overlay');const w=el('div','ar-win ar-inspect');ov.append(w);ov.onclick=e=>{if(e.target===ov)ov.remove();};
  const x=el('button','ar-close','✕');x.type='button';x.onclick=()=>ov.remove();const head=el('div','ar-ins-head');const ic=el('div','ar2-icon');ic.append(avatar(p.avatar,'ar2-av'));if(p.lv)ic.append(el('small','ar2-lv',String(p.lv)));
  const info=el('div');info.append(el('b','',p.name),el('small','','ID '+(1000000+p.id*7919)%9000000),el('small','','Server S1 · Rival local'));head.append(ic,info,x);w.append(head);
  const d=el('div','ar-ins-def');d.append(el('b','','Defense'));const pw=el('span','ar2-power');pw.append(img(A('force_icon')),el('b','',number(p.power||0)));d.append(pw);w.append(d);
  const px=Math.round(56*scale());
  (p.teams||[]).forEach((t,k)=>{const r=el('div','ar-ins-team');if((p.teams||[]).length>1)r.append(el('b','ar-ins-n',String(k+1)));for(let s=0;s<6;s++){const u=t.find(v=>v.pos===s+1)||t[s];const c=el('div','ar-ins-slot');if(u){c.append(typeof portrait==='function'?portrait(u.table_id,px):el('span'));c.append(el('small','',String(u.lv)));}r.append(c);}w.append(r);});
  curStage().append(ov);}
 // WindowTop (gold · gems · back) and the bottom navigation, as in the Arena screens
 function chrome(st,onBack){const bar=center(el('div','ar-top'),0,612,720,56);for(const id of ['1','2']){const r=el('span','ar-top-res');r.append(img(icon(id)),el('b','',number(state?.items?.[id]||0)));bar.append(r);}
  const back=el('button','ar-top-back');back.type='button';back.append(img('/assets/ui/win_back_btn.png'));back.onclick=onBack;bar.append(back);st.append(bar);
  const src=document.querySelector('.menu-explorer-bottom');if(src){const n=src.cloneNode(true);n.classList.add('ar-nav');n.querySelectorAll('button').forEach(b=>b.classList.remove('current'));st.append(n);}}
 return {open,render,rankRow,inspect,chrome};
})();
