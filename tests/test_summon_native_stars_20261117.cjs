'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const code=fs.readFileSync('web/summon-anim.js','utf8');
const fn=code.slice(code.indexOf('function nativeNameStars('),code.indexOf(' function caption(',code.indexOf('function nativeNameStars('))).trim();
class Graphics{
 beginFill(color,alpha){this.color=color;this.alpha=alpha;return this}
 drawRoundedRect(x,y,w,h,r){this.width=w;this.height=h;return this}
 endFill(){return this}
}
class Text{
 constructor(text,style){this.text=text;this.style=style;this.scale={x:1,y:1};this.width=text.length*14;
 this.anchor={set(x){this.value=x}};this.position={set(x,y){this.x=x;this.y=y}};}
}
const srcs=[];
const PIXI={Graphics,Text,Texture:{EMPTY:{}},Sprite:{from(src){srcs.push(src);return {
 src,anchor:{set(x){this.value=x}},position:{set(x,y){this.x=x;this.y=y}},
 scale:{set(x,y){this.x=x;this.y=y}}}}}};
const nativeNameStars=vm.runInNewContext('('+fn+')',{PIXI,revealStarsOneByOne:()=>{},setTimeout:()=>{}});
function mock(){
 const names=['name','zhiye','cv','1xing','2xing','3xing','4xing','5xing','xing6','xing7','xing8','xing9','xing10','xing11','xing12','xing13','xing14','3xing2','3xing3','3xing4'];
 const slots=names.map(()=>({children:[],addChild(x){this.children.push(x)}}));
 const hidden=[];return {slots,hidden,skeleton:{findSlotIndex(n){return names.indexOf(n)}},slotContainers:slots,hackTextureBySlotName(n){hidden.push(n)}};
}
for(const stars of [1,3,5,6,9,10,15,25]){
 const fig=mock();
 assert.equal(nativeNameStars(fig,{name:'King'},stars),true);
 assert(fig.slots[0].children[0] instanceof Graphics,'Native name plaque obscures the embedded Chinese text');
 assert.equal(fig.slots[0].children[0].alpha,.98);
 assert.equal(fig.slots[0].children[1].text,'King');
 assert.equal(fig.slots[0].children[1].scale.y,-1);
 assert(!fig.hidden.includes('name'),'Animated nameplate attachment is preserved');
 const icons=fig.slots[0].children.filter(x=>x.src);
 const count=stars>=10?1:stars>5?stars-5:stars;
 assert.equal(icons.length,count);
 assert(icons.every(x=>x.position.y===78));
 for(let s=3;s<=7;s++)assert.equal(fig.slots[s].children.length,0,'Never attach stars to a hidden animation slot');
 if(stars>=10)assert(fig.slots[0].children.some(x=>x.text===String(stars)));
}
assert(srcs.every(x=>x.startsWith('/assets/girl-ui/')));
assert(code.includes("await wait(900);if(!skipped)await tapOrSkip();"),'5-star display must remain visible');
assert(code.includes("await wait(900);\n   }finally{uncap();e.done();}"),'3-4 star display held long enough to read');
assert(fs.readFileSync('web/index.html','utf8').includes('/summon-anim.js?v=20261119-goddess-wish-manual-r2'));
console.log('PASS: original native plaque with no Chinese text, visible 1–25★, slower reveal, no new assets');
