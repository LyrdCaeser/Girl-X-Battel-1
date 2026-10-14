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

(async () => {
  testNephilimBattleModels();
  testBattleScale();
  testLobby();
  await testPvpResult();
})().catch(err => {console.error(err);process.exitCode = 1;});
