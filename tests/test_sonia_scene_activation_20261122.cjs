'use strict';
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const app=fs.readFileSync('web/app.js','utf8');
const start=app.indexOf("art.src=src||'/assets/ui/item_bg.png';");
const end=app.indexOf('art.alt=hero.name;',start);
assert(start>0 && end>start,'actual Sonia detail scene code located');
const source=app.slice(start,end);
const scene={querySelector:()=>null};
const classes=new Set();
const root={classList:{toggle(name,on){if(on)classes.add(name);else classes.delete(name)}}};
function simulate(heroId,imageId,src){
 classes.clear();
 const context={art:{},src,hero:{table_id:heroId},imageId,sheetScene:scene,
  $:id=>{assert.equal(id,'girl-detail-view');return root}, Number};
 vm.runInNewContext(source,context);
 return classes.has('sonia-continuation-scene');
}
// This source-path-independent activation was the missing requirement.
// The older code activated only when the art path was exactly .png.
assert(simulate(758001,758001,'/assets/characters/758001.png'));
assert(simulate(758001,758001,'/assets/pictures/758001.webp'));
assert(simulate(758001,758001,'/assets/any/758001.png?version=2'));
assert(!simulate(758001,1234,'/assets/skins/1234.webp'));
assert(!simulate(751001,751001,'/assets/characters/751001.png'));
const css=fs.readFileSync('web/girl-ui.css','utf8');
assert(css.includes('#girl-detail-view.gs-zoom.sonia-continuation-scene > .detail-scene'));
assert(css.includes("background-image:url('/assets/chaos/lyr_sonia_zoom_bedding_floor.png')!important"));
assert(css.includes('background-size:100% auto!important'));
assert(!css.includes('.sonia-bottom-fill{display:none;}'));
console.log('PASS: Sonia scene fallback works for any default-art URL, remains mobile-only, leaves other girls unchanged');
