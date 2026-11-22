'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const app=fs.readFileSync('web/app.js','utf8');
const anim=fs.readFileSync('web/battle-animation.js','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const status=JSON.parse(fs.readFileSync('web/assets/spine/battle-status.json','utf8'));
for(const name of ['spdSteal','seal','stunH','hpShield','hpShieldByAD','hpDotPoison','dotPoison']){
 assert(status[name],'Native status icon definition missing: '+name);
 for(const style of ['positive','negative']){
  const filename='web/assets/spine/status-icons/'+status[name][style]+'.png';
  assert(fs.existsSync(filename),'Missing GXB3 icon: '+filename);
 }
 assert(status[name].label,'No in-game Vietnamese name for '+name);
}
const start=anim.indexOf(' function change(active,buff){');
const end=anim.indexOf(' async function create(units)',start);
assert(start>0&&end>start);
const ctx=vm.createContext({});
vm.runInContext(anim.slice(start,end),ctx);
const active=[];
ctx.change(active,{name:'spdSteal',table_id:1758014,buffOn:1,value:-40});
ctx.change(active,{name:'hpDotPoison',table_id:1758019,buffOn:2,value:-2});
assert.equal(active.map(b=>b.name).join(','),'spdSteal,hpDotPoison');
ctx.change(active,{name:'spdSteal',table_id:1758014,buffOn:3,value:-40});
assert.equal(active.map(b=>b.name).join(','),'hpDotPoison');
ctx.change(active,{name:'hpShield',buffOn:5,shield:16,value:0});
assert(active.some(b=>b.name==='hpShield'));
ctx.change(active,{name:'hpShield',buffOn:5,shield:0,value:0});
assert(!active.some(b=>b.name==='hpShield'));
ctx.change(active,{name:'hpDotPoison',table_id:1758019,buffOn:4,value:-2});
assert.equal(active.length,0);
assert(app.includes('soniaPoisonDue=new Map()'));
assert(app.includes('5000/Math.max(1,battleSpeed)'));
assert(app.includes('1758018&&Number(buff.pos)!==sourcePos'));
assert(app.includes('75800112,soniaKnifeTargets.slice(0,5)'));
assert(anim.includes('case 75800112:'));
assert(anim.includes('case 75800113:'));
assert(anim.includes('new PIXI.Graphics()'));
assert(anim.includes("spawn('meiyingdu_hurt02','texiao01'"));
assert(anim.includes('index*105/Math.max(.25,rate)'));
assert(anim.includes('seen.size>=5'));
assert(anim.includes('clearInterval(timer)'));
assert(html.includes('app.js?v=20261122-sonia-poison-real-r9'));
assert(html.includes('battle-animation.js?v=20261122-sonia-five-daggers-r8'));
assert(html.includes('wish.js?v=20261122-sonia-poison-skilldesc-r8'));
const j=JSON.parse(fs.readFileSync('web/assets/chaos/lyr_sonia.json','utf8'));
assert.equal(j.skills.length,4);
for(const desc of j.skills[0].levels){
 for(const txt of ['Phóng Độc','5 dao','65%','2% HP','5 giây']){
  assert(desc.includes(txt),'Missing description: '+txt);
 }
}
console.log('PASS native status modes apply/tick/remove; shield reads Lua; five poison knives and 5-second presentation interval');
