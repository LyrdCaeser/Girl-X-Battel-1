'use strict';
// Checks the actual in-game price rendering helper and mobile awakening labels.
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('web/girl-ui.js','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const catalog=JSON.parse(fs.readFileSync('web/assets/items-catalog.json','utf8'));
const first=source.indexOf(' const NAMES=');
const last=source.indexOf(' function detail(hero){',first);
assert(first>=0&&last>first);
const create=(tag,cls,text)=>{
 const n={tag,cls:cls||'',textContent:text||'',children:[],title:'',
          append(...children){this.children.push(...children)}};
 return n;
};
const context=vm.createContext({
 el:create,
 img:(src,cls)=>({...create('img',cls),src}),
 itemCatalog:catalog,
 itemIcons:new Set(['icon_10','icon_417','icon_173']),
 state:{items:{10:30000,417:16100,173:200}},
 number:n=>Number(n).toLocaleString('vi-VN')
});
const {NAMES,cost}=vm.runInContext(source.slice(first,last)+';({NAMES,cost})',context);
assert.equal(NAMES['10'],'Hộp Cơm');
assert.equal(NAMES['417'],'Ngọc Linh Hồn');
assert.equal(NAMES['173'],'Honor Badge');
for(const [type,prices,expected] of [
 ['11–15★',{'10':15000,'417':500},'/assets/item-icons/icon_417.png'],
 ['16–25★',{'10':80000,'173':21},'/assets/item-icons/icon_173.png']
]){
 const parent=create('section');
 assert.equal(cost(parent,prices),type==='11–15★');
 const badges=parent.children[0].children;
 assert.equal(badges.length,2,type+' must show exactly two resource icons');
 assert.equal(badges[0].children[0].src,'/assets/item-icons/icon_10.png');
 assert.equal(badges[1].children[0].src,expected);
 assert(badges[0].title.includes('Hộp Cơm'));
 assert(badges[1].title.includes(type==='11–15★'?'Ngọc Linh Hồn':'Honor Badge'));
 assert(badges[1].title.includes('Hiện có'));
 if(type==='16–25★')assert.equal(badges[0].cls,'short');
}
const lackingSoul=create('section');
context.state.items[417]=199;
assert.equal(cost(lackingSoul,{'10':10000,'417':200}),false);
assert.equal(lackingSoul.children[0].children[1].cls,'short');
const lackingBadge=create('section');
context.state.items[173]=3;
assert.equal(cost(lackingBadge,{'10':25000,'173':4}),false);
assert.equal(lackingBadge.children[0].children[1].cls,'short');
assert(source.includes('Nguyên liệu tiêu hao: Hộp Cơm và Ngọc Linh Hồn.'));
assert(source.includes('Nguyên liệu tiêu hao: Hộp Cơm và Honor Badge.'));
assert(html.includes('girl-ui.js?v=20261123-sonia-ritual-costs-r6'));
console.log('PASS Sonia awakened resources: native icon_10/417/173, Vietnamese cost captions, visible counts, shortage disables action.');
