'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict');
const css=fs.readFileSync('web/style.css','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const i=css.indexOf('/* Narrower original summon-machine surround');
assert(i>0);
const part=css.slice(i);
assert(part.includes('--summon-rim:clamp(8px,3.1vw,5mm)'));
assert(part.includes('background-size:calc(100% + 22px) 100%'));
assert(part.includes('background-size:calc(100% + 30px) 100%'));
assert(part.includes('border-width:2px'));
assert(part.includes('html.gxb-mobile #app-frame #capsule-view'),'Desktop styles must stay independent');
assert(html.includes('style.css?v=20261117-narrow-original-border-r2'));
assert(css.includes("url('/assets/capsule/advanced-panel.png')"),'native art must not change');
assert(css.includes("url('/assets/wish/wish_capsule_summon_bg.png')")===false ||
       fs.readFileSync('web/wish.css','utf8').includes("url('/assets/wish/wish_capsule_summon_bg.png')"));
console.log('PASS: original panel art retained, mobile rim capped at 5mm, desktop untouched');
