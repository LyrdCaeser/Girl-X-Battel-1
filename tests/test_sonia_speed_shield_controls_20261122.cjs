'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const app=fs.readFileSync('web/app.js','utf8');
const battle=fs.readFileSync('web/battle-animation.js','utf8');
const css=fs.readFileSync('web/style.css','utf8');
const html=fs.readFileSync('web/index.html','utf8');
// The real functions from web/app.js are executed, not reimplemented.
const start=app.indexOf(' function paintBattleShield(unit){');
const end=app.indexOf(' const soniaCueSeen=new Set();',start);
assert(start>0&&end>start);
const ctx=vm.createContext({});
vm.runInContext(app.slice(start,end),ctx);
const u={
  shieldFill:{style:{}},
  hp:100,
  shieldValue:0,
  shieldBase:0,
  maxHp:1000
};
const buff=(table_id,name,value,hp=100)=>({table_id,name,value,hp,buffOn:2});
ctx.applyBattleShieldBuff(buff(1758017,'hpShieldByAD',300),u);
assert.equal(u.shieldValue,300);
assert.equal(u.shieldFill.style.width,'30.00%');
assert.equal(u.shieldFill.style.visibility,'visible');
ctx.applyBattleShieldBuff(buff(1758004,'hurt',-100),u);
assert.equal(u.shieldValue,200);
assert.equal(u.shieldFill.style.width,'20.00%');
ctx.applyBattleShieldBuff(buff(1758004,'hurt',-200),u);
assert.equal(u.shieldValue,0);
assert.equal(u.shieldFill.style.visibility,'hidden');
ctx.applyBattleShieldBuff(buff(1758007,'hpShieldByAD',175),u);
assert.equal(u.shieldValue,175);
ctx.applyBattleShieldBuff(buff(1536001,'clearHpShield',0),u);
assert.equal(u.shieldValue,0);
assert.equal(u.shieldFill.style.visibility,'hidden');
ctx.applyBattleShieldBuff(buff(1758017,'hpShieldByAD',320),u);
u.hp=0;ctx.paintBattleShield(u);
assert.equal(u.shieldFill.style.visibility,'hidden');
assert(app.includes("const shieldFill=node('i','shield-hp-fill')"));
assert(app.includes('bar.append(fill,shieldFill)'));
assert(app.includes('1758014:75800108'));
assert(app.includes('1758015:75800109'));
assert(app.includes('1758017:75800110'));
assert(app.includes('1758016:75800111'));
assert(app.includes('Number(buff.buffOn)!==0'));
assert(app.includes('if(buff.hp<=0){u.shieldValue=0;paintBattleShield(u);'));
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
assert(html.includes('app.js?v=20261122-sonia-four-new-status-r8'));
assert(html.includes('style.css?v=20261122-sonia-gold-shield-r5'));
assert(html.includes('battle-animation.js?v=20261122-sonia-dracula-promethea-r7'));
console.log('PASS: native Lua buffs drive real yellow shield that depletes/disappears, conditional Dracula+Promethea+ban visual cues');
