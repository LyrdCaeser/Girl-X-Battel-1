'use strict';
// Anima Gear (SoulEquipInfoWindow, SoulEquip1/2StrengthenWindow, bag tab, captures 2026-09-29-l/01-03). Rules: gxb2/souls.py.
// Sheet: the "Anima Gear" button (Lv 200+) opens the window with the Artifact (square, slot 1) and the four Anima Stones
// (round, slots 2-5), Unequip, and the Overview (attributes + set skill) / Replace (owned pieces for the chosen slot) /
// Plan tabs. A piece opens its detail: Equip / Remove, Lv. Up, Awaken, extra buff rolls (Artifact), lock.
const Souls=(()=>{
 let cat=null,sel=2,tab='overview',filter=0;
 const A=n=>'/assets/souls/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=vi(text);return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,vi(text));b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 const NAMES={atk:'Tấn Công',hp:'Sinh Lực',crit:'Bạo Kích',hit:'Chính Xác',miss:'Chặn Đòn',unCrit:'Kháng Bạo Kích',sklP:'Sát Thương Kỹ Năng',trueAtk:'Sát Thương Thánh',healI:'Hồi Máu Nhận',healB:'Lượng Hồi Máu',unfree:'Tỷ Lệ Khống Chế',free:'Miễn Khống Chế',atkP:'Tấn Công',hpP:'Sinh Lực'};
 const SET_NAMES={'1':'Cá Vàng May Mắn','2':'Sứa Trôi Nổi','3':'Cua Đá','4':'Dê Ma','5':'Kỳ Lân Lửa','6':'Thằn Lằn Tinh Ranh','7':'Cáo Chín Đuôi','8':'Mèo Dệt Vải','9':'Phượng Hoàng Uy Nghi'};
 const ARTIFACT_NAMES={
  5100001:'Bút Lông Ngọc Lục',5100002:'Sừng Mộng Mơ',5100003:'Hạt Sồi Trù Phú',
  5100004:'Đao Vảy Rồng',5100005:'Nấm Linh Thạch',5100006:'Hóa Thạch Chôn Vùi',
  5100007:'Bình Cát',5100008:'Bướm Huyền Bí',5100009:'Xúc Tu Dị Giới',
  5100010:'Mặt Nạ Hồ Ly',5100011:'Vỏ Sò Ca Hát',5100012:'Ánh Nhìn Thợ Săn',
  5100013:'Bùa Vực Sâu',5100014:'Sức Mạnh Thiên Nhiên',5100015:'Vuốt Mèo',
  5100016:'Lưới Bắt Mộng',5100017:'Lời Nguyền Rắn Độc',5100018:'Thuốc Uyên Ương',
  5100019:'Mũ Sừng',5100020:'Đồng Tiền Cổ',5100021:'Thuốc Sấm Sét'
 };
 const SET_DESC={
  '1':'Mỗi lần chịu sát thương không vượt quá 30% Sinh Lực tối đa. Tổng lượng sát thương giảm không vượt quá 100% Sinh Lực tối đa; kích hoạt tối đa 3 lần mỗi hiệp.',
  '2':'Giảm 0,5% sát thương nhận với mỗi 1% Kháng Bạo Kích. Khi bị đòn đánh thường hoặc kỹ năng chủ động gây bạo kích, tăng 30% Kháng Bạo Kích trong 1 hiệp.',
  '3':'Đầu mỗi hiệp nhận 1 tầng Giáp Cứng, tồn tại 1 hiệp. Khi chịu sát thương, tiêu hao 1 tầng Giáp Cứng để triệt tiêu lần sát thương đó.',
  '4':'Sau mỗi 3 lần gây sát thương, lần gây sát thương tiếp theo tăng thêm 60%.',
  '5':'Tăng 40% sát thương gây lên kẻ địch còn trên 80% Sinh Lực.',
  '6':'Tăng 50% sát thương gây lên trùm.',
  '7':'Cuối hiệp, nếu người mang bộ đã đánh thường hoặc không thể tấn công, tất cả đồng minh nhận 15% Chặn Đòn và 15% Miễn Khống Chế trong 2 hiệp.',
  '8':'Tăng 25% lượng lá chắn nhận được. Khi dùng kỹ năng chủ động trong lúc có Lá Chắn Ma Thuật, đồng minh ít Sinh Lực nhất nhận Lá Chắn Ma Thuật bằng 20% Sinh Lực tối đa của đồng minh đó.',
  '9':'Tăng 25% lượng hồi máu. Khi người mang bộ được hồi máu, xóa ngẫu nhiên 1 hiệu ứng bất lợi của 1 đồng minh ngẫu nhiên; tối đa 1 lần mỗi hiệp.'
 };
 const VN={
  'Anima Gear':'Trang Bị Linh Hồn','Anima Artifact':'Bảo Vật Linh Hồn','Anima Stone':'Đá Linh Hồn',
  'Anima Stone Ritual':'Nghi Thức Linh Hồn',
  'Overview':'Tổng Quan','Replace':'Chuyển Đổi','Plan':'Bộ Trang Bị','Unequip':'Tháo Tất Cả',
  'Attributes':'Thuộc Tính','Remove':'Tháo','Equip':'Trang Bị',
  'Unlock':'Mở Khóa','Lock':'Khóa','Lv. Up':'Nâng Cấp','Awaken':'Thức Tỉnh',
  'Save':'Lưu','Cancel':'Hủy','Descartar':'Bỏ Qua',
  'Maximum level for this star rank':'Đã đạt cấp tối đa của bậc sao này',
  'Basic Attribute':'Thuộc Tính Cơ Bản','Infuse Attribute':'Thuộc Tính Khắc Ấn',
  'Star up':'Tăng Sao','Star Rank':'Bậc Sao','Max Level':'Cấp Tối Đa',
  'Infuse Capacity':'Số Thuộc Tính Khắc Ấn','Upgrade':'Nâng Cấp',
  'Infuse':'Khắc Ấn','Convert':'Chuyển Đổi',
  'Thuộc Tính Chưa Mở':'Thuộc Tính Chưa Mở',
  'Level':'Cấp','Change ':'Đổi ','Obtener ':'Nhận ',
  'Primera vez':'Lần Đầu','Cambio':'Đổi Thuộc Tính','Atributos extra':'Thuộc Tính Phụ',
  'Soul Token':'Thẻ Linh Hồn','Shiny Soul Token':'Thẻ Linh Hồn Lấp Lánh',
  'Anima Artifact Chest':'Rương Bảo Vật Linh Hồn',
  'No spare 1★ Anima Stones':'Không có Đá Linh Hồn 1★ dư để làm nguyên liệu',
  'Đã nhận được trang bị':'Đã nhận được trang bị',
  'Skill-Synchronize':'Đồng Bộ Kỹ Năng','Elite Skills':'Kỹ Năng Tinh Anh','Reverse':'Hoàn Nguyên'
 };
 const vi=v=>typeof v==='string'?(VN[v]||v):v;
 const ORDER=['atk','hp','hit','miss','crit','unCrit','sklP','trueAtk','unfree','free','healI','healB'];
 const fmt=(k,v)=>['atk','hp'].includes(k)?number(Math.round(v)):['healI','healB','atkP','hpP'].includes(k)?(v*100).toFixed(2)+'%':v.toFixed(2)+'%';
 const G=list=>String(list).split('|').map(Number);
 async function load(){if(!cat)cat=await api('/api/souls/catalog',{});return cat;}
 const items=()=>state.souls_info?.items||{};
 const rec=id=>items()[String(id)];
 const isArt=r=>r.kind===1;
 const starOf=r=>isArt(r)?r.awake+1:Number(cat.equip2[r.table_id].star);
 const qltOf=r=>isArt(r)?cat.qlt1[r.table_id]:r.awake+1;
 const posOf=r=>isArt(r)?1:Number(cat.equip2[r.table_id].pos);
 const groupOf=r=>isArt(r)?0:Number(cat.equip2[r.table_id].group);
 const nameOf=r=>isArt(r)?(ARTIFACT_NAMES[r.table_id]||cat.names[r.table_id]||'Bảo Vật Linh Hồn'):(SET_NAMES[String(groupOf(r))]||'Đá Linh Hồn')+' · '+['','I','II','III','IV'][posOf(r)-1];
 const maxLv=r=>isArt(r)?G(cat.misc.soul_equip1_star_lvl)[starOf(r)-1]:Number(cat.equip2[r.table_id].max_lvl);
 // HeroAttr:getSouls
 function attrsOf(r){const out=[];const add=(k,v)=>out.push([k,v]);
  if(isArt(r)){const row=cat.equip1[r.table_id],sg=G(row.star_grow)[r.awake]||1;for(const i of [1,2,3]){const b=String(row['base'+i]||''),g=String(row['grow'+i]||'');if(!b.includes('#'))continue;const [k,bv]=b.split('#'),gv=Number(g.split('#')[1]||0);add(k,(Number(bv)+gv*r.lv)*sg);}
   return {main:out,ex:(r.attrs||[]).map(id=>id>0?[cat.buff1[id].buff,Number(cat.buff1[id].base)+Number(cat.buff1[id].grow)*r.lv]:null)};}
  const b=cat.base2[r.main],st=Number(cat.equip2[r.table_id].star);add(b.buff,(Number(b.base)+Number(b.grow)*r.lv)*G(b.star_grow)[st-1]*G(b.qlt_grow)[r.awake]);
  const ex=[...r.attrs,...r.ex_attrs].map(s=>{const [id,f]=s.split('#').map(Number),x=cat.buff2[id];return [x.buff,Number(x.base)*f*G(x.star_grow)[st-1]*G(x.qlt_grow)[r.awake]];});
  return {main:out,ex};}
 // ItemIcon:initSoulEquip: lead_skin_border_<qlt>, +lv, stars (pub_star_require<n>), pos marker soul_equip_icon_pos_<qlt>
 function icon(r,cls=''){const w=el('span','ag-icon'+(isArt(r)?' art':' stone p'+posOf(r))+(cls?' '+cls:''));w.style.backgroundImage=`url('${A('lead_skin_border_'+Math.min(7,qltOf(r)))}')`;
  w.append(img(A(cat.icons[r.table_id]||'soul_equip_5200001'),'ag-art'));if(!isArt(r))w.append(img(A('soul_equip_icon_pos_'+Math.min(6,qltOf(r))),'ag-pos'));
  w.append(img(A('pub_star_require'+Math.min(6,starOf(r))),'ag-stars'),el('b','ag-lv','+'+r.lv));
  if(r.owner){const o=state.roster.find(h=>h.partner_id===r.owner);if(o&&typeof portrait==='function'){const f=el('span','ag-owner');f.append(portrait(o.table_id,40));w.append(f);}}
  if(r.lock)w.append(el('i','ag-lock','🔒'));return w;}
 // SoulEquipInfoWindow iconPos2-5: round frame soul_equip_kuang_small_<qlt>, art, +lv, pub_star_require<star>
 function round(r){const w=el('span','ag-round');w.append(img(A(cat.icons[r.table_id]||'soul_equip_5200001'),'ag-art'),img(A('soul_equip_kuang_small_'+Math.min(6,qltOf(r))),'ag-ring'),img(A('pub_star_require'+Math.min(6,starOf(r))),'ag-stars'),el('b','ag-lv','+'+r.lv));return w;}
 async function act(req,after){try{const res=await api('/api/souls/action',req);state=res.state;if(typeof render==='function')render();after?.(res);return res;}catch(e){GirlUI.toast(e.message);return null;}}

 // ---- girl sheet: side buttons (midBtns btnSoulEquip / btnExSkill) ----
 function sheet(hero){const scene=document.querySelector('#girl-detail-view .detail-scene');if(!scene)return;scene.querySelectorAll('.gs-left').forEach(x=>x.remove());
  const add=(cls,icon,label,fn)=>{const b=btn('gs-left '+cls,'',fn);b.append(img(icon),el('small','',label));scene.append(b);};
  if(hero.lv>=(state.souls_info?.open_lv||200))add('soul','/assets/souls/soul_equip_icon_rk_lszb.png','Anima Gear',()=>open(hero.partner_id));
  if(hero.stars>=10){if(hero.group===7)add('ex','/assets/souls/skill_resonate_icon.png','Skill-Synchronize',()=>GirlUI.resonate(hero));
   else add('ex','/assets/souls/advanced_skill.png','Elite Skills',()=>GirlUI.eliteSkills?.(hero));}
  else if(hero.stars!==6&&hero.group!==7)add('ex','/assets/detail/sheet/partner_detail_btn_zjht.png','Reverse',()=>GirlUI.reverse(hero));}

 // ---- SoulEquipInfoWindow ----
 async function refreshInventory(pid){
  // Only use the authenticated player's own fresh server state. Do not
  // manufacture soul serials or silently replace unrelated client state.
  const fresh=await api('/api/state');
  if(!fresh?.souls_info?.items||!Array.isArray(fresh.roster))
   throw Error('Chưa nhận được dữ liệu Trang Bị Linh Hồn từ máy chủ.');
  if(state.uid&&fresh.uid&&String(fresh.uid)!==String(state.uid))
   throw Error('Hồ sơ trả về không khớp tài khoản đang sử dụng.');
  if(state.server_id&&fresh.server_id&&String(fresh.server_id)!==String(state.server_id))
   throw Error('Máy chủ trả về không đúng khu vực tài khoản.');
  const current=state.roster.find(h=>String(h.partner_id)===String(pid));
  const updated=fresh.roster.find(h=>String(h.partner_id)===String(pid));
  if(!updated||!current)throw Error('Không tìm thấy Nữ Thần trong hồ sơ hiện tại.');
  state.souls_info=fresh.souls_info;
  current.souls=Array.isArray(updated.souls)?updated.souls.slice():[0,0,0,0,0];
  current.soul_infos=Array.isArray(updated.soul_infos)?updated.soul_infos.slice():[];
  return Object.keys(fresh.souls_info.items).length;
 }
 async function open(pid,slot){
  await load();
  try{await refreshInventory(pid);}catch(e){GirlUI.toast('Chưa đồng bộ được Trang Bị Linh Hồn: '+e.message);}
  sel=slot||sel;filter=0;tab='overview';paint(pid);
 }
 function paint(pid){const hero=state.roster.find(h=>h.partner_id===pid);if(!hero)return;const {body,win}=GirlUI.win({title:'Trang Bị Linh Hồn',cls:'ag-win',help:'Nữ Thần từ cấp 200 có thể sử dụng Trang Bị Linh Hồn. Ô vuông giữa là Bảo Vật Linh Hồn, bốn ô tròn là Đá Linh Hồn. Trang bị đủ bốn viên cùng bộ sẽ kích hoạt kỹ năng bộ.'});
  const souls=(hero.souls||[]).concat([0,0,0,0,0]).slice(0,5);
  const top=el('div','ag-top');top.append(img(A('soul_equip_bg_lx'),'ag-bg'));
  souls.forEach((sid,i)=>{const r=sid&&rec(sid);const b=btn('ag-slot s'+(i+1)+(sel===i+1?' on':''),'',()=>{sel=i+1;filter=0;if(tab==='overview')tab='replace';paint(pid);});if(r)b.append(i?round(r):icon(r));else b.append(el('span','ag-plus','+'));top.append(b);});
  top.append(btn('gs-btn red ag-drop','Unequip',()=>act({action:'unequip',partner_id:pid},()=>paint(pid)),!souls.some(Boolean)));body.append(top);
  const nav=el('div','ag-tabs');for(const [k,label]of [['overview','Overview'],['replace','Replace'],['plan','Plan']])nav.append(btn('ag-tab'+(tab===k?' on':''),label,()=>{tab=k;paint(pid);}));body.append(nav);
  const box=el('div','ag-content');body.append(box);
  if(tab==='overview')overview(box,souls);
  else if(tab==='replace')replace(box,hero,souls);
  else plans(box,hero,souls);}
 // Saved gear sets are persisted by the server with actual Soul serial IDs.
 // No local-only mock data, no item generation, and no silent transfer from another hero.
 function plans(box,hero,equipped){
  const saved=state.souls_info?.plans?.[String(hero.partner_id)]||{};
  box.append(el('h4','ag-title','Bộ Trang Bị Linh Hồn'));
  box.append(el('p','ag-plan-hint','Lưu tối đa 3 bộ cho Nữ Thần này. Áp dụng sẽ thay các món đang trang bị; nếu vật phẩm đã chuyển sang Nữ Thần khác, hãy tháo ra trước.'));
  const list=el('div','ag-plans');
  for(let i=1;i<=3;i++){
   const ids=saved[String(i)],has=Array.isArray(ids)&&ids.length===5;
   const row=el('div','ag-plan');
   row.append(el('b','ag-plan-name','Bộ '+i+(has?' · Đã lưu':' · Chưa lưu')));
   const pictures=el('div','ag-plan-pieces');
   (has?ids:[0,0,0,0,0]).forEach(id=>{
    const r=id?rec(id):null;
    pictures.append(r?icon(r):el('span','ag-plan-empty',id?'!':'+'));
   });
   row.append(pictures);
   const actions=el('div','ag-plan-actions');
   actions.append(btn('gs-btn','Lưu bộ này',()=>act(
     {action:'plan_save',partner_id:hero.partner_id,plan:i},
     ()=>paint(hero.partner_id)),!equipped.some(Boolean)));
   actions.append(btn('gs-btn','Áp dụng',()=>act(
     {action:'plan_apply',partner_id:hero.partner_id,plan:i},
     ()=>paint(hero.partner_id)),!has));
   if(has)actions.append(btn('gs-btn white','Xóa bộ',()=>act(
     {action:'plan_delete',partner_id:hero.partner_id,plan:i},
     ()=>paint(hero.partner_id))));
   row.append(actions);list.append(row);
  }
  box.append(list);
 }
 function overview(box,souls){box.append(el('h4','ag-title','Attributes'));const sum={};for(const sid of souls){const r=sid&&rec(sid);if(!r)continue;const a=attrsOf(r);for(const x of [...a.main,...a.ex])if(x)sum[x[0]]=(sum[x[0]]||0)+x[1];}
  const grid=el('div','ag-attrs');for(const k of ORDER.concat(['atkP','hpP'].filter(k=>k in sum))){const d=el('div','ag-attr');d.append(el('b','',NAMES[k]+(['atkP','hpP'].includes(k)?' %':'')),el('span','',fmt(k,sum[k]||0)));grid.append(d);}box.append(grid);
  const groups=souls.slice(1).map(sid=>sid&&rec(sid)?groupOf(rec(sid)):0);const g=groups[0];
  if(g&&groups.every(x=>x===g)){const info=cat.groups[g];box.append(el('p','ag-set-name',(SET_NAMES[String(g)]||info.skill_name)),el('p','ag-set',(SET_DESC[String(g)]||info.skill_desc)));}
  else box.append(el('p','ag-set dim',"Trang bị 4 Đá Linh Hồn cùng bộ để kích hoạt kỹ năng bộ."));}
 function replace(box,hero,souls){const all=Object.entries(items()).map(([id,r])=>({id:Number(id),r})).filter(({r})=>posOf(r)===sel&&(!filter||qltOf(r)===filter)).sort((a,b)=>(a.r.owner===hero.partner_id)-(b.r.owner===hero.partner_id)||starOf(b.r)-starOf(a.r)||qltOf(b.r)-qltOf(a.r)||b.r.lv-a.r.lv);
  const grid=el('div','ag-grid');for(const {id,r}of all){const b=btn('ag-cell'+(souls[sel-1]===id?' on':''),'',()=>detail(id,hero.partner_id));b.append(icon(r));grid.append(b);}
  if(!Object.keys(items()).length){
   box.append(el('p','ag-inventory-warning',
    'Hồ sơ trên máy chủ hiện chưa có Trang Bị Linh Hồn. Đây là số vật phẩm thật đã lưu, không phải số đồ trong ảnh cũ.'));
  }
  const syncBar=el('div','ag-sync');
  syncBar.append(btn('gs-btn white','Làm Mới Túi Linh Hồn',async()=>{
   try{
    const count=await refreshInventory(hero.partner_id);
    GirlUI.toast('Đã đồng bộ: '+count+' món Trang Bị Linh Hồn.');
    paint(hero.partner_id);
   }catch(e){GirlUI.toast('Không thể đồng bộ: '+e.message);}
  }));
  box.append(syncBar);
  const totalForSlot=Object.values(items()).filter(r=>posOf(r)===sel).length;
  const totalInBag=Object.keys(items()).length;
  box.append(el('p','ag-slot-count','Ô '+sel+': '+all.length+' món phù hợp · '+totalForSlot+' món tại vị trí này · Tổng '+totalInBag+' món'));
  if(!all.length)grid.append(el('p','ag-empty',filter
    ?'Không có trang bị phẩm chất '+filter+'★ phù hợp. Chạm lại màu đang chọn để bỏ lọc.'
    :sel===1?'Chưa có Bảo Vật Linh Hồn cho ô trung tâm.'
     :'Chưa có Đá Linh Hồn phù hợp ô '+sel+'. Có thể chọn ô khác để xem vật phẩm.'));
  box.append(grid,filters(()=>paint(hero.partner_id)));}
 function filters(repaint){const f=el('div','ag-filters');for(let q=1;q<=7;q++){const b=btn('ag-q q'+q+(filter===q?' on':''),'',()=>{filter=filter===q?0:q;repaint();});b.title='Phẩm chất '+q;f.append(b);}return f;}

 // ---- piece detail / strengthen (SoulEquip1/2StrengthenWindow) ----
 function detail(id,pid){const r=rec(id);if(!r)return;if(isArt(r))return artDetail(id,pid);const {body,close}=GirlUI.win({title:isArt(r)?'Bảo Vật Linh Hồn':'Đá Linh Hồn',cls:'ag-detail'});
  const head=el('div','ag-head');head.append(icon(r,'big'));const info=el('div');info.append(el('b','ag-name',nameOf(r)),el('span','ag-sub','Cấp '+r.lv+' / '+maxLv(r)+' · '+starOf(r)+'★ · Phẩm chất '+qltOf(r)));
  const a=attrsOf(r);const ul=el('ul','ag-lines');for(const [k,v]of a.main)ul.append(el('li','main',NAMES[k]+' +'+fmt(k,v)));
  if(isArt(r)){const opened=G(cat.misc.soul_equip1_ex_num)[starOf(r)-1];for(let i=0;i<opened;i++){const x=a.ex[i];ul.append(el('li',x?'':'dim',x?NAMES[x[0]]+(['atkP','hpP'].includes(x[0])?' %':'')+' +'+fmt(x[0],x[1]):'Thuộc tính phụ '+(i+1)+': chưa có'));}}
  else a.ex.forEach(x=>ul.append(el('li','',NAMES[x[0]]+' +'+fmt(x[0],x[1]))));
  info.append(ul);head.append(info);body.append(head);
  if(!isArt(r)){const g=cat.groups[groupOf(r)];if(g)body.append(el('p','ag-set','Bộ '+(SET_NAMES[String(groupOf(r))]||g.name)+' (4 món): '+(SET_DESC[String(groupOf(r))]||g.skill_desc)));}
  if(r.owner){const o=state.roster.find(h=>h.partner_id===r.owner);if(o)body.append(el('p','ag-sub','Đang trang bị cho '+o.name));}
  const re=()=>{close();detail(id,pid);};
  const acts=el('div','gs-btns');
  if(pid){if(r.owner===pid)acts.append(btn('gs-btn red','Remove',()=>act({action:'unequip',partner_id:pid,slot:posOf(r)},()=>{close();paint(pid);})));else acts.append(btn('gs-btn','Equip',()=>act({action:'equip',partner_id:pid,soul_id:id},()=>{close();paint(pid);})));}
  acts.append(btn('gs-btn white',r.lock?'Mở Khóa':'Khóa',()=>act({action:'lock',soul_id:id},re)));body.append(acts);
  const up=el('div','ag-up');body.append(up);
  if(r.lv<maxLv(r)){if(isArt(r)){const cost=cat.exp1[r.lv+1]?.cost;up.append(el('b','','Lv. Up'),costRow(cost));const b=el('div','ag-row');b.append(btn('gs-btn','+1',()=>act({action:'lv_up',soul_id:id},re)),btn('gs-btn','+10',()=>act({action:'lv_up',soul_id:id,times:10},re)));up.append(b);}
   else{const need=Number(cat.exp2[r.lv+1]?.cost||0)-(r.exp||0);up.append(el('b','','Nâng Cấp · EXP '+(r.exp||0)+' / '+cat.exp2[r.lv+1]?.cost),el('small','',"Dùng Tinh Chất Linh Hồn (1 EXP) hoặc Đá Linh Hồn dư làm nguyên liệu. Mở thêm thuộc tính phụ ở cấp 5/10/15/20."));
    const b=el('div','ag-row');b.append(btn('gs-btn','Tinh Chất ×'+need,()=>act({action:'lv_up',soul_id:id,essence:need},re)),btn('gs-btn white','Dùng Đá 1★',()=>{const feed=Object.entries(items()).filter(([k,x])=>Number(k)!==id&&!isArt(x)&&!x.owner&&!x.lock&&starOf(x)===1).map(([k])=>Number(k)).slice(0,10);if(!feed.length){GirlUI.toast("Không có Đá Linh Hồn 1★ dư để làm nguyên liệu");return;}act({action:'lv_up',soul_id:id,feed},re);}));up.append(b);}}
  else up.append(el('b','',"Maximum level for this star rank"));
  if(isArt(r)){const row=cat.equip1[r.table_id];if(starOf(r)<Number(row.max_star)){const copies=Object.entries(items()).filter(([k,x])=>Number(k)!==id&&x.table_id===r.table_id&&!x.owner&&!x.lock).length;up.append(el('b','','Thức Tỉnh → '+(starOf(r)+1)+"★ (tăng giới hạn cấp)"),el('small','','Tiêu hao 1 Bảo Vật Linh Hồn cùng loại chưa trang bị · hiện có: '+copies));up.append(btn('gs-btn','Awaken',()=>act({action:'awake',soul_id:id},re),!copies));}
   const opened=G(cat.misc.soul_equip1_ex_num)[starOf(r)-1];if(opened){up.append(el('b','','Thuộc Tính Phụ'));const row2=el('div','ag-row');for(let i=0;i<opened;i++){const has=(r.attrs||[])[i]>0;row2.append(btn('gs-btn'+(has?' white':''),(has?"Đổi ":'Nhận ')+(i+1),()=>act({action:'roll_ex',soul_id:id,slot:i+1},re)));}up.append(row2,costRow(cat.misc.soul_equip1_ex_first_cost,'Primera vez'),costRow(cat.misc.soul_equip1_ex_cost,'Cambio'));
    if(r.replace){const x=cat.buff1[r.replace.id];const p=el('div','ag-replace');p.append(el('b','','Thuộc tính mới '+(r.replace.slot+1)+': '+NAMES[x.buff]+' +'+fmt(x.buff,Number(x.base)+Number(x.grow)*r.lv)));const rb=el('div','ag-row');rb.append(btn('gs-btn white','Descartar',()=>act({action:'discard_ex',soul_id:id},re)),btn('gs-btn',"Save",()=>act({action:'save_ex',soul_id:id},re)));p.append(rb);up.append(p);}}}
  else{const row=cat.equip2[r.table_id];if(r.awake+1<Number(row.max_qlt)){up.append(el('b','','Thức Tỉnh → phẩm chất '+(r.awake+2)),costRow(String(row.material).split('|')[r.awake].replace('@','|')));up.append(btn('gs-btn','Awaken',()=>act({action:'awake',soul_id:id},re)));}}}
 // SoulEquip1StrengthenWindow (capture fb/120): winged header with the piece, Equip / Lock, and the tabs Star up (Star Rank,
 // Max Level, Infuse Capacity now → next, a free copy as material), Upgrade (Level, Basic and Infuse Attributes now → next,
 // cost) and Infuse (Infuse Attribute · I-V with Infuse / Convert, locked until the star that opens them).
 let artTab=2;
 function artDetail(id,pid){const r=rec(id);if(!r)return;const {body,close}=GirlUI.win({title:'Trang Bị Linh Hồn',cls:'ag2'});const re=()=>{close();artDetail(id,pid);};
  const head=el('div','ag2-head');head.style.backgroundImage=`url('${A('chess_exchange')}')`;head.append(icon(r,'big'),el('b','ag2-name q'+Math.min(7,qltOf(r)),nameOf(r)));body.append(head);
  const acts=el('div','ag2-acts');if(pid){if(r.owner===pid)acts.append(btn('gs-btn red','Remove',()=>act({action:'unequip',partner_id:pid,slot:posOf(r)},()=>{close();paint(pid);})));else acts.append(btn('gs-btn','Equip',()=>act({action:'equip',partner_id:pid,soul_id:id},()=>{close();paint(pid);})));}
  if(r.owner){const o=state.roster.find(h=>h.partner_id===r.owner);if(o)acts.append(el('small','ag-sub','Đang trang bị cho '+o.name));}
  acts.append(btn('ag2-lock'+(r.lock?' on':''),r.lock?'🔒':'🔓',()=>act({action:'lock',soul_id:id},re)));body.append(acts);
  const nav=el('div','ag2-nav');[['Star up','left'],['Upgrade','mid'],['Infuse','right']].forEach(([t,k],i)=>{const b=btn('ag2-tab'+(artTab===i+1?' on':''),t,()=>{artTab=i+1;re();});b.style.backgroundImage=`url('${A('nav_btn_'+(artTab===i+1?'blue':'white')+'_'+k)}')`;nav.append(b);});body.append(nav);
  const box=el('div','ag2-box');body.append(box);const opened=s=>G(cat.misc.soul_equip1_ex_num)[s-1]||0;const star=starOf(r),max=Number(cat.equip1[r.table_id].max_star);
  const cmp=(label,a,b)=>{const row=el('div','ag2-cmp');row.append(el('span','',label),el('b','',a));if(b!==undefined&&b!==null){row.append(el('i','','➜'),el('b','next',b));}return row;};
  const exLine=(x)=>x?NAMES[x[0]]+(['atkP','hpP'].includes(x[0])?' %':'')+' +'+fmt(x[0],x[1]):'—';
  if(artTab===1){if(star<max){box.append(cmp('Star Rank',star+'★',(star+1)+'★'),cmp('Max Level',String(maxLv(r)),String(G(cat.misc.soul_equip1_star_lvl)[star])),cmp('Infuse Capacity',String(opened(star)),String(opened(star+1))));
    const copies=Object.entries(items()).filter(([k,x])=>Number(k)!==id&&x.table_id===r.table_id&&!x.owner&&!x.lock);const mat=el('div','ag2-mat');if(copies.length)mat.append(icon(copies[0][1]));else mat.append(img(A('arena_team_plus'),'ag2-plus'));box.append(mat,el('small','ag2-need','Bảo Vật Linh Hồn cùng loại còn dư: '+copies.length+'/1'));
    box.append(btn('gs-btn ag2-go','Star up',()=>act({action:'awake',soul_id:id},re),!copies.length));}
   else{box.append(cmp('Star Rank',star+'★'),img(A('pet_skill_max_en_en'),'ag2-max'));}}
  else if(artTab===2){const a=attrsOf(r);if(r.lv<maxLv(r)){const n=attrsOf({...r,lv:r.lv+1});box.append(cmp('Level','Cấp '+r.lv,'Cấp '+(r.lv+1)),el('h5','ag2-sec','Basic Attribute'));a.main.forEach(([k,v],i)=>box.append(cmp(NAMES[k],'+'+fmt(k,v),'+'+fmt(k,n.main[i][1]))));
    box.append(el('h5','ag2-sec','Infuse Attribute'));for(let i=0;i<opened(star);i++){const x=a.ex[i],y=n.ex[i],R=['I','II','III','IV','V'][i];box.append(x?cmp(R+' · '+NAMES[x[0]],'+'+fmt(x[0],x[1]),'+'+fmt(y[0],y[1])):cmp(R+' · Thuộc Tính Chưa Mở','—'));}
    const cost=cat.exp1[r.lv+1]?.cost;box.append(costRow(cost));const b=el('div','ag-row');b.append(btn('gs-btn ag2-go','Upgrade',()=>act({action:'lv_up',soul_id:id},re)),btn('gs-btn white','×10',()=>act({action:'lv_up',soul_id:id,times:10},re)));box.append(b);}
   else{box.append(cmp('Level','Cấp '+r.lv+' / '+maxLv(r)),el('h5','ag2-sec','Basic Attribute'));a.main.forEach(([k,v])=>box.append(cmp(NAMES[k],'+'+fmt(k,v))));box.append(img(A('pet_skill_max_en_en'),'ag2-max'),el('small','ag2-need',star<max?'Tăng sao để nâng cấp tối đa':''));}}
  else{box.append(el('p','ag2-tip','Thuộc tính khắc ấn tăng cùng với cấp Bảo Vật Linh Hồn'));const a=attrsOf(r);const need=i=>{for(let s2=1;s2<=max;s2++)if(opened(s2)>i)return s2;return max;};
   for(let i=0;i<5;i++){const row=el('div','ag2-ex');row.append(el('small','ag2-exname','Thuộc Tính Khắc Ấn · '+['I','II','III','IV','V'][i]));const has=(r.attrs||[])[i]>0;
    if(i<opened(star)){row.append(el('b','',has?exLine(a.ex[i]):'Thuộc Tính Chưa Mở'),btn('gs-btn',has?'Convert':'Infuse',()=>act({action:'roll_ex',soul_id:id,slot:i+1},re)));}
    else{row.classList.add('locked');row.append(el('b','','Mở khi Bảo Vật Linh Hồn đạt '+need(i)+'★'));}box.append(row);}
   box.append(costRow(cat.misc.soul_equip1_ex_first_cost,'Infuse'),costRow(cat.misc.soul_equip1_ex_cost,'Convert'));
   if(r.replace){const x=cat.buff1[r.replace.id];const p=el('div','ag-replace');p.append(el('b','','Thuộc Tính Khắc Ấn · '+['I','II','III','IV','V'][r.replace.slot]+': '+NAMES[x.buff]+' +'+fmt(x.buff,Number(x.base)+Number(x.grow)*r.lv)));const rb=el('div','ag-row');rb.append(btn('gs-btn white','Cancel',()=>act({action:'discard_ex',soul_id:id},re)),btn('gs-btn','Save',()=>act({action:'save_ex',soul_id:id},re)));p.append(rb);box.prepend(p);}}}
 function costRow(text,label){const c=el('span','ag-cost');if(label)c.append(el('small','',label));for(const part of String(text||'').split('|')){if(!part.includes('#'))continue;const [k,n]=part.split('#');const s=el('span',Number(state.items[k]||0)>=Number(n)?'':'short');const it=itemCatalog?.[k];const src=k==='1'?'/assets/currency/icon_1_small.png':it&&itemIcons.has(it.icon)?'/assets/item-icons/'+it.icon+'.png':(cat.icons[k]?A(cat.icons[k]):'');if(src)s.append(img(src));s.append(el('b','',number(Number(n))));s.title=(it?.name||cat.names[k]||k)+" · owned: "+number(state.items[k]||0);c.append(s);}return c;}

 // ---- Bag tab "Anima Gear" (capture l/01): pieces + boxes, quality circles, count / limit, Anima Stone Ritual ----
 async function bag(){if(bagTab!==7)return;await load();if(bagTab!==7)return;const grid=$('bag-grid');const list=Object.entries(items()).map(([id,r])=>({id:Number(id),r})).filter(({r})=>!bagQuality||qltOf(r)===bagQuality).sort((a,b)=>starOf(b.r)-starOf(a.r)||qltOf(b.r)-qltOf(a.r)||b.r.lv-a.r.lv||a.id-b.id);
  // Separate real serialized equip pieces from old stacked SoulEquip item IDs
  // so 10/1000 cannot be mistaken for the total number of unconverted stones.
  const firstStack=grid.firstElementChild;
  const frag=document.createDocumentFragment();for(const {id,r}of list){const b=btn('bag-item ag-bag','',()=>detail(id,null));b.title=nameOf(r);b.append(icon(r));frag.append(b);}
  if(list.length){
    grid.prepend(el('div','ag-bag-section','Trang Bị Linh Hồn · '+list.length+' món'),frag);
  }
  if(firstStack&&firstStack.isConnected){
    const oldCount=Array.from(grid.querySelectorAll('.bag-item:not(.ag-bag)')).length;
    grid.insertBefore(el('div','ag-bag-section','Đá và Bảo Vật Linh Hồn đang xếp chồng · '+oldCount+' loại'),firstStack);
  }
  $('bag-empty').hidden=grid.querySelectorAll('.bag-item').length>0;
  const acts=document.querySelector('.bag-actions');acts.querySelector('.ag-bag-info')?.remove();const info=el('div','ag-bag-info');
  info.append(el('b','','Đã nhận: '+Object.keys(items()).length+'/'+(state.souls_info?.limit||1000)),btn('ag-ritual','Nghi Thức Linh Hồn',ritual));acts.append(info);}
 function ritual(){const {body}=GirlUI.win({title:'Nghi Thức Linh Hồn',cls:'ag-ritual-win'});const lv=state.souls_info?.level||1;body.append(el('p','','Cấp nghi thức: '+lv+' (triệu hồi nhiều lần để tăng cấp, mở cơ hội nhận sao cao hơn).'));
  for(const [g,label,item]of [[1,'Soul Token','423'],[2,'Shiny Soul Token','424']]){const row=el('div','ag-gacha');row.append(img(A(cat.icons[item]||'icon_'+item)),el('b','',vi(label)+' · đang có: '+number(state.items[item]||0)));const r=el('div','ag-row');for(const t of [1,10])r.append(btn('gs-btn','×'+t,()=>act({action:'summon',gacha:g,times:t},res=>{GirlUI.toast('Obtenidas '+res.got.length+' Anima Stones');if(view==='bag')renderBag();})));row.append(r);body.append(row);}
  const boxes=el('div','ag-row');for(const [iid,label]of [[435,"Anima Artifact Chest"],[5200104,'Đá Linh Hồn 4★']]){if(Number(state.items[iid]||0)>0)boxes.append(btn('gs-btn white','Mở '+vi(label)+' ('+number(state.items[iid])+')',()=>act({action:'open',item_id:iid,count:1},res=>{GirlUI.toast("Piece obtained");if(view==='bag')renderBag();})));}body.append(boxes);}
 return {sheet,open,bag,load,ritual};
})();
