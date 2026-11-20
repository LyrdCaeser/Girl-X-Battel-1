'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const read=n=>fs.readFileSync(path.join(__dirname,'..',n),'utf8');
const intern=read('web/internship.js'),enroll=read('web/enroll.js'),html=read('web/index.html');
const data=JSON.parse(read('data/internship.json'));
const sourceNames=data.names;
const match=intern.match(/const TASK_NAMES_VI=Object\.freeze\((\{[\s\S]*?\})\);/);
assert(match,'Vietnamese mission title table');
const translated=JSON.parse(match[1]);
assert.equal(Object.keys(sourceNames).length,45);
assert.deepEqual(Object.keys(translated).sort(),Object.keys(sourceNames).sort());
const names=['Psychic','Kitty','Anna','Fleur','Reo','Lavia','Amazon','Lightin','Medusa','Guan Yin','Gabriel','Angel'];
for(const name of names){
 const sourceEntries=Object.entries(sourceNames).filter(([k,v])=>v.includes(name));
 for(const [id] of sourceEntries)assert(translated[id].includes(name),'Name must not be translated: '+name+' #'+id);
}
for(const id of ['18','19','22'])assert(!/Assisting|Request|Threat/.test(translated[id]),'not localized '+id);
const executableIntern=intern.split('\n').filter(x=>!x.trim().startsWith('//')).join('\n');
for(const fragment of [
 "tavern_text_en_en",'Not yet started','Claim in Bulk','Multi-Intern','Condiciones (',
 'No completed missions','No available Girls meet','Refresh will replace','No missions. More arrive'
])assert(!executableIntern.includes(fragment),fragment);
const executableEnroll=enroll.split('\n').filter(x=>!x.trim().startsWith('//')).join('\n');
for(const fragment of [
 'Choose a faction and stamp','Exchange Help','No available 4★/5★ Girls',
 'Save transforms her','Use 10 Seals','Not enough Seals','Select a Girl to Exchange',"Ghost"
])assert(!executableEnroll.includes(fragment),fragment);
for(const name of ['Hệ U Linh Ma','Hệ Nhân Tộc','Hệ Ma Thú','Hệ Tinh Linh','Hệ Ánh Sáng & Bóng Tối'])assert(enroll.includes(name),name);
for(const src of ['/internship.js?v=20261117-intern-fullvi-r1','/internship.css?v=20261117-intern-fullvi-r1','/enroll.js?v=20261117-enroll-fullvi-r1','/enroll.css?v=20261117-enroll-fullvi-r1'])assert(html.includes(src),src);

class El{
 constructor(tag='div'){this.tagName=tag;this.children=[];this.className='';this.style={};this.dataset={};this.attributes={};this.textContent='';this.hidden=false;this.parent=null;this.classList={add:()=>{}};}
 append(...nodes){for(const x of nodes){if(x===null)continue;this.children.push(x);x.parent=this;} }
 replaceChildren(...nodes){this.children=[];this.append(...nodes);}
 after(x){if(this.parent){this.parent.append(x);}else{this.lastAfter=x;}}
 setAttribute(k,v){this.attributes[k]=v;}
 getBoundingClientRect(){return {width:720,height:1280};}
 querySelector(sel){if(sel[0]==='.')return this.descendants().find(x=>x.className.split(' ').includes(sel.slice(1)))||null;return null;}
 querySelectorAll(sel){if(sel[0]==='.')return this.descendants().filter(x=>x.className.split(' ').includes(sel.slice(1)));return [];}
 descendants(){return this.children.flatMap(x=>[x,...x.descendants()]);}
 remove(){if(this.parent)this.parent.children=this.parent.children.filter(x=>x!==this);}
}
const makeCtx=(mode)=>{
 const home=new El('div'),mounts={ 'home-systems-view':home };
 const state={server_time:100,internship_info:{missions:[{
  id:1,name:18,title:'Assisting Amazon',state:'idle',partner_star:0,conds:[],star:5,time:28800,
  locked:false,award:{'1':6300000},partner_num:1,end:0
 }],scrolls:{24:2,25:1},busy:[],daily:17,max:200,next_day:6000,refresh_cost:{'2':10}},
 items:{'1':0,'2':300,'19':10,'20':50},roster:[],partners:[],acquisition:{exchange:null,eligible:[]}};
 const ctx=vm.createContext({
  view:mode,state,document:{createElement:t=>new El(t)},performance:{now:()=>0},
  setInterval:()=>1,clearInterval:()=>{},setTimeout:()=>1,
  $:id=>mounts[id]||((id==='internship-view'||id==='enroll-view')?home.lastAfter:null),showView:x=>{ctx.view=x;},
  api:async()=>({state}),itemCatalog:{'1':{name:'Vàng',quality:1}},itemPicture:()=>'/assets/currency/icon_1_small.png',
  number:n=>String(n),girlsCatalog:[],cardIds:new Set(),window:{render:()=>{},GxbBagVi:{t:x=>x}},portrait:()=>new El('div'),
  CampaignUI:{popup:()=>{}},GirlUI:{win:()=>({body:new El(),close:()=>{}}),confirm:async()=>true,toast:()=>{}},
  GxbSpine:{mount:async()=>{throw Error('No GPU in test');}},GxbAudio:{sfx:()=>{}},
  ChibiBattle:{catalogue:async()=>({})}
 });
 return {ctx,home,mounts};
};
(async()=>{
 const first=makeCtx('internship');vm.runInContext(intern,first.ctx);
 const int=vm.runInContext('Internship',first.ctx);int.render();
 const ir=first.home.lastAfter;
 assert(ir,'Internship root created');
 assert(ir.descendants().some(x=>x.className==='in-title-vi'&&x.textContent==='Thực Tập'));
 assert(ir.descendants().some(x=>x.className==='in-name'&&x.textContent==='Trợ Giúp Amazon'));
 assert(ir.descendants().some(x=>x.textContent==='Chưa bắt đầu'));
 for(const label of ['Dùng Vé','Cử Hàng Loạt','Nhận Tất Cả'])assert(ir.descendants().some(x=>x.textContent===label),label);
 const h=ir.descendants().find(x=>x.className==='in-help');assert(h);h.onclick();
 const other=makeCtx('enroll');vm.runInContext(enroll,other.ctx);
 const en=vm.runInContext('Enroll',other.ctx);en.render();
 const er=other.home.lastAfter;
 assert(er.descendants().some(x=>x.textContent==='Ghi Danh'));
 assert(er.descendants().some(x=>x.textContent==='Hoán Đổi'));
 assert(er.descendants().some(x=>x.textContent==='Tri thức chính là sức mạnh!'));
 assert(er.descendants().some(x=>x.textContent==='Hệ U Linh Ma'));
 const enrollHelp=er.descendants().find(x=>x.className==='en-help');assert(enrollHelp);
 enrollHelp.onclick();
 const exchangeTab=er.descendants().find(x=>x.textContent==='Hoán Đổi');assert(exchangeTab);
 exchangeTab.onclick();
 assert(er.descendants().some(x=>x.textContent==='Chọn Nữ Thần Để Hoán Đổi'));
 console.log('PASS 45/45 names, goddess proper names, Intern and Enroll primary UI and Vietnamese help');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1;});
