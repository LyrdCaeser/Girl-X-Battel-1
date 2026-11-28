'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const doc={readyState:'loading',documentElement:{},addEventListener(){},body:{}};
const c=vm.createContext({
 window:{},document:doc,Node:{TEXT_NODE:3,ELEMENT_NODE:1},
 MutationObserver:class {observe(){}}
});
vm.runInContext(fs.readFileSync('web/i18n-vi.js','utf8'),c);
const t=c.window.GxbVi?.t;
assert.equal(typeof t,'function');
const original='Crit +2.000  Crit DMG +5.000  Block +2.080  Crit Resist +2.000  DMG Red. +1.000  CC Immune +600';
const out=t(original);
for(const label of ['Bạo Kích +2.000','ST Bạo Kích +5.000','Đỡ Đòn +2.080','Kháng Bạo Kích +2.000','Giảm Sát Thương +1.000','Miễn Khống Chế +600']){
 assert(out.includes(label),'missing: '+label+' got: '+out);
}
for(const forbidden of ['Crit +','Crit DMG','DMG Red.','CC Immune','Crit Resist']){
 assert(!out.includes(forbidden),'English label still rendered: '+forbidden);
}
assert.equal(t('Lord Dracula'), 'Lord Dracula');
assert.equal(t('Critical Force'), 'Critical Force');
assert.equal(t('Crit +2.000'),'Bạo Kích +2.000');
console.log('PASS: all six numeric stat labels localized; values unchanged; Goddess names protected');
