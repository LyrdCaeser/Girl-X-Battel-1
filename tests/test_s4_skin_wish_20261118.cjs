'use strict';
// Isolated DOM checks for the S4 Wish 104-goddess and 324-skin flow.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('web/home-menus.js','utf8');
const fn=source.slice(source.indexOf(' function revealS4Skins('),source.indexOf(' async function revealS4Bundle(prize){')).trim();
assert(fn.startsWith('function revealS4Skins('));
function E(tag='',text,cls){
 this.tag=tag;this.textContent=text??'';this.className=cls||'';this.children=[];this.style={};this.removed=false;
 const classes=new Set((cls||'').split(/\s+/).filter(Boolean));
 this.classList={add:k=>classes.add(k),remove:k=>classes.delete(k),contains:k=>classes.has(k)};
 this.append=(...children)=>this.children.push(...children);
 this.replaceChildren=(...children)=>{this.children=[...children]};
 this.remove=()=>{this.removed=true};
 this.focus=()=>{};
 this.querySelector=()=>null;
}
const root=new E('root');
const context={
 el:(tag,text,cls)=>new E(tag,text,cls),
 window:{GxbFrame:{root:()=>root},GxbBagVi:{t:txt=>txt==='Sunbath'?'Tắm Nắng':txt}},
 document:{body:root},
 girlIconSource:tid=>'/assets/cards/partner_card_'+tid+'.png',
 state:{server_id:'S4'},
 Number,Map,Promise
};
const reveal=vm.runInNewContext('('+fn+')',context);
const prize={
 wish_count:104,skin_count:324,catalog_total:104,skin_catalog_total:324,outfit_total:242,
 goddesses:Array.from({length:104},(_,i)=>({table_id:751001+i,name:'Nữ Thần '+i,stars:25})),
 skin_ids:Array.from({length:324},(_,i)=>7001+i),
 skin_details:Array.from({length:324},(_,i)=>({id:7001+i,name:i===0?'Sunbath':'Trang phục '+i}))
};
(async()=>{
 let done=false;
 const promise=reveal(prize,'goddesses').then(()=>done=true);
 const girls=root.children.at(-1),head=girls.children[0],body=girls.children[1],foot=girls.children[2];
 const cards=body.children[0].children[1];
 assert.equal(cards.children.length,12);
 assert.equal(cards.children[0].children[0].children[0].src,'/assets/cards/partner_card_751001.png');
 assert.equal(cards.children[0].children[0].children[1].textContent,'25★');
 assert(head.children[1].textContent.includes('12 / 104'));
 const [next,overview,skip]=foot.children;
 overview.onclick();
 assert.equal(cards.children.length,104,'104 unique goddess cards should be listed in gallery');
 assert(body.children[1].textContent.includes('324'));
 next.onclick();await promise;
 assert(done&&girls.removed);
 const second=reveal(prize,'skins');
 const skin=root.children.at(-1),skinHead=skin.children[0],skinBody=skin.children[1],skinFoot=skin.children[2];
 const skinCards=skinBody.children[0].children[1];
 assert.equal(skinCards.children.length,12,'Paginate skins to protect Android GPU');
 assert.equal(skinCards.children[0].children[0].children[0].src,'/assets/skins/cards/7001.webp');
 assert.equal(skinCards.children[0].children[1].children[0].textContent,'Tắm Nắng');
 assert(skinHead.children[1].textContent.includes('12 / 324'));
 skinFoot.children[2].onclick();
 assert.equal(skinCards.children.length,324);
 assert(skinCards.classList.contains('all'));
 skinFoot.children[0].onclick();await second;
 assert(skin.removed);
 context.state.server_id='S1';
 const old=root.children.length;
 await reveal(prize,'goddesses');await reveal(prize,'skins');
 assert.equal(root.children.length,old,'Never show S4 exclusive gifts in other worlds');
 const html=fs.readFileSync('web/index.html','utf8');
 assert(html.includes('home-menus.js?v=20261118-s4-complete-v2'));
 assert(html.includes('home-menus.css?v=20261118-s4-complete-v2'));
 const css=fs.readFileSync('web/home-menus.css','utf8');
 assert(css.includes('summon_scene.png'));
 assert(css.includes('hm-s4-wish-goddess'));
 assert(css.includes('@media(prefers-reduced-motion:reduce)'));
 const fragment=source.slice(source.indexOf(' async function revealS4Bundle(prize){'),source.indexOf(' async function claimServerMail(mailId){'));
 assert(fragment.includes("girls.slice(0,4),{s4:true}"),'No 104 full-screen Spine effects');
 assert(fragment.includes("revealS4Skins(prize,'goddesses')"));
 assert(fragment.includes("revealS4Skins(prize,'skins')"));
 console.log('PASS: 104 goddess Wish, 324 skins, S4-only, paging, original artwork, bounded Spine');
})().catch(e=>{console.error(e);process.exitCode=1});
