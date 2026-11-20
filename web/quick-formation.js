'use strict';
// Lineup presets (QuickFormationWindow, capture 2026-09-29-fb/44): tabs Lineup 1-3 (+ locked), the lineup power and Set,
// one row per position (Front 1-2, Back 1-4) with the girl, her saved gear and potentials and a remove button, Return / Save
// (the current battle formation). Rules: gxb2/quick_formation.py. Prefix qf-.
const QuickFormation=(()=>{
 let origin='girls',idx=0,pots=null,eq=null;
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 const POS=['','Front 1','Front 2','Back 1','Back 2','Back 3','Back 4'],ART=['partner_weapon','partner_cloth','partner_pants','partner_shoes','partner_treasure','partner_artifact'];
 function root(){let r=$('quick-formation-view');if(!r){r=el('section','quick-formation-view');r.id='quick-formation-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function open(from){origin=from||view;root();if(!pots)pots=await api('/assets/potentials.json').catch(()=>({skills:{}}));if(typeof Equipment!=='undefined')eq=await Equipment.load().catch(()=>null);showView('quick-formation');render();const g=$('game-root');if(g)g.scrollTop=0;}
 async function act(req,msg){try{const r=await api('/api/quick-formation/action',{index:idx,...req});state=r.state;if(msg)toast(msg);if(r.missing?.length)toast("Missing "+r.missing.length+" pieces of equipment; the rest was applied.");return r;}catch(e){toast(e.message);return null;}finally{if(view==='quick-formation')render();}}
 function toast(t){if(typeof GirlUI!=='undefined')GirlUI.toast(t);}
 function gearIcon(id,slot){const w=el('span','qf-gear');if(id&&eq?.items?.[id]){w.style.backgroundImage=`url('/assets/ui/quality_${Math.min(eq.items[id].qlt||0,7)}.png')`;w.append(img(Equipment.icon(id)||'/assets/ui/item_bg.png'));w.title=eq.items[id].name;}else{w.classList.add('empty');w.append(img('/assets/detail/sheet/'+ART[slot]+'.png'));}return w;}
 function render(){const r=root();if(view!=='quick-formation')return;const info=state.quick_formation_info||{};r.replaceChildren();
  const top=el('div','qf-top');top.append(btn('qf-help','?',()=>CampaignUI.popup("1. Lineups unlock after clearing stage 8-5.\n2. Prepare multiple lineups without changing your current team.\n3. They save each Girl's equipment, Crystal, Antique, and Potentials.\n4. Set applies the lineup as your battle team and equips its gear.\n5. There are 3 free lineups.",{})));
  const back=btn('qf-back','',()=>showView(origin==='quick-formation'?'girls':origin));back.append(img('/assets/ui/win_back_btn.png'));top.append(back);r.append(top);
  if(!info.open){r.append(el('p','qf-note','Available after passing Stage 8-5 in Campaign'));return;}
  const tabs=el('div','qf-tabs');info.lineups.forEach((l,i)=>{const b=btn('qf-tab'+(i===idx?' on':''),l.name,()=>{idx=i;render();});b.ondblclick=async()=>{const n=await GirlUI.promptText('Tên mới cho đội hình (tối đa 6 ký tự)',{title:'Đổi Tên Đội Hình',value:l.name,maxLength:6});if(n)act({action:'rename',name:n},'Đã Đổi Tên');};tabs.append(b);});tabs.append(btn('qf-tab add','+',()=>toast('Locked')));r.append(tabs);
  const lineup=info.lineups[idx];const byId=new Map(state.roster.map(h=>[h.partner_id,h]));
  const head=el('div','qf-head');const power=lineup.team.reduce((a,t)=>a+Number(byId.get(t.partner_id)?.power||0),0);head.append(img('/assets/detail/sheet/force_icon.png','qf-force'),el('b','',power?number(power):'—'),btn('gs-btn white qf-set','Set',()=>act({action:'set'},"Lineup applied to your team"),!lineup.team.length));r.append(head);
  const list=el('div','qf-list');
  for(let pos=1;pos<=6;pos++){const t=lineup.team.find(x=>x.pos===pos);const row=el('div','qf-row');row.append(el('b','qf-pos'+(pos<=2?' front':' back'),POS[pos]));
   if(!t){row.append(el('p','qf-empty',"Empty"));list.append(row);continue;}const h=byId.get(t.partner_id);
   const face=el('div','qf-face');if(typeof portrait==='function')face.append(portrait(h?.table_id,64));face.append(el('small','',String(h?.lv||'')));row.append(face);
   const gear=el('div','qf-gears');[1,2,3,4,5,6].forEach((s,k)=>gear.append(gearIcon(Number((t.equips||[])[s-1]||0),k)));row.append(gear);
   const pp=el('div','qf-pots');(h?.potential_options||[]).forEach((opts,i)=>{const pick=(t.potentials||[])[i],id=pick&&opts[pick-1],info=id&&pots.skills[String(id)];const c=el('span','qf-pot');if(info?.icon)c.append(img('/assets/skills/'+info.icon+'.png'));c.title=info?.name||'—';pp.append(c);});row.append(pp);
   row.append(btn('qf-remove','−',()=>{const team=lineup.team.filter(x=>x!==t).map(x=>({partner_id:x.partner_id,pos:x.pos}));act({action:'save',team});}));list.append(row);}
  r.append(list);const foot=el('div','qf-foot');foot.append(btn('gs-btn white','Return',()=>showView(origin==='quick-formation'?'girls':origin)),btn('gs-btn','Lưu',async()=>{if(await GirlUI.confirm('Lưu đội hình hiện tại?',{title:'Lưu Đội Hình',ok:'Lưu'}))act({action:'save'},'Đã lưu');}));r.append(foot);}
 // entry next to "← Collection" in the formation panel
 document.addEventListener('DOMContentLoaded',()=>{const ref=$('girls-return');if(ref&&!$('qf-open')){const b=el('button','secondary','Lineups');b.id='qf-open';b.type='button';b.onclick=()=>open('girls');ref.after(' ',b);}});
 return {open,render};
})();
