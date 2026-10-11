'use strict';
const FireworkProject=(()=>{
 let data=null,loading=null,host=null,busy=false,page='shop',message='',last={};
 const el=(t,c,text)=>{const e=document.createElement(t);if(c)e.className=c;if(text!==undefined)e.textContent=text;return e;};
 const img=(name,cls)=>{const i=el('img',cls);i.src='/assets/firework-project/'+name+'.png';i.alt='';return i;};
 const btn=(text,fn,disabled=false)=>{const b=el('button','pe-button',text);b.type='button';b.disabled=busy||disabled;b.onclick=fn;return b;};
 function rewards(text){const box=el('div','pe-rewards');for(const part of text.split('|')){const [id,n]=part.split('#');const item=itemCatalog[id];const src=['1','2'].includes(id)?'/assets/currency/icon_'+id+'_small.png':(item?itemPicture(item):'');const row=el('span','pe-reward');row.title=item?.name||(id==='1'?"Gold":id==='2'?"Gems":"Item "+id);if(src){const i=el('img');i.src=src;i.alt=row.title;row.append(i);}else row.append(el('small','',row.title));row.append(el('b','',number(Number(n))));box.append(row);}return box;}
 async function act(req){if(busy)return;busy=true;message='';paint();try{const r=await api('/api/firework-project/action',req);state=r.state;last=r.got;message=req.action==='craft'?"Crafting completed!":"Rewards added to your Bag.";host?.closest('#events-view')?.querySelectorAll('.ev-money b').forEach((b,i)=>b.textContent=number(state.items[String(i+1)]||0));}catch(e){message=e.message;}finally{busy=false;paint();}}
 function paint(){if(!host||!data)return;host.replaceChildren();const s=state.firework_project_info;const root=el('div','pe-root fw-project');host.append(root);root.append(img('activity_bomb_logo_en_en','fw-logo'));
  const toolbar=el('div','pe-toolbar');toolbar.append(rewards('225#'+s.dust+'|226#'+s.fireworks),btn("Daily supply +"+s.daily,()=>act({action:'daily'}),!s.daily_ready));root.append(toolbar);
  const nav=el('nav','fw-tabs');nav.append(btn("Store",()=>{page='shop';paint();}),btn('Fabricar',()=>{page='craft';paint();}),btn("Rates",()=>{page='rates';paint();}));root.append(nav);
  root.append(el('h3','',"Level "+s.level));const progress=el('progress');progress.max=data.level_step;progress.value=s.level_progress;root.append(progress,el('p','pe-instruction',s.level_progress+' / '+data.level_step+" dust to the next level"));
  if(page==='craft'){root.append(img('activity_bomb','fw-bomb'),el('p','pe-instruction',"Craft fireworks and level up to unlock rewards."));const cost=Number(data.cost.split('#')[1]);const actions=el('div','fw-tabs');actions.append(btn('Fabricar 1 · '+cost+" Dust",()=>act({action:'craft',num:1}),s.dust<cost),btn('Fabricar 10 · '+cost*10+" Dust",()=>act({action:'craft',num:10}),s.dust<cost*10));root.append(actions);}
  else if(page==='rates'){const total=Object.values(data.activity_bomb_make).reduce((n,r)=>n+r.weight,0);for(const row of Object.values(data.activity_bomb_make)){const card=el('div','pe-tier');card.append(rewards(row.awards),el('b','',(row.weight/total*100).toFixed(1)+' %'));root.append(card);}}
  else{const shop=el('div','pe-milestones');for(const row of s.shop){const card=el('div','pe-tier');card.append(rewards(row.awards),rewards(row.cost),el('small','',row.unlocked?"Remaining: "+row.left+' / '+row.limit:"Unlocks at level "+row.num/data.level_step));const [item,cost]=row.cost.split('#');card.append(btn(!row.unlocked?"Locked":row.left?"Redeem":"Sold out",()=>act({action:'buy',id:row.id}),!row.unlocked||!row.left||Number(state.items[item]||0)<Number(cost)));shop.append(card);}root.append(shop);}
  if(message){const box=el('div','pe-message');box.setAttribute('role','status');box.append(el('p','',message));if(Object.keys(last).length)box.append(rewards(Object.entries(last).map(([id,n])=>id+'#'+n).join('|')));root.append(box);}
 }
 async function render(parent){host=parent;page='shop';message='';last={};if(!loading)loading=api('/assets/firework-project.json').then(d=>data=d);await loading;paint();}
 return {render};
})();
