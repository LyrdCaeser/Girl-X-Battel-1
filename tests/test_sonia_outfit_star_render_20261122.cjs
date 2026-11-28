'use strict';
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const code = fs.readFileSync('web/skins.js','utf8');
const start=code.indexOf(' function card(s,hero,');
const end=code.indexOf(' async function detail(hero)',start);
assert(start>0 && end>start,'actual Skins.card source extracted');
const factory=code.slice(start,end);
const el=(tag,cls='',txt='')=>({
  tag,cls,textContent:String(txt),style:{},children:[],attrs:{},
  append(...children){this.children.push(...children)},
  setAttribute(k,v){this.attrs[k]=v},
});
const context=vm.createContext({
  el,btn:(cls,text,fn)=>{const out=el('button',cls,text);out.onclick=fn;return out},
  cardIds:new Set([758001,41001]),artId:id=>id,detailImage:id=>'/assets/characters/'+id+'.png',
  U:'/assets/skins/ui/',RARITY:['','Common','Rare','Epic','Legendary'],
  baseName:hero=>hero.stars>=10?'10★':'Mặc Định',
  renderGirlDetail(){},Number,
});
vm.runInContext(factory+';globalThis.extractedCard=card',context);
const card=context.extractedCard;
function walk(elm){return [elm,...elm.children.flatMap(walk)]}
for (const [stars,asset,number] of [
  [10,'star_orange_group_7.png',null],
  [11,'potentiality_card_star_group_7.png','1'],
  [15,'potentiality_card_star_group_7_max.png','5'],
  [25,'potentiality_card_star_group_7_max.png','15'],
]){
  const out=card({id:758001,base:true},{table_id:758001,stars,group:8}, {on:true,worn:false,own:true});
  const all=walk(out);
  const emblem=all.find(x=>x.cls==='gu-emblem');
  assert(emblem?.src.endsWith(asset), 'correct Cosmos emblem for '+stars+'★');
  const label=all.find(x=>x.cls.includes('sk-cosmos-star'));
  assert(label, 'native Cosmos presentation for '+stars+'★');
  assert(!all.some(x=>x.textContent==='10★'),'no fabricated 10★ text');
  assert.equal(all.find(x=>x.cls==='gu-emblem-num')?.textContent ?? null,number);
  assert(all.some(x=>x.cls==='sk-group' && x.src.endsWith('img_group8.png')),'Chaos icon retained');
}
const other=card({id:41001,base:true},{table_id:41001,stars:10,group:1},{on:true,worn:false,own:true});
assert(walk(other).some(x=>x.cls==='sk-name' && x.textContent==='10★'), 'unrelated originals unaffected');
console.log('PASS: Sonia outfit displays real Cosmos emblem (10-25★), Chaos faction unchanged');
