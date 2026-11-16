'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const ui=read('web/souls.js'),catalog=JSON.parse(read('data/souls.json'));
class El{
 constructor(tag){this.tag=tag;this.children=[];this.className='';this.style={};this.textContent='';this.disabled=false;}
 append(...list){this.children.push(...list);}
 get descendants(){return this.children.flatMap(c=>[c,...(c.descendants||[])]);}
}
const panel=[];
const player={partner_id:77,lv:250,table_id:41001,souls:[0,0,0,0,0],soul_infos:[]};
const state={uid:'test-user',server_id:'S1',roster:[player],souls_info:{items:{'fake-old':{}},plans:{}},items:{}};
let stored={uid:'test-user',server_id:'S1',roster:[{...player}],souls_info:{items:{},plans:{}}};
const ctx=vm.createContext({
 document:{createElement:t=>new El(t)},
 api:async url=>url==='/api/souls/catalog'?catalog:(url==='/api/state'?stored:Promise.reject(Error('Unexpected '+url))),
 state,
 GirlUI:{win(){const b=new El('div');panel.push(b);return{body:b};},toast(){}},
 render(){},number:n=>String(n)
});
vm.runInContext(ui,ctx);
const api=vm.runInContext('Souls',ctx),latest=()=>panel.at(-1);
const find=text=>latest().descendants.find(x=>x.textContent===text);
(async()=>{
 await api.open(77,5);
 assert.equal(Object.keys(state.souls_info.items).length,0,'Stale local inventory must be replaced by actual server count');
 const replaceTab=find('Chuyển Đổi');assert(replaceTab);replaceTab.onclick();
 assert(find('Hồ sơ trên máy chủ hiện chưa có Trang Bị Linh Hồn. Đây là số vật phẩm thật đã lưu, không phải số đồ trong ảnh cũ.'));
 assert(find('Làm Mới Túi Linh Hồn'));
 const id=Object.keys(catalog.equip1)[0];
 stored={...stored,souls_info:{items:{'98':{kind:1,table_id:Number(id),lv:0,awake:0,attrs:[],lock:0,owner:0}},plans:{}}};
 await find('Làm Mới Túi Linh Hồn').onclick();
 assert.equal(Object.keys(state.souls_info.items).length,1);
 const before=state.souls_info;
 stored={...stored,uid:'different-user',souls_info:{items:{},plans:{}}};
 await find('Làm Mới Túi Linh Hồn').onclick();
 assert.equal(state.souls_info,before,'Mismatched accounts must never overwrite inventory');
 console.log('PASS: real profile refresh handles empty items, later server items, and rejects wrong account');
})().catch(e=>{console.error(e);process.exitCode=1});
