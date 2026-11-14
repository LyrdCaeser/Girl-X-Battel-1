'use strict';

// Game audio and notification preferences. Each channel uses real publisher assets.
// No server state, rewards or gameplay flags are modified by these local settings.

// Menu (SettingUpWindow), Yume Collection (CollectionWindow) and Manga (ComicWindow), laid out at prefab coordinates on a
// 720-unit canvas (references docs/references/2026-09-30-user-b/02, 06, 07). Data: web/assets/menu/menu.json
// (tools/extract_settings_menu.py). Prefix sm-.
const SettingsMenu=(()=>{
 let screen='menu',origin='home',data=null,page=0;
 const A=n=>'/assets/menu/'+n+'.png';
 const el=(t,c,x)=>{const e=document.createElement(t);if(c)e.className=c;if(x!==undefined)e.textContent=x;return e;};
 const img=(src,c)=>{const i=el('img',c);i.src=src;i.alt='';i.draggable=false;return i;};
 const at=(e,x,y,w,h,top=640)=>{e.style.left=`calc(${x-w/2+360} * var(--u))`;e.style.top=`calc(${top-y-h/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;e.style.height=`calc(${h} * var(--u))`;return e;};
 const T=k=>data?.text?.[k]||k;
 function root(){let r=$('settings-menu-view');if(!r){r=el('section','sm-view');r.id='settings-menu-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function open(from,s='menu'){if(screen==='menu'||view!=='settings-menu')origin=from||view;screen=s;if(!data)data=await api('/assets/menu/menu.json');root();showView('settings-menu');draw();}
 function back(){if(screen!=='menu'){screen='menu';draw();}else showView(origin==='settings-menu'?'home':origin);}
 function top(r){const h=el('header','sm-top');for(const id of ['1','2']){const c=el('span','sm-res');c.append(img('/assets/currency/icon_'+id+'_small.png'),el('b','',number(state.items?.[id]||0)));h.append(c);}
  const b=el('button','sm-back');b.type='button';b.append(img('/assets/ui/win_back_btn.png'));b.setAttribute('aria-label',"Back");b.onclick=back;h.append(b);r.append(h);}
 function nav(r){const src=document.querySelector('.menu-explorer-bottom');if(src){const n=src.cloneNode(true);n.classList.add('sm-nav');n.querySelectorAll('button').forEach(b=>b.classList.toggle('current',b.dataset.menu==='settings'));r.append(n);}}
 function draw(){const r=root();if(view!=='settings-menu')return;r.replaceChildren();r.dataset.screen=screen;top(r);const st=el('div','sm-stage');r.append(st);
  if(screen==='collection')collection(st);else if(screen==='comic')comic(st);else menu(st);nav(r);}
 function btn(st,x,y,w,h,icon,iw,ih,label,fn,dx=-42){const b=at(el('button','sm-btn'),x,y,w,h);b.type='button';const i=img(A(icon),'sm-btn-icon');i.style.left=`calc(${w/2+dx-iw/2} * var(--u))`;i.style.width=`calc(${iw} * var(--u))`;i.style.height=`calc(${ih} * var(--u))`;b.append(i,el('span','sm-btn-label',label));b.onclick=fn;st.append(b);return b;}
 function lace(st,y,label){const g=at(el('div','sm-lace'),0,y,720,30);g.append(img(A('title_line02')),el('b','',label),img(A('title_line02')));st.append(g);}
 const soon=(title,text)=>()=>{const {body}=GirlUI.win({title,cls:'sm-win'});body.append(el('p','sm-note',text));};
 // SettingUpInfoWindow ("Help"): Help / FAQ tabs, each topic a "?" row that unfolds (help: subtitle + text, with the status
 // icons of "Status Icons"; FAQ: Q/A lines). "Faction Aura" lists group_buff (assets/group-buff/buffs.json).
 let helpData=null,auras=null;
 async function help(tab=0,openId=null){helpData=helpData||await api('/assets/menu/help.json');
  const {body}=GirlUI.win({title:'Trợ Giúp',cls:'sm-help'});const draw=async()=>{body.replaceChildren();const tabs=el('div','sm-htabs');['Hướng Dẫn','Câu Hỏi Thường Gặp'].forEach((n,i)=>{const b=el('button','sm-htab'+(tab===i?' on':''),n);b.type='button';b.onclick=()=>{tab=i;openId=null;draw();};tabs.append(b);});body.append(tabs);
   const list=el('div','sm-hlist');for(const t of tab?helpData.faq:helpData.help){const it=el('div','sm-hitem'+(openId===t.id?' open':''));const h=el('button','sm-hhead');h.type='button';h.append(el('b','sm-hq','?'),el('span','',t.title),el('i','sm-hchev',openId===t.id?'⌄':'›'));h.onclick=()=>{openId=openId===t.id?null:t.id;draw();};it.append(h);
    if(openId===t.id){const d=el('div','sm-hbody');
     if(t.aura){auras=auras||await api('/assets/group-buff/buffs.json');for(const a of Object.values(auras)){const r=el('div','sm-aura');const ic=img('/assets/group-buff/group_buff_on_'+a.id+'.png');ic.onerror=()=>{ic.src='/assets/group-buff/group_buff_off_'+a.id+'.png';};const tx=el('div');tx.append(el('b','',a.name),GirlUI.rich('p','',a.desc));const st=el('p','sm-aura-st');for(const p of String(a.show||'').split('|')){const [k,v]=p.split('#');if(k)st.append(el('span','',`${({hpP:'HP',atkP:'Attack',brk:'Armor Break',hit:'Precision',block:'Block',spd:'Speed',crit:'Crit',armP:'Armor'})[k]||k} +${Number(v)<1?Math.round(v*100)+'%':v}`));}tx.append(st);r.append(ic,tx);d.append(r);}}
     else if(t.sections){for(const s of t.sections){const sub=el('div','sm-hsub');for(const n of s.icons)sub.append(img('/assets/menu/buffs/'+n+'.png'));sub.append(el('b','',(s.icons.length?'':'◆ ')+s.title));d.append(sub);if(s.text)d.append(GirlUI.rich('p','sm-htext',s.text));}}
     else for(const l of t.lines)d.append(GirlUI.rich('p','sm-htext'+(/^\d+\.\s*Q/.test(l)?' q':''),l));
     it.append(d);}list.append(it);}body.append(list);const o=list.querySelector('.sm-hitem.open');if(o)o.scrollIntoView({block:'start'});};
  draw();}

 // Local-only audio mixer and badge visibility. The original menu layout is preserved.
 function audioAndNotifications(){
  const {body}=GirlUI.win({title:'Âm Thanh & Thông Báo',cls:'sm-sound-panel'});
  body.replaceChildren();
  const title=el('p','sm-sound-intro','Điều chỉnh âm lượng riêng cho Âm Thanh, Nhạc Nền và Voice Nữ Thần.');
  body.append(title);
  for(const [key,label] of [['effects','Âm Thanh'],['music','Nhạc Nền'],['voice','Voice Nữ Thần']]){
   const row=el('label','sm-sound-row');
   const heading=el('span','sm-sound-heading');
   const name=el('strong','',label),value=el('output','',GxbAudio.volume(key)+'%');
   heading.append(name,value);
   const slider=el('input','sm-volume-slider');slider.type='range';slider.min='0';slider.max='100';
   slider.step='1';slider.value=String(GxbAudio.volume(key));slider.setAttribute('aria-label','Âm lượng '+label);
   slider.oninput=()=>{GxbAudio.setVolume(key,Number(slider.value));value.textContent=slider.value+'%';};
   row.append(heading,slider);body.append(row);
  }
  const row=el('label','sm-sound-toggle');
  const check=el('input');check.type='checkbox';check.checked=GxbAudio.hiddenDots();
  const label=el('span','','Tắt dấu chấm đỏ thông báo');
  check.onchange=()=>GxbAudio.dots(check.checked);
  row.append(check,label);body.append(row);
  body.append(el('p','sm-sound-foot','Tùy chọn được lưu trên thiết bị. Không thay đổi trạng thái nhiệm vụ hoặc phần thưởng trên máy chủ.'));
 }
 // Jukebox (local addition): choose the Front Page music among the client's tracks and the ten Music Game songs.
 const TRACK_NAMES={home_bg_music:'Front Page',old_home_bg_music:'Front Page (classic)',campaign_bg_music:'Campaign',battle_bg_music_1:'Battle',main_story_battle:'Story · Battle',main_story_campus:'Story · Campus',story_vow:'Oath'};
 async function jukebox(){await GxbAudio.ready;const t=GxbAudio.table()||{tracks:[],songs:[]};const {body}=GirlUI.win({title:'Music',cls:'sm-juke'});const draw=()=>{body.replaceChildren();const cur=GxbAudio.homeTrack();
   const row=(file,title,sub)=>{const on=(cur||'')===file;const r=el('button','sm-song'+(on?' on':''));r.type='button';r.dataset.nosound='';r.append(el('i','',on?'♪':'▶'),el('b','',title),el('small','',sub||''));r.onclick=()=>{GxbAudio.bgm(file);GxbAudio.play('home');draw();};body.append(r);};
   body.append(el('h4','sm-juke-h','Game music'));row('','Default',"based on the screen");for(const f of t.tracks)if(f!=='home_bg_music')row(f,TRACK_NAMES[f]||f,'');
   body.append(el('h4','sm-juke-h','Music Game'));for(const sng of t.songs)row(sng.file,sng.title,sng.artist);
   body.append(el('p','sm-note',"The selected track plays on FrontPage and in menus; Campaign and battles keep their own music."));};draw();}
 function menu(st){st.classList.add('sm-menu');
  const big=[[-170,T('SETTING_UP_3'),'setting_icon_memories',()=>openMenu('memories','settings-menu')],[170,T('COLLECTION_TITLE'),'setting_icon_achieve',()=>{screen='collection';draw();}]];
  for(const [x,l,ic,fn]of big){const b=btn(st,x,451,312,128,ic,182,116,l,fn,-60);b.classList.add('big');}
  lace(st,335,T('SETTING_UP_1'));
  btn(st,-225,239,202,78,'setting_icon_notice',78,72,T('SETTING_UP_5'),soon(T('SETTING_UP_5'),"Notices came from the game server; there are no new notices in the local version."));
  btn(st,0,239,202,78,'setting_icon_help',78,72,T('SETTING_UP_6'),()=>help());
  btn(st,225,239,202,78,'setting_icon_enhance',78,72,T('SETTING_UP_7'),()=>openMenu('enhance','settings-menu'));
  btn(st,-225,141,202,78,'setting_icon_community',78,72,T('SETTING_UP_10'),soon(T('SETTING_UP_10'),"The game's social networks and community are unavailable offline."));
  btn(st,225,141,202,78,'setting_icon_comic',78,72,'Music',jukebox);
  btn(st,0,141,202,78,'setting_icon_gm',78,72,T('CHAT_LABEL_1'),soon(T('CHAT_LABEL_1'),"Chat with GMs required the original server."));
  lace(st,50,T('SETTING_UP_2'));
  btn(st,-225,-46,202,78,'setting_icon_comic',78,72,T('SETTING_UP_9'),()=>{screen='comic';page=0;draw();});
  btn(st,0,-46,202,78,'setting_icon_background',78,72,T('SETTING_UP_BACKGROUND'),()=>{if(typeof Wallpaper!=='undefined')Wallpaper.open();});
  btn(st,225,-46,202,78,'setting_icon_award',78,72,T('SETTING_UP_AWARD_1'),soon(T('SETTING_UP_AWARD_1'),"Redeem codes were validated by the game server; there are no local codes."));
  btn(st,0,-157,405,78,'setting_icon_notice',78,72,'Âm Thanh & Thông Báo',audioAndNotifications,-100).classList.add('sm-sound-entry');}
 // CollectionWindow: seven entrances with their progress (collected / collection.lua rows of that type) and the collect points
 // (item 123 awards of every collected row). Collected = the item is owned; Skins use the Costume Wardrobe count.
 function owned(type){const rows=data.collection[type]||[];const got=state.collection_info?.got;if(got){const g=new Set(got);return rows.filter(r=>g.has(r[0]));}if(type==='1'){const s=state.skins_info||{};const got=new Set((s.collected||[]).map(Number));return rows.filter(r=>got.has(r[1])||got.has(r[0])||Number(state.items?.[r[1]]||0)>0);}
  if(type==='5')return rows.filter(r=>Number(state.items?.[r[1]]||0)>0||(state.house_dress_info?.inventory?.[r[1]]||0)>0);
  if(type==='2'){const have=new Set(Object.values(state.souls_info?.items||{}).map(s=>Number(s.table_id)));return rows.filter(r=>have.has(r[1])||Number(state.items?.[r[1]]||0)>0);}
  return rows.filter(r=>Number(state.items?.[r[1]]||0)>0);}
 function pct(types){let got=0,all=0;for(const t of types){got+=owned(t).length;all+=(data.collection[t]||[]).length;}return all?Math.floor(100*got/all):0;}
 function collection(st){st.classList.add('sm-coll');
  st.append(at(img(A('collection_main_hero'),'sm-hero'),155,206,572,700,604));st.append(at(img(A('collection_logo_en_en'),'sm-logo'),-120,551,436,145,604));
  const book=at(el('div','sm-book'),0,-10,712,920,604);st.append(book);
  const ci=state.collection_info;let pts=ci?.points??0;if(!ci)for(const t of Object.keys(data.collection))for(const r of owned(t))pts+=r[2];
  const res=at(el('div','sm-points'),-232,420,178,40,604);res.append(img(A('icon_123')),el('b','',number(pts)));res.title="Collection Points · each point adds 1 VIP EXP";st.append(res);
  const shop=at(el('button','sm-shop'),296,420,80,82,604);shop.type='button';shop.append(img(A('shop')));shop.onclick=()=>collectionShop(1);st.append(shop);
  const titles=String(T('SEVEN_COLLECTION_TITLES')).split('|');const labels=['Skins','Icons & Frames','Antiques','Special Items','Furniture','Emojis','Backgrounds'];
  const nodes=[['collection_skin_bg',-161,101,316,488,['1'],()=>openMenu('costumes','settings-menu')],['collection_frame_icon',168,231,320,228,['3','4']],['collection_soul_icon',168,-16,316,254,['2']],
   ['collection_story_icon',-161,-256,316,162,['7'],()=>{if(typeof StoryItems!=='undefined')StoryItems.open('settings-menu');}],['collection_furniture_icon',168,-256,316,162,['5'],()=>openMenu('dorm','settings-menu')],['collection_face_icon',-161,-424,316,162,['8']],['collection_bg_icon',169,-422,318,166,['6']]];
  nodes.forEach(([pic,x,y,w,h,types,fn],i)=>{const c=at(el('button','sm-node'),x,y+50,w,h,604);c.type='button';c.append(img(A(pic),'sm-node-art'),el('b','sm-node-title',labels[i]||titles[i]));const key=['skin','frame','soul','story','furniture','face','bg'][i];const nd=ci?.nodes?.[key];const p=nd&&nd[1]?Math.floor(100*nd[0]/nd[1]):pct(types);const bar=el('div','sm-bar');const fill=el('i');fill.style.width=p+'%';bar.append(fill);c.append(bar,el('span','sm-pct',p+'%'));c.title=titles[i];c.onclick=fn||(()=>list(labels[i],types));st.append(c);});}
 // CollectionShopWindow: Rare Store (once ever) / Common Store (weekly), three stages unlocked by Collect Points.
 function shopIcon(id){if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}const m=/^2000(\d{4})$/.exec(id);if(m)return profileAsset('head_'+Number(m[1]));return null;}
 function collectionShop(tab){const ci=state.collection_info;if(!ci){GirlUI.toast("Loading…");return;}const {body,close}=GirlUI.win({title:'Collection Store',cls:'sm-win sm-cshop',help:'1. The merchandise in this store will be unlocked after having enough Collection Points and needs Coins or Gems to purchase.\n2. Common and Rare merchandise can be purchased only once.\n3. The Common Store limits refresh every Monday at 0:00. The Rare items never refresh.'});
  const tabs=el('div','sm-ctabs');[[1,'Rare Store'],[2,'Common Store']].forEach(([k,l])=>{const b=el('button',k===tab?'on':'',l);b.type='button';b.onclick=()=>{close();collectionShop(k);};tabs.append(b);});body.append(tabs);
  const head=el('div','sm-chead');const pi=el('span','sm-cpts');pi.append(img(A('icon_123')),el('b','',number(ci.points)));head.append(pi);if(tab===2){const t=el('span','sm-cweek');const upd=()=>{const s=Math.max(0,ci.week_end-(state.server_time||Date.now()/1000));t.textContent='Refresh '+Math.floor(s/86400)+'d '+String(Math.floor(s%86400/3600)).padStart(2,'0')+'h';};upd();head.append(t);}body.append(head);
  const rows=ci.shops[String(tab)]||[];ci.levels.forEach((lv,k)=>{const lock=ci.points<lv;const g=el('div','sm-cgroup'+(lock?' lock':''));g.append(el('h4','',lock?`🔒 Unlock after acquiring ${lv} Collection Points`:`✔ Stage ${k+1}`));const grid=el('div','sm-cgrid');
   for(const r of rows.filter(r=>r.point===lv)){const [ik,inum]=r.item.split('#');const [ck,cn]=r.cost.split('#');const sold=r.limit>=0&&r.bought>=r.limit;const c=el('div','sm-citem'+(sold?' sold':''));const ic=el('div','sm-cicon');const it=itemCatalog?.[ik];ic.style.backgroundImage=`url('/assets/ui/quality_${Math.min(Math.max(it?.quality||1,1),7)}.png')`;const src=r.icon||shopIcon(ik);if(src)ic.append(img(src));ic.append(el('b','',number(Number(inum))));const nm=r.name||it?.name||'#'+ik;c.title=nm;c.append(ic,el('small','sm-cname',nm));
    const b=el('button','sm-cbuy');b.type='button';if(sold)b.textContent='Sold out';else{b.append(img('/assets/currency/icon_'+ck+'_small.png'),el('span','',number(Number(cn))));}b.disabled=lock||sold||Number(state.items?.[ck]||0)<Number(cn);
    b.onclick=async()=>{if(!await GirlUI.confirm('Mua '+(r.name||it?.name||ik)+'?',{title:'Mua Bộ Sưu Tập',ok:'Mua'}))return;try{const res=await api('/api/collection/action',{action:'buy',shop:tab,id:r.id});state=res.state;close();collectionShop(tab);CampaignUI.popup('Collection Store',res.got);}catch(e){GirlUI.toast(e.message);}};c.append(b);grid.append(c);}
   g.append(grid);body.append(g);});}
 function list(title,types){const {body}=GirlUI.win({title,cls:'sm-win'});const g=el('div','sm-list');for(const t of types)for(const r of data.collection[t]||[]){const it=itemCatalog?.[r[1]];const got=owned(t).includes(r);const c=el('div','sm-item'+(got?'':' off'));const pic=it&&typeof itemPicture==='function'?itemPicture(it):null;if(pic)c.append(img(pic));else c.append(el('span','sm-q','?'));c.title=(it?.name||r[3]||'#'+r[0])+(got?'':" · not obtained");g.append(c);}body.append(g);}
 // ComicWindow: 9 episodes per page, newest first, the newest one in the book banner. Pages and covers come from the user's
 // manga folder (tools/extract_manga.py → /assets/menu/manga/<id>.webp); "Birthday" is a local extra tab for the 62
 // birthday mangas of that folder.
 let manga=null,mtab='ep',reader=null;
 const M=(id,c)=>'/assets/menu/manga/'+(mtab==='bd'?'birthday/':'')+id+(c?'_c':'')+'.webp';
 async function comic(st){st.classList.add('sm-comic');if(!manga){try{manga=await api('/assets/menu/manga/manga.json');}catch{manga={episodes:data.comics.map(c=>[c[0],c[1],false]),birthday:[]};}if(view==='settings-menu'&&screen==='comic')draw();return;}
  const list=mtab==='bd'?manga.birthday.map(b=>[b[0],b[1],true]):[...manga.episodes].reverse(),pages=Math.max(1,Math.ceil(list.length/9));page=Math.max(0,Math.min(page,pages-1));
  const banner=at(el('div','sm-banner'),0,470,742,356,640);banner.append(img(A('comic_banner_1')));const nw=el('button','sm-newest');nw.type='button';const first=list[0];nw.append(first?.[2]?img(M(first[0],true),'sm-cover'):img(A('setting_icon_comic'),'sm-ep-art'),el('span','sm-new','MỚI'));nw.onclick=()=>read(list,0);banner.append(nw);st.append(banner);
  if(manga.birthday.length){const tabs=at(el('div','sm-mtabs'),0,262,420,48,640);for(const [k,l]of [['ep','Tập Truyện'],['bd','Sinh Nhật']]){const b=el('button',mtab===k?'on':'',l);b.type='button';b.onclick=()=>{mtab=k;page=0;draw();};tabs.append(b);}st.append(tabs);}
  const box=at(el('div','sm-eps'),0,-40,700,630,640);list.slice(page*9,page*9+9).forEach((e,k)=>{const b=el('button','sm-ep');b.type='button';b.append(e[2]?img(M(e[0],true),'sm-cover'):img(A('setting_icon_comic'),'sm-ep-art'),el('b','',e[1]));b.onclick=()=>read(list,page*9+k);box.append(b);});st.append(box);
  const pg=at(el('nav','sm-pager'),0,-420,710,56,640);const go=p=>{page=Math.max(0,Math.min(p,pages-1));draw();};
  const arrow=(cls,src,p,flip)=>{const b=el('button','sm-pg '+cls);b.type='button';const i=img(A(src));if(flip)i.style.transform='scaleX(-1)';b.append(i);b.onclick=()=>go(p);pg.append(b);};
  arrow('edge','comic_double_arrow',0);arrow('','comic_arrow',page-1);
  const from=Math.max(0,Math.min(page-1,pages-3));for(let k=from;k<Math.min(pages,from+3);k++){const b=el('button','sm-pg num'+(k===page?' on':''),String(pages-k));b.type='button';b.onclick=()=>go(k);pg.append(b);}
  arrow('','comic_arrow',page+1,true);arrow('edge','comic_double_arrow',pages-1,true);st.append(pg);}
 // ComicDetailWindow: the whole page scrolls; ‹ › move to the next / previous episode.
 function read(list,k){const e=list[k];if(!e)return;if(!e[2]){const {body}=GirlUI.win({title:e[1],cls:'sm-win'});body.append(el('p','sm-note','Tập truyện này chưa được mở.'));return;}
  document.querySelector('.sm-reader')?.remove();const ov=el('div','sm-reader');const bar=el('div','sm-reader-bar');const prev=el('button','sm-rbtn','‹');prev.type='button';prev.disabled=k>=list.length-1;prev.onclick=()=>read(list,k+1);const next=el('button','sm-rbtn','›');next.type='button';next.disabled=k<=0;next.onclick=()=>read(list,k-1);
  const x=el('button','sm-rclose');x.type='button';x.setAttribute('aria-label',"Đóng");x.onclick=()=>ov.remove();bar.append(prev,el('b','',e[1]),next,x);const sc=el('div','sm-reader-page');sc.append(img(M(e[0])));ov.append(bar,sc);root().append(ov);}
 return {open,render:draw};
})();
