'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict');
const js=fs.readFileSync('web/wish.js','utf8');
const css=fs.readFileSync('web/wish.css','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const events=fs.readFileSync('web/events.js','utf8');
const server=fs.readFileSync('server.py','utf8');
for(const category of ['regular','advanced','wish','sonia']){
  assert(js.includes("oddsButton('"+category+"')"),category+' has clickable ≡');
}
assert(js.includes("api('/api/summon/rates')"));
assert(js.includes('wc-odds-row'));
assert(js.includes('Bảo hiểm đầu tiên:'));
assert(js.includes('95% Lyr Sonia · 5% Nữ Thần 5★ khác'));
assert(css.includes('.wc-odds-window .wc-odds-list'));
assert(server.includes("if path == '/api/summon/rates':"));
assert(events.includes('Thử Thách · 120 Vé'));
assert(events.includes('Quà Nạp · 350 Vé'));
assert(events.includes('sonia_paid_claim'));
assert(html.includes('wish.js?v=20261122-live-wish-odds-r5'));
assert(html.includes('events.js?v=20261122-sonia-visual-tickets-r6'));
console.log('PASS: all four Wish odds buttons, live rate request, pity details and paid/free mission tabs');
