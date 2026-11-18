'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const read=f=>fs.readFileSync(f,'utf8');
const auth=read('web/auth.js'),home=read('web/home-menus.js'),css=read('web/home-menus.css');
const events=read('web/events.js'),html=read('web/index.html');
assert(auth.includes("special?' · VIP 15'"));
assert(auth.includes("S4 Độc Quyền VIP 15"));
assert(home.includes("m.attachments?.__s4_exclusive_bundle__"));
assert(home.includes("filter(([id,count])=>/^[0-9]+$/.test(id)"),'Reserved keys never passed into normal reward rendering');
assert(home.includes('await SummonAnim.playS4Rewards(girls,skins)'),
 'Every Goddess and Skin must play fullscreen native Wish');
assert(!home.includes('function revealS4Skins('),
 'Fake paginated gallery is not a Wish animation');
assert(fs.readFileSync('web/summon-anim.js','utf8').includes(
 "'/assets/skins/cards/'+sid+'.webp'"),'Original skin artwork in native Spine');
assert(home.includes("celebration=result?.s4_rewards||null"));
assert(!css.includes('.hm-s4-wish-cards'));
assert(fs.readFileSync('web/summon-anim.css','utf8').includes('.sa-s4-native-wish'));
assert(events.includes("c.featured_30_days||[]"));
assert(events.includes("!cal()?.exclusive_s4"));
for(const name of ['home-menus.js?v=20261118-native-wish-r1',
 'home-menus.css?v=20261118-native-wish-r1',
 'auth.js?v=20261118-vip15-s4key-r1','events.js?v=20261118-s4-calendar-r1'])
 assert(html.includes(name),name);
console.log('PASS S4: visible VIP gate, scoped mail, native Wish gacha, 324 original skins, 30-day event calendar');
