'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const app=fs.readFileSync('web/app.js','utf8');
const battle=fs.readFileSync('web/battle-animation.js','utf8');
const css=fs.readFileSync('web/style.css','utf8');
const html=fs.readFileSync('web/index.html','utf8');
// The real functions from web/app.js are executed, not reimplemented.
const start=app.indexOf(' function paintBattleShield(unit){');
const end=app.indexOf(' const soniaCueSeen=new Set(),',start);
assert(start>0&&end>start);
const ctx=vm.createContext({});
vm.runInContext(app.slice(start,end),ctx);
const u={shieldFill:{style:{}},hp:100,shieldValue:0,shieldBase:0,
  shieldPercent:null,maxHp:1000};
ctx.applyBattleShieldBuff({
  name:'hpShield',buffOn:5,shield:16,shieldCost:2112,value:0
},u);
assert.equal(u.shieldPercent,16);
assert.equal(u.shieldValue,2112);
assert.equal(u.shieldFill.style.width,'16.00%');
assert.equal(u.shieldFill.style.visibility,'visible');
ctx.applyBattleShieldBuff({
 name:'hpShield',buffOn:5,shield:7,shieldCost:900,value:0
},u);
assert.equal(u.shieldFill.style.width,'7.00%');
ctx.applyBattleShieldBuff({
 name:'hpShield',buffOn:5,shield:0,shieldCost:0,value:0
},u);
assert.equal(u.shieldValue,0);
assert.equal(u.shieldFill.style.visibility,'hidden');
ctx.applyBattleShieldBuff({name:'hpShield',buffOn:5,shield:24,shieldCost:3000,value:0},u);
u.hp=0;ctx.paintBattleShield(u);
assert.equal(u.shieldFill.style.visibility,'hidden');
assert(app.includes("const shieldFill=node('i','shield-hp-fill')"));
assert(app.includes('bar.append(fill,shieldFill)'));
assert(app.includes('1758014:75800108'));
assert(app.includes('1758015:75800109'));
assert(app.includes('1758017:75800110'));
assert(app.includes('1758016:75800111'));
assert(app.includes('Number(buff.buffOn)!==3'));
assert(app.includes('if(buff.hp<=0){u.shieldValue=0;u.shieldPercent=0;paintBattleShield(u);'));
assert(css.includes('.battlefield .unit .hp>i.shield-hp-fill'));
assert(css.includes('linear-gradient(180deg,#fff8b4'));
assert(css.includes('.battlefield .unit.dead .hp>i.shield-hp-fill'));
for(const [id,resource] of [
  [75800108,'spdegula_hurt01'],[75800109,'puluomixiusi_hurt02'],
  [75800110,'sonia_chaos_guard'],[75800111,'sonia_chaos_collapse']]){
 assert(battle.includes(id+':{impact:'),'missing FX timeline '+id);
 assert(battle.includes("at('"+resource+"'"),'missing original FX '+resource);
 const d=JSON.parse(fs.readFileSync('web/assets/battle-fx/'+resource+'/model.json','utf8'));
 assert.equal(d.skeleton.spine,'3.6.37');
 assert(fs.existsSync('web/assets/battle-fx/'+resource+'/model.atlas'));
}
assert(html.includes('app.js?v=20261122-skill-click-r10'));
assert(html.includes('style.css?v=20261122-sonia-gold-shield-r5'));
assert(html.includes('battle-animation.js?v=20261122-sonia-five-daggers-r8'));
console.log('PASS: native Lua buffs drive real yellow shield that depletes/disappears, conditional Dracula+Promethea+ban visual cues');
