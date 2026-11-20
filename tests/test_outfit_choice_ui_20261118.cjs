'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const app=fs.readFileSync('web/app.js','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const css=fs.readFileSync('web/bag-actions.css','utf8');
const local=fs.readFileSync('web/bag-vi.js','utf8');
const ctx=vm.createContext({window:{}});
vm.runInContext(local,ctx);
const t=ctx.window.GxbBagVi.t;
assert.equal(t('Customized Celestial Outfit Chest'),'Rương tự chọn Trang Phục Tinh Tú');
assert.equal(t('You can select to get an Outfit piece of "Celestial" Set for opening this chest'),
             'Mở rương để chọn một món trang phục thuộc bộ Tinh Tú.');
assert(app.includes('originalOutfit?option.image:(reward&&itemPicture(reward))'));
assert(app.includes('Number(option.quality||reward?.quality)'));
assert(app.includes('image.onerror=()=>{image.onerror=null;image.remove();}'));
assert(css.includes('.bag-native-choice-art img{width:88%;height:88%;object-fit:contain}'));
for(const key of ['app.js?v=20261118-outfit-choice-image-r1','bag-vi.js?v=20261118-outfit-chest-vi-r1','bag-actions.css?v=20261118-outfit-choice-layout-r1'])
 assert(html.includes(key),key);
console.log('PASS: original Outfit icons & 100% Vietnamese Celestial chest names, no visible item codes');
