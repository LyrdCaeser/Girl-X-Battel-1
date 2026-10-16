// Giftcode Studio UI regression, no network/browser or player data.
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const app=fs.readFileSync(path.join(root,'giftcode-studio/app.js'),'utf8');
const html=fs.readFileSync(path.join(root,'giftcode-studio/index.html'),'utf8');
const bridge=fs.readFileSync(path.join(root,'giftcode-studio/api/bridge.js'),'utf8');
const back=fs.readFileSync(path.join(root,'gxb2/skin_store.py'),'utf8');
const priceStart=app.indexOf('function parseSkinPrice(raw){');
const priceEnd=app.indexOf('\nfunction skinSettings(card){',priceStart);
const start=app.indexOf('function skinSettings(card){');
const end=app.indexOf('\nfunction skinSaveStatus(',start);
assert(priceStart>=0&&priceEnd>priceStart,'VNĐ prices must use a localized integer parser');
assert(start>=0&&end>start,'Skin settings form implementation must exist');
const parsePrice=vm.runInNewContext('('+app.slice(priceStart,priceEnd)+')');
const serialize=vm.runInNewContext('('+app.slice(start,end)+')',{parseSkinPrice:parsePrice});
assert.equal(parsePrice('299.000'),299000);
assert.equal(parsePrice('1.299.000'),1299000);
const makeCard=(enabled,bank,crystal,vnd='59999',crystals='200')=>{
 const fields={
   enabled:{checked:enabled},allow_bank:{checked:bank},allow_crystal:{checked:crystal},
   price_vnd:{value:vnd},price_crystal:{value:crystals}
 };
 return {dataset:{skinId:'7280'},querySelector(q){const m=/^\[data-field="([a-z_]+)"\]$/.exec(q);return m?fields[m[1]]:null;}};
};
for(const choice of [[true,true,false],[false,false,false],[true,false,true]]){
 const payload=serialize(makeCard(...choice));
 assert.equal(typeof payload.enabled,'boolean');
 assert.equal(typeof payload.allow_bank,'boolean');
 assert.equal(typeof payload.allow_crystal,'boolean');
 assert.equal(payload.enabled,choice[0]);
 assert.equal(payload.allow_bank,choice[1]);
 assert.equal(payload.allow_crystal,choice[2]);
 assert.equal(typeof payload.price_vnd,'number');
 assert.equal(typeof payload.price_crystal,'number');
 assert.deepEqual(
   [typeof JSON.parse(JSON.stringify(payload)).enabled,
    typeof JSON.parse(JSON.stringify(payload)).allow_bank],
   ['boolean','boolean']);
}
assert.throws(()=>serialize(makeCard(true,true,false,'10.5','100')),/số nguyên/);
assert.throws(()=>serialize(makeCard(true,true,false,'-1','100')),/số nguyên/);
assert(/type\(req\.get\(k\)\) is not bool/.test(back),'server must validate real JSON booleans');
assert(/Chuyển khoản ngân hàng/.test(app),'Studio must use bank payment instead of old Gold');
assert(!/Bán bằng Vàng/.test(app),'obsolete Gold controls must never return');
assert(/id="account-sync"[\s\S]*?giftcode\/sso\/start/.test(html),'GXB3 sync action must be visible in the header');
assert(/id="account-character"/.test(html),'Studio must show selected game character and server');
assert(/giftcode\/sso\/exchange/.test(app),'SSO ticket must be consumed by Studio');
assert(/accountIdentity/.test(app)&&/panelAccess='';state\.gmActionKey='';state\.skins=\[\]/.test(app),'owner unlock and GM key must be cleared when switching account');
for(const id of ['unlock-admin-key','unlock-password','unlock-gm-key']){
 assert(html.includes('id="'+id+'"'),'Owner gate must include '+id);
}
assert(app.includes("el.hidden=!['redeem','shop','gift'].includes(el.dataset.view)&&!(state.admin&&state.panelUnlocked)"),
 'Privileged navigation must remain locked while Shop and GiftSkin are public');
assert(html.includes('data-view="gift"')&&html.includes('id="gift-view"'),
 'GiftSkin must be visible to players and separate from the admin settings');
assert(html.includes('id="account-switch"')&&app.includes("api('/api/auth/logout'"),
 'Studio must allow changing only its own signed-in account');
assert(app.includes("api('/api/giftskin/verify'")&&app.includes("api('/api/giftskin/crystal'"),
 'Public GiftSkin requires recipient verification and atomic Crystal endpoint');
assert(/admin_key:\$\('unlock-admin-key'\)\.value/.test(app),'Gate must send admin key only on explicit unlock');
assert(bridge.includes('sso\\/exchange')&&bridge.includes('giftcode\\/'),'Vercel bridge must allow game SSO endpoint');
console.log('PASS | Studio SSO account identity is explicit and synced by one-use GXB3 ticket');
console.log('PASS | Studio Skin checkbox fields serialize as JSON booleans, VNĐ/Crystal only');
