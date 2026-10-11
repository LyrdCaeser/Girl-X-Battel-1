'use strict';
window.GxbOnline=(()=>{
  let overlay=null,tab='leaderboard',timer=null,pvpMode='arena';
  const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  const T=s=>window.GxbLocale?GxbLocale.t(s):s;
  const fmt=n=>typeof number==='function'?number(Number(n||0)):String(n||0);
  async function get(url){return api(url);}
  async function post(url,body){return api(url,body);}
  function close(){if(timer)clearInterval(timer);timer=null;overlay?.remove();overlay=null;}
  function shell(title){
    close();overlay=el('div','online-overlay');
    const box=el('section','online-box'),head=el('header','online-head');
    head.append(el('div','online-brand',T('GXB 3 Online')),el('h2','',T(title)));
    const x=el('button','online-close','✕');x.onclick=close;head.append(x);box.append(head);
    const nav=el('nav','online-tabs');
    [['leaderboard','Leaderboard'],['guild','Guild'],['pvp','PvP Match']].forEach(([id,label])=>{const b=el('button',id===tab?'on':'',T(label));b.onclick=()=>{tab=id;renderBody(box);};nav.append(b);});
    box.append(nav);const body=el('div','online-body');body.id='online-body';box.append(body);overlay.append(box);
    overlay.onclick=e=>{if(e.target===overlay)close();};(window.GxbFrame?.root()||document.body).append(overlay);return box;
  }
  async function open(next='leaderboard',mode='arena'){tab=next;pvpMode=mode;const box=shell(next==='guild'?'Guild':next==='pvp'?'PvP Match':'Leaderboard');await renderBody(box);}
  async function renderBody(box){
    if(timer)clearInterval(timer);timer=null;
    box.querySelectorAll('.online-tabs button').forEach((b,i)=>b.classList.toggle('on',['leaderboard','guild','pvp'][i]===tab));
    const body=box.querySelector('#online-body');body.replaceChildren(el('p','online-loading',T('Loading…')));
    try{
      if(tab==='leaderboard')await renderLeaderboard(body);
      if(tab==='guild')await renderGuild(body);
      if(tab==='pvp'){await renderPvp(body);timer=setInterval(()=>{if(overlay&&tab==='pvp')renderPvp(body,true).catch(()=>{});},2500);}
    }catch(e){body.replaceChildren(el('p','online-error',e.message));}
  }
  async function renderLeaderboard(body){
    const sid=encodeURIComponent(state?.server_id||'S1');
    const [rank,online]=await Promise.all([get('/api/leaderboard?server_id='+sid+'&limit=100'),get('/api/world/online?server_id='+sid)]);
    body.replaceChildren();
    const top=el('div','online-summary');top.append(el('strong','',T('Server')+' '+rank.server_id),el('span','',fmt(online.count)+' '+T('Online')));body.append(top);
    const list=el('div','online-list');
    for(const p of rank.ranking||[]){const row=el('article','online-rank'+(p.uid===state?.uid?' me':''));
      row.append(el('b','online-place','#'+p.rank),el('div','online-main'),el('strong','online-power',fmt(p.power)));
      row.querySelector('.online-main').append(el('b','',p.character_name),el('small','',p.uid+' · '+T('Level')+' '+p.level));
      list.append(row);}
    if(!(rank.ranking||[]).length)list.append(el('p','online-empty',T('No ranking data yet.')));
    body.append(list);
  }
  async function renderGuild(body){
    const data=await get('/api/world-guild');body.replaceChildren();
    if(data.guild){
      const g=data.guild,hero=el('section','online-guild-hero');hero.append(el('small','',T('Server')+' '+g.server_id),el('h3','',g.name),el('p','',g.notice||T('No guild notice.')),el('b','',T('Members')+': '+g.member_count));body.append(hero);
      const members=el('div','online-list');for(const m of g.members||[]){const row=el('article','online-member');row.append(el('div','online-main'),el('strong','online-power',fmt(m.power)));row.querySelector('.online-main').append(el('b','',m.character_name),el('small','',m.role+' · '+m.uid));members.append(row);}body.append(members);
      const leave=el('button','online-danger',g.role==='leader'?T('Disband Guild'):T('Leave Guild'));leave.onclick=async()=>{if(!confirm(T('Are you sure?')))return;await post('/api/world-guild/action',{action:'leave'});renderGuild(body);};body.append(leave);return;
    }
    const create=el('section','online-card');create.append(el('h3','',T('Create Guild')));
    const name=document.createElement('input');name.placeholder=T('Guild Name');name.maxLength=24;
    const note=document.createElement('textarea');note.placeholder=T('Guild Notice');note.maxLength=180;
    const go=el('button','online-primary',T('Create Guild'));go.onclick=async()=>{await post('/api/world-guild/action',{action:'create',name:name.value,notice:note.value});renderGuild(body);};create.append(name,note,go);body.append(create);
    const list=el('div','online-list');
    for(const g of data.guilds||[]){const row=el('article','online-guild-row'),main=el('div','online-main');main.append(el('b','',g.name),el('small','',T('Members')+': '+g.member_count+' · Lv.'+g.level));const join=el('button','online-primary',T('Join'));join.onclick=async()=>{await post('/api/world-guild/action',{action:'join',guild_id:g.id});renderGuild(body);};row.append(main,join);list.append(row);}
    if(!(data.guilds||[]).length)list.append(el('p','online-empty',T('No Guild has been created on this server.')));body.append(list);
  }
  function matchOpponent(m){const mine=state?.uid;return m.player_a===mine?{uid:m.player_b,name:m.name_b,power:m.power_b}:{uid:m.player_a,name:m.name_a,power:m.power_a};}
  async function renderPvp(body,quiet=false){
    const data=await get('/api/pvp/status?mode='+encodeURIComponent(pvpMode));body.replaceChildren();
    const modes=el('div','online-mode');
    [['arena','Arena'],['team','Team Arena'],['cross','Cross-server Arena']].forEach(([id,label])=>{const b=el('button',id===pvpMode?'on':'',T(label));b.onclick=()=>{pvpMode=id;renderPvp(body);};modes.append(b);});body.append(modes);
    const rating=data.rating||{rating:1000,wins:0,losses:0,matches:0,season_id:'-'};
    const ratingBox=el('section','online-rating');
    ratingBox.append(el('div','',T('Season')+' '+rating.season_id),el('strong','',String(rating.rating)),el('small','',T('Wins')+' '+rating.wins+' · '+T('Losses')+' '+rating.losses+' · '+T('Matches')+' '+rating.matches));
    body.append(ratingBox);
    const p=data.pvp||{status:'idle'};
    if(p.status==='matched'&&p.match){
      const m=p.match,opp=matchOpponent(m),card=el('section','online-match');
      let session=null;try{session=await post('/api/pvp/match/heartbeat',{match_id:m.id,ready:true});}catch{}
      const peerCount=(session?.peers||[]).filter(x=>Date.now()/1000-Number(x.last_seen||0)<=15).length;
      card.append(el('small','',m.id+' · '+m.mode.toUpperCase()),el('h3','',T('Opponent Found')),el('b','online-opponent',opp.name),el('p','',opp.uid+' · '+T('Power')+' '+fmt(opp.power)),el('p','online-live',T((session?.match?.status||m.status)==='active'?'Battle session active':'Match ready')));
      card.append(el('div','online-peer-state',T('Realtime peers')+': '+peerCount+'/2'));
      const statusNow=session?.match?.status||m.status;
      const activate=el('button','online-primary',T(statusNow==='active'?'Refresh Session':'Enter Match'));activate.onclick=async()=>{await post('/api/pvp/match/heartbeat',{match_id:m.id,ready:true});renderPvp(body);};card.append(activate);
      if(statusNow==='active'){
        const fight=el('button','online-fight',T('Start Battle'));
        fight.onclick=async()=>{fight.disabled=true;fight.textContent=T('Server is simulating battle…');try{
          const out=await post('/api/pvp/match/battle',{match_id:m.id});showBattleResult(body,out.result);
        }catch(e){fight.disabled=false;fight.textContent=T('Start Battle');alert(e.message);}};
        card.append(fight);
      }
      card.append(el('small','online-note',T('The server loads both saved teams and simulates the result. The client cannot submit a winner.')));body.append(card);
    }else if(p.status==='waiting'){
      const card=el('section','online-match waiting');card.append(el('h3','',T('Finding opponent…')),el('p','',T('The server is matching by mode and combat power.')));
      const cancel=el('button','online-danger',T('Cancel Matchmaking'));cancel.onclick=async()=>{await post('/api/pvp/queue',{action:'cancel',mode:pvpMode});renderPvp(body);};card.append(cancel);body.append(card);
    }else{
      const card=el('section','online-match');card.append(el('h3','',T('PvP Matchmaking')),el('p','',T('Join the queue to find another online player.')));
      const join=el('button','online-primary',T('Find Match'));join.onclick=async()=>{await post('/api/pvp/queue',{action:'join',mode:pvpMode});renderPvp(body);};card.append(join);body.append(card);
    }
    const board=el('div','online-history');board.append(el('h3','',T('Season Ranking')));
    for(const r of (data.rating_board||[]).slice(0,20)){const row=el('article','online-history-row');row.append(el('b','','#'+r.rank+' '+(r.character_name||r.uid)),el('span','',String(r.rating)),el('small','',r.server_id+' · '+T('Wins')+' '+r.wins));board.append(row);}body.append(board);
    const hist=el('div','online-history');hist.append(el('h3','',T('Recent Matches')));
    for(const m of data.history||[]){const opp=matchOpponent(m),r=el('article','online-history-row');const won=m.status==='finished'&&m.winner_uid===state?.uid;const delta=m.player_a===state?.uid?Number(m.rating_delta_a||0):Number(m.rating_delta_b||0);
      r.append(el('b','',opp.name),el('span','',m.status==='finished'?(won?T('Victory'):T('Defeat')):m.status),el('small','',m.mode+' · '+(m.status==='finished'?(delta>=0?'+':'')+delta+' '+T('Rating'):'')+' · '+new Date(m.created_at*1000).toLocaleString()));hist.append(r);}
    body.append(hist);
  }
  function showBattleResult(body,result){
    if(timer)clearInterval(timer);timer=null;body.replaceChildren();
    const mine=state?.uid,won=result?.winner_uid===mine,delta=result?.player_a===mine?Number(result?.rating_delta_a||0):Number(result?.rating_delta_b||0);
    const card=el('section','online-result '+(won?'win':'lose'));card.append(el('small','',result?.id||''),el('h2','',T(won?'Victory':'Defeat')),el('strong','',T('Rating')+' '+(delta>=0?'+':'')+delta));
    const report=result?.battle_report||{};if(report.total_round!==undefined)card.append(el('p','',T('Rounds')+': '+report.total_round));
    const back=el('button','online-primary',T('Back to PvP'));back.onclick=()=>renderPvp(body);card.append(back);body.append(card);
  }
  function bind(){
    document.addEventListener('click',e=>{
      const guild=e.target.closest('[data-coming="Guild"]');if(guild){e.preventDefault();e.stopImmediatePropagation();open('guild');return;}
      const rank=e.target.closest('.idle-icon[title^="Ranking"]');if(rank){e.preventDefault();e.stopImmediatePropagation();open('leaderboard');return;}
      const league=e.target.closest('.league-card');if(league){const label=league.getAttribute('aria-label');if(label==='Team Arena'||label==='Cross-server Arena'){e.preventDefault();e.stopImmediatePropagation();open('pvp',label==='Team Arena'?'team':'cross');}}
    },true);
  }
  document.addEventListener('DOMContentLoaded',bind,{once:true});
  return{open,close};
})();