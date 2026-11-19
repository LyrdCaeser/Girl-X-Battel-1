'use strict';
/** Regression: S4 Wish has an actual full-screen animation for every
 * Goddess & skin, never the old 12-tile list or a baked GIRLS/CV strip.
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
 s4SuppressBakedGirlHeading:()=>actions.push(['hide-baked-girls']),
 attachGirl:async(fig,id)=>actions.push(['goddess-image',id]),
 nativeNameStars:(fig,entry,star)=>{
  actions.push(['native-name-and-stars',entry.name,star]);
  return true;
 },
 caption:(entry)=>()=>{},
 s4RevealSkinCinema:async(items)=>{
  actions.push(['skin-cinema',items.length]);
  items.forEach((item)=>actions.push(['skin-frame',item.id]));
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
 assert.equal(actions.filter(a=>a[0]==='goddess-image').length,104);
 assert.equal(actions.filter(a=>a[0]==='skin-frame').length,248);
 assert.equal(actions.filter(a=>a[0]==='hide-baked-girls').length,105);
 assert.equal(actions.filter(a=>a[0]==='native-name-and-stars').length,104);
 assert.equal(actions.filter(a=>a[0]==='skin-cinema').length,1);
 assert.equal(actions.filter(a=>a[0]==='spine-animation'&&a[1]==='222').length,2,
  'Original gacha egg animation should introduce both phases');
 assert.equal(actions.filter(a=>a[0]==='spine-animation'&&a[1]==='texiao10').length,104,
  'Native Goddess effect belongs to Goddesses only');
 assert.deepEqual(mounts,[
  '/assets/spine/fx_ui_gacha_revision',
  '/assets/spine/fx_ui_newgirl_gaino',
  '/assets/spine/fx_ui_gacha_revision'
 ],'No Goddess-only skeleton mounted during the skin phase');
 assert(!home.includes('function revealS4Skins('),'Old paginated gallery removed');
 assert(!homeCss.includes('.hm-s4-wish-cards'),'Fake carousel CSS removed');
 assert(home.includes('SummonAnim.playS4Rewards(girls,skins)'));
 assert(home.includes("'/api/s4/wish/replay'"));
 assert(home.includes('Xem Lại Wish (Không Nhận Quà Lần Nữa)'));
 assert(home.includes('WishRecorder.finishWish()'));
 for(const css of ('.sa-s4-skin-scene','.sa-s4-skin-portrait',
                   '.gxb-s4-cinematic .auth-s4-countdown',
                   '.gxb-s4-cinematic .gxb-wish-record-widget')){
   assert(style.includes(css),css);
 }
 assert(style.includes('.gxb-s4-cinematic .sa-s4-progress'));
 assert(style.includes('.gxb-s4-cinematic .sa-s4-instruction'));
 assert(style.includes('width:92%;height:72%'),
  'Mobile portrait must be large, not a natural 208px card in the center');
 assert(style.includes('object-fit:contain;object-position:center center'),
  'Never crop the skin portrait for video');
 assert(style.includes('width:73%;height:79%'),
  'PC layout must remain separate from mobile');
 assert(style.includes('.sa-s4-skin-portrait[hidden]'),
  'Graceful fallback for missing art must not reveal a broken image');
 assert(anim.includes("document.documentElement.classList.add('gxb-s4-cinematic')"));
 assert(anim.includes("document.documentElement.classList.remove('gxb-s4-cinematic')"));
 assert(html.includes('summon-anim.js?v=20261118-s4-cinema-clean-r1'));
 assert(html.includes('home-menus.js?v=20261119-s4-gm-trial-gift-r1'));
 console.log('PASS: 104+248 Wish cinematic frames, original Gacha FX, no baked skin labels or film-blocking HUD');
})().catch(e=>{console.error(e);process.exitCode=1;});
