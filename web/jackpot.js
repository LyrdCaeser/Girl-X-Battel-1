'use strict';
// Jackpot of Fortune (activity 64; capture 2026-09-29-fb/3): cat machine with three reels of heads, Basic/Super, bet x1/2/5/10,
// Jackpot Energy, progress awards and coin transfer; the exchange shop is the generic ActKit panel. Rules: gxb2/jackpot.py. Prefix jp-.
const Jackpot=(()=>{
 let data=null,loading=null,host=null,mode='basic',betIx=0,tab='machine',busy=false,spinning=false,last=null,note='';
 const A=n=>'/assets/jackpot/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 const fmt=n=>typeof number==='function'?number(Number(n)):String(n);
 const pairs=t=>String(t||'').split('|').filter(s=>s.includes('#')).map(s=>s.split('#'));
 const info=()=>state.jackpot_info;
 function load(){if(data)return Promise.resolve(data);if(!loading)loading=api('/assets/jackpot.json').then(d=>{data=d;});return loading;}
 function name(id){return itemCatalog?.[id]?.name||({57:'Jackpot Energy',58:'Jackpot Coin',305:'Super Jackpot Coin'})[id]||"Item "+id;}
 function icon(id){id=String(id);if(id==='2'||id==='1')return '/assets/currency/icon_'+id+'_small.png';if(id==='57')return A('jackpot_energy_icon');const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}return null;}
 function chip(id,n){const w=el('span','jp-chip');const s=icon(id);if(s)w.append(img(s));else w.append(el('em','',name(id)));w.append(el('b','',fmt(n)));w.title=name(id);return w;}
 async function act(req){if(busy)return null;busy=true;note='';try{const r=await api('/api/jackpot/action',req);state=r.state;return r;}catch(e){note=e.message;return null;}finally{busy=false;}}
 async function render(parent){await load();host=parent;paint();if(!info().started)act({action:'open'}).then(()=>{if(host?.isConnected)paint();});}
 function place(e,x,y,w,h){e.style.left=x/6.95+'%';e.style.top=y/9.7+'%';e.style.width=w/6.95+'%';if(h)e.style.height=h/9.7+'%';return e;}
 function head(pos){return data.heads[pos][mode];}
 function reelCol(pos,blur){const col=el('div','jp-col'+(blur?' spin':''));const order=blur?[1,2,3,2,1,3,1,3,2,1,2,3]:[(pos%3)+1,pos,((pos+1)%3)+1];for(const p of order)col.append(img(A(head(p)+(blur?'_vague':'')),'jp-head'));return col;}
 function paint(){if(!host)return;host.querySelector('.jp-root')?.remove();const s=info(),root=el('div','jp-root');host.append(root);
  const nav=el('nav','jp-tabs');for(const [id,label] of [['machine',"Machine"],['exchange','Canje']]){nav.append(btn('jp-tab'+(tab===id?' on':''),label,()=>{tab=id;paint();}));}root.append(nav);
  if(tab==='exchange'){const box=el('div','jp-ex');root.append(box);if(typeof ActKit!=='undefined')ActKit.render(box,{id:64});return;}
  const top=el('div','jp-top');top.append(chip(58,s.coin),chip(305,s.super_coin),btn('jp-help','?',()=>CampaignUI.popup((data.text.ACTIVITY_JACKPOT_HELP||'Spin the machine with Jackpot Energy to win coins.').split('|').join('\n'),{})));root.append(top);
  const st=el('div','jp-stage');root.append(st);st.append(img(A(mode==='basic'?'jackpot_machine':'jackpot_senior_machine'),'jp-machine'));
  st.append(place(img(A(mode==='basic'?'jackpot_normal_en_en':'jackpot_senior_en_en'),'jp-title'),210,120,275));
  [[118,147],[277,141],[430,147]].forEach(([x,w],i)=>{const win=place(el('div','jp-reel'),x,240,w,285);win.append(reelCol(last?last.pos[i]:s.pos[i],spinning));st.append(win);});
  const bet=s.bets[betIx],cost=bet*s.base_cost;
  const plate=place(el('div','jp-plate'),195,585,305,130);plate.append(btn('jp-bet','Usar ×'+cost,()=>{betIx=(betIx+1)%s.bets.length;paint();}),(()=>{const e=el('div','jp-energy');e.append(img(A('jackpot_energy_icon')),el('b','',s.energy+' / '+s.limit));return e;})());st.append(plate);
  const locked=mode==='super'&&!s.super_open;
  const spin=place(btn('jp-spin',spinning?'…':'Girar',spin_,busy||spinning||s.energy<cost||locked),150,760,395,120);st.append(spin);
  st.append(place(btn('jp-mode'+(mode==='basic'?' on':''),'Basic',()=>{mode='basic';last=null;paint();}),10,780,125,100),place(btn('jp-mode super'+(mode==='super'?' on':''),'Super',()=>{mode='super';last=null;paint();}),560,780,125,100));
  const foot=el('div','jp-foot');foot.append(el('small','',s.energy<s.limit&&s.next_at?"Next energy in "+clock(s.next_at):"Energy full"));if(!s.super_open)foot.append(el('small','',"Super unlocks after "+s.unlock+" draws ("+s.spins+')'));
  if(last&&last.got&&Object.keys(last.got).length){const g=el('div','jp-got');for(const [k,n] of Object.entries(last.got))g.append(chip(k,n));foot.append(el('b','',"Reward"),g);}else if(last)foot.append(el('b','',"No reward"));
  root.append(foot,el('p','ak-note',note));
  const conv=el('div','jp-conv');conv.append(btn('jp-btn','Convertir 1 moneda Basic → Super',async()=>{await act({action:'transfer',count:1});paint();},s.coin<1||busy));root.append(conv);
  const list=el('div','jp-list');data.awards.forEach((a,i)=>{const done=s.claimed.includes(i),ok=s.senior>=a.need;const row=el('div','jp-row'+(done?' done':''));row.append(el('span','','Super: '+a.need+" energy ("+Math.min(s.senior,a.need)+')'));const rw=el('span','jp-rw');for(const [k,n] of pairs(a.awards))rw.append(chip(k,n));row.append(rw,btn('jp-btn'+(ok&&!done?' go':''),done?'✔':"Claim",async()=>{await act({action:'claim',index:i});paint();},!ok||done||busy));list.append(row);});root.append(el('h4','jp-h',"Progress rewards (energy spent in Super)"),list);}
 const clock=at=>{const t=Math.max(0,at-(state.server_time||0));return [Math.floor(t/3600),Math.floor(t%3600/60),t%60].map(n=>String(n).padStart(2,'0')).join(':');};
 async function spin_(){spinning=true;last=null;paint();const t0=Date.now();const r=await act({action:'spin',mode,bet:info().bets[betIx]});const wait=Math.max(0,1400-(Date.now()-t0));await new Promise(x=>setTimeout(x,wait));spinning=false;last=r||null;paint();}
 return {render};
})();
