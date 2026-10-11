'use strict';
// Story Items (CollectionStoryWindow / CollectionStoryDetailWindow; captures 2026-09-29-fb/35, 103-105): the three
// collection "story" antiques (collection type 7: items 94, 95, 175). The list shows each icon (grey until owned); the
// detail shows the icon_<id>_big art, name, lore, the Yume Collection coins it grants and ‹ › to browse. Prefix si-.
const StoryItems=(()=>{
 let origin='girls',list=null,idx=-1;
 const A=n=>'/assets/story-items/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';return i;};
 const btn=(cls,text,fn)=>{const b=el('button',cls,text);b.type='button';b.onclick=fn;return b;};
 const got=id=>Number(state.items?.[String(id)]||0)>0;
 function root(){let r=$('story-items-view');if(!r){r=el('section','story-items-view');r.id='story-items-view';r.hidden=true;$('home-systems-view').after(r);}return r;}
 async function open(from){origin=from||view;if(!list)list=await api('/assets/story-items/catalog.json');idx=-1;root();showView('story-items');render();}
 function render(){const r=root();if(view!=='story-items'||!list)return;r.replaceChildren();
  const top=el('div','si-top');const back=btn('si-back','',()=>{if(idx>=0){idx=-1;render();}else showView(origin==='story-items'?'girls':origin);});back.append(img('/assets/ui/win_back_btn.png'));top.append(back);r.append(top);
  if(idx<0){const box=el('div','si-box');box.append(el('h2','si-title','Story Items'));const g=el('div','si-grid');list.forEach((it,i)=>{const c=btn('si-cell'+(got(it.id)?'':' locked'),'',()=>{idx=i;render();});c.append(img(A('icon_'+it.id)),el('small','',it.name));g.append(c);});for(let k=list.length;k<12;k++)g.append(el('span','si-cell empty'));box.append(g);r.append(box);return;}
  const it=list[idx];const d=el('div','si-detail');d.append(img(A('icon_'+it.id+'_big'),'si-big'));
  d.append(btn('si-arrow l','‹',()=>{idx=(idx+list.length-1)%list.length;render();}),btn('si-arrow r','›',()=>{idx=(idx+1)%list.length;render();}));
  const card=el('div','si-card');const head=el('div','si-head');head.append(el('span','si-coin',String(it.coin)),el('b','',it.name),img(A(got(it.id)?'collection_got_en_en':'collection_no_get_en_en'),'si-got'));card.append(head,el('p','si-desc',it.desc));d.append(card);r.append(d);}
 document.addEventListener('DOMContentLoaded',()=>{const intro=document.querySelector('#girls-gallery-panel .gallery-intro');if(intro&&!$('si-open')){const b=el('button','secondary','Story Items');b.id='si-open';b.type='button';b.onclick=()=>open('girls');intro.append(' ',b);}});
 return {open,render};
})();
