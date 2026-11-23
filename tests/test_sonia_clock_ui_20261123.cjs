'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const ui=fs.readFileSync('web/events.js','utf8');
const style=fs.readFileSync('web/events.css','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const grants=fs.readFileSync('gxb2/sonia_festival.py','utf8');
const target='Vòng Quay Kim Đồng Hồ';
assert(!ui.includes('Vòng Quay Mảnh'),'Obsolete title must be absent from the event page');
assert(ui.includes("['shards',"+JSON.stringify(target).replace(/"/g,"'")+']') || ui.includes("'shards','"+target+"'"));
assert(ui.includes("shards:'"+target+"'"));
assert(ui.includes("'shards'?' sf-clock-tab'")||ui.includes("id==='shards'?' sf-clock-tab'"));
assert(ui.includes('/assets/events/icon_activity_clock.png'));
assert(ui.includes("const section=el('div','sf-banner'+(kind==='shards'?' sf-clock-banner':''));"));
assert(ui.includes("parent.append(soniaClockFace(w.odds));"));
assert(ui.includes("if(kind!=='shards')parent.append(rows);"),
  'Original Star and Mission event tables must not be altered');
assert(ui.includes("const dial=el('div','sf-clock-dial'"));
assert(ui.includes("const marks=el('div','sf-clock-marks')"));
assert(ui.includes('for(let i=0;i<12;i++)'));
assert(ui.includes("const item=el('div','sf-clock-prize'"));
assert(ui.includes("const hand=el('div','sf-clock-hand')"));
assert(ui.includes("const center=el('div','sf-clock-center')"));
assert(ui.includes("const crown=el('div','sf-clock-crown')"));
assert(!ui.includes('sonia_clock_ornate_20261123.webp'),
  'Reverted clock must not use the owner image any more');
assert(!ui.includes('sf-clock-ornate-dial'));
assert(ui.includes('for(let i=0;i<odds.length;i++)'));
assert(ui.includes('w.spins+count>w.cap'));
assert(ui.includes("Number(state.items['2']||0)<price"));
assert(ui.includes("send({action:'sonia_spin',count})"));
assert(ui.includes("if(pending)return;"));
assert(ui.includes("soniaClockSpinning=true"));
assert(ui.includes("if(request.action==='sonia_spin')"));
assert(ui.includes("soniaDraws=Array.isArray(r.draws)?r.draws:[]"));
assert(ui.includes("odds.findIndex(o=>o.label===soniaDraws[soniaDraws.length-1]?.name)"));
assert(!ui.includes("Math.random"),'Frontend must never roll prizes locally');
assert(ui.includes("const id=Object.keys(reward.awards||{})[0]"));
assert(ui.includes("r.chance.toLocaleString('vi-VN')+'%'"));
assert(ui.includes('Kim đồng hồ minh họa các phần quà'));
for(const selector of ['.sf-clock-stage','.sf-clock-dial','.sf-clock-marks',
 '.sf-clock-prize','.sf-clock-hand','.sf-clock-center','.sf-clock-crown',
 '.sf-clock-progress','.sf-clock-spin-btn',
 '.sf-clock-odds-card','.sf-clock-result-list','.sf-clock-banner','.sf-clock-tab']){
 assert(style.includes(selector), 'Missing native-game styled UI '+selector);
}
assert(style.includes('/assets/detail/sheet/blue_btn_65_65.png'),
 'The official blue game button must be retained');
assert(style.includes('/assets/events/activity_bg03.png'),
 'The original ActivityWindow banner background must be retained');
assert(style.includes('@media(prefers-reduced-motion:reduce)'),
 'Reduced-motion preferences must be supported');
for(const version of [
 '/events.js?v=20261123-sonia-classic-polish-r10',
 '/events.css?v=20261123-sonia-classic-polish-r10']){
 assert(html.includes(version),'Cache-busting build must use updated wheel resources');
}
assert(grants.includes('SPIN_COST={1:1200,5:5800}'),'Updated server-verified x1/x5 prices are required');
assert(grants.includes('SPIN_CAP=200'),'No increased draw cap');
assert(grants.includes('(300, {SHARD:2}'),'3% fragments rate preserved');
assert(grants.includes('(20, {SHARD:5}'),'0.2% rare fragment rate preserved');
assert(grants.includes('hit=int(rng(10000))'),'Only server draws results');
assert(grants.includes("'awards':awards,'draws':draws"),'Result must originate on server');
console.log('PASS: Clock-themed original ActivityWindow, native item rewards and buttons, authenticated spins and original economy.');
