/* Browser-free regression: exact VNĐ amounts and saved Skin state.
 * Run: node tests/test_giftcode_studio_prices.cjs
 */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const app=fs.readFileSync(path.join(root,'giftcode-studio/app.js'),'utf8');
const html=fs.readFileSync(path.join(root,'giftcode-studio/index.html'),'utf8');

function fromFunction(name,next,bindings={}){
  const from=app.indexOf('function '+name+'(');
  const to=app.indexOf(next,from);
  assert.ok(from>=0&&to>from,'Cannot locate '+name);
  return vm.runInNewContext('('+app.slice(from,to).trim()+')',bindings);
}
const parse=fromFunction('parseSkinPrice','function skinSettings(');
for(const [raw,want] of [
  ['0',0],['299000',299000],['299.000',299000],['359.000',359000],
  ['1.299.000',1299000],['1,299,000',1299000],['1 299 000',1299000],
  ['49.999',49999],['2000000000',2000000000]
]) assert.equal(parse(raw),want,'Wrong price for '+raw);
for(const raw of ['', '-1', '1.5', '299.00', '2e5','299.000,50','abc']) {
  assert.throws(()=>parse(raw),/Giá phải/,'Should reject '+raw);
}
const settings=fromFunction('skinSettings','function skinSaveStatus(',{parseSkinPrice:parse});
const fake=(data)=>({
  dataset:{skinId:'7193'},
  querySelector(selector){
    const name=selector.match(/data-field="([^"]+)"/)?.[1];
    if(!name||!Object.hasOwn(data,name))throw Error('Unknown data field '+selector);
    const val=data[name];
    return {value:String(val),checked:val===true};
  }
});
const good={enabled:true,allow_bank:true,allow_crystal:false,price_vnd:'299.000',price_crystal:'0'};
const read=settings(fake(good));
assert.deepEqual(JSON.parse(JSON.stringify(read)),{
  skin_id:7193,enabled:true,allow_bank:true,allow_crystal:false,
  price_vnd:299000,price_crystal:0
});
assert.throws(()=>settings(fake({...good,price_vnd:'299.00'})),/số nguyên/);
assert.throws(()=>settings(fake({...good,enabled:true,allow_bank:false})),/bật bán/);
assert.ok(app.includes("cache:'no-store'"),'Always request fresh saved data');
assert.ok(app.includes("await api('/api/skin-shop/admin/catalog')"),'Require fresh read after saving');
assert.ok(app.includes('function matchesSavedSkin('),'Require exact field checks');
assert.ok(app.includes('skin-save-result'),'Show per-card save outcomes');
assert.ok(html.includes('id="account-sync"'),'Expose GXB3 account sync on Studio');
console.log('PASS | Studio VNĐ 299.000 => 299000, valid Skin config, server read-back, and SSO entry');
