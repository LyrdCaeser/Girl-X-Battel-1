// Browser-free regression tests for lobby selection and real PvP result rendering.
// No HTTP, gameplay, database or player state is accessed.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ROOT = path.resolve(__dirname, '..');

class Element {
  constructor(tag = 'div') {
    this.tagName = tag.toLowerCase();
    this.children = [];
    this.parentElement = null;
    this.className = '';
    this.id = '';
    this.textContent = '';
    this.hidden = false;
    this.classList = {toggle: () => {}, add: () => {}, remove: () => {}};
  }
  append(...nodes) {
    for (const child of nodes) {
      this.children.push(child);
      if (child && typeof child === 'object') child.parentElement = this;
    }
  }
  appendChild(node) {this.append(node);}
  replaceChildren(...nodes) {this.children = [];this.append(...nodes);}
  setAttribute(name, value) {this[name] = value;}
  addEventListener(event, fn) {this['on' + event] = fn;}
  remove() {
    if (this.parentElement) {
      this.parentElement.children = this.parentElement.children.filter(x => x !== this);
      this.parentElement = null;
    }
  }
  descendants() {
    const all = [];
    for (const child of this.children) {
      all.push(child);
      if (child && typeof child.descendants === 'function') all.push(...child.descendants());
    }
    return all;
  }
  querySelector(selector) {
    const match = n => selector.startsWith('#')
      ? n.id === selector.slice(1)
      : selector.startsWith('.') ? n.className.split(' ').includes(selector.slice(1)) : false;
    return this.descendants().find(match) || null;
  }
  querySelectorAll() {return [];}
}

function testLobby() {
  const stage = new Element('div');
  const document = {
    readyState: 'loading',
    querySelector: selector => selector === '#home-view .home-stage' ? stage : null,
    createElement: tag => new Element(tag),
    addEventListener: () => {},
  };
  const ctx = vm.createContext({document, window: {}, homeHeroIndex: 0});
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'web/lobby-dialogue.js'), 'utf8'), ctx);
  const dialogue = vm.runInContext('LobbyDialogue', ctx);
  dialogue.sync(43001);
  dialogue.sync(42001);
  dialogue.sync(41001);
  assert.equal(stage.children.length, 0, 'do not cover original MainWindow artwork with an invented speech box');
  assert.match(dialogue.translateQuote(43001, ''), /Thượng Đế/);
  assert.match(dialogue.translateQuote(42001, ''), /thao tác/);
  assert.match(dialogue.translateQuote(41001, ''), /xác sống/);
  console.log('PASS | lobby: original artwork unobstructed; authentic quotes in character details');
}

async function testPvpResult() {
  const document = {
    body: new Element('body'),
    createElement: tag => new Element(tag),
    addEventListener: () => {},
  };
  const notices = [];
  const match = {
    id: 'PVP-TEST', mode: 'arena', status: 'active',
    player_a: 'U1', player_b: 'U2', name_a: 'A', name_b: 'B',
    power_a: 1000, power_b: 1100,
  };
  const api = async (url) => {
    if (url.startsWith('/api/pvp/status')) {
      return {pvp: {status: 'matched', match}, rating_board: [], history: []};
    }
    if (url === '/api/pvp/match/heartbeat') {
      return {match: {status: 'active'}, peers: []};
    }
    if (url === '/api/pvp/match/battle') {
      return {result: {
        id: 'PVP-TEST', player_a: 'U1', winner_uid: 'U1',
        rating_delta_a: 12, battle_report: {total_round: 3},
      }};
    }
    throw Error('Unexpected API request: ' + url);
  };
  const window = {};
  const ctx = vm.createContext({
    window, document, api, state: {uid: 'U1', server_id: 'S1'},
    GirlUI: {notice: message => notices.push(message)},
    setInterval: () => 1, clearInterval: () => {},
  });
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'web/online-hub.js'), 'utf8'), ctx);
  await window.GxbOnline.open('pvp');
  const fight = document.body.descendants().find(n => n.className.includes('online-fight'));
  assert.ok(fight, 'real PvP fight button must be present');
  await fight.onclick();
  const result = document.body.descendants().find(n => n.className.includes('online-result'));
  assert.ok(result, 'PvP must render result without an undefined timer ReferenceError');
  assert.equal(notices.length, 0, 'no JavaScript error should be shown to players');
  assert.ok(result.descendants().some(n => n.textContent === 'Rounds: 3'));
  window.GxbOnline.close();
  console.log('PASS | PvP: server result renders without undefined timer');
}

function testBattleScale() {
  const ctx = vm.createContext({});
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'web/battle-animation.js'), 'utf8'), ctx);
  const fit = vm.runInContext('ChibiBattle.fitScaleForBounds', ctx);
  for (const box of [
    {width: 720, height: 320}, // wide character skin
    {width: 280, height: 950}, // tall skin
    {width: 110, height: 125}, // native small-scale chibi
    {width: 350, height: 470},
  ]) {
    const scale = fit(box);
    assert.ok(scale > 0 && Number.isFinite(scale), 'all Spine skin sizes need a finite scale');
    assert.ok(box.width * scale <= 320.001, 'regular fighter cannot overflow formation width');
    assert.ok(box.height * scale <= 330.001, 'regular fighter cannot overflow formation height');
  }
  // Regression: wide archived rigs should no longer shrink to a 250px cap.
  const oldWideSize = 250;
  const wide = {width: 468, height: 380};
  assert.ok(wide.width * fit(wide) > oldWideSize,
    'wide models regain size while respecting portrait footprint');
  const alreadyGood = {width:193, height:289};
  const unchanged = Math.min(2.6,250/alreadyGood.width,285/alreadyGood.height);
  assert.ok(Math.abs(fit(alreadyGood)-unchanged)<1e-9,
    'normal-sized fighters must keep their earlier size');
  const face = vm.runInContext('ChibiBattle.modelFacing', ctx);
  const leftNative = {width: 240, bones: [
    {name:'Pattack01', x:-110},{name:'Pattack02',x:-85},{name:'root',x:0},
  ]};
  const rightNative = {width: 240, bones: [
    {name:'Pattack01', x:160},{name:'Pattack02',x:190},
  ]};
  assert.equal(face(leftNative,{x:-75,width:220}),-1,
    'strongly leftward attack origins need native-left sprite orientation');
  assert.equal(face(rightNative,{x:-75,width:220}),1,
    'native-right models keep their original orientation');
  assert.equal(face({width:240,bones:[{name:'Pattack01',x:-80}]},{x:-75,width:220}),1,
    'one uncertain bone must not flip the entire character');
  assert.equal(face(rightNative,{x:-75,width:220},{facing:'left'}),-1,
    'asset-specific facing can override ambiguous skeletons');
  assert.ok(fit({width: 110, height: 125}) > 1.15,
    'small native models are sized consistently rather than stuck at the old 1.15 scale cap');
  const boss = {width: 600, height: 1100};
  const sBoss = fit(boss, {boss:true, bossScene:true, bossScale:2});
  assert.ok(boss.width * sBoss <= 760.001 && boss.height * sBoss <= 850.001,
    'boss keeps its special layout but cannot cover the portrait arena');
  const css = fs.readFileSync(path.join(ROOT, 'web/mobile-layout.css'), 'utf8');
  assert.match(css, /#arena:not\(\[hidden\]\) \.battlefield/);
  assert.match(css, /#event-arena \.battlefield/);
  assert.match(css, /aspect-ratio:9\/16!important/);
  console.log('PASS | battle: native Spine bounds, facing and portrait viewport verified');
}

function testNephilimBattleModels() {
  const catalogue = JSON.parse(fs.readFileSync(path.join(ROOT, 'web/assets/chibis/catalog.json'), 'utf8'));
  const ids = ['56006','656016','756006','110050','1000040','2000029',
    '7119','7125','7133','7193','7209'];
  const ctx = vm.createContext({});
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'web/battle-animation.js'), 'utf8'), ctx);
  const scale = vm.runInContext('ChibiBattle.fitScaleForModel', ctx);
  const facing = vm.runInContext('ChibiBattle.modelFacing', ctx);
  for (const id of ids) {
    const expectedFacing=id==='7125'?'left':'right';
    assert.equal(catalogue[id]?.facing,expectedFacing,`Nephilim ${id} keeps its authored native attack direction`);
    assert.equal(catalogue[id]?.battleHeight, 260, `Nephilim ${id} must keep its readable height`);
    assert.equal(facing({bones:[]},{},catalogue[id]),id==='7125'?-1:1,
      'Nephilim body orientation is independent from the FX direction');
  }
  const mapCtx=vm.createContext({});
  vm.runInContext(fs.readFileSync(path.join(ROOT,'web/campaign-map.js'),'utf8'),mapCtx);
  const mapScale=vm.runInContext('CampaignMap.chibiScale',mapCtx);
  const mapFacing=vm.runInContext('CampaignMap.chibiFacing',mapCtx);
  for(const id of ids) {
    assert.equal(catalogue[id]?.mapHeight,300,'Nephilim campaign height is model-specific');
    assert.equal(mapFacing(catalogue[id]),id==='7125'?-1:1,
      'campaign orientation follows the corresponding rig');
  }
  const rig={height:344.65887451171875};
  assert.ok(Math.abs(mapScale(rig,catalogue['56006'])*rig.height-300)<0.1,
    'Nephilim stays legible in the separate 720x627 scene');
  assert.ok(Math.abs(mapScale(rig,{})*rig.height-190)<0.1,
    'unrelated chibis keep their previous 190-unit display height');
  // Nephilim's idle attachment bounds include oversized spell particles:
  // using those instead of the original 344.66-unit skeleton made it tiny.
  const badVisibleBounds={x:-750,y:-1400,width:1600,height:2200};
  const originalHeight=344.65887451171875;
  const recovered=mapScale(badVisibleBounds,catalogue['56006'],originalHeight);
  assert.ok(Math.abs(recovered*originalHeight-300)<0.1,
    'campaign scale must ignore Nephilim FX attachment bounds');
  const position=vm.runInContext('CampaignMap.chibiPosition',mapCtx);
  const anchored=position(360,410,badVisibleBounds,recovered,1,
    {worldX:0,worldY:0},catalogue['56006']);
  assert.equal(anchored.x,360,'campaign chibi stays centered at its root foot');
  assert.equal(anchored.y,410,'campaign chibi stays grounded despite FX bounds');
  const legacy=position(360,410,{x:0,y:-190,width:90,height:190},1,1,null,{});
  assert.equal(legacy.x,315,'unrelated chibis keep their legacy anchor');
  assert.equal(legacy.y,410,'unrelated chibis keep their legacy foot position');
  const effectFlip=vm.runInContext('ChibiBattle.effectFlipForSide',ctx);
  assert.equal(effectFlip('spmijiale_hurt02_skill01',false),true,
    'Nephilim normal ultimate FX must undo its negative-X parent on allied side');
  assert.equal(effectFlip('spmijiale_hurt02_skill01',true),false,
    'Nephilim normal ultimate FX must remain leftward on enemy side');
  for(const fx of ['sp_mijiale_awaken_hurt02_skill01','sp_mijiale_10_hurt02_skill01',
    'spmijiale_hurt02','unrelated_skill_fx']){
    assert.equal(effectFlip(fx,false),false,`native-right FX ${fx} unchanged on allies`);
    assert.equal(effectFlip(fx,true),true,`native-right FX ${fx} unchanged on enemies`);
  }
  const rigs = [
    ['56006',554.1474609375,344.65887451171875],
    ['656016',346.0149841308594,379.0011901855469],
    ['756006',345.9549255371094,358.03485107421875],
    ['7125',914.1292724609375,464.1204833984375],
  ];
  for (const [id,width,height] of rigs) {
    const factor=scale({width,height},catalogue[id]);
    assert.ok(Math.abs(factor*height-260)<0.01,
      `Nephilim skin ${id} must not be tiny because wide skill/cape bounds`);
    const safeBoss=scale({width,height},catalogue[id],{boss:true,bossScene:true,bossScale:1});
    assert.ok(safeBoss*height<=850.001,'original boss fitting stays protected');
  }
  assert.equal(scale({width:280,height:290},catalogue['56003']),
    vm.runInContext('ChibiBattle.fitScaleForBounds',ctx)({width:280,height:290}),
    'Michael and unrelated characters keep automatic fitting');
  console.log('PASS | Nephilim: default, awakened, advanced and five skins keep facing and size');
}


async function testNativeAssistantInteraction() {
  class UiElement extends Element {
    constructor(tag){super(tag);this.style={};this.scrollTop=0;this.disabled=false;}
  }
  const root=new UiElement('div');
  const document={
    createElement:tag=>new UiElement(tag),
    addEventListener:()=>{},
    querySelector:()=>null,
  };
  const state={
    midas_info:{times:6,buys:1},explore_info:{buy_limit:4,bought:0},
    house_exam_info:{certs:3},items:{'1':10000,'2':50},
    home_systems:{},missions_info:{},
  };
  const calls=[],popups=[];
  const ctx=vm.createContext({
    document,state,number:n=>String(n),itemCatalog:{},itemIcons:new Set(),
    localStorage:{getItem:()=>null,setItem:()=>{}},
    window:{GxbFrame:{root:()=>root}},
    CampaignUI:{popup:s=>popups.push(s)},
    api:async(route,body)=>{
      calls.push({route,body});return {state,report:[]};
    },
  });
  vm.runInContext(fs.readFileSync(path.join(ROOT,'web/game-assistant.js'),'utf8'),ctx);
  const ui=vm.runInContext('GameAssistant',ctx);
  ui.open();
  let pane=root.querySelector('.ga2-scroll');
  assert.ok(pane,'original assistant scroll area must render');
  pane.scrollTop=184;
  const radio=pane.querySelector('.ga2-radio');
  assert.ok(radio&&typeof radio.onclick==='function','Yes/No must be tappable');
  radio.onclick();
  pane=root.querySelector('.ga2-scroll');
  assert.equal(pane.scrollTop,184,'changing Yes/No must not jump to page top');
  pane.scrollTop=221;
  const plus=pane.descendants().find(n=>n.tagName==='button'&&n.textContent==='+');
  assert.ok(plus&&typeof plus.onclick==='function','quantity + must be tappable');
  plus.onclick();
  assert.equal(root.querySelector('.ga2-scroll').scrollTop,221,
    'changing a quantity must preserve scroll position');
  const execute=root.descendants().find(n=>n.tagName==='button'&&n.textContent==='Thực Hiện Tất Cả');
  assert.ok(execute&&execute.disabled===false,'source execute button must be active');
  await execute.onclick();
  assert.equal(calls.length,1,'assistant must submit a real server action exactly once');
  assert.equal(calls[0].route,'/api/assistant/run');
  assert.ok(Array.isArray(calls[0].body.steps));
  assert.equal(popups.length,0,'assistant must not fail on supported test step');
  console.log('PASS | Game Assistant radios, quantity buttons, scrolling and real action');
}

function testNativeBagAndEquipment() {
  const html=fs.readFileSync(path.join(ROOT,'web/index.html'),'utf8');
  const css=fs.readFileSync(path.join(ROOT,'web/bag-actions.css'),'utf8');
  const equip=fs.readFileSync(path.join(ROOT,'web/equipment.css'),'utf8');
  const app=fs.readFileSync(path.join(ROOT,'web/app.js'),'utf8');
  assert.match(html,/id="bag-detail-summon"/);
  assert.match(app,/action\('SUMMON',\{summon_id:Number\(current.summon_id\),times\}\)/);
  assert.match(html,/id="bag-summon-count"/);
  assert.match(app,/Math\.floor\(Number\(current.count\)\/Number\(current.need\)\)/);
  assert.match(app,/times>maxCurrent/);
  assert.match(app,/current\?\.can_compose/);
  assert.match(app,/const art=node\('span','shard-card-art'\)/);
  assert.match(css,/\.bag-view \.bag-panel\{flex:1 1 auto;min-height:0;overflow-y:auto/);
  assert.match(css,/touch-action:pan-y/);
  assert.match(equip,/\.eq-board/);
  assert.match(equip,/\.eq-slot/);
  console.log('PASS | native Girl Shards summon, long Bag scroll and equipment sheet');
}


async function testAudioSettingsAndCyclicVoice(){
  const texts=new Map();
  const listeners={}, winEvents=[];
  const storage={getItem:k=>texts.get(k)||null,setItem:(k,v)=>texts.set(k,String(v))};
  const clas={state:new Set(),toggle(name,on){if(on)this.state.add(name);else this.state.delete(name);}};
  const created=[];
  class MockAudio{
    constructor(src=''){this.src=src;this.volume=1;this.paused=true;created.push(this);}
    pause(){this.paused=true;}
    play(){this.paused=false;return Promise.resolve();}
    load(){}
    addEventListener(){}
  }
  const doc={
    documentElement:{classList:clas},
    addEventListener:(kind,fn)=>{listeners[kind]=fn;},
  };
  const source=fs.readFileSync(path.join(ROOT,'web/settings-menu.js'),'utf8');
  const audioFile=fs.readFileSync(path.join(ROOT,'web/campaign-ui.js'),'utf8');
  const audioStart=audioFile.indexOf('const GxbAudio=(()=>{');
  const audioEnd=audioFile.indexOf('\n\nconst CampaignUI=',audioStart);
  assert.ok(audioStart>=0&&audioEnd>audioStart,'GxbAudio module must exist');
  const audioSource=audioFile.slice(audioStart,audioEnd);
  const ctx=vm.createContext({
    document:{...doc,createElement:()=>({addEventListener(){},setAttribute(){}})},window:{dispatchEvent:e=>winEvents.push(e)},
    localStorage:storage,Audio:MockAudio,
    CustomEvent:class{constructor(type,options){this.type=type;this.detail=options.detail;}},
    fetch:async url=>({ok:true,json:async()=>String(url).endsWith('skills.json')?{}:{tracks:['home_bg_music'],songs:[],ids:{}}}),
  });
  vm.runInContext(audioSource,ctx);
  const settings=vm.runInContext('GxbAudio',ctx);
  await settings.ready;
  assert.equal(settings.volume('music'),70);
  assert.equal(settings.volume('effects'),80);
  assert.equal(settings.volume('voice'),90);
  settings.setVolume('music',35);
  settings.setVolume('voice',40);
  settings.setVolume('effects',0);
  assert.equal(JSON.parse(texts.get('gxb3:audio-levels:v1')).music,35);
  assert.equal(settings.volume('voice'),40);
  settings.dots(true);
  assert.ok(clas.state.has('gxb-hide-red-dots'),'badge toggle applies without changing task state');
  assert.equal(texts.get('gxb3:hide-red-dots:v1'),'1');
  listeners.pointerdown();
  assert.equal(created[0].volume,.35,'music volume must affect real audio playback');
  settings.setVolume('music',15);
  assert.equal(created[0].volume,.15,'music slider immediately changes playing track');
  assert.ok(winEvents.some(e=>e.detail.channel==='voice'&&e.detail.level===40));
  assert.match(source,/Tắt dấu chấm đỏ thông báo/);
  assert.match(source,/Âm Thanh/);
  const dotsCSS=fs.readFileSync(path.join(ROOT,'web/settings-menu.css'),'utf8');
  assert.match(dotsCSS,/\.ms-home-btn img/,'native mission corner dot must be suppressed');

  const characterSounds=[];
  const voiceChange={};
  class VoiceAudio{
    constructor(src){this.src=src;this.volume=0;characterSounds.push(this);}
    pause(){}
    play(){return Promise.resolve();}
  }
  const db={rules:{},dialogs:{
    '41001':[{type:1,sound:'110010201',text:'line one'},
             {type:2,sound:'110010202',text:'line two'},
             {type:3,sound:'110010203',text:'line three'}]
  }};
  const voiceContext=vm.createContext({
    window:{addEventListener:(event,fn)=>{voiceChange[event]=fn;}},
    Audio:VoiceAudio,GxbAudio:settings,api:async()=>db,
  });
  vm.runInContext(fs.readFileSync(path.join(ROOT,'web/dates.js'),'utf8'),voiceContext);
  const dates=vm.runInContext('Dates',voiceContext);
  for(let n=0;n<4;n++)assert.equal(await dates.playGirlVoice(41001),true);
  assert.deepEqual(characterSounds.map(v=>v.src),[
    '/assets/voices/110010201.mp3',
    '/assets/voices/110010202.mp3',
    '/assets/voices/110010203.mp3',
    '/assets/voices/110010201.mp3',
  ],'tapping original Girl art cycles distinct source clips and wraps without random repeats');
  assert.ok(characterSounds.every(v=>v.volume===.4));
  voiceChange['gxb-audio-volume']({detail:{channel:'voice',level:23}});
  assert.equal(characterSounds.at(-1).volume,.23,'voice slider changes currently playing clip');
  console.log('PASS | Settings mixer persists volumes and badge choice; original Girl voice cycles sequentially');
}

function testCharacterVietnameseAcrossRoster() {
  const html=fs.readFileSync(path.join(ROOT,'web/index.html'),'utf8');
  assert.match(html,/i18n-vi\.js\?v=20261015-character-vi1/,
    'game must actually load its character translation dictionary');
  const noop=()=>{};
  class FakeObserver { observe(){} }
  const locale={current:()=> 'vi'};
  const doc={readyState:'loading',documentElement:{},addEventListener:noop};
  const context=vm.createContext({
    window:{GxbLocale:locale},GxbLocale:locale,document:doc,
    MutationObserver:FakeObserver,Node:{TEXT_NODE:3,ELEMENT_NODE:1,DOCUMENT_FRAGMENT_NODE:11},
  });
  vm.runInContext(fs.readFileSync(path.join(ROOT,'web/i18n-vi.js'),'utf8'),context);
  const local=context.window.GxbVi;
  assert.equal(typeof local?.clean,'function');
  const raw='[c][d2a300]Nê - phi - lim: [-][/c]Một tay cầm ánh sáng, còn tay kia ôm lấy bóng tối.';
  assert.equal(local.t(raw),'Nephilim: Một tay cầm ánh sáng, còn tay kia ôm lấy bóng tối.');
  for(const [from,to] of [
    ['Gift','Quà Tặng'],['Voice','Giọng Nói'],['Discuss','Trò Chuyện'],
    ['File','Hồ Sơ'],['Touch 5','Chạm 5'],['Report','Báo Cáo'],
    ['Strategy','Chiến Thuật'],['Review','Đánh Giá'],
    ['Skill Description','Mô Tả Kỹ Năng'],['Level Up','Tăng Cấp'],
    ['Promote','Nâng Bậc'],['Elite Skills','Kỹ Năng Tinh Anh']
  ]) assert.equal(local.t(from),to,from);
  const station=JSON.parse(fs.readFileSync(path.join(ROOT,'web/assets/station/station.json'),'utf8'));
  for(const label of Object.values(station.labels))
    assert.notEqual(local.t(label.text),label.text,'missing native tag translation: '+label.text);
  const neph=Object.values(station.girls).find(g=>g.name==='Nephilim');
  assert.ok(neph&&neph.skills.length===4);
  assert.match(local.t(neph.desc),/Tốc Độ|tốc độ/i);
  for(const skill of neph.skills){
    assert.notEqual(local.t(skill.name),skill.name,'Nephilim skill name '+skill.id);
    assert.match(local.t(skill.desc),/[À-ỹ]/,'Nephilim skill description '+skill.id);
  }
  const girls=JSON.parse(fs.readFileSync(path.join(ROOT,'web/assets/girl-details.json'),'utf8'));
  assert.ok(Object.keys(girls).length>=500);
  for(const girl of Object.values(girls)){
    if(!girl.quote)continue;
    assert.doesNotMatch(local.t(girl.quote),/\[c\]|\[\/c\]|\[-\]|\[[a-f0-9]{6,8}\]/i,
      'publisher markup leaks in girl quote');
  }
  const src=fs.readFileSync(path.join(ROOT,'web/station.js'),'utf8');
  assert.match(src,/GxbVi\.t\(text\)/,'station must translate labels and skill descriptions across the roster');
  const dates=fs.readFileSync(path.join(ROOT,'web/dates.js'),'utf8');
  assert.match(dates,/GxbVi\.t\(text\)/,'dates must translate native voice text');
  console.log('PASS | all 38 Station tags, universal character UI, and original quote markup are localized');
}

(async () => {
  testCharacterVietnameseAcrossRoster();
  await testAudioSettingsAndCyclicVoice();
  testNativeBagAndEquipment();
  await testNativeAssistantInteraction();
  testNephilimBattleModels();
  testBattleScale();
  testLobby();
  await testPvpResult();
})().catch(err => {console.error(err);process.exitCode = 1;});
