'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const code=fs.readFileSync('web/summon-anim.js','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const begin=code.indexOf(' function nativeNameStars(');
const end=code.indexOf(' function caption(',begin);
const nativeCode=code.slice(begin,end);
assert(begin>0&&end>begin);
class Graphics{
 beginFill(){return this}drawRoundedRect(){return this}endFill(){return this}
}
class Text{
 constructor(text){this.text=text;this.width=text.length*14;this.scale={x:1,y:1};this.anchor={set(){}};this.position={set(){}};}
}
class Sprite{
 constructor(texture){this.texture=texture;this.src=texture?.src;this.scale={x:1,y:1,set(x,y){this.x=x;this.y=y}};this.anchor={set(){}};this.position={set(x,y){this.x=x;this.y=y}};}
 static from(src){return new Sprite({src})}
}
const PIXI={Graphics,Text,Sprite,Texture:{EMPTY:{}}};
const win=vm.createContext({PIXI,revealStarsOneByOne:()=>{},setTimeout:()=>0});
vm.runInContext(nativeCode,win);
const nativeNameStars=win.nativeNameStars;
function fig(){
 const slot={children:[],addChild(i){this.children.push(i)}};
 const slots=new Array(19).fill(null).map(()=>slot);
 const hidden=[];
 return {hidden,slot,skeleton:{findSlotIndex(n){
 return n==='name'?0:n==='1xing'?1: n==='xing10'?2:-1;
 }},slotContainers:slots,hackTextureBySlotName(n){hidden.push(n)}};
}
for(const n of [1,5,10,15,25]){
 const f=fig();
 assert.equal(nativeNameStars(f,{table_id:758001,name:'Lyr Sonia'},n,true),true);
 const images=f.slot.children.filter(x=>x instanceof Sprite);
 assert.equal(images.length,1,'Sonia Wish must have exactly one Cosmos badge');
 assert.equal(images[0].src,
   '/assets/chaos/lyr_sonia_tag_cosmos'+(n>=15?'_max':'')+'.png');
 assert.equal(images[0].position.y,78);
 assert(!f.slot.children.some(x=>x.src?.includes('partner_star_yellow')));
 if(n>=10)assert(f.slot.children.some(x=>x instanceof Text&&x.text===String(n)),
  'Actual star number must be preserved, not an arbitrary gold star');
}
const ordinarySonia=fig();
nativeNameStars(ordinarySonia,{table_id:758001,name:'Lyr Sonia'},5,false);
assert(ordinarySonia.slot.children.some(x=>x.src?.includes('partner_star_yellow')),
 'Non-Wish Sonia star stays exactly as before');
const other=fig();
nativeNameStars(other,{table_id:51016,name:'Diana'},5,true);
assert.equal(other.slot.children.filter(x=>x.src?.includes('partner_star_yellow')).length,5,
 'Wish of every other goddess must keep publisher stars');

const fstart=code.indexOf(' async function attachGirl(');
const fend=code.indexOf(' // The original Spine movie ships',fstart);
const attachSource=code.slice(fstart,fend);
assert(fstart>0&&fend>fstart);
const sources=[];
class MockImage{
 constructor(){this.onload=null;this.onerror=null;this.naturalWidth=1152;this.naturalHeight=1536}
 set src(v){this.path=v;sources.push(v);this.onload?.()}
 get src(){return this.path}
}
const ctx=vm.createContext({
 PIXI:{Sprite,Texture:{from(im){return {src:im.src}}}},
 Image:MockImage,
 pics:new Set([758001,51016]),
 pictures:{758001:{xy:[0,0],summon_static_scale:.47}},
 hostChain:id=>[id],
 girlIconSource:id=>'/assets/cards/partner_card_'+id+'.png',
 skipped:false,s4Sequence:false,
 setTimeout:()=>7,clearTimeout:()=>{},setInterval:()=>8,clearInterval:()=>{},
});
vm.runInContext(attachSource,ctx);
const attachGirl=ctx.attachGirl;
function artSlot(){
 const slot={children:[],addChild(o){this.children.push(o)}};
 const fig={skeleton:{findSlotIndex:n=>n==='juese'?0:-1},slotContainers:[slot]};
 return {slot,fig};
}
(async()=>{
 for(const [id,wish,url] of [
  [758001,true,'/assets/chaos/lyr_sonia_wish_cutout.webp'],
  [758001,false,'/assets/pictures/758001.webp'],
  [51016,true,'/assets/pictures/51016.webp']
 ]){
  const holder=artSlot();await attachGirl(holder.fig,id,wish);
  assert.equal(sources.at(-1),url);
  assert.equal(holder.slot.children.length,1);
  assert.equal(holder.slot.children[0].src,url);
 }
 assert(code.includes('Number(summonId)===29&&Number(partners[i].table_id)===758001'),
  'Only Sonia banner 29 may use cutout in ordinary draws');
 assert(code.includes('await attachGirl(fig,entry.table_id,Number(entry.table_id)===758001);'),
  'S4/Wish includes Sonia-only artwork substitution');
 assert(code.includes('nativeNameStars(fig,entry,star,Number(entry.table_id)===758001)'),
  'S4/Wish includes Sonia-only Cosmos badge');
 assert(html.includes('/summon-anim.js?v=20261123-faction-reveal-r6'));
 assert(fs.existsSync('web/assets/chaos/lyr_sonia_wish_cutout.webp'));
 console.log('PASS: Sonia Wish alone gets cutout + purple Cosmos star; other girls, non-Wish art and original overlays unchanged.');
})().catch(e=>{console.error(e);process.exitCode=1});
