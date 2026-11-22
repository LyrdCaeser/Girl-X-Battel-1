'use strict';
const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
const source=fs.readFileSync('web/sonia-battle-vfx.js','utf8');
const animation=fs.readFileSync('web/battle-animation.js','utf8');
const app=fs.readFileSync('web/app.js','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const calls={frames:0,draws:0,removed:0};
let next=1,rafs=new Map();
const gradient={addColorStop(){}};
const drawing={
 createRadialGradient(){return gradient;},
 setTransform(){},clearRect(){calls.frames++},save(){},restore(){},
 beginPath(){calls.draws++},moveTo(){},lineTo(){},ellipse(){},stroke(){},
 arc(){},fill(){},bezierCurveTo(){},quadraticCurveTo(){},
 translate(){},rotate(){},scale(){},drawImage(){calls.draws++},
 fillRect(){},fillText(){}
};
const ctx=vm.createContext({
 console,Math,Number,Set,Object,Map,Array,Image:class{constructor(){this.complete=false;this.naturalWidth=0;}},
 performance:{now:()=>100},
 document:{createElement(name){
  assert.equal(name,'canvas');
  return {width:0,height:0,style:{},className:'',
   getContext:()=>drawing,remove(){calls.removed++}};
 }},
 requestAnimationFrame(fn){const id=next++;rafs.set(id,fn);return id;},
 cancelAnimationFrame(id){rafs.delete(id);}
});
vm.runInContext(source+';globalThis.VFX=SoniaBattleVFX;',ctx);
const vfx=ctx.VFX;
assert.deepEqual(Object.keys(vfx.SKILLS).map(Number),[75800100,75800101,75800102,75800103,75800104]);
const field={append(node){this.node=node;}};
const units=[{pos:1,table_id:758001},{pos:7,table_id:51017},{pos:8,table_id:51018}];
const xy={1:[270,600],7:[800,700],8:[840,1000]};
const engine=vfx.mount(field,units,xy);
assert.equal(field.node.width,540,'half-resolution Android-safe drawing surface');
assert.equal(field.node.height,960);
assert.equal(engine.skillCount,1);
assert.equal(engine.timing(75800101,1).impact,1350);
assert.equal(engine.timing(75800104,1).duration,2750);
assert.equal(engine.timing(75800101,7),null,'enemy or non-Sonia caster cannot call Sonia FX');
assert.equal(engine.timing(1110101,1),null);
assert.equal(engine.play(75800101,7,[1]),null);
const effects=[75800101,75800102,75800103,75800104];
for(const id of effects){
 const data=engine.play(id,1,[7,8]);
 assert(data&&data.duration>0,'every original skill gets a visible clip');
 assert(rafs.size>0,'rAF is scheduled');
 let t=100;
 for(let j=0;j<5;j++){
  const callbacks=[...rafs.values()];rafs.clear();t+=120;
  for(const cb of callbacks)cb(t);
 }
}
assert(calls.draws>250,'VFX must draw actual pixels, got '+calls.draws);
assert(calls.frames>=4);
engine.speed(2);engine.speed(4);engine.speed(1);
engine.destroy();
assert.equal(calls.removed,1);
assert.equal(rafs.size,0);
assert(animation.includes('soniaFx?.play(skillId,caster,targets)'));
assert(animation.includes('soniaFx?.destroy()'));
assert(animation.includes('soniaFx?.guard()'));
assert(animation.includes('soniaFx?.speed(value)'));
assert(app.includes('const soniaTiming=frame.skill_id>0?battleAnimation?.timing?'));
assert(app.includes('soniaTiming.impact/battleSpeed'));
assert(html.includes('sonia-battle-vfx.js?v=20261122-4skills-r1'));
assert(html.indexOf('/sonia-battle-vfx.js')<html.indexOf('/battle-animation.js'));
assert(html.includes('wish.js?v=20261122-sonia-pity-985-r6'));
console.log('PASS: 4 VFX cues draw real frames, no other girls affected, 0.5x backing canvas, speed/skip/destroy, timed damage');
