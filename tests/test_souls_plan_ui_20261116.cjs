'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'..');
const ui=fs.readFileSync(path.join(ROOT,'web/souls.js'),'utf8');
const css=fs.readFileSync(path.join(ROOT,'web/souls.css'),'utf8');
const html=fs.readFileSync(path.join(ROOT,'web/index.html'),'utf8');
const catalog=JSON.parse(fs.readFileSync(path.join(ROOT,'data/souls.json'),'utf8'));

class Element{
 constructor(tag){this.tagName=tag;this.children=[];this.style={};this.className='';this.textContent='';this.disabled=false;}
 append(...children){this.children.push(...children.filter(Boolean));}
 get descendants(){return this.children.flatMap(c=>[c,...(c.descendants||[])]);}
}
const root=new Element('div');
const req=[];
const soulId=Object.keys(catalog.equip1)[0];
const state={
 roster:[{partner_id:7,table_id:41001,lv:250,souls:[7,0,0,0,0]}],
 souls_info:{items:{'7':{kind:1,table_id:Number(soulId),lv:0,awake:0,attrs:[],owner:7,lock:0}},plans:{}},
 items:{},profile:{}
};
const ctx=vm.createContext({
 document:{createElement:tag=>new Element(tag)},
 api:async(url,body)=>{
  if(url==='/api/souls/catalog')return catalog;
  assert.equal(url,'/api/souls/action');
  req.push(body);
  const bucket=state.souls_info.plans['7']||{};
  if(body.action==='plan_save')bucket[String(body.plan)]=state.roster[0].souls.slice();
  if(body.action==='plan_delete')delete bucket[String(body.plan)];
  if(body.action==='plan_apply')state.roster[0].souls=bucket[String(body.plan)].slice();
  state.souls_info.plans['7']=bucket;
  return {state};
 },
 state,
 GirlUI:{win(){const body=new Element('div'),win=new Element('div');root.append(body);return {body,win};},toast(msg){throw Error(msg)}},
 render(){},
 number:n=>String(n),
 portrait:()=>new Element('img'),
});
vm.runInContext(ui,ctx);
const api=vm.runInContext('Souls',ctx);
function latest(){return root.children.at(-1)}
function match(text){return latest().descendants.find(x=>x.textContent===text)}
(async()=>{
 await api.open(7);
 assert(match('Tổng Quan'),'Overview must be Vietnamese');
 assert(match('Chuyển Đổi'),'Replace must be Vietnamese');
 const tab=match('Bộ Trang Bị');assert(tab,'Plan tab must be localized');
 assert(match('Tháo Tất Cả'),'Unequip must be localized');
 tab.onclick();
 assert(match('Bộ Trang Bị Linh Hồn'));
 assert.equal(latest().descendants.filter(x=>x.className==='ag-plan').length,3);
 assert(!match('Anima Gear plans (saved combinations) are not available in the local version yet.'));
 assert(match('Lưu bộ này'),'save button missing');
 await match('Lưu bộ này').onclick();
 assert.equal(req[0].action,'plan_save');
 assert.equal(req[0].partner_id,7);
 assert.equal(req[0].plan,1);
 assert(match('Bộ 1 · Đã lưu'),'Saved plan must render after server state refresh');
 await match('Áp dụng').onclick();
 assert.equal(req[1].action,'plan_apply');
 await match('Xóa bộ').onclick();
 assert.equal(req[2].action,'plan_delete');
 assert(match('Bộ 1 · Chưa lưu'),'Deleted plan must disappear');
 assert.match(css,/\.ag-plan-pieces/);
 assert.match(css,/\.gs-win\.ag-win/,'Anima header clipping must be fixed on Mobile');
 assert.match(html,/\/souls\.js\?v=20261116-anima-vi-r2/);
 assert.match(html,/\/souls\.css\?v=20261116-anima-vi-r2/);
 console.log('PASS | Anima: Vietnamese titles and 3 server-backed saved sets (save/apply/delete)');
})().catch(err=>{console.error(err);process.exitCode=1});
