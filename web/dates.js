'use strict';
// Dates (DatesListWindow / DatesWindow / DatesPledgeWindow / DatesAttrWindow). Rules: gxb2/relations.py.
// Layout from dates_window.prefab: full art, right panel dates_bg02 with the intimacy icon, 5 hearts and gifts,
// Gift / Voice tabs, bottom buttons. Voices: partner_dialog → sound1/sound2 → /assets/voice/<id>.mp3.
const Dates=(()=>{
 let data=null,loading=null,mode='list',pid=null,tab='gift',origin='home',bubble='',busyLocal=false,note='',many=false,audio=null,picked=null;
 const A=n=>'/assets/dates/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const load=()=>data?Promise.resolve(data):(loading||=api('/assets/relations.json').then(d=>data=d));
 const R=()=>data.rules,BASE=()=>Number(R().love_point_max_base),GROW=()=>Number(R().love_point_max_grow);
 function root(){let r=$('dates-view');if(!r){r=el('section','dates-view');r.id='dates-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from,partnerId){origin=from||view;pid=partnerId||null;mode=pid?'date':'list';tab='gift';bubble='';note='';load().then(()=>{api('/api/relations/action',{action:'visit'}).then(r=>{state=r.state;render();}).catch(()=>{});showView('dates');render();});}
 function hero(){return state.roster.find(h=>h.partner_id===pid);}
 function maxOf(h){return h?.is_vowed?GROW():BASE();}
 function iconOf(h){if(h?.is_vowed)return A('love_point_icon6');const row=data.appointment[Math.min(data.appointment.length-1,Math.floor((h?.love_point||0)/1000))];return A(row?.icon||'love_point_icon1');}
 function play(sound,text){if(text&&text!=='-1')bubble=text;try{audio?.pause();if(sound){audio=new Audio('/assets/voice/'+sound+'.mp3');audio.volume=.9;audio.play().catch(()=>{});}}catch{}}
 function allLines(h){const base=[String(h.table_id),String(h.table_id%100000),String(h.table_id%10000+50000)];for(const k of base)if(data.dialogs[k])return data.dialogs[k];return [];}
 async function act(request){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/relations/action',request);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;render();}}
 function render(){const r=root();if(view!=='dates')return;if(!data){load().then(render);return;}r.replaceChildren();top(r);if(mode==='date'&&hero())date(r);else{artHandle?.destroy?.();artHandle=null;artKey='';list(r);}}
 function top(r){const t=el('header','dt-top');for(const id of ['44','45']){const c=el('span','dt-cur');c.append(img(A('icon_'+id)),el('b','',number(state.items[id]||0)));c.title=itemCatalog?.[id]?.name||'';t.append(c);}const b=el('button','dt-back');b.type='button';b.append(img('/assets/ui/win_back_btn.png'));b.onclick=()=>{audio?.pause();if(mode==='date'&&!picked){mode='list';render();}else showView(origin==='dates'?'home':origin);};t.append(b);r.append(t);}

 // ---- DatesListWindow: girls sorted by intimacy ----
 function list(r){r.append(el('h2','dt-title','Dates'));const seen=new Set();const girls=[...state.roster].sort((a,b)=>(b.love_point||0)-(a.love_point||0)||b.stars-a.stars).filter(h=>{const k=h.table_id;if(seen.has(k))return false;seen.add(k);return true;});
  const g=el('div','dt-grid');for(const h of girls){const c=el('button','dt-card');c.type='button';c.append(typeof portrait==='function'?portrait(h.table_id,76):el('span'),img(iconOf(h),'dt-card-love'),el('b','',h.name),el('small','',(h.love_point||0)+' / '+maxOf(h)));c.onclick=()=>{pid=h.partner_id;picked=null;mode='date';bubble='';render();};g.append(c);}r.append(g);}

 // ---- DatesWindow (dates_window.prefab on a 720×1280 canvas) ----
 // Art = PartnerImg at partner_picture_xy (as the girl sheet); name + CV top-left; Gift / Voice tabs (dates_icon05/06);
 // right panel dates_bg02 (258×971 at 228,-30): intimacy icon (tap = Oath), 5 hearts, "Tap to send gift", the gifts
 // box (2 columns, favourite marks), Gift Box (43) and Make Gift; dialogue bubble; bottom Discuss / File / Date.
 let artHandle=null,artKey='';
 const at=(e,x,y,w,h)=>{e.style.left=`calc(${x-w/2+360} * var(--u))`;e.style.top=`calc(${640-y-(h||0)/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;if(h!=null)e.style.height=`calc(${h} * var(--u))`;return e;};
 function date(r){const h=hero();const st=el('div','dt-stage');st.style.backgroundImage=`url('/assets/scenes/college_scene${h.group||1}.png')`;r.append(st);
  const art=el('div','dt-art');st.append(art);const key=h.partner_id+':'+h.table_id;
  if(artKey!==key||!artHandle){artHandle?.destroy?.();artHandle=null;artKey=key;if(typeof Wallpaper!=='undefined'&&Wallpaper.mountArt)Wallpaper.mountArt(art,h.table_id,'xy').then(v=>{if(artKey!==key||!art.isConnected){v?.destroy();return;}artHandle=v;if(!v){const src=(typeof detailImage==='function'&&detailImage(h.table_id))||'';if(src)art.append(img(src,'dt-art-fallback'));}});}
  else art.append(artHandle.layer);
  art.onclick=()=>{const ls=allLines(h).filter(x=>x.type===1||x.type===2||x.type===3);const pick=ls[Math.floor(Math.random()*ls.length)];if(pick){play(pick.sound,pick.text);render();}};
  st.append(at(nameTag(h),-207,588,282,80));
  {const cv=data.cv?.[String(h.table_id)]||(typeof hostChain==='function'?hostChain(h.table_id).map(x=>data.cv?.[String(x)]).find(Boolean):'');if(cv){const c=at(el('div','dt-cv2'),230,600,250,34);c.append(el('span','','CV: '+cv));st.append(c);}}
  const help=at(el('button','dt-help'),60,535,52,52);help.type='button';help.append(img(A('help_2')));help.onclick=()=>CampaignUI.popup('Send gifts to raise intimacy: a gift she likes gives '+POINTS()[2]+', a normal one '+POINTS()[1]+' and one she dislikes '+POINTS()[0]+'. Every 2000 intimacy fills a heart and unlocks more voice lines. At '+BASE()+' you can form the Oath (1 Oath Ring) and the cap rises to '+GROW()+'. Make Gift turns 10 Gift Shards into the gift you choose; a Gift Box gives a random gift and 3-5 shards.',{});st.append(help);
  for(const [k,label,x,icon,icon2]of [['gift','Gift',168,'dates_icon07','dates_icon07_2'],['voice','Voice',290,'dates_icon12','dates_icon12_2']]){const b=at(el('button','dt-tab2'+(tab===k?' on':'')),x,537,122,61);b.type='button';b.style.backgroundImage=`url('${A(tab===k?'dates_icon06':'dates_icon05')}')`;b.append(img(A(tab===k?icon2:icon),'dt-tab-ic'),el('span','',label));b.onclick=()=>{tab=k;render();};st.append(b);}
  const panel=at(el('div','dt-side'),228,10,258,1000);panel.style.backgroundImage=`url('${A('dates_bg02')}')`;st.append(panel);
  const love=at(el('button','dt-love2'),228,420,128,128);love.type='button';love.append(img(iconOf(h)),el('b','',String(h.love_point||0)));love.title='Oath';love.onclick=()=>oath(h);st.append(love);
  for(let i=0;i<5;i++){const w=at(el('span','dt-heart2'),148+40*i,340,40,40);w.append(img(A('dates_icon40')));if((h.love_point||0)>=(i+1)*2000)w.append(img(A('dates_icon39'),'fill'));st.append(w);}
  if(tab==='gift'){st.append(at(el('p','dt-tip','Tap to send gift'),228,300,220,24));const box=at(el('div','dt-giftbox'),228,-5,216,580);gifts(box,h);st.append(box);
   const bag=at(el('button','dt-bluebtn'),228,-343,191,60);bag.type='button';bag.append(img(A('icon_43')),el('small','',short(Number(state.items['43']||0))),el('span','','Open'));bag.onclick=async()=>{const n=Number(state.items['43']||0);if(!n){note='No giftboxes available';render();return;}const r=await act({action:'open_box',count:many?Math.min(n,10):1});if(r?.got)CampaignUI.popup('Gift Box',r.got);};st.append(bag);
   const make=at(el('button','dt-bluebtn'),228,-413,191,60);make.type='button';make.append(img(A('icon_44')),el('small','',short(Number(state.items['44']||0))),el('span','','Make Gift'));make.onclick=()=>makeGift();st.append(make);
   const t=at(el('label','dt-many2'),228,-468,160,30);const cb=el('input');cb.type='checkbox';cb.checked=many;cb.onchange=()=>{many=cb.checked;};t.append(cb,el('span','','×10'));st.append(t);}
  else{const box=at(el('div','dt-voicebox'),228,-60,226,780);voices(box,h);st.append(box);}
  if(bubble){const bb=at(el('div','dt-bubble2'),-130,-156,450,null);bb.append(el('span','',bubble),img(A('partner_detail_bubble_arrow'),'dt-bubble-arrow'));st.append(bb);}
  for(const [label,icon,x,fn]of [['Discuss','dates_icon38',-282,()=>Station.open(h.table_id).then(ok=>{if(!ok){note='Coming soon~';render();}})],['File','dates_icon14',-130,()=>file(h)],['Date','dates_icon13',22,()=>dateStories(h)]]){const b=at(el('button','dt-btn2'),x,-476,143,80);b.type='button';b.style.backgroundImage=`url('${A('dates_btn')}')`;b.append(img(A(icon),'dt-btn-ic'),el('span','',label));b.onclick=fn;st.append(b);}
  if(note)st.append(at(el('p','dt-note2',note),0,-560,560,40));
  {const src=document.querySelector('.menu-explorer-bottom');if(src){const n=src.cloneNode(true);n.classList.add('dt-nav');n.querySelectorAll('button').forEach(b=>b.classList.remove('current'));r.append(n);}}}
 const POINTS=()=>R().love_gift_point.split('|').map(Number);
 // DatesGiftsWindow: Food / Toy / Accessory / Variety tabs, pick a gift, choose how many (10 Gift Shards each), Make.
 let makeGroup=1,makePick=null,makeNum=1;
 function makeGift(){const {body,close}=GirlUI.win({title:'Make Gift',cls:'dt-make-win'});const tabs=el('div','dt-make-tabs');['Food','Toy','Accessory','Variety'].forEach((l,k)=>{const b=el('button',makeGroup===k+1?'on':'',l);b.type='button';b.onclick=()=>{makeGroup=k+1;makePick=null;close();makeGift();};tabs.append(b);});body.append(tabs);
  const ids=Object.entries(data.gifts).filter(([,g])=>g.group===makeGroup).map(([id])=>id);if(!makePick||!ids.includes(makePick))makePick=ids[0];
  const grid=el('div','dt-make-grid');for(const id of ids){const b=el('button','dt-gift'+(makePick===id?' on':''));b.type='button';b.append(img(A('icon_'+id)),el('b','',short(Number(state.items[id]||0))));b.title=data.gifts[id].name;b.onclick=()=>{makePick=id;close();makeGift();};grid.append(b);}body.append(grid);
  const [ck,cn]=R().love_gift_cost.split('#');const max=Math.floor(Number(state.items[ck]||0)/Number(cn));makeNum=Math.max(1,Math.min(makeNum,Math.max(1,max)));
  const row=el('div','dt-make-row');row.append(el('b','dt-make-name',data.gifts[makePick]?.name||''));const minus=el('button','dt-num','−');minus.type='button';minus.onclick=()=>{makeNum=Math.max(1,makeNum-1);close();makeGift();};const plus=el('button','dt-num','+');plus.type='button';plus.onclick=()=>{makeNum=Math.min(Math.max(1,max),makeNum+1);close();makeGift();};const mx=el('button','dt-num','Max');mx.type='button';mx.onclick=()=>{makeNum=Math.max(1,max);close();makeGift();};
  const cost=el('span','dt-make-cost');cost.append(img(A('icon_'+ck)),el('b','',number(makeNum*Number(cn))+' / '+number(Number(state.items[ck]||0))));row.append(minus,el('b','dt-make-n','×'+makeNum),plus,mx,cost);body.append(row);
  const go=el('button','dt-bluebtn static','Make');go.type='button';go.disabled=max<1;go.onclick=async()=>{const r=await act({action:'compose',count:makeNum,item_id:Number(makePick)});close();if(r?.got)CampaignUI.popup('Success',r.got);};body.append(go);}
 function gifts(panel,h){const [first,count]=R().love_gift_item_num.split('|').map(Number);const g=el('div','dt-gifts');let any=false;
  for(let i=0;i<count;i++){const id=String(first+i),n=Number(state.items[id]||0);if(!n)continue;any=true;const b=el('button','dt-gift');b.type='button';const it=itemCatalog?.[id];b.style.backgroundImage=`url('/assets/ui/quality_${Math.min(Math.max(it?.quality||2,1),7)}.png')`;const src=A('icon_'+id);b.append(img(src),el('b','',short(n)));if(isLiked(h,id))b.append(img(A('dates_favorite'),'dt-fav'));b.title=(data.gifts[id]?.name||id);b.onclick=()=>give(h,id,many?Math.min(n,10):1);g.append(b);}
  if(!any)g.append(el('p','dt-empty','No gifts: open a Gift Box or Make one with Gift Shards.'));panel.append(g);
}
 const short=n=>n>=1e6?Math.floor(n/1e5)/10+'M':n>=1e4?Math.floor(n/1e3)+'K':String(n);
 function isLiked(h,id){return String(h.gift_like||'').split('|').includes(id);}
 async function give(h,id,num){const r=await act({action:'gift',partner_id:h.partner_id,item_id:Number(id),num});if(r){const ls=allLines(hero()).filter(x=>x.type===r.reaction);const pick=ls[Math.floor(Math.random()*ls.length)];play(pick?.sound,pick?.text||('+'+r.delta+' intimidad'));note='+'+r.delta+' intimidad';render();}}
 function voices(panel,h){const all=allLines(h);const love=h.love_point||0;const g=el('div','dt-voices');const types=new Map();for(const x of all){if(!types.has(x.type))types.set(x.type,[]);types.get(x.type).push(x);}
  let idx=0;for(const [type,ls]of types){const label=(data.dialog_types[type]||'Voice').replace(' {1}','');ls.forEach((x,i)=>{const lockAt=type===15?Math.min(BASE(),(i+1)*2000):type===16?(h.is_vowed?0:Infinity):0;const locked=love<lockAt;const b=el('button','dt-voice'+(locked?' lock':''));b.type='button';b.append(el('span','',label+(ls.length>1?' '+(i+1):'')));b.title=x.text&&x.text!=='-1'?x.text:'';b.disabled=locked||!x.sound;b.onclick=()=>{play(x.sound,x.text);render();};g.append(b);idx++;});}
  if(!idx)g.append(el('p','dt-empty',"This Girl has no voice lines in the data."));panel.append(g);}
 function attr(h){const rows=data.appointment;const lv=Math.floor((h.love_point||0)/1000);const cur=rows[Math.min(lv,rows.length-1)],next=rows[Math.min(lv+1,rows.length-1)];const fmt=b=>String(b||'—').split('|').map(p=>{const [k,v]=p.split('#');return k?(k==='atkP'?'Attack':k==='hpP'?'HP':k)+' +'+(Number(v)*100).toFixed(1)+'%':'—';}).join(' · ');
  CampaignUI.popup('Intimacy bonus',{});const box=document.querySelector('.cr-overlay .cr-box');const d=el('div','dt-attr');d.append(el('p','',"Level "+lv+': '+fmt(cur.bonus)),el('p','',"Next ("+next.point+'): '+fmt(next.bonus)),el('p','dt-small-note',"These bonuses apply in battle (original HeroAttr)."));box.querySelector('.cr-rewards')?.replaceWith(d);}
 function pledge(h){if(h.is_vowed){CampaignUI.popup(h.name+": Oath completed. Maximum Intimacy "+GROW()+'.',{});const l=allLines(h).find(x=>x.type===16);play(l?.sound,l?.text);return;}
  if((h.love_point||0)<BASE()){CampaignUI.popup("Oath requires "+BASE()+" Intimacy ("+(h.love_point||0)+' ahora).',{});return;}
  if(!confirm("Perform the Oath with "+h.name+'? Cuesta 1 anillo.'))return;act({action:'vow',partner_id:h.partner_id}).then(r=>{if(r){const l=allLines(hero()).find(x=>x.type===16);play(l?.sound,l?.text||'♥');note="Oath completed!";render();}});}
 // PartnerNameTag (partner_name_tag prefab 282×80): partner_name_frame_bg, faction at -90,2, stars at 18,17, name at 18,-21.
 function nameTag(h){const t=el('div','dt-nametag');t.append(img(A('partner_name_frame_bg'),'dt-nt-bg'));const g=girlsCatalog.find(x=>x.id===h.table_id);
  t.append(img('/assets/factions/'+(g?.group||h.group||1)+'.png','dt-nt-group'));const st=el('div','dt-nt-stars');const n=Number(h.stars||g?.stars||1);
  if(n>=10){st.append(img(A('potentiality_nametag_star'),'dt-nt-pot'),el('b','',String(n)));}else{const red=n>5;for(let i=0;i<(red?n-5:n);i++)st.append(img(A(red?'partner_star_red':'partner_star_yellow')));}
  t.append(st,el('b','dt-nt-name',h.name));return t;}
 // DatesDataWindow ("File"): partner_data_id texts unlocked at partner_data_lev intimacy; "[c][f55090]x[-][/c]" colours.
 function fmt(text,h){const [d1,d2]=(PARTNER_GIFTS(h)[1]||[]).map(id=>data.gifts[id]?.name||''),[l1,l2]=(PARTNER_GIFTS(h)[0]||[]).map(id=>data.gifts[id]?.name||'');
  const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');return esc(String(text||'').replace('{1}',d1||'').replace('{2}',d2||'').replace('{3}',l1||'').replace('{4}',l2||'')).replace(/\[c\]\[([0-9a-f]{6})\]/gi,'<b style="color:#$1">').replace(/\[-\]\[\/c\]/g,'</b>').replace(/\n/g,'<br>');}
 const bonusText=b=>{const parts=String(b||'').split('|').filter(p=>p.includes('#')).map(p=>{const [k,v]=p.split('#');return (k==='atkP'?'ATK':k==='hpP'?'HP':k)+' +'+(Number(v)*100).toFixed(1)+'%';});return parts.length?parts.join(' · '):'No Bonus';};
 const PARTNER_GIFTS=h=>[String(h.gift_like||'').split('|').filter(Boolean),String(h.gift_dislike||'').split('|').filter(Boolean)];
 function file(h){const list=data.files?.[String(h.table_id)]||(typeof hostChain==='function'?hostChain(h.table_id).map(x=>data.files?.[String(x)]).find(Boolean):null)||[];const lev=String(R().partner_data_lev).split('|').map(Number);
  const {body}=GirlUI.win({title:h.name+' · File',cls:'dt-file-win'});if(!list.length){body.append(el('p','dt-empty2','No file'));return;}
  list.forEach((d,i)=>{const need=i===0?0:lev[i-1]||0;const open=(h.love_point||0)>=need;const c=el('div','dt-file'+(open?'':' lock'));c.append(el('h4','',open?d.title:'🔒 Unlock at '+Math.floor(need/100)+' Intimacy'));if(open){const p=el('p');p.innerHTML=fmt(d.text,h);c.append(p);}body.append(c);});
  const rows=data.appointment;const lv=Math.floor((h.love_point||0)/1000);const cur=rows[Math.min(lv,rows.length-1)];const b=el('div','dt-file dt-file-bonus');b.append(el('h4','','Intimacy bonus'),el('p','',bonusText(cur?.bonus)));body.append(b);}
 // DatesStoryWindow ("Date"): the partner_achievement chain; finishing a task unlocks and plays its story (partner_plot).
 function dateStories(h){const key=chainKey(h);const info=key&&state.dates_info?.[String(key)];if(!info){note='This Girl currently has no story';render();return;}
  const {body,close}=GirlUI.win({title:h.name+' · Date',cls:'dt-story-win'});
  info.chain.forEach((id,i)=>{const a=data.achievements[String(id)]||{};const done=i<info.done,cur=i===info.done;const c=el('div','dt-story'+(done?' done':cur?' cur':' lock'));
   const pic=el('div','dt-story-pic');pic.style.backgroundImage=`url('${A((a.bg||'dates_plot_caocao')+(1+i%3))}')`;c.append(pic);
   const txt=el('div','dt-story-txt');txt.append(el('b','',done?('Story '+(i+1)):cur?'Mission':'Locked'),el('span','',done||cur?a.desc:'Unlock by finishing the story'));
   if(cur)txt.append(el('small','',info.have+' / '+info.need));c.append(txt);
   const b=el('button','dt-story-btn');b.type='button';
   if(done){b.textContent='Replay';b.onclick=()=>{close();playPlot(a.plot);};}
   else if(cur){b.textContent=Number(a.type)===5?'Consume':'Unlock';b.disabled=!info.ready;b.onclick=async()=>{const r=await act({action:'date_step',table_id:key});if(r?.plot){close();playPlot(r.plot);}};if(!info.ready)b.title='Finish this mission to unlock the story.';}
   else{b.textContent='Locked';b.disabled=true;}c.append(b);body.append(c);});}
 function chainKey(h){const ids=typeof hostChain==='function'?hostChain(h.table_id):[h.table_id];return ids.find(x=>state.dates_info?.[String(x)])||[...String((h.show_ids||'')).split('|')].map(Number).find(x=>state.dates_info?.[String(x)])||0;}
 async function playPlot(plot){try{const r=await api('/api/relations/plot',{plot});if(r.lines?.length&&typeof Story!=='undefined')Story.play(plot,{lines:r.lines,title:r.title});}catch(e){note=e.message;render();}}
 // DatesPledgeWindow · Marriage Certificate (dates_pledge_window 660×1042): frame dates_bg09 + dates_bg17 (mirrored halves),
 // title dates_text01, Groom (player) / Bride (girl) with rect_bg underlines, Intimacy chip dates_bg15 (points / 100) and Bonus,
 // the girl's picture, the vow text on dates_bg11 lace with the date, and the wax seal: dates_icon41 = Vow (not yet sworn),
 // dates_icon42 = sealed. Tap outside to close.
 // The girl's wedding skin (partner_picture.is_wedding): the Oath gives it, and the certificate of a married girl shows it.
 let wedCache=null;
 async function weddingSkin(h){if(!wedCache){try{const [pics,cat]=await Promise.all([api('/assets/partner-pictures.json'),api('/api/skins/catalog',{})]);wedCache={pics,skins:cat.skins||{}};}catch{wedCache={pics:{},skins:{}};}}
  const ids=typeof hostChain==='function'?hostChain(h.table_id):[h.table_id];const si=state.skins_info||{};
  const owned=id=>Number(si.owned?.[String(id)]||0)>0||(si.collected||[]).map(Number).includes(Number(id))||(state.roster||[]).some(x=>Number(x.equips?.[6]||0)===Number(id));
  for(const [id,row]of Object.entries(wedCache.skins))if(wedCache.pics[id]?.wed&&row.partners.some(p=>ids.includes(Number(p))))return Number(id);return 0;}
 function oath(h){document.querySelector('.dt-cert-ov')?.remove();const ov=el('div','dt-cert-ov');const c=el('div','dt-cert');ov.append(c);ov.onclick=e=>{if(e.target===ov)ov.remove();};
  const P=(e,x,y,w,hh)=>{e.style.left=`calc(${x+330-w/2} * var(--c))`;e.style.top=`calc(${536-y-hh/2} * var(--c))`;e.style.width=`calc(${w} * var(--c))`;e.style.height=`calc(${hh} * var(--c))`;c.append(e);return e;};
  P(img(A('dates_bg09'),'dt-c-bg'),-165,15,330,1042);P(img(A('dates_bg09'),'dt-c-bg flip'),165,15,330,1042);
  P(img(A('dates_bg17'),'dt-c-bg'),-157,5,314,946);P(img(A('dates_bg17'),'dt-c-bg flip'),157,5,314,946);
  // groupPicture (0,-127): the girl's PartnerImg in a 720×1280 frame centred there, clipped to the certificate paper
  const pic=P(el('div','dt-c-pic'),0,-60,600,520);const frame=el('div','dt-c-frame');frame.style.cssText=`left:calc(-60 * var(--c));top:calc(-313 * var(--c));width:calc(720 * var(--c));height:calc(1280 * var(--c))`;pic.append(frame);
  (h.is_vowed?weddingSkin(h):Promise.resolve(0)).then(id=>{const show=id||h.table_id;if(typeof Wallpaper!=='undefined'&&Wallpaper.mountArt)Wallpaper.mountArt(frame,show,'xy').then(v=>{if(!v){const src=(typeof detailImage==='function'&&detailImage(show))||'';if(src)frame.append(img(src));}});});
  P(img(A('dates_text01_en_en'),'dt-c-title'),0,431,418,70);
  P(img(A('dates_text02_en_en'),'dt-c-lab'),-131,344,80,34);P(img(A('dates_text03_en_en'),'dt-c-lab'),-131,302,80,34);
  P(el('b','dt-c-val',state.name||'Senpai'),48,346,250,30);P(el('b','dt-c-val',h.name),48,302,250,30);P(el('i','dt-c-rule'),43,330,248,2);P(el('i','dt-c-rule'),43,285,248,2);
  const chip=P(el('span','dt-c-chip','Intimacy'),-217,246,102,32);chip.style.borderImageSource=`url('${A('dates_bg15')}')`;
  P(el('b','dt-c-num',Math.floor((h.love_point||0)/100)+'/'+Math.floor(maxOf(h)/100)),-120,249,100,28);P(el('i','dt-c-rule'),-118,231,100,2);
  P(el('b','dt-c-bonus','Bonus:'),-22,249,90,28);P(el('b','dt-c-num left',bonusText(data.appointment[Math.min(Math.floor((h.love_point||0)/1000),data.appointment.length-1)]?.bonus).replace(/ · /g,'  ')),150,249,260,28);P(el('i','dt-c-rule'),150,231,260,2);
  const txt=P(el('div','dt-c-text'),0,-347,616,239);txt.style.borderImageSource=`url('${A('dates_bg11')}')`;txt.append(el('p','','From this day forward,\nyou shall not walk alone.\nMy heart will be your shelter,\nand my arms will be your home.'));
  if(h.is_vowed){const d=new Date((h.wedding_date||Date.now()/1000)*1000);P(el('b','dt-c-date',d.getFullYear()+'-'+(d.getMonth()+1)+'-'+d.getDate()),95,-440,200,28);P(img(A('dates_icon42'),'dt-c-seal'),280,-438,130,124).onclick=()=>{const l=allLines(h).find(x=>x.type===16);play(l?.sound,l?.text);ov.remove();render();};}
  else{const b=P(el('button','dt-c-vow'),242,-352,132,132);b.type='button';b.append(img(A('dates_icon41')),el('span','','Oath'));
   const need=el('b','dt-c-need',(h.love_point||0)>=BASE()?'Oath Ring ×'+number(state.items['45']||0):'Intimacy '+Math.floor((h.love_point||0)/100)+'/'+Math.floor(BASE()/100));P(need,150,-440,260,28);
   b.onclick=async()=>{if((h.love_point||0)<BASE()){GirlUI.toast('Intimacy '+Math.floor((h.love_point||0)/100)+' / '+Math.floor(BASE()/100));return;}if(!Number(state.items['45']||0)){GirlUI.toast('No Oath Rings');return;}
    const r=await act({action:'vow',partner_id:h.partner_id});if(r){const nh=hero();const l=allLines(nh).find(x=>x.type===16);play(l?.sound,l?.text||'♥');note='Oath formed!';oath(nh);if(r.got)CampaignUI.popup('Wedding skin unlocked',r.got);}};}
  root().append(ov);}
 return {open,render};
})();
