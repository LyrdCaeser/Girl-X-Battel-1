'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const ROOT=path.resolve(__dirname,'..');
class N{
 constructor(tag){this.tag=tag;this.children=[];this.style={};this.className='';this.textContent='';this.hidden=false;this.dataset={};this.value='';this.classList={toggle:()=>{},add:()=>{},remove:()=>{}};}
 append(...xs){this.children.push(...xs);this.lastChild=this.children.at(-1);this.lastElementChild=this.lastChild;this.firstChild=this.children[0];}
 prepend(...xs){this.children.unshift(...xs);this.lastChild=this.children.at(-1);this.firstChild=this.children[0];}
 replaceChildren(...xs){this.children=[];this.append(...xs);}
 after(n){this.children.push(n);}
 get descendants(){return this.children.flatMap(x=>[x,...(x.descendants||[])]);}
 querySelector(q){return this.descendants.find(x=>q.startsWith('.')?x.className?.split(' ').includes(q.slice(1)):x.id===q.slice(1))||null;}
 querySelectorAll(q){return this.descendants.filter(x=>x.className?.split(' ').includes(q.slice(1)));}
}
(async()=>{
 const roots={},calls=[],originalNavigation=[];
 const realMember={uid:'P1',server_id:'S1',character_name:'Nhân Vật Thật',role:'leader',avatar:'head_1001',power:4000,contribution:5,joined_at:100,last_seen:Math.floor(Date.now()/1000)};
 const owned={id:18,server_id:'S1',name:'Bang Hội Thật',notice:'Thông báo lưu Neon',role:'leader',
   members:[realMember,{uid:'P2',server_id:'S1',character_name:'Người Chơi 2',role:'member',avatar:'partner_avatar_5501104',power:125,contribution:0,joined_at:100,last_seen:Math.floor(Date.now()/1000)}],member_count:2,activity:{
    has:true,unlocked:true,flag:1,level:1,exp:0,base_exp:0,next_exp:100,capacity:20,
    created:1700000000,checked_in:false,sign_in:{coin:'4#25',exp:10},log:[],
    mill:{gold:0,level:1,max_level:2,factor:10000,next_gold:100,donate:'1#100'},
    orders:{open:false,open_level:3,slots:3,list:[],refresh_at:0},
    boss:{current:1,cleared:[],fights:0,cost:{},fight_at:0,max:10,exp_left:5}
   }};
 const ctx=vm.createContext({
  document:{createElement:x=>new N(x)},
  window:{},state:{uid:'P1',server_id:'S1',name:'Nhân Vật Thật',level:33,roster:[{table_id:41001}],items:{'1':2000,'2':300,'4':10}},
  view:'home',$:id=>(roots[id]??=new N('section')),
  showView:function(v){ctx.view=v;},number:n=>String(n),
  itemCatalog:{},itemPicture:()=>null,portrait:id=>{const x=new N('portrait');x.textContent=String(id);return x;},
  GirlUI:{toast:()=>{},win:()=>({body:new N('div'),close:()=>{}}),confirm:async()=>true},
  Shops:{open:(origin,id)=>originalNavigation.push({name:'shop',origin,id})},
  GuildLab:{open:(origin)=>originalNavigation.push({name:'lab',origin})},
  setInterval:()=>1,clearInterval:()=>{},setTimeout,clearTimeout,
  api:async(url,req)=>{
   calls.push({url,req});
   if(url==='/assets/guild.json')return {names:{},text:{},bosses:[],flags:[1],mill:{'1':{all_gold:0}},};
   if(url==='/api/world-guild')return {guild:owned,guilds:[{id:18,name:'Bang Hội Thật',level:1,member_count:1}],ranking:[],wars:[],chat:[],applications:[]};
   if(url==='/api/world-guild/activity')return {state:ctx.state,got:{'4':25}};
   throw Error('Unexpected guild endpoint '+url);
  }
 });
 vm.runInContext(fs.readFileSync(path.join(ROOT,'web/guild.js'),'utf8'),ctx);
 const guild=vm.runInContext('Guild',ctx);
 await guild.openOnline('guild','home');
 assert.equal(ctx.view,'guild');
 assert(calls.some(c=>c.url==='/api/world-guild'),'must read authenticated guild');
 assert(!calls.some(c=>c.url==='/api/guild/action'),'never call local fake guild backend');
 const nodes=roots['guild-view'].descendants;
 const contents=nodes.map(n=>n.textContent).filter(Boolean).join(' / ');
 assert(contents.includes('Bang Hội Thật'),'original native office displays real guild name');
 assert(contents.includes('Nhân Vật Thật'),'member from real Neon membership table');
 assert(!contents.includes('No applications: simulated'),'local bot placeholder is never presented');
 assert(nodes.some(n=>n.className?.includes('gd2-stage')),'original 720x1280 Guild window');
 assert(nodes.some(n=>n.src?.includes('guild_bg03')),'original Guild Office art is retained');
 assert(nodes.some(n=>n.src?.includes('/assets/avatar-hd/profile/head_1001.webp')),
        'leader portrait must use actual public Neon avatar key');
 assert(nodes.some(n=>n.src?.includes('/assets/avatar-hd/profile/partner_avatar_5501104.webp')),
        'other members must use actual private-to-public profile avatars instead of fake placeholders');
 const guildStore=nodes.find(n=>n.textContent==='Cửa Hàng Bang Hội');
 const lab=nodes.find(n=>n.textContent==='Phòng Nghiên Cứu');
 assert(guildStore&&lab,'original Guild Shop and Lab are reachable from online Office');
 guildStore.onclick();lab.onclick();
 assert.deepEqual(originalNavigation,[{name:'shop',origin:'guild',id:6},{name:'lab',origin:'guild'}],
                 'existing Guild Shop ID 6 and original research subsystem are reused, never reimplemented');
 const sign=nodes.find(n=>n.textContent==='Điểm Danh');
 assert(sign,'original office sign-in is present');
 await sign.onclick();
 assert(calls.some(c=>c.url==='/api/world-guild/activity'&&c.req.action==='checkin'),
        'original native Guild Sign In must execute authenticated Neon activity');
 assert(!calls.some(c=>c.url==='/api/guild/action'),'no fake membership actions');
 console.log('PASS | original Office Guild prefab displays real Neon guild members, and signs in through world-guild activity');
})().catch(e=>{console.error(e);process.exitCode=1;});
