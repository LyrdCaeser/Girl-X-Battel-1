'use strict';
// Guild (LOCAL-060): create screen + Office / Cafeteria / Gym / Playground windows over the territory backdrop. Rules: gxb2/guild.py.
// Original: tables, costs, cooldowns, orders, bosses, window layouts. Local: NPC members, single-player guild. Prefix gd- / gd2-.
// Layout: every window is laid out on the 720×1280 canvas with the coordinates of its prefab (y up, centre 640): guild_window,
// guild_dininghall, guild_gym_window, guild_boss_window, guild_war_info_window. Sprites come from /assets/sprite/<name>.png.
const Guild=(()=>{
 let origin='home',tab='office',data=null,loading=null,busy=false,ticker=null,page=null,bossOpen=null,cafe='order',warTab=1,fx=null,skew=0,seen=null,form={name:'',flag:1,notice:''},note='';
 const KEYS={'guild-territory':'office','guild':'office','guild-search':'office','guild-create':'office','guild-hall':'office','guild-members':'office','guild-dining':'dining','guild-gym':'gym','guild-war':'war'};
 const A=n=>'/assets/guild/'+n+'.png',S=n=>'/assets/sprite/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis||busy;return b;};
 const fmt=n=>typeof number==='function'?number(Number(n)):String(n);
 const short=n=>{n=Number(n)||0;return n>=1e7?Math.floor(n/1e6)+'M':n>=1e5?Math.floor(n/1e3)+'K':String(n);};
 const pairs=t=>String(t||'').split('|').filter(s=>s.includes('#')).map(s=>s.split('#'));
 const T=(k,d='')=>data?.text?.[k]||d;
 const info=()=>state.guild_info;
 const toast=t=>{if(typeof GirlUI!=='undefined')GirlUI.toast(t);};
 function handles(key){return key in KEYS && typeof state!=='undefined' && !!state;}
 function root(){let r=$('guild-view');if(!r){r=el('section','guild-view');r.id='guild-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function open(key,from){return openOnline(key,from);}
  function name(id){id=String(id);return id==='4'?'Xu Bang Hội':id==='1'?"Vàng":id==='2'?"Kim Cương":id==='5'?'EXP Bang Hội':itemCatalog?.[id]?.name||data.names?.[id]||"Vật phẩm "+id;}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';if(id==='4')return '/assets/original-ui/guild-lab/coin.png';const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}return null;}
 function chip(id,n){const w=el('span','gd-chip');const s=icon(id);if(s)w.append(img(s));else w.append(el('em','',name(id)));w.append(el('b','',fmt(n)));w.title=name(id)+' × '+fmt(n);return w;}
 function chips(text,mult=1){const w=el('span','gd-chips');for(const [k,n] of pairs(text))w.append(chip(k,Math.floor(Number(n)*mult)));return w;}
 function item(id,n){const w=el('span','gd2-item');const s=icon(id);if(s)w.append(img(s));w.append(el('b','',short(n)));w.title=name(id)+' × '+fmt(n);return w;}
 async function act(req){if(busy)return null;busy=true;note='';try{const r=await api('/api/guild/action',req);state=r.state;if(r.got&&Object.keys(r.got).length)toast('+ '+Object.entries(r.got).map(([k,n])=>fmt(n)+' '+name(k)).join(' · '));return r;}catch(e){note=e.message;toast(e.message);return null;}finally{busy=false;if(view==='guild')render();}}
 const now=()=>Date.now()/1000+skew;
 const hms=s=>{s=Math.max(0,Math.ceil(s));return [Math.floor(s/3600),Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');};
 const close=()=>showView(origin==='guild'?'home':origin);
 function ask(text,yes){const {body,close:c}=GirlUI.win({title:'Tips',cls:'gd2-ask',stack:true});body.append(el('p','',text));const r=el('div','gd2-askrow');r.append(btn('gd2-btn white','Cancel',c),btn('gd2-btn blue','OK',()=>{c();yes();}));body.append(r);}
 function help(title,lines){const {body}=GirlUI.win({title,cls:'gd2-ask'});for(const l of lines)body.append(el('p','',l));}

 // ---- canvas helpers (prefab coordinates) ----
 const at=(e,x,y,w,h)=>{e.style.left=`calc(${360+x-w/2} * var(--u))`;e.style.top=`calc(${640-y-(h||0)/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;if(h!=null)e.style.height=`calc(${h} * var(--u))`;return e;};
 const put=(st,e,x,y,w,h)=>{st.append(at(e,x,y,w,h));return e;};
 const pic=(st,n,x,y,w,h,cls='')=>put(st,img(n.startsWith('/')?n:S(n),'gd2-abs '+cls),x,y,w,h);
 const box=(st,cls,x,y,w,h)=>put(st,el('div','gd2-abs '+cls),x,y,w,h);
 // text anchored like an NGUI label: 'l' = left edge at x, 'r' = right edge at x, 'c' = centred on x
 const text=(st,str,x,y,cls='',anchor='c',w=320)=>{const e=el('span','gd2-abs gd2-t '+anchor+' '+cls,str);return put(st,e,anchor==='l'?x+w/2:anchor==='r'?x-w/2:x,y,w,40);};
 const B=(st,kind,label,fn,x,y,w,h,dis=false)=>put(st,btn('gd2-abs gd2-btn '+kind,label,fn,dis),x,y,w,h);
 const until=(e,t)=>{e.dataset.until=String(t);e.textContent=hms(t-now());return e;};
 function tick(){let over=false;const n=now();root().querySelectorAll('[data-until]').forEach(e=>{const left=Number(e.dataset.until)-n;if(e.dataset.total){e.firstChild.style.width=Math.min(100,100*(1-left/Number(e.dataset.total)))+'%';e.lastChild.textContent=hms(left);}else e.textContent=e.dataset.days?dh(left):hms(left);if(left<=0)over=true;});if(over&&!busy)render();}
 const dh=s=>{s=Math.max(0,s);return Math.floor(s/86400)+'D '+Math.floor(s%86400/3600)+'H';};
 function stage(){const r=root();try{fx?.destroy?.();}catch{}fx=null;r.replaceChildren();const st=el('div','gd2-stage');r.append(st);const back=el('div','gd-backdrop');st.append(back);if(typeof GuildTerritory!=='undefined')GuildTerritory.paint(back,false);
  st.append(el('div','gd2-shade'));const top=at(el('div','gd2-top'),0,602,720,76);for(const id of ['1','2']){const c=el('span','gd2-res');c.append(img('/assets/currency/icon_'+id+'_small.png'),el('b','',short(state.items[id]||0)),el('i','','+'));top.append(c);}
  const bk=btn('gd2-back','',close);bk.disabled=false;bk.append(img('/assets/ui/win_back_btn.png'));top.append(bk);st.append(top);return st;}
 function frame(st,title,h,cy,helpFn,cx=309){box(st,'gd2-w21',0,cy,680,h);text(st,title,0,cy+h/2-25,'gd2-title');const c=put(st,btn('gd2-abs gd2-ib','',bossOpen?()=>{bossOpen=null;render();}:close),cx,cy+h/2-25,44,44);c.disabled=false;c.append(img(S('close_btn_2'),'gd2-x'));
  if(helpFn){const hb=put(st,btn('gd2-abs gd2-ib','',helpFn),-316,cy+h/2-20,52,52);hb.disabled=false;hb.append(img(S('help_2')));}}
 function tabs(st,labels,cur,y,w,pick){const n=labels.length;labels.forEach((l,i)=>{const side=i===0?'left':i===n-1?'right':'mid';const b=put(st,btn('gd2-abs gd2-nav '+side+(cur===i?' on':''),l,()=>pick(i)),(i-(n-1)/2)*w,y,w,48);b.disabled=false;});}
 function none(st,label,y){pic(st,'bp_none_bg',0,y+22,285,302);text(st,label,0,y-150,'gd2-none');}

 function render(){if(onlineMode){renderOnlineGuild();return;}if(view!=='guild'||!data)return;clearInterval(ticker);ticker=null;const g=info();if(seen!==state){seen=state;if(state.server_time)skew=state.server_time-Date.now()/1000;}
  if(!g||!g.unlocked){const b=el('div','gd-body');b.append(el('p','gd-lock',"Bang Hội mở khóa sau khi vượt qua ải Chiến Dịch "+(g?.unlock_stage||32)+"."));shell(b);return;}
  if(!g.has){createScreen(g);return;}
  const keep=root().querySelector('.gd2-scroll')?.scrollTop||0;const st=stage();({office,dining,gym,war})[tab](st,g);const sc=st.querySelector('.gd2-scroll');if(sc)sc.scrollTop=keep;
  if(st.querySelector('[data-until]'))ticker=setInterval(()=>{if(view==='guild')tick();else{clearInterval(ticker);ticker=null;}},1000);}

 // ---- create / locked (plain window) ----
 function shell(body){const r=root();r.replaceChildren();const back=el('div','gd-backdrop');r.append(back);if(typeof GuildTerritory!=='undefined')GuildTerritory.paint(back,false);
  const win=el('div','gd-win');r.append(win);const head=el('header','gd-head');const x=btn('gd-close','×',close);x.disabled=false;head.append(el('h2','',T('GUILD_TEXT12','Guild')),x);win.append(head);
  const res=el('div','gd-res');for(const id of ['4','2','1'])res.append(chip(id,state.items[id]||0));win.append(res);win.append(body);win.append(el('p','gd-note',note));return win;}
 function createScreen(g){const b=el('div','gd-body');b.append(el('h3','',T('GUILD_TEXT14','Create Guild')));
  const nm=el('input','gd-input');nm.placeholder=T('GUILD_TEXT62','3-12 characters');nm.maxLength=12;nm.value=form.name;nm.oninput=()=>{form.name=nm.value;};
  const nt=el('textarea','gd-input');nt.placeholder=T('GUILD_TEXT23','Guild Notice');nt.maxLength=100;nt.value=form.notice;nt.oninput=()=>{form.notice=nt.value;};
  const flags=el('div','gd-flags');for(const f of g.flags){const c=btn('gd-flagpick'+(form.flag===f?' on':''),'',()=>{form.flag=f;render();});c.append(img(A('guild_flag_'+f)));flags.append(c);}
  const cost=el('div','gd-cost');cost.append(el('span','',"Cost"),chips(g.create_cost));
  b.append(nm,nt,flags,cost,btn('gd-go',"Tạo Bang Hội",async()=>{const r=await act({action:'create',name:form.name,flag:form.flag,notice:form.notice});if(r)toast("Đã tạo Bang Hội!");}));
  b.append(el('small','gd-help',"Without a server, your Guild has simulated members who join daily, sign in daily, and level it up with you."));shell(b);}

 // ---- members (NPC members of gxb2/guild.py + the player as Leader) ----
 const botRows=()=>(state.bots_info?.ranks?.cafeteria?.rows||[]).filter(r=>r.bot);
 function avatar(i,me){const h=el('span','gd2-av');const rows=botRows();if(me||!rows.length||typeof Bots==='undefined'){if(typeof portrait==='function'&&state.roster?.[0])h.append(portrait(state.roster[0].table_id,74));}else h.append(Bots.avatar(rows[i%rows.length].avatar,74));return h;}
 function people(g){const out=[{me:true,name:state.name||'Senpai',level:state.level,job:3,online:true,power:0}];g.members.forEach((m,i)=>out.push({i,name:m.name,level:m.level,job:m.role==='deputy'?2:1,online:m.online,power:m.power,ago:1+(m.id*7)%23}));
  return out.sort((a,b)=>b.job-a.job);}
 const seen2=p=>p.online?T('GUILD_TEXT07','Online'):p.ago+' hrs ago';
 function memberRow(p){const r=el('div','gd2-mrow');r.append(avatar(p.i,p.me),el('span','gd2-mlv',String(p.level)),el('b','gd2-mname',p.name),el('small','gd2-mjob',T('GUILD_JOB'+p.job,p.job===3?'Leader':p.job===2?'Deputy Leader':'Members')),img(S('guild_war_fight'),'gd2-mwar'),el('span','gd2-mseen',seen2(p)));return r;}

 // ---- Office (guild_window.prefab) ----
 function office(st,g){frame(st,T('GUILD_WINDOW','Office'),963,0,()=>help('Office',["Sign In once per day: Guild Coins and Guild EXP.","Guild levels increase through Sign Ins and Gym bosses; each level allows more members.","Local: simulated members join one per day and sign in automatically."]));
  pic(st,'guild_bg03',0,278,668,306);box(st,'gd2-w24 gd2-veil',0,312,660,210);
  pic(st,A('guild_flag_'+g.flag),-216,336,107,116,'gd2-fit');text(st,g.name,-216,242,'gd2-gname');
  const rows=[[T('GUILD_ID_TIPS','ID:'),String(15200000+((g.created||0)%99999)),1],[T('GUILD_LANG_TIPS','Main Language:'),'English',0],[T('GUILD_NUM_TIPS','Member:'),(g.members.length+1)+'/'+g.capacity,1],[T('GUILD_OPEN_TYPE_LABEL','Verification:'),T('GUILD_OPEN_TYPE2','Auto Pass'),0],[T('GUILD_OPWER_LIMIT_LABEL','Power Limit:'),'0',1],[T('GUILD_POLICY_TIPS','Priority:'),T('GUILD_POLICY_TEXT2','EZ Game'),0]];
  rows.forEach(([k,v,blue],i)=>{const y=388-25*i;if(i%2===0)box(st,'gd2-strip',111.5,y,400,24);text(st,k,-85,y,'gd2-k','l');text(st,v,308,y,'gd2-v'+(blue?' blue':''),'r');});
  text(st,'Lv.'+g.level,-82,228,'gd2-glv','l',90);const bar=box(st,'gd2-exp',150,228,316,28);const f=el('i');f.style.width=(g.next_exp?Math.min(100,100*(g.exp-g.base_exp)/(g.next_exp-g.base_exp)):100)+'%';bar.append(f);bar.title=g.next_exp?fmt(g.exp)+' / '+fmt(g.next_exp)+' EXP':fmt(g.exp)+' EXP · MAX';
  const nt=box(st,'gd2-w14 gd2-notice',0,132,658,122);nt.textContent=g.notice||T('GUILD_TEXT01','Our leader is so lazy! No messages yet~');pic(st,'chat_transl',303,94,40,43);
  const lg=B(st,'white gd2-icobtn',T('LOG','LOG'),()=>logWin(g),-244,23,144,65);lg.prepend(img(S('guild_icon04')));lg.disabled=false;
  const ml=B(st,'white gd2-icobtn',T('MAIL_TEXT','Mail'),()=>toast("Guild Mail requires other players; there is no server."),-88,23,144,65);ml.prepend(img(S('guild_icon06')));ml.disabled=false;
  const sign=B(st,'blue',T('CHECKIN_TEXT04','Sign In'),()=>act({action:'checkin'}),212,23,210,65,g.checked_in);sign.title='+'+g.sign_in.exp+' Guild EXP';
  if(g.checked_in){const d=new Date();d.setHours(24,0,0,0);until(box(st,'gd2-bubble',212,65,140,42),d.getTime()/1000+skew);}else pic(st,'alert_icon',309,46,28,30);
  box(st,'gd2-w14',0,-203,660,363);const list=box(st,'gd2-scroll gd2-mlist',0,-203,660,355);for(const p of people(g))list.append(memberRow(p));
  const set=put(st,btn('gd2-abs gd2-ib','',()=>settings(g)),-290,-425,54,54);set.append(img(S('guild_icon08')));
  B(st,'blue',T('GUILD_TEXT02','Requests'),()=>{const {body}=GirlUI.win({title:T('GUILD_TEXT02','Requests'),cls:'gd2-ask'});body.append(img(S('bp_none_bg'),'gd2-noneimg'),el('p','',"No applications: simulated members join automatically (Auto Pass), one per day."));},-176,-428,144,66).disabled=false;
  B(st,'blue',T('GUILD_TEXT03','Members'),()=>membersWin(g),-20,-428,144,66).disabled=false;
  B(st,'blue',T('GUILD_TEXT04','Recruit'),()=>toast("Recruit posts an advertisement in server chat; without a server, members join automatically."),136,-428,144,66).disabled=false;
  const q=put(st,btn('gd2-abs gd2-ib','',()=>ask("Disband the Guild? Its level and orders will be lost. (As Leader, you cannot leave without disbanding.)",()=>act({action:'dissolve'}))),287,-428,62,65);q.append(img(S('guild_btn01')));}
 function logWin(g){const {body}=GirlUI.win({title:T('LOG','LOG'),cls:'gd2-ask'});if(!g.log.length)body.append(el('p','','—'));for(const l of g.log)body.append(el('p','gd2-logline',new Date(l.at*1000).toLocaleString()+' · '+l.text));}
 function membersWin(g){const {body}=GirlUI.win({title:T('GUILD_TEXT03','Members')+' '+(g.members.length+1)+'/'+g.capacity,cls:'gd2-ask gd2-memwin'});for(const p of people(g)){const r=memberRow(p);if(!p.me)r.querySelector('.gd2-mseen').textContent=short(p.power)+' PWR';body.append(r);}}
 function settings(g){const {body,close:c}=GirlUI.win({title:'Settings',cls:'gd2-ask'});const nm=el('input','gd-input');nm.value=g.name;nm.maxLength=12;const nt2=el('textarea','gd-input');nt2.value=g.notice;nt2.maxLength=100;
  const flags=el('div','gd-flags');let flag=g.flag;for(const f of data.flags){const b=btn('gd-flagpick'+(flag===f?' on':''),'',()=>{flag=f;flags.querySelectorAll('.gd-flagpick').forEach((x,i)=>x.classList.toggle('on',data.flags[i]===flag));});b.append(img(A('guild_flag_'+f)));flags.append(b);}
  body.append(el('small','',"Name (changing it costs 1,000 Gems)"),nm,el('small','','Notice'),nt2,flags,btn('gd2-btn blue','OK',async()=>{c();await act({action:'edit',name:nm.value,flag,notice:nt2.value});}));}

 // ---- Cafeteria (guild_dininghall.prefab): Order / Lv. Up / Rank ----
 function dining(st,g){const o=g.orders,m=g.mill;frame(st,T('GUILD_DININGHALL','Cafeteria'),896,0,()=>help('Cafeteria',["Get Order brings new orders every 12 h. Start begins them; Finished grants rewards when they are complete.","The arrow upgrades an order with Gems (more stars, better rewards).","Lv. Up: donate Gold to upgrade the Cafeteria for more orders and better returns."]));
  tabs(st,[T('ORDER','Order'),T('LEV_UP','Lv. Up'),T('RANK','Rank')],['order','lvup','rank'].indexOf(cafe),365,220,i=>{cafe=['order','lvup','rank'][i];render();});
  box(st,'gd2-w23',0,-54,660,764);
  if(!o.open){none(st,T('GUILD_TEXT48','Unlocks at Guild level {1}').replace('{1}',o.open_level),-54);return;}
  if(cafe==='rank'){const l=box(st,'gd2-scroll gd2-ranklist',0,-54,650,750);l.append(Bots.list('cafeteria'));return;}
  if(cafe==='lvup'){lvup(st,g);return;}
  const wait=o.refresh_at>now(),idle=o.list.map((od,i)=>[od,i]).filter(([od])=>!od.start);
  if(wait)until(text(st,'',-222,298,'gd2-count'),o.refresh_at);else text(st,T('ORDER_NUM','Order Amount: {1}').replace('{1}',o.list.length),-312,298,'gd2-k','l');
  B(st,'white gd2-sm',T('GET_ORDER','Get Order'),()=>act({action:'order_refresh'}),-222,249,190,60,wait);
  B(st,'white gd2-sm',T('GUILD_MEAL_TEXT1','Upgrade Order'),()=>{const ups=idle.filter(([od])=>od.up_cost);const total=ups.reduce((s,[od])=>s+Number(pairs(od.up_cost)[0]?.[1]||0),0);ask(T('UPGRADE_ORDER_TIPS','Upgrading order level will cost {1} Gems. Continue?').replace('{1}',total),async()=>{for(const [,i]of ups){const r=await act({action:'order_upgrade',slot:i});if(!r)break;}});},0,249,190,60,!idle.some(([od])=>od.up_cost));
  B(st,'white gd2-sm',T('GUILD_MEAL_TEXT2','Start Order'),async()=>{for(const [,i]of idle){const r=await act({action:'order_start',slot:i});if(!r)break;}},222,249,190,60,!idle.length);
  if(!o.list.length){none(st,T('NO_ORDERS','No orders'),-65);return;}
  const grid=box(st,'gd2-scroll gd2-orders',0,-111,660,630);o.list.forEach((od,i)=>grid.append(orderCard(od,i,m)));}
 function orderCard(od,i,m){const c=el('div','gd2-ocard');const left=od.start?od.ready_at-now():0,done=od.start&&left<=0;
  c.append(el('b','gd2-otime',T('HOUR','{1}H').replace('{1}',Math.round(od.time/3600))));
  if(!od.start&&od.up_cost){const up=btn('gd2-oup','',()=>ask(T('UPGRADE_ORDER_TIPS','Upgrading order level will cost {1} Gems. Continue?').replace('{1}',pairs(od.up_cost)[0][1]),()=>act({action:'order_upgrade',slot:i})));up.append(img(S('guild_arrow3')));c.append(up);}
  c.append(img(A(od.picture.replace(/_png$/,'')),'gd2-food'));const stars=el('div','gd2-ostars');for(let k=0;k<Math.max(1,Number(od.id)||1);k++)stars.append(img(S('partner_star_yellow')));c.append(stars,el('i','gd2-oline'));
  const aw=el('div','gd2-oaw');for(const [k,n]of pairs(od.awards))aw.append(item(k,Math.floor(Number(n)*m.factor/10000)));c.append(aw);
  if(!od.start)c.append(btn('gd2-btn white gd2-ostart',T('START','Start'),()=>act({action:'order_start',slot:i})));
  else if(done)c.append(btn('gd2-btn blue gd2-ostart',T('PUB_MISSION_COMPLETE','Finished'),()=>act({action:'order_complete',slot:i})));
  else{const pb=el('div','gd2-obar');pb.append(el('i'),el('small'));pb.dataset.until=String(od.ready_at);pb.dataset.total=String(od.time);pb.firstChild.style.width=Math.min(100,100*(1-left/od.time))+'%';pb.lastChild.textContent=hms(left);c.append(pb);}
  return c;}
 function building(st,x,lv){const row=data.mill?.[String(lv)];box(st,'gd2-bg09',x,-20.5,276,357);pic(st,'guild_bg11',x-46,17.5,92,100,'gd2-deco');pic(st,'guild_bg11',x+46,17.5,92,100,'gd2-deco flip');box(st,'gd2-bg07',x,127,166,30);text(st,'Lv.'+lv,x,127,'gd2-blv');
  pic(st,String(row?.picture||'guild_territory_icon05_png').replace(/_png$/,''),x,-11.5,153,187,'gd2-fit');put(st,el('i','gd2-abs gd2-oline'),x,-104,234,8);
  text(st,T('MILL_FACTOR','+ {1}% Order Yield').replace('%%','%').replace('{1}',Math.round((Number(row?.factor||10000)-10000)/100)),x,-137.5,'gd2-bdesc');text(st,T('ORDER_NUMS','{1} Orders').replace('{1}',row?.order_num??'-'),x,-163.5,'gd2-bdesc');}
 function lvup(st,g){const m=g.mill,base=Number(data.mill?.[String(m.level)]?.all_gold||0);const max=!m.next_gold;
  const res=put(st,el('span','gd2-abs gd2-res'),0,285,230,44);res.append(img('/assets/currency/icon_1_small.png'),el('b','',short(state.items['1']||0)));
  const bar=box(st,'gd2-upbar',0,211,634,40);const f=el('i');f.style.width=(max?100:Math.min(100,100*(m.gold-base)/(m.next_gold-base)))+'%';bar.append(f,img('/assets/currency/icon_1_small.png'),el('b','',max?'MAX':short(m.gold-base)+'/'+short(m.next_gold-base)));
  if(max){building(st,0,m.level);pic(st,A('guild_level_max_en_en'),0,-209,220,60,'gd2-fit');}
  else{building(st,-185,m.level);pic(st,'summon_special_hero_gift_icon01',0,-18,70,42);building(st,185,m.level+1);}
  String(m.donate).split('|').forEach((p,i)=>{const [k,n]=p.split('#');const x=i?185:-185;const c=box(st,'gd2-cost',x,-246,200,38);c.append(img(icon(k)),el('b','',short(n)));
   B(st,'blue',T(i?'DONATE_TEN':'DONATE_ONE',i?'Donate*10':'Donate*1'),()=>act({action:'donate',index:i}),x,-320,262,66,max||Number(state.items[k]||0)<Number(n));});}

 // ---- Gym (guild_gym_window.prefab): 9 boss cards a page; the current boss opens guild_boss_window ----
 function bossCard(st,bs,bo,x,y,click){const cleared=bo.cleared.includes(bs.id),locked=bs.id>bo.current,cur=bs.id===bo.current&&!cleared;
  const c=put(st,btn('gd2-abs gd2-card'+(cleared?' cleared':locked?' locked':cur?' cur':''),'',click),x,y,156,240);c.disabled=false;
  c.append(img(locked?S('guild_boss_card_close'):'/assets/guild/boss/'+bs.show+'.png','gd2-cardart'),el('i','gd2-cardframe'),el('b','gd2-cardid',String(bs.id)));
  if(cleared)c.append(img(A('guild_boss_clear_en_en'),'gd2-finish'));
  if(cur){c.append(img(S('guild_boss_lace'),'gd2-lace l'),img(S('guild_boss_lace'),'gd2-lace r'));const sw=el('span','gd2-swords');sw.append(img(S('guild_war_fight')));c.append(sw);swords(c,sw);
   if(bo.cost===null&&bo.fight_at>now()){const t=el('span','gd2-cardtime');until(t,bo.fight_at);c.append(t);}}
  return c;}
 function swords(card,fallback){if(typeof GxbSpine==='undefined')return;const host=el('span','gd2-jian');card.append(host);GxbSpine.mount(host,'/assets/spine/jianxg',{width:284,height:450,scale:1.55,origin:[.5,.5],sequence:[['texiao1',true]]}).then(h=>{if(!host.isConnected){h.destroy();return;}fx=h;fallback.remove();}).catch(()=>host.remove());}
 function gym(st,g){const bo=g.boss;if(bossOpen){bossWin(st,g,data.bosses.find(x=>x.id===bossOpen));return;}
  const per=9,pages=Math.ceil(bo.max/per);if(page===null)page=Math.min(pages-1,Math.floor((Math.min(bo.current,bo.max)-1)/per));
  frame(st,T('GUILD_GYM_WINDOW','Gym'),912,0,null);box(st,'gd2-w14',0,-22,636,822);
  data.bosses.slice(page*per,page*per+per).forEach((bs,i)=>{if(bs.id>bo.max)return;bossCard(st,bs,bo,(i%3-1)*198,248-Math.floor(i/3)*255,()=>{if(bs.id>bo.current){toast("Defeat the previous boss first");return;}bossOpen=bs.id;render();});});
  const L=put(st,btn('gd2-abs gd2-arrow flip','',()=>{page--;render();},page<=0),-336,0,46,92);L.append(img(S('partner_detail_arrow')));const R=put(st,btn('gd2-abs gd2-arrow','',()=>{page++;render();},page>=pages-1),336,0,46,92);R.append(img(S('partner_detail_arrow')));
  for(let i=0;i<pages;i++)pic(st,i===page?'page_icon_1':'page_icon_0',(i-(pages-1)/2)*38,-410,i===page?22:16,i===page?22:16);}
 function bossWin(st,g,bs){const bo=g.boss,cleared=bo.cleared.includes(bs.id),cost=bo.cost;frame(st,T('GUILD_BOSS_WINDOW','Boss'),927,0,null,302);
  box(st,'gd2-w24',0,248.5,636,295);bossCard(st,bs,bo,-185,248.5,()=>{});
  text(st,'Boss '+bs.id+'  ·  Lv.'+bs.lv,-60,352.5,'gd2-bossid','l');
  const hp=box(st,'gd2-hp',102,287,324,28);const f=el('i');f.style.width=cleared?'0%':'100%';hp.append(f,el('b','',(cleared?'0':short(bs.hp))+' / '+short(bs.hp)));
  if(cost===null)until(text(st,'',102,208.5,'gd2-count'),bo.fight_at);else text(st,T('GUILD_BOSS_TEXT01','Chances:{1}').replace('{1}',Math.max(0,4-bo.fights)),102,208.5,'gd2-k');
  const gem=cost&&Object.values(cost)[0];const fb=B(st,'blue gd2-icobtn',gem?String(gem)+'  '+T('FIGHT3','Fight'):T('FIGHT3','Fight'),()=>fight(bs),102,161,210,65,cost===null);if(gem)fb.prepend(img('/assets/currency/icon_2_small.png'));
  const hb=put(st,btn('gd2-abs gd2-ib','',()=>help('Gym',["Each battle grants battle rewards; victory adds defeat rewards and Guild EXP (EXP from up to 5 wins per day).","4 battles per 16-hour cycle: the first 2 are free, then 40 and 80 Gems.","Local: battles are solo; simulated members do not attack the boss."])),179,340,52,52);hb.disabled=false;hb.append(img(S('help_2')));
  const ab=put(st,btn('gd2-abs gd2-ib','',()=>{const {body}=GirlUI.win({title:T('GUILD_WAR_AWARD','Rewards'),cls:'gd2-ask'});const r=(l,t)=>{const d=el('div','gd2-awrow');d.append(el('span','',l));for(const [k,n]of pairs(t))d.append(item(k,n));body.append(d);};r('Battle',bs.battle_awards);r('Kill',bs.kill_awards);body.append(el('p','','+'+bs.guild_exp+' Guild EXP'));}),238,340,52,52);ab.disabled=false;ab.append(img(S('btn_award')));
  text(st,T('DAMAGE_RANK','Damage rank:'),-315,86,'gd2-k','l');box(st,'gd2-w19',0,-192,634,501);
  if(!cleared){none(st,'No record yet',-192);return;}
  const row=box(st,'gd2-rankrow',0,6,604,96);row.append(img('/assets/arena/rank_icon01.png','gd2-rk'),avatar(0,true),el('span','gd2-mlv',String(state.level)),el('b','gd2-mname',state.name||'Senpai'),el('span','gd2-mseen',short(bs.hp)));}
 async function fight(bs){const r=await act({action:'boss_fight',boss:bs.id});if(!r)return;const label='Guild Boss '+bs.id;const got={...(r.got||{})};
  if(r.report&&typeof watchEventBattle==='function')await watchEventBattle({report:r.report,rewards:got},'guild',label);else if(typeof CampaignUI!=='undefined')CampaignUI.result(r.win,got,{event:true,label,report:r.report});
  if(r.win)bossOpen=null;if(view==='guild')render();}

 // ---- Playground (guild_war_info_window.prefab). LOCAL: there are no rival guilds, so this is the Rest Area only: the guild's
 // teams and the season clock. Registering needs a guild-war server and isn't rebuilt. ----
 function team(seed,lv){const list=(typeof girlsCatalog!=='undefined'?girlsCatalog.filter(x=>x.stars>=5):[]);const w=el('span','gd2-team');if(!list.length)return w;for(let k=0;k<6;k++){const g2=list[(seed*31+k*97+k*k*13)%list.length];const h=el('span','gd2-hero');h.append(portrait(g2.id,54),el('small','',String(lv)));w.append(h);}return w;}
 function war(st,g){const cy=13;frame(st,T('GUILD_WAR_INFO_WWINDOW','Playground'),1090,cy,()=>help('Playground',["Guild War matched your Guild's teams against other server Guilds each week.","Local: no rival Guilds. The Rest Area shows your Guild teams; Register and Competition Area require a server."]),302);
  tabs(st,[T('REST_ZONE','Rest Area'),T('MATCH_ZONE','Competition Area')],warTab-1,473,328,i=>{warTab=i+1;render();});
  if(warTab===2){box(st,'gd2-w23',0,-45,660,970);none(st,T('GUILD_WAR_NO_MATCH_TEAM','No guild matched'),0);return;}
  box(st,'gd2-w27',0,77,660,716);pic(st,'force_icon',-290,402,57,60);text(st,'0',-255,402,'gd2-force','l');
  B(st,'blue',T('SET_FORMATION','Set Team'),()=>toast("Local: Guild teams belong to its simulated members."),238,398,166,58).disabled=false;
  const top3=g.members.slice().sort((a,b)=>b.power-a.power).slice(0,3);text(st,T('GUILD_TEAM','Guild Team')+' : 0/'+top3.length,-314,346.5,'gd2-k','l');
  const list=box(st,'gd2-scroll gd2-teams',0,12,658,586);top3.forEach(m=>{const r=el('div','gd2-trow');const i=g.members.indexOf(m);const av=avatar(i,false);av.append(el('small','',String(m.level)));const mag=btn('gd2-mag','',()=>toast(m.name+' · '+short(m.power)+' PWR'));mag.disabled=false;mag.append(img(S('guild_war_btn02')));r.append(av,el('b','gd2-tname',m.name),team(m.id,Math.min(330,m.level)),mag);list.append(r);});
  if(!top3.length)none(st,T('NO_TEAMS','No Team'),12);
  const by=-408;pic(st,'guild_war_bg08',0,by,658,252);pic(st,'guild_war_deco',-266,by+36,132,126);pic(st,'guild_war_deco',-134,by+36,132,126,'flip');pic(st,'guild_war_line',-200,by+36,92,10);
  text(st,T('POINT','Score'),-316,by-50,'gd2-k','l');text(st,'1000',-254,by-50,'gd2-v blue','l');text(st,T('TIME_TO_GUILD_WAR_0','Countdown'),-316,by-80,'gd2-k','l');
  const d=new Date();d.setHours(24,0,0,0);while(d.getDay()!==1)d.setDate(d.getDate()+1);const cd=text(st,'',-202,by-80,'gd2-count','l');cd.dataset.days='1';cd.dataset.until=String(d.getTime()/1000+skew);cd.textContent=dh(d.getTime()/1000+skew-now());
  const soon=()=>toast("Guild War requires rival Guilds: no server available (not restored yet).");
  [['guild_war_award',T('GUILD_WAR_AWARD','Rewards'),8],['guild_war_record',T('REOCRD','Record'),126],['guild_war_rank',T('CAMPAIGN_RANK','Rank'),244.1]].forEach(([s,l,x])=>{const b=put(st,btn('gd2-abs gd2-ib','',soon),x,by+31.4,77,77);b.disabled=false;b.append(img(S(s)));text(st,l,x,by-3.6,'gd2-icolabel');});
  const bell=put(st,btn('gd2-abs gd2-ib','',soon),-83,by-40,44,44);bell.disabled=false;bell.append(img(S('guild_war_btn04')));
  B(st,'blue',T('SIGN_UP','Register'),soon,46,by-55,172,69).disabled=false;B(st,'blue',T('MY_TEAM','My Team'),soon,230,by-55,172,69).disabled=false;}

 // Online guilds are real shared PostgreSQL entities. Use the original Guild
 // windows, backdrop and flags; never call the legacy NPC guild action API.
 let onlineMode=false,onlineData=null,onlineBusy=false,onlineSection='office',onlineWarDetail=null;
 const onlineText=(parent,tag,cls,txt)=>{const e=el(tag,cls,txt);parent.append(e);return e;};
 async function onlineRequest(url,payload){
  if(onlineBusy)return null;
  onlineBusy=true;
  try{const result=await api(url,payload);if(Number.isFinite(Number(result?.result?.sent)))toast('Đã gửi thư cho '+Number(result.result.sent)+' thành viên.');if(result?.result?.id&&url.includes('/world-guild/manage')&&payload?.action==='war')toast('Đã lên lịch Bang Chiến.');await loadOnlineGuild();return result;}
  catch(e){note=e.message||'Không thể kết nối Bang Hội';renderOnlineGuild();}
  finally{onlineBusy=false;}
 }
 async function loadOnlineGuild(){
  let timer;
  try{
    const timeout=new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error('Máy chủ Bang Hội phản hồi quá lâu. Vui lòng tải lại.')),20000);});
    onlineData=await Promise.race([api('/api/world-guild'),timeout]);
    note='';
  }catch(e){onlineData=null;note=e.message||'Bang Hội trực tuyến chưa sẵn sàng';}
  finally{clearTimeout(timer);}
  renderOnlineGuild();
 }
 async function openOnline(key,from){
  onlineMode=true;onlineSection=({ 'guild-search':'ranking','guild-members':'members','guild-create':'directory','guild-war':'wars','guild-dining':'cafeteria','guild-gym':'gym' })[key]||'office';onlineWarDetail=null;
  origin=(from&&from!=='guild')?from:view==='guild'?'home':view;
  root();showView('guild');renderOnlineGuild();await loadOnlineGuild();
 }
 async function loadOnlineWar(warId){
  try{onlineWarDetail=await api('/api/guild-war?war_id='+encodeURIComponent(warId));onlineSection='war-detail';note='';}
  catch(e){note=e.message||'Không tải được chi tiết Bang Chiến.';}
  renderOnlineGuild();
 }
 function onlineConfirm(text,yes,title='Xác nhận Bang Hội'){
  GirlUI.confirm(text,{title,ok:'Xác nhận',danger:true}).then(ok=>{if(ok)yes();});
 }
 function onlineHeading(parent,label){onlineText(parent,'h3','',''+label);}
 function onlinePanel(parent){const p=el('section','gd-online-panel');parent.append(p);return p;}

 function onlineButton(parent,label,fn,disabled=false){
  parent.append(btn('gd-go',label,fn,disabled));return parent.lastElementChild;
 }
 function renderOnlineGuild(){
  if(!onlineMode||view!=='guild')return;
  const b=el('div','gd-body'),d=onlineData;
  onlineText(b,'h3','','Bang Hội');
  if(!d){onlineText(b,'p','gd-help',note||'Đang tải dữ liệu Bang Hội từ máy chủ…');onlineButton(b,'Tải lại Bang Hội',()=>loadOnlineGuild());shell(b);return;}
  const nav=el('nav','gd-online-nav');
  const sections=[['office','Tổng Quan'],['members','Thành Viên'],['directory','Tìm Bang'],['cafeteria','Căng Tin'],['gym','Phòng Tập'],['ranking','Xếp Hạng'],['wars','Bang Chiến']];
  for(const [id,label] of sections){
   const tab=btn('gd-online-tab'+(onlineSection===id||onlineSection==='war-detail'&&id==='wars'?' on':''),label,()=>{onlineSection=id;onlineWarDetail=null;renderOnlineGuild();});tab.disabled=false;nav.append(tab);
  }
  b.append(nav);
  if(d.guild){
   const g=d.guild;
   if(onlineSection==='office'){
    const identity=el('div','gd-online-identity');identity.append(img(A('guild_flag_'+(Number(g.flag)||1))));
    const totalPower=(g.members||[]).reduce((sum,m)=>sum+Number(m.power||0),0);
    const summary=el('div');summary.append(el('h3','',g.name),el('p','',g.notice||'Chưa có thông báo Bang Hội.'),el('p','',`Cấp ${g.level} · ${g.member_count} thành viên · EXP ${fmt(g.exp)} · Tổng lực chiến ${fmt(totalPower)}`));
    identity.append(summary);b.append(identity);
    if(['leader','deputy'].includes(g.role)){
     const panel=onlinePanel(b),noticeInput=el('textarea','gd-input');noticeInput.placeholder='Thông báo Bang Hội';noticeInput.maxLength=180;noticeInput.value=g.notice||'';
     panel.append(el('label','gd-online-label','Thông báo Bang Hội'),noticeInput);
     onlineButton(panel,'Lưu thông báo',()=>onlineRequest('/api/world-guild/manage',{action:'notice',notice:noticeInput.value}));
     const mailTitle=el('input','gd-input');mailTitle.placeholder='Tiêu đề thư Bang Hội';mailTitle.maxLength=100;
     const mailBody=el('textarea','gd-input');mailBody.placeholder='Nội dung gửi đến hộp thư tất cả thành viên';mailBody.maxLength=1500;
     panel.append(el('label','gd-online-label','Gửi thư đến toàn Bang'),mailTitle,mailBody);
     onlineButton(panel,'Gửi thư Bang Hội',()=>{
      if(!mailTitle.value.trim()||!mailBody.value.trim()){toast('Nhập tiêu đề và nội dung thư trước.');return;}
      onlineConfirm(`Gửi thư này đến ${g.member_count} thành viên trong Bang Hội?`,()=>onlineRequest('/api/world-guild/manage',{action:'mail',title:mailTitle.value,body:mailBody.value}),'Xác nhận gửi thư');
     });
    }
    onlineHeading(b,'Bang Hội đang hoạt động');
    onlineText(b,'p','gd-help','Thành viên, trò chuyện, thư và chiến tranh đều lấy từ máy chủ PostgreSQL. Không hiển thị thành viên NPC.');
    onlineButton(b,'Xem danh sách thành viên',()=>{onlineSection='members';renderOnlineGuild();});
    onlineButton(b,'Xem Bang Chiến',()=>{onlineSection='wars';renderOnlineGuild();});
    if(g.role==='leader'&&Number(g.member_count)===1){onlineButton(b,'Giải tán Bang Hội',()=>onlineConfirm('Bang Hội chỉ còn mình bạn. Giải tán sẽ xóa Bang Hội này. Tiếp tục?',()=>onlineRequest('/api/world-guild/action',{action:'leave'}),'Giải tán Bang Hội'));}
    else if(g.role!=='leader'){onlineButton(b,'Rời Bang Hội',()=>onlineConfirm('Bạn chắc chắn muốn rời Bang Hội?',()=>onlineRequest('/api/world-guild/action',{action:'leave'}),'Rời Bang Hội'));}
    else onlineText(b,'p','gd-help','Bang Chủ cần chuyển quyền lãnh đạo trước khi rời hoặc giải tán Bang Hội có thành viên khác.');
   }else if(onlineSection==='members'){
    onlineHeading(b,`Thành Viên Thật · ${g.member_count}`);
    for(const m of g.members||[]){
     const row=el('div','gd-online-member'),meta=el('div','gd-online-member-meta');
     meta.append(el('b','',m.character_name),el('small','',`${m.role==='leader'?'Bang Chủ':m.role==='deputy'?'Phó Bang':'Thành Viên'} · LC ${fmt(m.power)} · Đóng góp ${fmt(m.contribution)}`));row.append(meta);
     if(m.role!=='leader'&&g.role==='leader'){
      row.append(btn('gd-go',m.role==='deputy'?'Hạ Phó Bang':'Bổ Nhiệm Phó Bang',()=>onlineRequest('/api/world-guild/manage',{action:'role',target_uid:m.uid,role:m.role==='deputy'?'member':'deputy'})));
      row.append(btn('gd-go','Chuyển Bang Chủ',()=>onlineConfirm(`Chuyển quyền Bang Chủ cho ${m.character_name}? Tài khoản của bạn sẽ trở thành Thành Viên.`,()=>onlineRequest('/api/world-guild/manage',{action:'transfer',target_uid:m.uid}),'Chuyển quyền Bang Chủ')));
     }
     if(m.role!=='leader'&&(g.role==='leader'||g.role==='deputy'&&(m.role!=='deputy'))){
      row.append(btn('gd-go','Mời rời Bang',()=>onlineConfirm(`Xóa ${m.character_name} khỏi Bang Hội?`,()=>onlineRequest('/api/world-guild/manage',{action:'kick',target_uid:m.uid}),'Xóa thành viên')));
     }
     b.append(row);
    }
    if(['leader','deputy'].includes(g.role)){
     onlineHeading(b,'Đơn Xin Gia Nhập');
     for(const a of d.applications||[]){
      const row=el('div','gd-online-member');row.append(el('b','',a.character_name),el('small','',`Lực chiến ${fmt(a.power)}`));
      row.append(btn('gd-go','Duyệt',()=>onlineRequest('/api/world-guild/manage',{action:'review',target_uid:a.uid,approve:true})));
      row.append(btn('gd-go','Từ chối',()=>onlineRequest('/api/world-guild/manage',{action:'review',target_uid:a.uid,approve:false})));
      b.append(row);
     }
     if(!(d.applications||[]).length)onlineText(b,'p','gd-help','Chưa có đơn xin gia nhập đang chờ.');
    }
    onlineHeading(b,'Trò Chuyện Bang Hội');
    const chatList=onlinePanel(b);for(const m of (d.chat||[]).slice(-50))onlineText(chatList,'p','gd-online-message',`${m.character_name}: ${m.message}`);
    const chat=el('input','gd-input');chat.placeholder='Tin nhắn Bang Hội';chat.maxLength=280;b.append(chat);
    onlineButton(b,'Gửi tin nhắn',()=>{if(chat.value.trim())onlineRequest('/api/world-guild/manage',{action:'chat',message:chat.value});});
   }else if(onlineSection==='directory'){
    onlineHeading(b,'Tạo Bang Hội');
    const form=onlinePanel(b),name=el('input','gd-input'),notice=el('textarea','gd-input');name.placeholder='Tên Bang Hội · 3–24 ký tự';name.maxLength=24;notice.placeholder='Thông báo Bang Hội';notice.maxLength=180;form.append(name,notice);
    onlineButton(form,'Tạo Bang Hội',()=>{if(name.value.trim().length<3){toast('Tên Bang Hội cần từ 3 đến 24 ký tự.');return;}onlineRequest('/api/world-guild/action',{action:'create',name:name.value,notice:notice.value});});
    onlineHeading(b,'Bang Hội Trên Máy Chủ');
    for(const guild of d.guilds||[]){
     const row=el('div','gd-online-member');row.append(el('b','',guild.name),el('small','',`Cấp ${guild.level} · ${guild.member_count} thành viên · EXP ${fmt(guild.exp)}`));
     row.append(btn('gd-go','Xin gia nhập',()=>onlineRequest('/api/world-guild/manage',{action:'apply',guild_id:guild.id})));
     b.append(row);
    }
    if(!(d.guilds||[]).length)onlineText(b,'p','gd-help','Chưa có Bang Hội nào trên máy chủ này.');
   }else if(onlineSection==='cafeteria'||onlineSection==='gym'){
    const cafeteria=onlineSection==='cafeteria';
    onlineHeading(b,cafeteria?'Căng Tin Bang Hội':'Phòng Tập Bang Hội');
    onlineText(b,'p','gd-help',cafeteria
      ?'Căng Tin gốc gồm Cối Xay, Đơn Hàng, nâng cấp đơn và nhận thưởng. Phần này chưa được chuyển sang trạng thái dùng chung trên PostgreSQL, nên đang tạm khóa để không dùng đơn hàng/NPC giả hoặc ghi tài nguyên sai.'
      :'Phòng Tập gốc gồm chuỗi Boss Bang Hội, giới hạn lượt, hồi lượt, chiến đấu bằng đội hình thật và thưởng theo kết quả. Phần này chưa được chuyển sang PostgreSQL, nên đang tạm khóa để không dùng tiến trình Boss cục bộ hoặc dữ liệu giả.');
    onlineText(b,'p','gd-help','Dữ liệu Bang Hội online hiện tại vẫn được giữ nguyên. Không có thao tác ghi tài nguyên hoặc tiến trình nào được thực hiện ở màn này.');
    onlineButton(b,'Quay lại Tổng Quan',()=>{onlineSection='office';renderOnlineGuild();});
   }else if(onlineSection==='ranking'){
    onlineHeading(b,'Xếp Hạng Bang Hội · '+(g.server_id||''));
    for(const r of d.ranking||[]){
     const row=el('div','gd-online-member');row.append(el('b','',`#${r.rank} · ${r.name}`),el('small','',`Cấp ${r.level} · ${r.member_count} thành viên · LC ${fmt(r.total_power)}`));b.append(row);
    }
    if(!(d.ranking||[]).length)onlineText(b,'p','gd-help','Chưa có dữ liệu xếp hạng Bang Hội.');
   }else if(onlineSection==='wars'){
    const ownWars=(d.wars||[]).filter(w=>Number(w.guild_a)===Number(g.id)||Number(w.guild_b)===Number(g.id));
    onlineHeading(b,'Bang Chiến');
    if(['leader','deputy'].includes(g.role)){
     const opponents=(d.guilds||[]).filter(x=>Number(x.id)!==Number(g.id));
     if(opponents.length){
      const panel=onlinePanel(b),select=el('select','gd-input');
      for(const op of opponents){const option=el('option','',`${op.name} · Cấp ${op.level} · ${op.member_count} thành viên`);option.value=String(op.id);select.append(option);}
      panel.append(el('label','gd-online-label','Chọn Bang Hội đối thủ'),select);
      onlineButton(panel,'Thách Đấu Bang Hội',()=>onlineConfirm('Lên lịch Bang Chiến với Bang Hội đã chọn? Trận đấu dự kiến bắt đầu sau thời gian chuẩn bị của máy chủ.',()=>onlineRequest('/api/world-guild/manage',{action:'war',opponent_guild_id:Number(select.value),duration:86400}),'Xác nhận Bang Chiến'));
     }
    }
    for(const w of ownWars){
     const row=el('div','gd-online-member'),enemy=Number(w.guild_a)===Number(g.id)?w.guild_b_name:w.guild_a_name;
     row.append(el('b','',enemy),el('small','',`${w.status==='scheduled'?'Đã lên lịch':w.status==='active'?'Đang chiến đấu':w.status==='finished'?'Đã kết thúc':'Đã hủy'} · ${w.score_a} : ${w.score_b}`));
     row.append(btn('gd-go','Chi tiết',()=>loadOnlineWar(w.id)));b.append(row);
    }
    if(!ownWars.length)onlineText(b,'p','gd-help','Bang Hội chưa có trận Bang Chiến nào được ghi nhận.');
   }else if(onlineSection==='war-detail'&&onlineWarDetail){
    const detail=onlineWarDetail,war=detail.war;
    onlineHeading(b,`${war.guild_a_name} VS ${war.guild_b_name}`);
    onlineText(b,'p','gd-online-message',`Trạng thái: ${war.status==='active'?'Đang chiến đấu':war.status==='scheduled'?'Đã lên lịch':'Đã kết thúc'} · ${war.score_a} : ${war.score_b}`);
    onlineButton(b,'Quay lại Bang Chiến',()=>{onlineSection='wars';onlineWarDetail=null;renderOnlineGuild();});
    onlineHeading(b,'Đối Thủ Thật');
    for(const enemy of detail.enemies||[]){
     const row=el('div','gd-online-member');row.append(el('b','',enemy.character_name),el('small','',`LC ${fmt(enemy.power)} · ${enemy.role==='leader'?'Bang Chủ':enemy.role==='deputy'?'Phó Bang':'Thành Viên'}`));
     const already=(detail.battles||[]).some(x=>String(x.defender_uid)===String(enemy.uid));
     if(war.status==='active'&&!already)row.append(btn('gd-go','Tấn Công',async()=>{
      onlineConfirm(`Dùng đội hình đang lưu của bạn để chiến đấu với ${enemy.character_name}?`,async()=>{
       const result=await onlineRequest('/api/guild-war/battle',{war_id:war.id,defender_uid:enemy.uid});
       if(result?.result)toast(result.result.winner_uid?'Đã ghi nhận kết quả trận Bang Chiến.':'Trận đấu đã hoàn tất.');
       await loadOnlineWar(war.id);
      },'Xác nhận tấn công');
     }));
     else if(already)row.append(el('small','gd-online-note','Đã đấu cặp này'));
     b.append(row);
    }
    onlineHeading(b,'Lịch Sử Trận Đấu');
    for(const match of detail.battles||[])onlineText(b,'p','gd-online-message',`${match.attacker_uid===match.winner_uid?'Thắng':'Kết quả'} · ${fmt(match.score)} điểm · ${new Date(Number(match.created_at)*1000).toLocaleString()}`);
   }
  }else{
   onlineHeading(b,'Tạo Bang Hội');
   const form=onlinePanel(b),name=el('input','gd-input'),notice=el('textarea','gd-input');name.placeholder='Tên Bang Hội · 3–24 ký tự';name.maxLength=24;notice.placeholder='Thông báo Bang Hội';notice.maxLength=180;form.append(name,notice);
   onlineButton(form,'Tạo Bang Hội',()=>{if(name.value.trim().length<3){toast('Tên Bang Hội cần từ 3 đến 24 ký tự.');return;}onlineRequest('/api/world-guild/action',{action:'create',name:name.value,notice:notice.value});});
   onlineHeading(b,'Danh Sách Bang Hội');
   for(const guild of d.guilds||[]){
    const row=el('div','gd-online-member');row.append(el('b','',guild.name),el('small','',`Cấp ${guild.level} · ${guild.member_count} thành viên`));
    row.append(btn('gd-go','Xin gia nhập',()=>onlineRequest('/api/world-guild/manage',{action:'apply',guild_id:guild.id})));b.append(row);
   }
  }
  if(note)onlineText(b,'p','gd-note',note);
  shell(b);
 }

 return {handles,open,openOnline,render};
})();
