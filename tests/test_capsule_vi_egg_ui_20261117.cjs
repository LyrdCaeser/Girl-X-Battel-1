'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const code=fs.readFileSync('web/app.js','utf8');
const source=code.slice(code.indexOf('function renderCapsule(){'),code.indexOf('function renderSummon(partners){')).trim();
const ids=['capsule-gold','capsule-gems','regular-count','advanced-count','bff-count',
 'regular-stock','regular-free','advanced-free','capsule-egg-points','capsule-egg-fill',
 'summon-egg','summon-free','summon-one','summon-ten','summon-senior-free',
 'summon-senior-one','summon-senior-ten','summon-senior-gem-one','summon-senior-gem-ten',
 'summon-bff-one','summon-bff-ten'];
const nodes=Object.fromEntries(ids.map(id=>[id,{textContent:'',style:{},disabled:true,firstChild:{nodeType:3,nodeValue:'Free'},
 querySelector(sel){if(sel==='small')return this._small??=( {textContent:''});
 if(sel==='strong')return this._strong??=({firstChild:{nodeType:3,nodeValue:'1'},textContent:''});
 return null;},setAttribute(name,value){this[name]=value}}]));
const banners={};for(const type of ['regular','advanced','bff']){
 const target={children:[],append(n){this.children.push(n)}};
 banners[type]={target,querySelector(sel){return sel==='.capsule-title-vi'?target.children[0]||null:target}};
}
const document={
 querySelector(sel){const m=/\.capsule-banner\.(\w+)$/.exec(sel);return m?banners[m[1]]:null},
 createElement(){return {className:'',textContent:''}},
 createTextNode(value){return {nodeType:3,nodeValue:value}},
};
const context=vm.createContext({document,busy:false,number:n=>String(n),
 $:id=>nodes[id],state:{}});
vm.runInContext(source,context);
const render=vm.runInContext('renderCapsule',context);
function state(pts,starter,unlocked){
 context.state={items:{'1':100,'2':300,'12':pts,'33':12,'36':2,'11':120},
 vip_info:{level:unlocked?3:0},summon:{free_ready:true,senior_free_ready:false,
 egg_points:pts,egg_cost:1000,egg_starter_available:starter,egg_vip_unlocked:unlocked}};
 render();
}
state(1000,true,false);
assert.equal(nodes['summon-egg'].disabled,false);
assert.equal(nodes['summon-egg'].querySelector('small').textContent,'Mở đầu · 5★');
assert.equal(nodes['capsule-egg-fill'].style.width,'100%');
assert.equal(nodes['summon-ten'].disabled,false);
assert.equal(nodes['summon-senior-ten'].disabled,true);
assert.equal(nodes['summon-free'].disabled,false);
assert.equal(nodes['summon-senior-free'].disabled,true);
assert.equal(nodes['summon-one'].firstChild.nodeValue,'Triệu Hồi 1');
assert.equal(nodes['summon-senior-gem-one'].disabled,false);
assert.equal(banners.advanced.target.children[0].textContent,'Triệu Hồi Cao Cấp');
state(2000,false,false);
assert.equal(nodes['summon-egg'].disabled,true,'VIP0 cannot open a second Egg');
assert.equal(nodes['capsule-egg-fill'].style.width,'100%','progress remains capped');
state(1000,false,true);
assert.equal(nodes['summon-egg'].disabled,false,'VIP3 can open');
state(999,false,true);
assert.equal(nodes['summon-egg'].disabled,true,'VIP3 still needs 1000 points');
assert.equal(banners.regular.target.children.length,1,'no stacked labels');
assert.equal(banners.advanced.target.children.length,1,'no stacked labels');
console.log('PASS: translated capsule UI, non-overlapping titles, VIP3 gate, starter egg, real stock and cooldown');
