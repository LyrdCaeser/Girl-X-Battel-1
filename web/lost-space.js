'use strict';
// Lost Space Zone (activity 292; capture 2026-09-29-fb/62). The Events hub shows the entrance (banner, logo, Begin); the zone
// itself is a full view laid out from activity_lost_space_map_window.prefab on the 720x1280 canvas (x/y centred, y up): zone
// chests scroller (upCon), the 6x11 board (UIGrid 100x85 at -47,-33: hidden / explorable / explored / reward / event blocks),
// and the bottom bar (Supply Coordinates, Copier, laser + energy, Auto Explore, Claim All). Rules: gxb2/lost_space.py. Prefix ls-.
const LostSpace=(()=>{
 let data=null,origin='events',busy=false,flash=[];
 const A=n=>'/assets/lost-space/'+n+(n.startsWith('activity_lost_space_bg_banner')||n.startsWith('activity_lost_space_bg_di')?'.webp':'.png');
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 const T=k=>data?.text?.[k]||'';
 function at(e,x,y,w,h){e.style.left=`calc(${360+x-w/2} * var(--u))`;e.style.top=`calc(${640-y-h/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;e.style.height=`calc(${h} * var(--u))`;return e;}
 function iconSrc(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';if(['349','350','355','356'].includes(id))return A('icon_'+id);const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}return it&&itemIcons.has(it.icon)?'/assets/item-icons/'+it.icon+'.png':'';}
 function chip(text,cls='ls-chip'){const [k,n]=String(text).split('#');const w=el('span',cls);const s=iconSrc(k);if(s)w.append(img(s));w.append(el('b','',number(Number(n))));w.title=itemCatalog?.[k]?.name||k;return w;}
 async function load(){if(!data)data=await api('/assets/lost-space.json');return data;}
 async function act(req,quiet){if(busy)return null;busy=true;try{const r=await api('/api/lost-space/action',req);state=r.state;return r;}catch(e){if(!quiet)GirlUI.toast(e.message);return null;}finally{busy=false;if(view==='lost-space')draw();}}
 // --- Events hub entrance -------------------------------------------------------------------------------------------
 async function panel(parent){await load();parent.replaceChildren();const s=state.lost_space_info;const w=el('div','ls-entry');w.style.backgroundImage=`url('${A('activity_lost_space_bg_banner')}')`;
  w.append(img(A('activity_lost_space_logo_en_en'),'ls-entry-logo'));const info=el('div','ls-entry-info');info.append(el('b','',T('ACTIVITY_LOST_SPACE_AWARD_NUM').replace('{1}',s.stage)),chip('349#'+s.radars));
  w.append(info,el('p','ls-entry-text',T('ACTIVITY_LOST_SPACE_HELP_TEXT').split('|')[0]),btn('gs-btn ls-begin',T('ACTIVITY_LOST_SPACE_SKILL_START')||'Bắt Đầu',()=>open('events')));parent.append(w);}
 // --- Map view --------------------------------------------------------------------------------------------------------
 function root(){let r=$('lost-space-view');if(!r){r=el('section','lost-space-view');r.id='lost-space-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function open(from){origin=from||view;await load();root();showView('lost-space');draw();}
 function cellState(s,i){const m=s.map[i],c=s.content[i];if(m===3)return 'empty';if(m===1)return c.startsWith('e#')?'event':'award';return s.explorable[i]?'common':'grey';}
 function draw(){const r=root();if(view!=='lost-space'||!data)return;const s=state.lost_space_info;r.replaceChildren();const st=el('div','ls-stage');r.append(st);
  st.append(at(img(A('activity_lost_space_bg_banner'),'ls-abs ls-bg'),0,0,1024,1280),at(img(A('activity_lost_space_bg_di'),'ls-abs ls-bg'),0,-557,1024,512));
  // top bar
  const top=el('div','ls-top');const rad=el('span','ls-res');rad.append(img(A('icon_349')),el('b','',number(s.radars)),btn('ls-plus','+',()=>buy(s)));const gem=el('span','ls-res');gem.append(img('/assets/currency/icon_2_small.png'),el('b','',number(state.items?.['2']||0)));
  const back=btn('ls-back','',()=>showView(origin));back.append(img('/assets/ui/win_back_btn.png'));top.append(rad,gem,back);st.append(top);
  // zone chests (upCon)
  st.append(at(img(A('activity_lost_space_bg_jlyl'),'ls-abs'),22,515,520,112));
  const zone=at(el('div','ls-abs ls-zone'),-293,512,110,90);zone.append(el('small','',s.stash?'Kho Tiếp Tế':T('ACTIVITY_LOST_SPACE_TEXT01')||'Khu Vực'),el('b','',s.stash?'★':String(s.stage)));st.append(zone);
  const chests=at(el('div','ls-abs ls-chests'),22,508,480,100);for(let z=s.stage;z<s.stage+4&&data.awards[z];z++){const c=el('div','ls-chest'+(z===s.stage?' now':''));c.append(chip(data.awards[z].award),el('small','',T('ACTIVITY_LOST_SPACE_AWARD_NUM').replace('{1}',z)));if(data.awards[z].if_treasure)c.append(img(A('activity_lost_space_icon_bjzb'),'ls-flag'));chests.append(c);}st.append(chests);
  const help=at(btn('ls-abs ls-round','',()=>CampaignUI.popup(T('ACTIVITY_LOST_SPACE_HELP_TEXT').split('|').join('\n'),{})),314,531,62,66);help.append(img(A('btn_tips')));st.append(help);
  const prev=at(btn('ls-abs ls-round','',()=>preview(s)),314,466,62,66);prev.append(img(A('btn_award')));st.append(prev);
  // board
  s.map.forEach((m,i)=>{const row=Math.floor(i/6),col=i%6,kind=cellState(s,i);const c=at(el('button','ls-abs ls-cell '+kind),-47+(col-2.5)*100,-33+(5-row)*85,100,85);c.type='button';
   const bg=img(A(kind==='award'||(kind==='event'&&!/^e#[567]$/.test(s.content[i]))?'activity_lost_space_gz_hd':/^e#[567]$/.test(s.content[i])&&kind==='event'?'activity_lost_space_gz_dian':'activity_lost_space_gz_pt'),'ls-bgc');c.append(bg);
   if(kind==='grey'||kind==='common')c.append(img(A(kind==='grey'?'activity_lost_space_gz_yc':'activity_lost_space_gz_ktc'),'ls-up'));
   if(m===4)c.append(img(A('activity_lost_space_icon_xj'),'ls-tip'));
   if(kind==='award'){const box=Number(s.content[i]);const [k,n]=data.boxes[box%10000].award.split('#');const ic=iconSrc(k);if(ic)c.append(img(ic,'ls-icon'));c.append(el('b','ls-num',number(Number(n)*(box>10000?2:1))));if(box>10000)c.append(el('i','ls-x2','×2'));}
   if(kind==='event'){const e=Number(s.content[i].slice(2));const ev={1:'activity_lost_space_gz_double',2:'activity_lost_space_icon_xj',3:'activity_lost_space_icon_nl',4:'activity_lost_space_icon_nl',5:'activity_lost_space_gz_xyg',6:'activity_lost_space_gz_bjd',7:'activity_lost_space_gz_bjzb'}[e];c.append(img(A(ev),e>=5?'ls-up raised':'ls-icon'));if(e===3||e===4)c.append(el('b','ls-num','+'+data.events[e].energy_num));c.title=data.event_text[{1:5,2:4,3:6,4:6,5:1,6:2,7:3}[e]]?.name||'';}
   if(i===s.last&&!s.stash)c.append(el('span','ls-last'));if(flash.includes(i))c.classList.add('flash');
   c.onclick=()=>tap(s,i,kind);st.append(c);});flash=[];
  // bottom bar (downCon)
  const part=at(btn('ls-abs ls-bb','',()=>GirlUI.toast(data.event_text[3].desc)),-269,-566,92,84);part.append(img(A('activity_lost_space_btn_bjzb')),el('b','',s.piece+'/3'));if(!s.treasure_zone&&!s.piece)part.classList.add('dim');st.append(part);
  const dbl=at(btn('ls-abs ls-bb','',()=>GirlUI.toast(data.event_text[5].desc)),-173,-566,92,84);dbl.append(img(A('activity_lost_space_btn_double')),el('b','',String(s.double)));st.append(dbl);
  const sk=at(btn('ls-abs ls-bb ls-skill'+(s.skill&&s.energy>=s.cap?' full':''),'',()=>s.skill?laser(s):skills(s)),-66,-571,80,80);sk.append(img(A('activity_lost_space_btn_skill')));if(s.skill)sk.append(img(A(data.skill_text[s.skill].icon),'ls-sk-icon'));sk.append(el('b','',s.skill?s.energy+'/'+s.cap:'—'));st.append(sk);
  const ch=at(btn('ls-abs ls-change','',()=>skills(s)),-102,-544,38,40);ch.append(img(A('activity_lost_space_btn_qh')));st.append(ch);
  const auto=at(btn('ls-abs ls-bb','',()=>autoExplore(s)),44,-566,84,84);auto.append(img(A('activity_lost_space_btn_zzts')),el('b','',T('ACTIVITY_LOST_SPACE_TEXT11')||'Auto Explore'));st.append(auto);
  const all=at(btn('ls-abs ls-claim',T('ACTIVITY_LOST_SPACE_AUTO_GET')||'Claim All',async()=>{const r=await act({action:'claim'});if(r)toastGot(r.got);}),232,-572,228,96);st.append(all);
  st.append(at(img(A('activity_lost_space_xian'),'ls-abs'),0,-635,756,38));
  if(s.stash){const tag=at(el('div','ls-abs ls-stashtag',data.event_text[2].name),-47,475,300,40);st.append(tag);}}
 function toastGot(got){const e=Object.entries(got||{});if(e.length)GirlUI.toast(e.slice(0,4).map(([k,n])=>'+'+number(n)+' '+(itemCatalog?.[k]?.name||k)).join(' · ')+(e.length>4?' …':''));}
 async function tap(s,i,kind){
  if(kind==='grey'){GirlUI.toast(T('ACTIVITY_LOST_SPACE_SKILL_NO_CLICK'));return;}
  if(kind==='common'){if(s.skill&&s.energy>=s.cap&&!confirm(T('ACTIVITY_LOST_SPACE_SKILL_ENERGY_TIPS')))return;const r=await act({action:'open',id:i});if(r){flash=[i];draw();}return;}
  if(kind==='award'){const r=await act({action:'claim',ids:[i]});if(r)toastGot(r.got);return;}
  if(kind==='event'){const e=Number(s.content[i].slice(2));if(e===5&&!s.stash&&!confirm(T('ACTIVITY_LOST_SPACE_EXIT_TIPS1')))return;
   const r=await act({action:'event',id:i});if(!r)return;if(r.got){toastGot(r.got);GirlUI.toast(T('ACTIVITY_LOST_SPACE_AWARD_NUM').replace('{1}',r.stage));}
   if(r.stash_found)GirlUI.toast(T('ACTIVITY_LOST_SPACE_SKILL_MASK_TREASURE_SHOW'));if(r.event===2)GirlUI.toast(T('ACTIVITY_LOST_SPACE_SKILL_MASK_EXIT_SHOW').replace('Portal','Reward'));if(r.pos!==undefined){flash=[r.pos];draw();}}}
 async function laser(s){if(s.energy<s.cap){skills(s);return;}const r=await act({action:'laser'});if(r){flash=r.found.map(x=>x[0]);draw();GirlUI.toast(data.skill_text[s.skill].name+' ×'+r.found.length);}}
 async function autoExplore(s){if(s.radars<5){GirlUI.toast(T('ACTIVITY_LOST_SPACE_TEXT12'));return;}if(!await GirlUI.confirm('Dùng ra-đa để tự động thám hiểm khu vực này?',{title:'Tự Động Thám Hiểm',ok:'Thám Hiểm'}))return;
  const r=await act({action:'auto'});if(!r)return;const {body}=GirlUI.win({title:T('ACTIVITY_LOST_SPACE_TEXT13')||'Kết Quả',cls:'ls-win'});
  const u=el('p','ls-line');u.append(el('span','',(T('ACTIVITY_LOST_SPACE_TEXT14')||'Ra-đa Đã Dùng')+': '),chip('349#'+r.used));body.append(u,el('p','ls-line',T('ACTIVITY_LOST_SPACE_TEXT15')||'Phần Thưởng Nhận Được'));
  const g=el('div','ls-gotgrid');for(const [k,n]of Object.entries(r.got))g.append(chip(k+'#'+n));body.append(g);if(r.portal)body.append(el('p','ls-line',T('ACTIVITY_LOST_SPACE_SKILL_MASK_EXIT_SHOW')));}
 function skills(s){const {body,close}=GirlUI.win({title:T('ACTIVITY_LOST_SPACE_SKILL_CHOOSE')||'Chọn',cls:'ls-win'});
  for(const id of Object.keys(data.skills)){const t=data.skill_text[id];const row=el('div','ls-skrow'+(Number(id)===s.skill?' on':''));row.append(img(A(t.icon),'ls-skbig'));const info=el('div','');info.append(el('b','',t.name),el('small','',(T('ACTIVITY_LOST_SPACE_SKILL_ENERGY_COST')||'Tốn {1} Năng Lượng').replace('{1}',s.costs[id])),el('p','',t.desc.replace('{1}',String(s.lvs[id]||0))));row.append(info);
   row.append(btn('gs-btn'+(Number(id)===s.skill?' white':''),Number(id)===s.skill?'✔':(T('ACTIVITY_LOST_SPACE_SKILL_CHOOSE')||'Chọn'),async()=>{if(s.skill&&s.energy>0&&!await GirlUI.confirm('Đổi kỹ năng hiện tại? Năng lượng còn lại có thể bị ảnh hưởng.',{title:'Đổi Kỹ Năng',ok:'Đổi'}))return;close();await act({action:'skill',id:Number(id)});},Number(id)===s.skill));body.append(row);}}
 function preview(s){const {body}=GirlUI.win({title:T('ACTIVITY_LOST_SPACE_AWARD_TITLE')||'Xem Trước',cls:'ls-win'});const g=el('div','ls-pgrid');
  for(const z of Object.keys(data.awards).map(Number).sort((a,b)=>a-b)){const c=el('div','ls-pz'+(z<s.stage?' done':z===s.stage?' now':''));c.append(el('small','',T('ACTIVITY_LOST_SPACE_AWARD_NUM').replace('{1}',z)),chip(data.awards[z].award));if(data.awards[z].if_treasure)c.append(img(A('activity_lost_space_icon_bjzb'),'ls-flag'));g.append(c);}body.append(g);
  setTimeout(()=>g.querySelector('.now')?.scrollIntoView({block:'center'}),50);}
 async function buy(s){const left=s.buy_limit-s.buy;if(left<=0){GirlUI.toast('Đã đạt giới hạn mua hằng ngày');return;}const n=await GirlUI.promptNumber('Mua Ra-đa Không Gian (100 Kim Cương/chiếc; còn '+left+' lượt)',{title:'Mua Ra-đa',value:Math.min(5,left),min:1,max:left});if(n)act({action:'buy',num:n});}
 return {panel,open,render:draw};
})();
