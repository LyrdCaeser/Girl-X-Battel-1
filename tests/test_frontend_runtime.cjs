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

(async () => {
  testLobby();
  await testPvpResult();
})().catch(err => {console.error(err);process.exitCode = 1;});
