'use strict';
// Wallpaper Girls list (capture 2026-09-29-fb/34): pick up to 6 owned girls or skins for the Front Page, faction filter,
// "Current Wallpaper Girl" slots and "Random Switch when entering Frontpage". Saved in profile.wallpapers /
// wallpaper_random (Engine.update_profile). The Front Page shows them in turn (or at random). Prefix wp-.
const Wallpaper=(()=>{
 let group=0,pick=null,rnd=0;
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';return i;};
 const nameOf=id=>(skinCat?skinCat[String(id)]:id>=7000&&id<8000)?'Skin':(girlsCatalog.find(g=>g.id===id)?.name||"Girl "+id);
 let skinCat=null;
 // Card first (re-issues use their host's card), then the full art / lihui picture, then the avatar.
 const isSkin=id=>skinCat?!!skinCat[String(id)]:(id>=7000&&id<8000);
 const art=id=>{if(isSkin(id))return '/assets/skins/cards/'+id+'.webp';if(cardIds.has(id))return '/assets/cards/partner_card_'+id+'.png';const base=typeof artId==='function'?artId(id):id;if(cardIds.has(base))return '/assets/cards/partner_card_'+base+'.png';
  const d=typeof detailImage==='function'&&(detailImage(base)||detailImage(id));if(d)return d;const av=avatars?.[String(id)]||avatars?.[String(base)];return av?.src||'';};
 function options(){const seen=new Set(),out=[];for(const h of state.roster){if(seen.has(h.table_id))continue;seen.add(h.table_id);out.push({id:h.table_id,group:h.group,label:h.name,sub:'Original'});}
  // skins you own (in the bag, collected or worn), under the girl who can wear them
  const si=state.skins_info||{};const have=new Set([...Object.keys(si.owned||{}).map(Number),...(si.collected||[]).map(Number),...state.roster.map(h=>Number(h.equips?.[6]||0)).filter(Boolean)]);
  for(const sid of [...have].sort((a,b)=>a-b)){const row=skinCat?.[String(sid)];const girl=row&&state.roster.find(h=>row.partners.includes(h.table_id));if(!girl&&skinCat)continue;out.push({id:sid,group:girl?.group||0,label:girl?.name||'Skin',sub:row?.name||'Skin'});}return out;}
 async function open(){if(!skinCat){try{skinCat=(await api('/api/skins/catalog',{})).skins;}catch{skinCat={};}}const p=state.profile||{};pick=[...(p.wallpapers||[])];rnd=p.wallpaper_random?1:0;paint();}
 // Front Page scene (local addition): the client's 25 animated login scenes (Animation (Misc)/background/login_*) as the
 // background behind the girl. Stored per browser ('gxb2-scene'); converted on demand by the server (/assets/spine/<name>).
 const SCENES=['login_summer','login_summer2022','login_summer_2nd','login_sunshine','login_fish','login_hot_spring','login_sleepdream','login_music','login_magicgirl','login_valkyrie','login_angel','login_mafia','login_liquor','login_chilian','login_halloween2021','login_xmas','login_maxs2021','login_maxs2022','login_2022newyear','login_anniversary','login_2nd_birthday_cake','login_4th_birthday','login_fool_loading'];
 let sceneView=null,sceneKey='';
 const sceneName=()=>{try{return localStorage.getItem('gxb2-scene')||'';}catch{return '';}};
 async function mountScene(){const stage=document.querySelector('#home-view .home-stage');const name=sceneName();if(!stage)return;if(sceneKey===name&&(!name||stage.querySelector('.wp-scene')))return;
  sceneKey=name;sceneView?.destroy?.();sceneView=null;stage.querySelector('.wp-scene')?.remove();if(!name)return;const host=el('div','wp-scene');stage.prepend(host);
  try{const h=await GxbSpine.mount(host,'/assets/spine/'+name,{width:720,height:1280,scale:1,origin:[.5,.5],className:'wp-scene-canvas'});if(sceneKey!==name||!host.isConnected){h.destroy();return;}sceneView=h;}catch{host.remove();sceneKey='';}}
 function sceneRow(body){const row=el('div','wp-scenes');const cur=sceneName();const add=(name,label)=>{const b=el('button','wp-scene-btn'+(cur===name?' on':''),label);b.type='button';b.onclick=()=>{try{localStorage.setItem('gxb2-scene',name);}catch{}mountScene();paint();};row.append(b);};
  add('','Default');for(const n of SCENES)add(n,n.replace('login_','').replace(/_/g,' '));body.append(el('b','wp-scenes-h','Front Page scene'),row);}
 function paint(){document.querySelector('.gs-overlay')?.remove();const {body,close}=GirlUI.win({title:'Wallpaper Girls list',cls:'wp-win'});sceneRow(body);
  const grid=el('div','wp-grid');for(const o of options().filter(o=>!group||o.group===group)){const on=pick.includes(o.id);const c=el('button','wp-card'+(on?' on':''));c.type='button';const a=art(o.id);if(a){const im=img(a);im.onerror=()=>{const alt=isSkin(o.id)&&typeof detailImage==='function'?detailImage(o.id):'';if(alt&&!im.dataset.alt){im.dataset.alt=1;im.src=alt;}else im.replaceWith(el('span','wp-noart'));};c.append(im);}else c.append(el('span','wp-noart'));c.append(el('b','',o.label),el('small','',o.sub));if(on)c.append(el('i','wp-check','✔'));
   c.onclick=()=>{if(on)pick=pick.filter(x=>x!==o.id);else if(pick.length<6)pick.push(o.id);else{GirlUI.toast("Up to 6");return;}paint();};grid.append(c);}body.append(grid);
  const f=el('div','wp-filters');[0,1,2,3,4,5,6,7].forEach(g=>{const b=el('button','wp-f'+(group===g?' on':''));b.type='button';if(g)b.append(img('/assets/factions/'+g+'.png'));else b.textContent='All';b.onclick=()=>{group=g;paint();};f.append(b);});body.append(f);
  body.append(el('h4','wp-title','◆ Current Wallpaper Girl'));const cur=el('div','wp-cur');for(let i=0;i<6;i++){const id=pick[i];const s=el('span','wp-slot');if(id){const a=art(id);if(a)s.append(img(a));}cur.append(s);}body.append(cur);
  const r=el('label','wp-random');const cb=el('input');cb.type='checkbox';cb.checked=!!rnd;cb.onchange=()=>{rnd=cb.checked?1:0;};r.append(cb,el('span','','Random Switch when entering Frontpage'));
  const ok=el('button','gs-btn','OK');ok.type='button';ok.onclick=async()=>{try{const res=await api('/api/profile',{wallpapers:pick,wallpaper_random:rnd});state=res.state||res;close();render();GirlUI.toast("Wallpaper saved");}catch(e){GirlUI.toast(e.message);}};
  const foot=el('div','wp-foot');foot.append(r,ok);body.append(foot);}
 // Front Page picture: the chosen girls in turn (or at random); falls back to the three default heroes
 function heroSrc(index){const p=state.profile||{};const list=p.wallpapers||[];if(!list.length)return null;const id=p.wallpaper_random?list[Math.floor(Math.random()*list.length)]:list[index%list.length];
  const base=typeof artId==='function'?artId(id):id;const pic=typeof GirlUI!=='undefined'&&(GirlUI.picture(id)||GirlUI.picture(base));return pic||(typeof detailImage==='function'?detailImage(id)||detailImage(base):'')||null;}
 // MainMap:updateImg — the Front Page girl is a partnerImg at the screen centre, SetLocalPosition(xy2.x, -xy2.y) and
 // SetLocalScale(scale) (partner_picture_xy2); static pictures at their native size, Spine models 200 lower
 // (GirlsModelLite). Returns true when the wallpaper layer is shown (the default hero stays hidden then).
 let meta=null,homeKey='',homeView=null;
 async function homeMeta(){if(!meta){try{const [p,l,q]=await Promise.all([api('/assets/partner-pictures.json'),api('/assets/lihui.json'),api('/assets/pictures.json')]);meta={pics:p,lihui:new Set(l),files:new Set(q.map(Number))};}catch{meta={pics:{},lihui:new Set(),files:new Set()};}}return meta;}
 function staticOf(m,id){const chain=typeof hostChain==='function'?hostChain(id):[Number(id)];const f=chain.find(x=>m.files.has(x));return f?'/assets/pictures/'+f+'.webp':'';}
 function pickId(index){const p=state.profile||{};const list=p.wallpapers||[];if(!list.length)return null;return p.wallpaper_random?list[Math.floor(Math.random()*list.length)]:list[index%list.length];}
 function clearHome(){homeKey='';homeView?.destroy?.();homeView=null;document.querySelector('#home-view .wp-home')?.remove();}
 // PartnerImg at the screen centre, SetLocalPosition(x, -y), SetLocalScale(scale): a 720×1280 layer inside `host` with the
 // picture at its native size, or the Spine model 200 lower (GirlsModelLite). coord 'xy' = partner_picture_xy (detail,
 // dates), 'xy2' = partner_picture_xy2 (MainMap). Returns {layer, destroy} or null when the girl has no art.
 async function mountArt(host,id,coord='xy'){const m=await homeMeta();const chain=typeof hostChain==='function'?hostChain(id):[Number(id)];
  const showId=chain.find(x=>m.pics[String(x)])??Number(id);const pic=m.pics[String(showId)];const staticSrc=staticOf(m,id);
  const spine=pic?.spine&&m.lihui.has(pic.spine)?pic.spine:'';const own=staticSrc&&staticSrc.includes('/'+showId+'.webp');
  if(!pic||(!spine&&!staticSrc))return null;
  const layer=el('div','wp-home');host.append(layer);let view=null;
  if(spine&&!own){const [x,y]=pic[coord]||pic.xy;const sh=el('div','wp-home-spine');layer.append(sh);try{view=await GxbSpine.mount(sh,'/assets/lihui/'+spine,{width:720,height:1280,scale:pic.scale,origin:[(360+x)/720,(640+y+200*pic.scale)/1280],className:'wp-home-canvas'});}catch{layer.remove();return null;}}
  else{let usePic=pic;if(!own){const m2=/\/assets\/pictures\/(\d+)\.webp/.exec(staticSrc);if(m2&&m.pics[m2[1]])usePic=m.pics[m2[1]];}const [ux,uy]=usePic[coord]||usePic.xy;const im=img(staticSrc,'wp-home-pic');const put=()=>{im.style.setProperty('--pw',im.naturalWidth*usePic.scale);im.style.setProperty('--px',ux);im.style.setProperty('--py',uy);};if(im.complete&&im.naturalWidth)put();else im.onload=put;layer.append(im);}
  return {layer,destroy(){view?.destroy?.();layer.remove();}};}
 async function mountHome(index){mountScene();const id=pickId(index);const stage=document.querySelector('#home-view .home-stage');if(!id||!stage){clearHome();return false;}
  const key=String(id);if(homeKey===key&&document.querySelector('#home-view .wp-home'))return true;clearHome();homeKey=key;
  const tmp=el('div');const h=await mountArt(tmp,id,'xy2');if(!h||homeKey!==key){h?.destroy();if(homeKey===key)homeKey='';return !!h&&false;}
  stage.querySelector('.home-background')?.after(h.layer);homeView=h;return true;}
 document.addEventListener('DOMContentLoaded',()=>{const page=$('profile-info-page');if(page&&!$('wp-open')){const b=el('button','secondary wp-open','Wallpaper Girls');b.id='wp-open';b.type='button';b.onclick=open;page.append(b);}});
 return {open,heroSrc,mountHome,clearHome,mountArt};
})();
