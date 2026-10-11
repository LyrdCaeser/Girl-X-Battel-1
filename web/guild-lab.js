'use strict';
const GuildLab=(()=>{
 let origin='menu-explorer',job=1,page=0,selected=null,pending=false,note='',catalog=null,confirmReset=false;
 const jobs=['','Warrior','Mage','Ranger','Assassin','Priest'],A=n=>'/assets/original-ui/guild-lab/'+n+'.png';
 const el=(tag,cls,text)=>node(tag,cls,text),img=(name,cls='')=>{const i=el('img',cls);i.src=A(name);i.alt='';return i;};
 const button=(text,fn,cls='')=>{const b=el('button',cls,text);b.type='button';b.addEventListener('click',fn);return b;};
 function root(){let r=$('guild-lab-view');if(!r){r=el('section','guild-lab-view');r.id='guild-lab-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function open(from){origin=from||view;job=1;page=0;selected=null;note='';confirmReset=false;if(!catalog)catalog=await api('/assets/original-ui/guild-lab/catalog.json');root();showView('guild-lab');}
 async function send(message,data){if(pending)return;pending=true;note='';render();try{const res=await api('/api/action',{message,data});state=res.state;note=message==='GUILD_RESET_SKILL'?"Branch reset. Resources returned.":"Research saved.";confirmReset=false;}catch(e){note=e.message;}finally{pending=false;render();}}
 function resource(id,n){const wrap=el('span','gl-resource');const icon=el('img');icon.src=id===4?A('coin'):'/assets/currency/icon_'+(id===2?'2_small':'1_small')+'.png';icon.alt=id===4?"Guild Coins":id===2?"Gems":"Gold";wrap.append(icon,el('b','',number(n)));return wrap;}
 function cost(parent,values){for(const [k,v] of Object.entries(values))parent.append(resource(Number(k),v));}
 const affordable=values=>Object.entries(values).every(([k,v])=>Number(state.items[k]||0)>=v);
 function change(j,p){job=j;page=p;selected=null;confirmReset=false;note='';render();}
 function format(key,value){const b=catalog.buffs[key];return b?.show_percent===1?(value*100/(Number(b.factor)||1)).toFixed(1).replace('.0','')+'%':String(value);}
 function render(){if(view!=='guild-lab')return;const outer=root();outer.replaceChildren();const backdrop=el('div','gl-territory-backdrop');outer.append(backdrop);if(typeof GuildTerritory!=='undefined')GuildTerritory.paint(backdrop,false);const r=el('div','gl-modal');outer.append(r);const info=state.guild_lab_info;if(!info)return;const top=el('header','gl-top');top.append(resource(1,state.items['1']||0),resource(4,state.items['4']||0),button("Back",()=>showView(origin==='guild-lab'?'home':origin),'gl-back'));outer.prepend(top);
 const title=el('header','gl-title');title.append(el('h2','','Lab'),button('×',()=>showView(origin),'gl-close'));r.append(title);const tabs=el('nav','gl-tabs');for(let j=1;j<=5;j++){const b=button(jobs[j],()=>change(j,page),j===job?'active':'');b.append(img('pub_job_icon'+j,'gl-job-icon'));tabs.append(b);}r.append(tabs);
 const nodes=info.nodes.filter(n=>n.job===job&&((n.reset>=10)===Boolean(page)));if(!nodes.some(n=>n.id===selected))selected=nodes[0]?.id;const chosen=nodes.find(n=>n.id===selected);
 const tree=el('div','gl-tree');tree.append(el('div','gl-ring'),img('guild_bg_flower','gl-sigil'),img('guild_skill_job'+job+(page?'_new':''),'gl-center'));const arrow=button('',()=>change(job,page?0:1),'gl-page-arrow '+(page?'previous':'next'));arrow.setAttribute('aria-label',page?"Back to Basic":'Ir a Avanzado');arrow.title=page?"Basic":'Avanzado';arrow.append(img('partner_detail_arrow'));tree.append(arrow);const dots=el('nav','gl-page-dots');dots.setAttribute('aria-label',"Laboratory page");for(let p=0;p<=1;p++){const dot=button('',()=>change(job,p));dot.setAttribute('aria-label',p?'Avanzado':"Basic");dot.setAttribute('aria-current',p===page?'page':'false');dot.append(img(p===page?'page_icon_1':'page_icon_0'));dots.append(dot);}tree.append(dots);nodes.forEach((n,i)=>{const positions=[[-75,167],[-177,64],[-177,-75],[-75,-167],[75,-167],[177,-75],[177,64],[75,167]];const [x,y]=positions[i];const b=button('',()=>{selected=n.id;confirmReset=false;render();},'gl-node'+(n.id===selected?' selected':'')+(!n.unlocked?' locked':''));b.style.left=(50+x/6.4)+'%';b.style.top=(50-y/4.6)+'%';b.setAttribute('aria-label',n.name+" level "+n.level+" of "+n.max+(n.unlocked?'':" locked"));b.append(img(n.icon),el('b','',n.level+'/'+n.max));tree.append(b);});r.append(tree);
 if(chosen){const detail=el('article','gl-detail');const portrait=el('div','gl-selected');portrait.append(img(chosen.icon),el('b','',chosen.name));detail.append(portrait);detail.append(el('h3','',chosen.name+' · '+chosen.level+'/'+chosen.max));const boosts=el('div','gl-boosts');Object.entries(chosen.effects).forEach(([key,value],i)=>{const next=chosen.next_effects[key];const line=el('p','gl-effect');line.append(el('b','gl-effect-label',(Object.keys(chosen.effects).length>1?(/Hp/.test(key)?'HP':/Atk/.test(key)?'ATK':'Skill DMG'):chosen.name)+' Adds'),el('span','',format(key,value)),el('strong','gl-next',chosen.level<chosen.max?' ▸ '+format(key,next):''));boosts.append(line);});detail.append(boosts);
 if(!chosen.unlocked)detail.append(el('p','gl-note',"Requires: "+chosen.requirements.map(([sid,lv])=>{const n=info.nodes.find(v=>v.id===sid);return n.name+' '+n.level+'/'+lv;}).join(' · ')));
 const costs=el('div','gl-costs');cost(costs,chosen.cost);const actions=el('div','gl-actions');for(const count of [1,10]){const b=button(count===1?'Lv. Up':'×10',()=>send('GUILD_UPGRADE_SKILL',{skill_id:chosen.id,num:count}));let total={};const table=catalog.skills[String(chosen.id)];for(const [field,grow] of [['base_gold','grow_gold'],['base_guild_coin','grow_guild_coin']]){const [key,base]=table[field].split('#');total[key]=count*Number(base)+Number(table[grow])*(count*chosen.level+count*(count-1)/2);}b.disabled=pending||!chosen.unlocked||chosen.level+count>chosen.max||!affordable(total);actions.append(b);}r.append(detail,costs,actions);}
 const group=page?job+9:job,reset=info.resets[String(group)];const resetBox=el('div','gl-reset');if(confirmReset){resetBox.append(el('p','',"This branch will be reset and its resources returned."),el('strong','',"Refund"));cost(resetBox,reset.refund);resetBox.append(el('strong','',"Cost"));cost(resetBox,reset.cost);const accept=button("Confirm reset",()=>send('GUILD_RESET_SKILL',{job:group}));accept.disabled=pending||!affordable(reset.cost);resetBox.append(accept,button("Cancel",()=>{confirmReset=false;render();}));}else{const b=button(Object.keys(reset.cost).length?"Reset · 2,000 Gems":"First reset free",()=>{confirmReset=true;render();});b.disabled=pending||!Object.keys(reset.refund).length;b.classList.add('gl-reset-icon');b.title=b.textContent;b.setAttribute('aria-label',b.textContent);b.replaceChildren(img('guild_btn_reset'));tree.append(b);}r.append(resetBox);const help=button('?',()=>{note="Complete the required levels to unlock each upgrade. The first reset of each branch is free.";render();},'gl-help');help.setAttribute('aria-label',"Laboratory help");help.replaceChildren(img('help_2'));tree.append(help);const nav=el('nav','girls-bottom-nav gl-nav');for(const [index,label,dest]of [[1,"FrontPage",'home'],[2,"Girls",'girls'],[3,"Bag",'bag'],[4,"Capsule",'capsule'],[5,"Guild",'guild'],[6,"Menu",'settings']]){const b=button('',()=>['guild','settings'].includes(dest)?openMenu(dest,'home'):showView(dest));const icon=el('img');icon.src='/assets/nav-reference/bottom-'+index+'.png';b.append(icon,el('small','',label));nav.append(b);}outer.append(nav);if(note)r.append(el('p','gl-note',note));r.append(el('p','gl-footer',"Upgrades for "+jobs[job]+". Progress saved in your save."));
 }
 return {open,render};
})();

// GuildTerritoryWindow: original prefab coordinates, 720 px design → 480 px frame.
const GuildTerritory=(()=>{
 let merchant=null,token=0;
 const A=n=>'/assets/menus/'+n+'.png',N=(tag,cls,text)=>node(tag,cls,text);
 const buildings=[
  ['guild-hall','Office',3,0,255,298,252,0,144],
  ['guild-dining','Cafeteria',5,248,115,230,226,229,18],
  ['guild-gym','Gym',6,224,-265,311,299,210,-390],
  ['guild-war','Playground',1,-235,-282,359,389,-208,-412],
  ['guild-lab','Lab',4,-253,113,265,221,-241.5,36]
 ];
 function at(e,x,y,w,h){e.style.left='calc(50% + '+((x-w/2)*2/3)+'px)';e.style.top='calc(53% - '+((y+h/2)*2/3)+'px)';e.style.width=w*2/3+'px';e.style.height=h*2/3+'px';return e;}
 function picture(src,cls){const i=N('img',cls);i.src=src;i.alt='';i.draggable=false;return i;}
 function clear(){token++;try{merchant?.destroy();}catch{}merchant=null;}
 function paint(host,interactive=true){
  for(const [key,label,id,x,y,w,h,lx,ly]of buildings){const b=N(interactive?'button':'div','gt-building');if(interactive){b.type='button';b.setAttribute('aria-label',label);b.addEventListener('click',()=>menuForward(key));}b.append(picture('/assets/original-ui/guild-territory/guild_territory_icon0'+id+'_mask.png'));host.append(at(b,x,y,w,h));const title=N('span','gt-label',label);host.append(at(title,lx,ly,170,28));}
  host.append(at(picture(A('guild_territory_icon02'),'gt-fountain'),0,0,120,90));
 }
 function render(host){clear();if(!host)return;paint(host);const current=token;
  const shop=N('button','gt-merchant');shop.type='button';shop.setAttribute('aria-label',"Merchant · Guild Store");shop.addEventListener('click',()=>openMenu('guild-shop','menu-explorer'));
  shop.style.left='calc(50% - 137px)';shop.style.top='calc(53% - 77px)';shop.append(N('span','gt-merchant-name','Merchant'));const canvas=N('div','gt-merchant-model');shop.append(canvas);host.append(shop);
  if(typeof GxbSpine!=='undefined')GxbSpine.mount(canvas,'/assets/chibis/yuanshu',{width:120,height:170,scale:.28,origin:[.5,.94],sequence:[['idle',true]]}).then(g=>{if(current!==token||!host.isConnected){g.destroy();return;}merchant=g;}).catch(()=>{shop.title="Guild Store";});
 }
 return {render,paint,clear};
})();
