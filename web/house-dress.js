'use strict';
// HouseWindow + DressMainWindow: original tables, sprites and three synchronized Spine parts.
const HouseDress=(()=>{
 let data=null,origin='campus',mode='dorm',editing=false,hidden=false,restDraft=null,floor=1,draft=[],selected=0,filter=0,series=0,tab='room',outfit={},draftName='',note='',busy=false,handles=[],generation=0;
 const A=n=>'/assets/original-ui/house-dress/'+n+'.png',N=(t,c,text)=>node(t,c,text),I=(n,c)=>{const e=N('img',c);e.src=A(n);e.alt='';e.draggable=false;return e;};
 const B=(label,fn,c='hd-button')=>{const e=N('button',c,label);e.type='button';e.onclick=fn;return e;};
 const H=()=>state.house_dress_info,clone=v=>JSON.parse(JSON.stringify(v));
 function clear(){generation++;for(const h of handles)h.destroy();handles=[];}
 async function open(key,from){if(key!=='dorm'&&typeof Dress!=='undefined'){Dress.open(from||view,key==='outfit'?'locker':'shop');return;}origin=from||view;mode=key;floor=1;tab='room';editing=false;filter=0;series=0;selected=0;note='';try{data||=await api('/assets/original-ui/house-dress/catalog.json');const r=await api('/api/house-dress/action',{action:'open'});state=r.state;draft=clone(H().rooms['1']);outfit=clone(H().outfit);draftName=H().name;showView('house-dress');}catch(e){error(e.message);}}
 async function send(req,msg="Saved"){if(busy)return;busy=true;note='';try{const r=await api('/api/house-dress/action',req);state=r.state;note=msg;return true;}catch(e){note=e.message;return false;}finally{busy=false;render();}}
 function top(root){const h=N('header','hd-top');for(const id of ['1','2']){const res=N('span','hd-money');res.append(I('icon_'+id),N('b','',number(state.items[id]||0)));h.append(res);}const back=B('',()=>{clear();showView(origin);},'hd-back');back.append(I('win_back_btn'));back.setAttribute('aria-label',"Back");h.append(back);root.append(h);}
 function bottom(root){const nav=N('nav','hd-nav');const tabs=[['Cafe','dorm'],['Locker Room','outfit'],['Outfit Store','outfit-store']];for(const [i,[label,key]]of tabs.entries()){const k=i===0?'left':i===tabs.length-1?'right':'mid';const b=B(label,()=>{if(key!=='dorm'&&typeof Dress!=='undefined'){clear();Dress.open('house-dress',key==='outfit'?'locker':'shop');return;}mode=key;editing=false;hidden=false;selected=0;filter=0;tab='room';note='';outfit=clone(H().outfit);draft=clone(H().rooms[String(floor)]);draftName=H().name;render();},mode===key?'active':'');b.style.borderImageSource=`url('${A('nav_btn_'+(mode===key?'blue':'white')+'_'+k)}')`;nav.append(b);}root.append(nav);}
 function render(){if(view!=='house-dress'){clear();return;}const root=$('house-dress-view');if(!data||!H())return;clear();root.replaceChildren();root.className='hd-view';top(root);if(mode==='dorm'){if(tab==='store')shop(root);else if(tab==='girls')girls(root);else room(root);}else if(mode==='outfit')wardrobe(root);else dressStore(root);if(note)root.append(N('p','hd-message',note));bottom(root);root.scrollTop=0;}
 function row(e){return data.house_furniture[String(e.id)];}
 function dims(e){let [w,h]=String(row(e).area).split('|').map(Number);return e.flip?[h,w]:[w,h];}
 // Floor cells (24×24 grid) where nothing stands: the resting girls use them, from the room centre outwards.
 function occupied(entries){const busy=new Set();for(const p of entries){if(p.plane!=='floor'||p.parent||[1,3,10].includes(row(p).type))continue;const [w,h]=dims(p);for(let x=p.x;x<p.x+w;x++)for(let y=p.y;y<p.y+h;y++)busy.add(x+','+y);}return busy;}
 function freeSpots(entries,n){const busy=occupied(entries),out=[];const cells=[];for(let x=2;x<22;x++)for(let y=2;y<22;y++)cells.push([x,y]);cells.sort((a,b)=>Math.hypot(a[0]-13,a[1]-13)-Math.hypot(b[0]-13,b[1]-13));
  for(const gap of [8,6,4]){for(const [x,y]of cells){if(out.length>=n)break;let free=true;for(let dx=-2;dx<=2&&free;dx++)for(let dy=-2;dy<=2;dy++)if(busy.has((x+dx)+','+(y+dy))){free=false;break;}if(free&&out.every(([a,b])=>Math.hypot(a-x,b-y)>=gap))out.push([x,y]);}if(out.length>=n)break;}return out;} // 2-cell margin around furniture, spread out
 function fits(entries,e){if(e.plane!=='floor'||[1,3].includes(row(e).type))return true;const [w,h]=dims(e);if(e.x<0||e.y<0||e.x+w>24||e.y+h>24)return false;return entries.every(p=>{if(p===e||p.plane!=='floor'||p.parent||[1,3,10].includes(row(p).type))return true;const [pw,ph]=dims(p);return e.x+w<=p.x||e.x>=p.x+pw||e.y+h<=p.y||e.y>=p.y+ph;});}
 // HouseSelectBox (house_select_box prefab, 336×329 at 720 → ×0.45 here): Flip top, OK right, Cancel left, Store bottom-left,
 // Details bottom-right; the footprint tiles green / red (house_floor_unit_*) and — local addition — iso arrows to nudge.
 let selOrig=null;
 function selectBox(world,entries,e,step,base){const [w,h]=dims(e);let cx,cy;if(e.plane==='floor'){cx=240+((e.x+w/2)-(e.y+h/2))*step;cy=base+((e.x+w/2)+(e.y+h/2))*step/2-12;}else{cx=240+(e.x>=24?1:-1)*(e.x%24)*step;cy=base+(e.x%24)*step/2-80-e.y*70;}
  if(e.plane==='floor'&&![1,3].includes(row(e).type)){const ok=fits(entries,e);for(let x=e.x;x<e.x+w;x++)for(let y=e.y;y<e.y+h;y++){const t=I(ok?'house_floor_unit_green':'house_floor_unit_red','hd-foot');t.style.cssText=`left:${240+(x-y)*step-step}px;top:${base+(x+y)*step/2}px;width:${2*step}px;height:${step}px`;world.append(t);}}
  const box=N('div','hd-selbox');box.style.cssText=`left:${cx}px;top:${cy}px`;box.append(I('house_select_box_bg','hd-selring'));
  const K=.45,btn=(icon,label,x,y,fn)=>{const b=B('',ev=>{ev.stopPropagation();fn();},'hd-selbtn');b.style.cssText=`left:${x*K}px;top:${-y*K}px`;b.append(I('house_select_btnbg','hd-selbtn-bg'),I(icon,'hd-selbtn-ic'),N('span','',label));b.setAttribute('aria-label',label);box.append(b);};
  btn('house_select_btn1','Flip',0,154,()=>{e.flip=e.flip?0:1;render();});
  btn('house_select_btn2','OK',142,50,()=>{if(!fits(entries,e)){note="Cannot place here";render();return;}selected=0;selOrig=null;render();});
  btn('house_select_btn5','Cancel',-142,50,()=>{if(selOrig)Object.assign(e,selOrig);else draft=draft.filter(d=>d.uid!==e.uid&&d.parent!==e.uid);selected=0;selOrig=null;render();}); // a piece just taken from the box goes back
  btn('house_select_btn4','Store',-88,-116,()=>{draft=draft.filter(d=>d.uid!==e.uid&&d.parent!==e.uid);selected=0;selOrig=null;render();});
  btn('house_select_btn3','Details',88,-116,()=>{note=row(e).label+' · Comfort '+row(e).comfort+' · '+dims(e).join('×');render();});
  const pad=N('div','hd-selpad');const mv=(dx,dy,label,cls)=>{const b=B(label,ev=>{ev.stopPropagation();if(e.plane==='floor'){e.x=Math.max(0,Math.min(24-w,e.x+dx));e.y=Math.max(0,Math.min(24-h,e.y+dy));}else e.x=Math.max(0,Math.min(47,e.x+(dx||-dy)));render();},'hd-arrow '+cls);b.setAttribute('aria-label','Mover '+label);pad.append(b);};
  mv(-1,0,'↖','nw');mv(0,-1,'↗','ne');mv(0,1,'↙','sw');mv(1,0,'↘','se');box.append(pad);world.append(box);}
 function scene(root,entries,interactive){const stage=N('div','hd-room-scene');root.append(stage);const background=entries.find(e=>row(e).type===10);if(background){const names=String(row(background).img).split('|');const bg=N('div','hd-scene-background');for(const [i,n]of names.entries()){if(!data.sizes[n])continue;const tile=I(n);tile.style.cssText=`left:${i%2*366.4}px;top:${Math.floor(i/2)*356.8}px`;bg.append(tile);}stage.append(bg);}const world=N('div','hd-world');stage.append(world);const step=10,scale=.2,base=205;
  const floorRow=entries.find(e=>row(e).type===1),wallRow=entries.find(e=>row(e).type===2);let fn=floorRow?row(floorRow).img:'img_1010002',wn=wallRow?row(wallRow).img:'img_1010001';
  // Original 24×24 grid, mapSize50. Each floor sprite spans 6×6 cells and wall strip spans6.
  for(let x=0;x<4;x++)for(let y=0;y<4;y++){const tile=I(fn,'hd-tile');tile.style.cssText=`left:${240+(x-y)*60-60}px;top:${base+(x+y)*30}px;width:120px;height:65px`;world.append(tile);}
  for(let side=0;side<2;side++)for(let k=0;k<4;k++){const n=wn+'_'+(k===0?1:2);const wall=I(n,'hd-wall');wall.style.cssText=`left:${side?240+k*60:240-(k+1)*60}px;top:${base+(k+1)*30-114}px;width:60px;height:114px;transform:${side?'scaleX(-1)':'none'}`;world.append(wall);}
  for(const e of entries){const r=row(e);if([1,2,10].includes(r.type))continue;let x=e.x,y=e.y,z=0;const parent=e.parent&&entries.find(p=>p.uid===e.parent);if(parent){x+=parent.x;y+=parent.y;z=25;}if(e.plane==='floor'){const [fw,fh]=dims(e);x+=fw;y+=fh;} // HouseMap:getMapPosByInfo: floor pieces stand on the far corner of their footprint (pivot Bottom)
   let px=240+(x-y)*step,py=base+(x+y)*step/2-z;if(e.plane==='wall'){px=240+(x>=24?1:-1)*(x%24)*step;py=base+(x%24)*step/2-50-e.y*70;}
   let name=String(e.flip&&r.flip_img?r.flip_img:r.img).split('|')[0];const sz=data.sizes[name]||[120,120];const object=B('',()=>{if(interactive){if(selected!==e.uid)selOrig={x:e.x,y:e.y,flip:e.flip};selected=e.uid;render();}},'hd-furniture'+(e.uid===selected?' selected':''));object.setAttribute('aria-label',r.label);object.style.cssText=`left:${px-sz[0]*scale/2}px;top:${py-sz[1]*scale}px;width:${sz[0]*scale}px;height:${sz[1]*scale}px;z-index:${30+Math.round((x+y)*3)+(e.parent?1:0)}`;const art=I(name);if(e.flip&&!r.flip_img)art.style.transform='scaleX(-1)';object.append(art);world.append(object);
   if(interactive&&!e.parent){let drag=null;object.onpointerdown=ev=>{if(ev.button!==0)return;if(selected!==e.uid)selOrig={x:e.x,y:e.y,flip:e.flip};selected=e.uid;const rect=world.getBoundingClientRect();drag={cx:ev.clientX,cy:ev.clientY,x:e.x,y:e.y,s:rect.width/480};object.setPointerCapture(ev.pointerId);};object.onpointermove=ev=>{if(!drag)return;const dx=(ev.clientX-drag.cx)/drag.s,dy=(ev.clientY-drag.cy)/drag.s;const [w,h]=dims(e);if(e.plane==='floor'){e.x=Math.max(0,Math.min(24-w,Math.round(drag.x+dx/(2*step)+dy/step)));e.y=Math.max(0,Math.min(24-h,Math.round(drag.y-dx/(2*step)+dy/step)));}else e.x=Math.max(0,Math.min(47,Math.round(drag.x-dx/step)));{const [fw,fh]=e.plane==='floor'?dims(e):[0,0];object.style.left=240+(e.x+fw-e.y-fh)*step-sz[0]*scale/2+'px';object.style.top=base+(e.x+fw+e.y+fh)*step/2-sz[1]*scale+'px';}};object.onpointerup=()=>{if(drag){drag=null;render();}};object.onpointercancel=()=>{drag=null;};}
  }
  // Girls at home (HouseHero.lua): they wander between free cells (walk), rest (houseidle), use free furniture with an
  // interaction (house_furniture.interact 1 sit / 2 lie at point_xy) and react to a touch (hurt / hit).
  if(!interactive){const spots=freeSpots(entries,H().girls.length);const life={world,entries,step,base,busy:occupied(entries),used:new Set(),at:new Map(),gen:generation};
   life.seats=entries.filter(e=>e.plane==='floor'&&!e.parent&&['1','2'].includes(String(row(e).interact))).map(e=>{const [fw,fh]=dims(e);const ax=e.x+fw,ay=e.y+fh;const [ptx,pty]=String(row(e).point_xy||'0|0').split('#')[0].split('|').map(Number);const f=e.flip?-1:1;
     const kind=String(row(e).interact)==='1'?'sit':'lie';const mx=e.x+fw/2,my=e.y+fh/2;
     return kind==='lie'?{uid:e.uid,kind,px:240+(mx-my)*step-16,py:base+(mx+my)*step/2+6,z:30+Math.round((ax+ay)*3)+2,flip:e.flip?1:0}:{uid:e.uid,kind,px:240+(ax-ay)*step+f*ptx*scale,py:base+(ax+ay)*step/2+pty*scale,z:30+Math.round((ax+ay)*3)+2,flip:e.flip?1:0};});
   for(const [i,pid]of H().girls.entries()){const g=state.roster.find(g=>g.partner_id===pid);if(!g||!spots[i])continue;const [cx,cy]=spots[i];const px=240+(cx-cy)*step,py=base+(cx+cy)*step/2;const host=N('div','hd-room-girl');host.style.cssText=`left:${px-45}px;top:${py-104}px;z-index:${30+Math.round((cx+cy)*3)}`;world.append(host);mountGirl(host,g.table_id,i,life,{px,py});}}
  if(interactive&&selected){const e=entries.find(x=>x.uid===selected);if(e&&!e.parent)selectBox(world,entries,e,step,base);}
  return stage;
 }
 async function mountGirl(host,id,i=0,life=null,pos=null){const gen=generation;try{const catalog=await ChibiBattle.catalogue();if(gen!==generation||!host.isConnected)return;const meta=catalog[String(id)];const model=meta?.model;if(!model)return;const names=meta.animations||[];const anim=names.includes('houseidle')?'houseidle':'idle';const h=await GxbSpine.mount(host,'/assets/chibis/'+model,{width:90,height:110,scale:.2,origin:[.5,.95],sequence:[[anim,true]],resolution:Math.max(3,Math.ceil((devicePixelRatio||1)*2))});if(i%2&&h?.figure)h.figure.scale.x*=-1;if(gen!==generation||!host.isConnected){h.destroy();return;}handles.push(h);if(life&&pos)live(host,h,names,life,pos,i);}catch{}}
 // One girl's routine. Timers stop when the room is redrawn (generation) or the node leaves the page.
 function live(host,h,names,life,pos,i){const fig=h.figure,sx=Math.abs(fig.scale.x);const has=n=>names.includes(n);const idle=has('houseidle')?'houseidle':'idle';const walkA=has('walk')?'walk':has('move')?'move':idle;let seat=null,cur=idle,alive=()=>life.gen===generation&&host.isConnected&&!h.dead;
  const play=(n,loop=true)=>{cur=n;try{fig.state.setAnimation(0,n,loop);}catch{}};const face=dir=>{fig.scale.x=dir<0?-sx:sx;};
  const place=(px,py,z,t)=>{host.style.transition=t?`left ${t}s linear, top ${t}s linear`:'none';host.style.left=(px-45)+'px';host.style.top=(py-104)+'px';if(z!=null)host.style.zIndex=String(z);pos.px=px;pos.py=py;};
  const leave=()=>{if(seat){life.used.delete(seat.uid);seat=null;}};
  const next=()=>{if(!alive())return;const r=Math.random();const free=life.seats.filter(q=>!life.used.has(q.uid));
   if(seat){leave();const [cx,cy]=cell();const px=240+(cx-cy)*life.step,py=life.base+(cx+cy)*life.step/2;place(px,py,30+Math.round((cx+cy)*3),0);play(idle);return setTimeout(next,1500+Math.random()*2000);}
   if(r<.2){play(idle);return setTimeout(next,3000+Math.random()*4000);}
   if(r<.45&&free.length){const q=free[Math.floor(Math.random()*free.length)];life.used.add(q.uid);seat=q;return go(q.px,q.py,q.z,()=>{face(q.flip?-1:1);play(has(q.kind)?q.kind:idle);setTimeout(next,12000+Math.random()*10000);});}
   const [cx,cy]=cell();go(240+(cx-cy)*life.step,life.base+(cx+cy)*life.step/2,30+Math.round((cx+cy)*3),()=>{play(idle);setTimeout(next,2500+Math.random()*4000);});};
  const cell=()=>{for(let k=0;k<40;k++){const x=2+Math.floor(Math.random()*20),y=2+Math.floor(Math.random()*20);let ok=true;for(let dx=-1;dx<=1&&ok;dx++)for(let dy=-1;dy<=1;dy++)if(life.busy.has((x+dx)+','+(y+dy))){ok=false;break;}if(ok&&[...life.at.entries()].every(([k,c])=>k===i||Math.hypot(c[0]-x,c[1]-y)>=4)){life.at.set(i,[x,y]);return [x,y];}}return [12,12];};
  const go=(px,py,z,done)=>{const d=Math.hypot(px-pos.px,py-pos.py),t=Math.max(.4,d/32);face(px<pos.px?-1:1);play(walkA);host.style.zIndex=String(Math.max(Number(host.style.zIndex)||0,z));place(px,py,null,t);setTimeout(()=>{if(!alive())return;host.style.zIndex=String(z);done();},t*1000+60);};
  host.onclick=()=>{if(!alive())return;const t=has('hurt')?'hurt':has('hit')?'hit':null;if(!t)return;const back=cur;try{fig.state.setAnimation(0,t,false);fig.state.addAnimation(0,back,true,0);}catch{}};
  setTimeout(next,1500+i*900+Math.random()*2000);}
 // HouseWindow chrome (house_window prefab, 720 → 480 px): name plate + comfort chip top-left, help / hide top-right,
 // round Manage / Store / Floor / Date buttons bottom-left and the big Rest button bottom-right; in edit mode Clear + Cancel / Save.
 function round(cls,icon,label,fn,badge){const b=B('',fn,'hd-round '+cls);b.append(I('house_icon_2','hd-round-bg'),I(icon,'hd-round-icon'),N('span','hd-round-label',label));if(badge)b.append(I('alert_icon','hd-badge'));b.setAttribute('aria-label',label);b.addEventListener('click',()=>{note='';},true);return b;}
 function room(root){root.classList.toggle('hd-editing',editing);root.classList.toggle('hd-hide',hidden&&!editing);const r=editing?draft:H().rooms[String(floor)];
  const info=N('div','hd-room-info');const plate=N('div','hd-plate');plate.append(I('house_name_bg','hd-plate-bg'));const name=N('input','hd-name');name.value=draftName||H().name;name.disabled=!editing;name.oninput=()=>{draftName=name.value;};name.maxLength=32;name.setAttribute('aria-label',"Cafe name");plate.append(name);
  const comfort=N('div','hd-chip');comfort.append(I('common_btn_icon_1','hd-chip-bg'),I('house_icon_3','hd-chip-icon'),N('b','',number(H().comfort)));comfort.title='Comfort';comfort.classList.add('hd-chip-btn');comfort.onclick=comfortWin;info.append(plate,comfort);root.append(info);
  const side=N('div','hd-side');const help=B('',()=>CampaignUI.popup("Decorate your Cafe with furniture from the store: each item adds Comfort.\nManage: place, rotate, and remove furniture (drag items on the grid).\nRest: up to 5 Girls can rest in the Cafe.\nFloor: unlock and switch to the second floor.",{}),'hd-side-btn');help.append(I('help_3'));help.setAttribute('aria-label',"Help");side.append(help);
  if(!editing){const hide=B('',()=>{hidden=!hidden;render();},'hd-side-btn');hide.append(I('house_btn_1'));hide.setAttribute('aria-label',"Hide interface");side.append(hide);}root.append(side);
  const stage=scene(root,r,editing);if(hidden&&!editing)stage.onclick=()=>{hidden=false;render();};
  const tools=N('div','hd-room-tools');
  if(editing){const clr=B('',()=>{draft=draft.filter(e=>[1,2,10].includes(row(e).type));selected=0;render();},'hd-clear');clr.append(I('white_btn70_70','hd-round-bg'),I('house_btn_6','hd-round-icon'),N('span','hd-clear-label','Clear'));
   tools.append(clr,B('Cancel',()=>{editing=false;selected=0;draftName=H().name;draft=clone(H().rooms[String(floor)]);render();},'hd-blue hd-cancel'),B('Save',async()=>{if(await send({action:'save_room',revision:H().revision,floor,layout:draft,name:name.value})){editing=false;selected=0;draftName=H().name;draft=clone(H().rooms[String(floor)]);render();}},'hd-blue hd-save'));
   root.append(tools);storage(root);return;}
  const floorBtn=async()=>{if(H().rooms['2']){floor=floor===1?2:1;draft=clone(H().rooms[String(floor)]);render();}else if(await send({action:'open_floor'})){floor=2;draft=clone(H().rooms['2']);render();}};
  tools.append(round('hd-manage','house_btn_3','Manage',()=>{editing=true;draft=clone(H().rooms[String(floor)]);draftName=H().name;selected=0;filter=0;render();}),round('hd-shop','house_btn_4','Store',()=>{tab='store';series=6;render();}),round('hd-floor','house_btn_8_'+floor,'Floor '+floor,floorBtn),round('hd-date','house_btn_5','Date',()=>openMenu('date','house-dress')));
  const rest=B('',()=>{tab='girls';render();},'hd-rest');rest.append(I('house_btn_2_en_en'),N('span','hd-rest-num',H().girls.length+'/5'));if(!H().girls.length)rest.append(I('alert_icon','hd-badge'));rest.setAttribute('aria-label','Rest');tools.append(rest);root.append(tools);
 }
 function category(root){const nav=N('div','hd-categories');for(const [id,label]of [[0,'ALL'],[4,'Table'],[5,'Stool'],[6,'Bed'],[8,'Decor'],[9,'Wall Deco'],[1,'Floor'],[2,'Wall']])nav.append(B(label,()=>{filter=id;render();},id===filter?'active':''));root.append(nav);}
 function card(root,label,icon,fn,sub='',selected=false){const c=B('',fn,'hd-card'+(selected?' equipped':''));c.append(I(icon),N('b','',label),N('small','',sub));root.append(c);return c;}
 function usedCopies(id){return draft.filter(e=>e.id===id).length+Object.entries(H().rooms).filter(([f])=>f!==String(floor)).reduce((n,[f,entries])=>n+entries.filter(e=>e.id===id).length,0);}
 function place(id){const r=data.house_furniture[String(id)];let used=usedCopies(id);if((H().inventory[String(id)]||0)<=used){note="No spare copies available";render();return;}const uid=Math.max(0,...draft.map(e=>e.uid))+1;
  if([1,2,10].includes(r.type))draft=draft.filter(e=>row(e).type!==r.type);
  let e={uid,id,x:8,y:8,flip:0,plane:[2,9].includes(r.type)?'wall':r.type===10?'background':'floor',parent:0};
  if(e.plane==='floor'&&![1,3].includes(r.type)){const [w,h]=dims(e);outer:for(let y=0;y<=24-h;y++)for(let x=0;x<=24-w;x++){const free=draft.every(p=>{if(p.plane!=='floor'||p.parent||[1,3].includes(row(p).type))return true;const [pw,ph]=dims(p);return x+w<=p.x||x>=p.x+pw||y+h<=p.y||y>=p.y+ph;});if(free){e.x=x;e.y=y;break outer;}}}
  if(e.plane!=='floor'){e.x=0;e.y=0;}draft.push(e);selected=uid;selOrig=null;render();
 }
 function storage(root){const box=N('div','hd-storage');{const bar=N('div','hd-box-bar');bar.append(I('house_icon_5'),N('b','','Storage Box'));box.append(bar);}category(box);const grid=N('div','hd-storage-grid');for(const [id,count]of Object.entries(H().inventory)){const r=data.house_furniture[id];if(filter&&r.type!==filter)continue;const used=usedCopies(Number(id));card(grid,r.label,r.collection_img||String(r.img).split('|')[0],()=>place(Number(id)),(count-used)+'/'+count);}box.append(grid);root.append(box);}
 // HouseShopWindow: series tabs + house_icon_8 cards (comfort top-left, owned top-right, price button) over the room.
 function shop(root){room(root);root.classList.add('hd-hide');const over=N('div','hd-rest-over');const win=N('div','hd-rest-win hd-shop-win');over.append(win);
  const head=N('div','hd-rest-head');head.append(N('b','','Furniture Store'),B('',()=>{tab='room';note='';render();},'hd-rest-close'));win.append(head);
  const bar=N('div','hd-shop-bar');const select=N('select','hd-series');select.setAttribute('aria-label',"Furniture series");select.append(new Option('All series','0'));for(const [id,r]of Object.entries(data['en_en/house_furniture_group_text_en_en']))select.append(new Option(r.name,id));select.value=String(series);select.onchange=()=>{series=Number(select.value);render();};
  const balance=N('div','hd-shop-balance');balance.append(I('icon_69'),N('b','',number(state.items['69']||0)));bar.append(select,balance);win.append(bar);
  const grid=N('div','hd-shop-grid');for(const [id,s]of Object.entries(data.shop_house_furniture)){const [iid]=s.item.split('#');const r=data.house_furniture[iid];if(series&&r.group_id!==series)continue;const [cid,cost]=s.cost.split('#');
   const c=N('article','hd-shop-card');const cm=N('span','hd-shop-comfort');cm.append(I('house_icon_3'),N('b','',String(r.comfort)));c.append(cm,N('span','hd-shop-own',String(H().inventory[iid]||0)),I(r.collection_img||String(r.img).split('|')[0],'hd-shop-img'),N('b','hd-shop-name',r.label));
   const buy=B('',()=>send({action:'buy_furniture',shop_id:Number(id),count:1},'Comprado: '+r.label),'hd-shop-buy');buy.append(I(cid==='69'?'icon_69':'icon_'+cid),N('b','',cost));buy.disabled=busy||Number(state.items[cid]||0)<Number(cost)||(s.limit>=0&&(H().bought[id]||0)>=s.limit);c.append(buy);grid.append(c);}
  win.append(grid);root.append(over);}
 // HouseSelectHerosWindow: five slots on top (tap to remove), the roster below (tap to add), Cancel / Confirm; the room stays behind.
 function girls(root){room(root);root.classList.add('hd-hide');restDraft||=[...H().girls];const over=N('div','hd-rest-over');const win=N('div','hd-rest-win');over.append(win);
  const head=N('div','hd-rest-head');head.append(N('b','','Rest'),B('',()=>{restDraft=null;tab='room';render();},'hd-rest-close'));win.append(head);
  const icon=g=>typeof CampaignFlow!=='undefined'?CampaignFlow.heroIcon(g):portrait(g.table_id,80);
  const slots=N('div','hd-rest-slots');for(let i=0;i<5;i++){const id=restDraft[i],g=id&&state.roster.find(x=>x.partner_id===id);const s=B('',()=>{if(g){restDraft=restDraft.filter(x=>x!==id);render();}},'hd-rest-slot');s.append(g?icon(g):I('icon_none'));slots.append(s);}win.append(slots);
  win.append(N('p','hd-rest-tip',"Selected Girls are resting in the Cafe"));
  const acts=N('div','hd-rest-acts');acts.append(B('Cancel',()=>{restDraft=null;tab='room';render();},'hd-rest-btn white'),B('Confirm',async()=>{const ids=restDraft;restDraft=null;if(await send({action:'girls',ids},''))tab='room';render();},'hd-rest-btn'));win.append(acts);
  const list=N('div','hd-rest-list');const seen=[...state.roster].sort((a,b)=>(b.stars||0)-(a.stars||0)||(b.lv||0)-(a.lv||0));
  for(const g of seen){const on=restDraft.includes(g.partner_id);const c=B('',()=>{if(on)restDraft=restDraft.filter(x=>x!==g.partner_id);else if(restDraft.length>=5){note="Up to 5 Girls";}else restDraft=[...restDraft,g.partner_id];render();},'hd-rest-pick'+(on?' on':''));c.append(icon(g));list.append(c);}
  win.append(list);root.append(over);}
 async function dressModel(host,styles,width=480,height=320,scale=.8){
  const gen=generation,rows=[1,2,3].map(pos=>data.senpai_dress_style[String(styles[String(pos)])]);
  try{
   const parts=await Promise.all(rows.map(r=>GxbSpine.load('/assets/original-ui/house-dress/models/'+r.resource)));
   if(gen!==generation||!host.isConnected)return;
   const app=new PIXI.Application({width,height,transparent:true,antialias:true,resolution:2,autoDensity:true});app.view.style.width=width+'px';app.view.style.height=height+'px';host.append(app.view);
   const layers=[];
   // Original prefabs split head at face_layer and body at body_layer; SenpaiModel
   // assigns base depths1/2/3 and separator increments9/5. Reproduce that order.
   for(let p=0;p<3;p++){
    const d=parts[p],r=rows[p],separator=(data.separators[r.resource]||[])[0],cut=separator?d.slots.findIndex(s=>s.name===separator):-1;
    for(const front of cut<0?[false]:[false,true]){
     const fig=new PIXI.spine.Spine(d);fig.autoUpdate=false;fig.scale.set(scale);fig.position.set(width/2,height*.76);
     const idle=d.animations.find(a=>a.name==='idle')||d.animations[0];if(idle)fig.state.setAnimation(0,idle.name,true);
     const depth=p+1+(front?(p===0?9:5):0);layers.push({fig,cut,front,depth});
    }
   }
   layers.sort((a,b)=>a.depth-b.depth);for(const l of layers)app.stage.addChild(l.fig);
   const extras=[];
   for(const pos of [4,5]){
    const r=data.senpai_dress_style[String(styles[pos])];if(!r||!data.sizes[r.resource])continue;
    const part=pos===4?1:2;const owner=layers.find(l=>{if(![part,part+(part===1?9:5)].includes(l.depth))return false;const i=l.fig.skeleton.findSlot(r.slot)?.data.index;return i!==undefined&&(l.cut<0||(l.front?i>=l.cut:i<l.cut));});
    const slot=owner?.fig.skeleton.findSlot(r.slot);if(!slot)continue;
    const wrapper=new PIXI.Container(),sprite=PIXI.Sprite.from(A(r.resource));sprite.anchor.set(.5);
    const offset=String(r.offset).split('|').map(Number),sz=String(r.scale).split('|').map(Number);sprite.position.set(offset[0]||0,-(offset[1]||0));sprite.scale.set(sz[0]||1,sz[1]||1);sprite.rotation=-(Number(r.rotation)||0)*Math.PI/180;wrapper.addChild(sprite);
    const c=owner.fig.slotContainers[slot.data.index];c.addChild(wrapper);extras.push({owner,c,slot});
   }
   function tick(delta){for(const l of layers){l.fig.update(delta/60);for(let i=0;i<l.fig.slotContainers.length;i++)l.fig.slotContainers[i].renderable=l.cut<0||(l.front?i>=l.cut:i<l.cut);}
    for(const e of extras){e.c.visible=true;e.c.transform.setFromMatrix(e.slot.bone.matrix);}}
   tick(0);app.ticker.add(tick);
   handles.push({destroy:()=>{try{app.destroy(true,{children:true,texture:false,baseTexture:false});}catch{}}});
  }catch{if(gen===generation&&host.isConnected)host.append(N('p','',"Preview pending"));}
 }

 function wardrobe(root){const tabs=N('div','hd-wardrobe-tabs');tabs.append(B('Locker Room',()=>{tab='room';render();},tab==='room'?'active':''),B('Closet',()=>{tab='closet';render();},tab==='closet'?'active':''));root.append(tabs);const hero=N('div','hd-dress-preview');const canvas=N('div','hd-dress-model');hero.append(canvas);dressModel(canvas,outfit);const slots=N('div','hd-dress-slots');for(let p=1;p<=5;p++){const r=data.senpai_dress_style[String(outfit[p])];const slot=B('',()=>{filter=p;render();},'hd-slot slot-'+p);slot.append(r?I('icon_'+r.image):N('span','',p===4?'Headwear':'Accessory'));slot.title=['','Head','Body','Legs','Headwear','Accessory'][p];slot.setAttribute('aria-label',slot.title);slots.append(slot);}hero.append(slots);root.append(hero);const actions=N('div','hd-dress-actions');actions.append(B('Cancel',()=>{outfit=clone(H().outfit);note='';render();}),B('Save',()=>send({action:'equip',styles:Object.values(outfit).map(Number)})));root.append(actions);const cats=N('div','hd-categories');for(let p=0;p<=5;p++)cats.append(B(['ALL','Head','Body','Legs','Headwear','Accessory'][p],()=>{filter=p;render();},filter===p?'active':''));root.append(cats);const grid=N('div','hd-closet-grid');for(const id of H().styles){const r=data.senpai_dress_style[String(id)];if(filter&&r.pos!==filter)continue;const dr=data.senpai_dress[String(r.dress_id)];const item=String(dr.items).split('|').find(k=>H().clothes[k]);const ir=data.senpai_dress_item[item];card(grid,ir?.label||['','Head','Body','Legs','Headwear','Accessory'][r.pos],'icon_'+r.image,()=>{if(r.pos>=4&&outfit[String(r.pos)]===id)delete outfit[String(r.pos)];else outfit[String(r.pos)]=id;note='';render();},H().clothes[item]||'',outfit[String(r.pos)]===id);}root.append(grid);}
 function dressStore(root){const stage=N('div','hd-outfit-store');stage.append(I('dress_summon_normal_bg','hd-outfit-banner'),I('dress_summon_logo_en_en','hd-outfit-logo'));const money=N('div','hd-dress-currency');money.append(I('icon_258'),N('b','',number(state.items['258']||0)));stage.append(money);const actions=N('div','hd-dress-actions');for(const n of [1,10]){const b=B('Purchase '+n+' · '+n,()=>{},'hd-gold');b.disabled=true;actions.append(b);}stage.append(actions,N('p','hd-store-note',"Outfit purchases: coming soon"));root.append(stage);const strip=N('div','hd-outfit-prizes');strip.append(N('h3','','Available Outfits'));const items=N('div','hd-outfit-strip');for(const id of String(data.misc.dress_gacha_show).split('|')){const r=data.senpai_dress_item[id];if(r)card(items,r.label,String(r.icon).split('|')[0],()=>{note=r.label;render();},'');}strip.append(items);root.append(strip);}
 // HouseComfortWindow: comfort, the three resources produced since the last Collect (house_award rate × 5 s ticks, 12 h cap)
 function comfortWin(){const {body,close}=GirlUI.win({title:'Comfort',cls:'hd-comfort'});const hg=H().hang||{award:{},rate:{}};
  const head=N('div','hd-cf-head');head.append(I('house_icon_3'),N('b','',number(H().comfort)));body.append(head,N('p','hd-cf-tip',"The Dorm's resource output will increase according to its comfort level."));
  const row=N('div','hd-cf-row');for(const k of ['1','2','14']){const c=N('div','hd-cf-item');const it=itemCatalog?.[k];const src=k==='1'||k==='2'?'/assets/currency/icon_'+k+'_small.png':(it&&typeof itemPicture==='function'?itemPicture(it):'');const im=N('img');im.src=src;im.alt='';c.append(im,N('b','',number(hg.award?.[k]||0)),N('small','',it?.name||(k==='1'?'Coin':'Gem')));row.append(c);}body.append(row);
  if(hg.full_at){const left=Math.max(0,hg.full_at-Math.floor(Date.now()/1000));body.append(N('p','hd-cf-full',left?'Full in '+Math.floor(left/3600)+'h '+Math.floor(left%3600/60)+'m':'Storage full (12 h)'));}
  const b=B('Collect',async()=>{b.disabled=true;try{const r=await api('/api/house-dress/action',{action:'hang_collect'});state=r.state;close();CampaignUI.popup('Comfort',r.got||{});render();}catch(e){GirlUI.toast(e.message);b.disabled=false;}},'gs-btn hd-cf-get');b.disabled=!Object.keys(hg.award||{}).length;body.append(b);}
 return {open,render};
})();
