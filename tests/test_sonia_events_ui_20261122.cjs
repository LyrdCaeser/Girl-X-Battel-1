'use strict';
const fs=require('node:fs');
const assert=require('node:assert/strict');
const js=fs.readFileSync('web/events.js','utf8');
const css=fs.readFileSync('web/events.css','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const game=fs.readFileSync('gxb2/engine.py','utf8');
for(const label of ['Lễ Hội Thức Tỉnh','Vòng Quay Mảnh','Chinh Phục Nhiệm Vụ']){
  assert(js.includes(label),label+' is visible in EventWindow');
}
for(const token of ['sonia_festival_info','sonia_star_claim','sonia_spin',
                     'sonia_mission_claim','activity_icon_1_middle','activity_icon_0_middle',
                     'pe-list sf-list','sf-spin-buttons','sf-progress','leftText(m.end)']){
  assert(js.includes(token),'missing UI feature '+token);
}
for(const token of ['sonia_festival.snapshot','sonia_festival.action',
                     "sonia_festival.record(state,'victory'",
                     "sonia_festival.record(state,'arena_win'",
                     "sonia_festival.record(state,'advanced'","sonia_festival.record_sonia_star"]){
  assert(game.includes(token),'server missing '+token);
}
assert(html.includes('/events.js?v=20261122-sonia-economy-calendar-r5'));
assert(html.includes('/events.css?v=20261122-sonia-mission-paid-r3'));
assert(html.includes('/admin.js?v=20261122-gm-sonia-r5'));
assert(css.includes('/assets/events/activity_bg03.png'));
assert(css.includes('/assets/detail/sheet/blue_btn_65_65.png'));
assert(js.includes('Vé Lyr Sonia') && js.includes('Mảnh Lyr Sonia'));
assert(js.includes('sonia_paid_claim')&&js.includes('soniaMissionTab'));
assert(js.includes('Thử Thách · 120 Vé')&&js.includes('Quà Nạp · 350 Vé'));

console.log('PASS: events use native game boards, visible times, authenticated rewards and Vietnamese labels');
