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
 let simulatedMatch=null,heartbeatReady=false,simulatedMatchMode='arena3v3',seriesAllPaid=false;const replays=[];
 const dataFor=mode=>({
  rating:{season_id:'2026-11',rating:1140,wins:4,losses:1,matches:5},
  rating_board:[
   {rank:1,uid:'PLAYER-ALPHA',server_id:'S2',character_name:'Người Chơi Thật',rating:1211,wins:3,losses:2,level:51,power:12344},
   {rank:2,uid:'PLAYER-SELF',server_id:'S1',character_name:'Chủ Tài Khoản',rating:1140,wins:4,losses:1,level:61,power:23445}
  ],
  pvp:simulatedMatch&&mode===simulatedMatchMode?{status:'matched',match:{...simulatedMatch}}:{status:'idle'},history:[],
  series:simulatedMatch&&mode==='arena3v3'?{paid:seriesAllPaid,all_paid:seriesAllPaid,rounds:[],wins_a:0,wins_b:0,next_round:0}:undefined,
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
  watchEventBattle:async(data,origin,label)=>{replays.push({data,origin,label});},
  Shops:{open:()=>{}},
  api:async(url,body)=>{
   calls.push({url,body});
   if(url.startsWith('/api/pvp/status'))return dataFor(new URL('https://example.test'+url).searchParams.get('mode'));
   if(url==='/api/pvp/match/heartbeat')return {match:{...simulatedMatch,status:heartbeatReady?'active':'ready'}};
   if(url==='/api/pvp/queue')return {status:'waiting'};
   if(url==='/api/pvp/arena3v3/teams')return {ok:true,teams:body.teams};
   if(url==='/api/pvp/match/battle')return {result:{winner_uid:'PLAYER-SELF',battle_report:{total_round:2}}};
   if(url==='/api/pvp/match/replay')return {report:{frames:[{pos:1,round:1,buffs:[]}],isWin:1,display_units:[]}};
   if(url==='/api/pvp/arena3v3/round')return {round_report:{isWin:1,total_round:4},already_resolved:false,series:{wins_a:1,wins_b:0}};
   if(url==='/api/pvp/arena3v3/replay')return {report:{frames:[{pos:1,round:1,buffs:[]}],isWin:1,display_units:[]}};
   throw Error('Unexpected request '+url);
  }
 });
 vm.runInContext(fs.readFileSync(path.join(ROOT,'web/arena-online-native.js'),'utf8'),ctx);
 return {ctx,roots,calls,rows,notifications,replays,match:(ready=false,matchMode='arena3v3',allPaid=false)=>{simulatedMatchMode=matchMode;seriesAllPaid=allPaid;simulatedMatch={id:'M-REAL-1',status:'ready',player_a:'PLAYER-SELF',player_b:'PLAYER-ALPHA',name_a:'Chủ Tài Khoản',name_b:'Người Chơi Thật',server_a:'S1',server_b:'S1'};heartbeatReady=ready;}};
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
 // A finished single PvP battle must replay the authentic server report,
 // without accepting frames/winner supplied by the browser.
 const single=makeContext();single.match(true,'arena');
 await vm.runInContext('NativeOnlineArenas',single.ctx).open('arena','home');
 const singleFight=single.roots['arena-view'].descendants.find(n=>n.className==='ar-fight');
 singleFight.onclick();
 const enter=single.roots['arena-view'].descendants.find(n=>n.textContent==='Vào trận với đối thủ thật');
 assert(enter,'only an active real match may enter combat');
 await enter.onclick();
 assert(single.calls.some(c=>c.url==='/api/pvp/match/battle'&&c.body?.match_id==='M-REAL-1'));
 assert(single.calls.some(c=>c.url==='/api/pvp/match/replay'&&c.body?.match_id==='M-REAL-1'));
 assert.equal(single.replays.length,1,'original LuaJIT replay is rendered once after match resolution');
 assert.equal(single.replays[0].data.report.isWin,1);
 // Three-team Arena must replay each committed LuaJIT round, not a fake
 // clip derived from the match winner/scoreboard.
 const series=makeContext();series.match(true,'arena3v3',true);
 await vm.runInContext('NativeOnlineArenas',series.ctx).open('arena3v3','home');
 series.roots['arena3v3-view'].descendants.find(n=>n.className==='ar-fight').onclick();
 const startRound=series.roots['arena3v3-view'].descendants.find(n=>n.textContent==='Thi đấu lượt 1');
 assert(startRound,'ready/paid 3v3 match can run native first round');
 await startRound.onclick();
 assert(series.calls.some(c=>c.url==='/api/pvp/arena3v3/round'&&c.body?.expected_round===0));
 assert(series.calls.some(c=>c.url==='/api/pvp/arena3v3/replay'&&c.body?.round===0));
 assert.equal(series.replays.length,1,'real 3v3 round is replayed exactly once');
 assert.equal(series.replays[0].label.includes('Lượt 1'),true);
 console.log('PASS | original native Junior Varsity, three-team and cross-server screens use only real PVP data and queue APIs');
})().catch(e=>{console.error(e);process.exitCode=1;});
