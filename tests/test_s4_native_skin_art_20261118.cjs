'use strict';
/** Actual S4 cinematic skin playback: original full portrait before cards,
 * isolated from the Goddess-only GIRLS/CV/name/star skeleton.
 */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('web/summon-anim.js','utf8');
const begin=source.indexOf(' async function s4RevealSkinCinema(items,progress){');
const end=source.indexOf(' function s4SuppressBakedGirlHeading(fig){',begin);
assert(begin>=0&&end>begin);
const js=source.slice(begin,end);
let scene=null;const mounted=[],images=[],played=[],texts=[],effects=[];
class Element {
 constructor(tag,cls,text){
  this.tag=tag;this.className=cls||'';this.textContent=text||'';
  this.children=[];this.attr={};this.style={};this.hidden=false;
  this.classList={
   values:new Set(),add:name=>this.classList.values.add(name),
   remove:name=>this.classList.values.delete(name)
  };
 }
 append(...child){this.children.push(...child);}
 remove(){this.removed=true;}
 setAttribute(k,v){this.attr[k]=v;}
 removeAttribute(k){delete this.attr[k];}
 get offsetWidth(){return 680;}
}
const stage=new Element('div','sa-stage');
const state={
 skipped:false,
 layer:async path=>{
  mounted.push(path);return {host:{classList:{add:()=>{}}},fig:{state:{}},done:()=>{}};
 },
 overlay:{querySelector:()=>stage},
 el:(tag,cls,text)=>new Element(tag,cls,text),
 sfx:(key)=>effects.push(key),
 run:async(fig,anim)=>played.push(anim),
 s4LoadImage:async(url)=>{
  images.push(url);
  // Only original full model files are present for some skins.
  return url.includes('/assets/pictures/5200403.webp')||
         url.includes('/assets/skins/cards/7231.webp')?
    {src:url}:null;
 },
 s4Pause:async ms=>{assert.equal(ms,1800);},
 Number,String,Math,Array,console
};
vm.runInNewContext(js,state);
const fn=vm.runInContext('s4RevealSkinCinema',state);
(async()=>{
 await fn([
  {id:7020,name:'Scarlet',picture_model:'5200403',partners:[754013]},
  {id:7231,name:'Present Keeper',picture_model:'',partners:[755010]},
  {id:7235,name:'Intertwined',picture_model:'',partners:[54013,654020,754013]}
 ],{textContent:''});
 assert.deepEqual(mounted,['/assets/spine/fx_ui_gacha_revision'],
  'Skin must use real Gacha FX and must never mount Goddess-only gaino skeleton');
 assert(images.includes('/assets/pictures/5200403.webp'),
  'Prefer original full-size skin picture');
 assert(images.includes('/assets/skins/cards/7231.webp'),
  'Use correct original skin card if no full-size picture is available');
 assert(images.includes('/assets/cards/partner_card_754013.png'),
  'Missing original skin art gracefully falls back to its real family goddess');
 assert.equal(played.filter(x=>x==='222').length,3);
 assert.equal(effects.filter(x=>x==='ui_gain_hero_5star').length,3);
 assert(stage.children.some(n=>n.className==='sa-s4-skin-scene'));
 const imageNode=stage.children.find(n=>n.className==='sa-s4-skin-scene');
 assert.equal(imageNode.children.length,3);
 assert.equal(imageNode.children[1].tag,'img');
 assert(imageNode.removed);
 assert(!js.includes('s4SkinLabel('),'No Goddess nameplate/CV star overlay for skins');
 assert(!js.includes('s4Slot(fig'),'No narrow juese slot for skins');
 console.log('PASS: full-size original skin art, gacha VFX, fallback for missing skin, no GIRLS/CV/star skeleton');
})().catch(err=>{console.error(err);process.exitCode=1});
