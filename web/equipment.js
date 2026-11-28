'use strict';
// Equipment UI: Gear tab of the girl sheet, real attributes (HeroAttr), Smithy forge and antique upgrade.
// Sources: PartnerDetailWindow.lua, SmithyWindow.lua (+ smithy_window.prefab), ArtifactUpWindow.lua.
const Equipment=(()=>{
 const ARTVI={
  'AI Teddy Staff':'Trượng Gấu Bông AI','Advance Magic Guide':'Sách Ma Thuật Cao Cấp',
  'Afterglow':'Dư Quang','Alarm Lamp':'Đèn Báo Động','Angel Twig':'Cành Thiên Sứ',
  'Axe of Snow':'Rìu Tuyết','Balance':'Cân Bằng','Baseball Bat':'Gậy Bóng Chày',
  'Beach Volleyball':'Bóng Chuyền Bãi Biển','Black Belt':'Đai Đen',
  'Black Magic Hat':'Mũ Hắc Thuật','Bow of Snow':'Cung Tuyết',
  'Brave Heart':'Trái Tim Dũng Cảm','Burning Blades':'Song Đao Rực Lửa',
  'Carnival Staff':'Trượng Lễ Hội','Cat Hood':'Mũ Trùm Mèo',
  'Chainblade Axe':'Rìu Xích Đao','Chalk':'Phấn Trắng',
  'Cherry Blossoms':'Hoa Anh Đào','Christmas Tree':'Cây Giáng Sinh',
  'Clover':'Cỏ Bốn Lá','Crossbow':'Nỏ','Cunning Lizard':'Thằn Lằn Tinh Ranh',
  'Dancing Mask':'Mặt Nạ Vũ Hội','Deception':'Lừa Dối',
  'Demonic Blade':'Ma Đao','Demonic Book':'Ma Thư','Demonic Wings':'Cánh Quỷ',
  'Dice of Destiny':'Xúc Xắc Định Mệnh','Dragon Teeth':'Nanh Rồng',
  'Echoes':'Dư Âm','Eternal Dawn':'Bình Minh Vĩnh Cửu','Evil Machete':'Ma Đao Cắt',
  'Fairy Crown':'Vương Miện Tinh Linh','Fate Cross':'Thánh Giá Định Mệnh',
  'Fate Crystal':'Pha Lê Định Mệnh','Fate Guide':'Sách Dẫn Lối Định Mệnh',
  'Fate Mirror':'Gương Định Mệnh','Fiery Qilin':'Kỳ Lân Lửa',
  'Flame Feather':'Lông Vũ Rực Lửa','Floating Jellyfish':'Sứa Trôi Nổi',
  'Fruit Cake':'Bánh Trái Cây','Fusion Umbrella':'Ô Dung Hợp',
  "Gabriel's Song":'Khúc Ca Gabriel','Galaxy Paintbrush':'Cọ Ngân Hà',
  "Geisha's Blessing":'Phúc Lành Geisha','Gentle Knight':'Kỵ Sĩ Dịu Dàng',
  'Ghostly Goat':'Dê Ma','Golden Cube':'Khối Lập Phương Vàng',
  'Guardian Gauntlet':'Găng Hộ Vệ','Heart Earring':'Hoa Tai Trái Tim',
  'Holy Grail':'Chén Thánh','Hosiery':'Vớ Dài','Invisible Cloak':'Áo Choàng Tàng Hình',
  'Judgment Sword':'Kiếm Phán Xét','Judo Headband':'Băng Đô Nhu Đạo',
  'Kagura Bell':'Chuông Kagura','Katana':'Kiếm Katana',
  'Key of Mind':'Chìa Khóa Tâm Trí','Key to Heaven':'Chìa Khóa Thiên Đường',
  'Kiss of Snow':'Nụ Hôn Tuyết','Lace Stockings':'Vớ Ren',
  'Leather Shoes':'Giày Da','Lighting Rune':'Phù Văn Ánh Sáng',
  'Lucky Goldfish':'Cá Vàng May Mắn','Magic Brick':'Gạch Phép Thuật',
  'Magic Guide Book':'Sách Chỉ Dẫn Ma Thuật','Magic Hat':'Mũ Phép Thuật',
  'Majestic Phoenix':'Phượng Hoàng Uy Nghi','Midnight Star':'Sao Nửa Đêm',
  'Muramasa':'Muramasa','Nebula Slasher':'Đao Tinh Vân',
  'Necronomicon':'Cấm Thư Necronomicon','Neutron Blades':'Lưỡi Đao Neutron',
  'Nightshade':'Bóng Đêm Độc','Nine-Tailed Fox':'Cáo Chín Đuôi',
  'Oil Tank':'Thùng Dầu','Opposite':'Đối Cực',
  'Peacock Tambourine':'Trống Lắc Khổng Tước',
  'Perception Watch':'Đồng Hồ Tri Giác','Poker Queen':'Nữ Hoàng Bài',
  'Power of Wind':'Sức Mạnh Gió','Punishment Sword':'Kiếm Trừng Phạt',
  "Queen's Crown":'Vương Miện Nữ Hoàng','Rage of Flame':'Cơn Thịnh Nộ Lửa',
  'Raven Scepter':'Quyền Trượng Quạ',"Reaper's Voice":'Tiếng Gọi Tử Thần',
  'Recovery All':'Hồi Phục Toàn Bộ','Rock Crab':'Cua Đá',
  'Sacred Handbell':'Chuông Tay Thần Thánh','Sacred Vial':'Lọ Thánh',
  'Samurai Helmet':'Mũ Samurai','Sand of Time':'Cát Thời Gian',
  'Seals Book':'Sách Phong Ấn','Secret Keys':'Chìa Khóa Bí Mật',
  'Silver Crown':'Vương Miện Bạc','Silver Mirage':'Ảo Ảnh Bạc',
  'Slingshot':'Ná','Snow Chime':'Chuông Tuyết','Snowball':'Quả Cầu Tuyết',
  'Soul Censer':'Lư Hương Linh Hồn','Soul Destruction':'Hủy Diệt Linh Hồn',
  'Soul Pendant':'Mặt Dây Chuyền Linh Hồn','Stinger':'Ngòi Độc',
  'Stool':'Ghế Đẩu','Super Potion':'Siêu Dược','Swiss Army Knife':'Dao Đa Năng',
  'The Wings of Icarus':'Đôi Cánh Icarus',"Thorn's Heart":'Trái Tim Gai',
  'Thunder Heart':'Trái Tim Sấm Sét','Tool of Trade':'Dụng Cụ Nghề Nghiệp',
  'Torch of Despair':'Đuốc Tuyệt Vọng','Universal Bag':'Túi Vạn Năng',
  "Warg's Bite":'Vết Cắn Sói Ma','Weaver Kitty':'Mèo Dệt Vải',
  'Windbringer':'Sứ Giả Gió','Witch Curse':'Lời Nguyền Phù Thủy',
  'Yume Lantern':'Đèn Lồng Yume'
 };
 const FCTVI={'Angel':'Ánh Sáng','Demon':'Bóng Tối','Fairy':'Tinh Linh','Ghost':'U Linh Ma','Human':'Nhân Tộc','Monster':'Ma Thú'};
 const ARTGROUPVI={'Demon Blood':'Máu Quỷ','Seal Sword':'Kiếm Phong Ấn','Sealed Heart':'Trái Tim Phong Ấn','Shackle of Pain':'Xiềng Xích Đau Đớn','Spike Shield':'Khiên Gai'};
 function antiqueName(raw){
  const name=String(raw||'');
  const stripped=name.replace(/ \(Test\)$/,'');
  if(ARTVI[stripped])return ARTVI[stripped]+(stripped!==name?' (Thử Nghiệm)':'');
  const [group,fac]=stripped.split('·');
  if(fac&&ARTGROUPVI[group]&&FCTVI[fac])return ARTGROUPVI[group]+' · '+FCTVI[fac];
  return name;
 }
 const ATTRVI={
  'DMG Dep.':'Giảm Sát Thương','Attack':'Tấn Công','Armor Brk':'Xuyên Giáp',
  'DMG vs Assassin':'Sát Thương lên Sát Thủ','Crit':'Bạo Kích','Crit DMG':'Sát Thương Bạo Kích',
  'DMG Red.':'Giảm Sát Thương','CC Immune':'Miễn Khống Chế',
  'DMG vs Mage':'Sát Thương lên Pháp Sư','Precision':'Chính Xác','HP':'Sinh Lực',
  'Block':'Chặn Đòn','DMG vs Priest':'Sát Thương lên Hỗ Trợ',
  'Skill DMG':'Sát Thương Kỹ Năng','Speed':'Tốc Độ','Holy Dmg':'Sát Thương Thánh',
  'Crit Resist':'Kháng Bạo Kích','Control Rate':'Tỷ Lệ Khống Chế',
  'DMG vs Ranger':'Sát Thương lên Xạ Thủ','DMG vs Warrior':'Sát Thương lên Chiến Binh'
 };
 const TREASURE_VI={'Blue Crystal':'Pha Lê Lam','Yellow Crystal':'Pha Lê Vàng','Agate Crystal':'Pha Lê Mã Não','Dragon Jade':'Ngọc Rồng','Nebula Core':'Lõi Tinh Vân','Paradise Crystal':'Pha Lê Thiên Đường','Rune Crystal':'Pha Lê Phù Văn'};
 const JOB_VI={1:'Chiến Binh',2:'Pháp Sư',3:'Xạ Thủ',4:'Sát Thủ',5:'Linh Mục'};
 const displayName=r=>r?.pos===5?(TREASURE_VI[r.name]||'Bảo Vật'):r?.pos===6?antiqueName(r.name):r?.name||'Trang bị';
 const treasureLevel=()=>state.server_id==='S5'?1:data.treasure_open_level;
 const SLOTS=[[1,'Vũ khí','partner_weapon'],[2,'Áo','partner_cloth'],[3,'Phụ kiện','partner_pants'],[4,'Giày','partner_shoes'],[5,'Bảo vật','partner_treasure'],[6,'Cổ vật','partner_artifact']];
 const SMITHY_TABS=[[1,'Vũ khí'],[2,'Áo'],[3,'Phụ kiện'],[4,'Giày']];
 const STAT_KEYS=[['hp','HP','attr_hp_icon'],['atk','ATK','attr_atk_icon'],['arm','DEF','attr_def_icon'],['spd','SPD','attr_spd_icon']];
 const EXTRA=['hit','crit','critTime','brk','miss','sklP','trueAtk','unCrit','decDmg','free','unfree','zs','fs','yx','ck','ms'];
 let data=null,loading=null,slot=1,pending=false,message='',attrCache={},attrKey='',smithyPos=1,smithyItem=null,smithyCount=1,feed={},artifactTarget=null,smithyBack='bag';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.loading='lazy';return i;};
 const fmt=n=>number(Math.round(Number(n)||0));
 const load=()=>data?Promise.resolve(data):(loading||=api('/assets/equipment/catalog.json').then(d=>{data=d;return d;}));
 const row=id=>data.items[String(id)];
 const have=id=>Number(state.items[String(id)]||0);
 function pairs(text){return String(text||'').split('|').filter(s=>s.includes('#')).map(s=>s.split('#'));}
 function attrText(key,value,localize=true){const original=data.attr_names[key]||key;const name=localize?(ATTRVI[original]||original):original;const v=Number(value);return name+' +'+(v<1&&v>0||key.endsWith('P')||['zs','fs','yx','ck','ms'].includes(key)?(v*100).toFixed(v*100%1?1:0)+'%':fmt(v));}
 function icon(id,extra=''){const r=row(id),w=el('span','eq-icon '+extra);w.style.backgroundImage=`url('/assets/ui/quality_${Math.min(r?.qlt||0,7)}.png')`;if(r)w.append(img(data.icons[String(id)]||'/assets/ui/item_bg.png','',r.name));if(r&&r.pos!==5&&r.star){const st=el('span','eq-stars');for(let i=0;i<Math.min(r.star,6);i++)st.append(img('/assets/equipment/equip_star.png'));w.append(st);}return w;}
 function lines(parent,id,partner,localize=true){const r=row(id);if(!r)return;const list=el('ul','eq-lines');for(const k of ['base1','base2','base3','base4'])for(const [a,v]of pairs(r[k]))list.append(el('li','',attrText(a,v,localize)));
  if(r.act){const ok=partner&&((r.job&&r.job===jobOf(partner))||(r.group&&r.group===groupOf(partner)));const li=el('li','eq-act'+(ok?' on':''),(r.job?'Nghề '+JOB_VI[r.job]:'Hệ '+r.group)+': '+pairs(r.act).map(([a,v])=>attrText(a,v)).join(', '));list.append(li);}
  if(r.form){const pieces=String(r.form).split('|').map(Number),worn=partner?pieces.filter(p=>partner.equips?.includes(p)).length:0;for(const [n,k]of [[2,'suit1'],[3,'suit2'],[4,'suit3']])if(r[k])list.append(el('li','eq-suit'+(worn>=n?' on':''),'Bộ trang bị '+n+'/4: '+pairs(r[k]).map(([a,v])=>attrText(a,v)).join(', ')));}
  if(r.suit_skill_names)list.append(el('li','eq-suit',"Kỹ năng bộ: "+r.suit_skill_names.join(' / ')));
  parent.append(list);}
 function jobOf(p){return Number(data.partner_jobs[String(p.table_id)]||0);}
 function groupOf(p){return Number(data.partner_groups[String(p.table_id)]||0);}
 function cost(parent,text,label){const c=el('span','eq-cost');for(const [id,n]of pairs(text)){const ok=have(id)>=Number(n);const s=el('span',ok?'':'short');const src=id==='1'?'/assets/equipment/icon_1.png':id==='2'?'/assets/currency/icon_2_small.png':itemIconSrc(id);if(src)s.append(img(src));s.append(el('b','',fmt(n)));s.title=(id==='14'?'Đục Pha Lê':id==='1'?'Vàng':itemCatalog[id]?.name||'Vật phẩm')+' · Sở hữu: '+fmt(have(id));c.append(s);}if(label)c.prepend(el('small','',label));parent.append(c);}
 function itemIconSrc(id){const it=itemCatalog[id];if(it&&itemIcons.has(it.icon))return '/assets/item-icons/'+it.icon+'.png';return data.icons[String(id)]||'';}
 function affordable(text){return pairs(text).every(([id,n])=>have(id)>=Number(n));}
 async function send(request,after){if(pending)return;pending=true;message='Đang lưu…';try{const r=await api('/api/equipment/action',request);state=r.state;message=after?after(r):'';}catch(e){message=e.message;}finally{pending=false;render();if(view==='detail'&&message&&typeof GirlUI!=='undefined')GirlUI.toast(message);}}
 function refresh(){if(view==='detail')renderGirlDetail();if(view==='smithy')renderSmithy();}
 function btn(parent,label,fn,disabled=false,cls='eq-btn'){const b=el('button',cls,label);b.type='button';b.disabled=pending||disabled;b.onclick=fn;parent.append(b);return b;}

 // ---- Gear tab (content_2 of partner_detail_window) ----
 // The board only: tapping a filled slot opens item_tips_window (Remove / Replace; the crystal: Exchange / Lv. Up;
 // antiques add Lv. Up), tapping an empty one opens choose_equip_window with the matching gear of the Bag.
 const SLOT_TITLE={1:'Vũ khí',2:'Áo',3:'Phụ kiện',4:'Giày',5:'Bảo Vật',6:'Cổ vật'};
 const W=o=>GirlUI.win(o);
 function gear(hero){const host=$('detail-gear');if(!host)return;for(const c of host.children)if(!c.classList.contains('eq-root'))c.hidden=true;let root=host.querySelector('.eq-root');if(!root){root=el('div','eq-root');host.append(root);}if(!data){root.replaceChildren(el('p','detail-note',"Đang tải trang bị…"));load().then(()=>view==='detail'&&renderGirlDetail());return;}
  const eq=(hero.equips||[]).concat([0,0,0,0,0,0,0]).slice(0,7);root.replaceChildren();
  const grid=el('div','eq-board');grid.append(img('/assets/detail/sheet/equip_bg.png','eq-board-bg'),img('/assets/detail/sheet/equip_bg.png','eq-board-bg flip'));
  for(const [s,,art]of SLOTS){const b=el('button','eq-slot s'+s);b.type='button';const id=eq[s-1];
   if(id&&row(id))b.append(icon(id));else{b.append(img('/assets/detail/sheet/item_icon_bg01.png','eq-empty-bg'),img('/assets/detail/sheet/'+art+'.png','eq-empty'));if(s===5?hero.lv>=treasureLevel():bagFor(s,hero).length)b.append(img('/assets/detail/sheet/icon_add.png','eq-plus'));}
   b.title=id&&row(id)?displayName(row(id)):SLOT_TITLE[s];b.onclick=()=>{slot=s;message='';if(id&&row(id))tip(hero,s,id);else if(s===5)treasureWin(hero,'unlock');else choose(hero,s);};grid.append(b);}
  const bar=el('div','eq-main-btns');btn(bar,'Tháo trang bị',()=>send({action:'unequip_all',partner_id:hero.partner_id}),![1,2,3,4,6].some(s=>eq[s-1]),'gs-btn red eq-big');btn(bar,'Trang bị tối ưu',()=>send({action:'equip_all',partner_id:hero.partner_id}),false,'gs-btn eq-big');grid.append(bar);
  root.append(grid);}
 function bagFor(s,hero){return Object.entries(state.items).filter(([id,n])=>Number(n)>0&&row(id)?.pos===s).map(([id,n])=>({id:Number(id),n:Number(n),r:row(id)})).sort((a,b)=>b.r.item_lv-a.r.item_lv||a.id-b.id);}
 // item_tips_window
 function tip(hero,s,id){const r=row(id);const {body,close}=W({title:SLOT_TITLE[s],cls:'eq-tip'});
  body.append(el('b','eq-tip-name',displayName(r)));const top=el('div','eq-tip-top');top.append(icon(id));body.append(top);lines(body,id,hero);
  const acts=el('div','gs-btns');
  if(s===5){
   acts.classList.add('eq-treasure-buttons');
   btn(acts,'Sửa Thuộc Tính',()=>{close();treasureWin(hero,'exchange');},false,'gs-btn');
   btn(acts,'Nâng cấp',()=>{close();treasureWin(hero,'up');},!r.treasure_upgrade,'gs-btn');
   if(state.server_id==='S5')btn(acts,'Chọn Bảo Vật Khác',()=>{close();chooseTreasure(hero);},false,'gs-btn eq-select-other');
  }
  else{btn(acts,'Tháo',()=>{close();send({action:'unequip',partner_id:hero.partner_id,slot:s});},false,'gs-btn red');
   if(s===6&&r.artifact_next)btn(acts,'Nâng cấp',()=>{close();openArtifact(id,hero.partner_id);},false,'gs-btn');
   btn(acts,'Thay thế',()=>{close();choose(hero,s);},!bagFor(s,hero).length,'gs-btn');}
  body.append(acts);}
 // choose_equip_window
 function choose(hero,s){const {body,close}=W({title:SLOT_TITLE[s],cls:'eq-choose'});const mine=jobOf(hero),list=bagFor(s,hero).sort((a,b)=>(Number(b.r.job||0)===mine)-(Number(a.r.job||0)===mine));let pick=null;
  body.append(el('p','eq-choose-label','Chọn trang bị:'));const grid=el('div','eq-choose-grid');const info=el('div','eq-choose-info');
  const paint=()=>{info.replaceChildren();if(!pick){info.append(el('p','detail-note',list.length?"Chạm vào trang bị để xem thuộc tính.":"Chưa có "+SLOT_TITLE[s].toLowerCase()+" chưa mặc trong Túi Đồ."+(s<=4?" Có thể nhận từ Chiến Dịch hoặc Xưởng Rèn.":"")));return;}
   const r=row(pick);info.append(el('b','',displayName(r)));lines(info,pick,hero);const job=Number(r.job||0),bad=job&&jobOf(hero)&&job!==jobOf(hero);const a=el('div','gs-btns');btn(a,bad?'Nghề '+JOB_VI[job]:'Trang bị',()=>{close();send({action:'equip',partner_id:hero.partner_id,item_id:pick});},!!bad,'gs-btn');info.append(a);};
  for(const {id,n}of list){const b=el('button','eq-choose-item');b.type='button';b.append(icon(id));if(n>1)b.append(el('small','',String(n)));b.onclick=()=>{pick=id;grid.querySelectorAll('.on').forEach(x=>x.classList.remove('on'));b.classList.add('on');paint();};grid.append(b);}
  body.append(grid,info);paint();
  if(s<=4){const f=el('div','gs-btns');btn(f,"Xưởng Rèn",()=>{close();openSmithy(s,'detail');},false,'gs-btn white');body.append(f);}}
 // crystal (treasure): unlock, Exchange (treasure_change_window: new random attribute) and Lv. Up (treasure_up_window)
 function chooseTreasure(hero){
  if(state.server_id!=='S5')return;
  const current=Number(hero.equips?.[4]||0),old=row(current),all=Object.values(data.items).filter(r=>r.pos===5);
  const levels=[...new Set(all.map(r=>r.item_lv))].sort((a,b)=>b-a);
  const {body,close}=W({title:'Chọn Bảo Vật Khác',cls:'eq-treasure-select'});
  body.append(el('p','eq-select-note','Đặc quyền S5: chọn miễn phí Bảo Vật và thuộc tính theo dữ liệu gốc. Không ảnh hưởng nữ thần khác.'));
  const levelRow=el('label','eq-select-level','Cấp Bảo Vật');
  const select=el('select');select.setAttribute('aria-label','Cấp Bảo Vật');
  for(const lv of levels){const example=all.find(r=>r.item_lv===lv),o=el('option','',displayName(example)+' · Cấp '+lv+(lv===levels[0]?' (Tối đa)':''));o.value=String(lv);select.append(o);}
  select.value=String(old?.item_lv||levels[0]);levelRow.append(select);body.append(levelRow);
  const grid=el('div','eq-select-grid'),info=el('div','eq-select-info');body.append(grid,info);
  let picked=0,confirmed=false;
  function paint(){
   info.replaceChildren();if(!picked){info.append(el('p','detail-note','Chọn một Bảo Vật để xem thuộc tính.'));return;}
   const r=row(picked),different=!!old&&old.item_lv!==r.item_lv;
   info.append(el('strong','',displayName(r)+' · Cấp '+r.item_lv));lines(info,picked,hero);
   if(hero.tmp_treasure)info.append(el('p','eq-select-note','Lượt sửa thuộc tính chưa lưu sẽ bị bỏ khi chọn.'));
   if(different){const label=el('label','eq-select-confirm'),check=el('input');check.type='checkbox';check.checked=confirmed;
    label.append(check,el('span','','Xác nhận đổi cấp '+old.item_lv+' → '+r.item_lv));check.onchange=()=>{confirmed=check.checked;apply.disabled=!confirmed||pending;};info.append(label);}
   const actions=el('div','gs-btns');
   const apply=btn(actions,picked===current?'Đang sử dụng':'Chọn Bảo Vật',()=>{close();send({action:'treasure_select',partner_id:hero.partner_id,item_id:picked,confirm_level_change:confirmed},x=>'Đã chọn '+displayName(row(x.treasure))+' · Cấp '+row(x.treasure).item_lv);},picked===current||(different&&!confirmed),'gs-btn');
   info.append(actions);
  }
  function draw(){picked=0;confirmed=false;grid.replaceChildren();
   const seen=new Set();
   for(const r of all.filter(r=>r.item_lv===Number(select.value)).sort((a,b)=>(b.id===current)-(a.id===current)||a.id-b.id)){
    const key=JSON.stringify([r.name,r.base1,r.base2,r.base3,r.base4]);if(seen.has(key))continue;seen.add(key);
    const b=el('button','eq-select-card');b.type='button';b.append(icon(r.id),el('strong','',displayName(r)),el('small','','Cấp '+r.item_lv));lines(b,r.id,hero);
    if(r.id===current)b.append(el('small','eq-select-active','Đang dùng'));
    b.onclick=()=>{picked=r.id;confirmed=false;grid.querySelectorAll('button').forEach(x=>x.classList.toggle('on',x===b));paint();};grid.append(b);
   }paint();
  }
  select.onchange=draw;draw();
 }
 function treasureWin(hero,mode){const eq=(hero.equips||[])[4];const title=mode==='up'?'Nâng cấp Bảo Vật':mode==='exchange'?'Sửa Thuộc Tính':'Bảo Vật';const {body,close}=W({title,cls:'eq-treasure'});if(typeof ImgGuides!=='undefined'){const h=btn(body,'?',()=>ImgGuides.open('treasure_guide'),false,'ig-native-question');h.setAttribute('aria-label',"Hướng dẫn Bảo Vật");}
  if(!eq){body.append(el('p','',"Bảo Vật mở miễn phí từ cấp "+treasureLevel()+". Thuộc tính được chọn ngẫu nhiên."));const a=el('div','gs-btns');btn(a,'Mở khóa',()=>{close();send({action:'treasure_on',partner_id:hero.partner_id},r=>"Đã nhận: "+displayName(row(r.treasure)));},hero.lv<treasureLevel(),'gs-btn');if(state.server_id==='S5')btn(a,'Chọn Bảo Vật Khác',()=>{close();chooseTreasure(hero);},false,'gs-btn');body.append(a);return;}
  const r=row(eq),cur=el('div','eq-current');cur.append(icon(eq));const inf=el('div');inf.append(el('strong','',displayName(r)+" · Cấp "+r.item_lv));lines(inf,eq,hero);cur.append(inf);body.append(cur);
  if(hero.tmp_treasure){const pre=el('div','eq-current eq-preview');pre.append(icon(hero.tmp_treasure));const pi=el('div');pi.append(el('strong','',"Mới: "+displayName(row(hero.tmp_treasure))));lines(pi,hero.tmp_treasure,hero);pre.append(pi);body.append(pre);const b=el('div','gs-btns');btn(b,'Bỏ qua',()=>{close();send({action:'treasure_discard',partner_id:hero.partner_id});},false,'gs-btn white');btn(b,"Lưu",()=>{close();send({action:'treasure_save',partner_id:hero.partner_id});},false,'gs-btn');body.append(b);return;}
  const box=el('div','eq-actions');
  if(mode==='exchange'){const rf=el('div','eq-action');rf.append(el('b','',"Đổi ngẫu nhiên thuộc tính, giữ nguyên cấp"));cost(rf,r.treasure_refresh);body.append(rf);const a=el('div','gs-btns');btn(a,'Sửa Thuộc Tính',()=>{close();return send({action:'treasure_refresh',partner_id:hero.partner_id},()=>{setTimeout(()=>treasureWin(state.roster.find(h=>h.partner_id===hero.partner_id),'exchange'),0);return '';});},!affordable(r.treasure_refresh),'gs-btn');body.append(a);return;}
  if(!r.treasure_upgrade){body.append(el('p','detail-note',"Bảo Vật đã đạt cấp tối đa."));return;}
  const up=el('div','eq-action');up.append(el('b','',"Nâng cấp (thuộc tính ngẫu nhiên)"));cost(up,r.treasure_upgrade);btn(up,'Nâng cấp',()=>{close();send({action:'treasure_upgrade',partner_id:hero.partner_id},x=>"Mới: "+displayName(row(x.treasure)));},!affordable(r.treasure_upgrade),'gs-btn');box.append(up);
  const [target,extra]=String(r.treasure_lock_up||'').split('|');if(target&&row(target)){const lk=el('div','eq-action');lk.append(el('b','',"Nâng cấp và giữ thuộc tính → "+displayName(row(target))));const total=pairs(r.treasure_upgrade).map(([k,v])=>[k,Number(v)+Number(pairs(extra).find(([x])=>x===k)?.[1]||0)]);for(const [k,v]of pairs(extra))if(!total.some(([x])=>x===k))total.push([k,Number(v)]);const txt=total.map(([k,v])=>k+'#'+v).join('|');cost(lk,txt);btn(lk,'Nâng cấp',()=>{close();send({action:'treasure_upgrade',partner_id:hero.partner_id,lock:true});},!affordable(txt),'gs-btn');box.append(lk);}
  body.append(box);}

 // ---- Real attributes (HeroAttr) ----
 function attrs(hero){const key=JSON.stringify([hero.partner_id,hero.table_id,hero.lv,hero.grade,hero.awake,hero.equips]);const stats=$('detail-stats');if(!stats)return;
  const paint=a=>{if(!a||view!=='detail'||selectedGirlPartnerId!==hero.partner_id)return;$('detail-power-label').textContent="Power "+fmt(a.power);stats.replaceChildren();for(const [k,label,ic]of STAT_KEYS){const e=el('div','detail-stat');e.append(img('/assets/detail/'+ic+'.png'),el('span','',label+': '+fmt(a[k])));stats.append(e);}// HeroAttr gives every girl sklP = 1000 (neutral skill damage): only the part above it is an extra
  const base=k=>k==='sklP'?1000:['zs','fs','yx','ck','ms'].includes(k)?1:0;const extra=EXTRA.filter(k=>Number(a[k])>base(k));if(extra.length&&data){const x=el('div','eq-extra');for(const k of extra)x.append(el('span','',k==='sklP'?(data.attr_names[k]||'Skill DMG')+' +'+fmt(a[k]-1000)+'%':attrText(k,a[k]-base(k))));stats.append(x);}};
  if(attrCache[key]){paint(attrCache[key]);return;}attrKey=key;
  Promise.all([load(),api('/api/partner/'+hero.partner_id+'/attrs')]).then(([,a])=>{attrCache[key]=a;if(attrKey===key)paint(a);}).catch(()=>{});}

 // ---- Smithy ----
 function openSmithy(pos,from){smithyPos=pos||1;smithyItem=null;smithyCount=1;message='';smithyBack=from||view;load().then(()=>{showView('smithy');renderSmithy();});}
 function chain(){return Object.values(data.items).filter(r=>r.pos===smithyPos&&r.need_formula).sort((a,b)=>a.id-b.id);}
 function renderSmithy(){const root=$('smithy-view');if(!root||view!=='smithy'||!data)return;root.replaceChildren();
  if(artifactTarget)return artifactView(root);
  const top=el('header','eq-top');const back=el('button','eq-back');back.type='button';back.append(img('/assets/ui/win_back_btn.png'));back.onclick=()=>showView(smithyBack);top.append(back,el('h1','','Rèn'),money());root.append(top);
  const nav=el('nav','eq-nav');for(const [p,label]of SMITHY_TABS){const b=el('button',smithyPos===p?'on':'',label);b.type='button';b.onclick=()=>{smithyPos=p;smithyItem=null;smithyCount=1;message='';renderSmithy();};if(chain().length&&Object.values(data.items).some(r=>r.pos===p&&r.need_formula&&canForge(r)>0))b.append(img('/assets/equipment/alert_icon.png','eq-red'));nav.append(b);}root.append(nav);
  const list=chain();
  if(!list.length){root.append(el('p','eq-status','Không có công thức Rèn của nhà phát triển cho loại trang bị này.'));return;}
  if(!smithyItem||!list.some(r=>r.id===smithyItem))smithyItem=(list.find(r=>canForge(r)>0)||list[0]).id;
  const r=row(smithyItem);
  // The original equip recipe may have more than one material. Display every
  // cost, and never assume a single non-gold ingredient exists.
  const originalNeed=pairs(r.need_formula).filter(([id,amount])=>Number(amount)>0&&row(id));
  const main=originalNeed.find(([id])=>String(id)!=='1')||originalNeed[0];
  if(!main){root.append(el('p','eq-status','Công thức Rèn gốc chưa đủ dữ liệu để sử dụng.'));return;}
  const [src,per]=main;
  const gold=Number(pairs(r.need_formula).find(([k])=>k==='1')?.[1]||0);
  const head=el('div','sm-top');head.style.backgroundImage="url('/assets/equipment/bp_smithy_top.png')";const from=el('div','sm-from');from.append(icon(src));const pr=el('div','sm-bar');pr.style.backgroundImage="url('/assets/equipment/bp_bar_bg.png')";const fill=el('i');fill.style.width=Math.min(100,have(src)/per*100)+'%';fill.style.backgroundImage=`url('/assets/equipment/${have(src)>=per?'bp_bar_green':'bp_bar_blue'}.png')`;pr.append(fill,el('span','',fmt(have(src))+'/'+per));from.append(pr);
  head.append(from,img('/assets/equipment/mergeArrow.png','sm-arrow'),icon(r.id,'sm-result'));root.append(head);
  const info=el('div','sm-info');info.append(el('strong','',(row(src)?.name||'Vật phẩm #'+src)+' ×'+per+' → '+r.name));lines(info,r.id);
  cost(info,r.need_formula,'Toàn bộ nguyên liệu gốc cho mỗi lần rèn');
  root.append(info);
  const max=canForge(r);smithyCount=max?Math.max(1,Math.min(smithyCount,max)):0;const qty=el('div','sm-qty');btn(qty,'−',()=>{smithyCount=Math.max(1,smithyCount-1);renderSmithy();},smithyCount<=1,'sm-step');qty.append(el('b','',String(smithyCount)));btn(qty,'+',()=>{smithyCount=Math.min(max,smithyCount+1);renderSmithy();},smithyCount>=max,'sm-step');btn(qty,'Tối đa',()=>{smithyCount=max;renderSmithy();},max<=1,'sm-step');root.append(qty);
  const c=el('div','sm-cost');c.append(img('/assets/equipment/icon_1.png'),el('b',have(1)<gold*Math.max(1,smithyCount)?'short':'',fmt(gold*Math.max(1,smithyCount))));root.append(c);
  const acts=el('div','sm-actions');btn(acts,'Rèn',()=>send({action:'forge',item_id:r.id,count:smithyCount},x=>'Đã rèn: '+Object.entries(x.forged).map(([k,n])=>n+'× '+row(k).name).join(', ')),!max,'sm-btn white');btn(acts,'Tự động rèn',()=>send({action:'forge_auto',pos:smithyPos},x=>'Đã rèn: '+Object.entries(x.forged).map(([k,n])=>n+'× '+row(k).name).join(', ')),!list.some(x=>canForge(x)>0),'sm-btn blue');root.append(acts);
  const grid=el('div','sm-grid');for(const x of list){const b=el('button','sm-item'+(x.id===smithyItem?' on':''));b.type='button';b.append(icon(x.id));if(have(x.id))b.append(el('small','',fmt(have(x.id))));if(canForge(x)>0)b.append(img('/assets/equipment/alert_icon.png','eq-red'));b.title=x.name;b.onclick=()=>{smithyItem=x.id;smithyCount=1;message='';renderSmithy();};grid.append(b);}root.append(grid);
  root.append(el('p','eq-status',message));}
 function canForge(r){
  const need=pairs(r.need_formula);
  if(!need.length||need.some(([k,v])=>!Number.isSafeInteger(Number(v))||Number(v)<=0))return 0;
  let n=Infinity;
  for(const [k,v] of need)n=Math.min(n,Math.floor(have(k)/Number(v)));
  return Number.isFinite(n)?Math.max(0,n):0;
}
 function money(){const m=el('div','eq-money');for(const id of ['1','2']){const s=el('span');s.append(img('/assets/currency/icon_'+id+'_small.png'),el('b','',fmt(state.items[id]||0)));m.append(s);}return m;}

 // ---- Antique upgrade (ArtifactUpWindow) ----
 function openArtifact(id,partnerId){artifactTarget={id,partnerId};feed={};message='';smithyBack=view;load().then(()=>{showView('smithy');renderSmithy();});}
 function artifactView(root){const {id,partnerId}=artifactTarget,r=row(id);const top=el('header','eq-top');const back=el('button','eq-back');back.type='button';back.append(img('/assets/ui/win_back_btn.png'));back.onclick=()=>{artifactTarget=null;showView(smithyBack);};top.append(back,el('h1','','Nâng cấp Cổ vật'),money());root.append(top);
  const head=el('div','sm-top art');head.append(icon(id),img('/assets/equipment/mergeArrow.png','sm-arrow'),icon(r.artifact_next,'sm-result'));root.append(head);
  const info=el('div','sm-info');info.append(el('strong','',antiqueName(r.name)+' → '+antiqueName(row(r.artifact_next).name)));lines(info,r.artifact_next,null,true);root.append(info);
  const exp=Object.entries(feed).reduce((s,[k,n])=>s+Number(row(k).artifact_exp)*n,0),need=Number(r.artifact_upg);const pr=el('div','sm-bar wide');pr.style.backgroundImage="url('/assets/equipment/bp_bar_bg.png')";const fill=el('i');fill.style.width=Math.min(100,exp/need*100)+'%';fill.style.backgroundImage=`url('/assets/equipment/${exp>=need?'bp_bar_green':'bp_bar_blue'}.png')`;pr.append(fill,el('span','',fmt(exp)+'/'+fmt(need)));root.append(pr);
  const acts=el('div','sm-actions');btn(acts,'Tự Chọn',()=>{feed={};let left=need;for(const m of mats(id,partnerId).sort((a,b)=>a.r.item_lv-b.r.item_lv||a.r.artifact_exp-b.r.artifact_exp)){while(left>0&&(feed[m.id]||0)<m.n){feed[m.id]=(feed[m.id]||0)+1;left-=Number(m.r.artifact_exp);}if(left<=0)break;}renderSmithy();},false,'sm-btn white');
  btn(acts,"Nâng Cấp",()=>send({action:'artifact_upgrade',item_id:id,materials:feed,...(partnerId?{partner_id:partnerId}:{})},x=>{artifactTarget=row(x.upgraded)?.artifact_next?{id:x.upgraded,partnerId}:null;feed={};return "Đã nâng cấp: "+antiqueName(row(x.upgraded).name)+(x.returned?" · hoàn lại: "+x.returned+'× '+antiqueName(row(6000).name):'');}),exp<need,'sm-btn blue');root.append(acts);
  btn(acts,"Xóa Chọn",()=>{feed={};renderSmithy();},!Object.keys(feed).length,'sm-step');root.append(el('h4','',"Nguyên liệu (chạm để chọn; chạm lại hoặc nhấn Xóa Chọn để bỏ)"));const grid=el('div','sm-grid');for(const m of mats(id,partnerId)){const b=el('button','sm-item'+(feed[m.id]?' on':''));b.type='button';b.append(icon(m.id));b.append(el('small','',(feed[m.id]||0)+'/'+m.n));b.title=m.r.name+' · '+m.r.artifact_exp+' exp';b.onclick=()=>{if((feed[m.id]||0)<m.n){feed[m.id]=(feed[m.id]||0)+1;renderSmithy();}};b.oncontextmenu=e=>{e.preventDefault();if(feed[m.id]){feed[m.id]--;if(!feed[m.id])delete feed[m.id];renderSmithy();}};grid.append(b);}root.append(grid);
  if(!mats(id,partnerId).length)root.append(el('p','detail-note','Không có Cổ vật nào để dùng làm nguyên liệu.'));root.append(el('p','eq-status',message));}
 function mats(id,partnerId){return Object.entries(state.items).filter(([k,n])=>Number(n)>0&&row(k)?.pos===6&&row(k).artifact_exp).map(([k,n])=>({id:Number(k),n:Number(n)-(!partnerId&&Number(k)===id?1:0),r:row(k)})).filter(m=>m.n>0);}

 // ---- Bag hooks ----
 function bagDetail(itemId){const r=data&&row(itemId);const box=$('bag-detail');box.querySelector('.eq-bag-actions')?.remove();if(!r){if(!data)load().then(()=>bagDetail(itemId));return;}const wrap=el('div','eq-bag-actions');const info=el('div');lines(info,itemId);wrap.append(info);if(r.pos===6&&r.artifact_next)btn(wrap,'Nâng cấp',()=>openArtifact(itemId,null));if(r.pos<=4&&r.need_formula)btn(wrap,'Đến Xưởng Rèn',()=>openSmithy(r.pos,'bag'));box.append(wrap);}
 function render(){refresh();}
 document.addEventListener('DOMContentLoaded',()=>{const old=$('bag-forge');if(old){const b=old.cloneNode(true);old.replaceWith(b);b.addEventListener('click',()=>openSmithy(1,'bag'));}});
 return {gear,attrs,openSmithy,renderSmithy,bagDetail,load,icon:id=>data?.icons[String(id)]};
})();
