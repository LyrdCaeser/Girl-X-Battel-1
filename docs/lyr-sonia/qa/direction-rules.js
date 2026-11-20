/* Lyr Sonia six-view facing contract: pure, tested; NO fake movement or flipping. */
(function(root,factory){
 const rules=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=rules;
 root.LyrSoniaDirectionRules=rules;
})(typeof window!=='undefined'?window:globalThis,function(){
 'use strict';
 const VIEWS=Object.freeze([
  Object.freeze({id:'front',angle:0,label:'Chính diện'}),
  Object.freeze({id:'three_quarter_right',angle:45,label:'Góc ¾ phải'}),
  Object.freeze({id:'right_profile',angle:90,label:'Nghiêng phải'}),
  Object.freeze({id:'back',angle:180,label:'Phía sau'}),
  Object.freeze({id:'left_profile',angle:270,label:'Nghiêng trái'}),
  Object.freeze({id:'three_quarter_left',angle:315,label:'Góc ¾ trái'})
 ]);
 const ACTIONS=Object.freeze(['idle','attack','skill','hurt','dead']);
 const DEATH_LENGTH_MS=1250;
 function normalize(degrees){
  if(!Number.isFinite(degrees))throw Error('Invalid facing angle');
  return ((degrees%360)+360)%360;
 }
 function facingForAngle(degrees){
  const target=normalize(degrees);
  return VIEWS.reduce((best,next)=>{
   const nextGap=Math.abs((next.angle-target+540)%360-180);
   const bestGap=Math.abs((best.angle-target+540)%360-180);
   return nextGap<bestGap?next:best
  }).id;
 }
 function isCombatClip(clip){return ACTIONS.includes(clip)}
 function hasAnimatedRig(view,clip){
  if(!VIEWS.some(v=>v.id===view)||!isCombatClip(clip))return false;
  // Only front has verified animated source. Do not present a static side view as combat motion.
  return view==='front';
 }
 function stateAt(view,clip,ms,deathMs=DEATH_LENGTH_MS){
  if(!VIEWS.some(v=>v.id===view))throw Error('Unknown original 6-view artwork');
  if(!isCombatClip(clip))throw Error('No Move/Run in stationary GXB 3 combat');
  if(!Number.isFinite(ms)||ms<0)throw Error('Invalid timeline');
  if(!Number.isFinite(deathMs)||deathMs<=0)throw Error('Invalid dead duration');
  return Object.freeze({
   view,clip,stationary:true,rigReady:hasAnimatedRig(view,clip),
   visible:clip!=='dead'||ms<deathMs,
   removeAfterDead:clip==='dead'&&ms>=deathMs,
   awaitDirectionalArt:view!=='front'
  });
 }
 return Object.freeze({VIEWS,ACTIONS,DEATH_LENGTH_MS,normalize,facingForAngle,isCombatClip,hasAnimatedRig,stateAt});
});
