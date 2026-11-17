'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const code=fs.readFileSync('web/summon-anim.js','utf8');
const fn=code.slice(code.indexOf('function nativeNameStars('),code.indexOf(' function caption(',code.indexOf('function nativeNameStars('))).trim();
class Text{
 constructor(text,style){this.text=text;this.style=style;this.scale={x:1,y:1};this.width=text.length*14;this.anchor={set(x){this.value=x}};}
}
const srcs=[];
const PIXI={Text,Texture:{EMPTY:{}},Sprite:{from(src){srcs.push(src);return {src,anchor:{set(x){this.value=x}},scale:{set(x,y){this.x=x;this.y=y}}}}}};
const nativeNameStars=vm.runInNewContext('('+fn+')',{PIXI});
function mock(){
 const names=['name','zhiye','cv','1xing','2xing','3xing','4xing','5xing','xing6','xing7','xing8','xing9','xing10','xing11','xing12','xing13','xing14','3xing2','3xing3','3xing4','xing14'];
 const slots=names.map(()=>({children:[],addChild(x){this.children.push(x)}}));
 const hidden=[];return {slots,hidden,skeleton:{findSlotIndex(n){return names.indexOf(n)}},slotContainers:slots,hackTextureBySlotName(n){hidden.push(n)}};
}
for(const stars of [1,3,5,6,9,10,15,25]){
 const fig=mock();
 assert.equal(nativeNameStars(fig,{name:'King'},stars),true);
 assert.equal(fig.slots[0].children[0].text,'King');
 assert.equal(fig.slots[0].children[0].scale.y,-1);
 assert(!fig.hidden.includes('name'),'Original nameplate must remain visible');
 const starCount=fig.slots.slice(3,8).flatMap(x=>x.children).filter(x=>x.src).length;
 assert.equal(starCount,stars>=10?1:stars>5?stars-5:stars);
 if(stars>=10) assert(fig.slots.slice(3,8).some(x=>x.children.some(c=>c.text===String(stars))));
}
assert(srcs.every(x=>x.startsWith('/assets/girl-ui/')));
console.log('PASS: native nameplate and star slots for 1/3/5/6/9/10/15/25★, no new art');
