'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync('web/dress.js','utf8');
class El{
 constructor(tag){this.tag=tag;this.children=[];this.style={};this.attributes={};this.className='';this.textContent='';this.dataset={};this.disabled=false;this.isConnected=true;this.parent=null;this.onclick=null;this.title='';}
 append(...values){for(const c of values){if(!c)continue;this.children.push(c);c.parent=this;}}
 after(v){registry[v.id]=v;}
 replaceChildren(...values){this.children=[];this.append(...values);}
 setAttribute(k,v){this.attributes[k]=v;}
 get lastChild(){return this.children[this.children.length-1];}
 all(){return this.children.flatMap(c=>[c,...c.all()]);}
 querySelector(selector){
  if(selector.startsWith('.'))return this.all().find(x=>x.className?.split(' ').includes(selector.slice(1)))||null;
  return this.all().find(x=>x.tag===selector)||null;
 }
}
const registry={'home-systems-view':new El('div')};
const owned=[{dress:101001,star:1,cost:null},{dress:101231,star:1,cost:null}];
const state={items:{'1':100000,'2':100000},dress_info:{
  owned,equipped:[1000101,1000201,1000301,0,0],style:{'101001':1000102},
  attrs:[5,7,8],skills:[],free:{'1':600,'2':600},buttons:{'258':0,'259':0},
  silk:{'260':0,'261':0},common:{'1':0},max_drop:100,pity:{'1':4,'2':0}
 }};
const cat={
 pieces:{
  '101001':{name:'Head (Standard Uniform)',pos:1,styles:[1000101,1000102],items:[3100001],available:true},
  '101231':{name:'',pos:1,styles:[1023101],items:[3101381],available:false}
 },
 items:{'3100001':{qlt:1,base:[4,2,1],icon:['icon_dress_1000101']}},
 styles:{
 '1000101':{dress:101001,image:'dress_1000101'},
 '1000102':{dress:101001,image:'dress_1000102'}
 },
 slots:{'1':{name:'Head',can_rm:0},'2':{name:'Body',can_rm:0},'3':{name:'Legs',can_rm:0},'4':{name:'Headwear',can_rm:1},'5':{name:'Accessories',can_rm:1}},
 groups:{},skill_text:{},common:[],shard_names:{}
};
const ctx=vm.createContext({
 view:'campus',state,devicePixelRatio:1,
 document:{createElement:x=>new El(x)},
 $:x=>registry[x]||null,
 showView:x=>{ctx.view=x;},
 api:async url=>{if(url==='/api/dress/catalog')return cat;throw new Error('unexpected API '+url);},
 number:x=>String(x),
 GxbSpine:{load:async()=>{throw new Error('no canvas in DOM mock');}},
 PIXI:{},
});
(async()=>{
 vm.runInContext(source,ctx);
 const dress=vm.runInContext('Dress',ctx);
 await dress.open('campus','closet');
 const root=registry['dress-view'];
 assert(root,'closet view mounted');
 assert(root.all().some(x=>x.textContent==='Tủ Trang Phục'));
 let cards=root.all().filter(x=>x.className.includes('dr-card'));
 assert.equal(cards.length,2,'owned broken piece is still visible, not silently removed from save');
 assert.equal(cards.filter(x=>x.className.includes('dr-unavailable')).length,1,'broken entry is disabled');
 assert.equal(cards.find(x=>x.className.includes('dr-unavailable')).disabled,true);
 const gallery=root.all().find(x=>x.className.includes('dr-gal'));
 assert(gallery,'gallery filter');
 gallery.onclick();
 cards=root.all().filter(x=>x.className.includes('dr-card'));
 assert.equal(cards.length,1,'catalogue gallery excludes genuinely missing art/data');
 assert(!cards[0].disabled);
 const store=root.all().find(x=>x.className.includes('dr-tab')&&x.textContent==='Cửa Hàng Trang Phục');
 assert(store,'store tab');
 store.onclick();
 let drawButtons=root.all().filter(x=>x.className==='dr-drawbtn');
 assert.equal(drawButtons.length,2);
 assert(drawButtons.every(b=>b.disabled),'paid draw buttons disabled without ticket inventory');
 state.dress_info.free['1']=0;
 dress.render();
 drawButtons=root.all().filter(x=>x.className==='dr-drawbtn');
 assert.equal(drawButtons[0].disabled,false,'free draw remains available with zero buttons');
 assert.equal(drawButtons[1].disabled,true,'ten draws still require ten buttons');
 await dress.open('campus','locker');
 const editSlot=root.all().find(x=>x.className==='dr-slot');
 assert(editSlot,'outfit slot must exist');
 editSlot.onclick();
 const editCards=root.all().filter(x=>x.className.includes('dr-card'));
 assert.equal(editCards.length,1,'broken legacy art must not be selectable when editing');
 assert(!editCards[0].disabled,'valid alternative outfit remains selectable');
 console.log('PASS: Outfit Closet/Gallery/Locker Room ignore broken art, keep native pieces and paid/free buttons correct');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1;});
