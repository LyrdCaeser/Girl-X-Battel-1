'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const read=p=>fs.readFileSync(require('node:path').join(__dirname,'..',p),'utf8');

class El{
 constructor(tag='div'){this.tagName=tag.toLowerCase();this.children=[];this.parentElement=null;this.className='';this.textContent='';this.style={};this.disabled=false;this.scrollTop=0;this.hidden=false;this.attributes={};}
 append(...children){for(const child of children){this.children.push(child);if(child&&typeof child==='object')child.parentElement=this;}}
 remove(){if(this.parentElement){this.parentElement.children=this.parentElement.children.filter(c=>c!==this);this.parentElement=null;}}
 setAttribute(k,v){this.attributes[k]=v;}
 descendants(){return this.children.flatMap(c=>[c,...(c.descendants?c.descendants():[])]);}
 querySelector(sel){return this.descendants().find(c=>c.className.split(' ').includes(sel.slice(1)))||null;}
 get childElementCount(){return this.children.length;}
}
async function main(){
 const root=new El('main'),document={createElement:t=>new El(t),addEventListener:()=>{}};
 const report=[
  {key:'midas',label:'Alchemy',ok:true,got:{'1':6300000}},
  {key:'midas',label:'Alchemy · Purchase with Gems',ok:true,got:{'1':8382150000}},
  {key:'excursion',label:'Excursion - Resource Collection',ok:false,error:'Todavía no hay recursos para recoger'},
  ...Array.from({length:18},(_,i)=>({key:'daily',label:'Daily Tasks',ok:false,error:i%2?'Nada que reclamar':'Ya usada hoy'}))
 ];
 const state={midas_info:{times:3,buys:0},home_systems:{},missions_info:{},explore_info:{buy_limit:0,bought:0},house_exam_info:{certs:0},items:{'1':0,'2':0}};
 const ctx=vm.createContext({
  document,state,number:n=>Number(n).toLocaleString('vi-VN'),itemCatalog:{'1':{name:'Coin'}},itemIcons:new Set(),
  localStorage:{getItem:()=>null,setItem:()=>{}},window:{GxbFrame:{root:()=>root}},
  CampaignUI:{popup:()=>{throw Error('unexpected popup');}},
  api:async(uri,params)=>{
   assert.equal(uri,'/api/assistant/run');
   assert.ok(Array.isArray(params.steps));
   return {state,report};
  }
 });
 vm.runInContext(read('web/game-assistant.js'),ctx);
 const ui=vm.runInContext('GameAssistant',ctx);
 ui.open();
 const help=root.querySelector('.ga2-help');
 assert.ok(help&&typeof help.onclick==='function');
 help.onclick();
 const helpWin=root.querySelector('.ga2-help-over');
 assert.ok(helpWin,'help must use the native window, not giant text in Campaign popup');
 assert.ok(helpWin.querySelector('.ga2-olist'),'help text must scroll');
 const helpText=helpWin.descendants().filter(x=>x.className==='ga2-help-text').map(x=>x.textContent);
 assert.equal(helpText.length,5);
 assert.ok(helpText[0].includes('Luyện Kim'));
 const dismissHelp=helpWin.querySelector('.ga2-confirm');
 assert.equal(dismissHelp.textContent,'Đóng');
 dismissHelp.onclick();
 assert.equal(root.querySelector('.ga2-help-over'),null);
 let run=root.descendants().find(x=>x.textContent==='Thực Hiện Tất Cả');
 assert.ok(run,'main original assistant execution button remains');
 await run.onclick();
 const win=root.querySelector('.ga2-result-wrap');
 assert.ok(win,'summary must open in overlay');
 const box=win.querySelector('.ga2-over'),list=box.querySelector('.ga2-olist');
 assert.ok(list,'list should be separate from fixed footer');
 assert.equal(list.attributes.role,'region');
 assert.equal(list.attributes.tabindex,'0','accessible scroll list');
 assert.equal(list.children.length,21,'every reported step must remain visible in list');
 assert.ok(box.querySelector('.ga2-over-foot'),'footer cannot be part of scrolling list');
 const titles=list.descendants().filter(x=>x.className==='ga2-res-label').map(x=>x.textContent);
 assert.equal(titles[0],'Luyện Kim');
 assert.equal(titles[1],'Luyện Kim · Mua bằng Kim Cương');
 assert.equal(titles[2],'Thám Hiểm · Nhận tài nguyên');
 const errors=list.descendants().filter(x=>x.className==='ga2-skip').map(x=>x.textContent);
 assert.equal(errors[0],'Chưa có tài nguyên để thu thập');
 assert.ok(errors.every(s=>!/Ya usada|Nada que|Todav|No hay|Alchemy|Excursion/.test(s)),'all known status messages in Vietnamese');
 const done=box.querySelector('.ga2-confirm');
 assert.ok(done&&typeof done.onclick==='function','fixed confirm button');
 done.onclick();
 assert.equal(root.querySelector('.ga2-result-wrap'),null,'confirm closes result only');
 const css=read('web/game-assistant.css');
 assert.match(css,/border-image:url\('\/assets\/detail\/sheet\/9gongge21\.png'\)/,'native publisher frame required');
 assert.match(css,/\.ga2-over\{[\s\S]*?display:flex;flex-direction:column/);
 assert.match(css,/\.ga2-olist\{[\s\S]*?flex:1 1 auto;min-height:0/);
 assert.match(css,/\.ga2-olist\{[\s\S]*?overflow-y:auto;overflow-x:hidden/);
 assert.match(css,/\.ga2-olist\{[\s\S]*?touch-action:pan-y/);
 assert.match(css,/\.ga2-over-foot\{[\s\S]*?flex:0 0 auto/);
 assert.match(css,/\.ga2-help-text\{/);
 assert.ok(!/\.ga2-over\{[^}]*overflow-y:auto/.test(css),'summary shell must not steal touch scrolling');
 const html=read('web/index.html');
 assert.ok(html.includes('/game-assistant.js?v=20261117-native-result-vi-r4'));
 assert.ok(html.includes('/game-assistant.css?v=20261117-native-result-scroll-r4'));
 console.log('PASS: original assistant result frame, 21 scrollable result rows, Vietnamese entries/errors, persistent footer and confirm');
}
main().catch(e=>{console.error(e.stack||e);process.exitCode=1;});
