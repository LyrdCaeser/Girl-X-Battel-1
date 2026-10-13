'use strict';
// Deep Sea Treasures (329; captures docs/references/2026-09-30-user/05-06): five lands to Raid, chest collection progress, daily
// compasses and the free pack. Palace Vaults (330; capture 07): Secret Vault shop (generic ActKit) + Collection Reward. Rules: gxb2/pirate.py. Prefix pi-.
const Pirate=(()=>{
 let data=null,loading=null,host=null,busy=false,raid=null,note='',mode='deep',vtab='shop',last=null;
 const A=n=>'/assets/pirate/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis||busy;return b;};
 const fmt=n=>typeof number==='function'?number(Number(n)):String(n);
 const pairs=t=>String(t||'').split('|').filter(s=>s.includes('#')).map(s=>s.split('#'));
 const info=()=>state.pirate_info;
 const T=k=>data.text[k]||'';
 function load(){if(data)return Promise.resolve(data);if(!loading)loading=api('/assets/pirate.json').then(d=>{data=d;});return loading;}
 function name(id){return itemCatalog?.[id]?.name||data.names[id]||"Item "+id;}
 function icon(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}return null;}
 function chip(id,n,extra){const w=el('span','pi-chip');const s=icon(id);if(s)w.append(img(s));else w.append(el('em','',name(id)));w.append(el('b','',fmt(n)));if(extra)w.append(el('small','',extra));w.title=name(id);return w;}
 async function act(req){if(busy)return null;busy=true;note='';try{const r=await api('/api/pirate/action',req);state=r.state;if(r.got&&Object.keys(r.got).length)note="Received: "+Object.entries(r.got).map(([k,n])=>fmt(n)+' × '+name(k)).join(', ');return r;}catch(e){note=e.message;return null;}finally{busy=false;}}
 async function render(parent){await load();host=parent;mode='deep';raid=null;paint();if(!info().started)act({action:'open'}).then(()=>{if(host?.isConnected)paint();});}
 async function vaults(parent){await load();host=parent;mode='vault';paint();}
 function paint(){if(!host)return;host.querySelector('.pi-root')?.remove();const root=el('div','pi-root '+mode);host.append(root);if(mode==='vault')return paintVaults(root);
  const s=info();root.append(el('h2','pi-logo pi-logo-vi','Kho Báu Biển Sâu'));
  const top=el('div','pi-top');top.append(chip(410,s.compass),btn('pi-mini'+(s.daily_ready?' go':''),s.daily_ready?'+'+s.daily+" hằng ngày":'✔',async()=>{await act({action:'daily'});paint();},!s.daily_ready),chip(411,s.coin),
   btn('pi-mini'+(s.pack_ready?' go':''),s.pack_ready?"Gói Miễn Phí":'✔',async()=>{await act({action:'pack'});paint();},!s.pack_ready),btn('pi-mini','?',()=>CampaignUI.popup((T('ACTIVITY_PIRATE_HELP')||'').split('|').join('\n'),{})));root.append(top);
  const map=el('div','pi-map');[[4,0],[56,14],[2,36],[34,44],[54,62]].forEach(([x,y],i)=>{const l=el('div','pi-land');l.style.left=x+'%';l.style.top=y+'%';l.append(img(A('activity_pirate_land'+(i+1)),'pi-land-img'),el('b','',T('ACTIVITY_PIRATE_PLACE'+(i+1))),btn('pi-raid','Đột Kích',()=>{raid={land:i+1,num:1};paint();}));map.append(l);});root.append(map);
  const col=el('div','pi-col');col.append(el('b','','Tiến Độ Sưu Tập'));const row=el('div','pi-chests');data.collection.forEach((c,i)=>{const w=el('span','pi-chest'+(s.have[c.item]>=c.need?' got':''));w.append(img(A('activity_pirate_icon_box'+(i+1)),'pi-chest-img'),el('small','',Math.min(s.have[c.item],c.need)+'/'+c.need));w.title=name(c.item);row.append(w);});col.append(row,btn('pi-go','Đến Kho Báu',()=>{if(typeof EventsHub!=='undefined')EventsHub.openPoint(330,'home');}));root.append(col);
  root.append(el('p','pi-note',note||''),el('small','pi-foot',"Total raids: "+s.raids+" · Guaranteed chest in "+s.guarantee_in+" raid(s)"));
  if(raid)root.append(raidWindow(s));}
 function raidWindow(s){const ov=el('div','pi-overlay'),w=el('div','pi-win');ov.append(w);const land=data.lands[raid.land-1];
  const head=el('div','pi-win-h');head.append(el('b','',('{1} - Đột Kích').replace('{1}',T('ACTIVITY_PIRATE_PLACE'+raid.land))),btn('pi-x','✕',()=>{raid=null;paint();}));w.append(head,el('h4','','Thưởng Mỗi Lần Đột Kích'),el('small','','Phần Thưởng'));
  const rw=el('div','pi-list');const [ck,cn]=pairs(data.misc.activity_pirate_drop_awards)[0];rw.append(chip(ck,cn,'100%'));const tot=land.drop.reduce((a,b)=>a+b.weight,0);for(const d of land.drop){const [k,n]=pairs(d.awards)[0];rw.append(chip(k,n,(Math.round(1000*d.weight/tot)/10)+'%'));}w.append(rw);
  w.append(el('small','','Rương'));const cl=el('div','pi-list');const ct=data.chests.reduce((a,b)=>a+b.weight,0);data.chests.forEach((c,i)=>{const [k,n]=pairs(c.awards)[0];const x=chip(k,n,(Math.round(1000*c.weight/ct)/10)+'%');cl.append(x);});w.append(cl);
  const max=Math.max(1,Math.min(100,s.compass));const q=el('div','pi-qty');q.append(btn('pi-mini','|◀',()=>{raid.num=1;paint();}),btn('pi-mini','−',()=>{raid.num=Math.max(1,raid.num-1);paint();}),el('b','pi-num',String(raid.num)),btn('pi-mini','+',()=>{raid.num=Math.min(max,raid.num+1);paint();}),btn('pi-mini','▶|',()=>{raid.num=max;paint();}));w.append(el('small','','Chọn Số Lượng'),q,el('small','',raid.num+'/'+s.compass));
  w.append(btn('pi-go big','Đột Kích',async()=>{const r=await act({action:'raid',land:raid.land,num:raid.num});if(r){last=r;raid=null;if(r.chests?.length&&typeof GirlUI!=='undefined')GirlUI.toast(" "+r.chests.length+' rương!');}paint();},s.compass<raid.num),el('small','pi-guar',('Bảo đảm nhận Rương sau {1} lần đột kích').replace(/\[[^\]]*\]/g,'').replace('{1}',s.guarantee_in)));return ov;}
 function paintVaults(root){const nav=el('nav','pi-tabs');for(const [id,label] of [['shop','Kho Bí Mật'],['col','Thưởng Sưu Tập']])nav.append(btn('pi-tab'+(vtab===id?' on':''),label,()=>{vtab=id;paint();}));root.append(nav);
  if(vtab==='shop'){const box=el('div','pi-shop');root.append(box);if(typeof ActKit!=='undefined')ActKit.render(box,{id:330});return;}
  const s=info(),list=el('div','pi-clist');data.collection.forEach((c,i)=>{const have=Math.min(s.have[c.item],c.need),done=s.claimed.includes(c.id);const row=el('div','pi-crow'+(done?' done':''));row.append(img(A('activity_pirate_icon_box'+(i+1)),'pi-chest-img'),el('span','pi-bar',have+'/'+c.need));const rw=el('span','pi-rw');for(const [k,n] of pairs(c.awards))rw.append(chip(k,n));row.append(rw,btn('pi-go'+(have>=c.need&&!done?' ok':''),done?'✔':('Nhận'),async()=>{await act({action:'collect',id:c.id});paint();},have<c.need||done));list.append(row);});root.append(list,el('p','pi-note',note));}
 return {render,vaults};
})();
