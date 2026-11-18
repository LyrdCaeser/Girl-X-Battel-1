'use strict';
// Isolated DOM-style tests for S4 cinematic skin phase; never calls the server.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('web/home-menus.js','utf8');
const fn=source.slice(source.indexOf(' function revealS4Skins(prize){'),source.indexOf(' async function revealS4Bundle(prize){')).trim();
assert(fn.startsWith('function revealS4Skins('));
function E(tag='',text,cls){
 this.tag=tag;this.textContent=text??'';this.className=cls||'';this.children=[];this.style={};this.removed=false;
 const classes=new Set((cls||'').split(/\s+/).filter(Boolean));
 this.classList={add:k=>classes.add(k),remove:k=>classes.delete(k),contains:k=>classes.has(k)};
 this.append=(...elements)=>this.children.push(...elements);
 this.replaceChildren=(...elements)=>{this.children=[...elements];};
 this.remove=()=>{this.removed=true;};
 this.focus=()=>{};
 this.querySelector=()=>null;
}
const root=new E('root');
const context={
 el:(tag,text,cls)=>new E(tag,text,cls),
 window:{GxbFrame:{root:()=>root},GxbBagVi:{t:text=>text==='Sunbath'?'Tắm Nắng':text}},
 document:{body:root},
 state:{server_id:'S4'},
 Number,Map,Promise
};
const reveal=vm.runInNewContext('('+fn+')',context);
const prize={
 wish_count:24,skin_count:76,outfit_total:242,
 skin_ids:Array.from({length:76},(_,i)=>7001+i),
 skin_details:Array.from({length:76},(_,i)=>({id:7001+i,name:i===0?'Sunbath':'Limited '+i}))
};
(async()=>{
 let done=false;const pending=reveal(prize).then(()=>done=true);
 const overlay=root.children.at(-1);
 assert.equal(overlay.className,'hm-s4-wish-overlay');
 const [head,body,foot]=overlay.children;
 const [portal,instruction]=body.children;
 const [flare,cards]=portal.children;
 const [next,overview,skip]=foot.children;
 assert.equal(cards.children.length,6);
 assert.equal(cards.children[0].children[0].children[0].src,'/assets/skins/cards/7001.webp');
 assert.equal(cards.children[0].children[1].children[0].textContent,'Tắm Nắng');
 assert(head.children[1].textContent.includes('6 / 76'));
 assert(instruction.textContent.includes('6 / 76'));
 assert(!done);
 for(let page=1;page<13;page++)next.onclick();
 assert.equal(cards.children.length,4,'Final Wish batch contains 4 skins');
 next.onclick();
 assert.equal(cards.children.length,76,'Last step shows all awarded skins');
 assert(cards.classList.contains('all'));
 assert(head.children[1].textContent.includes('76 / 76'));
 assert(instruction.textContent.includes('242'));
 next.onclick();
 await pending;
 assert(overlay.removed&&done);

 let skipResolved=false;const second=reveal(prize).then(()=>skipResolved=true);
 const secondOverlay=root.children.at(-1);
 const next2=secondOverlay.children[2].children[0];
 const skip2=secondOverlay.children[2].children[2];
 skip2.onclick();
 const grid2=secondOverlay.children[1].children[0].children[1];
 assert.equal(grid2.children.length,76,'Skipping animation must still show all owned skins');
 next2.onclick();await second;
 assert(skipResolved);
 // Never show this exclusive cinematic on S1/S2/S3.
 context.state.server_id='S2';
 const previous=root.children.length;
 await reveal(prize);
 assert.equal(root.children.length,previous);
 const css=fs.readFileSync('web/home-menus.css','utf8');
 assert(css.includes('summon_scene.png'));
 assert(css.includes('.hm-s4-wish-cards.all'));
 assert(css.includes('hm-s4-wish-skin-arrive'));
 assert(css.includes('@media(prefers-reduced-motion:reduce)'));
 const html=fs.readFileSync('web/index.html','utf8');
 assert(html.includes('home-menus.js?v=20261118-s4-skin-wish-r2'));
 assert(html.includes('home-menus.css?v=20261118-s4-skin-wish-r2'));
 console.log('PASS: 76 actual skin artwork, grouped Wish batches, full gallery, skip, S4-only');
})().catch(err=>{console.error(err);process.exitCode=1;});
