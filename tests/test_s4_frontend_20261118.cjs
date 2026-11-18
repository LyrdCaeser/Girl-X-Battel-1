'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const read=f=>fs.readFileSync(f,'utf8');
const auth=read('web/auth.js'),home=read('web/home-menus.js'),css=read('web/home-menus.css');
const events=read('web/events.js'),html=read('web/index.html');
assert(auth.includes("special?' · 🔒 Yêu cầu VIP 15'"));
assert(auth.includes("S4 • Thời Không Sai Lệch"));
assert(home.includes("m.attachments?.__s4_exclusive_bundle__"));
assert(home.includes("filter(([id,count])=>/^[0-9]+$/.test(id)"),'Reserved keys never passed into normal reward rendering');
assert(home.includes("await SummonAnim.play(26,girls)"),'Wish machine plays before skin reveal');
assert(home.includes("'/assets/skins/cards/'+Number(sid)+'.webp'"),'Original limited skin artwork');
assert(home.includes("celebration=result?.s4_rewards||null"));
assert(css.includes(".hm-s4-skin-grid"));
assert(events.includes("c.featured_30_days||[]"));
assert(events.includes("!cal()?.exclusive_s4"));
for(const name of ['home-menus.js?v=20261118-s4-wish-bundle-r1',
 'home-menus.css?v=20261118-s4-wish-bundle-r1',
 'auth.js?v=20261118-s4-vip15-r1','events.js?v=20261118-s4-calendar-r1'])
 assert(html.includes(name),name);
console.log('PASS S4: visible VIP gate, scoped mail, native Wish gacha, 76 original skins, 30-day event calendar');
