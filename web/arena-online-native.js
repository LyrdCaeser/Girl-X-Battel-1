'use strict';
// Restored ArenaWindow / Arena3v3Window presentation. All opponents, seasons,
// rankings, scores, lineups and results come from authenticated online services.
// Never call local arena simulators, seed fake rivals, or forge match outcomes.
const NativeOnlineArenas=(()=>{
 let mode='arena',origin='home',data=null,panel='',note='',busy=false,draft=null,teamIndex=0,defenseDraft=null,defensePos=1,attackDraft=null,attackPos=1;
 let timer=null,sequence=0,lastMatchResult=null;
 const A=n=>'/assets/arena/'+n+'.png';
 const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=String(text);return n;};
 const img=(src,cls)=>{const n=el('img',cls);n.src=src;n.alt='';n.draggable=false;return n;};
 const center=(n,x,y,w,h)=>{n.style.left='calc('+(360+x-w/2)+' * var(--u))';n.style.top='calc('+(640-y-h/2)+' * var(--u))';n.style.width='calc('+w+' * var(--u))';if(h!=null)n.style.height='calc('+h+' * var(--u))';return n;};
 const fmt=n=>typeof number==='function'?number(Number(n||0)):String(n||0);
 const title=()=>mode==='arena3v3'?'Đấu Trường Đội':mode==='cross'?'Đấu Trường Liên Server':'Đấu Trường';
 const activeView=()=>mode==='arena3v3'?'arena3v3':'arena';
 const selected=()=>view===activeView();
 const root=()=>{
  const id=activeView()+'-view';let r=$(id);
  if(!r){r=el('section','arena-view'+(mode==='arena3v3'?' a3-view':''));r.id=id;r.hidden=true;$('home-systems-view').after(r);}
  return r;
 };
 const own=()=>String(state?.uid||'');
 const opponent=m=>String(m?.player_a)===own()?
  {uid:m.player_b,name:m.name_b,power:m.power_b,server_id:m.server_b}:
  {uid:m?.player_a,name:m?.name_a,power:m?.power_a,server_id:m?.server_a};
 function stop(){if(timer){clearInterval(timer);timer=null;}}
 function beginPoll(){stop();timer=setInterval(()=>{
  if(!selected()){stop();return;}
  // An inspected opponent profile belongs to the current Arena stage. Do not
  // rebuild that stage underneath it; polling resumes after the player closes it.
  if(panel==='teams'||busy||root().querySelector('.ar-inspect'))return;
  refresh(true);
 },5000);}
 async function open(which='arena',from='home'){
  if(!state?.items){GirlUI.notice('Hồ sơ người chơi đang tải. Vui lòng thử lại.',{title:'Đấu Trường'});return;}
  mode=['arena','cross','arena3v3'].includes(which)?which:'arena';origin=from||view||'home';
  data=null;panel='';note='';lastMatchResult=null;draft=null;teamIndex=0;defenseDraft=null;defensePos=1;attackDraft=null;attackPos=1;stop();
  root();showView(activeView());render();await refresh();beginPoll();
 }
 function back(){stop();data=null;panel='';showView(origin===activeView()?'home':origin);}
 async function refresh(quiet=false){
  const stamp=++sequence;
  try{const next=await api('/api/pvp/status?mode='+encodeURIComponent(mode));
   if(stamp!==sequence||!selected())return;
   // Each participant must keep an authenticated ready heartbeat alive; 3v3
   // ticket payment is forbidden until BOTH real players are active.
   if(next?.pvp?.status==='matched'&&next.pvp.match?.id){
    try{const ready=await api('/api/pvp/match/heartbeat',{match_id:next.pvp.match.id,ready:true});
      if(ready?.match)next.pvp.match=ready.match;
    }catch(err){note=err.message||'Không thể kết nối trận đấu với đối thủ thật';}
   }
   if(stamp!==sequence||!selected())return;
   data=next;
   if(Number.isFinite(Number(next?.own_power)))state.power=Number(next.own_power);
   if(!quiet&&!note)note='';render();
  }catch(e){if(stamp!==sequence||!selected())return;note=e.message||'Không tải được đấu trường từ máy chủ';render();}
 }
 async function post(url,body){
  if(busy)return null;busy=true;try{
   const result=await api(url,body);
   if(result?.state)state=result.state;
   note='';return result;
  }catch(e){note=e.message||'Máy chủ chưa xử lý được yêu cầu';GirlUI.notice(note,{title:title()});return null;}
  finally{busy=false;await refresh();}
 }
 async function queue(action){
  if(mode==='arena3v3'&&action==='join'&&!validTeams(data?.arena3v3?.teams)){
   panel='teams';render();return;
  }
  const r=await post('/api/pvp/queue',{action,mode});if(r)panel='';
 }
 async function challenge(player){
  if(mode==='arena3v3'&&!validTeams(data?.arena3v3?.teams)){panel='teams';render();return;}
  const r=await post('/api/pvp/challenge',{mode,target_uid:player.uid,target_server:player.server_id});
  if(r?.match){data.pvp=r;attackDraft=null;attackPos=1;panel=mode==='arena3v3'?'match':'attack';render();}
 }
 function validTeams(teams){return Array.isArray(teams)&&teams.length===3
  &&teams.every(t=>Array.isArray(t)&&t.length>=1&&t.length<=6)
  &&new Set(teams.flat().map(x=>Number(x.partner_id))).size===teams.flat().length;}
 // Original Arena3v3BattleFormationWindow begins with three EMPTY teams
 // until the player explicitly selects Girls. Never auto-create a formation.
 function teamDraft(){
  if(!draft){
   const original=data?.arena3v3?.needs_repair?data?.arena3v3?.draft_teams:data?.arena3v3?.teams;
   draft=Array.isArray(original)&&original.length===3&&original.every(Array.isArray)
     ?JSON.parse(JSON.stringify(original)):[[],[],[]];
  }
  return draft;
 }
 async function saveTeams(){
  const teams=teamDraft();
  if(!validTeams(teams)){GirlUI.notice('Cần đủ 3 đội, mỗi đội 1–6 Nữ Thần khác nhau.',{title:title()});return;}
  const r=await post('/api/pvp/arena3v3/teams',{teams});
  if(r){draft=null;panel='';GirlUI.toast('Đã lưu ba đội hình thật trên máy chủ.');}
 }
 function defenseTeam(){
  if(!defenseDraft){
   const raw=Array.isArray(data?.defense)&&data.defense.length?data.defense:(state?.formation||[]);
   defenseDraft=JSON.parse(JSON.stringify(raw)).map(x=>({partner_id:Number(x.partner_id),pos:Number(x.pos)}));
  }
  return defenseDraft;
 }
 async function saveDefense(){
  const formation=defenseTeam();
  if(!Array.isArray(formation)||formation.length<1||formation.length>6){
   GirlUI.notice('Đội hình phòng thủ cần từ 1 đến 6 Nữ Thần.',{title:'Đội Hình Phòng Thủ'});return;
  }
  const r=await post('/api/pvp/defense',{formation});
  if(r){data.defense=r.formation;defenseDraft=null;panel='';GirlUI.toast('Đã lưu đội hình phòng thủ riêng.');}
 }
 function attackTeam(){
  if(!attackDraft){
   const roster=new Set((state?.roster||[]).map(h=>Number(h.partner_id)));
   const seen=new Set(),used=new Set();
   attackDraft=[];
   for(const x of state?.formation||[]){
    const id=Number(x.partner_id),pos=Number(x.pos);
    if(!roster.has(id)||!Number.isInteger(pos)||pos<1||pos>6||seen.has(id)||used.has(pos))continue;
    attackDraft.push({partner_id:id,pos});seen.add(id);used.add(pos);
   }
  }
  return attackDraft;
 }
 function validAttack(team){
  const owned=new Set((state?.roster||[]).map(h=>Number(h.partner_id)));
  if(!Array.isArray(team)||team.length<1||team.length>6)return false;
  const ids=new Set(),positions=new Set();
  for(const entry of team){
   const id=Number(entry.partner_id),pos=Number(entry.pos);
   if(!owned.has(id)||!Number.isSafeInteger(id)||!Number.isInteger(pos)||pos<1||pos>6
      ||ids.has(id)||positions.has(pos))return false;
   ids.add(id);positions.add(pos);
  }
  return true;
 }
 async function fightSingle(match){
  if(!match)return;
  const formation=attackTeam().map(x=>({partner_id:Number(x.partner_id),pos:Number(x.pos)}));
  if(!validAttack(formation)){
   GirlUI.notice('Hãy chọn từ 1 đến 6 Nữ Thần của mình và sắp xếp đúng vị trí trước khi chiến đấu.',
     {title:'Đội Hình Tấn Công'});panel='attack';render();return;
  }
  const session=await post('/api/pvp/match/heartbeat',{match_id:match.id,ready:true});
  if(!session)return;
  if((session.match?.status||match.status)!=='active'){
   note='Đang đợi đối thủ vào trận.';panel='match';render();return;
  }
  panel='replay-loading';render();
  const r=await post('/api/pvp/match/battle',{match_id:match.id,formation});
  if(!r?.result){panel='attack';render();return;}
  lastMatchResult=r.result;
  // The server has finalized an authentic match. Do not display the winner
  // until the saved, server-authenticated battle frames have been played.
  const playback=await post('/api/pvp/match/replay',{match_id:match.id});
  if(!playback?.report||!Array.isArray(playback.report.frames)||!playback.report.frames.length){
   note='Máy chủ đã ghi nhận trận đấu nhưng không tải được hình chiến đấu. Có thể thử xem lại.';
   panel='replay-error';render();return;
  }
  if(typeof watchEventBattle!=='function'){
   note='Không tìm thấy trình phát trận chiến. Hãy tải lại giao diện để xem trận.';
   panel='replay-error';render();return;
  }
  try{
   stop();
   await watchEventBattle({report:playback.report},activeView(),title());
   panel='result';
   // The original replay's "Tiếp tục" button returns to this Arena view.
   // Result appears only on return, never in front of the battle animation.
   if(selected())render();
  }catch(error){
   note=error.message||'Không thể phát báo cáo trận đấu thật';
   showView(activeView());panel='replay-error';render();
  }
 }
 async function pay3v3(match){const r=await post('/api/pvp/arena3v3/pay',{match_id:match.id});if(r){panel='match';render();}}
 async function replay3v3(matchId,index){
  // Playback is loaded only from the authenticated original LuaJIT report,
  // never reconstructed from the scoreboard or an artificial NPC battle.
  const reply=await post('/api/pvp/arena3v3/replay',{match_id:matchId,round:Number(index)});
  if(reply?.report&&typeof watchEventBattle==='function'){
   try{await watchEventBattle({report:reply.report},activeView(),title()+' · Lượt '+(Number(index)+1));}
   catch(error){note=error.message||'Không thể xem báo cáo chiến đấu gốc';showView(activeView());render();}
  }
 }
 async function replaySingle(matchId){
  // A finished 1v1/cross-server match keeps its original authenticated
  // LuaJIT report, so history can replay the exact battle instead of a summary.
  const reply=await post('/api/pvp/match/replay',{match_id:matchId});
  if(reply?.report&&typeof watchEventBattle==='function'){
   try{await watchEventBattle({report:reply.report},activeView(),title()+' · Xem Lại Trận Đấu');}
   catch(error){note=error.message||'Không thể xem lại trận đấu';showView(activeView());render();}
  }
 }
 async function round3v3(match,round){
  const r=await post('/api/pvp/arena3v3/round',{match_id:match.id,expected_round:round});
  if(!r)return;
  if(r.result){lastMatchResult=r.result;panel='result';}
  else {panel='match';if(r.round_report)note='Đã hoàn tất lượt '+(round+1)+' trên máy chủ.';}
  render();
  if(!r.already_resolved&&r.round_report)await replay3v3(match.id,round);
 }
 function titleArt(st){
  if(mode==='arena'||mode==='arena3v3'){
   st.append(center(img(A(mode==='arena'?'arena_title_en_en':'arena3v3_title_en_en'),'ar-title'),0,499,360,104));
  }else{
   const label=center(el('h2','ar-native-title','Đấu Trường Liên Server'),0,495,506,65);st.append(label);
  }
  const help=center(el('button','ar-icon-btn'),-316,530,53,53);
  help.type='button';help.append(img(A('help_2')));help.onclick=()=>GirlUI.notice(
    'Đấu trường thật: chọn đối thủ trong danh sách cùng bậc, cùng điểm hoặc nhỉnh hơn. '+
    'Bảng xếp hạng theo điểm; trước trận đầu tiên sẽ xếp theo lực chiến đội hình. '+
    'Không dùng ghép ngẫu nhiên, đối thủ mô phỏng hay NPC. Mỗi mùa kéo dài 30 ngày.',
    {title:title()});st.append(help);
  const shop=center(el('button','ar-icon-btn'),311,516,78,80);shop.type='button';shop.append(img(A('shop')));
  shop.onclick=()=>Shops.open('arena',5);st.append(shop);
  if(mode==='arena'){
   const team=center(el('button','ar-3v3-entry'),-248,450,166,59);team.type='button';team.append(img(A('btn_arena_3v3')));
   team.onclick=()=>Arena3v3.open('arena');st.append(team);
  }
 }
 function render(){
  if(!selected())return;
  const target=root();
  // The opponent inspector is an intentional modal owned by Arena.inspect().
  // Any in-flight status response, heartbeat or global state repaint must wait
  // until the player closes it instead of replacing the whole Arena stage.
  if(target.querySelector('.ar-inspect'))return;
  target.replaceChildren();const stage=el('div','ar-stage');target.append(stage);
  const scene=mode==='cross'?'/assets/menus/arena-cross.png':A(mode==='arena3v3'?'arena_3v3_scene':'arena_scene');
  stage.append(center(img(scene,'ar-bg'),0,5,1457,1457));
  Arena.chrome(stage,back);titleArt(stage);
  const left=Math.max(0,Number(data?.season?.seconds_left||0));
  const days=Math.floor(left/86400),hours=Math.floor((left%86400)/3600);
  stage.append(center(el('div','ar-ddl',
    !data?'Đang tải mùa Đấu Trường…':'Mùa 30 ngày · còn '+days+' ngày '+hours+' giờ'),0,448,515,30));
  const rank=center(el('div','ar-rank'),0,71,706,681);rank.style.borderImageSource="url('"+A('arena_bg')+"')";
  const rows=el('div','ar-rank-list');rank.append(rows);
  for(const [i,p] of (data?.rating_board||[]).entries()){
   const player={uid:p.uid,server_id:p.server_id,name:p.character_name,lv:p.level,
     power:p.power||0,score:p.rating,me:String(p.uid)===own(),avatar:p.avatar||'head_1001'};
   rows.append(Arena.rankRow(player,i,Number(state?.power||0),openPlayer));
  }
  if(!data)rows.append(el('p','ar-empty',note||'Đang tải bảng xếp hạng trực tuyến…'));
  else if(!(data.rating_board||[]).length)rows.append(el('p','ar-empty','Chưa có người chơi đủ dữ liệu xếp hạng.'));
  stage.append(rank);
  stage.append(center(el('div','ar-detail'),0,-395,706,232));
  const icon=center(el('div','ar-me-icon'),-290,-348,114,114);
  const avatarSrc=typeof profileAsset==='function'?profileAsset(state?.profile?.avatar||'head_1001'):'/assets/profile/head_1001.png';
  const face=img(avatarSrc,'ar-own-avatar');face.onerror=()=>{face.onerror=null;face.src='/assets/profile/head_1001.png';};icon.append(face);
  stage.append(icon);
  const power=center(el('div','ar-power'),-194,-357,110,70);
  power.append(img(A('force_icon')),el('b','',fmt(data?.own_power??state?.power??0)));stage.append(power);
  const myRow=(data?.rating_board||[]).find(p=>String(p.uid)===own());
  for(const [label,value,y] of [['Xếp hạng',myRow?.rank||'—',-421],['Điểm',Number(data?.rating?.matches||0)>0?data.rating.rating:'Chưa đấu',-465]]){
   const field=center(el('div','ar-stat '+(label==='Xếp hạng'?'ar-stat-rank':'ar-stat-score')),-230,y,170,30);field.append(el('span','',label),el('b','',value));stage.append(field);
  }
  stage.append(center(img(A('arena_decoration'),'ar-deco'),0,-411,270,164));
  const res=center(el('div','ar-res'),0,-333,220,36);
  res.append(el('span','',mode==='arena3v3'?'3 đội · Vé:':'Trận trực tuyến'),img(A('icon_34_small')),
   el('b','',fmt(mode==='arena3v3'?data?.arena3v3?.tickets??state?.items?.['34']??0:data?.rating?.matches??0)));
  stage.append(res);
  const status=data?.pvp?.status||'idle';
  const fight=center(el('button','ar-fight'),0,-419,212,77);fight.type='button';
  fight.style.backgroundImage="url('"+A('blue_btn_65_65')+"')";
  fight.textContent=status==='matched'?'Vào Trận':'Chiến đấu';
  fight.disabled=!data||busy;
  fight.onclick=()=>{panel=status==='matched'?(mode==='arena3v3'?'match':'attack'):
    mode==='arena3v3'&&!validTeams(data?.arena3v3?.teams)?'teams':'opponents';render();};
  stage.append(fight);
  const choices=[
   ['Phần thưởng','arena_award_s',-328,()=>{panel='rewards';render();}],
   ['Lịch sử','arena_record',-397,()=>{panel='history';render();}],
   [mode==='arena3v3'?'Đội hình':'Phòng thủ','arena_defence',-464,()=>{
     panel=mode==='arena3v3'?'teams':'defense';render();
   }]
  ];
  for(const [label,asset,y,action] of choices){
   const b=center(el('button','ar-side ar-side-'+asset),242,y,170,54);b.type='button';
   b.style.backgroundImage="url('"+A('white_btn_65_65')+"')";b.append(img(A(asset)),el('span','',label));
   b.onclick=action;stage.append(b);
  }
  const statusNote=note||(mode==='arena3v3'&&data?.arena3v3?.needs_repair?data.arena3v3.warning:'');
  if(statusNote)stage.append(center(el('p','ar-note',statusNote),0,-555,620,45));
  if(panel)drawPanel(stage);
 }
 async function openPlayer(p){
  const uid=String(p?.uid||''),sid=String(p?.server_id||state?.server_id||'S1');
  if(!uid)return;
  try{
   const profile=await api('/api/pvp/opponent?uid='+encodeURIComponent(uid)+
     '&server_id='+encodeURIComponent(sid)+'&mode='+encodeURIComponent(mode));
   if(p?.score!=null)profile.score=p.score;
   Arena.inspect(profile,mode==='arena3v3'?'Hồ Sơ Đấu Tổ Đội':'Hồ Sơ Đối Thủ');
  }catch(e){
   GirlUI.notice(e.message||'Không tải được hồ sơ và đội hình đối thủ.',{title:'Hồ Sơ Đối Thủ'});
  }
 }
 function drawPanel(stage){
  const ov=el('div','ar-overlay');ov.onclick=e=>{if(e.target===ov){if(panel==='defense')defenseDraft=null;panel='';render();}};
  const win=el('div','ar-win'+((panel==='teams'||panel==='defense'||panel==='attack')?' a3-win':''));ov.append(win);
  const x=el('button','ar-close','✕');x.type='button';x.onclick=()=>{if(panel==='defense')defenseDraft=null;panel='';render();};
  const heading=el('h2','',title());win.append(heading,x);
  const paragraph=text=>win.append(el('p','ar-empty',text));
  const button=(label,action,disabled=false)=>{
    const b=el('button','ar-small',label);b.type='button';b.disabled=disabled||busy;b.onclick=action;win.append(b);return b;
  };
  const p=data?.pvp||{};
  if(panel==='opponents'){
   paragraph('Chọn người chơi thật cùng bậc, cùng điểm hoặc nhỉnh hơn để So Tài.');
   const list=el('div','ar-opponents');win.append(list);
   for(const rival of data?.candidates||[]){
    const row=el('article','ar-opponent');
    const face=img(typeof profileAsset==='function'?profileAsset(rival.avatar||'head_1001'):'/assets/profile/head_1001.png','ar-opponent-avatar');
    face.onerror=()=>{face.onerror=null;face.src='/assets/profile/head_1001.png';};
    const info=el('div','ar-opponent-info');info.append(el('b','',rival.character_name),
      el('small','','Cấp '+fmt(rival.level)+' · Điểm '+fmt(rival.rating)),
      el('small','','Lực chiến '+fmt(rival.power)+' · '+rival.server_id));
    face.role='button';face.tabIndex=0;face.onclick=()=>openPlayer({
      uid:rival.uid,server_id:rival.server_id,name:rival.character_name,
      power:rival.power,score:rival.rating});
    info.role='button';info.tabIndex=0;info.onclick=face.onclick;
    const go=el('button','ar-small','So Tài');go.type='button';go.disabled=busy;go.onclick=()=>challenge(rival);
    row.append(face,info,go);list.append(row);
   }
   if(!(data?.candidates||[]).length)paragraph('Hiện chưa có đối thủ phù hợp. Hãy làm mới danh sách.');
   button('Làm mới danh sách',()=>refresh());
  }else if(panel==='match'){
   const m=p.match,opp=opponent(m),series=data?.series;
   if(!m){paragraph('Đang nhận trạng thái trận từ máy chủ.');button('Tải lại',()=>refresh());}
   else{
    paragraph('Đối thủ: '+(opp.name||opp.uid)+' · '+(opp.server_id||state?.server_id||'')+' · LC '+fmt(opp.power));
    button('Xem Hồ Sơ & Đội Hình Đối Thủ',()=>openPlayer(opp));
    if(mode==='arena3v3'){
     if(series){
      paragraph('Tỉ số: '+(series.wins_me??(String(m.player_a)===own()?series.wins_a:series.wins_b))+
        ' - '+(String(m.player_a)===own()?series.wins_b:series.wins_a));
      for(const row of series.rounds||[])paragraph('Lượt '+(Number(row.round)+1)+' · '+(row.won_by_me?'Thắng':'Thua'));
     }
     if(m.status!=='active'){
      paragraph('Đang chờ người chơi thật bên kia xác nhận vào trận. Chưa trừ vé.');
      button('Sẵn Sàng Vào Trận',()=>refresh());
     }else if(!series?.paid)button('Xác nhận 3 Vé',()=>pay3v3(m));
     else if(!series?.all_paid)button('Tải lại trạng thái vé',()=>refresh());
     else if(series?.complete)button('Nhận Kết Quả Loạt Đấu',()=>round3v3(m,Number(series.next_round||0)));
     else button('Thi đấu lượt '+(Number(series.next_round||0)+1),()=>round3v3(m,Number(series.next_round||0)));
    }else if(m.status==='active')button('Chọn Đội Hình Tấn Công',()=>{panel='attack';render();});
    else{paragraph('Đang chờ đối thủ thật xác nhận sẵn sàng.');button('Sẵn Sàng Vào Trận',()=>refresh());}
    button('Tải lại',()=>refresh());
   }
  }else if(panel==='attack'){
   drawAttack(win,button);
  }else if(panel==='replay-loading'){
   paragraph('Đang tải khung hình chiến đấu từ máy chủ…');
  }else if(panel==='replay-error'){
   paragraph(note||'Không thể tải trận chiến.');
   const m=p.match||lastMatchResult;
   if(m?.id)button('▶ Phát Lại Trận Đấu',async()=>{
     const replay=await post('/api/pvp/match/replay',{match_id:m.id});
     if(!replay?.report)return;
     try{stop();await watchEventBattle({report:replay.report},activeView(),title());panel='result';if(selected())render();}
     catch(e){note=e.message||'Không phát được trận đấu';panel='replay-error';render();}
   });
  }else if(panel==='rewards'){
   const r=data?.season_reward;
   if(!r)paragraph('Máy chủ chưa trả dữ liệu thưởng mùa.');
   else{
    paragraph('Thưởng mùa '+(r.season_id||'—')+' · '+(r.eligible?'Đủ điều kiện':'Chưa đủ điều kiện'));
    if(r.reward)paragraph(Object.entries(r.reward).map(([id,n])=>id+' × '+fmt(n)).join(' · '));
    button(r.claimed?'Đã nhận thưởng':'Nhận thưởng',async()=>{const s=await post('/api/pvp/season/claim',{mode});if(s){panel='';render();}},!r.eligible||r.claimed);
   }
  }else if(panel==='history'){
   const rows=(data?.history||[]).filter(x=>x.mode===mode);
   for(const h of rows.slice(0,25)){
    const o=opponent(h),won=h.winner_uid===own();
    win.append(el('div','ar-rec '+(won?'win':'lose'),(won?'Thắng':'Thua')+' · '+(o.name||o.uid)+' · '+new Date(h.created_at*1000).toLocaleString()));
    if(h.mode==='arena3v3')for(const step of h.arena3v3_rounds||[]){
     const n=Number(step.round);
     if(Number.isInteger(n)&&n>=0&&n<3)
      button('▶ Xem Lượt '+(n+1),()=>replay3v3(h.id,n));
    }
    else button('▶ Xem Lại Trận Đấu',()=>replaySingle(h.id));
   }
   if(!rows.length)paragraph('Chưa có trận nào trong lịch sử thực.');
  }else if(panel==='defense'){
   drawDefense(win,button);
  }else if(panel==='teams'){
   drawTeams(win,button);
  }else if(panel==='result'){
   const r=lastMatchResult||{},report=r.battle_report||{},mine=own();
   paragraph('Kết quả do máy chủ xác nhận: '+(String(r.winner_uid)===mine?'Chiến thắng':'Thất bại'));
   paragraph('Số hiệp: '+(report.total_round??report.series?.rounds?.length??'—'));
   if(mode==='arena3v3'&&r.id)for(const step of report.series?.rounds||[]){
    const n=Number(step.round);
    if(Number.isInteger(n)&&n>=0&&n<3)
     button('▶ Xem Lượt '+(n+1),()=>replay3v3(r.id,n));
   }
   button('Xem bảng xếp hạng',()=>{panel='';lastMatchResult=null;refresh();});
  }
  stage.append(ov);
 }
 function nativeCardStars(hero,extraClass=''){
  const n=Number(hero?.stars)||0;
  const wrap=el('span','ar-native-stars'+(extraClass?' '+extraClass:''));
  wrap.setAttribute('aria-label',n+' sao');
  // Use the exact original card star textures / awakening emblem.
  if(typeof GirlUI!=='undefined'&&typeof GirlUI.stars==='function'){
   wrap.append(GirlUI.stars(n,'card'));
  }else wrap.append(el('span','ar-native-star-fallback',n+'★'));
  return wrap;
 }
 function drawAttack(win,button){
  const match=data?.pvp?.match;
  if(!match){win.append(el('p','ar-empty','Chưa có trận được xác nhận.'));return;}
  if(String(match.player_a)!==own()){
    win.append(el('p','ar-empty','Đang chờ người thách đấu chọn đội hình và bắt đầu trận.'));
    button('Làm mới trận đấu',()=>refresh());return;
  }
  const team=attackTeam(),roster=state?.roster||[],used=new Set(team.map(x=>Number(x.partner_id)));
  win.append(el('h3','ar-defense-title','Đội Hình Tấn Công'));
  win.append(el('p','ar-defense-help',
    'Chọn Nữ Thần từ danh sách bên dưới. Hai vị trí hàng trước và bốn vị trí hàng sau; chạm Nữ Thần trên ô để tháo ra. Đội hình chỉ dùng cho trận này.'));
  const board=el('div','ar-defense-board');
  for(const [label,positions,kind] of [['Hàng Trước',[1,2],'front'],['Hàng Sau',[3,4,5,6],'back']]){
   const row=el('section','ar-defense-row '+kind);
   row.append(el('b','ar-defense-label',label));
   const slots=el('div','ar-defense-slots');
   for(const pos of positions){
    const member=team.find(x=>Number(x.pos)===pos);
    const hero=member&&roster.find(h=>Number(h.partner_id)===Number(member.partner_id));
    const slot=el('button','ar-defense-slot'+(hero?' full':'')+(attackPos===pos?' active':''));
    slot.type='button';
    slot.title=hero?'Gỡ '+(hero.name||'Nữ Thần'):'Vị trí '+pos;
    if(hero){
     if(typeof portrait==='function')slot.append(portrait(hero.table_id,72,hero));
     slot.append(nativeCardStars(hero,'ar-attack-slot-stars'));
    }else slot.append(el('span','','+'),el('small','',String(pos)));
    slot.onclick=()=>{
     attackPos=pos;
     if(member)attackDraft=team.filter(x=>Number(x.pos)!==pos);
     render();
    };
    slots.append(slot);
   }
   row.append(slots);board.append(row);
  }
  win.append(board);
  const pool=el('div','ar-defense-pool');
  for(const hero of roster){
   const id=Number(hero.partner_id),chosen=used.has(id);
   const b=el('button','ar-defense-candidate'+(chosen?' used':''));b.type='button';
   if(typeof portrait==='function')b.append(portrait(hero.table_id,90,hero));
   b.append(nativeCardStars(hero,'ar-attack-candidate-stars'));
   b.title=(hero.name||'Nữ Thần')+' · '+(hero.stars||0)+'★ · Cấp '+(hero.lv||1);
   b.onclick=()=>{
    if(chosen){attackDraft=team.filter(x=>Number(x.partner_id)!==id);render();return;}
    attackDraft=team.filter(x=>Number(x.pos)!==attackPos);
    attackDraft.push({partner_id:id,pos:attackPos});
    const next=[1,2,3,4,5,6].find(pos=>!attackDraft.some(x=>Number(x.pos)===pos));
    if(next)attackPos=next;
    render();
   };
   pool.append(b);
  }
  win.append(pool);
  button('Chiến Đấu',()=>fightSingle(match),!validAttack(team));
 }
 function drawDefense(win,button){
  const team=defenseTeam(),roster=state?.roster||[];
  win.append(el('h3','ar-defense-title','Đội Hình Phòng Thủ'));
  win.append(el('p','ar-defense-help','Chạm vị trí muốn xếp, sau đó chọn Nữ Thần. Đội này được lưu riêng và dùng khi người khác thách đấu.'));
  const board=el('div','ar-defense-board');
  const makeRow=(label,positions,kind)=>{
   const row=el('section','ar-defense-row '+kind);
   row.append(el('b','ar-defense-label',label));
   const slots=el('div','ar-defense-slots');
   for(const pos of positions){
    const member=team.find(x=>Number(x.pos)===pos);
    const hero=member&&roster.find(x=>Number(x.partner_id)===Number(member.partner_id));
    const slot=el('button','ar-defense-slot'+(hero?' full':'')+(defensePos===pos?' active':''));
    slot.type='button';slot.title=hero?'Chạm để bỏ '+(hero.name||'Nữ Thần'):'Chọn vị trí '+pos;
    if(hero){
     if(typeof portrait==='function')slot.append(portrait(hero.table_id,72,hero));
     slot.append(nativeCardStars(hero,'ar-defense-slot-native-stars'));
    }else slot.append(el('span','','+'),el('small','',String(pos)));
    slot.onclick=()=>{
     defensePos=pos;
     if(member)defenseDraft=team.filter(x=>Number(x.pos)!==pos);
     render();
    };
    slots.append(slot);
   }
   row.append(slots);board.append(row);
  };
  makeRow('Hàng Trước',[1,2],'front');
  makeRow('Hàng Sau',[3,4,5,6],'back');
  win.append(board);

  const used=new Set(team.map(x=>Number(x.partner_id)));
  const pool=el('div','ar-defense-pool');
  for(const hero of roster){
   const b=el('button','ar-defense-candidate'+(used.has(Number(hero.partner_id))?' used':''));
   b.type='button';b.disabled=used.has(Number(hero.partner_id));
   if(typeof portrait==='function')b.append(portrait(hero.table_id,96,hero));
   b.append(nativeCardStars(hero,'ar-defense-candidate-stars'));
   b.title=(hero.name||'Nữ Thần')+' · '+(hero.stars||0)+'★ · Cấp '+(hero.lv||1);
   b.onclick=()=>{
    const pid=Number(hero.partner_id);
    defenseDraft=team.filter(x=>Number(x.pos)!==defensePos&&Number(x.partner_id)!==pid);
    defenseDraft.push({partner_id:pid,pos:defensePos});
    const free=[1,2,3,4,5,6].find(pos=>!defenseDraft.some(x=>Number(x.pos)===pos));
    if(free)defensePos=free;
    render();
   };
   pool.append(b);
  }
  win.append(pool);
  button('Lưu Đội Hình Phòng Thủ',saveDefense,team.length<1);
 }
 function drawTeams(win,button){
  // Original Arena3v3BattleFormationWindow layout: three native team badges
  // with six positional slots each and the original candidate card grid.
  // Only the authenticated saved roster is offered; no NPC, auto-filled team,
  // random candidate or fabricated rival exists in this screen.
  const teams=teamDraft(),locked=data?.pvp?.status==='matched',roster=state?.roster||[];
  win.append(el('h3','','Bố Trận 3 Đội'));
  if(data?.arena3v3?.needs_repair)
   win.append(el('p','ar-defense-help',data.arena3v3.warning));
  const used=new Set(teams.flat().map(x=>Number(x.partner_id)));
  teams.forEach((team,i)=>{
   const row=el('div','a3-team'+(teamIndex===i?' on':''));
   row.append(img(A('arena_3v3_t'+(i+1)),'a3-badge'));
   const slots=el('div','a3-slots');
   for(let pos=1;pos<=6;pos++){
    const member=team.find(x=>Number(x.pos)===pos),hero=member&&roster.find(h=>Number(h.partner_id)===Number(member.partner_id));
    const slot=el('button','a3-slot'+(hero?' full':''));slot.type='button';slot.disabled=locked;
    slot.title=hero?(hero.name||'Nữ Thần')+' · '+(hero.stars||0)+'★':'Đội '+(i+1)+' · Vị trí '+pos;
    if(hero){
     if(typeof portrait==='function')slot.append(portrait(hero.table_id,56,hero));
     slot.append(nativeCardStars(hero,'a3-slot-native-stars'));
     slot.onclick=()=>{teams[i]=team.filter(x=>Number(x.pos)!==pos);teamIndex=i;render();};
    }else slot.onclick=()=>{teamIndex=i;render();};
    slots.append(slot);
   }
   row.append(slots);row.onclick=e=>{if(!e.target.closest('.a3-slot')){teamIndex=i;render();}};
   win.append(row);
  });
  if(!locked){
   const pool=el('div','a3-pool');
   for(const hero of roster){
    if(used.has(Number(hero.partner_id)))continue;
    const b=el('button','a3-cand');b.type='button';
    if(typeof portrait==='function')b.append(portrait(hero.table_id,56,hero));
    b.append(nativeCardStars(hero,'a3-candidate-native-stars'));
    b.title=(hero.name||'Nữ Thần')+' · '+(hero.stars||0)+'★ · Cấp '+(hero.lv||1);
    b.onclick=()=>{
     const team=teams[teamIndex];if(team.length>=6)return;
     const free=[1,2,3,4,5,6].find(x=>!team.some(y=>Number(y.pos)===x));
     if(!free)return;
     team.push({partner_id:Number(hero.partner_id),pos:free});render();
    };pool.append(b);
   }win.append(pool);
   button('Lưu 3 đội hình gốc trên máy chủ',saveTeams,!validTeams(teams));
  }else win.append(el('p','ar-empty','Không đổi đội hình khi trận trực tuyến đã ghép.'));
 }
 function currentMode(){return mode;}
 function isActive(viewName){return selected()&&viewName===activeView();}
 return {open,render,refresh,isActive,currentMode,stop};
})();
