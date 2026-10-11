'use strict';
// Halloween Pumpkin Patch (activity 150; capture 2026-09-29-fb/78) inside the Events hub, laid out from the pumpkin field of
// halloween_pumpkin_field.prefab (groupTwo; 696 wide, y down from the top edge): logo, the ten pumpkins (whole / cut with the
// reward on top), Pumpkin Dagger counter with "+", Cut / Claim and the round reward ("Pack Reward"). Rules: gxb2/pumpkin.py.
// Prefix pk-.
const PumpkinPatch=(()=>{
 let data=null,host=null,busy=false,fresh=-1;
 const A=n=>'/assets/pumpkin/'+n+(n==='halloween_cut_bg'?'.webp':'.png');
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 const btn=(cls,text,fn,dis=false)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;b.disabled=dis;return b;};
 const T=k=>data?.text?.[k]||'';
 function at(e,x,y,w,h){e.style.left=`calc(${348+x-w/2} * var(--u))`;e.style.top=`calc(${-y-h/2} * var(--u))`;e.style.width=`calc(${w} * var(--u))`;e.style.height=`calc(${h} * var(--u))`;return e;}
 function iconSrc(id){id=String(id);if(id==='1'||id==='2')return '/assets/currency/icon_'+id+'_small.png';if(id==='182')return A('icon_182');if(/^2000\d{4}$/.test(id))return '/assets/profile/head_'+Number(id.slice(4))+'.png';const it=itemCatalog?.[id];if(it&&typeof itemPicture==='function'){const p=itemPicture(it);if(p)return p;}return it&&itemIcons.has(it.icon)?'/assets/item-icons/'+it.icon+'.png':'';}
 function item(k,n,cls='pk-item'){const w=el('span',cls);const it=itemCatalog?.[k];w.style.backgroundImage=`url('/assets/ui/quality_${Math.min(it?.quality||1,7)}.png')`;const s=iconSrc(k);if(s)w.append(img(s));w.append(el('b','',n>=10000?number(Math.round(n/1000))+'K':number(n)));w.title=it?.name||(/^2000\d{4}$/.test(String(k))?'Avatar':k);return w;}
 const rows=text=>String(text).split('|').map(p=>p.split('#').map(Number));
 // pumpkinBtn1-10 of the prefab: [x, y, sprite, w, h]
 const P=[[-178,-350,1,314,254],[31,-393,2,192,188],[234,-343,2,192,188],[-208,-548,3,187,168],[-16,-564,3,187,168],[207,-515,3,187,168],[-261,-709,4,160,158],[-85,-750,4,160,158],[90,-707,4,160,158],[261,-679,4,160,158]];
 async function act(req){if(busy)return null;busy=true;try{const r=await api('/api/pumpkin/action',req);state=r.state;return r;}catch(e){GirlUI.toast(e.message);return null;}finally{busy=false;if(host?.isConnected)draw();}}
 async function render(parent){host=parent;if(!data)data=await api('/assets/pumpkin.json');draw();}
 function draw(){const s=state.pumpkin_info;if(!s||!host)return;host.querySelector('.pk-root')?.remove();const root=el('div','pk-root');const st=el('div','pk-stage');root.append(st);host.append(root);
  st.style.backgroundImage=`url('${A('halloween_cut_bg')}')`;
  st.append(at(img(A('halloween_name_en_en'),'pk-abs pk-logo'),10,-72,425,188));
  st.append(at(btn('pk-abs pk-help','',()=>CampaignUI.popup(T('ACTIVITY_HALLOWEEN_HELP').split('|').join('\n')+"\n\nLocal: 5 Pumpkin Daggers per day; Gem purchases have a daily limit.",{})),310,-37,52,52));
  st.append(at(el('p','pk-abs pk-hint',T('ACTIVITY_HALLOWEEN_TEXT2')+' · Round '+s.round),0,-218,600,40));
  s.awards.forEach((a,i)=>{const [x,y,kind,w,h]=P[i];const cut=a>0;const b=at(btn('pk-abs pk-pumpkin'+(cut?' cut':'')+(i===fresh?' fresh':'')+([2,5,7,9].includes(i)&&!cut?' flip':''),'',()=>odds(i)),x,y,w,h);
   b.append(img(A(cut?'halloween_pumpkin_cut':'halloween_pumpkin_'+kind)));if(cut){const [k,n]=rows(data.pumpkins[i].award)[a-1];const it=item(k,n,'pk-item on');b.append(it);}st.append(b);});fresh=-1;
  const res=at(el('div','pk-abs pk-res'),-255,-849,169,82);res.append(img(A('halloween_icon_outline_img'),'pk-res-icon'),el('b','',number(s.daggers)),btn('pk-add','',()=>buy(s)));st.append(res);
  if(s.left){const c=at(btn('pk-abs pk-cut','',()=>cut()),0,-816,252,96);const ic=el('span','pk-cost');ic.append(img(A('halloween_icon_outline_img')),el('small','','x1'));c.append(ic,el('b','',T('ACTIVITY_HALLOWEEN_USE')||'Cut'));st.append(c);}
  else{const c=at(btn('pk-abs pk-claim',T('ACTIVITY_HALLOWEEN_GET')||'Claim',async()=>{const r=await act({action:'claim'});if(r)GirlUI.toast('🎃 '+Object.entries(r.got).map(([k,n])=>number(n)+' '+(itemCatalog?.[k]?.name||k)).join(', '));}),0,-816,256,100);st.append(c);}
  const fin=at(el('div','pk-abs pk-final'),265,-773,163,202);const [fk,fn]=rows(s.final)[0];fin.append(item(fk,fn,'pk-item big'),el('small','',T('ACTIVITY_HALLOWEEN_AWARD')||'Pack Reward'),btn('pk-look','🔍',()=>rounds(s)));st.append(fin);}
 async function cut(){const s=state.pumpkin_info;if(s.daggers<1){GirlUI.toast('Not enough Pumpkin Dagger');return;}const r=await act({action:'cut'});if(!r)return;fresh=r.pumpkin;draw();
  const [k,n]=Object.entries(r.got)[0];GirlUI.toast('+'+number(n)+' '+(itemCatalog?.[k]?.name||k));}
 function odds(i){const row=data.pumpkins[i];const w=String(row.weight).split('|').map(Number),tot=w.reduce((a,b)=>a+b,0);const {body}=GirlUI.win({title:'Pumpkin',cls:'pk-win'});body.append(el('p','pk-note',T('ACTIVITY_HALLOWEEN_TEXT4')));
  const g=el('div','pk-grid');rows(row.award).forEach(([k,n],j)=>{const c=el('div','pk-odd');c.append(item(k,n),el('small','',(w[j]/tot*100).toFixed(1)+'%'));g.append(c);});body.append(g);}
 function rounds(s){const {body}=GirlUI.win({title:T('ACTIVITY_HALLOWEEN_AWARD')||'Pack Reward',cls:'pk-win'});const g=el('div','pk-grid');
  data.rounds.forEach((r,i)=>{const [k,n]=rows(r.award)[0];const c=el('div','pk-odd'+(i+1<s.round?' done':i+1===s.round?' now':''));c.append(item(k,n),el('small','',(i+1===data.rounds.length?'Round '+(i+1)+'+':'Round '+(i+1))));g.append(c);});body.append(g);}
 function buy(s){const left=s.limit-s.buy;if(left<=0){GirlUI.toast("Daily limit reached");return;}const n=Number(prompt("Pumpkin Daggers (150 Gems each, remaining: "+left+' hoy)','1'))||0;if(n>0)act({action:'buy',num:Math.min(n,left)});}
 return {render};
})();
