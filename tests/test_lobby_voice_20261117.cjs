'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const nodes=[];const stage={
 dataset:{},listeners:{},querySelector(s){return nodes.find(n=>n.className?.includes('lb-quote'))||null},
 append(n){nodes.push(n)},addEventListener(type,fn){this.listeners[type]=fn}
};
const document={querySelector(s){return s==='#home-view .home-stage'?stage:null},
 createElement(){return {className:'',textContent:'',classList:{add(){},remove(){}},setAttribute(){},remove(){}}}};
let called=[],view='home';
const Dates={playGirlVoice:async(id,callback)=>{called.push(id);callback('Lời chào của Nữ Thần');return true}};
const context=vm.createContext({document,Dates,view,clearTimeout(){},setTimeout(){return 1},window:{GxbVi:{t:s=>s}}});
vm.runInContext(fs.readFileSync('web/lobby-dialogue.js','utf8'),context);
const L=vm.runInContext('LobbyDialogue',context);
(async()=>{
 L.sync(751017);
 assert.equal(typeof stage.listeners.click,'function');
 stage.listeners.click({target:{closest:()=>false}});
 await Promise.resolve();await Promise.resolve();
 assert.equal(called[0],751017);
 assert.equal(nodes[0].textContent,'Lời chào của Nữ Thần');
 stage.listeners.click({target:{closest:()=>true}});
 await Promise.resolve();assert.equal(called.length,1,'menu tap should never trigger voice');
 L.sync(651024);
 await L.speak();assert.equal(called.at(-1),651024);
 assert.equal(nodes.length,1,'reuse bubble; never stack duplicates');
 L.sync(null);
 assert.equal(await L.speak(),false);
 assert.equal(L.translateQuote(43001,'fallback'),'Thế giới này được Thượng Đế tạo ra. Vậy nên, hãy bày tỏ lòng biết ơn với Người.');
 console.log('PASS: lobby actual wallpaper voice + Vietnamese bubble, ignores buttons, prevents duplication');
})().catch(e=>{console.error(e);process.exitCode=1});
