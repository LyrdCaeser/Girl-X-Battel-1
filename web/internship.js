'use strict';
// Internship (TavernWindow → TavernDetailWindow). Rules: gxb2/internship.py. Original sprites: pub_mission_star1-7,
// pub_star_require*, img_group*, pub_job_icon*, pub_lock / pub_un_lock, pub_timer1, icon_24 / icon_25.
const Internship=(()=>{
 let origin='campus',panel=null,note='',busyLocal=false,pick=[],timer=null;
 const A=n=>'/assets/internship/'+n+'.png';
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
 function condIcons(m){const w=el('span','in-conds');if(m.partner_star>0){const r=img(A('pub_star_require'+Math.min(6,m.partner_star)),'in-req');r.title=`One Girl of ${m.partner_star}★ or higher`;w.append(r);}
  for(const c of m.conds){if(c.group){const g=img(A('img_group'+c.group),'in-cond');g.title="Faction "+c.group;w.append(g);}if(c.job){const j=img(A('pub_job_icon'+c.job),'in-cond');j.title='Clase '+c.job;w.append(j);}}return w;}
 // TavernWindow (tavern_window prefab): "Quest(n/daily) will be reset hh:mm:ss" + help; one pub_mis_bg1 row per quest
 // (name, lock button, pub_mission_starN bar, progress bar, reward icon, timer); star filters pub_sort1-7 and
 // Use / Multi-Intern / Claim in bulk at the bottom. Tap an idle row to pick the Girls (TavernDetailWindow).
 let starFilter=new Set();
 const H=s=>s%3600===0?s/3600+'H':hms(s);
 function reward(m){const w=el('div','in-reward');const [k,n]=Object.entries(m.award||{})[0]||[];if(!k){w.append(el('span','in-q','?'));return w;}const row=itemCatalog?.[k];const q=Math.min(Math.max(row?.quality||1,1),7);w.style.backgroundImage=`url('/assets/ui/quality_${q}.png')`;const s=icon(k);if(s)w.append(img(s));w.append(el('b','',number(n)));w.title=(row?.name||k)+' ×'+n;return w;}
 async function multi(info){let started=0;for(const m of info.missions.filter(m=>m.state==='idle'&&(!starFilter.size||starFilter.has(m.star)))){const fresh=state.internship_info;const ids=auto(m,fresh);if(ids.length!==m.partner_num||meets(m,ids).some(x=>!x))continue;const r=await act({action:'start',mission:m.id,partners:ids});if(r)started++;}note=started?`${started} encargo(s) empezados`:"No available Girls meet the conditions";render();}
 async function claimAll(info){const got={};let n=0;for(const m of info.missions.filter(m=>m.state==='done')){const r=await act({action:'complete',mission:m.id});if(r?.got){n++;for(const [k,v]of Object.entries(r.got))got[k]=(got[k]||0)+v;}}if(n)CampaignUI.popup(`Completed ${n} Internship Quest(s)!`,got);else{note="No completed missions";render();}}
 function useScroll(info){const {body,close}=GirlUI.win({title:'Use',cls:'in-usewin'});for(const [id,idx,label]of [['24',1,'Internship Scroll · 1-4★'],['25',2,'Advanced Internship Scroll · 4-7★']]){const b=btn('in-usebtn','',async()=>{if(!info.scrolls[id]){GirlUI.toast(idx===1?"You don't have any Internship Scrolls!":"You don't have any Advanced Internship Scrolls!");return;}close();const r=await act({action:'scroll',index:idx});if(r){note="New mission added!";render();}});b.append(img(A('icon_'+id)),el('span','',label),el('b','','×'+info.scrolls[id]));body.append(b);}
 }
 function refreshPreview(info){const idle=info.missions.filter(m=>m.state==='idle'&&!m.locked).length;const cost=Object.fromEntries(Object.entries(info.refresh_cost).map(([k,n])=>[k,n*idle]));const {body,close}=GirlUI.win({title:'Refresh Quests',cls:'in-usewin'});body.append(el('p','',idle?`Refresh will replace ${idle} unstarted missions. Locked, running, and completed missions are preserved.`:"No unlocked, unstarted missions available to refresh."));if(!idle)return;const price=el('div','in-refresh-cost');price.append(el('span','',"Cost: "));for(const [k,n]of Object.entries(cost))price.append(chip(k,n));body.append(price);const yes=btn('in-usebtn','Refresh',async()=>{yes.disabled=true;const res=await act({action:'refresh'});if(res){close();note=`${res.refreshed} encargo(s) renovados`;render();}else yes.disabled=false;});body.append(yes,btn('in-usebtn',"Cancel",close));}

 function render(){const r=root();if(view!=='internship'){clearInterval(timer);timer=null;return;}loadedAt=performance.now();const info=state.internship_info;r.replaceChildren();const st=el('div','in-stage');r.append(st);
  const top=el('div','in-top');const back=btn('in-back','',()=>showView(origin==='internship'?'campus':origin));back.append(img('/assets/ui/win_back_btn.png'));
  top.append(img(A('tavern_text_en_en'),'in-title'),back);st.append(top);
  if(!info){st.append(el('p','in-note',"Loading…"));return;}
  const head=el('div','in-head');const hb=btn('in-help','',()=>CampaignUI.popup("Internship: send Girls on missions from 1★ to 7★. Each mission requires a number of Girls, one meeting the minimum star rank, and Girls from specific factions or classes. Claim rewards when it finishes. New missions per day: "+info.daily+" (maximum "+info.max+"); scrolls add one mission. Lock a mission to protect it from Refresh.",{}));hb.append(img(A('help_2')));
  const reset=el('b','in-reset');reset.dataset.end=info.next_day;head.append(hb,el('span','',`Quest(${info.missions.length}/${info.daily})will be reset `),reset);st.append(head);
  const list=el('div','in-list');const shown=info.missions.filter(m=>!starFilter.size||starFilter.has(m.star));
  if(!shown.length)list.append(el('p','in-note',"No missions. More arrive tomorrow, or use a scroll."));
  for(const m of shown){const row=el('div','in-row s'+m.star+' '+m.state);row.onclick=e=>{if(m.state==='idle'&&!e.target.closest('button')){pick=[];panel=m.id;render();}};
   row.append(el('b','in-name',m.title),el('i','in-line'));
   const lk=btn('in-lock','',()=>act({action:'lock',mission:m.id}));lk.append(img(A(m.locked?'partner_lock_btn':'partner_unlock_btn')));lk.title=m.locked?"Locked: excluded from Refresh":"Lock to protect from Refresh";lk.disabled=m.state!=='idle';row.append(lk);
   const stars=el('div','in-stars');stars.style.borderImageSource=`url('${A('pub_mission_star'+m.star)}')`;for(let k=0;k<m.star;k++)stars.append(img(A('pub_mission_star')));row.append(stars);
   const prog=el('div','in-prog');const fill=el('i');const lab=el('span');if(m.state==='idle'){lab.textContent='Not yet started';}else if(m.state==='running'){fill.dataset.end=m.end;fill.dataset.len=m.time;lab.className='in-clock';lab.dataset.end=m.end;lab.textContent=hms(m.end-now());fill.style.width=Math.min(100,100*(1-(m.end-now())/m.time))+'%';}else{fill.style.width='100%';lab.textContent='Completed';}prog.append(fill,lab);row.append(prog);
   row.append(reward(m));
   if(m.state==='idle'){const t=el('div','in-time');t.append(img(A('pub_timer1')),el('b','',H(m.time)));row.append(t);}
   else if(m.state==='running'){const sp=m.speedup;const spd=btn('in-rbtn blue','',async()=>{const c=sp['2']||0;if(c&&!await GirlUI.confirm(`Dùng ${c} Kim Cương để hoàn thành ngay?`,{title:"Tăng Tốc Thực Tập",ok:"Hoàn Thành"}))return;await act({action:'speed',mission:m.id});});if(sp['2'])spd.append(img('/assets/currency/icon_2_small.png'),el('small','',String(sp['2'])));spd.append(el('span','','Speed up'));row.append(spd);const cn=btn('in-cancel','',async()=>{if(await GirlUI.confirm("Hủy nhiệm vụ thực tập? Các Nữ Thần sẽ được giải phóng.",{title:"Hủy Nhiệm Vụ",ok:"Hủy",danger:true}))await act({action:'cancel',mission:m.id});});cn.append(img(A('pub_cancel_btn')));cn.title='Cancel';row.append(cn);}
   else row.append(btn('in-rbtn blue done','Complete',async()=>{const res=await act({action:'complete',mission:m.id});if(res?.got)CampaignUI.popup(`Completed ${res.star} Star Internship Quest!`,res.got);}));
   list.append(row);}
  st.append(list);
  const sorts=el('div','in-sorts');for(let s=1;s<=7;s++){const b=btn('in-sort'+(starFilter.has(s)?' on':''),'',()=>{starFilter.has(s)?starFilter.delete(s):starFilter.add(s);render();});b.append(img(A('pub_sort'+s)));if(starFilter.has(s))b.append(img(A('select'),'in-sel'));b.title=s+'★';sorts.append(b);}const refresh=btn('in-refresh-native','',()=>refreshPreview(info));refresh.append(img('/assets/ui/switch_btn.png'));refresh.title='Refresh Quests';refresh.setAttribute('aria-label','Refresh Quests');sorts.append(refresh);st.append(sorts);
  const bottom=el('div','in-bottom');const use=btn('in-bbtn','',()=>useScroll(info));use.append(img(A('icon_ticket')),el('span','','Use'));bottom.append(use,btn('in-bbtn','Multi-Intern',()=>multi(info)),btn('in-bbtn','Claim in Bulk',()=>claimAll(info)));st.append(bottom);
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
  w.append(el('h2','',m.title),btn('in-close','✕',()=>{panel=null;render();}));const ok=meets(m,pick);
  const req=el('div','in-reqs');let i=0;if(m.partner_star>0){const c=el('span','in-reqitem'+(ok[i++]?' ok':''));c.append(img(A('pub_star_require'+Math.min(6,m.partner_star))),el('small','',`≥${m.partner_star}★`));req.append(c);}
  for(const c of m.conds){if(c.group){const e=el('span','in-reqitem'+(ok[i++]?' ok':''));e.append(img(A('img_group'+c.group)));req.append(e);}if(c.job){const e=el('span','in-reqitem'+(ok[i++]?' ok':''));e.append(img(A('pub_job_icon'+c.job)));req.append(e);}}
  w.append(el('p','',`Condiciones (${m.partner_num} Girl${m.partner_num>1?'s':''}, ${hms(m.time)}):`),req);
  const slots=el('div','in-slots');for(let k=0;k<m.partner_num;k++){const pid=pick[k];const h=(state.roster||[]).find(x=>x.partner_id===pid);const s=btn('in-slot','',()=>{if(pid){pick=pick.filter(x=>x!==pid);render();}});if(h)s.append(typeof portrait==='function'?portrait(h.table_id,64):el('span'));slots.append(s);}w.append(slots);
  const pool=el('div','in-pool');for(const h of [...(state.roster||[])].sort((a,b)=>b.stars-a.stars||b.lv-a.lv)){const isBusy=info.busy.includes(h.partner_id);const on=pick.includes(h.partner_id);const c=btn('in-cand'+(on?' on':'')+(isBusy?' busy':''),'',()=>{if(isBusy)return;if(on)pick=pick.filter(x=>x!==h.partner_id);else if(pick.length<m.partner_num)pick.push(h.partner_id);render();});c.disabled=isBusy;
   c.append(typeof portrait==='function'?portrait(h.table_id,56):el('span'),el('small','',`${h.stars}★`));if(h.group)c.append(img(A('img_group'+h.group),'in-g'));c.title=h.name+(isBusy?" (on Internship)":'');pool.append(c);}
  w.append(pool);const acts=el('div','in-acts');acts.append(btn('in-small','Auto',()=>{pick=auto(m,info);render();}),btn('in-go','Start',async()=>{if(pick.length!==m.partner_num||ok.some(x=>!x)){note="Girls do not meet the mission requirements";render();return;}panel=null;await act({action:'start',mission:m.id,partners:pick});}));w.append(acts);st.append(ov);}
 return {open,render};
})();
