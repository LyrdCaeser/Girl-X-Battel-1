'use strict';
// Browser-free native Arena prefab online smoke: real people only, server actions.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const ROOT=path.resolve(__dirname,'..');
class Node{
 constructor(tag){this.tag=tag;this.children=[];this.style={};this.className='';this.textContent='';this.hidden=false;this.dataset={};}
 append(...a){this.children.push(...a);this.lastChild=this.children.at(-1);}
 replaceChildren(...a){this.children=[];this.append(...a);}
 after(n){this.children.push(n);}
 get descendants(){return [...this.children.flatMap(x=>[x,...(x.descendants||[])])];}
 querySelector(q){return this.descendants.find(x=>q.startsWith('.')?x.className?.split(' ').includes(q.slice(1)):x.id===q.slice(1))||null;}
 querySelectorAll(q){return this.descendants.filter(x=>x.className?.split(' ').includes(q.slice(1)));}
}
function makeContext(){
 const roots={},calls=[],rows=[],notifications=[];
 let simulatedMatch=null,heartbeatReady=false;
 const dataFor=mode=>({
  rating:{season_id:'2026-11',rating:1140,wins:4,losses:1,matches:5},
  rating_board:[
   {rank:1,uid:'PLAYER-ALPHA',server_id:'S2',character_name:'Người Chơi Thật',rating:1211,wins:3,losses:2,level:51,power:12344},
   {rank:2,uid:'PLAYER-SELF',server_id:'S1',character_name:'Chủ Tài Khoản',rating:1140,wins:4,losses:1,level:61,power:23445}
  ],
  pvp:simulatedMatch&&mode==='arena3v3'?{status:'matched',match:{...simulatedMatch}}:{status:'idle'},history:[],
  series:simulatedMatch&&mode==='arena3v3'?{paid:false,all_paid:false,rounds:[],wins_a:0,wins_b:0,next_round:0}:undefined,
  arena3v3:mode==='arena3v3'?{teams:[
   [{partner_id:1,pos:1}],[{partner_id:2,pos:1}],[{partner_id:3,pos:1}]],tickets:11,ticket_cost:3}:undefined,
 });
 const ctx=vm.createContext({
  document:{createElement:tag=>new Node(tag),querySelector:()=>null},
  window:{},state:{uid:'PLAYER-SELF',server_id:'S1',items:{'1':100,'2':200,'34':11},power:22222,
   roster:[{partner_id:1,table_id:41001,name:'A',lv:60,stars:6},
           {partner_id:2,table_id:41002,name:'B',lv:60,stars:6},
           {partner_id:3,table_id:41003,name:'C',lv:60,stars:6}]},
  view:'home',number:x=>String(x),portrait:(id)=>{const n=new Node('span');n.textContent='Portrait '+id;return n;},
  $:id=>(roots[id]??=new Node('section')),
  showView:function(v){ctx.view=v;},setInterval:()=>1,clearInterval:()=>{},
  Arena:{chrome:(stage)=>{const n=new Node('div');n.className='ar-top';stage.append(n);},
   rankRow:(p)=>{rows.push(p);const n=new Node('div');n.className='ar-row2';n.textContent=p.name+' '+p.server_id+' '+p.score;return n;}},
  Arena3v3:{open:()=>{}},
  GirlUI:{notice:(m)=>notifications.push(m),toast:(m)=>notifications.push(m)},
  Shops:{open:()=>{}},
  api:async(url,body)=>{
   calls.push({url,body});
   if(url.startsWith('/api/pvp/status'))return dataFor(new URL('https://example.test'+url).searchParams.get('mode'));
   if(url==='/api/pvp/match/heartbeat')return {match:{...simulatedMatch,status:heartbeatReady?'active':'ready'}};
   if(url==='/api/pvp/queue')return {status:'waiting'};
   if(url==='/api/pvp/arena3v3/teams')return {ok:true,teams:body.teams};
   throw Error('Unexpected request '+url);
  }
 });
 vm.runInContext(fs.readFileSync(path.join(ROOT,'web/arena-online-native.js'),'utf8'),ctx);
 return {ctx,roots,calls,rows,notifications,match:(ready=false)=>{simulatedMatch={id:'M-REAL-1',status:'ready',player_a:'PLAYER-SELF',player_b:'PLAYER-ALPHA',name_a:'Chủ Tài Khoản',name_b:'Người Chơi Thật',server_a:'S1',server_b:'S1'};heartbeatReady=ready;}};
}
(async()=>{
 const {ctx,roots,calls,rows,notifications,match}=makeContext();
 await vm.runInContext('NativeOnlineArenas',ctx).open('arena','home');
 assert.equal(ctx.view,'arena');
 assert.equal(rows.length,2,'the native original rank sprite receives only actual server characters');
 assert.equal(rows[0].name,'Người Chơi Thật');
 assert.equal(rows[0].server_id,'S2','preserve server identity, not invented S1');
 const markup=roots['arena-view'].descendants;
 assert(markup.some(n=>n.src?.includes('arena_scene.png')),'original Junior Varsity background');
 assert(markup.some(n=>n.src?.includes('arena_title_en_en.png')),'original Junior Varsity title image');
 assert(markup.some(n=>n.style?.backgroundImage?.includes('white_btn_65_65.png')),
        'original 65x65 white sprite is present for reward/history/defense buttons');
 const fight=markup.find(n=>n.className==='ar-fight');
 fight.onclick();
 const join=roots['arena-view'].descendants.find(n=>n.textContent==='Ghép trận');
 assert(join,'native original matchmaking panel');
 await join.onclick();
 assert(calls.some(c=>c.url==='/api/pvp/queue'&&c.body?.action==='join'&&c.body.mode==='arena'));
 await vm.runInContext('NativeOnlineArenas',ctx).open('cross','home');
 assert(roots['arena-view'].descendants.some(n=>n.src?.includes('arena-cross.png')),
        'original cross-server Arena art, not generic dark online popup');
 assert(calls.some(c=>c.url.includes('/api/pvp/status?mode=cross')));
 await vm.runInContext('NativeOnlineArenas',ctx).open('arena3v3','home');
 assert.equal(ctx.view,'arena3v3');
 assert(roots['arena3v3-view'].descendants.some(n=>n.src?.includes('arena_3v3_scene.png')),
        'three-team Arena uses original 3v3 scenery');
 assert(calls.some(c=>c.url.includes('/api/pvp/status?mode=arena3v3')));
 match(false);
 await vm.runInContext('NativeOnlineArenas',ctx).open('arena3v3','home');
 const go=roots['arena3v3-view'].descendants.find(n=>n.className==='ar-fight');go.onclick();
 assert(roots['arena3v3-view'].descendants.some(n=>n.textContent==='Sẵn Sàng Vào Trận'),
        'no ticket charge before both real peers are active');
 assert(!roots['arena3v3-view'].descendants.some(n=>n.textContent==='Xác nhận 3 Vé'),
        'cannot charge ticket while opponent is not ready');
 assert(calls.some(c=>c.url==='/api/pvp/match/heartbeat'&&c.body?.match_id==='M-REAL-1'));
 assert.equal(notifications.length,0);
 console.log('PASS | original native Junior Varsity, three-team and cross-server screens use only real PVP data and queue APIs');
})().catch(e=>{console.error(e);process.exitCode=1;});
