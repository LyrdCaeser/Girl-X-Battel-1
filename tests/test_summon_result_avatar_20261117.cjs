'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const js=fs.readFileSync('web/summon-result.js','utf8');
const cut=js.slice(js.indexOf('function nativePortrait('),js.indexOf(' function heroIcon(')).trim();
function img(src,cls){
 return {src,className:cls,removed:false,classList:{add(n){this[n]=true}},removeAttribute(n){if(n==='src'){this.src='';this.removed=true}}}
}
const avatars={'31001':{src:'/assets/avatar-hd/portraits/partner_avatar_31001.webp?v=1.1.2'}};
const context=vm.createContext({img,avatars,hostChain:id=>[id],girlIconSource:()=>''});
const nativePortrait=vm.runInContext('('+cut+')',context);
const head=nativePortrait(31001);
assert.equal(head.src,'/assets/avatar-hd/portraits/partner_avatar_31001.webp?v=1.1.2');
head.onerror();assert.equal(head.src,'/assets/original-ui/portraits/partner_avatar_31001.png');
head.onerror();assert.equal(head.src,'/assets/cards/partner_card_31001.png');
head.onerror();assert.equal(head.removed,true);
assert.equal(head.classList['sr-av-unavailable'],true);
assert.equal(head.onerror,null);
const missing=nativePortrait(999999);
assert.equal(missing.src,'/assets/original-ui/portraits/partner_avatar_999999.png');
missing.onerror();missing.onerror();assert(missing.removed);
assert(!js.includes("'/assets/ui/item_bg.png'"),'Invalid old placeholder must be removed');
assert(js.includes("'Xác Nhận'")&&js.includes("'Triệu Hồi '+n"));
console.log('PASS: original HD portrait -> original atlas -> original card, no broken icon, Vietnamese controls');
