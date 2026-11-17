'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const html=read('web/index.html'),css=read('web/equipment.css'),app=read('web/app.js'),souls=read('web/souls.js');
const bag=read('web/bag-vi.js'),soulCss=read('web/souls.css');
const catalog=JSON.parse(read('web/assets/items-catalog.json'));
const ctx=vm.createContext({window:{}});
vm.runInContext(bag,ctx);
const t=vm.runInContext('window.GxbBagVi.t',ctx);
const stones=Object.values(catalog).filter(x=>x.category===7&&[39,40,41,42].includes(x.type));
const artifacts=Object.values(catalog).filter(x=>x.category===7&&x.type===38);
assert.equal(stones.length,216);
assert.equal(artifacts.length,24);
for(const x of [...stones,...artifacts]){
 assert(!/Majestic Phoenix|Anima Stone|Objeto |Slot \d/i.test(t(x.name)),x.name);
 assert(!/Anima Stone|Primary Attribute provides|Crit Resist\/Block/.test(t(x.description||'')),x.description);
}
assert.equal(t(catalog['5209404'].name),'Phượng Hoàng Uy Nghi · IV');
assert.match(t(catalog['5209404'].description),/Kháng Bạo Kích.*Miễn Khống Chế/);
assert.match(css,/#smithy-view \.sm-grid \.sm-item>img\.eq-red\{[\s\S]*?width:14px!important/);
assert.match(css,/#smithy-view \.eq-nav button>img\.eq-red\{[\s\S]*?width:13px!important/);
assert.match(souls,/Đá và Bảo Vật Linh Hồn đang xếp chồng/);
assert.match(souls,/Trang Bị Linh Hồn · /);
assert.match(soulCss,/\.ag-bag-section/);
assert.match(app,/original\.usable[\s\S]*?Number\(item\.category\)===7&&\[38,39,40,41,42\]/);
assert.match(app,/kind:'soul_receive'/);
assert.match(app,/receive_inventory_gear/);
assert.match(app,/Mỗi món nhận sẽ trừ đúng 1 vật phẩm gốc/);
assert.match(app,/GirlUI\.confirm\(msg,\{title:'Xác Nhận Nhận Trang Bị'/);
for(const v of [
'\/equipment.css?v=20261117-forge-alert-size-r4',
'\/bag-vi.js?v=20261117-anima-stone-vi-r10',
'\/app.js?v=20261117-anima-convert-r4',
'\/souls.js?v=20261117-anima-split-r4',
'\/souls.css?v=20261117-anima-split-r4'])assert(html.includes(v),v);
console.log('PASS: tiny forge red dots, localized 216 stones and 24 artifacts, separated Anima inventory and confirmed conversion');
