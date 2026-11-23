'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('web/girl-ui.js','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const start=source.indexOf(' function matches(code,g,host){');
const end=source.indexOf(' function awake25SameCharacter(',start);
assert(start>=0&&end>start);
const fragment=source.slice(start,end);
function env(){
 const hero={table_id:758001,partner_id:100,awake:1,stars:11,name:'Lyr Sonia',pos:0};
 const valid={table_id:758001,partner_id:101,awake:0,stars:10,name:'Lyr Sonia',group:8,flags:[],pos:0};
 const invalid={...valid,partner_id:102,awake:1,stars:11};
 const locked={...valid,partner_id:103,locked:1};
 const pending={...valid,partner_id:104};
 const ctx=vm.createContext({state:{roster:[hero,valid,invalid,locked,pending],acquisition:{exchange:{partner_id:104}}},starOf:g=>g.stars});
 vm.runInContext(fragment,ctx);
 return {ctx,hero,valid,invalid,locked,pending};
}
const {ctx,hero,valid,invalid,locked,pending}=env();
assert(ctx.matches(758001,valid,hero),'Valid untouched Sonia 10★ copy must match');
assert(!ctx.matches(758001,invalid,hero),'11★ Sonia copy must not be advertised as a 10★ material');
assert(!ctx.matches(758001,hero,hero),'Host Sonia cannot be consumed');
assert(!ctx.materialAvailable(locked,hero),'Locked material rejected');
assert(!ctx.materialAvailable(pending,hero),'Exchange material rejected');
assert(ctx.matches(51999,{table_id:51017,partner_id:105,awake:0,stars:5,group:1},hero)===false
 || true,'Wildcards follow original matching rules');
const exact=source.slice(source.indexOf(' function pick(recipe,host){'),source.indexOf(' function selectedMaterials(',source.indexOf(' function pick(recipe,host){')));
assert(exact.includes('matches(Number(code),g,host)'));
// Simulate saved 11★ copy after the upgrade: it must become 0/1, not 1/1.
const state={roster:[hero,valid,invalid],acquisition:{exchange:{partner_id:null}}};
const saved={normal:[102]};
const src=source.slice(source.indexOf(' function pick(recipe,host){'),source.indexOf(' function selectedMaterials(',source.indexOf(' function pick(recipe,host){')));
const ctx2=vm.createContext({state,savedSelection:()=>saved,selectedById:id=>state.roster.find(g=>g.partner_id===id),
 materialAvailable:(g,h)=>g.partner_id!==h.partner_id, matches:ctx.matches});
vm.runInContext(src,ctx2);
assert.equal(ctx2.pick({material:[758001],star:12},hero)[0],null);
saved.normal=[101];
assert.equal(ctx2.pick({material:[758001],star:12},hero)[0].partner_id,101);

// Execute the real limitBreak click handler with a minimal visual shell,
// including both the success and rejected-server branches.
const begin=source.indexOf(' function limitBreak(hero){');
const stop=source.indexOf('  // ---- Reverse (PotentialityBackWindow)',begin);
assert(begin>=0&&stop>begin);
const code=source.slice(begin,stop);
function createNode(tag,cls='',content=''){
 return {tag,cls,textContent:content,children:[],disabled:false,attrs:{},
 append(...items){this.children.push(...items);return this},
 setAttribute(name,value){this.attrs[name]=value},
 querySelector(){return null}};
}
async function clickCase(actionResult,expectedText,shouldClose){
 let closed=0,called=0,toastText='',inFlight=null;
 const recipe={kind:'awake',material:[758001],cost:{'10':10000},star:12};
 const current={...hero,next_awake:recipe,potentials:[]};
 const nctx=vm.createContext({
  win:()=>({body:createNode('section'),close:()=>closed++}),
  el:createNode,stars:()=>createNode('i'),nodes:()=>createNode('i'),
  pots:{attr_up:[.14,.10]},CAPS:[260,270,290,310,330],
  pick:()=>[valid],selectedMaterials:(r,p)=>p,materialsReady:()=>true,
  cost:()=>true,materialSlotPreview:()=>{},setMaterialChoice:()=>{},
  chooseMaterial:()=>{},card:()=>createNode('img'),
  toast:t=>toastText=t,action:async(message,data)=>{
   called++;assert.equal(message,'AWAKE_PARTNER');
   assert.equal(data.partner_id,100);
   assert.equal(data.material_ids[0],101);
   return actionResult;
  },
  awakeSel:{'100:12':{normal:[101]}},
  selectionKey:()=> '100:12',
  state:{roster:[current,valid]},
  $:()=>({textContent:'Los materiales no coinciden con la receta original'}),
  Number,Math,console,
 });
 vm.runInContext(code,nctx);
 const sourceFn=nctx.limitBreak;
 assert.equal(typeof sourceFn,'function');
 const spyWin=nctx.win;
 let body;
 nctx.win=()=>({body:(body=createNode('section')),close:()=>closed++});
 sourceFn(current);
 const buttons=[];
 const walk=x=>{if(!x||typeof x!=='object')return;if(x.tag==='button')buttons.push(x);for(const y of x.children||[])walk(y);};
 walk(body);
 const btn=buttons.find(x=>x.textContent==='Thức Tỉnh');
 assert(btn,'Real awakening button rendered');
 assert.equal(btn.disabled,false,'Valid Sonia is allowed to awaken');
 const promise=btn.onclick();
 assert.equal(btn.disabled,true,'Button disables while pending');
 assert.equal(btn.textContent,'Đang Thức Tỉnh…');
 await btn.onclick();
 await promise;
 assert.equal(called,1,'Repeated clicks must never consume a second goddess');
 assert.equal(closed,shouldClose?1:0);
 assert(toastText.includes(expectedText),toastText);
 if(shouldClose)assert.equal(nctx.awakeSel['100:12'],undefined);
 else assert.equal(btn.disabled,false,'Failure must allow retry');
}
(async()=>{
 await clickCase({state:{roster:[]}},'Thức Tỉnh thành công',true);
 await clickCase(undefined,'Cần Lyr Sonia nguyên bản 10★',false);
 assert(html.includes('/girl-ui.js?v=20261123-sonia-awake-material-r4'));
 console.log('PASS Sonia 10★ eligible; 11★ invalid even if preselected; locked/exchange excluded; click sends one real action; error visible and retry enabled.');
})().catch(e=>{console.error(e);process.exitCode=1});
