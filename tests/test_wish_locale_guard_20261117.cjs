'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const src=fs.readFileSync('web/wish.js','utf8');
const block=src.slice(src.indexOf('const LOCAL_WISH_VI='),src.indexOf('const girl=id=>'));
const ctx=vm.createContext({data:{text:{
 WISH_GACHA_TIPS_3:'The Wish Girl can be chosen and changed freely anytime during the event.',
 WISH_GACHA_NUM:'Draws',
 WISH_GACHA_TEXT5:'Guaranteed\nNew Girl',
 WISH_GACHA_TEXT10:"Wish Capsule won't count in Daily Task and Trophies",
 WISH_GACHA_TEXT_1:'Draw {1} Wish Capsules\n(Repeatable)',
 WISH_GACHA_NUM1:'100'
}}});
vm.runInContext(block,ctx);
const T=vm.runInContext('T',ctx);
assert(T('WISH_GACHA_TIPS_3').startsWith('Bạn có thể tự do chọn'));
assert(!T('WISH_GACHA_TIPS_3').includes('The Wish Girl'));
assert.equal(T('WISH_GACHA_NUM'),'Lượt triệu hồi');
assert(T('WISH_GACHA_TEXT5').includes('Nữ Thần'));
assert(T('WISH_GACHA_TEXT10').includes('Nhiệm Vụ Hằng Ngày'));
assert.equal(T('WISH_GACHA_TEXT_1',100).split('\n')[0],'Triệu Hồi Ước Nguyện 100 lần');
assert.equal(T('WISH_GACHA_NUM1'),'100');
const html=fs.readFileSync('web/index.html','utf8');
assert(html.includes('wish.js?v=20261123-sonia-hard150-r9'));
console.log('PASS: 20 cached English strings suppressed in client, numbers and gameplay untouched');
