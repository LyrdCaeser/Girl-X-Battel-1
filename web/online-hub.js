'use strict';
window.GxbOnline=(()=>{
  let overlay=null,tab='leaderboard',stream=null,fallbackTimer=null,refreshing=false,pvpMode='arena';
  const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  const T=s=>window.GxbLocale?GxbLocale.t(s):s;
  const fmt=n=>typeof number==='function'?number(Number(n||0)):String(n||0);
  // API values remain stable English identifiers; translate only visible labels.
  const guildRoleLabel=role=>({leader:'Bang Chủ',deputy:'Phó Bang',member:'Thành Viên'})[role]||String(role||'');
  const pvpModeLabel=mode=>({arena:'Đấu Trường',team:'Đấu Trường Đội',cross:'Đấu Trường Liên Máy Chủ'})[mode]||String(mode||'');
  const matchStatusLabel=status=>({
    idle:'Chưa ghép trận',queued:'Đang xếp hàng',waiting:'Đang tìm đối thủ',
    matched:'Đã ghép trận',ready:'Sẵn sàng',scheduled:'Đã lên lịch',
    active:'Đang diễn ra',finished:'Đã kết thúc',
    cancelled:'Đã hủy',expired:'Đã hết hạn'
  })[status]||String(status||'');
  async function get(url){return api(url);}
  async function post(url,body){return api(url,body);}
  function close(){
    if(stream){stream.close();stream=null;}
    if(fallbackTimer){clearInterval(fallbackTimer);fallbackTimer=null;}
    overlay?.remove();overlay=null;
  }
  function shell(title){
    close();overlay=el('div','online-overlay');
    const box=el('section','online-box'),head=el('header','online-head');
    head.append(el('div','online-brand',T('GXB 3 Online')),el('h2','',T(title)));
    const x=el('button','online-close','✕');x.onclick=close;head.append(x);box.append(head);
    const nav=el('nav','online-tabs');
    [['leaderboard','Leaderboard'],['guild','Guild'],['pvp','PvP Match']].forEach(([id,label])=>{const b=el('button',id===tab?'on':'',T(label));b.onclick=()=>{if(id==='guild'&&typeof Guild!=='undefined'&&Guild.openOnline){close();Guild.openOnline('guild','home');return;}tab=id;renderBody(box);};nav.append(b);});
    box.append(nav);const body=el('div','online-body');body.id='online-body';box.append(body);overlay.append(box);
    overlay.onclick=e=>{if(e.target===overlay)close();};(window.GxbFrame?.root()||document.body).append(overlay);return box;
  }
  async function open(next='leaderboard',mode='arena'){
    if(next==='guild'&&typeof Guild!=='undefined'&&Guild.openOnline){close();await Guild.openOnline('guild','home');return;}
    tab=next;pvpMode=mode;
    const box=shell(next==='guild'?'Guild':next==='pvp'?'PvP Match':'Leaderboard');
    await renderBody(box);openRealtime(box);
  }
  function openRealtime(box){
    if(stream){stream.close();stream=null;}
    if(fallbackTimer){clearInterval(fallbackTimer);fallbackTimer=null;}
    const refresh=async()=>{
      if(!overlay||refreshing||!['pvp','leaderboard'].includes(tab))return;
      refreshing=true;
      try{await renderBody(box,true);}catch{}finally{refreshing=false;}
    };
    if(window.EventSource){
      stream=new EventSource('/api/events/stream?mode='+encodeURIComponent(pvpMode));
      stream.addEventListener('snapshot',()=>refresh());
      stream.onerror=()=>{};
    }else{
      fallbackTimer=setInterval(refresh,5000);
    }
  }
  async function renderBody(box,quiet=false){
    box.querySelectorAll('.online-tabs button').forEach((b,i)=>b.classList.toggle('on',['leaderboard','guild','pvp'][i]===tab));
    const body=box.querySelector('#online-body');body.replaceChildren(el('p','online-loading',T('Loading…')));
    try{
      if(tab==='leaderboard')await renderLeaderboard(body);
      if(tab==='guild')await renderGuild(body);
      if(tab==='pvp')await renderPvp(body,quiet);
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
    const rankCard=el('section','online-card');rankCard.append(el('h3','',T('Guild Ranking')));
    for(const r of (data.ranking||[]).slice(0,10)){const row=el('div','online-mini-row');row.append(el('b','','#'+r.rank+' '+r.name),el('span','',T('Power')+' '+fmt(r.total_power)),el('small','',T('Members')+' '+r.member_count));rankCard.append(row);}body.append(rankCard);

    if(data.guild){
      const g=data.guild,hero=el('section','online-guild-hero');
      hero.append(el('small','',T('Server')+' '+g.server_id),el('h3','',g.name),
        el('p','',g.notice||T('No guild notice.')),
        el('b','',T('Guild Level')+' '+g.level+' · EXP '+fmt(g.exp)),
        el('span','',T('Members')+': '+g.member_count+' · '+T('Role')+': '+guildRoleLabel(g.role)));
      body.append(hero);

      if(['leader','deputy'].includes(g.role)){
        const manage=el('section','online-card');manage.append(el('h3','',T('Guild Management')));
        const notice=document.createElement('textarea');notice.placeholder=T('Guild Notice');notice.value=g.notice||'';
        const saveNotice=el('button','online-primary',T('Save Notice'));saveNotice.onclick=async()=>{await post('/api/world-guild/manage',{action:'notice',notice:notice.value});renderGuild(body);};manage.append(notice,saveNotice);
        const mailTitle=document.createElement('input');mailTitle.placeholder=T('Guild Mail Title');
        const mailBody=document.createElement('textarea');mailBody.placeholder=T('Guild Mail Body');
        const sendMail=el('button','online-primary',T('Send Guild Mail'));sendMail.onclick=async()=>{await post('/api/world-guild/manage',{action:'mail',title:mailTitle.value,body:mailBody.value});mailTitle.value='';mailBody.value='';GirlUI.notice(T('Guild mail sent.'),{title:'Thư Bang Hội'});};manage.append(mailTitle,mailBody,sendMail);
        body.append(manage);

        const apps=el('section','online-card');apps.append(el('h3','',T('Applications')));
        for(const a of data.applications||[]){const row=el('div','online-app-row'),main=el('div','online-main');main.append(el('b','',a.character_name),el('small','',a.uid+' · '+T('Power')+' '+fmt(a.power)));
          const yes=el('button','online-primary',T('Approve'));yes.onclick=async()=>{await post('/api/world-guild/manage',{action:'review',target_uid:a.uid,approve:true});renderGuild(body);};
          const no=el('button','online-danger',T('Reject'));no.onclick=async()=>{await post('/api/world-guild/manage',{action:'review',target_uid:a.uid,approve:false});renderGuild(body);};
          row.append(main,yes,no);apps.append(row);}
        if(!(data.applications||[]).length)apps.append(el('p','online-empty',T('No pending applications.')));body.append(apps);
      }

      const members=el('section','online-card');members.append(el('h3','',T('Guild Members')));
      for(const m of g.members||[]){const row=el('article','online-member');const main=el('div','online-main');main.append(el('b','',m.character_name),el('small','',guildRoleLabel(m.role)+' · '+m.uid+' · '+T('Contribution')+' '+fmt(m.contribution||0)));row.append(main,el('strong','online-power',fmt(m.power)));
        if(g.role==='leader'&&m.uid!==state?.uid){
          if(m.role==='member'){const dep=el('button','online-small',T('Make Deputy'));dep.onclick=async()=>{await post('/api/world-guild/manage',{action:'role',target_uid:m.uid,role:'deputy'});renderGuild(body);};row.append(dep);}
          if(m.role==='deputy'){const dem=el('button','online-small',T('Make Member'));dem.onclick=async()=>{await post('/api/world-guild/manage',{action:'role',target_uid:m.uid,role:'member'});renderGuild(body);};row.append(dem);}
          const tr=el('button','online-small',T('Transfer Leader'));tr.onclick=async()=>{if(await GirlUI.confirm(T('Are you sure?'),{title:'Xác Nhận',ok:'Đồng Ý',danger:true})){await post('/api/world-guild/manage',{action:'transfer',target_uid:m.uid});renderGuild(body);}};row.append(tr);
        }
        if(['leader','deputy'].includes(g.role)&&m.uid!==state?.uid&&m.role!=='leader'){const kick=el('button','online-danger',T('Kick'));kick.onclick=async()=>{if(await GirlUI.confirm(T('Are you sure?'),{title:'Xác Nhận',ok:'Đồng Ý',danger:true})){await post('/api/world-guild/manage',{action:'kick',target_uid:m.uid});renderGuild(body);}};row.append(kick);}
        members.append(row);}body.append(members);

      const chat=el('section','online-card');chat.append(el('h3','',T('Guild Chat')));
      const chatList=el('div','online-chat');for(const m of data.chat||[]){const msg=el('div','online-chat-msg');msg.append(el('b','',m.character_name),el('span','',m.message),el('small','',new Date(m.created_at*1000).toLocaleTimeString()));chatList.append(msg);}chat.append(chatList);
      const chatRow=el('div','online-chat-send');const chatInput=document.createElement('input');chatInput.placeholder=T('Write a message…');const send=el('button','online-primary',T('Send'));send.onclick=async()=>{if(!chatInput.value.trim())return;await post('/api/world-guild/manage',{action:'chat',message:chatInput.value});chatInput.value='';renderGuild(body);};chatRow.append(chatInput,send);chat.append(chatRow);body.append(chat);

      const wars=el('section','online-card');wars.append(el('h3','',T('Guild War')));
      for(const w of data.wars||[]){
        const row=el('div','online-war-row'),main=el('div','online-main');
        const statusText=w.status==='scheduled'?T('Scheduled'):w.status==='active'?T('Active'):T('Finished');
        main.append(el('b','',w.guild_a_name+' VS '+w.guild_b_name),el('span','',w.score_a+' - '+w.score_b),el('small','',statusText));
        row.append(main);
        if([Number(w.guild_a),Number(w.guild_b)].includes(Number(g.id))){
          const detail=el('button','online-small',w.status==='active'?T('Battle'):T('Details'));
          detail.onclick=()=>openGuildWar(w.id);row.append(detail);
        }
        wars.append(row);
      }
      if(['leader','deputy'].includes(g.role)){
        const opponents=(data.guilds||[]).filter(x=>x.id!==g.id);if(opponents.length){const sel=document.createElement('select');for(const x of opponents){const o=el('option','',x.name);o.value=x.id;sel.append(o);}const war=el('button','online-primary',T('Challenge Guild'));war.onclick=async()=>{await post('/api/world-guild/manage',{action:'war',opponent_guild_id:Number(sel.value),duration:86400});renderGuild(body);};wars.append(sel,war);}
      }body.append(wars);

      const leave=el('button','online-danger',g.role==='leader'?T('Disband Guild'):T('Leave Guild'));leave.onclick=async()=>{if(!await GirlUI.confirm(T('Are you sure?'),{title:'Xác Nhận',ok:'Đồng Ý',danger:true}))return;await post('/api/world-guild/action',{action:'leave'});renderGuild(body);};body.append(leave);return;
    }

    const create=el('section','online-card');create.append(el('h3','',T('Create Guild')));
    const name=document.createElement('input');name.placeholder=T('Guild Name');name.maxLength=24;
    const note=document.createElement('textarea');note.placeholder=T('Guild Notice');note.maxLength=180;
    const go=el('button','online-primary',T('Create Guild'));go.onclick=async()=>{await post('/api/world-guild/action',{action:'create',name:name.value,notice:note.value});renderGuild(body);};create.append(name,note,go);body.append(create);
    const list=el('div','online-list');
    for(const g of data.guilds||[]){const row=el('article','online-guild-row'),main=el('div','online-main');main.append(el('b','',g.name),el('small','',T('Members')+': '+g.member_count+' · Lv.'+g.level));const apply=el('button','online-primary',T('Apply'));apply.onclick=async()=>{await post('/api/world-guild/manage',{action:'apply',guild_id:g.id});apply.disabled=true;apply.textContent=T('Applied');};row.append(main,apply);list.append(row);}
    if(!(data.guilds||[]).length)list.append(el('p','online-empty',T('No Guild has been created on this server.')));body.append(list);
  }
  async function openGuildWar(warId){
    try{
      const data=await get('/api/guild-war?war_id='+encodeURIComponent(warId));
      const modal=el('div','online-war-overlay'),box=el('section','online-war-box');
      const w=data.war,head=el('header','online-war-head');
      head.append(el('div','',w.guild_a_name+' VS '+w.guild_b_name),el('strong','',w.score_a+' - '+w.score_b));
      const x=el('button','online-close','✕');x.onclick=()=>modal.remove();head.append(x);box.append(head);
      box.append(el('p','online-note',T('Status')+': '+matchStatusLabel(w.status)+' · '+T('Guild War ID')+': '+w.id));
      if(w.status==='active'){
        const enemies=el('div','online-list');
        for(const enemy of data.enemies||[]){
          const row=el('article','online-member'),main=el('div','online-main');
          main.append(el('b','',enemy.character_name),el('small','',enemy.uid+' · '+T('Power')+' '+fmt(enemy.power)));
          const fight=el('button','online-fight',T('Attack'));
          fight.onclick=async()=>{
            fight.disabled=true;fight.textContent=T('Server is simulating battle…');
            try{
              const out=await post('/api/guild-war/battle',{war_id:w.id,defender_uid:enemy.uid});
              const r=out.result||{};
              GirlUI.notice((r.winner_uid===state?.uid?T('Victory'):T('Defeat'))+' · +'+fmt(r.score)+' '+T('Guild War Score'),{title:'Kết Quả Bang Hội Chiến'});
              modal.remove();
              const body=document.getElementById('online-body');if(body)renderGuild(body);
            }catch(e){fight.disabled=false;fight.textContent=T('Attack');GirlUI.notice(e.message,{title:'Thông Báo'});}
          };
          row.append(main,fight);enemies.append(row);
        }
        if(!(data.enemies||[]).length)enemies.append(el('p','online-empty',T('No opponents available.')));
        box.append(enemies);
      }
      const history=el('div','online-history');history.append(el('h3','',T('War Battles')));
      for(const b of data.battles||[]){
        const row=el('article','online-history-row');
        row.append(el('b','',b.attacker_uid+' → '+b.defender_uid),el('span','',T('Score')+' +'+b.score),
          el('small','',T('Winner')+': '+b.winner_uid+' · '+new Date(b.created_at*1000).toLocaleString()));
        history.append(row);
      }
      box.append(history);modal.append(box);document.body.append(modal);
    }catch(e){GirlUI.notice(e.message,{title:'Thông Báo'});}
  }

  function matchOpponent(m){const mine=state?.uid;return m.player_a===mine?{uid:m.player_b,name:m.name_b,power:m.power_b}:{uid:m.player_a,name:m.name_a,power:m.power_a};}
  async function renderPvp(body,quiet=false){
    const data=await get('/api/pvp/status?mode='+encodeURIComponent(pvpMode));body.replaceChildren();
    const modes=el('div','online-mode');
    [['arena','Arena'],['team','Team Arena'],['cross','Cross-server Arena']].forEach(([id,label])=>{const b=el('button',id===pvpMode?'on':'',T(label));b.onclick=()=>{pvpMode=id;renderPvp(body);const box=overlay?.querySelector('.online-box');if(box)openRealtime(box);};modes.append(b);});body.append(modes);
    const rating=data.rating||{rating:1000,wins:0,losses:0,matches:0,season_id:'-'};
    const ratingBox=el('section','online-rating');
    ratingBox.append(el('div','',T('Season')+' '+rating.season_id),el('strong','',String(rating.rating)),el('small','',T('Wins')+' '+rating.wins+' · '+T('Losses')+' '+rating.losses+' · '+T('Matches')+' '+rating.matches));
    const seasonReward=data.season_reward||null;
    if(seasonReward){
      const reward=el('div','online-season-reward');
      reward.append(el('b','',T('Previous Season Reward')+' · '+seasonReward.season_id));
      if(seasonReward.eligible){
        const items=Object.entries(seasonReward.reward||{}).map(([id,n])=>'#'+id+' × '+fmt(n)).join(' · ');
        reward.append(el('span','',items||T('No reward')));
        if(seasonReward.claimed)reward.append(el('small','',T('Claimed')));
        else{const claim=el('button','online-primary',T('Claim Reward'));claim.onclick=async()=>{claim.disabled=true;try{await post('/api/pvp/season/claim',{mode:pvpMode});await renderPvp(body);}catch(e){claim.disabled=false;GirlUI.notice(e.message,{title:'Thông Báo'});}};reward.append(claim);}
      }else reward.append(el('small','',T('Not eligible')));
      ratingBox.append(reward);
    }
    body.append(ratingBox);
    const p=data.pvp||{status:'idle'};
    if(p.status==='matched'&&p.match){
      const m=p.match,opp=matchOpponent(m),card=el('section','online-match');
      let session=null;try{session=await post('/api/pvp/match/heartbeat',{match_id:m.id,ready:true});}catch{}
      const peerCount=(session?.peers||[]).filter(x=>Date.now()/1000-Number(x.last_seen||0)<=15).length;
      card.append(el('small','',m.id+' · '+pvpModeLabel(m.mode)),el('h3','',T('Opponent Found')),el('b','online-opponent',opp.name),el('p','',opp.uid+' · '+T('Power')+' '+fmt(opp.power)),el('p','online-live',T((session?.match?.status||m.status)==='active'?'Battle session active':'Match ready')));
      card.append(el('div','online-peer-state',T('Realtime peers')+': '+peerCount+'/2'));
      const statusNow=session?.match?.status||m.status;
      const activate=el('button','online-primary',T(statusNow==='active'?'Refresh Session':'Enter Match'));activate.onclick=async()=>{await post('/api/pvp/match/heartbeat',{match_id:m.id,ready:true});renderPvp(body);};card.append(activate);
      if(statusNow==='active'){
        const fight=el('button','online-fight',T('Start Battle'));
        fight.onclick=async()=>{fight.disabled=true;fight.textContent=T('Server is simulating battle…');try{
          const out=await post('/api/pvp/match/battle',{match_id:m.id});showBattleResult(body,out.result);
        }catch(e){fight.disabled=false;fight.textContent=T('Start Battle');GirlUI.notice(e.message,{title:'Thông Báo'});}};
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
      r.append(el('b','',opp.name),el('span','',m.status==='finished'?(won?T('Victory'):T('Defeat')):matchStatusLabel(m.status)),el('small','',pvpModeLabel(m.mode)+' · '+(m.status==='finished'?(delta>=0?'+':'')+delta+' '+T('Rating'):'')+' · '+new Date(m.created_at*1000).toLocaleString()));hist.append(r);}
    body.append(hist);
  }
  function showBattleResult(body,result){
    body.replaceChildren();
    const mine=state?.uid,won=result?.winner_uid===mine,delta=result?.player_a===mine?Number(result?.rating_delta_a||0):Number(result?.rating_delta_b||0);
    const card=el('section','online-result '+(won?'win':'lose'));card.append(el('small','',result?.id||''),el('h2','',T(won?'Victory':'Defeat')),el('strong','',T('Rating')+' '+(delta>=0?'+':'')+delta));
    const report=result?.battle_report||{};if(report.total_round!==undefined)card.append(el('p','',T('Rounds')+': '+report.total_round));
    const back=el('button','online-primary',T('Back to PvP'));back.onclick=()=>renderPvp(body);card.append(back);body.append(card);
  }
  function bind(){
    document.addEventListener('click',e=>{
      const guild=e.target.closest('[data-coming="Guild"]');if(guild){e.preventDefault();e.stopImmediatePropagation();if(typeof Guild!=='undefined'&&Guild.openOnline)Guild.openOnline('guild','home');return;}
      const rank=e.target.closest('.idle-icon[title^="Ranking"]');if(rank){e.preventDefault();e.stopImmediatePropagation();open('leaderboard');return;}
      const league=e.target.closest('.league-card');if(league){const label=league.getAttribute('aria-label');if(label==='Team Arena'||label==='Cross-server Arena'){e.preventDefault();e.stopImmediatePropagation();open('pvp',label==='Team Arena'?'team':'cross');}}
    },true);
  }
  document.addEventListener('DOMContentLoaded',bind,{once:true});
  return{open,close};
})();