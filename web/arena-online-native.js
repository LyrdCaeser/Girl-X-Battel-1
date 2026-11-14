'use strict';
// Restored ArenaWindow / Arena3v3Window presentation. All opponents, seasons,
// rankings, scores, lineups and results come from authenticated online services.
// Never call local arena simulators, seed fake rivals, or forge match outcomes.
const NativeOnlineArenas=(()=>{
 let mode='arena',origin='home',data=null,panel='',note='',busy=false,draft=null,teamIndex=0;
 let timer=null,sequence=0,lastMatchResult=null;
 const A=n=>'/assets/arena/'+n+'.png';
 const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=String(text);return n;};
 const img=(src,cls)=>{const n=el('img',cls);n.src=src;n.alt='';n.draggable=false;return n;};
 const center=(n,x,y,w,h)=>{n.style.left='calc('+(360+x-w/2)+' * var(--u))';n.style.top='calc('+(640-y-h/2)+' * var(--u))';n.style.width='calc('+w+' * var(--u))';if(h!=null)n.style.height='calc('+h+' * var(--u))';return n;};
 const fmt=n=>typeof number==='function'?number(Number(n||0)):String(n||0);
 const title=()=>mode==='arena3v3'?'Đấu Trường Đội':mode==='cross'?'Đấu Trường Liên Server':'Junior Varsity';
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
 function beginPoll(){stop();timer=setInterval(()=>{if(!selected()){stop();return;}if(panel==='teams'||busy)return;refresh(true);},5000);}
 async function open(which='arena',from='home'){
  if(!state?.items){GirlUI.notice('Hồ sơ người chơi đang tải. Vui lòng thử lại.',{title:'Đấu Trường'});return;}
  mode=['arena','cross','arena3v3'].includes(which)?which:'arena';origin=from||view||'home';
  data=null;panel='';note='';lastMatchResult=null;draft=null;teamIndex=0;stop();
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
   data=next;if(!quiet&&!note)note='';render();
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
 function validTeams(teams){return Array.isArray(teams)&&teams.length===3
  &&teams.every(t=>Array.isArray(t)&&t.length>=1&&t.length<=6)
  &&new Set(teams.flat().map(x=>Number(x.partner_id))).size===teams.flat().length;}
 // Original Arena3v3BattleFormationWindow begins with three EMPTY teams
 // until the player explicitly selects Girls. Never auto-create a formation.
 function teamDraft(){if(!draft)draft=validTeams(data?.arena3v3?.teams)?
    JSON.parse(JSON.stringify(data.arena3v3.teams)):[[],[],[]];return draft;}
 async function saveTeams(){
  const teams=teamDraft();
  if(!validTeams(teams)){GirlUI.notice('Cần đủ 3 đội, mỗi đội 1–6 Nữ Thần khác nhau.',{title:title()});return;}
  const r=await post('/api/pvp/arena3v3/teams',{teams});
  if(r){draft=null;panel='';GirlUI.toast('Đã lưu ba đội hình thật trên máy chủ.');}
 }
 async function fightSingle(match){
  if(!match)return;
  const session=await post('/api/pvp/match/heartbeat',{match_id:match.id,ready:true});
  if(!session)return;
  if((session.match?.status||match.status)!=='active'){note='Đang đợi đối thủ vào trận.';panel='match';render();return;}
  const r=await post('/api/pvp/match/battle',{match_id:match.id});
  if(r?.result){
   lastMatchResult=r.result;panel='result';render();
   // Only play the original, stored LuaJIT combat frames. The server orients
   // all HP, targets, actors and FX for this authenticated viewer.
   const playback=await post('/api/pvp/match/replay',{match_id:match.id});
   if(playback?.report&&typeof watchEventBattle==='function'){
    try{await watchEventBattle({report:playback.report},activeView(),title());}
    catch(error){note=error.message||'Không thể phát lại báo cáo trận thật';showView(activeView());render();}
   }
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
    'Đấu trường thật: bảng xếp hạng, điểm, đối thủ và kết quả lấy từ máy chủ. '+
    'Không sử dụng đối thủ mô phỏng/NPC. '+(mode==='arena3v3'?'Mỗi trận dùng ba đội hình đã lưu, 3 Vé Đấu Trường/người.':'Ghép trận với người chơi khác đang trực tuyến.'),
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
  const target=root();target.replaceChildren();const stage=el('div','ar-stage');target.append(stage);
  const scene=mode==='cross'?'/assets/menus/arena-cross.png':A(mode==='arena3v3'?'arena_3v3_scene':'arena_scene');
  stage.append(center(img(scene,'ar-bg'),0,5,1457,1457));
  Arena.chrome(stage,back);titleArt(stage);
  const season=data?.rating?.season_id||'—';
  stage.append(center(el('div','ar-ddl','Mùa '+season+' · Máy chủ trực tuyến'),0,448,515,30));
  const rank=center(el('div','ar-rank'),0,71,706,681);rank.style.borderImageSource="url('"+A('arena_bg')+"')";
  const rows=el('div','ar-rank-list');rank.append(rows);
  for(const [i,p] of (data?.rating_board||[]).entries()){
   const player={uid:p.uid,server_id:p.server_id,name:p.character_name,lv:p.level,
     power:p.power||0,score:p.rating,me:String(p.uid)===own(),avatar:p.avatar||'head_1001'};
   rows.append(Arena.rankRow(player,i,Number(state?.power||0),openPlayer));
  }
  if(!data)rows.append(el('p','ar-empty',note||'Đang tải bảng xếp hạng trực tuyến…'));
  else if(!(data.rating_board||[]).length)rows.append(el('p','ar-empty','Chưa có trận xếp hạng thật được hoàn tất trong mùa này.'));
  stage.append(rank);
  stage.append(center(el('div','ar-detail'),0,-395,706,232));
  const icon=center(el('div','ar-me-icon'),-290,-348,114,114);
  const avatarSrc=typeof profileAsset==='function'?profileAsset(state?.profile?.avatar||'head_1001'):'/assets/profile/head_1001.png';
  const face=img(avatarSrc,'ar-own-avatar');face.onerror=()=>{face.onerror=null;face.src='/assets/profile/head_1001.png';};icon.append(face);
  stage.append(icon);
  const power=center(el('div','ar-power'),-194,-357,110,70);
  power.append(img(A('force_icon')),el('b','',fmt(state?.power||0)));stage.append(power);
  const myRow=(data?.rating_board||[]).find(p=>String(p.uid)===own());
  for(const [label,value,y] of [['Xếp hạng',myRow?.rank||'—',-421],['Điểm',Number(data?.rating?.matches||0)>0?data.rating.rating:'Chưa đấu',-465]]){
   const field=center(el('div','ar-stat'),-230,y,170,30);field.append(el('span','',label),el('b','',value));stage.append(field);
  }
  stage.append(center(img(A('arena_decoration'),'ar-deco'),0,-411,270,164));
  const res=center(el('div','ar-res'),0,-333,220,36);
  res.append(el('span','',mode==='arena3v3'?'3 đội · Vé:':'Trận trực tuyến'),img(A('icon_34_small')),
   el('b','',fmt(mode==='arena3v3'?data?.arena3v3?.tickets??state?.items?.['34']??0:data?.rating?.matches??0)));
  stage.append(res);
  const status=data?.pvp?.status||'idle';
  const fight=center(el('button','ar-fight'),0,-419,212,77);fight.type='button';
  fight.style.backgroundImage="url('"+A('blue_btn_65_65')+"')";
  fight.textContent=status==='waiting'?'Đang tìm':status==='matched'?'Vào Trận':'Chiến đấu';
  fight.disabled=!data||busy;
  fight.onclick=()=>{panel=status==='matched'?'match':status==='waiting'?'queue':
    mode==='arena3v3'&&!validTeams(data?.arena3v3?.teams)?'teams':'join';render();};
  stage.append(fight);
  const choices=[
   ['Phần thưởng','arena_award_s',-328,()=>{panel='rewards';render();}],
   ['Lịch sử','arena_record',-397,()=>{panel='history';render();}],
   [mode==='arena3v3'?'Đội hình':'Phòng thủ','arena_defence',-464,()=>{
     panel=mode==='arena3v3'?'teams':'defense';render();
   }]
  ];
  for(const [label,asset,y,action] of choices){
   const b=center(el('button','ar-side'),242,y,170,54);b.type='button';
   b.style.backgroundImage="url('"+A('white_btn_65_65')+"')";b.append(img(A(asset)),el('span','',label));
   b.onclick=action;stage.append(b);
  }
  if(note)stage.append(center(el('p','ar-note',note),0,-555,620,45));
  if(panel)drawPanel(stage);
 }
 function openPlayer(p){
  const uid=p?.uid||'—',sid=p?.server_id||'—';
  GirlUI.notice('Người chơi: '+p.name+'\nUID: '+uid+'\nMáy chủ: '+sid+
    '\nLực chiến: '+fmt(p.power)+'\nĐiểm mùa: '+fmt(p.score),
    {title:'Hồ sơ đối thủ thật'});
 }
 function drawPanel(stage){
  const ov=el('div','ar-overlay');ov.onclick=e=>{if(e.target===ov){panel='';render();}};
  const win=el('div','ar-win'+(panel==='teams'?' a3-win':''));ov.append(win);
  const x=el('button','ar-close','✕');x.type='button';x.onclick=()=>{panel='';render();};
  const heading=el('h2','',title());win.append(heading,x);
  const paragraph=text=>win.append(el('p','ar-empty',text));
  const button=(label,action,disabled=false)=>{
    const b=el('button','ar-small',label);b.type='button';b.disabled=disabled||busy;b.onclick=action;win.append(b);return b;
  };
  const p=data?.pvp||{};
  if(panel==='join'){
   paragraph(mode==='arena3v3'?'Đấu 3 đội thật · 3 Vé Đấu Trường mỗi người.':'Tìm người chơi thật đang trực tuyến. Không có đối thủ NPC.');
   if(mode==='arena3v3'&&!validTeams(data?.arena3v3?.teams))
    button('Thiết lập 3 đội hình',()=>{panel='teams';render();});
   else button('Ghép trận',()=>queue('join'));
  }else if(panel==='queue'){
   paragraph('Đang tìm người chơi thật trên máy chủ…');
   button('Làm mới',()=>refresh());
   button('Hủy tìm trận',()=>queue('cancel'));
  }else if(panel==='match'){
   const m=p.match,opp=opponent(m),series=data?.series;
   if(!m){paragraph('Đang nhận trạng thái trận từ máy chủ.');button('Tải lại',()=>refresh());}
   else{
    paragraph('Đối thủ: '+(opp.name||opp.uid)+' · '+(opp.server_id||state?.server_id||'')+' · LC '+fmt(opp.power));
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
     else if(!series?.all_paid)button('Chờ đối thủ · Làm mới',()=>refresh());
     else if(series?.complete)button('Nhận Kết Quả Loạt Đấu',()=>round3v3(m,Number(series.next_round||0)));
     else button('Thi đấu lượt '+(Number(series.next_round||0)+1),()=>round3v3(m,Number(series.next_round||0)));
    }else if(m.status==='active')button('Vào trận với đối thủ thật',()=>fightSingle(m));
    else{paragraph('Đang chờ đối thủ thật xác nhận sẵn sàng.');button('Sẵn Sàng Vào Trận',()=>refresh());}
    button('Tải lại',()=>refresh());
   }
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
   }
   if(!rows.length)paragraph('Chưa có trận nào trong lịch sử thực.');
  }else if(panel==='defense'){
   paragraph('Đội hình phòng thủ lấy từ đội hình Nữ Thần đã lưu trên máy chủ; không sử dụng đối thủ hoặc đội hình NPC.');
   const wrap=el('div','ar-ins-team');
   const used=new Set((state?.formation||[]).map(x=>Number(x.partner_id)));
   for(const h of (state?.roster||[]).filter(x=>used.has(Number(x.partner_id))).slice(0,6)){
    const slot=el('div','ar-ins-slot');slot.append(portrait(h.table_id,56));wrap.append(slot);
   }
   win.append(wrap);
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
 function drawTeams(win,button){
  // Original Arena3v3BattleFormationWindow layout: three native team badges
  // with six positional slots each and the original candidate card grid.
  // Only the authenticated saved roster is offered; no NPC, auto-filled team,
  // random candidate or fabricated rival exists in this screen.
  const teams=teamDraft(),locked=data?.pvp?.status==='matched',roster=state?.roster||[];
  win.append(el('h3','','Arena3v3BattleFormationWindow · 3 Đội Hình'));
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
    b.append(el('small','',hero.name||'Nữ Thần'));
    b.title=(hero.name||'Nữ Thần')+' · '+(hero.stars||0)+'★ · Lv.'+(hero.lv||1);
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
