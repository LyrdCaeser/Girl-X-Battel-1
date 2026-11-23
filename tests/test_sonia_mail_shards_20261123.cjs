'use strict';
// Test actual mail reward DOM and the bag's real collectible-shard metadata.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const home=fs.readFileSync('web/home-menus.js','utf8');
const app=fs.readFileSync('web/app.js','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const body=home.slice(home.indexOf(' function rewards(parent,text){'),
  home.indexOf(' function affordable(text){'));
assert(body.startsWith(' function rewards(parent,text){'));
const created=[];
function node(tag,cls,text){
 const o={tag,cls,textContent:text||'',children:[],append(...c){this.children.push(...c)}};
 created.push(o);return o;
}
const ctx=vm.createContext({
 el:(tag,text,cls)=>node(tag,cls,text),
 catalog:{items:{},assets:[]},
 itemCatalog:{},number:n=>Number(n).toLocaleString('vi-VN'),
 image:(name,cls)=>node('img',cls,name),
 itemPicture:()=>'',console
});
vm.runInContext(body,ctx);
const rewards=vm.runInContext('rewards',ctx);
const wrapper=node('article');
rewards(wrapper,'940061#500');
const container=wrapper.children[0];
assert.equal(container.cls,'hm-rewards');
assert.equal(container.children.length,1);
const tile=container.children[0];
assert.equal(tile.cls,'hm-reward');
const icon=tile.children.find(x=>x.tag==='img');
assert(icon,'The original Sonia shard portrait must be shown in GM mail');
assert.equal(icon.src,'/assets/item-icons/partner_avatar_758001.png');
assert.equal(icon.alt,'Mảnh Lyr Sonia');
assert(tile.children.some(x=>x.textContent==='500'));
assert(tile.children.some(x=>x.textContent==='Mảnh Lyr Sonia'));
assert(!tile.children.some(x=>/Vật phẩm 940061/.test(x.textContent)));
assert(app.includes("'940061':{id:940061,name:'Mảnh Lyr Sonia'"));
assert(app.includes("category:3,type:3"));
assert(app.includes("Tích đủ 100 mảnh"));
assert(app.includes("if(String(item?.id)==='940061')return '/assets/item-icons/partner_avatar_758001.png'"));
assert(app.includes('state.debris)?state.debris.find'));
assert(app.includes("action('SUMMON',{summon_id:Number(current.summon_id),times})"));
assert(html.includes('app.js?v=20261123-sonia-shard-mail-r12'));
assert(html.includes('home-menus.js?v=20261123-sonia-shard-mail-r3'));
console.log('PASS: Claimed 500 Sonia shards show real portrait/name in old admin letter; 100-shard compose remains in original bag.');
