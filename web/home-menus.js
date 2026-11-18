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
 function rewards(parent,text){const bar=el('div',undefined,'hm-rewards');for(const s of String(text||'').split('|')){if(!s.includes('#'))continue;const [id,num]=s.split('#'),label=el('span',undefined,'hm-reward');const icon=catalog.items[id]?.icon;const original=itemCatalog?.[id];const nativePicture=original&&typeof itemPicture==='function'?itemPicture(original):'';if(id==='999999991'){const picture=el('img',undefined,'hm-item-icon');picture.src='/assets/events/check_in_pop_up_vip_level_bg.png';picture.alt='EXP VIP';label.append(picture);}else if(nativePicture){const pic=el('img',undefined,'hm-item-icon');pic.src=nativePicture;pic.alt=original?.name||'Vật phẩm';pic.loading='lazy';pic.onerror=()=>{pic.hidden=true;};label.append(pic);}else if(icon&&catalog.assets.includes(icon))label.append(image(icon,'hm-item-icon'));label.append(el('span',number(num)),el('small',id==='999999991'?'EXP VIP':itemCatalog[id]?.name||({'1':"Vàng",'2':"Kim Cương",'26':'Đá Linh Thú','27':'EXP Kỹ Năng','117':'EXP Sách','203':'Bánh Mì','204':"Vật Liệu Xây Dựng",'205':"Vật Liệu Huấn Luyện",'221':'Xu Sách','222':"Vé Sách",'232':'Xu Lâu Đài','358':"Vé Vũ Trụ"}[id])||"Vật phẩm "+id));bar.append(label);}parent.append(bar);}
 function affordable(text){return String(text||'').split('|').every(p=>{const [id,n]=p.split('#');return !n||Number(state.items[id]||0)>=Number(n);});}
 function costButton(parent,label,text,request,disabled=false){const wrap=el('div',undefined,'hm-cost');if(text)rewards(wrap,text);button(wrap,label,()=>send(request),disabled||!affordable(text));parent.append(wrap);}
 async function send(request){if(pending)return;pending=true;message='Đang lưu…';render();try{const result=await api('/api/home/action',request);state=result.state;message="Đã lưu.";if(result.awards)message="Đã quay xong. Xem kết quả trong lịch sử.";}catch(e){message=e.message;}finally{pending=false;render();}}
 function navigation(parent,entries){const nav=el('nav',undefined,'hm-tabs');for(const [id,label]of entries)button(nav,label,()=>{page=0;change(id);},tab===id,'');parent.append(nav);}
 function link(parent,label,route){button(parent,label,()=>{if(route==='campaign'||route==='capsule'||route==='graduate')showView(route);else openMenu(route,'home-systems');});}
 function launch(key,from){if(key==='giftpacks'&&typeof EventsHub!=='undefined'){EventsHub.openOriginalEvent(2,from||view);return;}if(key==='chat'){chatRows=[];chatLoadedKey='';chatRecipient='';chatTyped='';chatError='';}if(key==='friends')friendsData=null;if(key==='mail')mailLastRefresh=0;if(from==='home-systems'&&view==='home-systems')stack.push({root,tab,selected,page,origin});else stack=[];if(from!=='home-systems'||!stack.length)origin=from||'home';root=key;tab='';selected=null;page=0;message='';showView('home-systems');if(!catalog&&!loaded){loaded=api('/assets/home-systems/catalog.json').then(c=>{catalog=c;if(view==='home-systems')render();}).catch(e=>{message=e.message;loaded=null;render();});}}
 function back(){if(tab==='detail'||tab==='building'||tab==='adventure'||tab==='training'){change('');return;}if(stack.length){({root,tab,selected,page,origin}=stack.pop());message='';showView('home-systems');render();return;}showView(origin==='home-systems'?'home':origin);}
 function render(){const wrap=$('home-systems-view');if(!wrap||view!=='home-systems')return;wrap.replaceChildren();wrap.dataset.hmRoot=root;
  const top=el('header',undefined,'hm-top');const b=button(top,'',back);b.setAttribute('aria-label',"Back");b.append(image('mail_back_bg','hm-back'));b.replaceChildren();const arrow=el('img');arrow.src='/assets/ui/win_back_btn.png';arrow.alt='';b.append(arrow);top.append(el('h1',titles[root]));const money=el('div',undefined,'hm-money');money.append(el('span',"Vàng "+number(state.items['1'])),el('span',"Kim Cương "+number(state.items['2'])));top.append(money);wrap.append(top);
  const content=el('div',undefined,'hm-content');wrap.append(content);if(!catalog){paragraph(content,message||"Đang tải…");return;}
  const status=el('p',message,'hm-status');status.setAttribute('role','status');wrap.append(status);
  if(root==='friends')friends(content);else if(root==='chat')chat(content);else if(root==='mail')mail(content);else if(root==='book')book(content);else if(root==='servant')servant(content);else if(root==='expedition')travel(content);else if(root==='starry-altar')cosmos(content);else if(root==='luvly-castle')castle(content);else if(root==='drift-bottle')drift(content);else if(root==='events')events(content);else gifts(content);
  const nav=el('nav',undefined,'hm-bottom');for(const [label,route]of[["Trang Chủ",'home'],["Nữ Thần",'girls'],["Túi Đồ",'bag'],["Triệu Hồi",'capsule']])button(nav,label,()=>showView(route));wrap.append(nav);
 }
 const info=()=>state.home_systems;
 async function heart(req){try{const r=await api('/api/hearts/action',req);state=r.state;if(r.got&&Object.keys(r.got).length&&typeof CampaignUI!=='undefined')CampaignUI.popup('Hearts',r.got);}catch(e){if(typeof GirlUI!=='undefined')GirlUI.toast(e.message);else console.error('Lỗi thao tác:',e);}render();}
 let friendsData=null,friendsBusy=false;
 function friendAvatar(key){
  key=String(key||'head_1001');
  return typeof profileAsset==='function'?profileAsset(key):('/assets/avatar-hd/profile/'+key+'.webp?v=1.1.2');
 }
 function friendPresence(player){
  if(player.online)return 'Đang trực tuyến';
  const seen=Number(player.last_seen||0);if(!seen)return 'Chưa từng online';
  const seconds=Math.max(0,Math.floor(Math.max(Date.now()/1000,Number(state.server_time||0))-seen));
  if(seconds<60)return 'Online vừa xong';
  if(seconds<3600)return 'Online '+Math.floor(seconds/60)+' phút trước';
  if(seconds<86400)return 'Online '+Math.floor(seconds/3600)+' giờ trước';
  if(seconds<604800)return 'Online '+Math.floor(seconds/86400)+' ngày trước';
  return 'Online '+new Date(seen*1000).toLocaleDateString('vi-VN');
 }
 function loadFriends(){
  if(friendsBusy)return;friendsBusy=true;
  api('/api/friends').then(r=>{friendsData=r;message='';}).catch(e=>{friendsData={players:[]};message=e.message||'Không tải được danh sách Bạn Bè.';})
   .finally(()=>{friendsBusy=false;if(view==='home-systems'&&root==='friends')render();});
 }
 async function friendAct(action,target_uid){
  if(friendsBusy)return;friendsBusy=true;
  try{friendsData=await api('/api/friends/action',{action,target_uid});message='';}
  catch(e){message=e.message||'Không thực hiện được.';}
  finally{friendsBusy=false;render();}
 }
 async function friendGift(profile,refresh){
  const giftName=item=>window.GxbBagVi?.t(item.name)||item.name||('Vật phẩm '+item.id);
  const owned=(profile.gift_items||[]).filter(x=>Number(x.owned)>0)
   .sort((a,b)=>(a.kind==='currency'?-1:0)-(b.kind==='currency'?-1:0)||Number(b.quality)-Number(a.quality)||giftName(a).localeCompare(giftName(b),'vi'));
  if(!owned.length){GirlUI.toast('Túi Đồ chưa có vật phẩm hoặc tiền tệ được phép tặng.');return;}
  const {body,close}=GirlUI.win({title:'Tặng Vật Phẩm',cls:'hm-social-win',stack:true});
  body.append(el('p','Vật phẩm thường: còn '+profile.gift_left+'/10 trong 7 ngày. Tiền tệ: còn '+profile.currency_gift_left+'/3 lần trong 7 ngày. Rương, hộp, túi, Nữ Thần, vé và vật phẩm sự kiện không được phép tặng.','hm-social-note'));
  const search=el('input',undefined,'hm-gift-search');search.type='search';search.placeholder='Tìm vật phẩm…';search.setAttribute('aria-label','Tìm vật phẩm');
  const list=el('div',undefined,'hm-gift-list');body.append(search,list);
  let selected=owned[0];
  const qty=el('input',undefined,'hm-gift-qty');qty.type='number';qty.min='1';qty.value='1';
  const preview=el('b','', 'hm-gift-points');
  const controls=el('div',undefined,'hm-gift-controls');controls.append(el('label','Số lượng'),qty);body.append(controls,preview);
  const sendButton=button(body,'Tặng Vật Phẩm',async()=>{
   try{const out=await api('/api/friends/gift',{target_uid:profile.uid,item_id:selected.id,quantity:Number(qty.value)});
    state.items=out.sender_items;close();GirlUI.toast('Đã tặng quà · +'+number(out.affection_gained)+' Hảo Cảm');await refresh();
   }catch(e){GirlUI.toast(e.message);}
  },false,'hm-social-primary');
  const itemImage=item=>{
   const original=itemCatalog?.[item.id];let src='';
   if(original&&typeof itemPicture==='function')src=itemPicture(original);
   if(!src&&item.icon)src='/assets/item-icons/'+item.icon+'.png';
   return src||'/assets/ui/item_bg.png';
  };
  const sync=()=>{
   const currency=selected.kind==='currency';
   const allowance=currency?(Number(profile.currency_gift_left||0)>0?Number(selected.max_quantity||0):0):Number(profile.gift_left||0);
   const max=Math.max(0,Math.min(Number(selected.owned||0),allowance));
   qty.max=String(max);if(Number(qty.value)>max)qty.value=String(max);if(Number(qty.value)<1&&max>0)qty.value='1';
   const amount=Number(qty.value||0),divisor=Math.max(1,Number(selected.affection_divisor||1));
   const affection=currency?Math.max(1,Math.ceil(amount/divisor)):Number(selected.points||0)*amount;
   preview.textContent=giftName(selected)+' · '+(currency?'Còn '+number(profile.currency_gift_left)+'/3 lần · Giới hạn '+number(max)+' · ':'')+'Nhận +'+number(affection)+' Hảo Cảm';
   sendButton.disabled=max<1;
  };
  const drawList=()=>{
   list.replaceChildren();const keyword=search.value.trim().toLocaleLowerCase('vi');
   const visible=owned.filter(item=>!keyword||giftName(item).toLocaleLowerCase('vi').includes(keyword));
   for(const item of visible){
    const currency=item.kind==='currency',card=el('button',undefined,'hm-gift-item'+(item.id===selected.id?' active':''));
    card.type='button';const pic=el('img');pic.src=itemImage(item);pic.alt=giftName(item);pic.loading='lazy';pic.onerror=()=>{pic.onerror=null;pic.src='/assets/ui/item_bg.png';};
    const text=el('span');text.append(el('b',giftName(item)),el('small','Có '+number(item.owned)),el('em',currency?'Tối đa '+number(item.max_quantity)+'/lần':('+'+number(item.points)+' Hảo Cảm/món')));
    card.append(pic,text);card.onclick=()=>{selected=item;drawList();sync();};list.append(card);
   }
   if(!visible.length)list.append(el('p','Không tìm thấy vật phẩm.','hm-social-note'));
  };
  search.oninput=drawList;qty.oninput=sync;drawList();sync();
 }
 async function friendMarriage(profile,action,refresh){
  try{const out=await api('/api/friends/marriage',{target_uid:profile.uid,action});
   if(action==='accept'){
    const {body}=GirlUI.win({title:'Lễ Đường',cls:'hm-wedding-hall'});
    const couple=el('div',undefined,'hm-wedding-couple');
    const person=(avatar,name)=>{const p=el('div');const im=el('img');im.src=friendAvatar(avatar);im.onerror=()=>{im.onerror=null;im.src='/assets/profile/head_1001.png';};p.append(im,el('b',name));return p;};
    couple.append(person(state.profile?.avatar,state.name||'Học viên'),el('span','💍','hm-wedding-ring'),person(out.avatar,out.character_name));
    body.append(el('p','Chúc mừng hai người đã chính thức kết duyên!','hm-wedding-title'),couple,el('p','Oath Ring đã được sử dụng và ngày cưới đã lưu vào hồ sơ của cả hai người.','hm-social-note'));
   }else{GirlUI.toast(action==='propose'?'Đã gửi lời cầu hôn.':'Đã từ chối lời cầu hôn.');await refresh();}
  }catch(e){GirlUI.toast(e.message);}
 }
 async function friendDuel(profile,close){
  try{const out=await api('/api/friends/duel',{target_uid:profile.uid});close();await watchEventBattle(out,'home-systems','So Tài · '+profile.character_name);}
  catch(e){GirlUI.toast(e.message);}
 }
 async function openFriendProfile(player){
  let profile;
  try{profile=await api('/api/friends/profile?uid='+encodeURIComponent(player.uid));}
  catch(e){GirlUI.toast(e.message);return;}
  const draw=async()=>{profile=await api('/api/friends/profile?uid='+encodeURIComponent(player.uid));open(profile);};
  const open=p=>{
   document.querySelector('.hm-social-profile')?.closest('.gs-overlay')?.remove();
   const {body,close}=GirlUI.win({title:'Hồ Sơ Người Chơi',cls:'hm-social-profile'});
   const head=el('div',undefined,'hm-profile-head');const av=el('img',undefined,'hm-profile-avatar');av.src=friendAvatar(p.avatar);av.onerror=()=>{av.onerror=null;av.src='/assets/profile/head_1001.png';};
   const who=el('div');who.append(el('h3',p.character_name),el('p','Cấp '+p.level+' · Lực chiến '+number(p.power)),el('p','Hảo Cảm '+number(p.affection)+' / '+number(p.affection_required),'hm-affection'));head.append(av,who);body.append(head);
   body.append(el('h4','Đội Hình Chính','hm-profile-title'));const lineup=el('div',undefined,'hm-profile-lineup');
   for(const h of p.lineup||[]){const c=el('div',undefined,'hm-profile-girl');const im=el('img');const gid=typeof artId==='function'?artId(h.table_id):h.table_id;im.src='/assets/cards/partner_card_'+gid+'.png';im.onerror=()=>im.remove();c.append(im,el('b','Lv.'+h.lv),el('small','Vị trí '+h.pos));lineup.append(c);}
   if(!lineup.childElementCount)paragraph(lineup,'Người chơi chưa xếp đội hình.');body.append(lineup);
   const acts=el('div',undefined,'hm-profile-actions');button(acts,'So Tài',()=>friendDuel(p,close),!p.friend,'hm-social-primary');button(acts,'Tặng Vật Phẩm',()=>friendGift(p,draw),!p.friend||!(p.gift_items||[]).length);
   const marriage=p.marriage;
   if(marriage?.status==='married')button(acts,'💍 Đã Kết Hôn',()=>{},true);
   else if(marriage?.status==='pending'&&marriage.proposer_uid===p.uid){button(acts,'Đồng Ý Kết Hôn',()=>friendMarriage(p,'accept',draw),false,'hm-marriage');button(acts,'Từ Chối',()=>friendMarriage(p,'reject',draw));}
   else if(marriage?.status==='pending')button(acts,'Đang Chờ Trả Lời',()=>{},true);
   else button(acts,'Cầu Hôn · 1 Oath Ring',()=>friendMarriage(p,'propose',draw),!p.friend||p.affection<p.affection_required,'hm-marriage');
   body.append(acts,el('p','Điểm Hảo Cảm phụ thuộc từng món và giá trị của món đó. Cần đủ 12.000 Hảo Cảm và 1 Oath Ring để mở Lễ Đường.','hm-social-note'));
  };open(profile);
 }
 function friends(parent){
  if(!tab)tab='players';
  const nav=el('nav',undefined,'hm-tabs');
  for(const [id,label] of [['players','Tìm Bạn'],['friends','Bạn Bè'],['requests','Lời Mời'],['coop','Boss Bạn Bè']])
   button(nav,label,()=>{tab=id;if(id==='coop')RemainingSystems.openFriendTab();render();},tab===id);
  parent.append(nav);
  if(tab==='coop'){RemainingSystems.friendPanel(parent);return;}
  if(friendsData===null){paragraph(parent,'Đang tải danh sách người chơi…');loadFriends();return;}
  let rows=friendsData.players||[];
  if(tab==='friends')rows=rows.filter(p=>p.relation==='friend');
  else if(tab==='requests')rows=rows.filter(p=>p.relation==='incoming'||p.relation==='outgoing');
  const board=el('div',undefined,'hm-friend-board');parent.append(board);
  for(const p of rows){
   const row=el('article',undefined,'hm-friend-row');
   const avatar=el('button',undefined,'hm-friend-avatar-btn');avatar.type='button';avatar.title='Xem hồ sơ và đội hình';const face=el('img',undefined,'hm-friend-avatar');face.src=friendAvatar(p.avatar);face.onerror=()=>{face.onerror=null;face.src='/assets/profile/head_1001.png';};avatar.append(face);avatar.onclick=()=>openFriendProfile(p);
   const inf=el('button',undefined,'hm-friend-info hm-friend-profile-open');inf.type='button';inf.title='Xem hồ sơ và đội hình';
   inf.append(el('b',p.character_name||p.uid),el('small','Cấp '+(p.level||1)+' · Lực chiến '+number(p.power||0)),el('span',friendPresence(p),p.online?'hm-online':'hm-offline'));inf.onclick=()=>openFriendProfile(p);
   const actions=el('div',undefined,'hm-friend-actions');
   if(p.relation==='none')button(actions,'Kết Bạn',()=>friendAct('request',p.uid));
   else if(p.relation==='outgoing')button(actions,'Đã gửi lời mời',()=>{},false).disabled=true;
   else if(p.relation==='incoming'){button(actions,'Đồng Ý',()=>friendAct('accept',p.uid));button(actions,'Từ Chối',()=>friendAct('reject',p.uid));}
   else{button(actions,'Hồ Sơ',()=>openFriendProfile(p));button(actions,'Xóa Bạn',()=>friendAct('remove',p.uid));}
   row.append(avatar,inf,actions);board.append(row);
  }
  if(!rows.length)paragraph(board,tab==='friends'?'Chưa có bạn bè.':tab==='requests'?'Chưa có lời mời nào.':'Chưa có người chơi phù hợp.');
  const reload=button(parent,'Làm mới',()=>{friendsData=null;loadFriends();});reload.disabled=friendsBusy;
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
  paragraph(parent,'Trò chuyện tại '+(state?.server_id||'S1')+'.');
  if(tab==='private'){
   const search=card(parent,'Trò Chuyện Riêng');
   const uid=el('input');uid.type='text';uid.maxLength=64;uid.autocomplete='off';
   uid.placeholder='Nhập UID người nhận';
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
  const key=chatKey(),messages=card(parent,'Tin Nhắn · '+({world:'Thế Giới',vietnamese:'Tiếng Việt',english:'Tiếng Anh',servers:'Máy Chủ',recruit:'Tuyển Thành Viên',private:'Tin Riêng'}[tab]||tab));
  const feed=el('div',undefined,'hm-chat-feed');
  feed.setAttribute('aria-live','polite');
  if(chatLoadedKey!==key){
   paragraph(feed,chatBusy?'Đang tải tin nhắn…':'Đang kết nối…');
   if(!chatBusy)refreshRealChat();
  }else if(!chatRows.length){
   paragraph(feed,'Chưa có tin nhắn trong kênh này.');
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

 let mailRefreshBusy=false,mailLastRefresh=0,giftcodeBusy=false,giftcodeTyped='';
 const mailSignature=rows=>JSON.stringify((rows||[]).map(m=>[m.id,m.status,m.created_at,m.read]));
 async function refreshServerMail(silent=false){
  if(mailRefreshBusy||pending)return;
  const expectedUid=state?.uid,previous=mailSignature(state?.mail_info);let redraw=false;
  mailRefreshBusy=true;
  try{
   const result=await api('/api/mail');
   if(expectedUid!==state?.uid)return;
   const rows=Array.isArray(result?.mail_info)?result.mail_info:[];
   const changed=mailSignature(rows)!==previous;
   state={...state,mail_info:rows};mailLastRefresh=Date.now();if(window.GameAssistant)GameAssistant.updateHome();
   if(!silent)message='Hòm Thư đã được cập nhật.';
   redraw=!silent||changed;
  }catch(e){
   if(!silent){message=e.message||'Không thể làm mới Hòm Thư.';redraw=true;}
  }finally{mailRefreshBusy=false;if(redraw&&view==='home-systems'&&root==='mail'&&tab==='server')render();}
 }
 function openGiftcode(){
  window.open('/api/giftcode/sso/start','_blank','noopener');
 }
 async function redeemGiftcode(){
  const code=giftcodeTyped.trim().toUpperCase();
  if(giftcodeBusy)return;
  if(!/^[A-Z0-9_-]{6,40}$/.test(code)){message='Giftcode gồm 6–40 ký tự A–Z, số, _ hoặc -.';render();return;}
  giftcodeBusy=true;message='Đang đổi Giftcode…';render();
  try{
   const result=await api('/api/giftcode/redeem',{code});
   giftcodeTyped='';message=result?.message||'Đổi mã thành công! Quà đã được gửi vào Hòm Thư.';
   if(result?.state_changed)state=await api('/api/state');
   mailLastRefresh=0;await refreshServerMail(true);
  }catch(e){message=e.message||'Không thể đổi Giftcode.';}
  finally{giftcodeBusy=false;if(view==='home-systems'&&root==='mail'&&tab==='server')render();}
 }
 function revealS4Skins(prize){
  // Separate S4 Wish PHASE 2: unlock the original Limited skins with a
  // visible gacha reveal, not a static end-of-mail grid. All ownership was
  // committed in the S4 mail transaction before this client-only scene.
  if(state?.server_id!=='S4')return Promise.resolve();
  const valid=(prize.skin_ids||[]).map(Number).filter(Number.isSafeInteger);
  if(!valid.length)return Promise.resolve();
  const labels=new Map((prize.skin_details||[]).map(s=>[Number(s.id),String(s.name||'')]));
  const pageSize=6;
  const nameFor=id=>{
   const original=labels.get(id)||'Trang phục Limited';
   const translated=window.GxbBagVi?.t?.(original);
   return typeof translated==='string'&&translated.trim()?translated:original;
  };
  return new Promise(resolve=>{
   const root=window.GxbFrame?.root()||document.body;
   // Exclusively one S4 cinematic at a time, including after rapid claims.
   root.querySelector('.hm-s4-wish-overlay')?.remove();
   const overlay=el('div',undefined,'hm-s4-wish-overlay');
   const head=el('header',undefined,'hm-s4-wish-head');
   const heading=el('div');heading.append(
    el('strong','S4 • TRIỆU HỒI WISH','hm-s4-wish-title'),
    el('span','Trang Phục Nữ Thần Limited • Độc Quyền S4','hm-s4-wish-subtitle'));
   const progress=el('span','','hm-s4-wish-progress');
   head.append(heading,progress);
   const body=el('section',undefined,'hm-s4-wish-body');
   const portal=el('div',undefined,'hm-s4-wish-portal');
   const light=el('div',undefined,'hm-s4-wish-flare');
   const cards=el('div',undefined,'hm-s4-wish-cards');
   portal.append(light,cards);
   const instruction=el('p','Trang phục Limited đã được mở khóa vĩnh viễn tại S4.','hm-s4-wish-note');
   body.append(portal,instruction);
   const foot=el('footer',undefined,'hm-s4-wish-actions');
   const next=el('button','Triệu Hồi Tiếp','hm-s4-wish-next');
   const overview=el('button','Xem Tất Cả','hm-s4-wish-overview');
   const skip=el('button','Bỏ Qua','hm-s4-wish-skip');
   for(const btn of [next,overview,skip])btn.type='button';
   let offset=0,finished=false;
   const close=()=>{
    if(finished)return;finished=true;
    overlay.remove();resolve();
   };
   const cardFor=(sid,i,all=false)=>{
    const item=el('article',undefined,'hm-s4-wish-card');
    item.style.animationDelay=all?'0ms':(i*115)+'ms';
    const frame=el('div',undefined,'hm-s4-wish-card-frame');
    const art=el('img');art.src='/assets/skins/cards/'+sid+'.webp';
    art.alt='Trang phục '+nameFor(sid);
    art.loading=all&&i>=12?'lazy':'eager';
    art.onerror=()=>{art.onerror=null;art.src='/assets/skins/'+sid+'.png';};
    frame.append(art);
    const text=el('div',undefined,'hm-s4-wish-card-title');
    text.append(el('span',nameFor(sid)),el('small','Trang Phục Limited • Đã Sở Hữu'));
    item.append(frame,text);
    return item;
   };
   const draw=()=>{
    cards.replaceChildren();
    cards.classList.remove('all');
    const upto=Math.min(offset+pageSize,valid.length);
    valid.slice(offset,upto).forEach((id,i)=>cards.append(cardFor(id,i)));
    progress.textContent='Trang phục '+upto+' / '+valid.length;
    instruction.textContent='Wish đã mở khóa '+upto+' / '+valid.length+
     ' trang phục. Chạm “Triệu Hồi Tiếp” để xem lượt tiếp theo.';
    next.textContent=upto>=valid.length?'Xem Kết Quả':'Triệu Hồi Tiếp';
    next.focus({preventScroll:true});
   };
   const summary=()=>{
    cards.replaceChildren();cards.classList.add('all');
    valid.forEach((id,i)=>cards.append(cardFor(id,i,true)));
    progress.textContent='Đã nhận '+valid.length+' / '+valid.length;
    instruction.textContent='Hoàn tất! '+Number(prize.wish_count||0)+
     ' Nữ Thần Wish Limited 25★ · '+valid.length+' trang phục · '+
     Number(prize.outfit_total||0)+' món Outfit, chỉ tại S4.';
    next.textContent='Hoàn Tất';
    next.focus({preventScroll:true});
   };
   next.onclick=()=>{
    if(cards.classList.contains('all')){close();return;}
    if(offset+pageSize>=valid.length){summary();return;}
    offset+=pageSize;draw();
   };
   overview.onclick=summary;
   skip.onclick=summary; // Never suppress an already-granted skin.
   foot.append(next,overview,skip);
   overlay.append(head,body,foot);
   root.append(overlay);
   draw();
  });
 }
 async function revealS4Bundle(prize){
  if(!prize||state?.server_id!=='S4')return;
  const girls=(prize.goddesses||[]).map(g=>({
   table_id:Number(g.table_id),name:g.name,star:Number(g.stars)
  }));
  if(girls.length&&typeof SummonAnim!=='undefined'){
   try{await SummonAnim.play(26,girls,{s4:true});}
   catch(e){console.warn('Hiệu ứng Wish S4:',e);}
  }
  await revealS4Skins(prize);
 }
 async function claimServerMail(mailId){
  if(pending)return;
  pending=true;message='';
  let celebration=null;
  try{
   const result=await api('/api/mail/claim',{mail_id:mailId});
   if(result?.state)state=result.state;
   mailLastRefresh=Date.now();if(window.GameAssistant)GameAssistant.updateHome();
   celebration=result?.s4_rewards||null;
   message=celebration
     ? 'Quà độc quyền S4 đã được nhận. Đang mở hiệu ứng Wish!'
     : result?.attachments?.__s4_exclusive_key__
       ? 'Chúc mừng VIP 15! Chìa Khóa S4 đã mở khóa máy chủ S4 cho tài khoản.'
       : 'Đã nhận vật phẩm đính kèm.';
  }catch(e){message=e.message||'Không thể nhận thư.';}
  finally{pending=false;render();}
  if(celebration)await revealS4Bundle(celebration);
 }
 async function markServerMailRead(){
  const unread=(state?.mail_info||[]).some(m=>!m.read);
  if(!unread)return;
  try{
   const result=await api('/api/mail/read',{});
   if(Array.isArray(result?.mail_info))state={...state,mail_info:result.mail_info};
   if(window.GameAssistant)GameAssistant.updateHome();
   if(view==='home-systems'&&root==='mail'&&tab==='server')render();
  }catch(_){}
 }
 function serverMail(parent){
  const tools=el('div',undefined,'hm-mail-tools');
  const gift=el('div',undefined,'hm-giftcode-entry'),code=el('input');
  code.type='text';code.inputMode='text';code.maxLength=40;code.autocomplete='off';
  code.placeholder='Nhập mã Giftcode';code.setAttribute('aria-label','Nhập mã Giftcode');code.value=giftcodeTyped;
  code.addEventListener('input',()=>{giftcodeTyped=code.value.toUpperCase();});
  code.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();giftcodeTyped=code.value;redeemGiftcode();}});
  gift.append(code);button(gift,giftcodeBusy?'Đang đổi…':'Đổi mã',()=>{giftcodeTyped=code.value;redeemGiftcode();},giftcodeBusy);
  tools.append(gift);
  button(tools,'Mở trang Giftcode',openGiftcode);
  button(tools,mailRefreshBusy?'Đang làm mới…':'↻ Làm mới',()=>refreshServerMail(false),mailRefreshBusy);
  parent.append(tools);
  if(!mailRefreshBusy&&Date.now()-mailLastRefresh>4000)queueMicrotask(()=>refreshServerMail(true));
  const rows=Array.isArray(state?.mail_info)?state.mail_info:[];
  if(rows.some(m=>!m.read))queueMicrotask(markServerMailRead);
  if(!rows.length)paragraph(parent,'Chưa có thư máy chủ.');
  for(const m of rows){
   const claimed=m.status==='claimed';
   const c=card(parent,m.title||'Thư Máy Chủ',claimed?'mail_sys02':'mail_gm01');
   if(m.created_at)paragraph(c,new Date(Number(m.created_at)*1000).toLocaleString('vi-VN'));
   if(m.body)paragraph(c,m.body,'hm-text');
   if(m.attachments?.__s4_exclusive_key__){
     const preview=el('div',undefined,'hm-s4-key-preview');
     const img=el('img');img.src='/s4-exclusive-key.svg';
     img.alt='Chìa Khóa S4 • Độc Quyền';
     const detail=el('div');
     detail.append(el('strong','Chìa Khóa S4 • Độc Quyền ×1'),
       el('small','Mở khóa máy chủ S4 khi nhận • Vĩnh viễn • Không tiêu hao'),
       el('small','Chìa khóa nằm trong Túi Đồ → Vật phẩm sau khi nhận'));
     preview.append(img,detail);c.append(preview);
   }
   if(m.attachments?.__s4_exclusive_bundle__){
    const gift=el('div',undefined,'hm-s4-gift-preview');
    gift.append(el('b','★ S4 • QUÀ WISH LIMITED 25★'),el('small',
      '24 Nữ Thần Wish 25★ · Cấp 1 · Không trang bị'),
      el('small','76 trang phục Nữ Thần Limited · Trọn bộ Outfit'));
    c.append(gift);
   }
   const goddess=m.attachments?.__gxb3_goddess__;
   if(goddess&&/^\/assets\/(?:cards|characters|original-ui)\//.test(String(goddess.image||''))){
     const tile=el('div',undefined,'hm-goddess-gift'),face=el('img');face.src=goddess.image;face.alt=goddess.name||'Nữ Thần';face.loading='lazy';
     tile.append(face,el('b',String(goddess.name||'Nữ Thần')+' · '+Number(goddess.stars)+'★ · Lv '+Number(goddess.level)));
     if(goddess.max_red6)tile.append(el('small','Trọn bộ trang bị đỏ 6★'));
     if(goddess.max_stellar)tile.append(el('small','Lõi Tinh Tú tối đa'));
     c.append(tile);
   }
   const items=Object.entries(m.attachments||{}).filter(([id,count])=>/^[0-9]+$/.test(id)&&Number(count)>0);
   if(items.length)rewards(c,items.map(([id,count])=>id+'#'+count).join('|'));
   if(m.status==='pending')button(c,
     m.attachments?.__s4_exclusive_key__?'Nhận Chìa Khóa S4':
       m.attachments?.__s4_exclusive_bundle__?'Nhận Quà & Triệu Hồi Wish':'Nhận Đính Kèm',
     ()=>claimServerMail(m.id),pending);
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
  else if(tab==='rewards'){paragraph(parent,"EXP Sách Kỳ Ảo: "+number(state.items['117']));const rows=catalog.battlepass_award.slice(page*10,page*10+10);for(const r of rows){const c=card(parent,"Cấp "+r.id+' · '+number(r.cost_total)+' EXP');const claimed=info().book.tiers.includes(Number(r.id));rewards(c,r.free_award);button(c,claimed?"Đã nhận":"Nhận thưởng miễn phí",()=>send({action:'book_tier',id:Number(r.id)}),claimed||Number(state.items['117']||0)<Number(r.cost_total));const premium=el('details');premium.append(el('summary',"Thưởng cao cấp · xem trước"));rewards(premium,r.paid_award);paragraph(premium,"Gói Cao Cấp chưa được mở cho tài khoản này.");c.append(premium);}button(parent,"Trang trước",()=>{page--;render();},page===0);button(parent,"Trang sau",()=>{page++;render();},page===4);}
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
 function castle(parent){const scene=el('div',undefined,'hm-archive-scene');scene.style.backgroundImage=`url('${asset('activity_lafuli_castle_bg')}')`;parent.append(scene);if(!tab)tab='map';navigation(parent,[['map','Lâu Đài'],['rewards','Phần Thưởng'],['shop','Cửa Hàng']]);paragraph(parent,'Vòng quay của sự kiện hiện chưa mở. Bạn vẫn có thể dùng Xu Sự Kiện trong Cửa Hàng.');
  if(tab==='map'){link(parent,'Tin Nhắn Phiêu Lưu','drift-bottle');link(parent,'Xem sự kiện','events');}else if(tab==='rewards')for(const r of catalog.activity_lafuli_award){const c=card(parent,r.point+' điểm');rewards(c,r.award);paragraph(c,'Phần thưởng sự kiện.');}else for(const r of catalog.activity_lafuli_shop){const c=card(parent,'Ưu đãi '+r.id);rewards(c,r.award);const used=info().castle_shop?.[r.id]||0;paragraph(c,used+' / '+r.limit+' đã mua');costButton(c,'Mua',r.cost,{action:'castle_shop',id:Number(r.id)},used>=Number(r.limit));}}
 function drift(parent){const scene=el('div',undefined,'hm-archive-scene');scene.style.backgroundImage=`url('${asset('activity_lafuli_drift_bg')}')`;parent.append(scene);paragraph(parent,"Recovered Adrift Message board: 21 spaces. Select one to inspect its rewards. Event movement and encounters have not been restored yet.");const board=el('div',undefined,'hm-drift-board');parent.append(board);for(const r of catalog.activity_lafuli_drift)button(board,r.id,()=>{selected=Number(r.id);render();},false,Number(r.id)===selected?'chosen':'');if(selected){const r=catalog.activity_lafuli_drift.find(r=>Number(r.id)===selected),c=card(parent,'Casilla '+r.id,r.icon_png);if(r.award.includes('#'))rewards(c,r.award);else paragraph(c,"Encounter or card choice");for(const n of [1,2,3])if(r['award'+n])rewards(c,r['award'+n]);paragraph(c,"Next: "+r.next_id+" · previous: "+r.back_id);}link(parent,"Back to the castle",'luvly-castle');}
 function events(parent){paragraph(parent,"Chọn hoạt động bé muốn tham gia.");for(const [title,key,icon]of[['Daily Quiz','quiz',''],['Tests','tests',''],['Luvly’s Dream Castle','luvly-castle',''],['Adrift Message','drift-bottle','lafuli_drift_card'],['Cosmos Portal','starry-altar','starry_bg_jlxz_1']]){const c=card(parent,title,icon);link(c,'Vào',key);}}
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
    paragraph(tile,'Gói quà sự kiện.');
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
 function showFriendsTab(next='friends'){tab=next;render();}
 function openFriendsBoss(from){launch('friends',from);tab='coop';render();RemainingSystems.openFriendTab();}
 // Poll only while the matching online window is open.
 setInterval(()=>{
  if(root==='chat'&&view==='home-systems'&&catalog&&!chatBusy)refreshRealChat(true);
 },12000);
 return {showFriendsTab,openFriendsBoss,handles:key=>Object.hasOwn(titles,key),open:launch,render};
})();
