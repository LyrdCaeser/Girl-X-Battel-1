'use strict';
const fs=require('fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const js=fs.readFileSync('web/summon-anim.js','utf8');
const from=js.indexOf(' function s4CleanupArt(slots){');
const to=js.indexOf(' // Use actual original Gacha effects',from);
assert(from>0&&to>from);
let tempDestroyed=0,sharedDestroyed=0,textDestroyed=0;
class NativeText {
 destroy(opts){if(opts.texture&&opts.baseTexture)textDestroyed++;}
}
const context=vm.createContext({PIXI:{Text:NativeText},console});
vm.runInContext(js.slice(from,to),context);
const cleanup=vm.runInContext('s4CleanupArt',context);
const root={children:[],removeChild(child){this.children.splice(this.children.indexOf(child),1);}};
const shared={destroy(opts){if(opts.texture||opts.baseTexture)sharedDestroyed++;}};
const transient={__s4WishTexture:{destroy(force){assert.equal(force,true);tempDestroyed++;}},
 destroy(opts){assert.equal(opts.texture,false);}};
const label=new NativeText();
root.children.push(shared,transient,label);
cleanup([{slot:root,original:new Set([shared])}]);
assert.equal(root.children.length,1);
assert.equal(root.children[0],shared);
assert.equal(tempDestroyed,1);
assert.equal(sharedDestroyed,0);
assert.equal(textDestroyed,1);
console.log('PASS: per-reward Wish WebGL textures reclaimed, original shared Spine/star assets retained');
