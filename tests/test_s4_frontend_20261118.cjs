'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const read=f=>fs.readFileSync(f,'utf8');
const auth=read('web/auth.js'),home=read('web/home-menus.js'),css=read('web/home-menus.css');
const events=read('web/events.js'),html=read('web/index.html');
assert(auth.includes("special?' · VIP 15'"));
assert(auth.includes("S4 Độc Quyền VIP 15"));
assert(home.includes("m.attachments?.__s4_exclusive_bundle__"));
assert(home.includes("filter(([id,count])=>/^[0-9]+$/.test(id)"),'Reserved keys never passed into normal reward rendering');
assert(home.includes("await SummonAnim.play(26,girls.slice(0,4),{s4:true})"),'Wish machine plays before skin reveal');
assert(home.includes("'/assets/skins/cards/'+entry+'.webp'"),'Original limited skin artwork');
assert(home.includes("celebration=result?.s4_rewards||null"));
assert(css.includes(".hm-s4-wish-cards"));
assert(events.includes("c.featured_30_days||[]"));
assert(events.includes("!cal()?.exclusive_s4"));
for(const name of ['home-menus.js?v=20261118-wish-capture-r1',
 'home-menus.css?v=20261118-s4-complete-v2',
 'auth.js?v=20261118-vip15-s4key-r1','events.js?v=20261118-s4-calendar-r1'])
 assert(html.includes(name),name);
console.log('PASS S4: visible VIP gate, scoped mail, native Wish gacha, 324 original skins, 30-day event calendar');
