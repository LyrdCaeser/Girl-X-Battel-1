'use strict';
// GrowthDiaryWindow: 40 pages, four missions, star-marked tasks start at chapter unlock.
const GrowthDiary=(()=>{
 let chapter=1,origin='home',busy=false,note='';
 const A=n=>'/assets/growth-diary/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const button=(text,fn,disabled=false)=>{const b=el('button','gd-button',text);b.type='button';b.onclick=fn;b.disabled=disabled||busy;return b;};
 const icon=id=>{if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const it=itemCatalog?.[id];return (typeof itemPicture==='function'&&it&&itemPicture(it))||'/assets/ui/item_bg.png';};
 const image=(src)=>{const i=el('img');i.src=src;i.alt='';return i;};
 function rewards(text){const r=el('div','gd-rewards');for(const v of String(text).split('|')){const [id,n]=v.split('#');if(!n)continue;const item=el('span');item.title=itemCatalog?.[id]?.name||id;item.append(image(icon(id)),el('b','',number(n)));r.append(item);}return r;}
 function root(){let r=$('growth-diary-view');if(!r){r=el('section','gd-view');r.id='growth-diary-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function act(req){if(busy)return;busy=true;note='';try{const res=await api('/api/growth-diary/action',req);state=res.state;if(req.action==='chapter')chapter=state.growth_diary_info.current;if(Object.keys(res.got||{}).length)CampaignUI.popup('Reward',res.got);}catch(e){note=e.message;}finally{busy=false;render();}}
 async function open(from){origin=from||view;chapter=state.growth_diary_info.current;root();showView('growth-diary');render();if(state.growth_diary_info.unlocked)await act({action:'open'});}
 const GO={campaign_window:'campaign',slot_window:'girls',summon_window:'capsule',altar_window:'transfer',market_window:'black-market',gamble_window:'slots',pet_window:'servant',guild_lab_window:'guild-lab',arena_window:'arena',tavern_window:'intern',smithy_window:'smithy',tower_window:'tests',time_cloister_main_window:'echoes',trial_window:'sanctuary',trial_enter_window:'sanctuary',friend_window:'friends',dress_summon_window:'dress',house_window:'dorm',hero_challenge_window:'hero-challenge',explore_window:'expedition',guild_territory_window:'guild-territory',academy_assessment_window:'house-exam',starry_altar_window:'stellar-altar',dungeon_window:'patrol',old_school_main_window:'old-campus',shrine_hurdle_entrance_window:'shrine',prophet_window:'enroll',arena_3v3_window:'arena3v3',shenxue_window:'graduate',background_window:'settings',pet_start_window:'pet-training'};
 function go(task){if(task.id===99){openMenu('friend-boss','growth-diary');return;}const target=GO[task.window];if(!target)return;if(target==='smithy'){Equipment.openSmithy(1,'growth-diary');return;}if(['campaign','girls','capsule','graduate'].includes(target))showView(target);else openMenu(target,'growth-diary');}
 function render(){const r=root();if(view!=='growth-diary')return;const info=state.growth_diary_info;if(!info)return;r.replaceChildren();
  const top=el('header','gd-top');top.append(el('h1','','Growth Diary'),button('Back',()=>showView(origin==='growth-diary'?'home':origin)));r.append(top);
  if(!info.unlocked){r.append(el('p','gd-message','Unlock after Campaign Stage '+info.unlock_stage));return;}
  const page=info.chapters.find(c=>c.id===chapter)||info.chapters[0];
  const book=el('div','gd-book');r.append(book);const nav=el('nav','gd-nav');
  nav.append(button('‹',()=>{chapter--;render();},chapter<=1),el('h2','','Chapter '+chapter),button('›',()=>{chapter++;render();},chapter>=info.chapters.length));book.append(nav);
  const summary=el('div','gd-chapter');summary.append(el('b','','Chapter Reward'),rewards(page.award),button(page.claimed?'Claimed':page.locked?'Locked':'Claim',()=>act({action:'chapter',id:page.id}),!page.can));book.append(summary);
  const list=el('div','gd-tasks');book.append(list);for(const task of page.tasks){const row=el('article','gd-task');const copy=el('div','gd-copy');copy.append(el('b','',task.text));if(task.special){const star=el('small','gd-special','★');star.title='Progress begins when this chapter unlocks';copy.prepend(star);}
   const bar=el('div','gd-bar');const fill=el('i');fill.style.width=Math.min(100,task.have/Math.max(1,task.need)*100)+'%';bar.append(fill,el('span','',task.have+'/'+task.need));copy.append(bar);row.append(copy,rewards(task.award));
   if(task.claimed)row.append(button('Claimed',null,true));else if(page.locked)row.append(button('Locked',null,true));else if(task.can)row.append(button('Claim',()=>act({action:'mission',id:task.id})));else if(!task.tracked){const b=button('Unavailable',null,true);b.title='This objective is not implemented locally yet';row.append(b);}else row.append(button('Go',()=>go(task),!GO[task.window]));list.append(row);}
  book.append(el('p','gd-foot',page.locked?'Unlock after completing the previous chapter':'★ Progress starts when the chapter unlocks.'));
  if(info.finished)book.append(el('p','gd-foot','All chapters completed'));if(note)r.append(el('p','gd-message',note));}
 document.addEventListener('DOMContentLoaded',()=>{const host=document.querySelector('.home-side.home-left');if(!host)return;const b=el('button','gd-home');b.type='button';b.title='Growth Diary';b.append(image(A('growth_diary_icon_h5')),el('small','','Growth Diary'));b.onclick=()=>open('home');host.prepend(b);});
 return {open,render,go,rewards,GO};
})();
