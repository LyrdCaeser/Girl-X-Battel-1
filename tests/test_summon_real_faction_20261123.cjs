'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const src=fs.readFileSync('web/summon-anim.js','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const f=src.slice(src.indexOf(' function factionOf(p){'),src.indexOf(' // PartnerSummonEffect:initEffect'));
assert(f.includes("fig.hackTextureBySlotName('zhiye',PIXI.Texture.EMPTY"));
assert(src.includes("for(const name of ['juese','name','zhiye'])"));
assert(src.match(/nativeFaction\(e\.fig,p\);/g)?.length===2);
assert(src.includes('nativeFaction(fig,entry);'));
const sprites=[];
const PIXI={Texture:{EMPTY:{empty:true}},Sprite:{from(src){
 const n=/\/8\.png$/.test(src)?256:46;
 const obj={src,texture:{orig:{width:n,height:n},baseTexture:{valid:true}},
 anchor:{set(x,y){obj.anchorPosition=[x,y]}},
 scale:{set(x,y){obj.scaling=[x,y]}}};sprites.push(obj);return obj;
}}};
const girlsCatalog=[
 {id:51019,group:1,name:'Raenvya'},
 {id:51016,group:1,name:'Diana'},
 {id:51017,group:2,name:'Nữ Thần Nhân Tộc'},
 {id:651026,group:1,name:'Raenvya evolved'},
 {id:758001,group:8,name:'Lyr Sonia'},
 {id:71001,group:7,name:'Nữ Thần Vũ Trụ'},
 {id:51022,group:6,name:'Nữ Thần Ánh Sáng'},
 {id:34003,group:4,name:'Mythra'},
];
const ctx=vm.createContext({girlsCatalog,avatars:{},
 PIXI,hostChain(id){return id===651026?[651026,51019]:[id]},
});
vm.runInContext(f,ctx);
const factionOf=vm.runInContext('factionOf',ctx);
const nativeFaction=vm.runInContext('nativeFaction',ctx);
function fig(){
 const slot={children:[],addChild(o){this.children.push(o)}},f={changes:[],
 skeleton:{findSlotIndex(n){return n==='zhiye'?0:-1}},
 slotContainers:[slot],
 hackTextureBySlotName(name,texture){this.changes.push([name,texture]);}};
 return f;
}
for(const [id,expected] of [[51019,1],[51016,1],[51017,2],[651026,1],[758001,8],[71001,7],[51022,6],[34003,4]]){
 const p={table_id:id};const x=fig();
 assert.equal(factionOf(p),expected);
 assert(nativeFaction(x,p),'Must show actual faction '+id);
 assert.equal(x.changes[0][0],'zhiye','Must clear baked icon in native slot');
 assert.equal(x.changes[0][1],PIXI.Texture.EMPTY);
 assert.equal(x.slotContainers[0].children[0].src,'/assets/factions/'+expected+'.png');
 assert(Math.abs(x.slotContainers[0].children[0].scaling[1]+60/(expected===8?256:46))<.00001,
   'All faction badges must display at 60px independent of source dimensions');
}
const unknown=fig();
assert.equal(nativeFaction(unknown,{table_id:99999999}),false);
assert.equal(unknown.changes.length,1,'Never leave incorrect blue icon for unknown girls');
assert.equal(unknown.slotContainers[0].children.length,0);
assert(html.includes('/summon-anim.js?v=20261123-faction-reveal-r6'));
assert(html.includes('/wish.js?v=20261123-sonia-hard150-r9'));
console.log('PASS: native faction in original gacha slot for Raenvya, Diana, all factions 1–8 and S4 Wish.');
