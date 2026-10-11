'use strict';
// Recovered GambleWindow/Shop contracts; board sampling and the brief highlight are local adapters.
const Slots=(()=>{
 let type=1,origin='campus',pending=false,message='',panel='machine',bulk=10;
 let generation=0,dealer=null,timer=null,anchorTime=null,anchorAt=0,lastSlot=0;
 const skips={};
 try{const saved=Number(localStorage.getItem('gxb2-slots-bulk'));if([10,20,50].includes(saved))bulk=saved;for(const t of [1,2])skips[t]=localStorage.getItem('gxb2-slots-skip-'+t)==='1';}catch{}
 const el=(tag,cls,text)=>node(tag,cls,text),A=n=>'/assets/slots/'+n+'.png';
 const info=()=>state.acquisition?.slots?.[type],lucky=()=>state.acquisition?.lucky;
 function root(){let r=$('slots-view');if(!r){r=el('section','slots-view');r.id='slots-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function stop(){generation++;if(timer){clearInterval(timer);timer=null;}if(dealer){dealer.destroy();dealer=null;}}
 function now(){return (anchorTime??Date.now()/1000)+(performance.now()-anchorAt)/1000;}
 function duration(seconds){const n=Math.max(0,Math.ceil(seconds));return [Math.floor(n/3600),Math.floor(n%3600/60),n%60].map(v=>String(v).padStart(2,'0')).join(':');}
 function cycleBulk(){bulk=({10:20,20:50,50:10})[bulk];try{localStorage.setItem('gxb2-slots-bulk',String(bulk));}catch{}render();}
 function button(parent,label,fn,disabled=false,cls=''){const b=el('button',cls,label);b.type='button';b.disabled=disabled||pending;b.addEventListener('click',fn);parent.append(b);return b;}
 function item(parent,id,n){const row=itemCatalog[id],extra=state.acquisition?.item_icons?.[id],picture=(id==='1'||id==='2')?'/assets/currency/icon_'+id+'_small.png':(row&&itemPicture(row))||(extra&&A(extra));if(picture){const im=el('img');im.src=picture;im.alt=(id==='1'?"Gold":id==='2'?"Gems":row?.name)||"Item "+id;parent.append(im);}parent.append(el('b','',number(n)),el('span','',(id==='1'?"Gold":id==='2'?"Gems":row?.name)||"Item "+id));}
 function illustrated(parent,label,asset,fn,disabled=false){const b=button(parent,label,fn,disabled,'sl-illustrated');const im=el('img');im.src=A(asset);im.alt='';b.prepend(im);return b;}
 async function mountDealer(host,token,typ){try{const mounted=await GxbSpine.mount(host,'/assets/spine/'+(typ===1?'gamble_girl':'gamble_up_girl'),{width:440,height:320,fit:.98,sequence:[['idle',true]]});if(token!==generation||view!=='slots'||!host.isConnected){mounted.destroy();return;}dealer=mounted;}catch{if(token===generation&&host.isConnected)host.append(el('span','sl-dealer-fallback',"Could not load the animation."));}}
 async function animate(slot,typ){lastSlot=slot;if(skips[typ]||view!=='slots'||panel!=='machine')return;const token=generation;const cells=[...root().querySelectorAll('.sl-cell')];for(let i=0;i<12;i++){if(view!=='slots'||generation!==token)return;for(const c of cells)c.classList.toggle('sl-lit',Number(c.dataset.slot)===(i%8)+1);await new Promise(resolve=>setTimeout(resolve,55+i*4));}for(const c of cells)c.classList.toggle('sl-lit',Number(c.dataset.slot)===slot);}
 async function send(name,data={},quiet=false){if(pending)return;const typ=type;pending=true;if(!quiet)message='';render();try{const before={...state.items};const r=await api('/api/action',{message:name,data:name.includes('SHOP')?{shop_type:3,...data}:{gamble_type:typ,...data}});state=r.state;
  if(name==='GAMBLE_GET_AWARD'||name==='BUY_SHOP_ITEM'){if(name==='GAMBLE_GET_AWARD'){const response=r.messages.find(m=>m.type==='gamble_get_award_res')?.data;await animate(response?.awards?.at(-1)||0,typ);}const got={};for(const [id,n]of Object.entries(state.items))if(Number(n)>Number(before[id]||0))got[id]=Number(n)-Number(before[id]||0);if(view==='slots'){CampaignUI.popup(name==='BUY_SHOP_ITEM'?"Lucky Store · received":"Slot Machine · prizes",got);GxbAudio.sfx('gain_window_sound');}}
 }catch(e){message=e.message;}finally{pending=false;render();if(typeof window.render==='function')window.render();}}
 function open(from){origin=from||'campus';type=1;panel='machine';message='';lastSlot=0;showView('slots');send('GAMBLE_GET_INFO',{},true);}
 function refreshControl(parent,s,shop=false){const label=el('b','sl-clock'),b=button(parent,'Refresh',()=>send(shop?'REFRESH_SHOP':'GAMBLE_REFRESH'));parent.append(label);const update=()=>{const free=now()>=s.free_refresh_at;const cost=s.refresh_cost[shop?'6':'2'];label.textContent=free?"Free Refresh available":duration(s.free_refresh_at-now());b.textContent=free?"Refresh · free":'Refresh · '+cost+' '+(shop?'Coupons':"Gems");b.disabled=pending||(!free&&Number(state.items[shop?'6':'2']||0)<Number(cost));};update();return update;}
 // GambleWindow groupBottom (prefab coordinates, 720 units wide): 3×3 machine with 8 gb_icon_bg cells clockwise from the
 // top-left, Next Refresh + green Refresh in the middle, X1 / X10 gb_btn_use_bg buttons, the 10× side lever (normal only),
 // Skip and "Go to Slot Points" above the machine and the dealer (GirlsModel 3 / 4) with her bubble (girls_model_text).
 const TALK={1:['What is more important than luck?',"It's show time~!","Don't pull my rabbit ears! Go away gosh I hate you!"],2:["Senpai I have a gift for you too! Let's swap gifts!","Don't forget to hang your stockings at the foot of your bed so I can leave gifts for you!",'No presents for naughty boys!','Make a wish!']};
 const at=(e,x,y,w,h)=>{e.style.left=`calc(${x-w/2+360} * var(--u))`;e.style.top=`calc(${490-y-h/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;e.style.height=`calc(${h} * var(--u))`;return e;};
 function icon(parent,id,n){const row=itemCatalog[id],extra=state.acquisition?.item_icons?.[id];const pic=(id==='1'||id==='2')?'/assets/currency/icon_'+id+'_small.png':(row&&itemPicture(row))||(extra&&A(extra));const q=Math.min(Math.max(row?.quality||1,1),7);
  const f=el('div','sl-icon');f.style.backgroundImage=`url('/assets/ui/quality_${q}.png')`;if(pic){const im=el('img');im.src=pic;im.alt='';f.append(im);}f.append(el('b','',compact(n)));f.title=(id==='1'?"Gold":id==='2'?"Gems":row?.name)||"Item "+id;parent.append(f);return f;}
 function compact(n){n=Number(n)||0;return n>=1e6&&n%1e5===0?n/1e6+'M':n>=1e4&&n%1e3===0?n/1e3+'K':String(n);}
 function machine(stage,s){
  const host=at(el('div','sl-dealer-model'),0,160,720,640);stage.append(host);mountDealer(host,generation,type);
  const talk=TALK[type];const bubble=at(el('button','sl-bubble'),150,230,300,133);bubble.type='button';bubble.append(el('span','',talk[0]));stage.append(bubble);let k=0;host.onclick=bubble.onclick=()=>{k=(k+1)%talk.length;bubble.firstChild.textContent=talk[k];};
  const skip=at(el('button','sl-skipbtn'+(skips[type]?' on':'')),-265,113,120,40);skip.type='button';skip.append(el('i'),el('span','','Skip'));skip.onclick=()=>{skips[type]=!skips[type];try{localStorage.setItem('gxb2-slots-skip-'+type,skips[type]?'1':'0');}catch{}skip.classList.toggle('on',skips[type]);};stage.append(skip);
  if(type===1&&state.point_events_info?.['20']){const go=at(el('button','sl-go','Go to Slot Points'),158,113,216,44);go.type='button';go.onclick=()=>EventsHub.openPoint(20,'slots');stage.append(go);}
  {const mid=at(el('div','sl-mid'),0,-214,688,616);mid.style.backgroundImage=`url('${A(type===1?'gb_normal_mid_bg':'gb_senior_mid_bg')}')`;stage.append(mid);}
  const pos=[[-170,-29],[0,-29],[170,-29],[170,-186],[170,-344],[0,-344],[-170,-344],[-170,-186]];
  for(const [i,reward]of (s.board?.items||[]).entries()){const [x,y]=pos[i];const cell=at(el('div','sl-cell'+(reward.buy_limit&&reward.buy_times>=reward.buy_limit?' exhausted':'')+(lastSlot===i+1?' sl-lit':'')),x,y,146,146);cell.dataset.slot=String(i+1);icon(cell,String(reward.item_id),reward.item_num);if(reward.buy_limit)cell.append(el('small','',reward.buy_times+'/'+reward.buy_limit));stage.append(cell);}
  const desc=at(el('b','sl-next','Next Refresh'),0,-140,200,26),clock=at(el('b','sl-clock'),0,-172,200,28);const rb=at(el('button','sl-refresh-btn'),0,-221,148,60);rb.type='button';stage.append(desc,clock,rb);
  rb.onclick=()=>send('GAMBLE_REFRESH');
  const upd=()=>{const free=now()>=s.free_refresh_at;const cost=s.refresh_cost['2'];rb.replaceChildren();if(!free){const ci=el('img');ci.src='/assets/currency/icon_2_small.png';ci.alt='';rb.append(ci,el('small','',cost));}rb.append(el('span','','Refresh'));rb.classList.toggle('free',free);rb.disabled=pending||(!free&&Number(state.items['2']||0)<Number(cost));
   clock.textContent=s.board?duration(s.board.system_refresh_time-now()):'--:--:--';};
  if(!s.board||s.expired){const b=at(el('button','sl-load',s.expired?'Update':'Load'),0,-100,160,40);b.type='button';b.onclick=()=>{lastSlot=0;send('GAMBLE_GET_INFO');};stage.append(b);}
  for(const [times,x]of [[1,-120],[type===1?bulk:10,120]]){const choices=s.options.filter(o=>o.times===times);const option=choices.filter(o=>o.available).at(-1)||choices[0];if(!option)continue;const [id,n]=Object.entries(option.cost)[0];
   const b=at(el('button','sl-use'),x,-464,210,73);b.type='button';const ci=el('img');ci.src=A('icon_'+id);ci.alt='';b.append(ci,el('small','',n),el('span','','X '+times));b.disabled=pending||!option.available||Number(state.items[id]||0)<Number(n)||!s.board;b.title=option.available?'':"Requires VIP";b.onclick=()=>send('GAMBLE_GET_AWARD',{index:option.index});stage.append(b);}
  if(type===1&&state.point_events_info?.['20']){const lever=at(el('button','sl-side'),309,-373,60,228);lever.type='button';lever.append(el('b','',String(bulk)),el('span','','×'));lever.title="Change quantity: ×10 → ×20 → ×50";lever.onclick=cycleBulk;stage.append(lever);}
  upd();timer=setInterval(upd,1000);
 }
 function shop(stage){const s=lucky();stage.append(el('h2','','Lucky Store'));if(!s?.available){stage.append(el('p','sl-note',"Lucky Store unlocks at level 14."));return;}if(!s.board){button(stage,"Load offers",()=>send('GET_SHOP_INFO'));return;}
  const grid=el('div','sl-shop-grid');for(const [i,row]of s.board.items.entries()){const c=el('div','sl-shop-item');item(c,String(row.item[0]),row.item[1]);const exhausted=row.buy_times>=s.limit||row.not_selling===1;button(c,exhausted?"Sold out":row.cost[1]+' Coupons',()=>send('BUY_SHOP_ITEM',{index:i+1,num:1}),exhausted||Number(state.items[row.cost[0]]||0)<row.cost[1]);grid.append(c);}stage.append(grid);
  const refresh=el('div','sl-shop-refresh');stage.append(refresh);const tick=refreshControl(refresh,s,true);timer=setInterval(tick,1000);stage.append(el('p','sl-note',"One purchase per offer. Free Refresh every 24 hours; otherwise costs 50 Coupons."));
 }
 function probabilities(stage,s){stage.append(el('h2','',"Board probabilities"));const active=s.board?.items.filter(r=>!r.buy_limit||r.buy_times<r.buy_limit)||[];const total=active.reduce((n,r)=>n+r.weight,0);for(const [i,row]of (s.board?.items||[]).entries()){const c=el('div','sl-probability');item(c,String(row.item_id),row.item_num);const exhausted=row.buy_limit&&row.buy_times>=row.buy_limit;c.append(el('strong','',exhausted?"Sold out":(total?100*row.weight/total:0).toFixed(2)+' %'));c.append(el('small','','Peso original: '+row.weight+" · position "+(i+1)));stage.append(c);}stage.append(el('p','sl-note',"Probability of the next draw in Reborn. Depleted rewards are excluded and remaining weights are normalized. The original cooldown rule has not been recovered yet."));
 }
 function render(){stop();const r=root();if(view!=='slots')return;if(anchorTime!==state.server_time){anchorTime=state.server_time??Date.now()/1000;anchorAt=performance.now();}r.replaceChildren();const s=info();
  const ticket=type===1?'35':'29';const top=el('header','sl-top sl-bar');for(const id of [ticket,'2']){const c=el('span','sl-res');const im=el('img');im.src=id==='2'?'/assets/currency/icon_2_small.png':A('icon_'+id);im.alt='';c.append(im,el('b','',number(state.items[id]||0)));c.title=itemCatalog[id]?.name||'';top.append(c);}
  const bk=button(top,'',()=>showView(origin==='slots'?'campus':origin),false,'sl-back');const bi=el('img');bi.src='/assets/ui/win_back_btn.png';bi.alt="Back";bk.append(bi);r.append(top);
  const nav=el('nav','sl-tabs sl-navsprite');const open2=state.acquisition?.slots?.[2]?.options?.[0]?.available!==false;for(const [id,label,side]of [[1,'Slot Machine','left'],[2,'High Stakes Slot Machine','right']]){const b=button(nav,label,()=>{type=id;panel='machine';message='';lastSlot=0;send('GAMBLE_GET_INFO',{},true);});b.classList.toggle('on',type===id);b.style.backgroundImage=`url('${A('nav_btn_'+(type===id?'blue':id===2&&!open2?'grey':'white')+'_'+side)}')`;if(id===2&&!open2){const lk=el('img','sl-navlock');lk.src=A('awake_lock');lk.alt='';b.append(lk);}}r.append(nav);
  const stage=el('div','sl-stage sl-board');stage.style.backgroundImage=`url('${A(type===1?'gb_normal_bg':'gb_senior_bg')}')`;r.append(stage);
  if(!s?.options[0]?.available){stage.append(el('p','sl-note sl-locked',"High Stakes unlocks at level 80 or VIP 3. Ten draws require VIP 3."));return;}
  const round=(x,y,w,h,src,title,fn,cls='sl-round')=>{const b=at(el('button',cls),x,y,w,h);b.type='button';const im=el('img');im.src=A(src);im.alt=title;b.append(im);b.title=title;b.onclick=fn;stage.append(b);return b;};
  const toggle=p=>()=>{panel=panel===p?'machine':p;if(panel==='shop')send('GET_SHOP_INFO',{},true);else render();};
  round(-315,444,65,65,'check_white_btn',"Rates",toggle('probability'));round(-240,444,65,65,'help_2',"Help",toggle('help'));
  round(type===1?205:280,440,73,71,type===1?'gb_normal_records':'gb_senior_records','Record',toggle('history'),'sl-deco').append(el('span','','Record'));
  if(type===1)round(304,441,80,82,'shop','Shop',toggle('shop'),'sl-deco');
  machine(stage,s);
  if(panel!=='machine'){const pan=el('div','sl-panel');const close=el('button','sl-panel-close');close.type='button';close.setAttribute('aria-label',"Close");close.onclick=()=>{panel='machine';render();};pan.append(close);
   if(panel==='shop')shop(pan);else if(panel==='probability')probabilities(pan,s);else if(panel==='help'){pan.append(el('h2','','Help'));pan.append(el('p','sl-note',"Normal: 1 ticket per draw; ×10/20/50 cost 8/16/40. The lever changes the quantity. Normal awards Coupons and Slot Points. High Stakes uses chips; ×10 requires VIP 3. Rewards reset daily; Refresh is free every 3 hours, otherwise costs 50 Gems (Normal) or 100 (High Stakes). Skip bypasses the animation and is saved per mode."));}
   else{pan.append(el('h2','','Record'));for(const row of s.board?.history||[]){const h=el('div','sl-history');h.append(el('p','',new Date(row.at*1000).toLocaleString('en-US')+' · '+row.times+" draw(s)"));const totals={...row.items};for(const [id,n]of Object.entries(row.bonus||{}))totals[id]=(totals[id]||0)+n;const g=el('div','sl-history-grid');for(const [id,n]of Object.entries(totals))icon(g,id,n);h.append(g);pan.append(h);}if(!s.board?.history?.length)pan.append(el('p','sl-note','No records yet.'));}
   stage.append(pan);}
  if(message){const status=el('p','sl-note sl-msg',message);status.setAttribute('role','status');stage.append(status);}
 }
 return {open,render};
})();
