'use strict';
// Skin Collection (CollectionSkinWindow; captures 2026-09-29-fb/17, 33 and -k/02): Fashion Level badge, points bar and
// "Attribute Boost: HP +…, Attack +…", search, "Hide locked Skins", Rarity mode (Common / Rare / Epic / Legendary) or Theme
// mode (themes with owned/total and their Fashion Point rewards; Festival / Oath / Swimsuit / Other). Cards reuse the Skins
// tab frame (PartnerCard:setSkinCard). Rules: gxb2/skins.py. Prefix scol-.
const SkinCollection=(()=>{
 let origin='girls',cat=null,mode='rarity',rarity=3,themeType=1,hide=false,query='';
 const U='/assets/skins/ui/',RAR=['','Common','Rare','Epic','Legendary'],THEMES=['','Festival','Oath','Swimsuit','Other'];
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 function root(){let r=$('skin-collection-view');if(!r){r=el('section','skin-collection-view');r.id='skin-collection-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function open(from){origin=from||view;if(!cat)cat=await api('/api/skins/catalog',{});root();showView('skin-collection');render();const g=$('game-root');if(g)g.scrollTop=0;}
 async function act(req){try{const r=await api('/api/skins/action',req);state=r.state;if(r.got)GirlUI.toast('+'+Object.values(r.got)[0]+' Fashion Point');}catch(e){GirlUI.toast(e.message);}finally{if(view==='skin-collection')render();}}
 const owned=id=>(state.skins_info?.collected||[]).includes(Number(id));
 function card(id){const s=cat.skins[id];const tid=s.partners[0];const girl=girlsCatalog.find(g=>g.id===tid);const c=el('div','sk-card scol-card'+(owned(id)?'':' locked'));
  const art=el('div','sk-pic');art.style.backgroundImage=`url('/assets/skins/cards/${id}.webp'),url('${typeof detailImage==='function'?detailImage(Number(id)):''}')`;c.append(art,el('i','sk-frame'));
  if(girl?.group){c.append(img(U+'img_group'+girl.group+'.png','sk-group'));}
  const r=Number(s.rarity||0);if(r){const q=el('span','sk-rarity',RAR[r]);q.style.backgroundImage=`url('${U}collection_dress_new_bg_${r}.png')`;c.append(q);}
  c.append(el('span','sk-amount scol-girl',girl?.name||''),el('b','sk-name',s.name));c.title=(girl?.name||'')+' · '+s.name+(owned(id)?'':" (locked)");return c;}
 function render(){const r=root();if(view!=='skin-collection'||!cat)return;const info=state.skins_info||{};r.replaceChildren();
  const top=el('div','scol-top');const back=btn('scol-back','',()=>showView(origin==='skin-collection'?'girls':origin));back.append(img('/assets/ui/win_back_btn.png'));top.append(back);r.append(top);
  const head=el('div','scol-head');const lv=el('div','scol-lv');lv.append(img('/assets/skins/ui/btn_skin_collection.png'),el('b','',String(info.level||0)));head.append(lv);
  const bar=el('div','scol-bar');const nxt=info.next_point||info.points||1;const fill=el('i');fill.style.width=Math.min(100,(info.points||0)/nxt*100)+'%';bar.append(fill,el('span','',(info.points||0)+'/'+(info.next_point??'MAX')));
  const eff=String(info.tier?.effect||'hp#0|atk#0').split('|').map(x=>x.split('#'));const boost=el('p','scol-boost','Attribute Boost: '+eff.map(([k,v])=>(k==='hp'?'HP':'Attack')+' +'+number(Number(v))).join(', '));
  const mid=el('div','scol-mid');mid.append(bar,boost);head.append(mid,btn('scol-help','?',()=>CampaignUI.popup("Each collected skin adds Fashion Points. Fashion level increases boost all Girls' HP and Attack.\nThemes grant rewards for collecting multiple skins from the same theme.",{})));r.append(head);
  const tools=el('div','scol-tools');const q=el('input','scol-search');q.placeholder='Enter Keyword';q.value=query;q.oninput=()=>{query=q.value;renderList();};const hl=el('label','scol-hide');const cb=el('input');cb.type='checkbox';cb.checked=hide;cb.onchange=()=>{hide=cb.checked;renderList();};hl.append(el('span','','Hide locked Skins'),cb);tools.append(q,hl);r.append(tools);
  const list=el('div','scol-list');r.append(list);
  const foot=el('div','scol-foot');const tabs=el('div','scol-tabs');(mode==='rarity'?RAR.slice(1):THEMES.slice(1)).forEach((t,i)=>tabs.append(btn('scol-tab'+((mode==='rarity'?rarity:themeType)===i+1?' on':''),t,()=>{if(mode==='rarity')rarity=i+1;else themeType=i+1;render();})));
  foot.append(tabs,btn('scol-mode',mode==='rarity'?'Rarity ▲':'Theme ▲',()=>{mode=mode==='rarity'?'theme':'rarity';render();}));r.append(foot);
  function match(id){const s=cat.skins[id];if(hide&&!owned(id))return false;if(!query)return true;const g=girlsCatalog.find(x=>x.id===s.partners[0]);return (s.name+' '+(g?.name||'')).toLowerCase().includes(query.toLowerCase());}
  function renderList(){list.replaceChildren();
   if(mode==='rarity'){const grid=el('div','scol-grid');const ids=Object.keys(cat.skins).filter(id=>Number(cat.skins[id].rarity)===rarity&&match(id)).sort((a,b)=>owned(b)-owned(a)||a-b);for(const id of ids)grid.append(card(id));if(!ids.length)grid.append(el('p','scol-empty',"No skins."));list.append(grid);return;}
   for(const t of cat.themes.filter(t=>t.type===themeType)){const ids=t.skins.map(String).filter(id=>cat.skins[id]&&match(id));if(!ids.length)continue;const have=t.skins.filter(owned).length;
    const h=el('div','scol-theme');h.append(el('b','','◆ '+(t.name||'Theme '+t.id)),el('span','',have+'/'+t.skins.length),btn('scol-info','!',()=>themeRewards(t)));list.append(h);const grid=el('div','scol-grid');for(const id of ids)grid.append(card(id));list.append(grid);}
   if(!list.childElementCount)list.append(el('p','scol-empty',"No skins."));}
  renderList();}
 function themeRewards(t){const have=t.skins.filter(owned).length,claimed=state.skins_info?.theme_claimed?.[t.id]||[];const {body}=GirlUI.win({title:t.name||'Theme',cls:'scol-rewards'});body.append(el('p','',"Theme skins: "+have+'/'+t.skins.length));
  for(const part of String(t.awards).split('|')){const [n,item,num]=part.split('#').map(Number);const row=el('div','scol-reward');row.append(el('b','',n+' skins'),el('span','','Fashion Point ×'+num));const done=claimed.includes(n);row.append(btn('gs-btn'+(done?' white':''),done?'Claimed':'Claim',()=>{document.querySelector('.gs-overlay')?.remove();act({action:'theme_claim',theme:t.id,count:n});},done||have<n));body.append(row);}}
 document.addEventListener('DOMContentLoaded',()=>{const intro=document.querySelector('#girls-gallery-panel .gallery-intro');if(intro&&!$('scol-open')){const b=el('button','secondary','Skin Collection');b.id='scol-open';b.type='button';b.onclick=()=>open('girls');intro.append(b);}});
 return {open,render};
})();
