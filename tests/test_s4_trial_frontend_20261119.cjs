'use strict';
/** GM items, bag activation and S4 expired countdown display. */
const fs=require('node:fs'),assert=require('node:assert/strict');
const read=p=>fs.readFileSync(p,'utf8');
const catalog=JSON.parse(read('web/assets/items-catalog.json'));
const admin=read('web/admin.js');
const app=read('web/app.js');
const auth=read('web/auth.js');
const css=read('web/auth.css');
const html=read('web/index.html');

for(const [i,hours] of [24,48,72,96,120].entries()){
 const id=String(990051+i),item=catalog[id];
 assert.equal(item.id,Number(id));
 assert(item.name.includes(hours+' giờ'));
 assert(item.description.toLowerCase().includes('không'),id);
 assert.equal(item.category,2);
 assert.equal(item.icon,'s4-exclusive-key');
 assert.equal(item.quality,7);
 assert.equal(item.type,1);
}
assert(admin.includes('Chìa Khóa S4 Dùng Thử • Quà Tri Ân Nạp Giá Trị Cao'));
assert(admin.includes('for(const hours of [24,48,72,96,120])'));
assert(admin.includes('const id=990050+hours/24'));
assert(admin.includes('addGift(row,1)'));
assert(admin.includes("show('mail')"));
assert(admin.includes("giftCards(body,'items')"));
assert(app.includes("original.kind==='s4_trial'"));
assert(app.includes("button.textContent='Kích Hoạt S4 • '"));
assert(app.includes("selected.kind==='s4_trial'"));
assert(app.includes("result.s4_trial.hours"));
assert(app.includes("window.GxbAuth?.refreshS4Trial?.()"));
assert(app.includes("'/assets/items-catalog.json?v=20261119-s4-trial-r1'"));
assert(app.includes("[990051,990052,990053,990054,990055].includes(Number(item?.id))"));
assert(auth.includes('s4TrialTime()'));
assert(auth.includes("'/api/s4/trial'"));
assert(auth.includes("s4Trial=data.s4_trial"));
assert(auth.includes("s4KickedReason='trial_expired'"));
assert(auth.includes("kickToServerLobby(s4Cycle,'trial_expired')"));
assert(auth.includes("session?.s4_access_expired"));
assert(auth.includes('Dùng thử còn '));
assert(auth.includes('refreshS4Trial:syncS4Trial'));
assert(auth.includes("Chọn máy chủ thường để tiếp tục chơi"));
assert(auth.includes("void syncS4Trial()"));
assert(auth.includes("performance.now()"));
assert(app.includes("['S4_LOCKED','S4_TRIAL_EXPIRED'].includes(data.code)"));
assert(css.includes('white-space:pre-line'));
for(const file of ['app.js','auth.js','auth.css'])
 assert(html.includes('/'+file+'?v=20261119-s4-trial-r1'),file);
assert(html.includes('/admin.js?v=20261119-gm-mobile-button-r4'));
console.log('PASS: GM S4 5 trial items, Bag use, timed VIP preview, expiry kick and independent clock');
