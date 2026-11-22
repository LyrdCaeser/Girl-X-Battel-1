'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const code=fs.readFileSync('web/girl-ui.js','utf8');
const start=code.indexOf('  function materialSlotPreview(');
const end=code.indexOf('  function chooseMaterial(',start);
assert(start>0&&end>start,'real awakening preview helper found');
const source=code.slice(start,end);
const el=(tag,cls='',text='')=>({
 tag,cls,text,children:[],attrs:{},
 append(...children){this.children.push(...children)},
 classList:{add(k){this.added=k},contains(k){return this.added===k}},
});
const context=vm.createContext({
 Number,
 el,card:id=>({tag:'span',cls:'lb-card',tid:id}),
 img:(src,cls)=>({tag:'img',src,cls}),
 materialCandidates:()=>[],
});
vm.runInContext(source+';globalThis.preview=materialSlotPreview',context);
const hero={table_id:758001,partner_id:77};
const recipe={material:[758001],star:11};
function slot(selected=null,code=758001,kind='normal',candidates=[]){
 context.materialCandidates=()=>candidates;
 const pic=el('span','lb-pic');
 context.preview(pic,hero,recipe,kind,0,selected,code);
 return pic;
}
let pic=slot();
assert.equal(pic.children[0].tid,758001,'unselected slot displays required Lyr Sonia artwork');
assert.equal(pic.children[1].cls,'lb-pick-mark','add small picker affordance');
assert(pic.classList.contains('lb-preview'),'empty shows preview not consumed');
pic=slot({table_id:758001,partner_id:10});
assert.equal(pic.children[0].tid,758001);
assert.equal(pic.children.length,1,'selected displays real portrait without plus');
assert(!pic.classList.contains('lb-preview'),'selected not dimmed');
pic=slot(null,51999,'normal',[{table_id:651001}]);
assert.equal(pic.children[0].tid,651001,'wildcard previews eligible artwork');
pic=slot(null,51999,'normal',[]);
assert.equal(pic.children[0].cls,'lb-required-star','empty wildcard shows a real star image');
pic=slot(null,0,'copies',[]);
assert.equal(pic.children[0].tid,758001,'16–25-star same-name recipe shows host girl artwork');
const css=fs.readFileSync('web/girl-ui.css','utf8');
const html=fs.readFileSync('web/index.html','utf8');
assert(css.includes('.lb-mat.choose .lb-pic .lb-card{width:100%;height:100%;border:0'));
assert(html.includes('/girl-ui.js?v=20261122-awake-material-image-r1'));
assert(html.includes('/girl-ui.css?v=20261122-awake-material-image-r1'));
assert(!code.includes("pic.append(el('i','',code%1000===999?"),'no literal Chọn tile in material slots');
assert(code.includes('cardIds.has(tid)||Number(tid)===758001'),'Sonia special card always resolves to real card art');
console.log('PASS: required Sonia portrait, selection 0/1 vs 1/1, wildcard/awake25 and unchanged choice logic');
