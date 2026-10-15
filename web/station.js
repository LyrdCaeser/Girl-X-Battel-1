// Partner Data Station ("Student Files", partner_data_station_window.prefab), opened by Discuss in the Dates window.
// Ring binder (station_bg_top1 cover + station_bg_top2 page) with three sticker tabs: Strategy (radar over
// direct_partner_point_full, Tags, Description, Rank, Skill Description, Recommended Antique), Lineup (Dummy Test /
// Tests / Guild Boss popular line-ups from direct_array with their Popularity stars) and Review (Like, the player's
// Tags and Comments — LOCAL-074: kept in the save, there is no online board). Coordinates: prefab units, y up, 720×1280.
const Station=(()=>{
 const S='/assets/station/';let world={hot:[],likes:0},data=null,root=null,cid=null,tab=0,card=0,rec=null,note='',line=0,popup=null,host=null;
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=typeof GxbVi!=='undefined'?GxbVi.t(text):text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const at=(e,x,y,w,h)=>{e.style.left=`calc(${x-w/2+360} * var(--u))`;e.style.top=`calc(${640-y-(h||0)/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;if(h!=null)e.style.height=`calc(${h} * var(--u))`;return e;};
 const u=()=>(host?.getBoundingClientRect().width||720)/720;
 const TABS=[['Strategy','direction',-217],['Lineup','array',-64],['Review','comment',89]];
 const POINTS=[['Attack',161,395],['Armor',254,315],['Speed',228,192],['Control',93,192],['HP',64,315]];
 const LINES=['Dummy Test','Tests','Guild Boss','Junior Varsity'];
 function find(tid){const ids=typeof hostChain==='function'?hostChain(tid):[Number(tid)];for(const [k,g]of Object.entries(data.girls))if(g.ids.some(i=>ids.includes(i)||i%100000===Number(tid)%100000))return k;return null;}
 async function call(req){try{const r=await api('/api/relations/action',{...req,id:cid});if(r.state)state=r.state;rec=r.station;world={hot:r.hot||[],likes:r.likes||0};note='';return r;}catch(e){note=e.message;return null;}finally{render();}}
 async function open(tableId){data=data||await api('/assets/station/station.json');cid=find(tableId);if(!cid)return false;
  tab=0;card=Math.max(0,data.girls[cid].ids.indexOf(Number(tableId)));line=0;note='';popup=null;host=document.querySelector('.dates-view')||window.GxbFrame?.root()||document.body;
  rec={like:0,labels:[],comments:[]};render();await call({action:'station'});return true;}
 function close(){root?.remove();root=null;}
 function render(){if(!cid)return;root?.remove();root=el('div','st-root');const g=data.girls[cid];
  const cover=at(img(S+'station_bg_top1.png','st-abs'),-71,32,862,1024),cb=at(img(S+'station_bg_bottom1.png','st-abs'),-77,-536,862,114);
  const page=at(img(S+'station_bg_top2.png','st-abs'),-71,32,862,1024),pb=at(img(S+'station_bg_bottom2.png','st-abs'),-77,-534,862,114);root.append(cover,cb,page,pb);
  TABS.forEach(([name,key,x],i)=>{const b=at(el('button','st-tab'+(tab===i?' on':'')),x,560+(tab===i?6:0),144,90);b.type='button';b.style.backgroundImage=`url('${S}station_img_${key}${tab===i?'_click':''}.png')`;
   b.append(img(S+`station_icon_${key}${tab===i?'_click':''}.png`),el('span','',name));b.onclick=()=>{if(i<2&&!g.skills.length){note='Coming soon~';render();return;}tab=i;popup=null;render();};root.append(b);});
  const x=at(el('button','st-close'),275,566,70,64);x.type='button';x.style.backgroundImage=`url('${S}station_close_img.png')`;x.setAttribute('aria-label',"Close");x.onclick=close;root.append(x);
  root.append(title(['Strategies','Lineup','Discuss'][tab]));cardBox(g);
  if(tab<2)radar(g);[strategy,lineup,review][tab](g);
  if(note){const n=at(el('p','st-note',note),0,-590,600,null);root.append(n);}
  if(popup)popup();host.append(root);}
 function title(t){const b=at(el('div','st-title'),0,478,508,78);b.style.backgroundImage=`url('${S}station_title_bg.png')`;b.append(el('b','',t));return b;}
 // group4: the girl's card (partner_card of each id in table_ids), btnChange cycles the re-issues
 function cardBox(g){const box=at(el('div','st-card'),-142,294,295,264);const id=g.ids[card%g.ids.length];
  const p=portrait(id,Math.round(230*u()));p.classList.add('st-portrait');box.append(p,at(img(S+'station_mask_left.png','st-mask l'),-118,0,64,315),at(img(S+'station_mask_right.png','st-mask r'),106,0,66,315));
  box.append(el('b','st-name',g.name||girlName(id)));root.append(box);
  if(g.ids.length>1){const c=at(el('button','st-change'),281,481,52,52);c.type='button';c.style.backgroundImage=`url('${S}partner_station_change.png')`;c.title="Change version";c.onclick=()=>{card++;render();};root.append(c);}}
 function girlName(id){return (typeof girlsCatalog!=='undefined'&&girlsCatalog.find(x=>x.id===Number(id))?.name)||'';}
 // pentagonForce: radius 92 around (159,287), ATK at the top then clockwise
 function radar(g){const bg=at(img(S+'station_radar_bg_bottom.png','st-abs'),162,294,208,200),fw=at(img(S+'station_radar_bg_top.png','st-abs st-radar-top'),162,294,208,200);
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','-100 -100 200 200');svg.classList.add('st-radar');at(svg,159,287,200,200);
  const pts=g.points.map((v,i)=>{const a=-Math.PI/2+i*2*Math.PI/5,r=92*Math.min(1,v/data.full);return `${(r*Math.cos(a)).toFixed(1)},${(r*Math.sin(a)).toFixed(1)}`;}).join(' ');
  const poly=document.createElementNS('http://www.w3.org/2000/svg','polygon');poly.setAttribute('points',pts);svg.append(poly);root.append(bg,svg,fw);
  POINTS.forEach(([n,x,y])=>root.append(at(el('span','st-point',n),x,y,90,22)));}
 function section(title,body){const s=el('section','st-sec');const t=el('div','st-sticker');t.style.backgroundImage=`url('${S}station_small_formation_bg.png')`;t.append(el('b','',title));const b=el('div','st-body');b.append(...[].concat(body));s.append(t,b);return s;}
 function chip(id,on,click){const L=data.labels[String(id)];if(!L)return el('span');const c=el(click?'button':'span','st-chip'+(on?' on':''),L.text);if(click)c.type='button';c.style.backgroundImage=`url('${S}${L.icon}${on?'_click':''}.png')`;c.style.setProperty('--c',L.color);if(click)c.onclick=click;return c;}
 function strategy(g){const sc=at(el('div','st-scroll'),6,-215,649,671);
  const tags=el('div','st-chips');g.labels.forEach(id=>tags.append(chip(id)));
  const rank=el('div','st-rank');for(const t of ['Patrol:','Junior Varsity:','Tests:','Guild Boss:'])rank.append(el('span','',t),el('b','','No Record'));
  const skills=g.skills.map(s=>{const r=el('div','st-skill');const i=el('div','st-skill-icon');i.style.backgroundImage=`url('/assets/detail/skill_icon_bg.png')`;if(s.icon)i.append(img('/assets/skills/'+s.icon+'.png'));const t=el('div');t.append(el('b','',s.name),el('p','',s.desc));r.append(i,t);return r;});
  const arts=g.artifacts.map(a=>{const r=el('div','st-skill');const i=el('div','st-skill-icon');const it=typeof itemCatalog!=='undefined'?itemCatalog?.[String(a.id)]:null;const src=it&&typeof itemPicture==='function'?itemPicture(it):'';if(src)i.append(img(src));const t=el('div');t.append(el('b','',a.name),el('p','',a.desc));r.append(i,t);return r;});
  sc.append(section('Tags',tags),section('Description',el('p','st-desc',g.desc||'—')),section('Rank',rank),section('Skill Description',skills.length?skills:el('p','st-desc','—')),section('Recommended Antique',arts.length?arts:el('p','st-desc','—')));root.append(sc);}
 function lineup(g){const bg=at(el('div','st-lbg'),0,-203,674,709);bg.style.borderImageSource=`url('${S}station_small_label_bg.png')`;root.append(bg);
  LINES.forEach((n,i)=>{const b=at(el('button','st-ltab'+(line===i?' on':''),n),[-230,-76,78,232][i],117,150,52);b.type='button';b.style.backgroundImage=`url('${S}station_small_label${line===i?'_click':''}.png')`;b.onclick=()=>{line=i;render();};root.append(b);});
  const panel=at(el('div','st-lpanel'),7.5,-223,621,551);panel.style.borderImageSource=`url('${S}station_bg.png')`;root.append(panel);
  const lt=at(el('div','st-ltitle','Lineup'),-229,52,148,37);lt.style.backgroundImage=`url('${S}station_small_title_bg.png')`;root.append(lt);
  const L=line<3?g.lineups[line]:null;const ok=L&&L.ids.length>=6&&L.ids.every(id=>id>10000&&id!==40000);
  if(!ok){const none=at(el('div','st-none'),0,-185,250,270);none.append(img('/assets/station/bp_none_bg.png'),el('p','',line===3?'Junior Varsity records came from other players online.':'No suitable Lineup now~'));root.append(none);return;}
  const f=at(el('div','st-form'),8,-165,595,245);f.style.backgroundImage=`url('${S}station_formation_bg01.png')`;
  const head=el('div','st-form-head');const stars=el('span','st-stars');for(let i=0;i<L.stars;i++)stars.append(img(S+'station_star.png'));head.append(el('b','','Popular Lineup'),el('span','','Popularity'),stars);f.append(head);
  const row=el('div','st-form-row');const px=Math.round(72*u());const front=el('div','st-front'),back=el('div','st-back');L.ids.forEach((id,i)=>(i<2?front:back).append(portrait(id,px)));row.append(front,back);f.append(row);
  const d=el('button','st-blue','Details');d.type='button';d.style.backgroundImage=`url('/assets/girl-ui/blue_btn_65_65.png')`;d.onclick=()=>{popup=()=>details(L);render();};f.append(d);root.append(f);}
 function details(L){const w=el('div','st-pop-wrap');const b=el('div','st-pop');b.append(el('b','st-pop-title','Popular Lineup'));
  L.ids.forEach((id,i)=>{const r=el('div','st-pop-row');r.append(portrait(id,Math.round(64*u())),el('span','',girlName(id)||('#'+id)),el('small','',i<2?'Front':'Back'));b.append(r);});
  const x=el('button','st-blue','OK');x.type='button';x.style.backgroundImage=`url('/assets/girl-ui/blue_btn_65_65.png')`;x.onclick=()=>{popup=null;render();};b.append(x);w.append(b);w.onclick=e=>{if(e.target===w){popup=null;render();}};root.append(w);}
 function review(g){const like=at(el('button','st-like'),158,328,80,84);like.type='button';like.style.backgroundImage=`url('${S}left_btn_bg.png')`;like.append(img(S+(rec.like?'partner_like01.png':'partner_like02.png')),el('small','','Like'));like.onclick=()=>{if(!rec.like)call({action:'station_like'});};
  root.append(like,at(el('span','st-like-t','Heart Received!'),158,268,200,22),at(el('b','st-like-n',typeof number==='function'?number(world.likes||rec.like||0):String(world.likes||0)),158,240,100,26));
  const tags=at(el('div','st-rtags'),10,110,623,100);tags.style.borderImageSource=`url('${S}station_formation_bg.png')`;const st=el('div','st-sticker');st.style.backgroundImage=`url('${S}station_small_formation_bg.png')`;st.append(el('b','','Tags'));
  const chips=el('div','st-chips');(rec.labels||[]).forEach(id=>chips.append(chip(id)));const cu=el('button','st-custom');cu.type='button';cu.style.backgroundImage=`url('${S}station_label_custom.png')`;cu.append(el('b','','+'),el('span','','Customize'));cu.onclick=()=>{popup=()=>pickLabels();render();};chips.append(cu);tags.append(st,chips);root.append(tags);
  const box=at(el('div','st-rcomments'),10,-222,623,420);box.style.borderImageSource=`url('${S}station_formation_bg.png')`;const s2=el('div','st-sticker');s2.style.backgroundImage=`url('${S}station_small_formation_bg.png')`;s2.append(el('b','','Comment'));box.append(s2);
  const list=el('div','st-clist');for(const c of world.hot||[]){const r=el('div','st-comment hot');const who=el('div','st-who');who.append(el('b','',c.name),el('small','','Lv.'+c.lv+' · '+new Date(c.time*1000).toLocaleDateString()));r.append(who,el('p','',c.text),el('span','st-clikes','♥ '+c.likes));list.append(r);}
  (rec.comments||[]).forEach((c,i)=>{const r=el('div','st-comment');const who=el('div','st-who');const av=state?.profile?.avatar||state?.avatar;who.append(el('b','',state?.name||'Senpai'),el('small','',new Date(c.time*1000).toLocaleString()));const del=el('button','st-del','✕');del.type='button';del.title='Xóa';del.onclick=()=>call({action:'station_delete',index:i});r.append(who,el('p','',c.text),del);list.append(r);});box.append(list);root.append(box);
  const bar=at(el('form','st-input'),4,-508,623,95);const ta=el('input');ta.maxLength=400;ta.placeholder="Let's send a message!";ta.style.backgroundImage=`url('${S}comic_comment_input_bg.png')`;const send=el('button','st-send');send.type='submit';send.style.backgroundImage=`url('${S}comic_comment_send_btn.png')`;send.setAttribute('aria-label',"Send");
  bar.onsubmit=e=>{e.preventDefault();call({action:'station_comment',text:ta.value});};bar.append(ta,send);root.append(bar);}
 function pickLabels(){const sel=new Set(rec.labels||[]);const w=el('div','st-pop-wrap');const b=el('div','st-pop');b.append(el('b','st-pop-title','Tags'),el('p','st-pop-note',"Choose up to 3 tags"));const grid=el('div','st-chips wrap');
  const paint=()=>{grid.replaceChildren();Object.keys(data.labels).forEach(k=>grid.append(chip(k,sel.has(Number(k)),()=>{const n=Number(k);if(sel.has(n))sel.delete(n);else if(sel.size<3)sel.add(n);paint();})));};paint();b.append(grid);
  const ok=el('button','st-blue','OK');ok.type='button';ok.style.backgroundImage=`url('/assets/girl-ui/blue_btn_65_65.png')`;ok.onclick=()=>{popup=null;call({action:'station_labels',labels:[...sel]});};b.append(ok);w.append(b);w.onclick=e=>{if(e.target===w){popup=null;render();}};root.append(w);}
 return {open,close};
})();
