'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const battle=fs.readFileSync('web/battle-animation.js','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const app=fs.readFileSync('web/app.js','utf8');
const skills=[75800100,75800101,75800102,75800103,75800104];
const clips=[
  'lianhua_hurt01',
  'sonia_chaos_orb',
  'sonia_chaos_siphon',
  'sonia_chaos_guard',
  'sonia_chaos_collapse'
];
assert(!fs.existsSync('web/sonia-battle-vfx.js'),'hand-painted Canvas engine removed');
assert(!html.includes('sonia-battle-vfx.js'),'second canvas no longer loaded');
assert(html.includes('battle-animation.js?v=20261122-sonia-five-daggers-r8'));
assert(battle.includes('const soniaSlots=new Set('));
assert(battle.includes("at('lianhua_hurt01',.72,'target',1.6,.96)"));
for(const res of ['lianhua_hurt01','sonia_chaos_orb','sonia_chaos_siphon','sonia_chaos_guard','sonia_chaos_collapse'])assert(battle.includes("'"+res+"'"));
assert(battle.includes(".map(name=>fxLoad(name))"));
assert(battle.includes("await Promise.race([preload,new Promise(resolve=>setTimeout(resolve,2800))])"));

assert(battle.includes('if(soniaNativeFx(skillId,caster,targets))return;'));
assert(battle.includes("at('sonia_chaos_guard',.72,'caster-front',1.35,1,0,'texiao02')"));
assert(battle.includes("place==='caster-front'?figure.y+3:py-1"));
assert(battle.includes("void spawn(res,clip,scale,px,py,flip,z,"));
assert(battle.includes("at('sonia_chaos_orb',.56,'target',2.1,.96)"));
assert(battle.includes("at('sonia_chaos_collapse',.76,'target',1.05,1)"));

assert(battle.includes("new PIXI.spine.Spine(data)"));
assert(!battle.includes('const fxLite=document.documentElement.classList.contains'));
assert(!battle.includes('if(!fxLite)at('));
assert(battle.includes('for(const timer of fxTimers){clearTimeout(timer);clearInterval(timer);}'));
assert(battle.includes('for(const f of live){'));
assert(battle.includes('f.state.timeScale=value*(fxConfigs.get(f)||1)'));
assert(app.includes('battleAnimation?.timing?.(displaySkillId,frame.pos)'));
assert(app.includes('soniaTiming.impact/battleSpeed'));
assert(!battle.includes('SoniaBattleVFX'));
for(const id of skills)assert(battle.includes(id+':{impact:'),'native timeline for '+id);
for(const name of clips){
 assert(battle.includes("'"+name+"'"),'Spine resource registered: '+name);
 const dir=path.join('web','assets','battle-fx',name);
 const data=JSON.parse(fs.readFileSync(path.join(dir,'model.json'),'utf8'));
 assert.equal(data.skeleton.spine,'3.6.37');
 assert(data.animations.texiao01,'native animation required: '+name);
 assert(fs.existsSync(path.join(dir,'model.atlas')));
 const imageNames=fs.readdirSync(dir).filter(n=>n.endsWith('.webp'));
 assert(imageNames.length>=1,'real game textures: '+name);
}
assert(!html.includes('<canvas class="sonia-'),'no added HTML canvas in app');
console.log('PASS: Sonia has one recolored Spine 3.6.37 visual from each of 4 goddesses, preserved basic hit, no Canvas/compositing');
