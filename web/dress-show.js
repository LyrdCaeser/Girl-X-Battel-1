'use strict';
// Outfit Showcase (capture 2026-09-29-fb/40). Layout from the prefabs, on the 720x1280 canvas (x/y centred, y up):
// dress_show_entrance_window (logo, SHOP, total score, the four framed Booths with rating medal and ribbon) and
// dress_show_main_window (Booth info rows ID / Slot / Rating / Daily Reward, ◀ ▶ between Booths, three shelves
// Courage / Charisma / Knowledge Booth with five Slots each). Rules: gxb2/dress_show.py. Prefix ds-.
const DressShow=(()=>{
 let origin='campus',data=null,cat=null,booth=0;
 const A=n=>'/assets/dress-show/'+n+(n.endsWith('_bg')&&/entrance|main/.test(n)?'.webp':'.png');
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 const T=(k,...a)=>{let s=data.text['SHOW_WINDOW_TEXT'+k]||'';a.forEach((v,i)=>{s=s.replace('{'+(i+1)+'}',v);});return s;};
 // Prefab coordinates → CSS on the 720x1280 stage.
 function at(e,x,y,w,h){e.style.left=`calc(${360+x-(w||0)/2} * var(--u))`;e.style.top=`calc(${640-y-(h||0)/2} * var(--u))`;if(w)e.style.width=`calc(${w} * var(--u))`;if(h)e.style.height=`calc(${h} * var(--u))`;return e;}
 function root(){let r=$('dress-show-view');if(!r){r=el('section','dress-show-view');r.id='dress-show-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function open(from){origin=from||view;if(!data)data=await api('/assets/dress-show.json');if(!cat)cat=await api('/api/dress/catalog',{});booth=0;root();showView('dress-show');render();if(state.dress_show_info?.pending_days){try{const r=await api('/api/dress-show/action',{action:'claim'});state=r.state;render();CampaignUI.popup('Daily Reward'+(r.days>1?' ×'+r.days:''),r.got||{});}catch{}}const g=$('game-root');if(g)g.scrollTop=0;}
 async function act(req,msg){try{const r=await api('/api/dress-show/action',req);state=r.state;if(msg)GirlUI.toast(msg);return r;}catch(e){GirlUI.toast(e.message);return null;}finally{if(view==='dress-show')render();}}
 const owned=did=>(state.dress_info?.owned||[]).find(p=>p.dress===did);
 const itemOf=(did,star)=>cat.items[cat.pieces[did]?.items?.[(star||owned(did)?.star||1)-1]];
 function chips(obj){const w=el('span','ds-chips');for(const [k,v]of Object.entries(obj||{})){const c=el('span','ds-chip');c.append(img(A('icon_'+k)),el('b','',number(v)));w.append(c);}return w;}
 function render(){const r=root();if(view!=='dress-show'||!data)return;r.replaceChildren();const stage=el('div','ds-stage');r.append(stage);
  const top=el('div','ds-top');for(const id of ['1','2']){const c=el('span','ds-res');c.append(img('/assets/currency/icon_'+id+'_small.png'),el('b','',number(state.items[id]||0)));top.append(c);}
  const back=btn('ds-back','',()=>{if(booth){booth=0;render();}else showView(origin==='dress-show'?'campus':origin);});back.append(img('/assets/ui/win_back_btn.png'));top.append(back);
  if(booth)detail(stage);else entrance(stage);stage.append(top);
  const nav=document.querySelector('.menu-explorer-bottom');if(nav){const n=nav.cloneNode(true);n.classList.add('ds-nav');n.querySelectorAll('button').forEach(b=>b.classList.remove('current'));stage.append(n);}}
 function entrance(st){const s=state.dress_show_info;const bg=at(img(A('dress_show_entrance_bg'),'ds-bg'),0,0,1000,1559);st.append(bg);
  // the header is anchored under the WindowTop strip (captures Reference/5. Outfit Showcase): 56 units lower than the prefab centre
  const H=-56;
  st.append(at(img(A('dress_show_logo_bg'),'ds-abs'),-2,499+H,1000,278),at(img(A('dress_show_logo_en_en'),'ds-abs ds-logo'),4,559+H,476,174),at(el('p','ds-abs ds-desc',T('01')),4,415+H,481,75));
  st.append(at(btn('ds-abs ds-help','',()=>CampaignUI.popup([T('01'),T('22'),"Local: tap Claim to receive daily Tags (accumulate up to 7 days)."].join('\n'),{})),313,519+H,52,52));
  const shop=at(btn('ds-abs ds-shop','',()=>store()),-288,393+H,80,82);shop.append(img(A('shop')));st.append(shop);
  const score=at(el('div','ds-abs ds-total'),-255,323+H+20,173,41);score.append(img(A('dress_show_score_icon')),el('b','',number(s.total)));st.append(score);
  const L={1:[-176,79,1],4:[176,-204,1],3:[-176,-282,2],2:[174,169,2]};
  for(const b of s.booths){const [x,y,k]=L[b.id];const tall=k===1;const c=at(btn('ds-abs ds-case'+(tall?'':' short'),'',()=>{booth=b.id;render();}),x,y,tall?351:348,tall?408:340);
   c.append(img(A(tall?'dress_show_case_bg':'dress_show_case_bg2'),'ds-frame'),img(A('dress_show_case_img_'+b.id),'ds-cimg'));st.append(c);
   st.append(at(img(A('dress_show_level_'+b.rating),'ds-abs ds-medal'),x+(tall?2:-4),y+(tall?-147:-102),54,48));
   const t=at(el('div','ds-abs ds-ribbon'),x,y+(tall?-196:-155),244,50);t.append(img(A('dress_show_text_en_en')),el('b','',String(b.id)));st.append(t);}}
 function detail(st){const s=state.dress_show_info;const b=s.booths.find(x=>x.id===booth);st.append(at(img(A('dress_show_main_bg'),'ds-bg'),0,-100,1000,1559));
  st.append(at(img(A('dress_show_level_'+b.rating),'ds-abs'),0,532,54,50),at(el('b','ds-abs ds-title',T('05')),3,491,300,30),at(btn('ds-abs ds-help','',()=>CampaignUI.popup(data.rank.map((p,i)=>'Rating '+(i+1)+': '+p+'+').join('\n'),{})),283,499,52,52));
  const nav=(d,x)=>{const a=at(btn('ds-abs ds-arrow'+(d<0?' left':''),'',()=>{booth=(booth+d+3)%4+1;render();}),x,379,45,92);a.append(img(A('partner_detail_arrow')));return a;};st.append(nav(-1,-331),nav(1,331));
  const by=t=>b.slots.filter(x=>x.type===t);const open=t=>by(t).filter(x=>x.unlocked).length,sc=t=>by(t).reduce((a,x)=>a+x.score,0);
  const rows=[[458,T('06'),T('02',b.id)],[416,T('07'),`${open(1)+open(2)+open(3)} [c][1ebc1b](${open(1)}+${open(2)}+${open(3)})[-][/c]`],[376,T('08'),`${b.score} [c][1ebc1b](${sc(1)}+${sc(2)}+${sc(3)})[-][/c]`],[311,T('09'),null]];
  for(const [y,name,val]of rows){const lb=at(el('div','ds-abs ds-lname',name),-189,y,145,26);st.append(lb);if(val!==null){st.append(at(el('i','ds-abs ds-dot'),56,y-12,433,2));const v=GirlUI.rich('span','ds-abs ds-lval',val);at(v,164,y,200,24);st.append(v);}else{const c=chips(b.daily);c.classList.add('ds-abs');if(!Object.keys(b.daily).length)c.append(el('small','','—'));st.append(at(c,150,y,300,50));}}
  st.append(at(img(A('dress_show_score_icon'),'ds-abs'),223-120,376,32,35));
  [1,2,3].forEach((type,g)=>{const gy=-3-g*240;st.append(at(img(A('dress_show_group_bg'),'ds-abs'),0,gy-13,706,91));
   const tt=at(el('div','ds-abs ds-gtitle'),0,gy+161,275,46);tt.append(el('b','',T(String(9+type))),el('small','',by(type).filter(x=>x.piece).length+'/5'));st.append(tt);
   by(type).forEach((sl,i)=>{const x=-250+i*125;const c=at(btn('ds-abs ds-slot','',()=>slotClick(sl)),x,gy+60,120,120);c.append(img(A('dress_show_icon_bg'),'ds-sbg'));
    if(sl.piece){const it=itemOf(sl.piece);if(it){c.append(img('/assets/dress/ui/'+it.icon[0]+'.png','ds-sicon'));}const sg=at(el('div','ds-abs ds-sscore'),x,gy-8,112,40);sg.append(img(A('dress_show_score_icon')),el('b','',String(sl.score)));st.append(c,sg);return;}
    if(sl.unlocked)c.append(img(A('altar_add_bg'),'ds-add'));else{c.classList.add('locked');c.append(img(A('lock_icon'),'ds-lock'));}st.append(c);});});}
 function reqText(sl){const types=String(sl.add_type).split('|'),nums=String(sl.add_num).split('|');const parts=types.map((t,i)=>(data.add_text[t+':'+(t==='1'||t==='2'?nums[i]:'')]||'').replace('{1}',nums[i]));return parts.length>1?T('17',...parts):T('16',parts[0]);}
 function slotClick(sl){if(!sl.unlocked)return unlockWin(sl);pick(sl);}
 function unlockWin(sl){const {body,close}=GirlUI.win({title:T('13'),cls:'ds-pick'});const tx=data.unlock_text[String(sl.unlock_type)];const prevOk=b=>b;
  if(sl.unlock_type){const line=(sl.can_unlock?tx[1]:tx[0]).replace(/\{1\}/g,number(sl.now)).replace(/\{2\}/g,number(sl.unlock_num));body.append(el('p',sl.can_unlock?'ds-ok':'ds-no',line));}
  body.append(el('p','ds-req',reqText(sl)));const a=el('div','gs-btns');a.append(btn('gs-btn','Unlock',()=>{close();act({action:'unlock',slot:sl.id},T('14'));},!sl.can_unlock));body.append(a);prevOk(0);}
 function fits(sl,did,it){const types=String(sl.add_type).split('|').map(Number),nums=String(sl.add_num).split('|').map(Number);return types.every((t,i)=>t===1?cat.pieces[did].pos===nums[i]:t===2?it.qlt>=nums[i]:t===3?it.star>=nums[i]:it.base[t-4]>=nums[i]);}
 // DressShowChooseWindow: top (the row's five slots, "Slot X · Slot Score", requirement, Display) and bottom (the pieces that
 // fit, filtered by position, with their score for this row's attribute).
 const POS=[['All',0],['Head',1],['Body',2],['Legs',3],['Headwear',4],['Accessories',5]];
 function pick(sl){let cur=sl.id,cand=null,pf=0;const {body,close,win}=GirlUI.win({title:T(String(9+sl.type)),cls:'ds-pick2'});
  const draw=()=>{const b=state.dress_show_info.booths.find(x=>x.id===booth);const row=b.slots.filter(x=>x.type===sl.type);const s=row.find(x=>x.id===cur)||sl;const type=s.type;body.replaceChildren();
   const top=el('div','ds-ptop');const total=el('div','ds-ptotal');total.append(el('span','','Total Score'),img(A('dress_show_score_icon')),el('b','',String(row.reduce((a,x)=>a+x.score,0))));top.append(total);
   const slots=el('div','ds-pslots');row.forEach((x,i)=>{const c=btn('ds-pslot'+(x.id===cur?' on':'')+(x.unlocked?'':' locked'),'',()=>{if(!x.unlocked){close();slotClick(x);return;}cur=x.id;cand=null;draw();});
     const did=x.id===cur&&cand?cand:x.piece;if(did){const it=itemOf(did);if(it){const f=el('span','ds-piece');f.style.backgroundImage=`url('/assets/dress/ui/lead_skin_border_${Math.min(7,it.qlt)}.png')`;f.append(img('/assets/dress/ui/'+it.icon[0]+'.png'));c.append(f);}}
     else c.append(el('b','ds-pplus',x.unlocked?'+':'🔒'));c.append(el('small','','Slot '+'ABCDE'[i]));slots.append(c);});top.append(slots);
   const i=row.findIndex(x=>x.id===cur);const desc=el('div','ds-pdesc');const h=el('div','ds-pdhead');const shown=cand||s.piece;const sc=shown?(itemOf(shown)?.base?.[type-1]||0):0;
   const ss=el('span','');ss.append(el('span','','Slot Score:'),img(A('dress_show_score_icon')),el('b','',String(sc)));h.append(el('b','','Slot '+'ABCDE'[i]),ss);desc.append(h,el('p','',reqText(s)));top.append(desc);
   const acts=el('div','ds-pacts');if(s.piece)acts.append(btn('gs-btn white','Take off',()=>{close();act({action:'place',slot:s.id,piece:0});}));acts.append(btn('gs-btn','Display',()=>{close();act({action:'place',slot:s.id,piece:cand},T('27',T(String(9+type))));},!cand||cand===s.piece));top.append(acts);body.append(top);
   const bot=el('div','ds-pbot');const fl=el('div','ds-pfilters');POS.forEach(([n,p])=>fl.append(btn('ds-pf'+(pf===p?' on':''),n,()=>{pf=p;draw();})));bot.append(fl);
   const list=(state.dress_info?.owned||[]).map(p=>({did:p.dress,it:itemOf(p.dress,p.star)})).filter(x=>x.it&&fits(s,x.did,x.it)&&(!pf||cat.pieces[x.did]?.pos===pf)).sort((a,b)=>b.it.base[type-1]-a.it.base[type-1]);
   const used=new Set(row.filter(x=>x.id!==cur&&x.piece).map(x=>x.piece));
   const grid=el('div','ds-grid');for(const x of list){const c=btn('ds-opt'+(x.did===(cand||s.piece)?' on':'')+(used.has(x.did)?' used':''),'',()=>{cand=x.did;draw();});const f=el('span','ds-piece');f.style.backgroundImage=`url('/assets/dress/ui/lead_skin_border_${Math.min(7,x.it.qlt)}.png')`;f.append(img('/assets/dress/ui/'+x.it.icon[0]+'.png'));
    const o=el('span','ds-oscore');o.append(img(A('dress_show_score_icon')),el('b','',String(x.it.base[type-1])));c.append(f,o);grid.append(c);}
   if(!list.length)grid.append(el('p','ds-empty',"You have no pieces that meet the requirement."));bot.append(grid);body.append(bot);};
  draw();void win;}
 // DressShowShopWindow: Buff (shop1: skill buffs, stacks of 3 battles) / Rare (shop2) / Common (shop3, by Stage = score gate),
 // weekly refresh countdown and the Rare / Metal Tags.
 let storeTab=0;
 const ICON1={1:'guide_icon_4',2:'guide_icon_4',3:'guide_icon_19',4:'guide_icon_19',5:'guide_icon_28',6:'guide_icon_28',7:'guide_icon_20',8:'guide_icon_20'};
 function store(){const {body,close}=GirlUI.win({title:T('30')||'Showcase Store',cls:'ds-storewin'});const draw=()=>{const s=state.dress_show_info;body.replaceChildren();
   const tabs=el('div','ds-stabs');[T('31'),T('32'),T('33')].forEach((n,i)=>{const b=btn('ds-stab'+(storeTab===i?' on':''),n,()=>{storeTab=i;draw();});tabs.append(b);});body.append(tabs);
   const head=el('div','ds-shead');const week=(data.refresh||604800);const left=week-(Math.floor(Date.now()/1000)%week);const tm=el('span','ds-timer');tm.append(el('i','','⏱'),el('b','',Math.floor(left/86400)+'D '+Math.floor(left%86400/3600)+'H'));head.append(tm);
   for(const id of ['314','315']){const c=el('span','ds-res');c.append(img(A('icon_'+id)),el('b','',number(state.items[id]||0)));head.append(c);}body.append(head);
   const list=el('div','ds-slist');body.append(list);
   const buyNow=async(req,msg)=>{try{const r=await api('/api/dress-show/action',req);state=r.state;GirlUI.toast(msg);}catch(e){GirlUI.toast(e.message);}draw();};
   const price=(cost,fn,off)=>{const [ck,cv]=String(cost).split('#');const bb=btn('gs-btn ds-buy','',fn,off);bb.append(img(A('icon_'+ck)),el('b','',number(Number(cv))));return bb;};
   if(storeTab===0){for(const [id,row]of Object.entries(data.shop1||{})){const tx=data.shop1_text?.[id]||[];const b=s.buffs?.[id]||{times:[],bought:0};const coop=String(row.func_id).split('|').includes('32');
     const r=el('div','ds-brow');const ic=el('div','ds-bicon');ic.append(img(A(ICON1[id]||'guide_icon_4')),el('small','',T('34',row.buy_time-b.bought)));
     const mid=el('div','ds-bmid');const name=el('b','',tx[0]||'Buff '+id);const info=btn('ds-binfo','!',()=>CampaignUI.popup((tx[0]||'')+'\n'+(tx[2]||'')+(b.times.length?'\n\n'+T('37',b.times.length,Math.min(...b.times)):''),{}));
     mid.append(name,info,el('p','',tx[1]||''));const st=el('span','ds-bstate'+(b.times.length?' on':''),b.times.length?T('36',b.times.length):T('35'));mid.append(st);
     const buy=price(row.cost,()=>buyNow({action:'buy_buff',id:Number(id)},tx[0]),coop||b.bought>=row.buy_time||b.times.length>=row.max_time);if(coop)buy.title="Security Squad requires online friends";
     r.append(ic,mid,buy);list.append(r);}}
   else{const shop=storeTab===1?'2':'3',rows=Object.values(storeTab===1?data.shop2:data.shop3);const gates=[...new Set(rows.map(r=>Number(r.point||0)))].sort((a,b)=>a-b);const names=(T('45')||'').split('|');
    if(storeTab===1&&s.history<Math.max(...gates))list.append(el('div','ds-sgate',T('40',number(Math.max(...gates)))));
    gates.forEach((g,gi)=>{if(storeTab===2||gates.length>1)list.append(el('div','ds-sstage',(names[gi]||T('39',gi+1))+(s.history<g?' · '+T('40',number(g)):'')));const grid=el('div','ds-store');
     for(const row of rows.filter(r=>Number(r.point||0)===g)){const key=shop+':'+row.id,bought=Number(s.shop[key]||0),locked=g>s.history,sold=bought>=Number(row.buy_time);const c=el('div','ds-sitem'+(locked?' locked':'')+(sold?' sold':''));
      const [iid,n]=String(row.item).split('#');const ic=itemCatalog?.[iid];const src=iid==='1'||iid==='2'?'/assets/currency/icon_'+iid+'_small.png':ic&&typeof itemPicture==='function'?itemPicture(ic):'';const pic=el('div','ds-spic');if(src)pic.append(img(src));pic.append(el('b','',number(Number(n))));if(sold)pic.append(el('span','ds-sold',T('38')));c.title=ic?.name||iid;
      c.append(pic,el('small','','Purchase limit: '+bought+'/'+row.buy_time),price(row.cost,()=>buyNow({action:'buy',shop,id:row.id},"Purchased"),locked||sold));grid.append(c);}list.append(grid);});}};
  draw();void close;}
 return {open,render};
})();
