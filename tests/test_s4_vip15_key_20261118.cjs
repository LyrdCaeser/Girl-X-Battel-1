'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const read=p=>fs.readFileSync(p,'utf8');
const key='990004', catalog=JSON.parse(read('web/assets/items-catalog.json'));
const item=catalog[key];
assert.equal(item.name,'Chìa Khóa S4 • Độc Quyền');
assert.equal(item.type,43); // social gift block
assert.equal(item.category,2);
assert(read('web/assets/ui/s4-exclusive-key.svg').includes('ĐỘC QUYỀN'));
const app=read('web/app.js'),home=read('web/home-menus.js'),auth=read('web/auth.js'),html=read('web/index.html');
assert(app.includes("String(item?.id)==='990004'"));
assert(home.includes('m.attachments?.__s4_exclusive_key__'));
assert(home.includes('Nhận Chìa Khóa S4'));
assert(home.includes('/assets/ui/s4-exclusive-key.svg'));
assert(auth.includes('Chìa Khóa S4 • Độc Quyền'));
for(const file of ['app.js','home-menus.js','home-menus.css','auth.js'])
 assert(html.includes('/'+file+'?v=20261118-vip15-s4key-r1'),file);
assert(app.includes('/assets/items-catalog.json?v=20261118-vip15-s4key-r1'));
console.log('PASS VIP15 S4 exclusive key UI: SVG, VIP mail, bag inventory, no gifts, versioned assets');
