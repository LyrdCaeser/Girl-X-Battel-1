'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const code=fs.readFileSync('web/summon-anim.js','utf8');
const fn=code.slice(code.indexOf('function revealStarsOneByOne('),code.indexOf(' function caption('));
const scheduled=[],sprites=[];
const PIXI={
 Graphics:class {beginFill(){return this}drawRoundedRect(){return this}endFill(){return this}},
 Text:class{constructor(text){this.text=text;this.width=100;this.scale={x:1,y:1};this.anchor={set(){}};this.position={set(){}}}},
 Texture:{EMPTY:{}},
 Sprite:{from(src){const s={src,scale:{x:1,y:-1,set(x,y){this.x=x;this.y=y}},position:{set(x,y){this.x=x;this.y=y}},anchor:{set(){}},alpha:1,visible:true};sprites.push(s);return s}}
};
const ctx=vm.createContext({PIXI,performance:{now:()=>1200},setTimeout(fn,ms){scheduled.push([ms,fn]);return 1},requestAnimationFrame:fn=>fn(1460)});
vm.runInContext(fn,ctx);
const render=vm.runInContext('nativeNameStars',ctx);
function fig(){
 const slots=['name','1xing','2xing','3xing','4xing','5xing'].map(()=>({children:[],addChild(o){this.children.push(o)}}));
 return {slotContainers:slots,skeleton:{findSlotIndex(n){return ['name','1xing','2xing','3xing','4xing','5xing'].indexOf(n)}},
 hackTextureBySlotName(){}};
}
for(const n of [1,2,3,4,5,6,9,10,15,25]){
 sprites.length=0;scheduled.length=0;const f=fig();
 assert(render(f,{name:'Samurai'},n));
 const icons=f.slotContainers[0].children.filter(o=>o.src);
 assert.equal(icons.length,n>=10?1:n>=6?n-5:n);
 assert(icons.every(o=>o.position.y===78),'Stars must be above CV and name plaque');
 assert(icons.every(o=>o.visible===false));
 const starTimers=scheduled.filter(([ms])=>ms>=1000);
 assert(starTimers.some(([ms])=>ms===1000));
 if(n<=9)assert(starTimers.some(([ms])=>ms===1000+(icons.length-1)*180));
 starTimers.forEach(([ms,fn])=>fn());
 assert(icons.every(o=>o.visible===true&&o.alpha===1),'Each star animates into place');
}
assert(fs.readFileSync('web/index.html','utf8').includes('/summon-anim.js?v=20261118-s4-wish-skins-r2'));
console.log('PASS: 1-25★ above CV, staggered original asset sprites, responsive scale animation');
