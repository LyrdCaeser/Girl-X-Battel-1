'use strict';
// Compact production UI guard: first-use discount, x1/x5 prices, no local RNG.
const assert=require('node:assert/strict'),fs=require('node:fs');
const js=fs.readFileSync('web/events.js','utf8');
const css=fs.readFileSync('web/events.css','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const server=fs.readFileSync('gxb2/sonia_festival.py','utf8');
for(const t of [
 "soniaDiscountSpinning", "soniaDiscountOffer(first)",
 "first=w.first_discount||{}", "if(first.eligible||soniaDiscountSpinning)",
 "id==='shards'&&!pending&&state.sonia_festival_info?.wheel?.first_discount?.needs_draw",
 "send({action:'sonia_discount_draw'})",
 "const dial=el('div','sf-sale-dial'",
 "const center=el('div','sf-sale-value')",
 "soniaDiscountSpinning?'✦':first.percent?fmt(first.percent)+'%':'?'",
 "r.discount_percent", "soniaDiscountSpinning=false",
 "for(const count of [1,5])", "const price=Number(first.prices?.[count]??w.costs[count]);",
 "price===0?'✧ Miễn phí'", "first.eligible&&first.percent",
 "w.spins+count>w.cap", "Number(state.items['2']||0)<price",
 "!!first.needs_draw", "b.disabled=pending",
 "send({action:'sonia_spin',count})",
 "if(pending)return;", "Array.isArray(r.draws)?r.draws:[]"
]) assert(js.includes(t),'Missing discount UI flow: '+t);
for(const s of [
 '.sf-clock-welcome','.sf-sale-dial','.sf-sale-needle',
 '.sf-sale-value','.sf-sale-notice','.sf-sale-retry','.sf-clock-discount',
 'sf-discount-roll','@media(prefers-reduced-motion:reduce)'
])assert(css.includes(s),'Missing discount visuals: '+s);
assert(!js.includes('Math.random'),'Discount must never be randomized by a mobile browser');
assert(html.includes('events.js?v=20261123-sonia-classic-polish-r10'));
assert(html.includes('events.css?v=20261123-sonia-classic-polish-r10'));
assert(server.includes('SPIN_COST={1:1200,5:5800}'));
assert(server.includes('if verb==\'sonia_discount_draw\':'));
assert(server.includes('draw=int(generator(100))'));
assert(server.includes("s['clock_discount_pct']=draw+1"));
assert(server.includes("s['clock_discount_used']=True"));
assert(server.includes("price=discount['prices'][str(count)]"));
assert(server.includes("'discount_percent':discount['percent']"));
assert(server.includes("def first_discount(state):"));
assert(server.includes("if discount['needs_draw']:"));
console.log('PASS: one free auto discount draw 1-100%, persistent first-time state, 0-gem 100% case and x1/x5 purchase UI.');
