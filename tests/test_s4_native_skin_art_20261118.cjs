'use strict';
// A missing skin-card portrait must fall back to an ORIGINAL character portrait
// inside the native Spine 'juese' slot, not an empty collection tile.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('web/summon-anim.js','utf8');
const begin=source.indexOf(' async function s4AttachSkin(fig,skin){');
const end=source.indexOf(' function s4Pause(ms){',begin);
assert(begin>=0&&end>begin);
const code=source.slice(begin,end);
const attempts=[],sprites=[];
const slot={addChild:child=>sprites.push(child)};
const ctx=vm.createContext({
 s4Slot:()=>slot,
 s4LoadImage:async url=>{
  attempts.push(url);
  return attempts.length===1?null:{naturalWidth:512,naturalHeight:680};
 },
 skipped:false,
 girlIconSource:()=>'', // Image not in the cached girl-icon list
 PIXI:{
  Texture:{from:img=>({img})},
  Sprite:class {
   constructor(texture){this.texture=texture;this.scale={set:(x,y)=>this.xy=[x,y]};this.anchor={set:()=>{}};this.position={set:(x,y)=>this.positioned=[x,y]};}
  },
 },
 Number,Math,
});
vm.runInContext(code,ctx);
const reveal=vm.runInContext('s4AttachSkin',ctx);
(async()=>{
 const result=await reveal({},{id:7235,name:'Intertwined',partners:[54013,654020,754013]});
 assert.equal(result,true);
 assert.equal(attempts[0],'/assets/skins/cards/7235.webp');
 assert.equal(attempts[1],'/assets/cards/partner_card_754013.png');
 assert.equal(sprites.length,1);
 assert.deepEqual(sprites[0].positioned,[0,145]);
 console.log('PASS: missing skin 7235 falls back to verified original 754013 artwork inside Spine');
})().catch(e=>{console.error(e);process.exitCode=1});
