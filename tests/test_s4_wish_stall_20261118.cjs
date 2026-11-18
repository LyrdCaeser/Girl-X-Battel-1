'use strict';
// Test the problematic async Spine completion and per-portrait fail-safe
// independently from the PIXI runtime (no production APIs invoked).
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('web/summon-anim.js','utf8');
const fragment=source.slice(source.indexOf(' function run(fig,name,loop=false){'),
                             source.indexOf(' async function layer(base,scale=1,oy=.5){'));
assert(fragment.includes('clearTimeout(timer)'));
assert(fragment.includes('clearInterval(skipPoll)'));
assert(fragment.includes('entry.listener=null'));
const pendingTimers=new Map(),pendingIntervals=new Map();
let serial=0;
const scope=vm.createContext({
 skipped:false,
 setTimeout(cb,ms){const id=++serial;pendingTimers.set(id,{cb,ms});return id;},
 setInterval(cb,ms){const id=++serial;pendingIntervals.set(id,{cb,ms});return id;},
 clearTimeout(id){pendingTimers.delete(id);},
 clearInterval(id){pendingIntervals.delete(id);}
});
vm.runInContext(fragment,scope);
const run=vm.runInContext('run',scope);
function fig(){
 const entry={listener:null};
 return {entry,spineData:{findAnimation(n){return n==='texiao10'?{duration:3.1}:null;}},
  state:{setAnimation(){return entry;}}};
}
(async()=>{
 const f=fig(),completed=run(f,'texiao10');
 assert.equal(pendingTimers.size,1);
 assert([...pendingTimers.values()].some(x=>x.ms===4500));
 assert.equal(pendingIntervals.size,1);
 f.entry.listener.complete();
 await completed;
 assert.equal(pendingTimers.size,0);
 assert.equal(pendingIntervals.size,0);
 assert.equal(f.entry.listener,null);

 const frozen=fig(),held=run(frozen,'texiao10');
 assert.equal(pendingTimers.size,1);
 [...pendingTimers.values()][0].cb();
 await held;
 assert.equal(pendingTimers.size,0);
 assert.equal(pendingIntervals.size,0);

 const skip=fig(),abort=run(skip,'texiao10');
 vm.runInContext('skipped=true',scope);
 [...pendingIntervals.values()][0].cb();
 await abort;
 assert.equal(pendingTimers.size,0);
 assert.equal(pendingIntervals.size,0);

 assert(source.includes("resolution:s4Sequence?1:null"));
 assert(source.includes('s4Sequence?3600:9000'));
 assert(source.includes('expired=true'));
 assert(source.includes("for(let i=0;i<partners.length&&!skipped;i++){"));
 assert(source.includes("catch(e){console.warn('Wish bỏ qua lượt hiển thị lỗi:'"));
 assert(source.includes('finally{uncap();e.done();}'));
 assert(source.includes('finally{m.done();}'));
 assert(source.includes('finally{overlay?.remove();overlay=null;s4Sequence=false;}'));
 const home=fs.readFileSync('web/home-menus.js','utf8');
 assert(home.includes('await SummonAnim.play(26,girls,{s4:true})'));
 const html=fs.readFileSync('web/index.html','utf8');
 assert(html.includes('/summon-anim.js?v=20261118-s4-wish-skins-r2'));
 assert(html.includes('/home-menus.js?v=20261118-s4-skin-wish-r2'));

 // A 25-star result in S4 can pause at tapOrSkip: automatically continue
 // after 3 seconds instead of silently waiting for an invisible tap.
 const tapSource=source.slice(source.indexOf(' function tapOrSkip(){'),source.indexOf(' function swipe(){'));
 const tapTimers=[],tapIntervals=[];
 let touch={hidden:true,onclick:null},hint={hidden:true,textContent:'',onclick:null};
 const tapCtx=vm.createContext({
  overlay:{querySelector:name=>name==='.sa-touch'?touch:hint},
  skipped:false,s4Sequence:true,
  setTimeout(fn,ms){tapTimers.push({fn,ms});return 1;},
  setInterval(fn,ms){tapIntervals.push({fn,ms});return 2;},
  clearTimeout(){},clearInterval(){}
 });
 vm.runInContext(tapSource,tapCtx);
 const tap=vm.runInContext('tapOrSkip',tapCtx);
 const p=tap();
 assert.equal(tapTimers.at(-1).ms,3000);
 assert.equal(hint.hidden,false);
 assert(hint.textContent.includes('Tự chuyển'));
 tapTimers.at(-1).fn();
 await p;
 assert.equal(touch.hidden,true);
 assert.equal(hint.hidden,true);
 assert.equal(touch.onclick,null);
 tapCtx.s4Sequence=false;
 const numTimers=tapTimers.length;
 const ordinary=tap();
 assert.equal(tapTimers.length,numTimers,'Other worlds must retain original manual tap');
 touch.onclick();await ordinary;

 console.log('PASS: 25-star frames bounded, S4 auto-advance 3s, skip, GPU budget, original standard behavior');
})().catch(e=>{console.error(e);process.exitCode=1;});
