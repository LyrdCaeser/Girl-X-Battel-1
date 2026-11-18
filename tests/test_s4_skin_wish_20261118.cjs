'use strict';
/** Regression: S4 Wish MUST be original fullscreen Spine, one awarded reward
 * per native reveal, NEVER a paginated 12-card CSS slideshow.
 */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const anim=fs.readFileSync('web/summon-anim.js','utf8');
const home=fs.readFileSync('web/home-menus.js','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const style=fs.readFileSync('web/summon-anim.css','utf8');
const homeCss=fs.readFileSync('web/home-menus.css','utf8');
const begin=anim.indexOf(' async function s4RevealSequence(items,type,progress){');
const end=anim.indexOf(' async function playS4Rewards(partners,skins){',begin);
assert(begin>0&&end>begin);
const fragment=anim.slice(begin,end);
const actions=[],mounts=[];
let skipped=false;
const scope=vm.createContext({
 skipped,
 console,
 sfx:n=>actions.push(['sfx',n]),
 layer:async(base)=>{
  mounts.push(base);
  return {fig:{state:{}},done:()=>actions.push(['destroy',base])};
 },
 run:async(fig,name)=>actions.push(['spine-animation',name]),
 s4SlotChildren:()=>[],
 attachGirl:async(fig,id)=>actions.push(['goddess-image',id]),
 nativeNameStars:(fig,entry,star)=>{
  actions.push(['native-name-and-stars',entry.name,star]);
  return true;
 },
 caption:(entry)=>()=>{},
 s4AttachSkin:async(fig,entry)=>actions.push(['skin-image',entry.id]),
 s4SkinLabel:(fig,name)=>{
  actions.push(['native-skin-name',name]);
  return true;
 },
 s4Pause:async()=>{},
 s4CleanupArt:()=>{}
});
vm.runInContext(fragment,scope);
const run=vm.runInContext('s4RevealSequence',scope);
(async()=>{
 const girls=Array.from({length:104},(_,i)=>({table_id:751001+i,name:'Nữ Thần '+i,star:25}));
 const skins=Array.from({length:248},(_,i)=>({id:7001+i,name:'Trang phục '+i}));
 const counter={textContent:''};
 await run(girls,'girls',counter);
 await run(skins,'skins',counter);
 assert.equal(actions.filter(a=>a[0]==='goddess-image').length,104,'Each goddess receives its own Wish reveal');
 assert.equal(actions.filter(a=>a[0]==='skin-image').length,248,'Every skin receives its own native Wish reveal');
 assert.equal(actions.filter(a=>a[0]==='native-name-and-stars').length,104);
 assert.equal(actions.filter(a=>a[0]==='native-skin-name').length,248);
 assert.equal(actions.filter(a=>a[0]==='spine-animation'&&a[1]==='222').length,2,
  'Original gacha egg animation for each phase');
 assert.equal(actions.filter(a=>a[0]==='spine-animation'&&a[1]==='texiao10').length,352,
  'Original native goddess reveal effect repeated for each item');
 assert.deepEqual(mounts,[
  '/assets/spine/fx_ui_gacha_revision',
  '/assets/spine/fx_ui_newgirl_gaino',
  '/assets/spine/fx_ui_gacha_revision',
  '/assets/spine/fx_ui_newgirl_gaino'
 ],'Reuse only one native Spine canvas per phase to avoid Android GPU freezes');
 assert(counter.textContent.includes('248 / 248'));
 assert(!home.includes('function revealS4Skins('),'Fake 12-card Wish grid must be removed');
 assert(!homeCss.includes('.hm-s4-wish-cards'),'Fake carousel CSS must be removed');
 assert(home.includes('SummonAnim.playS4Rewards(girls,skins)'));
 assert(home.includes("'/api/s4/wish/replay'"));
 assert(home.includes('Xem Lại Wish (Không Nhận Quà Lần Nữa)'));
 assert(home.includes('WishRecorder.finishWish()'));
 assert(style.includes('.sa-s4-native-wish'));
 assert(style.includes('.sa-s4-progress'));
 assert(html.includes('summon-anim.js?v=20261118-native-wish-r1'));
 assert(html.includes('home-menus.js?v=20261118-native-wish-r1'));
 console.log('PASS: 104+248 original Wish Spine reveals, no static grid, one GPU canvas per phase, replay & recorder');
})().catch(e=>{console.error(e);process.exitCode=1;});
