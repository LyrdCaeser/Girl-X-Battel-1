'use strict';
// Home windows reconstructed from archived Lua routes and data tables.
const HomeMenus=(()=>{
 const titles={friends:"Bạn Bè",chat:'Trò Chuyện',mail:"Hòm Thư",book:'Sách Kỳ Ảo',servant:'Linh Thú',expedition:"Thám Hiểm",'starry-altar':'Cổng Vũ Trụ','luvly-castle':'Lâu Đài Luvly','drift-bottle':'Tin Nhắn Trôi Dạt',events:"Sự Kiện",giftpacks:'Gói Quà',treasure:'Quà Đặc Biệt'};
 const petNames={101:'Hunter',201:'Kraken',301:'Deerling',401:'Void',501:'Robert',601:'Elixir',701:'Flora',801:'Sea Serpent',901:'Crystal Golem'};
 let stack=[],catalog=null,root='friends',tab='',selected=null,origin='home',pending=false,message='',page=0,loaded=null,topupPackages=null,topupLoading=false;
 const el=(tag,text,cls)=>node(tag,cls,text),asset=name=>'/assets/home-systems/'+name+'.png';
 function image(name,cls='hm-art',alt=''){const img=el('img',undefined,cls);img.src=asset(name);img.alt=alt;return img;}
 function paragraph(parent,text,cls='hm-note'){parent.append(el('p',text,cls));}
 function button(parent,text,fn,disabled=false,cls=''){const b=el('button',text,cls);b.type='button';b.disabled=pending||disabled;b.addEventListener('click',fn);parent.append(b);return b;}
 function change(next,id=null){if(root==='chat'){chatRows=[];chatLoadedKey='';chatTyped='';chatError='';}tab=next;selected=id;message='';render();}
 function card(parent,title,icon){const c=el('article',undefined,'hm-card');if(icon&&catalog.assets.includes(icon))c.append(image(icon,'hm-card-icon'));c.append(el('h3',title));parent.append(c);return c;}
 function rewards(parent,text){const bar=el('div',undefined,'hm-rewards');for(const s of String(text||'').split('|')){if(!s.includes('#'))continue;const [id,num]=s.split('#'),label=el('span',undefined,'hm-reward');const icon=catalog.items[id]?.icon;if(catalog.assets.includes(icon))label.append(image(icon,'hm-item-icon'));label.append(el('span',number(num)),el('small',itemCatalog[id]?.name||({'1':"Vàng",'2':"Kim Cương",'26':'Đá Linh Thú','27':'EXP Kỹ Năng','117':'EXP Sách','203':'Bánh Mì','204':"Vật Liệu Xây Dựng",'205':"Vật Liệu Huấn Luyện",'221':'Xu Sách','222':"Vé Sách",'232':'Xu Lâu Đài','358':"Vé Vũ Trụ"}[id])||"Vật phẩm "+id));bar.append(label);}parent.append(bar);}
 function affordable(text){return String(text||'').split('|').every(p=>{const [id,n]=p.split('#');return !n||Number(state.items[id]||0)>=Number(n);});}
 function costButton(parent,label,text,request,disabled=false){const wrap=el('div',undefined,'hm-cost');if(text)rewards(wrap,text);button(wrap,label,()=>send(request),disabled||!affordable(text));parent.append(wrap);}
 async function send(request){if(pending)return;pending=true;message='Đang lưu…';render();try{const result=await api('/api/home/action',request);state=result.state;message="Đã lưu.";if(result.awards)message="Đã quay xong. Xem kết quả trong lịch sử.";}catch(e){message=e.message;}finally{pending=false;render();}}
 function navigation(parent,entries){const nav=el('nav',undefined,'hm-tabs');for(const [id,label]of entries)button(nav,label,()=>{page=0;change(id);},tab===id,'');parent.append(nav);}
 function link(parent,label,route){button(parent,label,()=>{if(route==='campaign'||route==='capsule'||route==='graduate')showView(route);else openMenu(route,'home-systems');});}
 function launch(key,from){if(key==='chat'){chatRows=[];chatLoadedKey='';chatRecipient='';chatTyped='';chatError='';}if(key==='friends')onlinePlayers=null;if(from==='home-systems'&&view==='home-systems')stack.push({root,tab,selected,page,origin});else stack=[];if(from!=='home-systems'||!stack.length)origin=from||'home';root=key;tab='';selected=null;page=0;message='';showView('home-systems');if(!catalog&&!loaded){loaded=api('/assets/home-systems/catalog.json').then(c=>{catalog=c;if(view==='home-systems')render();}).catch(e=>{message=e.message;loaded=null;render();});}}
 function back(){if(tab==='detail'||tab==='building'||tab==='adventure'||tab==='training'){change('');return;}if(stack.length){({root,tab,selected,page,origin}=stack.pop());message='';showView('home-systems');render();return;}showView(origin==='home-systems'?'home':origin);}
 function render(){const wrap=$('home-systems-view');if(!wrap||view!=='home-systems')return;wrap.replaceChildren();wrap.dataset.hmRoot=root;
  const top=el('header',undefined,'hm-top');const b=button(top,'',back);b.setAttribute('aria-label',"Back");b.append(image('mail_back_bg','hm-back'));b.replaceChildren();const arrow=el('img');arrow.src='/assets/ui/win_back_btn.png';arrow.alt='';b.append(arrow);top.append(el('h1',titles[root]));const money=el('div',undefined,'hm-money');money.append(el('span',"Vàng "+number(state.items['1'])),el('span',"Kim Cương "+number(state.items['2'])));top.append(money);wrap.append(top);
  const content=el('div',undefined,'hm-content');wrap.append(content);if(!catalog){paragraph(content,message||"Đang tải tài nguyên gốc…");return;}
  const status=el('p',message,'hm-status');status.setAttribute('role','status');wrap.append(status);
  if(root==='friends')friends(content);else if(root==='chat')chat(content);else if(root==='mail')mail(content);else if(root==='book')book(content);else if(root==='servant')servant(content);else if(root==='expedition')travel(content);else if(root==='starry-altar')cosmos(content);else if(root==='luvly-castle')castle(content);else if(root==='drift-bottle')drift(content);else if(root==='events')events(content);else gifts(content);
  const nav=el('nav',undefined,'hm-bottom');for(const [label,route]of[["Trang Chủ",'home'],["Nữ Thần",'girls'],["Túi Đồ",'bag'],["Triệu Hồi",'capsule']])button(nav,label,()=>showView(route));wrap.append(nav);
 }
 const info=()=>state.home_systems;
 async function heart(req){try{const r=await api('/api/hearts/action',req);state=r.state;if(r.got&&Object.keys(r.got).length&&typeof CampaignUI!=='undefined')CampaignUI.popup('Hearts',r.got);}catch(e){if(typeof GirlUI!=='undefined')GirlUI.toast(e.message);else console.error('Lỗi thao tác:',e);}render();}
 let onlinePlayers=null,onlinePlayersBusy=false;
 function loadRealPlayers(){
  if(onlinePlayersBusy)return;
  onlinePlayersBusy=true;
  api('/api/world/online?server_id='+encodeURIComponent(state?.server_id||'S1')).then(res=>{
   onlinePlayers=Array.isArray(res?.players)?res.players:[];
  }).catch(e=>{
   onlinePlayers=[];
   message=e.message||'Không thể tải người chơi trực tuyến.';
  }).finally(()=>{
   onlinePlayersBusy=false;
   if(view==='home-systems'&&root==='friends')render();
  });
 }
 function friends(parent){
  // Real server population only. Local contacts and recommended NPCs must never
  // masquerade as real online people or a successful friend request.
  if(!tab)tab='online';
  if(tab==='online'){
   const header=card(parent,'Người Chơi Trực Tuyến');
   const refresh=button(header,'Làm mới danh sách',()=>{onlinePlayers=null;loadRealPlayers();});
   refresh.disabled=onlinePlayersBusy;
   if(onlinePlayers===null){paragraph(parent,'Đang lấy danh sách người chơi từ máy chủ…');loadRealPlayers();}
   else if(!onlinePlayers.length)paragraph(parent,'Hiện không có người chơi nào được máy chủ xác nhận đang trực tuyến.');
   else for(const p of onlinePlayers){
    const row=el('div',undefined,'hm-rec');
    row.append(el('b',p.character_name||p.name||p.uid),el('small','Cấp '+(p.level||1)));
    parent.append(row);
   }
   paragraph(parent,'Danh sách này lấy trực tiếp từ máy chủ. Chức năng gửi lời mời kết bạn đang chờ kết nối; không tạo lời mời giả.');
   return;
  }
  if(!tab)tab='list';if(tab==='detail'){const c=info().contacts.find(c=>c.id===selected);if(!c){change('list');return;}const panel=card(parent,c.name);const avatar=el('img',undefined,'hm-avatar');avatar.src='/assets/profile/'+c.avatar+'.png';avatar.alt=c.name;panel.append(avatar);paragraph(panel,"Local contact for this save.");const form=el('form');const text=el('textarea');text.maxLength=500;text.placeholder="Message (local draft)";text.setAttribute('aria-label',"Message for "+c.name);form.append(text);button(form,"Save draft",()=>send({action:'draft',recipient:c.name,text:text.value}));panel.append(form);button(panel,"Delete contact",async()=>{await send({action:'contact_delete',id:c.id});change('list');});return;}
  const nav=el('nav',undefined,'hm-tabs');for(const [id,label]of [['list',"List"],['search',"Search"],['requests','Solicitudes'],['coop','Co-op']]){const b=button(nav,label,()=>{change(id);if(id==='coop')RemainingSystems.openFriendTab();},tab===id);b.setAttribute('aria-current',tab===id?'page':'false');}parent.append(nav);
  if(tab==='coop'){RemainingSystems.friendPanel(parent);return;}
  // Hearts (gxb2/hearts.py): one sent to and one claimed from each contact a day, "Claim & Send" for all
  {const hi=state.hearts_info||{held:0,max:1000,daily_max:30,sent:[],got:[],recommended:[]};const bar=el('div',undefined,'hm-hearts');const ic=el('img');ic.src=(typeof itemPicture==='function'&&itemCatalog?.['11']&&itemPicture(itemCatalog['11']))||'';ic.alt='';ic.onerror=()=>ic.remove();if(!ic.getAttribute('src'))ic.hidden=true;
   bar.append(ic,el('b',`Hearts ${number(hi.held)}/${hi.max}`),el('small',`Hoy: ${hi.got.length}/${hi.daily_max} reclamados · ${hi.sent.length} sent`));
   button(bar,'Claim & Send',()=>heart({action:'all'}),false).disabled=!info().contacts.length;parent.append(bar);}
  if(tab==='requests'){paragraph(parent,"No incoming requests.");return;}
  const grid=el('div',undefined,'hm-list');parent.append(grid);
  const draw=q=>{grid.replaceChildren();for(const c of info().contacts.filter(c=>c.name.toLocaleLowerCase().includes(q.toLocaleLowerCase()))){const row=card(grid,c.name);const img=el('img',undefined,'hm-avatar');img.src='/assets/profile/'+c.avatar+'.png';img.alt='';row.prepend(img);button(row,"View profile",()=>change('detail',c.id));const hi=state.hearts_info||{sent:[],got:[]};const sb=button(row,hi.sent.includes(c.id)?"Sent ♥":"Send ♥",()=>heart({action:'send',ids:[c.id]}));sb.disabled=hi.sent.includes(c.id);const gb=button(row,hi.got.includes(c.id)?'Reclamado':"Claim ♥",()=>heart({action:'claim',ids:[c.id]}));gb.disabled=hi.got.includes(c.id);}if(!grid.childElementCount)paragraph(grid,"No local contacts.");};
  if(tab==='search'){const rec=state.hearts_info?.recommended||[];if(rec.length){const rc=card(parent,'Recommended');for(const r of rec){const row=el('div',undefined,'hm-rec');row.append(el('b',r.name),el('small','Lv. '+r.lv));button(row,"Add",()=>heart({action:'add',rid:r.rid}));rc.append(row);}}const search=el('input');search.placeholder="Search contacts by name";search.setAttribute('aria-label',"Search contacts");search.addEventListener('input',()=>draw(search.value));parent.insertBefore(search,grid);const add=card(parent,"Add local contact");const name=el('input');name.maxLength=20;name.placeholder="Contact name";name.setAttribute('aria-label',"Contact name");add.append(name);button(add,"Add",()=>send({action:'contact_add',name:name.value,avatar:state.profile.avatar}));paragraph(add,"Saves a local entry; no request is sent to another person.");}draw('');
 }

 let chatRows=[],chatBusy=false,chatSending=false,chatLoadedKey='',chatRecipient='',chatTyped='',chatError='';
 // Poll only while the authenticated user is looking at the chat screen.
 // Messages are fetched from the real server; no synthetic players are generated.
 if(typeof window!=='undefined'&&typeof window.setInterval==='function'){
  window.setInterval(()=>{
   if(root==='chat'&&view==='home-systems'&&document.visibilityState!=='hidden'
      &&!chatBusy&&!chatSending)refreshRealChat(true);
  },6000);
 }
 const chatKey=()=>[state?.server_id||'',tab||'world',tab==='private'?chatRecipient:''].join(':');
 async function refreshRealChat(silent=false){
  if(chatBusy||root!=='chat'||view!=='home-systems')return;
  const key=chatKey();
  chatBusy=true;
  try{
   const url='/api/chat/messages?channel='+encodeURIComponent(tab||'world')
       +(tab==='private'&&chatRecipient?'&recipient_uid='+encodeURIComponent(chatRecipient):'');
   const response=await api(url);
   // An earlier response must not replace messages from a different tab/account.
   if(root!=='chat'||view!=='home-systems'||key!==chatKey())return;
   chatRows=Array.isArray(response?.messages)?response.messages:[];
   chatLoadedKey=key;chatError='';
   const focused=document.activeElement;
   if(!silent||!focused||!focused.closest?.('.hm-chat-composer'))render();
  }catch(e){
   chatError=e.message||'Không thể kết nối Trò Chuyện.';
   if(!silent&&root==='chat'&&view==='home-systems')render();
  }finally{chatBusy=false;}
 }
 async function submitRealChat(){
  const text=chatTyped.trim();
  if(chatSending||!text)return;
  if(tab==='private'&&!chatRecipient){chatError='Nhập UID người nhận để nhắn tin riêng.';render();return;}
  chatSending=true;
  try{
   await api('/api/chat/send',{channel:tab,message:text,recipient_uid:tab==='private'?chatRecipient:''});
   chatTyped='';chatError='';
   await refreshRealChat(false);
  }catch(e){chatError=e.message||'Máy chủ không nhận được tin nhắn.';render();}
  finally{chatSending=false;}
 }
 function chat(parent){
  if(!tab)tab='world';
  navigation(parent,[['world','Thế Giới'],['vietnamese','Tiếng Việt'],['english','Tiếng Anh'],['servers','Máy Chủ'],['recruit','Tuyển Thành Viên'],['private','Tin Riêng']]);
  paragraph(parent,'Trò chuyện trực tuyến trên máy chủ '+(state?.server_id||'S1')+'. Chỉ hiển thị tin nhắn từ tài khoản người chơi thật.');
  if(tab==='private'){
   const search=card(parent,'Trò Chuyện Riêng');
   const uid=el('input');uid.type='text';uid.maxLength=64;uid.autocomplete='off';
   uid.placeholder='Nhập UID người nhận (cùng máy chủ)';
   uid.setAttribute('aria-label','UID người nhận');
   uid.value=chatRecipient;search.append(uid);
   button(search,'Xem hội thoại',()=>{
    const target=uid.value.trim();
    if(target!==chatRecipient){chatRecipient=target;chatRows=[];chatLoadedKey='';}
    chatError='';chatTyped='';
    refreshRealChat();
   });
   paragraph(search,chatRecipient?'Đang xem cuộc trò chuyện với '+chatRecipient:'Chưa chọn người nhận: hiển thị lịch sử tin nhắn riêng của chính bạn.');
  }
  const key=chatKey(),messages=card(parent,'Tin Nhắn Thật · '+({world:'Thế Giới',vietnamese:'Tiếng Việt',english:'Tiếng Anh',servers:'Máy Chủ',recruit:'Tuyển Thành Viên',private:'Tin Riêng'}[tab]||tab));
  const feed=el('div',undefined,'hm-chat-feed');
  feed.setAttribute('aria-live','polite');
  if(chatLoadedKey!==key){
   paragraph(feed,chatBusy?'Đang tải tin nhắn…':'Đang kết nối máy chủ…');
   if(!chatBusy)refreshRealChat();
  }else if(!chatRows.length){
   paragraph(feed,'Chưa có tin nhắn thật trong kênh này.');
  }else for(const m of chatRows){
   const row=el('article',undefined,'hm-chat-message');
   if(m.uid===state?.uid)row.classList.add('is-mine');
   const heading=el('div',undefined,'hm-chat-message-head');
   heading.append(el('strong',m.character_name||m.uid));
   if(m.channel==='private')heading.append(el('small',' · '+(m.uid===state?.uid?'Gửi tới '+m.recipient_uid:m.uid)));
   if(m.created_at)heading.append(el('time',new Date(Number(m.created_at)*1000).toLocaleString('vi-VN')));
   row.append(heading,el('p',m.message));feed.append(row);
  }
  messages.append(feed);
  const tools=el('div',undefined,'hm-chat-tools');
  button(tools,'Làm mới',()=>refreshRealChat(false),chatBusy);
  messages.append(tools);
  const composer=el('div',undefined,'hm-chat-composer');
  const input=el('textarea');input.maxLength=280;input.rows=3;
  input.placeholder='Nhập tin nhắn (tối đa 280 ký tự)…';
  input.value=chatTyped;input.setAttribute('aria-label','Soạn tin nhắn');
  input.addEventListener('input',()=>{chatTyped=input.value;});
  input.addEventListener('keydown',e=>{
   if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();chatTyped=input.value;submitRealChat();}
  });
  composer.append(input);
  button(composer,chatSending?'Đang gửi…':'Gửi',()=>{chatTyped=input.value;submitRealChat();},chatSending||(tab==='private'&&!chatRecipient),'hm-chat-send');
  messages.append(composer);
  if(chatError)paragraph(parent,chatError,'hm-chat-error');
 }

 async function claimServerMail(mailId){
  if(pending)return;
  pending=true;message='';
  try{
   const result=await api('/api/mail/claim',{mail_id:mailId});
   if(result?.state)state=result.state;
   message='Đã nhận vật phẩm đính kèm.';
  }catch(e){message=e.message||'Không thể nhận thư.';}
  finally{pending=false;render();}
 }
 function serverMail(parent){
  const rows=Array.isArray(state?.mail_info)?state.mail_info:[];
  if(!rows.length)paragraph(parent,'Chưa có thư máy chủ.');
  for(const m of rows){
   const claimed=m.status==='claimed';
   const c=card(parent,m.title||'Thư Máy Chủ',claimed?'mail_sys02':'mail_gm01');
   if(m.created_at)paragraph(c,new Date(Number(m.created_at)*1000).toLocaleString('vi-VN'));
   if(m.body)paragraph(c,m.body,'hm-text');
   const items=Object.entries(m.attachments||{}).filter(([,count])=>Number(count)>0);
   if(items.length)rewards(c,items.map(([id,count])=>id+'#'+count).join('|'));
   if(m.status==='pending')button(c,'Nhận Đính Kèm',()=>claimServerMail(m.id),pending);
   else if(claimed)paragraph(c,'Đã nhận đính kèm.');
  }
 }
 function mail(parent){if(!tab)tab='server';if(tab==='server'){navigation(parent,[['server','Thư Máy Chủ'],['friend','Thư Bạn Bè'],['system','Thư Hệ Thống'],['gm','Thư QTV']]);serverMail(parent);return;}if(tab==='detail'){const m=info().mail.find(m=>m.id===selected);if(!m){change('system');return;}const c=card(parent,m.title,'mail_item');paragraph(c,m.text,'hm-text');rewards(c,m.awards);button(c,m.claimed?"Đã nhận đính kèm":"Nhận đính kèm",()=>send({action:'mail_claim',id:m.id}),m.claimed);button(c,"Xóa thư",async()=>{await send({action:'mail_delete',id:m.id});if(!info().mail.find(x=>x.id===m.id))change('system');},!!m.awards&&!m.claimed);return;}
  navigation(parent,[['server','Thư Máy Chủ'],['friend','Thư Bạn Bè'],['system','Thư Hệ Thống'],['gm','Thư QTV']]);
  const rows=info().mail.filter(m=>m.type===tab);if(!rows.length)paragraph(parent,"Hòm thư này chưa có thư.");
  for(const m of rows){const c=card(parent,(m.read?'':'● ')+m.title,tab==='gm'?'mail_gm01':tab==='system'?'mail_sys01':'mail_box');button(c,"Mở thư",async()=>{await send({action:'mail_read',id:m.id});change('detail',m.id);});}
  button(parent,"Nhận tất cả đính kèm",()=>send({action:'mail_claim_all'}),!info().mail.some(m=>!m.claimed));if(state.developer)button(parent,"Tạo thư thử nghiệm · QTV",()=>send({action:'mail_test'}));
 }
 function book(parent){if(!tab)tab='missions';parent.append(image('battle_pass_logo_new_en_en','hm-title-art','Fantasy Book'));navigation(parent,[['missions',"Nhiệm Vụ"],['rewards',"Phần Thưởng"],['shop',"Store"]]);paragraph(parent,"Nhiệm vụ ngày và tuần được đặt lại theo giờ UTC. Tiến độ được lưu trên tài khoản của bạn.");
  if(tab==='missions'){for(const m of info().missions){const c=card(parent,m.label);paragraph(c,(m.period===1?'Hằng Ngày':"Hằng Tuần")+' · '+m.progress+' / '+m.goal,'hm-progress');rewards(c,m.award+'|'+m.xp);button(c,m.claimed?'Đã nhận':"Nhận",()=>send({action:'book_mission',id:m.id}),m.claimed||m.progress<m.goal);link(c,'Đến',m.route);}const details=el('details');details.append(el('summary',"Nhiệm vụ khác"));for(const r of catalog.battlepass_mission.filter(r=>!info().missions.some(m=>m.id===Number(r.id)))){const label=catalog.battlepass_mission_text.find(t=>t.id===r.id)?.mission_des;paragraph(details,(label||"Nhiệm vụ "+r.id)+' · '+r.complete_value+" · đang hoàn thiện");}parent.append(details);}
  else if(tab==='rewards'){paragraph(parent,"EXP Sách Kỳ Ảo: "+number(state.items['117']));const rows=catalog.battlepass_award.slice(page*10,page*10+10);for(const r of rows){const c=card(parent,"Cấp "+r.id+' · '+number(r.cost_total)+' EXP');const claimed=info().book.tiers.includes(Number(r.id));rewards(c,r.free_award);button(c,claimed?"Đã nhận":"Nhận thưởng miễn phí",()=>send({action:'book_tier',id:Number(r.id)}),claimed||Number(state.items['117']||0)<Number(r.cost_total));const premium=el('details');premium.append(el('summary',"Thưởng cao cấp · xem trước"));rewards(premium,r.paid_award);paragraph(premium,"Quyền sở hữu Gói Cao Cấp phụ thuộc dữ liệu máy chủ.");c.append(premium);}button(parent,"Trang trước",()=>{page--;render();},page===0);button(parent,"Trang sau",()=>{page++;render();},page===4);}
  else for(const r of catalog.shop_battlepass){const c=card(parent,'Ưu đãi '+r.id);rewards(c,r.item);const used=info().book.shop[r.id]||0;paragraph(c,used+' / '+r.buy_time+' đã mua');costButton(c,"Mua",r.cost,{action:'book_shop',id:Number(r.id)},used>=Number(r.buy_time));}
 }
 function servant(parent){
  const pets=info().pet_details;
  if(tab==='detail'){const row=catalog.pet.find(r=>Number(r.id)===selected);if(!row){change('');return;}const p=pets[row.id];const scene=el('div',undefined,'hm-pet-scene');scene.style.backgroundImage=`url('${asset(row.pet_bg)}')`;scene.append(image(row.pet_avatar+(p?.grade||1),'hm-pet-big',petNames[row.id]));parent.append(scene);const c=card(parent,petNames[row.id]);
   if(!p){paragraph(c,"Activate this Servant to upgrade its levels and skills.");costButton(c,"Activate",row.active_cost,{action:'pet_activate',id:selected});return;}
   paragraph(c,"Level "+p.lv+' / '+p.cap+" · Evolution "+p.grade+' / '+row.max_grade,'hm-progress');costButton(c,"Level up",p.level_cost,{action:'pet_level',id:selected},!p.level_cost);costButton(c,"Evolve",p.grade_cost,{action:'pet_grade',id:selected},!p.grade_cost);button(c,info().selected_pet===selected?"Selected":"Select Servant",()=>send({action:'pet_select',id:selected}),info().selected_pet===selected);
   for(const s of p.skill_details){const skill=card(parent,'Habilidad '+s.slot+" · level "+s.lv+' / '+s.max,s.icon);paragraph(skill,s.open?(s.effect||"No upgrade acquired"):"Unlocks at evolution "+row['pas_tier'+s.slot]);costButton(skill,"Upgrade skill",s.cost,{action:'pet_skill',id:selected,slot:s.slot},!s.open||s.lv>=s.max);}
   paragraph(parent,"Upgrades are saved with the recovered costs. Servant battle animations and effects have not been restored yet.");return;
  }
  paragraph(parent,"Activate, upgrade, and evolve your Servants.");const grid=el('div',undefined,'hm-pet-grid');parent.append(grid);for(const row of catalog.pet){const p=pets[row.id],c=card(grid,petNames[row.id],row.pet_avatar+(p?.grade||1));paragraph(c,p?"Lv. "+p.lv+" · evolution "+p.grade:"Not activated");button(c,"View Servant",()=>change('detail',Number(row.id)));}rewards(parent,'26#'+(state.items['26']||0)+'|27#'+(state.items['27']||0));
 }
 function travel(parent){
  const labels=["Market","Wishing Tree","Food Truck","Training Room","Adventure"];
  if(tab==='building'){const b=info().buildings.find(b=>b.id===selected);const c=card(parent,labels[b.id-1]+" · Lv. "+b.lv,'explore_icon_'+b.id);paragraph(c,"Production: "+number(b.out)+" / day · storage "+number(b.stock)+' / '+number(b.cap),'hm-progress');rewards(c,b.item+'#'+b.stock);button(c,"Nhận",()=>send({action:'travel_collect',id:b.id}),b.stock===0);paragraph(c,"Production is calculated hourly, even with the browser closed. Next cycle: "+Math.ceil(b.wait/60)+' min.');costButton(c,"Upgrade building",b.cost,{action:'travel_upgrade',id:b.id},b.lv>=50);paragraph(c,"Total training levels limit building upgrades.");
   const form=card(parent,"Assign Girls · "+b.slots+" slots");const assigned=new Set(b.partners);for(const p of state.roster){const line=el('label',undefined,'hm-choice');const input=el('input');input.type='checkbox';input.value=p.partner_id;input.checked=assigned.has(p.partner_id);line.append(input,el('span',p.name+" · Lv. "+p.lv));form.append(line);}button(form,"Save assignment",()=>send({action:'travel_assign',id:b.id,partners:[...form.querySelectorAll('input:checked')].map(i=>Number(i.value))}));paragraph(form,"Odd slots increase production; even slots increase capacity. Each Girl can occupy one building.");return;
  }
  if(tab==='training'){paragraph(parent,"Training level: "+Object.values(info().travel.training).reduce((s,v)=>s+v,0));paragraph(parent,"Each discipline limits the others' progression. These upgrades do not affect the battle engine yet.");for(const r of catalog.travel_train){const lv=info().travel.training[r.id]||1,c=card(parent,["HP","Attack","Armor","Speed","Crit"][Number(r.id)-1]+" · Lv. "+lv+' / 30','explore_icon_'+(Number(r.id)+3));const base=r.base_cost.split('|'),grow=r.grow_cost.split('|');const cost=base.map((v,i)=>{const [id,n]=v.split('#');return id+'#'+(Number(n)+Number(grow[i])*(lv-1));}).join('|');costButton(c,"Train",cost,{action:'travel_train',id:Number(r.id)},lv>=30);}return;}
  if(tab==='adventure'){const c=card(parent,"Adventure",'explore_icon_5');paragraph(c,"All 10 levels, events, and chests have been recovered. The map and server sequence have not been restored; this screen shows their rules.");for(const r of catalog.travel_box){const box=card(parent,'Cofre '+r.id+' · '+Math.round(Number(r.time_consume)/60)+' min');rewards(box,r.award1);}return;}
  const scene=el('div',undefined,'hm-travel-map');scene.style.backgroundImage=`url('${asset('explore_main_bg')}')`;parent.append(scene);for(let i=0;i<5;i++){const b=button(scene,'',()=>change(i<3?'building':i===3?'training':'adventure',i+1),false,'hm-map-building');b.append(image(i===3?'travel_guide_4':'explore_icon_'+(i+1),'hm-map-art'),el('strong',labels[i]));}
  paragraph(parent,"Store, Wishing Tree, and Food Truck produce resources. Enter a building to start local production.");if(!state.home_systems.started_travel)button(parent,"Start production",()=>send({action:'travel_start'}));
 }
 function cosmos(parent){const s=info().cosmos;const hero=el('div',undefined,'hm-cosmos-scene');hero.style.backgroundImage=`url('${asset('starry_altar_bg')}')`;hero.append(image('starry_altar_en_en','hm-title-art','Cosmos Portal'));{const gv=document.createElement('button');gv.type='button';gv.className='hm-galaxy-entry';gv.textContent='Galaxy Voyage ›';gv.title='GalaxyStartWindow: Galaxy Voyage';gv.onclick=()=>openMenu('galaxy','home');hero.append(gv);}parent.append(hero);if(!tab)tab='summon';navigation(parent,[['summon',"Summon"],['rates',"Rates"],['history',"History"]]);
  if(tab==='summon'){const c=card(parent,"Choose mode");const mode=el('select');mode.setAttribute('aria-label',"Cosmos mode");mode.append(new Option("Selected Girl · 0.25%",'4'),new Option("Shards · guaranteed every 40 draws",'5'));mode.value=String(s.mode);const choice=el('select');choice.setAttribute('aria-label',"Target Girl");for(const id of catalog.starry_altar.find(r=>r.id==='4').optional_award.split('|'))choice.append(new Option(girlsCatalog.find(g=>g.id===Number(id))?.name||"Girl "+id,id));choice.value=String(s.choice);c.append(mode,choice);button(c,"Save choice",()=>send({action:'cosmos_select',mode:Number(mode.value),choice:Number(choice.value)}));if(s.mode===5)paragraph(c,"Guaranteed 10 Shards: "+s.count+' / 40 sorteos.');else {const id=s.choice;if(cardIds.has(id)){const img=el('img',undefined,'hm-cosmos-partner');img.src='/assets/cards/partner_card_'+id+'.png';img.alt=choice.selectedOptions[0]?.text;c.append(img);}}rewards(c,'358#'+(state.items['358']||0));costButton(c,"Summon ×1",'358#1',{action:'cosmos_draw',count:1});costButton(c,"Summon ×10",'358#10',{action:'cosmos_draw',count:10});paragraph(parent,"Local draw using archived pools and probabilities. This is not a live event.");}
  else if(tab==='rates'){paragraph(parent,"Shards ×5: 10%. Selected Girl: 0.25% in her mode. Other rewards use the original weighted pool. Shards mode also guarantees ×10 every 40 draws.");const total=catalog.dropbox.reduce((a,r)=>a+Number(r.weight),0);for(const r of catalog.dropbox){const c=card(parent,(Number(r.weight)/total*100).toFixed(3)+" % of the basic pool");rewards(c,r.item);}}
  else{if(!s.history.length)paragraph(parent,"No draws yet.");for(const r of s.history){const c=card(parent,new Date(r.at*1000).toLocaleString('en-US'));if(r.partner)paragraph(c,"Girl: "+(girlsCatalog.find(g=>g.id===r.partner)?.name||r.partner));for(const [id,n]of Object.entries(r.items))rewards(c,id+'#'+n);for(const [id,n]of Object.entries(r.bonus)){paragraph(c,"Guarantee");rewards(c,id+'#'+n);}}}
 }
 function castle(parent){const scene=el('div',undefined,'hm-archive-scene');scene.style.backgroundImage=`url('${asset('activity_lafuli_castle_bg')}')`;parent.append(scene);if(!tab)tab='map';navigation(parent,[['map','Castillo'],['rewards',"Prizes"],['shop',"Store"]]);paragraph(parent,"Archived event. The original event and wheel draws are inactive. The store accepts coins held in the local save.");
  if(tab==='map'){link(parent,'Adrift Message','drift-bottle');link(parent,"View events",'events');}else if(tab==='rewards')for(const r of catalog.activity_lafuli_award){const c=card(parent,r.point+" points");rewards(c,r.award);paragraph(c,"Archived event reward.");}else for(const r of catalog.activity_lafuli_shop){const c=card(parent,'Ưu đãi '+r.id);rewards(c,r.award);const used=info().castle_shop?.[r.id]||0;paragraph(c,used+' / '+r.limit+' đã mua');costButton(c,"Mua",r.cost,{action:'castle_shop',id:Number(r.id)},used>=Number(r.limit));}}
 function drift(parent){const scene=el('div',undefined,'hm-archive-scene');scene.style.backgroundImage=`url('${asset('activity_lafuli_drift_bg')}')`;parent.append(scene);paragraph(parent,"Recovered Adrift Message board: 21 spaces. Select one to inspect its rewards. Event movement and encounters have not been restored yet.");const board=el('div',undefined,'hm-drift-board');parent.append(board);for(const r of catalog.activity_lafuli_drift)button(board,r.id,()=>{selected=Number(r.id);render();},false,Number(r.id)===selected?'chosen':'');if(selected){const r=catalog.activity_lafuli_drift.find(r=>Number(r.id)===selected),c=card(parent,'Casilla '+r.id,r.icon_png);if(r.award.includes('#'))rewards(c,r.award);else paragraph(c,"Encounter or card choice");for(const n of [1,2,3])if(r['award'+n])rewards(c,r['award'+n]);paragraph(c,"Next: "+r.next_id+" · previous: "+r.back_id);}link(parent,"Back to the castle",'luvly-castle');}
 function events(parent){paragraph(parent,"Danh sách hoạt động gốc được giữ nguyên; một số lịch hoặc xếp hạng của máy chủ gốc hiện chưa có dữ liệu.");for(const [title,key,icon]of[['Daily Quiz','quiz',''],['Tests','tests',''],['Luvly’s Dream Castle','luvly-castle',''],['Adrift Message','drift-bottle','lafuli_drift_card'],['Cosmos Portal','starry-altar','starry_bg_jlxz_1']]){const c=card(parent,title,icon);link(c,'Vào',key);}}
 function loadTopupPackages(){
  if(topupPackages!==null||topupLoading)return;
  topupLoading=true;
  api('/api/payment/packages').then(out=>{
   topupPackages=Array.isArray(out?.packages)?out.packages:[];
  }).catch(e=>{
   topupPackages=[];
   message=e.message||'Không thể tải danh sách gói nạp.';
  }).finally(()=>{
   topupLoading=false;
   if(view==='home-systems'&&root==='giftpacks')render();
  });
 }
 function gifts(parent){
  // The original monthly/weekly cards and gift events own their artwork and
  // item previews. This is merely the game's shortcut to those native events.
  // Never render an invented generic payment catalog in their place.
  const offers=[
    {event:2,id:'MONTHLY_GIFT',name:'Gói Quà Hằng Tháng',icon:'monthly_giftbag'},
    {event:3,id:'WEEKLY_GIFT',name:'Gói Quà Hằng Tuần',icon:'weekly_giftbag'},
    {event:6,id:'MONTHLY_CARD',name:'Thẻ Tháng',icon:'activity_month_card'},
    {event:24,id:'WEEKLY_CARD',name:'Thẻ Tuần',icon:'mana_week_card'}
  ];
  const container=el('section',undefined,'hm-original-offers');
  for(const o of offers){
    const tile=el('article',undefined,'hm-card hm-original-offer');
    const picture=el('img',undefined,'hm-card-icon');
    picture.src='/assets/events/icon_'+o.icon+'.png';picture.alt=o.name;
    tile.append(picture,el('h3',o.name));
    paragraph(tile,'Gói nguyên bản của game · giữ nguyên hình và sự kiện.');
    button(tile,'Xem gói trong Sự Kiện',()=>{
      if(typeof EventsHub!=='undefined')EventsHub.openOriginalEvent(o.event,'home-systems');
    });
    const p=(topupPackages||[]).find(pack=>pack.id===o.id);
    if(p&&p.price_label)paragraph(tile,p.price_label);
    button(tile,'Zalo 0856848557 · Đặt gói',()=>{
      window.GxbPayment?.open(o.id,o.name+' · Sự Kiện #'+o.event);
    },!window.GxbPayment);
    container.append(tile);
  }
  parent.append(container);
  if(topupPackages===null)loadTopupPackages();
  paragraph(parent,'Không dùng giá cũ từ nhà phát hành. EXP VIP và vật phẩm chỉ được cấp khi đơn được QTV xác nhận và người chơi nhận thư.');
 }
 function openFriendsBoss(from){launch('friends',from);tab='coop';render();RemainingSystems.openFriendTab();}
 // Poll only while the player actually has the online chat window open.
 setInterval(()=>{
  if(root==='chat'&&view==='home-systems'&&catalog&&!chatBusy)refreshRealChat(true);
 },12000);
 return {openFriendsBoss,handles:key=>Object.hasOwn(titles,key),open:launch,render};
})();
