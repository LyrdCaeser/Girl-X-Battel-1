'use strict';
// Internship (TavernWindow → TavernDetailWindow). Rules: gxb2/internship.py. Original sprites: pub_mission_star1-7,
// pub_star_require*, img_group*, pub_job_icon*, pub_lock / pub_un_lock, pub_timer1, icon_24 / icon_25.
const Internship=(()=>{
 let origin='campus',panel=null,note='',busyLocal=false,pick=[],timer=null;
 const A=n=>'/assets/internship/'+n+'.png';
 const TASK_NAMES_VI=Object.freeze({
 "1": "Tìm Skarivine",
 "2": "Rắc Rối Của Psychic",
 "3": "Rắc Rối Của Kitty",
 "4": "Trợ Giúp Anna",
 "5": "Yêu Cầu Của Fleur",
 "6": "Tìm Reo",
 "7": "Chế Ngự Lin AI",
 "8": "Món Quà Của Boro",
 "9": "Chế Ngự Magician",
 "10": "Yêu Cầu Của Litana",
 "11": "Yêu Cầu Của Octagirl",
 "12": "Haxie Mất Tích",
 "13": "Lily Mất Tích",
 "14": "Yêu Cầu Của Lavia",
 "15": "Điều Ước Của Ashely",
 "16": "Điều Ước Của Lavia",
 "17": "Rắc Rối Của Bud Elf",
 "18": "Trợ Giúp Amazon",
 "19": "Yêu Cầu Của Lightin",
 "20": "Susan Mất Tích",
 "21": "Tìm Hexa",
 "22": "Mối Đe Dọa Từ Medusa",
 "23": "Điều Ước Của Geisha",
 "24": "Yêu Cầu Của Toy Girl",
 "25": "Androi Mất Tích",
 "26": "Tìm Phoenix",
 "27": "Điều Ước Của Librarian",
 "28": "Sự Kiêu Hãnh Của Nani",
 "29": "Tìm Thanh Kiếm Của Javelin",
 "30": "Điều Ước Của Succuba",
 "31": "Rắc Rối Của Caitlyn",
 "32": "Thử Thách Của Dracula",
 "33": "Yêu Cầu Của Himoto",
 "34": "Tìm Blowie",
 "35": "Yêu Cầu Của Guan Yin",
 "36": "Điều Ước Của Silvia",
 "37": "Nhiệm Vụ Của Pandaria",
 "38": "Điều Ước Của Giana",
 "39": "Thử Thách Của Alice",
 "40": "Tìm Ennmaya",
 "41": "Điều Ước Của Nani",
 "42": "Truyền Thuyết Về Scythe",
 "43": "Truyền Thuyết Về Amelia",
 "44": "Truyền Thuyết Về Gabriel",
 "45": "Truyền Thuyết Về Angel"
});
 const missionName=m=>TASK_NAMES_VI[String(m.name)]||m.title||'Nhiệm Vụ Thực Tập';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const btn=(cls,text,fn)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
 function root(){let r=$('internship-view');if(!r){r=el('section','internship-view');r.id='internship-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from){origin=from||view;panel=null;note='';showView('internship');act({action:'open'});}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const row=itemCatalog?.[id];return (row&&itemPicture(row))||(row?.icon?'/assets/shops/items/'+row.icon+'.png':'');}
 function chip(k,n){const c=el('span','in-chip');const s=icon(k);if(s)c.append(img(s));c.append(el('b','',number(n)));return c;}
 async function act(req){if(busyLocal)return null;busyLocal=true;note='';try{const r=await api('/api/internship/action',req);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busyLocal=false;if(view==='internship')render();}}
 let loadedAt=performance.now();const now=()=>(state.server_time||0)+Math.floor((performance.now()-loadedAt)/1000);
 const hms=s=>{s=Math.max(0,s);return [Math.floor(s/3600),Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':');};
 function condIcons(m){const w=el('span','in-conds');if(m.partner_star>0){const r=img(A('pub_star_require'+Math.min(6,m.partner_star)),'in-req');r.title=`Cần một Nữ Thần từ ${m.partner_star}★ trở lên`;w.append(r);}
  for(const c of m.conds){if(c.group){const g=img(A('img_group'+c.group),'in-cond');g.title="Hệ "+c.group;w.append(g);}if(c.job){const j=img(A('pub_job_icon'+c.job),'in-cond');j.title='Nghề '+c.job;w.append(j);}}return w;}
 // TavernWindow (tavern_window prefab): "Quest(n/daily) will be reset hh:mm:ss" + help; one pub_mis_bg1 row per quest
 // (name, lock button, pub_mission_starN bar, progress bar, reward icon, timer); star filters pub_sort1-7 and
 // Use / Multi-Intern / Claim in bulk at the bottom. Tap an idle row to pick the Girls (TavernDetailWindow).
 let starFilter=new Set();
 const H=s=>s%3600===0?s/3600+'H':hms(s);
 function reward(m){const w=el('div','in-reward');const [k,n]=Object.entries(m.award||{})[0]||[];if(!k){w.append(el('span','in-q','?'));return w;}const row=itemCatalog?.[k];const q=Math.min(Math.max(row?.quality||1,1),7);w.style.backgroundImage=`url('/assets/ui/quality_${q}.png')`;const s=icon(k);if(s)w.append(img(s));w.append(el('b','',number(n)));w.title=(window.GxbBagVi?.t?.(row?.name||k)||row?.name||k)+' ×'+n;return w;}
 async function multi(info){let started=0;for(const m of info.missions.filter(m=>m.state==='idle'&&(!starFilter.size||starFilter.has(m.star)))){const fresh=state.internship_info;const ids=auto(m,fresh);if(ids.length!==m.partner_num||meets(m,ids).some(x=>!x))continue;const r=await act({action:'start',mission:m.id,partners:ids});if(r)started++;}note=started?`Đã bắt đầu ${started} nhiệm vụ`:"Không có Nữ Thần phù hợp điều kiện";render();}
 async function claimAll(info){const got={};let n=0;for(const m of info.missions.filter(m=>m.state==='done')){const r=await act({action:'complete',mission:m.id});if(r?.got){n++;for(const [k,v]of Object.entries(r.got))got[k]=(got[k]||0)+v;}}if(n)CampaignUI.popup(`Đã hoàn thành ${n} nhiệm vụ Thực Tập!`,got);else{note="Không có nhiệm vụ đã hoàn thành";render();}}
 function useScroll(info){const {body,close}=GirlUI.win({title:'Dùng Vé Thực Tập',cls:'in-usewin'});for(const [id,idx,label]of [['24',1,'Vé Thực Tập · 1–4★'],['25',2,'Vé Thực Tập Cao Cấp · 4–7★']]){const b=btn('in-usebtn','',async()=>{if(!info.scrolls[id]){GirlUI.toast(idx===1?"Không có Vé Thực Tập!":"Không có Vé Thực Tập Cao Cấp!");return;}close();const r=await act({action:'scroll',index:idx});if(r){note="Đã thêm nhiệm vụ mới!";render();}});b.append(img(A('icon_'+id)),el('span','',label),el('b','','×'+info.scrolls[id]));body.append(b);}
 }
 function refreshPreview(info){const idle=info.missions.filter(m=>m.state==='idle'&&!m.locked).length;const cost=Object.fromEntries(Object.entries(info.refresh_cost).map(([k,n])=>[k,n*idle]));const {body,close}=GirlUI.win({title:'Làm Mới Nhiệm Vụ',cls:'in-usewin'});body.append(el('p','',idle?`Làm mới sẽ thay ${idle} nhiệm vụ chưa bắt đầu. Nhiệm vụ đã khóa, đang thực hiện và hoàn thành được giữ nguyên.`:"Không có nhiệm vụ chưa bắt đầu và chưa khóa để làm mới."));if(!idle)return;const price=el('div','in-refresh-cost');price.append(el('span','',"Chi phí: "));for(const [k,n]of Object.entries(cost))price.append(chip(k,n));body.append(price);const yes=btn('in-usebtn','Làm Mới',async()=>{yes.disabled=true;const res=await act({action:'refresh'});if(res){close();note=`Đã làm mới ${res.refreshed} nhiệm vụ`;render();}else yes.disabled=false;});body.append(yes,btn('in-usebtn',"Hủy",close));}

 function render(){const r=root();if(view!=='internship'){clearInterval(timer);timer=null;return;}loadedAt=performance.now();const info=state.internship_info;r.replaceChildren();const st=el('div','in-stage');r.append(st);
  const top=el('div','in-top');const back=btn('in-back','',()=>showView(origin==='internship'?'campus':origin));back.append(img('/assets/ui/win_back_btn.png'));
  top.append(el('strong','in-title-vi','Thực Tập'),back);st.append(top);
  if(!info){st.append(el('p','in-note',"Đang tải…"));return;}
  const head=el('div','in-head');const hb=btn('in-help','',()=>{
   const win=GirlUI.win({title:'Hướng Dẫn Thực Tập',cls:'in-helpwin'});
   const lines=[
    'Cử Nữ Thần tham gia nhiệm vụ 1★–7★ để nhận thưởng. Mỗi Nữ Thần chỉ được tham gia một nhiệm vụ tại một thời điểm.',
    'Mỗi nhiệm vụ yêu cầu số Nữ Thần, số sao, hệ hoặc nghề phù hợp. Chỉ khi đáp ứng đủ điều kiện mới có thể bắt đầu.',
    'Nhiệm vụ mới mỗi ngày: '+info.daily+'; tối đa '+info.max+' nhiệm vụ. Dùng Vé Thực Tập để nhận thêm nhiệm vụ.',
    'Có thể làm mới nhiệm vụ chưa bắt đầu và chưa khóa. Nhiệm vụ đã khóa, đang thực hiện hoặc đã hoàn thành được giữ nguyên.',
    'Có thể tăng tốc bằng Kim Cương hoặc chờ đến thời gian hoàn thành, sau đó nhận thưởng.',
    'Dùng Cử Hàng Loạt để phân công Nữ Thần đủ điều kiện; Nhận Tất Cả để nhận những nhiệm vụ đã hoàn thành.'
   ];
   const wrapper=el('div','in-help-content');
   for(const line of lines)wrapper.append(el('p','in-help-paragraph',line));
   win.body.append(wrapper);
  });hb.append(img(A('help_2')));
  const reset=el('b','in-reset');reset.dataset.end=info.next_day;head.append(hb,el('span','',`Nhiệm vụ (${info.missions.length}/${info.daily}) · Làm mới sau: `),reset);st.append(head);
  const list=el('div','in-list');const shown=info.missions.filter(m=>!starFilter.size||starFilter.has(m.star));
  if(!shown.length)list.append(el('p','in-note',"Chưa có nhiệm vụ. Ngày mai sẽ có thêm, hoặc dùng Vé Thực Tập."));
  for(const m of shown){const row=el('div','in-row s'+m.star+' '+m.state);row.onclick=e=>{if(m.state==='idle'&&!e.target.closest('button')){pick=[];panel=m.id;render();}};
   row.append(el('b','in-name',missionName(m)),el('i','in-line'));
   const lk=btn('in-lock','',()=>act({action:'lock',mission:m.id}));lk.append(img(A(m.locked?'partner_lock_btn':'partner_unlock_btn')));lk.title=m.locked?"Đã khóa: không làm mới":"Khóa để giữ lại nhiệm vụ";lk.disabled=m.state!=='idle';row.append(lk);
   const stars=el('div','in-stars');stars.style.borderImageSource=`url('${A('pub_mission_star'+m.star)}')`;for(let k=0;k<m.star;k++)stars.append(img(A('pub_mission_star')));row.append(stars);
   const prog=el('div','in-prog');const fill=el('i');const lab=el('span');if(m.state==='idle'){lab.textContent='Chưa bắt đầu';}else if(m.state==='running'){fill.dataset.end=m.end;fill.dataset.len=m.time;lab.className='in-clock';lab.dataset.end=m.end;lab.textContent=hms(m.end-now());fill.style.width=Math.min(100,100*(1-(m.end-now())/m.time))+'%';}else{fill.style.width='100%';lab.textContent='Đã hoàn thành';}prog.append(fill,lab);row.append(prog);
   row.append(reward(m));
   if(m.state==='idle'){const t=el('div','in-time');t.append(img(A('pub_timer1')),el('b','',H(m.time)));row.append(t);}
   else if(m.state==='running'){const sp=m.speedup;const spd=btn('in-rbtn blue','',async()=>{const c=sp['2']||0;if(c&&!await GirlUI.confirm(`Dùng ${c} Kim Cương để hoàn thành ngay?`,{title:"Tăng Tốc Thực Tập",ok:"Hoàn Thành"}))return;await act({action:'speed',mission:m.id});});if(sp['2'])spd.append(img('/assets/currency/icon_2_small.png'),el('small','',String(sp['2'])));spd.append(el('span','','Tăng Tốc'));row.append(spd);const cn=btn('in-cancel','',async()=>{if(await GirlUI.confirm("Hủy nhiệm vụ thực tập? Các Nữ Thần sẽ được giải phóng.",{title:"Hủy Nhiệm Vụ",ok:"Hủy",danger:true}))await act({action:'cancel',mission:m.id});});cn.append(img(A('pub_cancel_btn')));cn.title='Hủy';row.append(cn);}
   else row.append(btn('in-rbtn blue done','Nhận Thưởng',async()=>{const res=await act({action:'complete',mission:m.id});if(res?.got)CampaignUI.popup(`Đã hoàn thành nhiệm vụ Thực Tập ${res.star}★!`,res.got);}));
   list.append(row);}
  st.append(list);
  const sorts=el('div','in-sorts');for(let s=1;s<=7;s++){const b=btn('in-sort'+(starFilter.has(s)?' on':''),'',()=>{starFilter.has(s)?starFilter.delete(s):starFilter.add(s);render();});b.append(img(A('pub_sort'+s)));if(starFilter.has(s))b.append(img(A('select'),'in-sel'));b.title=s+'★';sorts.append(b);}const refresh=btn('in-refresh-native','',()=>refreshPreview(info));refresh.append(img('/assets/ui/switch_btn.png'));refresh.title='Làm Mới Nhiệm Vụ';refresh.setAttribute('aria-label','Làm Mới Nhiệm Vụ');sorts.append(refresh);st.append(sorts);
  const bottom=el('div','in-bottom');const use=btn('in-bbtn','',()=>useScroll(info));use.append(img(A('icon_ticket')),el('span','','Dùng Vé'));bottom.append(use,btn('in-bbtn','Cử Hàng Loạt',()=>multi(info)),btn('in-bbtn','Nhận Tất Cả',()=>claimAll(info)));st.append(bottom);
  if(note)st.append(el('p','in-note in-err',note));
  if(panel)picker(st,info,info.missions.find(m=>m.id===panel));
  clearInterval(timer);timer=setInterval(()=>{if(view!=='internship'){clearInterval(timer);return;}let done=false;const rs=root().querySelector('.in-reset');if(rs)rs.textContent=hms(Number(rs.dataset.end)-now());root().querySelectorAll('.in-clock').forEach(c=>{const left=Number(c.dataset.end)-now();c.textContent=hms(left);if(left<=0)done=true;});root().querySelectorAll('.in-prog i[data-end]').forEach(f=>{f.style.width=Math.min(100,100*(1-(Number(f.dataset.end)-now())/Number(f.dataset.len)))+'%';});if(done){clearInterval(timer);api('/api/state').then(x=>{state=x;render();}).catch(()=>{});}},1000);
  {const rs=root().querySelector('.in-reset');if(rs)rs.textContent=hms(info.next_day-now());}}
 // TavernDetailWindow: choose partner_num free Girls; the conditions light up when met.
 function meets(m,ids){const byId=new Map((state.roster||[]).map(h=>[h.partner_id,h]));const girls=ids.map(i=>byId.get(i)).filter(Boolean);const needs=[];
  if(m.partner_star>0)needs.push(h=>h.stars>=m.partner_star);for(const c of m.conds){if(c.group)needs.push(h=>h.group===c.group);if(c.job)needs.push(h=>h.job===c.job);}
  const match=new Map();const assign=(i,seen)=>{for(const g of girls){if(seen.has(g.partner_id)||!needs[i](g))continue;seen.add(g.partner_id);if(!match.has(g.partner_id)||assign(match.get(g.partner_id),seen)){match.set(g.partner_id,i);return true;}}return false;};
  return needs.map((_,i)=>assign(i,new Set()));}
 function auto(m,info){const free=(state.roster||[]).filter(h=>!info.busy.includes(h.partner_id)).sort((a,b)=>b.stars-a.stars||b.lv-a.lv);const chosen=[];const take=f=>{const g=free.find(h=>!chosen.includes(h.partner_id)&&f(h));if(g)chosen.push(g.partner_id);};
  if(m.partner_star>0)take(h=>h.stars>=m.partner_star);for(const c of m.conds){if(c.group)take(h=>h.group===c.group);if(c.job)take(h=>h.job===c.job);}for(const h of free){if(chosen.length>=m.partner_num)break;if(!chosen.includes(h.partner_id))chosen.push(h.partner_id);}return chosen.slice(0,m.partner_num);}
 function picker(st,info,m){if(!m){panel=null;return;}const ov=el('div','in-overlay');ov.onclick=e=>{if(e.target===ov){panel=null;render();}};const w=el('div','in-win');ov.append(w);
  w.append(el('h2','',missionName(m)),btn('in-close','✕',()=>{panel=null;render();}));const ok=meets(m,pick);
  const req=el('div','in-reqs');let i=0;if(m.partner_star>0){const c=el('span','in-reqitem'+(ok[i++]?' ok':''));c.append(img(A('pub_star_require'+Math.min(6,m.partner_star))),el('small','',`≥${m.partner_star}★`));req.append(c);}
  for(const c of m.conds){if(c.group){const e=el('span','in-reqitem'+(ok[i++]?' ok':''));e.append(img(A('img_group'+c.group)));req.append(e);}if(c.job){const e=el('span','in-reqitem'+(ok[i++]?' ok':''));e.append(img(A('pub_job_icon'+c.job)));req.append(e);}}
  w.append(el('p','',`Điều kiện (${m.partner_num} Nữ Thần, ${hms(m.time)}):`),req);
  const slots=el('div','in-slots');for(let k=0;k<m.partner_num;k++){const pid=pick[k];const h=(state.roster||[]).find(x=>x.partner_id===pid);const s=btn('in-slot','',()=>{if(pid){pick=pick.filter(x=>x!==pid);render();}});if(h)s.append(typeof portrait==='function'?portrait(h.table_id,64):el('span'));slots.append(s);}w.append(slots);
  const pool=el('div','in-pool');for(const h of [...(state.roster||[])].sort((a,b)=>b.stars-a.stars||b.lv-a.lv)){const isBusy=info.busy.includes(h.partner_id);const on=pick.includes(h.partner_id);const c=btn('in-cand'+(on?' on':'')+(isBusy?' busy':''),'',()=>{if(isBusy)return;if(on)pick=pick.filter(x=>x!==h.partner_id);else if(pick.length<m.partner_num)pick.push(h.partner_id);render();});c.disabled=isBusy;
   c.append(typeof portrait==='function'?portrait(h.table_id,56):el('span'),el('small','',`${h.stars}★`));if(h.group)c.append(img(A('img_group'+h.group),'in-g'));c.title=h.name+(isBusy?" (đang thực tập)":'');pool.append(c);}
  w.append(pool);const acts=el('div','in-acts');acts.append(btn('in-small','Tự Chọn',()=>{pick=auto(m,info);render();}),btn('in-go','Bắt Đầu',async()=>{if(pick.length!==m.partner_num||ok.some(x=>!x)){note="Các Nữ Thần chưa đáp ứng điều kiện nhiệm vụ";render();return;}panel=null;await act({action:'start',mission:m.id,partners:pick});}));w.append(acts);st.append(ov);}
 return {open,render};
})();
