'use strict';
// Transfer (Campus → Transfer, AltarWindow): tabs Altar / Reverse over the fort_bg_1 backdrop. Altar: 12 slots to retire girls
// (DECOMPOSE_PARTNERS), preview of what comes back (/api/altar/preview = Partner:getDecompose), faction / star filter, roster
// count, Smart (fills with the lowest unlocked girls of the filter) and Retire. Reverse: pick a 5★+ girl and open the Reverse
// window of her sheet (ROLLBACK_PARTNER). Prefix al-.
const Altar=(()=>{
 let origin='campus',tab=1,sel=[],faction=0,star=0,busy=false;
 const A=n=>'/assets/altar/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 const icon=h=>typeof CampaignFlow!=='undefined'?CampaignFlow.heroIcon(h):portrait(h.table_id,80);
 const catOf=h=>girlsCatalog.find(g=>g.id===h.table_id)||{};
 const locked=h=>(h.flags||[]).some(Boolean)||catOf(h).group===7;
 function root(){let r=$('altar-view');if(!r){r=el('section','altar-view');r.id='altar-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from){origin=from||view;sel=[];root();showView('altar');draw();}
 function draw(){const r=root();if(view!=='altar')return;r.replaceChildren();sel=sel.filter(id=>state.roster.some(h=>h.partner_id===id));
  const top=el('div','al-top');for(const id of ['1','2']){const c=el('span','al-res');c.append(img('/assets/currency/icon_'+id+'_small.png'),el('b','',number(state.items?.[id]||0)));top.append(c);}
  const back=btn('al-back','',()=>showView(origin));back.append(img('/assets/ui/win_back_btn.png'));top.append(back);r.append(top);
  const nav=el('div','al-nav');[[1,'Altar','left'],[2,'Reverse','right']].forEach(([i,t,k])=>{const b=btn('al-tab'+(tab===i?' on':''),t,()=>{tab=i;sel=[];draw();});b.style.backgroundImage=`url('${A('nav_btn_'+(tab===i?'blue':'white')+'_'+k)}')`;nav.append(b);});r.append(nav);
  const upper=el('div','al-panel al-upper');r.append(upper);
  if(tab===1){upper.append(btn('al-help','?',()=>CampaignUI.popup("Retire Girls at the Altar to recover its resources, 70% of Grade Stones spent on grades, and 65% of their level EXP. Equipment returns to the Bag.\nLocked Girls, Cosmos Girls, and Dolls cannot be retired. Maximum 5 Girls of 6★ or higher per day.",{})),btn('al-preview','',()=>preview()));
   const grid=el('div','al-slots');for(let i=0;i<12;i++){const id=sel[i],h=id&&state.roster.find(x=>x.partner_id===id);const s=btn('al-slot'+(h?' full':''),'',()=>{if(h){sel=sel.filter(x=>x!==id);draw();}});if(h)s.append(icon(h));else s.append(img(A('icon_none'),'al-none'),img(A('altar_add_bg'),'al-add'));grid.append(s);}upper.append(grid);}
  else{const id=sel[0],h=id&&state.roster.find(x=>x.partner_id===id);upper.append(el('p','al-note',"Choose a Girl of 5★ or higher for Rebirth: she returns her materials (Dolls, copies, and part of her EXP)."));
   const s=el('div','al-slot big'+(h?' full':''));if(h)s.append(icon(h));else s.append(img(A('icon_none'),'al-none'),img(A('altar_add_bg'),'al-add'));upper.append(s);
   upper.append(btn('al-btn al-go','Reverse',()=>{if(h&&typeof GirlUI!=='undefined'&&GirlUI.reverse){GirlUI.reverse(h);}},!h));}
  const lower=el('div','al-panel al-lower');r.append(lower);
  const f=el('div','al-filter');for(let g=1;g<=6;g++){const b=btn('al-f'+(faction===g?' on':''),'',()=>{faction=faction===g?0:g;draw();});b.append(img('/assets/summon-result/img_group'+g+'.png'));f.append(b);}
  const ss=el('select','al-star');[['0',"★ All"],['1','1★'],['2','2★'],['3','3★'],['4','4★'],['5','5★'],['6','6★+']].forEach(([v,t])=>ss.append(new Option(t,v)));ss.value=String(star);ss.onchange=()=>{star=Number(ss.value);draw();};f.append(ss);lower.append(f);
  const list=listed();const g2=el('div','al-grid');for(const h of list){const on=sel.includes(h.partner_id);const c=el('button','al-pick'+(on?' on':'')+(locked(h)?' lock':''));c.type='button';c.append(icon(h));if(locked(h))c.append(el('span','al-lockicon','🔒'));c.onclick=()=>pick(h);g2.append(c);}lower.append(g2);
  const foot=el('div','al-foot');foot.append(el('span','al-count',"Girls: "+state.roster.length+'/'+(state.slots?.limit||state.partners_limit||'∞')));
  if(tab===1){foot.append(btn('al-btn white','Smart',()=>smart()),btn('al-btn al-retire','Retire',()=>retire(),!sel.length));}
  lower.append(foot);}
 function listed(){return [...state.roster].filter(h=>(!faction||catOf(h).group===faction)&&(!star||(star===6?(h.stars||0)>=6:(h.stars||0)===star))&&(tab===1||(h.stars||0)>=5)).sort((a,b)=>(a.stars||0)-(b.stars||0)||(a.lv||0)-(b.lv||0)||a.table_id-b.table_id);}
 function pick(h){if(locked(h)){GirlUI.toast(catOf(h).group===7?"Cosmos Girls cannot go to the Altar":"Girl locked");return;}
  if(tab===2){sel=sel[0]===h.partner_id?[]:[h.partner_id];draw();return;}
  if(sel.includes(h.partner_id))sel=sel.filter(x=>x!==h.partner_id);else{if(sel.length>=12){GirlUI.toast("Up to 12 Girls");return;}sel.push(h.partner_id);}draw();}
 function smart(){const used=new Set([...(state.formation||[]).map(f=>f.partner_id),...(state.campaign_hang||[]).map(f=>f.partner_id)]);for(const h of listed()){if(sel.length>=12)break;if(!locked(h)&&!used.has(h.partner_id)&&(h.stars||0)<=4&&!sel.includes(h.partner_id))sel.push(h.partner_id);}if(!sel.length)GirlUI.toast("No available Girls of 4★ or lower match this filter");draw();}
 async function preview(){if(!sel.length){GirlUI.toast("Choose Girls first");return;}try{const r=await api('/api/altar/preview',{partner_ids:sel});items('Preview',r.items);}catch(e){GirlUI.toast(e.message);}}
 function items(title,got){const {body}=GirlUI.win({title,cls:'al-win'});const g=el('div','al-items');for(const [k,n]of Object.entries(got||{})){const c=el('div','al-item');const it=itemCatalog?.[k];const src=(k==='1'||k==='2')?'/assets/currency/icon_'+k+'_small.png':it&&typeof itemPicture==='function'?itemPicture(it):'';if(src)c.append(img(src));c.append(el('b','',number(n)));c.title=it?.name||k;g.append(c);}if(!g.children.length)g.append(el('p','','—'));body.append(g);}
 async function retire(){if(busy||!sel.length)return;const hi=sel.map(id=>state.roster.find(h=>h.partner_id===id)).filter(h=>(h?.stars||0)>=4).length;if(hi&&!confirm('Vas a retirar '+hi+" Girl(s) of 4★ or higher. Continue?"))return;
  busy=true;try{const r=await api('/api/action',{message:'DECOMPOSE_PARTNERS',data:{partner_ids:sel}});state=r.state;sel=[];draw();items('Retire',state.last_decompose);}catch(e){GirlUI.toast(e.message);}finally{busy=false;}}
 return {open,render:draw};
})();
