'use strict';
// Daily Tasks + Trophies (DailyMissionWindow.lua / AchievementWindow.lua). Rules: gxb2/missions.py.
const Missions=(()=>{
 let tab='daily',origin='home',note='',busyLocal=false;
 const A=n=>'/assets/missions/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;return i;};
 const GO={midas_window:'midas',tavern_window:'intern',summon_window:'capsule',campaign_window:'campaign',daily_quiz_window:'quiz',smithy_window:'smithy',gamble_window:'slots',arena_window:'arena'};
 function pairs(t){return String(t||'').split('|').filter(x=>x.includes('#')).map(x=>x.split('#'));}
 function root(){let r=$('missions-view');if(!r){r=el('section','missions-view');r.id='missions-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 function open(from){origin=from||view;note='';showView('missions');render();}
 async function act(req){if(busyLocal)return;busyLocal=true;note='';try{const r=await api('/api/missions/action',req);state=r.state;if(r.got)CampaignUI.popup("Reward",r.got);}catch(e){note=e.message;}finally{busyLocal=false;render();}}
 function icon(id){if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const it=itemCatalog?.[id];return (typeof itemPicture==='function'&&it&&itemPicture(it))||'/assets/ui/item_bg.png';}
 function go(win){const v=GO[win];if(!v)return;if(v==='midas'){if(typeof Midas!=='undefined')Midas.open();return;}if(v==='intern'){openMenu('intern','missions');return;}if(v==='quiz')openMenu('quiz');else if(v==='slots')openMenu('slots');else if(v==='arena')openMenu('arena','missions');else if(v==='smithy')Equipment.openSmithy(1,'missions');else showView(v);}
 function row(parent,text,have,need,award,btn){const r=el('div','ms-row');const l=el('div','ms-left');l.append(el('b','',text));const bar=el('div','ms-bar');const f=el('i');f.style.width=Math.min(100,(Number(have)||0)/Math.max(1,Number(need))*100)+'%';f.append(el('u'));bar.append(f,el('span','',(have==null?'—':Math.min(Number(have),Number(need)||Number(have)))+'/'+need));l.append(bar);r.append(l);
  const aw=el('div','ms-awards');for(const [id,n]of pairs(award)){const c=el('span','ms-award');const q=Number(n);c.append(img(icon(id)),el('b','',q>=1e6?(q/1e6)+'M':q>=1e4?(q/1e3)+'K':number(n)));c.title=(itemCatalog?.[id]?.name||id)+' ×'+number(n);aw.append(c);}r.append(aw,btn);parent.append(r);}
 function render(){const r=root();if(view!=='missions')return;const info=state.missions_info;r.replaceChildren();
  const top=el('header','ms-top');const back=el('button','ms-back');back.type='button';back.append(img('/assets/ui/win_back_btn.png'));back.onclick=()=>showView(origin==='missions'?'home':origin);top.append(el('h1','',tab==='daily'?'Daily Tasks':'Trophies'),back);r.append(top);
  const tabs=el('nav','ms-tabs');for(const [k,l,pos]of [['daily','Daily Tasks','left'],['trophy','Trophies','right']]){const b=el('button','ms-tab '+pos+(tab===k?' on':''),l);b.type='button';b.onclick=()=>{tab=k;render();};tabs.append(b);}r.append(tabs);
  const list=el('div','ms-list');r.append(list);if(!info){list.append(el('p','',"Loading…"));return;}
  if(tab==='daily'){for(const t of info.daily){const b=el('button','ms-btn');b.type='button';if(t.claimed){b.disabled=true;b.classList.add('done');b.append(img(A('mission_awarded_en_en')));}else if(t.have>=t.need&&state.level>=t.lv){b.textContent='Claim';b.onclick=()=>act({action:'daily',id:t.id});}else if(!t.tracked){b.textContent='—';b.disabled=true;b.title="This system is not available in the local version yet";}else if(state.level<t.lv){b.textContent='Lv.'+t.lv;b.disabled=true;}else{b.textContent='Go';b.classList.add('go');b.onclick=()=>go(t.window);}row(list,t.text,t.have,t.need,t.award,b);}
   list.append(el('p','ms-note',"Tasks reset at midnight."));}
  else{const items=[...info.trophies].sort((a,b)=>(b.can?1:0)-(a.can?1:0)||(a.done?1:0)-(b.done?1:0)||(b.tracked?1:0)-(a.tracked?1:0));for(const t of items){const b=el('button','ms-btn');b.type='button';if(t.done){b.disabled=true;b.classList.add('done');b.append(img(A('mission_awarded_en_en')));}else if(t.can){b.textContent='Claim';b.onclick=()=>act({action:'trophy',type:t.type});}else{b.textContent=t.tracked?'…':'—';b.disabled=true;}row(list,t.text.replace('{1}',t.need),t.have,t.need,t.award,b);}}
  if(note)r.append(el('p','ms-note err',note));}
 document.addEventListener('DOMContentLoaded',()=>{const right=document.querySelector('.home-side.home-right');if(!right)return;const b=document.createElement('button');b.type='button';b.title='Tasks';b.className='ms-home-btn';b.append(img(A('right_mission_icon_v3_h5')),el('small','','Tasks'));b.onclick=()=>open('home');right.prepend(b);});
 return {open,render};
})();
