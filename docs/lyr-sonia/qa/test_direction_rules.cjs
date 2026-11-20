const assert=require('node:assert/strict');
const f=require('./direction-rules.js');
assert.equal(f.VIEWS.length,6);assert.equal(new Set(f.VIEWS.map(x=>x.id)).size,6);
for(const v of f.VIEWS){assert.equal(f.facingForAngle(v.angle),v.id);assert.equal(f.facingForAngle(v.angle+360),v.id)}
for(const [angle,id] of [[-1,'front'],[22,'front'],[23,'three_quarter_right'],[46,'three_quarter_right'],[91,'right_profile'],[179,'back'],[269,'left_profile'],[314,'three_quarter_left'],[359,'front']])
 assert.equal(f.facingForAngle(angle),id,angle);
assert.deepEqual(f.ACTIONS,['idle','attack','skill','hurt','dead']);
for(const clip of f.ACTIONS){
 assert(f.hasAnimatedRig('front',clip));
 for(const v of f.VIEWS.slice(1)){assert(!f.hasAnimatedRig(v.id,clip))}
}
assert.throws(()=>f.stateAt('front','move',0),/No Move/);
assert.throws(()=>f.stateAt('front','run',0),/No Move/);
const deadBefore=f.stateAt('front','dead',1240),deadAfter=f.stateAt('front','dead',1250);
assert(deadBefore.visible);assert(!deadAfter.visible);assert(deadAfter.removeAfterDead);assert(deadAfter.stationary);
assert.equal(f.stateAt('front','skill',1120).visible,true);
assert.equal(f.stateAt('back','idle',100).awaitDirectionalArt,true);
console.log('PASS Lyr Sonia: 6 true directions, 5 stationary clips, frontend rig gating, death vanishes, 4 action clips have same facing');
