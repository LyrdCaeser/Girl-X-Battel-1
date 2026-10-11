'use strict';
// Summon result window (summon_result_window.prefab; user capture 2026-09-29): after the capsule animation — or Skip —
// the girls drawn appear as HeroIcons (avatar, hero_frame, faction badge, stars) on the glowing `summon_res` band, with
// OK and the "draw again" buttons of the same capsule (scroll / gems). Prefix sr-.
const SummonResult=(()=>{
 const A=n=>'/assets/summon-result/'+n+'.png';
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const img=(src,cls)=>{const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;};
 // summon id drawn → the buttons offered again: [summon id, cost item, cost, draws]
 const AGAIN={1:[[1,'33',1,1],[2,'33',10,10]],2:[[1,'33',1,1],[2,'33',10,10]],3:[[1,'33',1,1],[2,'33',10,10]],
  4:[[7,'36',10,10],[5,'2',2200,10]],5:[[7,'36',10,10],[5,'2',2200,10]],6:[[7,'36',10,10],[5,'2',2200,10]],7:[[7,'36',10,10],[5,'2',2200,10]],8:[[7,'36',10,10],[5,'2',2200,10]],
  15:[[15,'11',10,1],[16,'11',100,10]],16:[[15,'11',10,1],[16,'11',100,10]],
  22:[[25,'36',10,10],[23,'2',2200,10]],23:[[25,'36',10,10],[23,'2',2200,10]],24:[[25,'36',10,10],[23,'2',2200,10]],25:[[25,'36',10,10],[23,'2',2200,10]],26:[[25,'36',10,10],[23,'2',2200,10]]};
 const costIcon=id=>id==='2'?'/assets/currency/icon_2_small.png':id==='11'?'/assets/capsule/summon_record_friendship_icon.png':'/assets/currency/icon_'+id+'.png';
 function heroIcon(p){const g=girlsCatalog.find(x=>x.id===Number(p.table_id));const star=Number(p.star)||avatars[String(p.table_id)]?.stars||g?.stars||1;const w=el('div','sr-hero'+(star>=5?' five':''));
  const av=img(girlIconSource(p.table_id)||'/assets/ui/item_bg.png','sr-av');
  w.append(av,img(A(star>=10?'hero_frame2':'hero_frame'),'sr-frame l'),img(A(star>=10?'hero_frame2':'hero_frame'),'sr-frame r'));
  const group=g?.group||avatars[String(p.table_id)]?.group;if(group){const b=el('span','sr-group');b.append(img(A('img_group'+group)));w.append(b);}
  const stars=el('span','sr-stars'+(star>5?' red':''));if(star>5)stars.textContent=star+'★';else for(let i=0;i<star;i++)stars.append(img(A('star')));stars.setAttribute('aria-label',star+" stars");w.append(stars);
  if(typeof HeroGlow!=='undefined')HeroGlow.attach(w,star,group,{frames:false});w.title=g?.name||p.name||'';return w;}
 // partners: [{table_id, star, name}]; again(summonId) runs another draw. Resolves when the window closes.
 function show(summonId,partners,again){document.querySelector('.sr-overlay')?.remove();if(!partners?.length)return Promise.resolve();
  return new Promise(res=>{const o=el('div','sr-overlay');const band=el('div','sr-band');const grid=el('div','sr-grid'+(partners.length<=5?' one':''));
   partners.forEach((p,i)=>{const h=heroIcon(p);h.style.animationDelay=(i*60)+'ms';grid.append(h);});band.append(grid);
   const btns=el('div','sr-buttons');const close=()=>{o.remove();res();};
   const ok=el('button','sr-btn','OK');ok.type='button';ok.onclick=close;btns.append(ok);
   for(const [sid,item,cost,n] of AGAIN[summonId]||[]){const b=el('button','sr-btn draw');b.type='button';const c=el('span','sr-cost');c.append(img(costIcon(item)),el('small','',number(cost)));b.append(c,el('span','','Draw '+n));
    const have=Number(state.items?.[item]||0);b.disabled=have<cost;b.onclick=()=>{close();again(sid);};btns.append(b);}
   o.append(band,btns);(window.GxbFrame?.root()||document.body).append(o);});}
 return {show,heroIcon};
})();
