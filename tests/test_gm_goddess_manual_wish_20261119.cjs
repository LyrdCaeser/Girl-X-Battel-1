'use strict';
// No live profile or mail mutation: verified GM-gift cinematic behavior only.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const home=fs.readFileSync('web/home-menus.js','utf8');
const src=fs.readFileSync('web/summon-anim.js','utf8');
const css=fs.readFileSync('web/summon-anim.css','utf8');
const html=fs.readFileSync('web/index.html','utf8');
assert(home.includes('goddessWish=result?.goddess||null'),
  'Only the confirmed mail-claim goddess can open GM Wish');
assert(home.includes('if(goddessWish)await revealGmGoddessWish(goddessWish)'),
  'Open the Wish only after backend transaction committed');
assert(home.includes('await SummonAnim.playS4Rewards([hero],[],{manual:true,goddessGift:true})'),
  'GM Goddess reuses native Wish without any time-based advance');
assert(home.includes('▶ Xem Lại Triệu Hồi Wish (Không Nhận Quà Lần Nữa)'),
  'Claimed mail can replay without receiving a duplicate heroine');
assert(src.includes("manualWish=options.manual===true"),
  'Manual mode must not change S4 movie behavior');
assert(src.includes('if(!manualWish)timer=setTimeout(finish,ms)'),
  'No automatic advance on GM Wish');
assert(css.includes('.sa-gm-goddess-wish .sa-s4-progress{display:none!important}'), 'GM Wish progress badge must stay hidden');
assert(html.includes('summon-anim.css?v=20261119-gm-wish-no-counter-r3'));
assert(css.includes('.sa-gm-goddess-wish .sa-hint'),
  'Visible touch-to-complete button for both PC and mobile');
assert(html.includes('summon-anim.js?v=20261123-faction-reveal-r6'));
assert(html.includes('home-menus.js?v=20261119-goddess-wish-manual-r2'));
const section=src.slice(src.indexOf(' function s4Pause(ms){'),
                        src.indexOf(' async function s4RevealSequence('));
assert(section.startsWith(' function s4Pause'));
let timers=[],intervals=[];
const touch={hidden:true,onclick:null};
const hint={hidden:true,onclick:null,textContent:''};
const context=vm.createContext({
 skipped:false,manualWish:true,
 overlay:{querySelector(sel){return sel==='.sa-touch'?touch:hint;}},
 setTimeout(fn,ms){timers.push({fn,ms});return timers.length;},
 clearTimeout(){},
 setInterval(fn){intervals.push(fn);return intervals.length;},
 clearInterval(){}
});
vm.runInContext(section,context);
const pause=vm.runInContext('s4Pause',context);
(async()=>{
 const manual=pause(900);
 assert.equal(timers.length,0,'GM Wish must wait forever for player tap');
 assert.equal(hint.hidden,false);
 assert.match(hint.textContent,/Chạm/);
 touch.onclick();await manual;
 assert.equal(touch.hidden,true);
 assert.equal(hint.hidden,true);
 context.manualWish=false;
 const ordinary=pause(900);
 assert.equal(timers.length,1,'Default S4 Wish remains timed for 48 goddess rewards');
 timers[0].fn();await ordinary;
 assert.equal(touch.hidden,true);
 console.log('PASS GM Goddess Wish: no auto-advance, manual tap, replay without new claim, S4 timer preserved');
})().catch(err=>{console.error(err);process.exitCode=1});
