'use strict';
// Land of Souls (SoulLandMainWindow / SoulLandFightWindow / SoulLandShopWindow). Rules: gxb2/soul_land.py.
// Banner soul_land_main_bg_banner, three forts (50 stages each) with the next stage, its stage rule (god skill) and Fight,
// idle Soul Branches (collect), Store (soul_land_shop), Anima Stone Ritual and the Anima Gear bag.
const SoulLand=(()=>{
 let origin='league',cat=null,fort=1,skipReplay=false;
 const A=n=>'/assets/souls/'+n;
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 try{skipReplay=localStorage.getItem('gxb2.soulLand.skip')==='1';}catch{}
 function root(){let r=$('soul-land-view');if(!r){r=el('section','soul-land-view');r.id='soul-land-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function open(from){origin=from||view;root();if(!cat)cat=await Souls.load();showView('soul-land');render();}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const it=itemCatalog?.[id];if(it&&itemIcons.has(it.icon))return '/assets/item-icons/'+it.icon+'.png';return cat?.icons?.[id]?A(cat.icons[id]+'.png'):'';}
 function chips(obj){const w=el('span','lsl-chips');for(const [k,n]of Object.entries(obj||{})){const c=el('span','lsl-chip');const s=icon(k);if(s)c.append(img(s));c.append(el('b','',number(n)));c.title=(itemCatalog?.[k]?.name||cat?.names?.[k]||k);w.append(c);}return w;}
 async function act(req){try{const r=await api('/api/soul-land/action',req);state=r.state;return r;}catch(e){GirlUI.toast(e.message);return null;}finally{if(view==='soul-land')render();}}
 // soul_land_main_window.prefab (720×1280, y up, centre 640): the map (soul_land_main_bg_banner), logo + "Remaining Time", help,
 // the three forts (soul_land.fort_img at their xy, "Progress: n/50" on soul_land_bg_gqjd), the hang tree (soul_land_bg_dx_1 +
 // soul_land_icon_ylz_2 + soul_land_award effect, amount, "n/5 min", Collect) and the Shop / Ritual buttons.
 const S=n=>'/assets/sprite/'+n+'.png';
 const at=(e,x,y,w,h)=>{e.style.left=`calc(${360+x-w/2} * var(--u))`;e.style.top=`calc(${640-y-(h||0)/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;if(h!=null)e.style.height=`calc(${h} * var(--u))`;return e;};
 const FORT_POS=[[-63,292],[144,-11],[-159,-125]];let hangFx=null;
 function render(){const r=root();if(view!=='soul-land'||!cat)return;const info=state.soul_land_info||{};hangFx?.destroy?.();hangFx=null;r.replaceChildren();const st=el('div','lsl2-stage');r.append(st);
  st.append(at(img('/assets/bg/soul_land_main_bg_banner.webp','lsl2-bg'),0,0,1024,2048));
  const top=at(el('div','lsl2-top'),0,612,720,56);const c=el('span','lsl2-res');c.append(img(icon('421')),el('b','',String(info.tickets??0)));c.title=cat.names['421']||'Soul Challenge Ticket';top.append(c);const back=btn('lsl2-back','',()=>showView(origin==='soul-land'?'league':origin));back.append(img('/assets/ui/win_back_btn.png'));top.append(back);st.append(top);
  st.append(at(img(S('soul_land_text_logo_en_en'),'lsl2-abs'),0,489-56,488,150));
  if(!info.open){st.append(at(el('p','lsl2-note',"Land of Souls unlocks when a Girl reaches level "+(info.open_lv||200)+'.'),0,200,560,null));nav(st);return;}
  const left=Math.max(0,(info.cycle_end||0)-Math.floor(Date.now()/1000));st.append(at(el('p','lsl2-time','Remaining Time: '+Math.floor(left/86400)+'D '+Math.floor(left%86400/3600)+'H'),0,436-56,360,26));
  const help=at(btn('lsl2-ibtn','',()=>CampaignUI.popup("Land of Souls\n\nThree areas of 50 stages with different rules. Each battle costs 1 Soul Challenge Ticket (returned on defeat).\nClearing more stages increases the tree's Anima Stone production every 5 minutes (up to 24 h accumulated).\nThe season resets when time runs out.",{})),317,517-56,52,52);help.append(img(S('help_2')));st.append(help);
  const gear=at(btn('lsl2-ibtn','',()=>Bots.open('soul_land','Rank')),317,454-56,52,52);gear.append(img(S('btn_rank_2')));gear.title='Rank';st.append(gear);
  info.forts.forEach((f,i)=>{const row=cat.land[f.first]||{};const [ox,oy]=String(row.xy||'0|0').split('|').map(Number);const [bx,by]=FORT_POS[i]||[0,0];const x=bx+(ox||0),y=by+(oy||0)-40;const done=f.cleared?f.cleared-f.first+1:0;
   const b=at(btn('lsl2-fort','',()=>stage(f)),x,y,124,160);b.append(img(S(row.fort_img||'soul_land_btn_gq'),'lsl2-fort-img'));b.querySelector('img').onerror=function(){this.onerror=null;this.src=S(['soul_land_btn_gq','soul_land_btn_gq_n','soul_land_btn_gq_zy'][i]);};st.append(b);
   const lab=at(el('div','lsl2-prog','Progress: '+done+'/'+f.total),x,y+98,200,36);lab.style.backgroundImage=`url('${S('soul_land_bg_gqjd')}')`;st.append(lab);});
  // bottom (downCon at y -433)
  const D=-433+40;const shopB=at(btn('lsl2-big','',shop),-220,D,266,230);shopB.append(img(S('soul_land_btn_sd')),img(S('soul_land_text_sd_en_en'),'lsl2-big-t'));st.append(shopB);
  const rit=at(btn('lsl2-big','',()=>Souls.ritual?.()),223,D-15,266,198);rit.append(img(S('soul_land_btn_jc')),img(S('soul_land_text_jc_en_en'),'lsl2-big-t r'));st.append(rit);
  const tree=at(el('div','lsl2-tree'),0,D+87,148,148);tree.style.backgroundImage=`url('${S('soul_land_bg_dx_1')}')`;const fxh=el('div','lsl2-treefx');tree.append(fxh,img(S('soul_land_icon_ylz_2')),el('b','',number(Object.values(info.hang||{})[0]||0)));st.append(tree);
  GxbSpine.mount(fxh,'/assets/spine/soul_land_award',{width:300,height:300,scale:1,origin:[.5,.5],sequence:[['texiao01',true]]}).then(h=>{if(fxh.isConnected)hangFx=h;else h.destroy();}).catch(()=>{});
  const rate=Object.entries(info.hang_rate||{})[0];const day=at(el('div','lsl2-rate'),0,D-13,200,36);day.style.backgroundImage=`url('${S('soul_land_bg_gqjd')}')`;if(rate)day.append(img(icon(rate[0])));day.append(el('b','',(rate?Math.round(rate[1]/12):0)+'/5 min'));st.append(day);
  const col=at(btn('lsl2-collect','Collect',async()=>{const x=await act({action:'hang'});if(x){CampaignUI.popup('Collect',x.got||info.hang||{});render();}},!(info.hang_hours>0)),0,D-68,172,66);col.style.backgroundImage=`url('${S('soul_land_btn_sj')}')`;st.append(col);
  nav(st);}
 function nav(st){const src=document.querySelector('.menu-explorer-bottom');if(src){const n=src.cloneNode(true);n.classList.add('lsl2-nav');n.querySelectorAll('button').forEach(b=>b.classList.remove('current'));st.append(n);}}
 // SoulLandFightWindow: the fort's next stage, its rule (god skill), rewards and Fight
 function stage(f){const info=state.soul_land_info||{};const {body,close}=GirlUI.win({title:'Area '+f.fort,cls:'lsl2-win'});
  if(!f.next){body.append(el('p','lsl-note',"Area completed!"));return;}
  const row=cat.land[f.next];const n=f.next-f.first+1;body.append(el('h3','lsl2-h','Stage '+n+' / '+f.total));const god=cat.god_text[row.god_skill];if(god)body.append(el('b','lsl-rule',god[0]),GirlUI.rich('p','lsl-desc',god[1]));
  const aw=el('div','lsl-awards');aw.append(el('small','','Rewards:'),chips(Object.fromEntries(String(row.awards_show||'').split('|').filter(x=>x.includes('#')).map(x=>x.split('#').map(Number)))));body.append(aw);
  const acts=el('div','lsl-acts');const sk=btn('lsl-skip'+(skipReplay?' on':''),(skipReplay?'☑':'☐')+' Skip',()=>{skipReplay=!skipReplay;try{localStorage.setItem('gxb2.soulLand.skip',skipReplay?'1':'0');}catch{}sk.textContent=(skipReplay?'☑':'☐')+' Skip';sk.classList.toggle('on',skipReplay);});
  acts.append(sk,btn('gs-btn lsl-fight','Fight',()=>{close();fight(f.next,n);},(info.tickets||0)<1));body.append(acts,el('small','lsl-hint',"Uses your current lineup · 1 Soul Challenge Ticket (returned on defeat)."));}
 async function fight(stage,n){const res=await act({action:'fight',stage});if(!res)return;const label="Land of Souls · Area "+fort+" · Stage "+n;
  if(!skipReplay&&res.report&&typeof watchEventBattle==='function'){await watchEventBattle({report:res.report,rewards:res.got||{}},'soul-land',label);}
  else CampaignUI.result(res.win,res.got||{},{event:true,label,report:res.report});}
 function shop(){const {body}=GirlUI.win({title:'Store',cls:'lsl-shop'});const info=state.soul_land_info||{};body.append(el('p','','Soul Branches: '+number(state.items['422']||0)+" · limits reset every 28-day cycle."));
  for(const row of Object.values(cat.land_shop)){const [iid,num]=String(row.item).split('#');const left=Number(row.limit)-Number(info.shop?.[row.id]||0);const r=el('div','lsl-shop-row');r.append(chips({[iid]:Number(num)}),el('span','',(cat.names[iid]||itemCatalog?.[iid]?.name||iid)),el('small','',"Remaining: "+left+'/'+row.limit),chips(Object.fromEntries([String(row.cost).split('#').map(Number)])));
   r.append(btn('gs-btn','Buy',async()=>{const x=await act({action:'buy',id:row.id,count:1});if(x){document.querySelector('.gs-overlay')?.remove();shop();}},left<=0));body.append(r);}}
 return {open,render};
})();
