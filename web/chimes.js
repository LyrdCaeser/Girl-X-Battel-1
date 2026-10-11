'use strict';
// Tree of Chimes (Tsuruga Grand Shrine → Tree of Chimes). ChimeMainWindow: the purple tree (chime_bg_ysm) with the Chimes
// hanging from cords three per row (itemLocalPosotionInLayer, rows alternate), each with its name in the quality colour,
// its Chimelight % (chime_bg_ysm_d) or the lock; side menu Gallery / Shards. ChimeDetailWindow tabs Status / Charge /
// Enchant / Ascend; ChimeDebrisBackpackWindow transfers spare shards into Chime Chips. Rules: gxb2/chimes.py. Prefix ch-.
const Chimes=(()=>{
 let data=null,origin='shrine',busy=false,tab=1;
 const A=n=>'/assets/chimes/'+n+(n==='chime_bg_ysm'?'.webp':'.png');
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 const T=k=>data?.text?.[k]||'';
 // ChimeMainWindow NameColor by quality (Color.New2 0xRRGGBBAA)
 const QCOL=['#ffffff','#e7d32c','#f446fa','#28df64','#f61067','#fd8214'];
 const NAMES={hp:'HP',atk:'Attack',arm:'Defense',spd:'Speed',hpP:'HP',atkP:'Attack',brk:'Armor Break',block:'Block',sklP:'Skill Damage',trueAtk:'Holy Damage',allHarmInc:'All Damage Dealt',decDmg:'Damage Depletion'};
 const POS=[[[-227,28],[-12,0],[206,-9]],[[-225,-8],[0,0],[203,22]]];
 const pairs=t=>String(t||'').split('|').filter(p=>p.includes('#')).map(p=>p.split('#'));
 function iconSrc(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';if(['325','326','373'].includes(id))return A('icon_'+id);const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}return it&&itemIcons.has(it.icon)?'/assets/item-icons/'+it.icon+'.png':'';}
 function costRow(text){const w=el('div','ch-cost');for(const [k,n]of pairs(text)){const have=Number(state.items?.[k]||0),need=Number(n);const c=el('span',have>=need?'':'short');const s=iconSrc(k);if(s)c.append(img(s));c.append(el('b','',(k==='1'?number(need):number(have)+'/'+number(need))));c.title=data.items[k]||itemCatalog?.[k]?.name||k;w.append(c);}return w;}
 async function act(req,msg){if(busy)return null;busy=true;try{const r=await api('/api/chimes/action',req);state=r.state;if(msg)GirlUI.toast(msg);return r;}catch(e){GirlUI.toast(e.message);return null;}finally{busy=false;if(view==='chimes'){draw();if(reopen)reopen();}}}
 let reopen=null;
 function root(){let r=$('chimes-view');if(!r){r=el('section','chimes-view');r.id='chimes-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function open(from){origin=from||view;if(!data)data=await api('/assets/chimes.json');root();showView('chimes');draw();}
 const info=()=>state.chimes_info?.chimes||{};
 function draw(){const r=root();if(view!=='chimes'||!data)return;r.replaceChildren();const st=el('div','ch-stage');st.style.backgroundImage=`url('${A('chime_bg_ysm')}')`;r.append(st);
  const top=el('div','ch-top');for(const id of ['325','326']){const c=el('span','ch-res');c.append(img(A('icon_'+id)),el('b','',number(state.items?.[id]||0)));top.append(c);}
  const back=btn('ch-back','',()=>showView(origin));back.append(img('/assets/ui/win_back_btn.png'));top.append(back);st.append(top);
  st.append(btn('ch-help','',()=>CampaignUI.popup(T('CHIME_HELP').split('|').join('\n').replace(/%%/g,'%'),{})));
  const side=el('div','ch-side');const g=btn('ch-sidebtn','',()=>gallery());g.append(img(A('icon_tj')),el('small','',T('CHIME_ATLAS')||'Gallery'));const b=btn('ch-sidebtn','',()=>shards());b.append(img(A('icon_sp')),el('small','',T('CHIME_BAG')||'Shards'));side.append(g,b);st.append(side);
  const list=Object.entries(data.chimes).sort((a,b)=>a[1].sort-b[1].sort);const tree=el('div','ch-tree');
  for(let row=0;row*3<list.length;row++){const layer=el('div','ch-layer'+(row%2?' flip':''));layer.append(img(A('chime_bg_ysm_x'),'ch-cord'));
   list.slice(row*3,row*3+3).forEach(([id,c],i)=>{const [x,y]=POS[(row+1)%2][i];const s=info()[id]||{lev:-1};const lock=s.lev<0;const canUnlock=lock&&s.shards>=Number(pairs(c.unlock)[0]?.[1]||0);
    const it=btn('ch-chime'+(lock?' locked':''),'',()=>detail(id));it.style.left=`calc(${360+x-100} * var(--u))`;it.style.top=`calc(${150-y} * var(--u))`;it.style.animationDelay=(-(i+row)*0.7)+'s';
    it.append(img(A(c.icon),'ch-bell'));if(lock)it.append(img(A('lock'),'ch-lock'));else{const p=el('span','ch-light');p.style.backgroundImage=`url('${A('chime_bg_ysm_d')}')`;p.textContent=s.lev>=Number(c.max_lv)?'MAX':s.lev+'%';it.append(p);}
    if(canUnlock)it.append(img(A('alert_icon'),'ch-red'));const nm=el('b','ch-name',data.names[id]?.name||id);nm.style.color=QCOL[Math.min(5,Number(c.qlt)-1)];it.append(nm);layer.append(it);});tree.append(layer);}
  st.append(tree);}
 function baseLines(c,lev){return pairs(c.attrs).map(([k,a,b])=>{a=Number(a);b=Number(b);const L=Math.max(0,lev);const v=Math.floor(a*(L+1)+b*L*(L+1)/2+a*Math.floor(L/10));return [NAMES[k]||k,v];});}
 function detail(id){reopen=()=>detail(id);const c=data.chimes[id],s=info()[id]||{lev:-1,buffs:[0,0,0,0]},nm=data.names[id]||{};const {body,close}=GirlUI.win({title:nm.name||'Chime',cls:'ch-win'});const re=()=>{close();detail(id);};
  const head=el('div','ch-head');head.append(img(A(c.icon),'ch-headbell'));const hi=el('div','');const n2=el('b','ch-hname',nm.name||id);n2.style.color=QCOL[Math.min(5,Number(c.qlt)-1)];hi.append(n2,el('span','ch-hlight',(T('CHIME_TEXT01')||'Chimelight')+' '+Math.max(0,s.lev)+'%'));head.append(hi);body.append(head);
  if(s.lev<0){const need=pairs(c.unlock)[0];const box=el('div','ch-box');box.append(el('p','',(T('CHIME_TEXT16')||'Owned Chime Shards')+': '+number(s.shards||0)+' / '+need[1]),costRow(c.unlock),btn('gs-btn ch-go',T('CHIME_TEXT14')||'Unlock',async()=>{const r=await act({action:'unlock',id},nm.name+' ✓');if(r)re();},(s.shards||0)<Number(need[1])));body.append(box);return;}
  const nav=el('div','ch-nav');[[1,'CHIME_TAB1','Status'],[2,'CHIME_TAB2','Charge'],[3,'CHIME_TAB3','Enchant'],[4,'CHIME_TAB4','Ascend']].forEach(([i,k,d])=>nav.append(btn('ch-tab'+(tab===i?' on':''),T(k)||d,()=>{tab=i;re();})));body.append(nav);
  const box=el('div','ch-box');body.append(box);const lim4=String(c.limit4||'').split('|').map(Number);const ench=[1,2,3].filter(i=>String(c['limit'+(i===2?1:i)]||'')!==''&&(i!==2||c.buff2));
  if(tab===1){box.append(el('h5','ch-sec',T('CHIME_TEXT02')||'Base Attributes'));for(const [k,v]of baseLines(c,s.lev))box.append(line(k,'+'+number(v)));
   box.append(el('h5','ch-sec',T('CHIME_TEXT03')||'Enchantment(s)'));for(const i of ench)box.append(line((s.buffs[i-1]?'✓ ':'🔒 ')+(nm.buffs?.[i-1]||''),s.buffs[i-1]?'':(c['limit'+i]||c.limit1)+'%',s.buffs[i-1]?'on':'off'));
   box.append(el('h5','ch-sec',T('CHIME_TEXT04')||'Ascension Skill(s)'));box.append(line((s.buffs[3]?'✓ ':'🔒 ')+(nm.buffs?.[3]||''),s.buffs[3]?'':lim4[0]+'%',s.buffs[3]?'on':'off'));}
  else if(tab===2){if(s.lev>=Number(c.max_lv)){box.append(el('p','ch-max',T('CHIME_TEXT08')||'Max. Chimelight reached'));}
   else{const now=baseLines(c,s.lev),next=baseLines(c,s.lev+1);box.append(line(T('CHIME_TEXT01')||'Chimelight',s.lev+'% ➜ '+(s.lev+1)+'%'));now.forEach(([k,v],j)=>box.append(line(k,'+'+number(v)+' ➜ +'+number(next[j][1]))));
    box.append(costRow(Object.entries(s.charge_cost||{}).map(([k,v])=>k+'#'+v).join('|')));const r2=el('div','ch-row');r2.append(btn('gs-btn ch-go',T('CHIME_BUTTON1')||'Charge',()=>act({action:'charge',id},'+1%')),btn('gs-btn white','×10',()=>act({action:'charge',id,times:10}).then(r=>r&&GirlUI.toast('+'+r.charged+'%'))));box.append(r2);}}
  else if(tab===3){const todo=ench.filter(i=>!s.buffs[i-1]);if(!todo.length){box.append(el('p','ch-max',T('CHIME_TEXT09')||'Enchanted'));}
   else{const i=todo[0],lim=Number(c['limit'+i]||c.limit1);box.append(line(nm.buffs?.[i-1]||'',''),line(T('CHIME_TEXT01')||'Chimelight',s.lev+'% / '+lim+'%',s.lev>=lim?'on':'off'),costRow(c['cost'+i]));box.append(btn('gs-btn ch-go',T('CHIME_BUTTON2')||'Enchant',()=>{if(confirm(T('CHIME_TEXT12')||'Enchant?'))act({action:'enchant',id},'✓');},s.lev<lim));}}
  else{if(s.buffs[3]){box.append(el('p','ch-max',T('CHIME_TEXT10')||'Ascended'));}
   else{const needE=lim4.slice(1).reduce((a,b)=>a+b,0),doneE=s.buffs.slice(0,3).reduce((a,b)=>a+b,0);box.append(line(nm.buffs?.[3]||'',''),line(T('CHIME_TEXT01')||'Chimelight',s.lev+'% / '+lim4[0]+'%',s.lev>=lim4[0]?'on':'off'),line(T('CHIME_TEXT03')||'Enchantment(s)',doneE+' / '+needE,doneE>=needE?'on':'off'),costRow(c.cost4));
    box.append(btn('gs-btn ch-go',T('CHIME_BUTTON3')||'Ascend',()=>{if(confirm(T('CHIME_TEXT13')||'Ascend?'))act({action:'ascend',id},'✓');},s.lev<lim4[0]||doneE<needE));}}}
 function line(label,value,cls=''){const r=el('div','ch-line '+cls);r.append(el('span','',label),el('b','',value));return r;}
 function shards(){reopen=()=>shards();const {body}=GirlUI.win({title:T('CHIME_BAG')||'Shards',cls:'ch-win'});body.append(el('p','ch-note',T('CHIME_TEXT18')));const grid=el('div','ch-grid');
  for(const [id,c]of Object.entries(data.chimes).sort((a,b)=>a[1].sort-b[1].sort)){const s=info()[id]||{};const card=el('div','ch-shard');const src=iconSrc(s.shard);card.append(src?img(src):img(A(c.icon)),el('b','',data.items[s.shard]||s.shard),el('small','',number(s.shards||0)+' · '+(T('CHIME_TEXT17')||'Transfer')+': '+number(s.spare||0)));
   card.append(btn('gs-btn white',T('CHIME_TEXT17')||'Transfer',async()=>{const n=Number(prompt((data.items[s.shard]||'')+" → Chime Chip (max. "+s.spare+')',String(s.spare)))||0;if(n>0){const r=await act({action:'transfer',shard:s.shard,count:n});if(r)GirlUI.toast('+'+number(r.got['373'])+' Chime Chip');}},!s.spare));grid.append(card);}body.append(grid);}
 function gallery(){reopen=null;const {body}=GirlUI.win({title:T('CHIME_ATLAS')||'Gallery',cls:'ch-win'});for(const [id,c]of Object.entries(data.chimes).sort((a,b)=>a[1].sort-b[1].sort)){const nm=data.names[id]||{};const r=el('div','ch-gal');r.append(img(A(c.icon)));const t=el('div','');const n2=el('b','',nm.name);n2.style.color=QCOL[Math.min(5,Number(c.qlt)-1)];t.append(n2);for(const [k,v]of baseLines(c,Number(c.max_lv)))t.append(el('small','','Max '+k+' +'+number(v)));(nm.buffs||[]).filter(Boolean).forEach(x=>t.append(el('small','','• '+x)));r.append(t);body.append(r);}}
 return {open,render:draw};
})();
