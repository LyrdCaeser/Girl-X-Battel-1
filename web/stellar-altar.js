'use strict';
// Stellar Altar (StarryAltarWindow, captures 2026-09-29-fb/13, 46, 115): starry_altar_bg, logo, the chosen Cosmos girl's
// chibi on the altar, her card (tap to change), record (last 50 draws), the reward-mode panel (Surprise 0.25 % / Accumulate
// 10 shards every 40), Draw 1 / Draw 10 with Star Tokens, Cosmos shards (100 → girl) and the Galaxy Voyage entry.
// Rules: gxb2/stellar_altar.py. Prefix sa-.
const StellarAltar=(()=>{
 let origin='home',chibi=null,chibiKey='';
 const A=n=>'/assets/stellar/'+n;
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 const nameOf=id=>girlsCatalog.find(g=>g.id===Number(id))?.name||"Girl "+id;
 function iconOf(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}if(it&&itemIcons.has(it.icon))return '/assets/item-icons/'+it.icon+'.png';return id==='358'?A('icon_358.png'):'';}
 function root(){let r=$('stellar-altar-view');if(!r){r=el('section','stellar-altar-view');r.id='stellar-altar-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from){origin=from||view;root();showView('stellar-altar');render();const g=$('game-root');if(g)g.scrollTop=0;}
 async function act(req){try{const r=await api('/api/stellar-altar/action',req);state=r.state;return r;}catch(e){GirlUI.toast(e.message);return null;}finally{if(view==='stellar-altar')render();}}
 function render(){const r=root();if(view!=='stellar-altar'){chibi?.destroy();chibi=null;chibiKey='';return;}const s=state.stellar_altar_info||{};r.replaceChildren();
  const top=el('div','sa-top');const t=el('span','sa-res');t.append(img(A('icon_358.png')),el('b','',number(s.tokens||0)));t.title='Star Token';top.append(t);
  const back=btn('sa-back','',()=>showView(origin==='stellar-altar'?'home':origin));back.append(img('/assets/ui/win_back_btn.png'));top.append(back);r.append(top);
  const stage=el('div','sa-stage');stage.append(img(A('starry_altar_en_en.png'),'sa-logo'));
  stage.append(btn('sa-round help','?',()=>CampaignUI.popup("1. Each Star Token grants one draw with a basic reward.\n2. Each draw may also grant the bonus reward (5 Customized Cosmos Shards, 10%) or the jackpot (selected Cosmos Girl, 0.25% in Surprise mode).\n3. Accumulation mode grants 10 extra Shards every 40 draws.\n4. 100 Shards grant a 10★ Cosmos Girl of your choice.",{})),btn('sa-round rates','🔍',rates),btn('sa-round rec','☰',record));
  if(!s.open){stage.append(el('p','sa-locked',"Stellar Altar unlocks after clearing Campaign stage 15-10."));r.append(stage);return;}
  const holder=el('div','sa-chibi');stage.append(holder);
  const card=btn('sa-card','',chooseGirl);if(cardIds.has(s.target))card.append(img('/assets/cards/partner_card_'+s.target+'.png'));card.append(el('i','sa-swap','⇄'));card.title=nameOf(s.target);stage.append(card);
  const galaxy=btn('sa-galaxy','Galaxy Voyage ›',()=>openMenu('galaxy','stellar-altar'));stage.append(galaxy);
  const mode=el('div','sa-mode');mode.append(el('b','',s.mode===4?'Reward · Surprise Mode':'Reward · Accumulate Mode'),el('span','',s.mode===4?'0.25% chance to obtain a Cosmos Girl for each draw':'Additional 10-star Cosmos Girls Shard ×10 in '+s.to_bonus+' draw(s)'));mode.append(btn('sa-mode-swap','⇄',()=>act({action:'mode',mode:s.mode===4?5:4})));stage.append(mode);
  const draws=el('div','sa-draws');for(const [n,label]of [[1,'Draw 1'],[10,'Draw 10']]){const b=el('div','sa-draw');b.append(btn('gs-btn','',()=>draw(n),(s.tokens||0)<n),el('span','sa-cost'));b.firstChild.textContent=label;b.lastChild.append(img(A('icon_358.png')),el('b','',String(n)));draws.append(b);}stage.append(draws);
  const shards=el('div','sa-shards');const ic=iconOf('940059');if(ic)shards.append(img(ic));shards.append(el('span','','Customized 10-star Cosmos Girls Shard: '+(s.shards||0)+' / 100'),btn('gs-btn','Summon',()=>act({action:'compose',target:s.target}).then(x=>x&&x.girls?.length&&GirlUI.toast(" "+nameOf(s.target)+" joins your team!")),(s.shards||0)<100));stage.append(shards);
  r.append(stage);mountChibi(holder,s.target);}
 async function mountChibi(host,id){try{const cat=await api('/assets/chibis/catalog.json');const meta=cat[String(id)];if(!meta||!host.isConnected)return;const key=id+':'+meta.model;chibi?.destroy();chibiKey=key;
  chibi=await GxbSpine.mount(host,'/assets/chibis/'+meta.model,{width:420,height:420,fit:.7,y:.62,sequence:[['idle',true]]});if(chibiKey!==key||!host.isConnected){chibi?.destroy();chibi=null;}}catch{}}
 async function draw(n){const r=await act({action:'draw',times:n});if(!r)return;const {body}=GirlUI.win({title:'Acquired',cls:'sa-result'});
  const grid=el('div','sa-grid');for(const [k,v]of Object.entries(r.got||{})){const c=el('div','sa-item');const ic=iconOf(k);if(ic)c.append(img(ic));c.append(el('b','',number(v)));c.title=itemCatalog?.[k]?.name||k;grid.append(c);}body.append(grid);
  for(const pid of r.girls||[]){const h=state.roster.find(x=>x.partner_id===pid);if(h){const g=el('div','sa-grand');if(cardIds.has(h.table_id))g.append(img('/assets/cards/partner_card_'+h.table_id+'.png'));g.append(el('b','',"Jackpot! "+h.name));body.append(g);}}
  const a=el('div','gs-btns');a.append(btn('gs-btn white','OK',()=>document.querySelector('.gs-overlay')?.remove()),btn('gs-btn','×'+n,()=>{document.querySelector('.gs-overlay')?.remove();draw(n);},(state.stellar_altar_info?.tokens||0)<n));body.append(a);}
 function chooseGirl(){const s=state.stellar_altar_info;const {body,close}=GirlUI.win({title:'Grand Reward',cls:'sa-choose'});body.append(el('p','',"Choose the Cosmos Girl for the jackpot and Shards."));const row=el('div','sa-girls');
  for(const id of s.girls){const b=btn('sa-girl'+(id===s.target?' on':''),'',()=>{close();act({action:'mode',mode:s.mode,target:id});});if(cardIds.has(id))b.append(img('/assets/cards/partner_card_'+id+'.png'));b.append(el('b','',nameOf(id)));row.append(b);}body.append(row);}
 function record(){const s=state.stellar_altar_info;const {body}=GirlUI.win({title:'Record',cls:'sa-record'});if(!s.record?.length){body.append(el('p','','No record yet'));return;}
  const list=el('div','sa-rec');for(const e of [...s.record].reverse()){const row=el('div','sa-rec-row'+(e.grand?' grand':e.extra?' extra':''));for(const [k,v]of Object.entries(e.basic||{})){const ic=iconOf(k);const c=el('span','sa-item small');if(ic)c.append(img(ic));c.append(el('b','',number(v)));row.append(c);}if(e.grand)row.append(el('b','sa-tag','★ '+nameOf(e.grand)));list.append(row);}body.append(list,el('p','detail-note',"The 50 most recent draws are saved."));}
 async function rates(){const drop=await api('/assets/dropbox-80001.json').catch(()=>null);const {body}=GirlUI.win({title:'Rate',cls:'sa-rates'});
  body.append(el('b','','Grand Reward'),el('p','',"Selected Cosmos Girl: 0.25% per draw (Surprise mode)."),el('b','','Additional Reward'),el('p','',"5 Customized 10-star Cosmos Girls Shards: 10% per draw."),el('b','','Basic Reward'),el('p','',"Each draw guarantees a basic reward:"));
  if(drop){const tot=drop.reduce((a,r)=>a+Number(r.weight),0);const g=el('div','sa-grid');for(const r of drop){const [k,v]=r.item.split('#');const c=el('div','sa-item');const ic=iconOf(k);if(ic)c.append(img(ic));c.append(el('b','',number(Number(v))),el('small','',(r.weight/tot*100).toFixed(2)+'%'));g.append(c);}body.append(g);}}
 return {open,render};
})();
