'use strict';
const ImgGuides=(()=>{
 let data;
 const titles={tavern_window:'Internship',prophet_window:'Enrollment',gamble_window:'High Stakes',tower_window:'Tests',daily_mission_window:'Daily Missions',arena_window:'Đấu Trường',shenxue_window:'Graduate',treasure_guide:'Crystal',friend_boss_guide:'Boss Bạn Bè',dates_window:'Dates',beach_window:'Beach',hero_challenge_detail_guide:'Hero Challenge',music_game_window:'Music Game',jump_game_window:'Jump Game'};
 const el=(t,c,txt)=>{const e=document.createElement(t);e.className=c||'';if(txt!==undefined)e.textContent=txt;return e;};
 const load=async()=>data||(data=await api('/assets/img-guides/catalog.json'));
 function rich(e,text){let color='',bold=false;for(const t of String(text).replace(/\[\/?c\]/g,'').split(/(\[[0-9a-fA-F]{6}\]|\[-\]|\[b\]|\[\/b\])/)){if(/^\[[0-9a-fA-F]{6}\]$/.test(t)){color='#'+t.slice(1,-1);continue;}if(t==='[-]'){color='';continue;}if(t==='[b]'){bold=true;continue;}if(t==='[/b]'){bold=false;continue;}const s=el('span','',t);if(color)s.style.color=color;if(bold)s.style.fontWeight='900';e.append(s);}}
 async function open(key,start=0){await load();if(!data.guides[key])return;let page=Math.min(Math.max(0,start),data.guides[key].pages.length-1);const {body}=GirlUI.win({title:titles[key]||data.guides[key].name,cls:'ig-window'});body.closest('.ig-window')?.setAttribute('data-guide',key);const draw=()=>{body.replaceChildren();const guide=data.guides[key],p=guide.pages[page];const nav=el('div','ig-nav');for(const [text,delta] of [['‹',-1],['›',1]]){const b=el('button','gs-btn',text);b.type='button';b.disabled=page+delta<0||page+delta>=guide.pages.length;b.onclick=()=>{page+=delta;draw();};nav.append(b);}nav.insertBefore(el('b','',`${page+1} / ${guide.pages.length}`),nav.lastChild);body.append(nav);const poster=el('div','ig-poster'+(p.layout?' ig-flow':''));poster.style.backgroundImage=`url('${p.background}')`;for(const n of p.nodes){const e=el(n.src?'img':'div',n.src?'ig-image':'ig-label');if(!n.src&&/^\d+ \/$/.test(n.text||''))e.classList.add('ig-num');if(n.src){e.src=n.src;e.alt="Illustration of "+(titles[key]||key);e.draggable=false;}else rich(e,n.text);if(!n.flow){Object.assign(e.style,{left:n.x/p.width*100+'%',top:n.y/p.height*100+'%',width:n.w/p.width*100+'%',height:n.h/p.height*100+'%',zIndex:n.z,fontSize:`calc(${n.font||20} * var(--ig-u))`});}poster.append(e);
      // The original guide artwork contains the English words Daily and
      // Seasonal *inside the image*. Hide only those labels with native-style
      // overlays while preserving the original badges, icons and illustrations.
      if(key==='arena_window'&&page===1&&n.src){
       const labels={
         'img_guide_arena_icon6_en_en.png':['Hằng Ngày','daily'],
         'img_guide_arena_icon7_en_en.png':['Theo Mùa','season']
       };
       const tag=Object.keys(labels).find(k=>n.src.endsWith(k));
       if(tag){
        const overlay=el('strong','ig-arena-native-label '+labels[tag][1],labels[tag][0]);
        Object.assign(overlay.style,{
          left:((n.x+n.w*.48)/p.width*100)+'%',
          top:((n.y+n.h*.32)/p.height*100)+'%',
          width:(n.w*.48/p.width*100)+'%',
          height:(n.h*.44/p.height*100)+'%',
          zIndex:String((n.z||0)+3)
        });
        poster.append(overlay);
       }
      }
    }body.append(poster);if(p.layout)body.append(el('p','ig-note',"Recovered original images and text; adapted layout."));};draw();}
 // Bind the actual question-mark control; do not create a second header button.
 const targets={internship:['.in-help','tavern_window'],enroll:['.en-help','prophet_window'],slots:["button[title=\"Help\"]",'gamble_window'],arena:['.ar-icon-btn:has(img[src$="help_2.png"])','arena_window'],dates:['.dt-help','dates_window'],tower:['#tower-help','tower_window']};
 function decorate(v){const target=targets[v],r=document.getElementById(v+'-view');if(!target||!r)return;r.querySelectorAll('.ig-help').forEach(b=>b.remove());const b=r.querySelector(target[0]);if(b&&!b.dataset.imgGuide){b.dataset.imgGuide=target[1];b.setAttribute('aria-label',"Hướng dẫn");b.onclick=()=>open(target[1]);}}
 let queued=false;new MutationObserver(()=>{if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;decorate(view);});}).observe(document.getElementById('app-frame'),{childList:true,subtree:true});
 return {open,decorate};
})();
