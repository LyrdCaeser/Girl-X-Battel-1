'use strict';
// Use the actual browser picker functions without loading a player account.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('web/girl-ui.js','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const css=fs.readFileSync('web/girl-ui.css','utf8');
const start=source.indexOf(' function starOf(g){'),end=source.indexOf(' function chooseMaterial(hero,',start);
assert(start>0&&end>start,'real material picker exists');
const ctx=vm.createContext({
 Number,JSON,Math,Set,
 awakeSel:{},state:{roster:[],acquisition:{exchange:{partner_id:null}}},
 girlsCatalog:[
  {id:758001,name:'Lyr Sonia',stars:10},
  {id:55014,name:'Apollis',stars:5},
  {id:53019,name:'Nymphaea',stars:5},
  {id:55012,name:'Promethea',stars:5},
  {id:655023,name:'Apollis',stars:6},
  {id:653026,name:'Nymphaea',stars:6},
  {id:753019,name:'Nymphaea',stars:10},
 ],factionNames:['','U Linh Ma','Nhân Tộc','Ma Thú','Tinh Linh','Bóng Tối','Ánh Sáng','Vũ Trụ','Hỗn Độn'],
});
const api=vm.runInContext(source.slice(start,end)+';({matches,codeLabel,pick,materialsReady,requirementsAvailable,materialCandidates,selectionKey,savedSelection})',ctx);
const host={partner_id:1,table_id:758001,stars:14,group:8,awake:4,flags:[],pos:0};
function girl(pid,id,stars,group,locked=false){return {partner_id:pid,table_id:id,stars,group,awake:stars-({758001:10,55014:5,53019:5,55012:5,655023:6,653026:6,753019:10,757001:10,757002:10,757003:10}[id]||10),flags:[],locked,pos:0,lv:1,name:'Nữ Thần'};}
const sonia=[girl(10,758001,10,8),girl(11,758001,10,8),girl(12,758001,10,8)];
const cosmos11=girl(20,757002,11,7),cosmos10=girl(21,757001,10,7),cosmos13=girl(22,757003,13,7);
const nym10=girl(30,753019,10,3);
assert(api.matches(7999,cosmos10,host));
assert(api.matches(7999,cosmos11,host));
assert(api.matches(7999,cosmos13,host));
assert(!api.matches(7999,nym10,host));
assert(!api.matches(7999,cosmos10,{...host,table_id:753019}));
assert(api.matches(117999,cosmos11,host));
assert(!api.matches(117999,cosmos10,host));
assert(!api.matches(117999,cosmos13,host));
assert(api.matches(109999,nym10,host));
assert(!api.matches(109999,girl(31,53019,5,3),host));
assert(!api.matches(758001,girl(40,758001,11,8),host));
assert(api.codeLabel(7999).includes('Hệ Vũ Trụ'));
assert(api.codeLabel(117999).includes('11★'));
assert(api.codeLabel(55014).includes('Apollis 5★'));
assert(api.codeLabel(653026).includes('Nymphaea 6★'));
assert(api.codeLabel(758001).includes('nguyên bản'));
const recipe={material:[758001,758001,758001,117999,753019],star:15};
ctx.state.roster=[host,...sonia,cosmos11,cosmos10,nym10];
const available=api.requirementsAvailable(recipe,host);
assert(available,'Exactly five distinct valid goddess copies available');
const saved=api.savedSelection(recipe,host);
saved.normal=[10,11,12,20,30];
const picked=api.pick(recipe,host);
assert(api.materialsReady(recipe,picked));
assert.deepEqual(Array.from(picked,x=>x.partner_id),[10,11,12,20,30]);
const excluded=api.materialCandidates(recipe,host,'normal',3);
assert(excluded.some(x=>x.partner_id===20),'Current choice remains available for re-selection');
assert(!excluded.some(x=>x.partner_id===21),'10★ Cosmos cannot replace 11★ Cosmos at 15');
ctx.state.roster=[host,...sonia,cosmos10,nym10];
assert(!api.requirementsAvailable(recipe,host));
assert(!api.materialsReady(recipe,api.pick(recipe,host)));
ctx.state.roster=[host,...sonia,cosmos11,nym10];ctx.state.roster[1]={...ctx.state.roster[1],locked:true};
assert(!api.requirementsAvailable(recipe,host));
assert(source.includes("const mats=el('div','lb-mats'+((r.material||[]).length>2?' wrap':''))"));
assert(source.includes("c.append(el('span','lb-material-label',codeLabel(Number(code))))"));
assert(css.includes('.lb-mats.wrap .lb-mat.choose'));
assert(css.includes('.lb-material-label'));
assert(html.includes('/girl-ui.js?v=20261123-sonia-ritual-costs-r6'));
assert(html.includes('/girl-ui.css?v=20261123-sonia-ritual-12-15-r5'));
console.log('PASS: 14★ Cosmos any rank, 15★ Cosmos exactly 11★, three distinct Sonia 10★, named-star labels, disabled absent/locked materials, mobile wrap.');
