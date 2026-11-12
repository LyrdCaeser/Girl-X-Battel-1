'use strict';
window.GxbOnline=(()=>{
  let overlay=null,tab='leaderboard',stream=null,fallbackTimer=null,refreshing=false,pvpMode='arena';
  let arena3v3Draft=null,arena3v3DraftUid='',arena3v3DraftDirty=false,arena3v3TeamIndex=0;
  const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  const T=s=>window.GxbLocale?GxbLocale.t(s):s;
  const fmt=n=>typeof number==='function'?number(Number(n||0)):String(n||0);
  // API values remain stable English identifiers; translate only visible labels.
  const guildRoleLabel=role=>({leader:'Bang Chủ',deputy:'Phó Bang',member:'Thành Viên'})[role]||String(role||'');
  const pvpModeLabel=mode=>({arena:'Đấu Trường',team:'Đấu Trường Đội',cross:'Đấu Trường Liên Máy Chủ',arena3v3:'Đấu Trường 3v3'})[mode]||String(mode||'');
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
  function autoArena3v3Teams(){
    const roster=[...(state?.roster||[])].sort((a,b)=>(Number(b.stars||0)*1000+Number(b.lv||0))-(Number(a.stars||0)*1000+Number(a.lv||0))).slice(0,18);
    return [0,1,2].map(i=>roster.slice(i*6,(i+1)*6).map((h,j)=>({partner_id:Number(h.partner_id),pos:j+1})));
  }
  function renderArena3v3Setup(body,config,locked=false){
    const saved=Array.isArray(config?.teams)?config.teams:[];
    const savedValid=saved.length===3&&saved.every(t=>Array.isArray(t)&&t.length>=1&&t.length<=6)&&
      new Set(saved.flat().map(x=>Number(x.partner_id))).size===saved.flat().length;
    if(arena3v3DraftUid!==String(state?.uid||'')){
      arena3v3DraftUid=String(state?.uid||'');arena3v3Draft=JSON.parse(JSON.stringify(savedValid?saved:autoArena3v3Teams()));
      arena3v3DraftDirty=!savedValid;arena3v3TeamIndex=0;
    }
    if(!Array.isArray(arena3v3Draft)||arena3v3Draft.length!==3)arena3v3Draft=[[],[],[]];
    const card=el('section','online-card'),head=el('h3','','Thiết Lập 3 Đội Hình 3v3');
    card.append(head,el('p','online-note','Mỗi đội cần 1–6 Nữ Thần. Một Nữ Thần chỉ được xuất hiện trong một đội. Đội hình được lưu vào hồ sơ Neon của tài khoản.'));
    const tabs=el('div','online-mode');
    for(let i=0;i<3;i++){const b=el('button',i===arena3v3TeamIndex?'on':'',`Đội ${i+1} · ${arena3v3Draft[i].length}/6`);b.onclick=()=>{arena3v3TeamIndex=i;renderPvp(body);};tabs.append(b);}
    card.append(tabs);
    const selected=arena3v3Draft[arena3v3TeamIndex];
    for(const slot of selected){
      const hero=(state?.roster||[]).find(x=>Number(x.partner_id)===Number(slot.partner_id));
      const row=el('div','online-mini-row');
      row.append(el('b','',hero?.name||`Nữ Thần #${slot.partner_id}`),el('span','',`Vị trí ${slot.pos} · Cấp ${hero?.lv||'—'}`));
      if(!locked){const remove=el('button','online-small','Bỏ');remove.onclick=()=>{arena3v3Draft[arena3v3TeamIndex]=selected.filter(x=>Number(x.partner_id)!==Number(slot.partner_id)).map((x,j)=>({...x,pos:j+1}));arena3v3DraftDirty=true;renderPvp(body);};row.append(remove);}
      card.append(row);
    }
    const used=new Set(arena3v3Draft.flat().map(x=>Number(x.partner_id)));
    const available=(state?.roster||[]).filter(x=>!used.has(Number(x.partner_id)));
    if(!locked&&selected.length<6&&available.length){
      const addRow=el('div','online-chat-send'),pick=document.createElement('select');pick.className='online-input';
      for(const h of available){const o=el('option','',`${h.name||'Nữ Thần'} · Lv.${h.lv||1} · ${h.stars||0}★`);o.value=String(h.partner_id);pick.append(o);}
      const add=el('button','online-primary','Thêm vào Đội');add.onclick=()=>{const id=Number(pick.value);if(!id||selected.length>=6||used.has(id))return;selected.push({partner_id:id,pos:selected.length+1});arena3v3DraftDirty=true;renderPvp(body);};
      addRow.append(pick,add);card.append(addRow);
    }else if(!selected.length)card.append(el('p','online-empty',locked?'Đội hình đã khóa trong trận.':'Chưa có Nữ Thần trong đội này.'));
    if(!locked){
      const actions=el('div','online-chat-send');
      const auto=el('button','online-small','Tự Xếp 3 Đội');auto.onclick=()=>{arena3v3Draft=autoArena3v3Teams();arena3v3DraftDirty=true;arena3v3TeamIndex=0;renderPvp(body);};
      const save=el('button','online-primary','Lưu 3 Đội');const valid=arena3v3Draft.every(t=>Array.isArray(t)&&t.length>=1&&t.length<=6)&&new Set(arena3v3Draft.flat().map(x=>Number(x.partner_id))).size===arena3v3Draft.flat().length;
      save.disabled=!valid||!arena3v3DraftDirty;
      save.onclick=async()=>{save.disabled=true;try{await post('/api/pvp/arena3v3/teams',{teams:arena3v3Draft});arena3v3DraftDirty=false;GirlUI.notice('Đã lưu 3 đội hình 3v3 vào hồ sơ tài khoản.',{title:'Đấu Trường 3v3'});await renderPvp(body);}catch(e){save.disabled=false;GirlUI.notice(e.message,{title:'Không thể lưu đội hình'});}};
      actions.append(auto,save);card.append(actions);
    }
    const ready=savedValid&&!arena3v3DraftDirty;
    card.append(el('small','online-note',`Vé Đấu Trường hiện có: ${fmt(config?.tickets||0)} · Mỗi loạt 3v3 tiêu hao ${Number(config?.ticket_cost||3)} vé từ mỗi người chơi.`));
    body.append(card);return ready;
  }
  async function renderArena3v3Match(body,match,data){
    const opp=matchOpponent(match),series=data.series||{paid:false,all_paid:false,rounds:[],next_round:0,wins_a:0,wins_b:0};
    const card=el('section','online-match');
    card.append(el('small','',match.id+' · Đấu Trường 3v3'),el('h3','',`Đối thủ: ${opp.name}`),el('p','',`${opp.uid} · ${T('Power')} ${fmt(opp.power)}`));
    let session=null;try{session=await post('/api/pvp/match/heartbeat',{match_id:match.id,ready:true});}catch{}
    const status=session?.match?.status||match.status;
    card.append(el('p','online-live',status==='active'?'Đã vào trận trực tuyến':'Đang chờ đối thủ xác nhận sẵn sàng'));
    const peers=(session?.peers||[]).filter(x=>Date.now()/1000-Number(x.last_seen||0)<=15).length;
    card.append(el('small','online-note',`Kết nối người chơi: ${peers}/2`));
    if(status!=='active'){
      const enter=el('button','online-primary','Sẵn Sàng Vào Trận');enter.onclick=async()=>{await post('/api/pvp/match/heartbeat',{match_id:match.id,ready:true});await renderPvp(body);};card.append(enter);
    }else if(!series.paid){
      const pay=el('button','online-primary','Dùng 3 Vé Đấu Trường');pay.onclick=async()=>{pay.disabled=true;try{await post('/api/pvp/arena3v3/pay',{match_id:match.id});await renderPvp(body);}catch(e){pay.disabled=false;GirlUI.notice(e.message,{title:'Không đủ điều kiện'});}};card.append(pay);
      card.append(el('small','online-note','Vé chỉ bị trừ một lần cho mỗi người; loạt đấu chỉ bắt đầu khi cả hai đã thanh toán.'));
    }else if(!series.all_paid){
      card.append(el('p','online-note','Bạn đã xác nhận vé. Đang chờ đối thủ xác nhận 3 vé.'));
      const refresh=el('button','online-primary','Kiểm Tra Đối Thủ');refresh.onclick=()=>renderPvp(body);card.append(refresh);
    }else{
      const meA=String(match.player_a)===String(state?.uid),myWins=meA?series.wins_a:series.wins_b,opponentWins=meA?series.wins_b:series.wins_a;
      card.append(el('h3','',`Tỷ số loạt đấu: ${myWins} – ${opponentWins} (Bạn – Đối Thủ)`));
      for(const r of series.rounds||[]){const who=r.won_by_me?'Bạn thắng':'Đối thủ thắng';card.append(el('div','online-mini-row',`Lượt ${Number(r.round)+1}: ${who} · ${Number(r.total_round||0)} vòng`));}
      if(series.complete){
        const close=el('button','online-primary','Cập Nhật Kết Quả Cuối');close.onclick=async()=>{try{const out=await post('/api/pvp/arena3v3/round',{match_id:match.id,expected_round:series.next_round});if(out.result)showBattleResult(body,out.result);else await renderPvp(body);}catch(e){GirlUI.notice(e.message,{title:'Đấu Trường 3v3'});}};card.append(close);
      }else{
        const next=el('button','online-fight',`Thi Đấu Lượt ${Number(series.next_round)+1}/3`);next.onclick=async()=>{next.disabled=true;next.textContent='Máy chủ đang mô phỏng trận…';try{const out=await post('/api/pvp/arena3v3/round',{match_id:match.id,expected_round:series.next_round});if(out.result)showBattleResult(body,out.result);else await renderPvp(body);}catch(e){next.disabled=false;next.textContent=`Thi Đấu Lượt ${Number(series.next_round)+1}/3`;GirlUI.notice(e.message,{title:'Đấu Trường 3v3'});}};card.append(next);
      }
      card.append(el('small','online-note','Mỗi lượt dùng đội hình tương ứng đã lưu. Máy chủ tự tính thắng/thua; không nhận kết quả từ thiết bị người chơi.'));
    }
    body.append(card);
  }
  async function renderPvp(body,quiet=false){
    const data=await get('/api/pvp/status?mode='+encodeURIComponent(pvpMode));body.replaceChildren();
    const modes=el('div','online-mode');
    [['arena','Arena'],['team','Team Arena'],['cross','Cross-server Arena'],['arena3v3','Đấu Trường 3v3']].forEach(([id,label])=>{const b=el('button',id===pvpMode?'on':'',T(label));b.onclick=()=>{pvpMode=id;renderPvp(body);const box=overlay?.querySelector('.online-box');if(box)openRealtime(box);};modes.append(b);});body.append(modes);
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
    let arena3v3Ready=true;
    if(pvpMode==='arena3v3')arena3v3Ready=renderArena3v3Setup(body,data.arena3v3||{},p.status==='matched');
    if(p.status==='matched'&&p.match){
      if(pvpMode==='arena3v3'){
        await renderArena3v3Match(body,p.match,data);
      }else{
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
      }
    }else if(p.status==='waiting'){
      const card=el('section','online-match waiting');card.append(el('h3','',T('Finding opponent…')),el('p','',T('The server is matching by mode and combat power.')));
      const cancel=el('button','online-danger',T('Cancel Matchmaking'));cancel.onclick=async()=>{await post('/api/pvp/queue',{action:'cancel',mode:pvpMode});renderPvp(body);};card.append(cancel);body.append(card);
    }else{
      const card=el('section','online-match');card.append(el('h3','',pvpMode==='arena3v3'?'Ghép Trận 3v3 Với Người Chơi Thật':T('PvP Matchmaking')),el('p','',T('Join the queue to find another online player.')));
      const join=el('button','online-primary',pvpMode==='arena3v3'?'Tìm Đối Thủ 3v3':T('Find Match'));join.disabled=pvpMode==='arena3v3'&&!arena3v3Ready;
      join.onclick=async()=>{try{await post('/api/pvp/queue',{action:'join',mode:pvpMode});renderPvp(body);}catch(e){GirlUI.notice(e.message,{title:'Ghép Trận'});}};
      card.append(join);if(pvpMode==='arena3v3'&&!arena3v3Ready)card.append(el('small','online-note','Hãy lưu đủ 3 đội hình trước khi xếp hàng.'));body.append(card);
    }
    const board=el('div','online-history');board.append(el('h3','',T('Season Ranking')));
    for(const r of (data.rating_board||[]).slice(0,20)){const row=el('article','online-history-row');row.append(el('b','','#'+r.rank+' '+(r.character_name||r.uid)),el('span','',String(r.rating)),el('small','',r.server_id+' · '+T('Wins')+' '+r.wins));board.append(row);}body.append(board);
    const hist=el('div','online-history');hist.append(el('h3','',T('Recent Matches')));
    for(const m of (data.history||[]).filter(x=>pvpMode!=='arena3v3'||x.mode==='arena3v3').slice(0,pvpMode==='arena3v3'?10:20)){const opp=matchOpponent(m),r=el('article','online-history-row');const won=m.status==='finished'&&m.winner_uid===state?.uid;const delta=m.player_a===state?.uid?Number(m.rating_delta_a||0):Number(m.rating_delta_b||0);
      const seriesNote=m.mode==='arena3v3'?` · ${String(m.player_a)===String(mine)?m.arena3v3_wins_a:m.arena3v3_wins_b}–${String(m.player_a)===String(mine)?m.arena3v3_wins_b:m.arena3v3_wins_a} · ${(m.arena3v3_rounds||[]).length} lượt`:'';
      r.append(el('b','',opp.name),el('span','',m.status==='finished'?(won?T('Victory'):T('Defeat')):matchStatusLabel(m.status)),el('small','',pvpModeLabel(m.mode)+' · '+(m.status==='finished'?(delta>=0?'+':'')+delta+' '+T('Rating'):'')+seriesNote+' · '+new Date(m.created_at*1000).toLocaleString()));hist.append(r);}
    body.append(hist);
  }
  function showBattleResult(body,result){
    body.replaceChildren();
    const mine=state?.uid,won=result?.winner_uid===mine,delta=result?.player_a===mine?Number(result?.rating_delta_a||0):Number(result?.rating_delta_b||0);
    const card=el('section','online-result '+(won?'win':'lose'));card.append(el('small','',result?.id||''),el('h2','',T(won?'Victory':'Defeat')),el('strong','',T('Rating')+' '+(delta>=0?'+':'')+delta));
    const report=result?.battle_report||{};if(report.total_round!==undefined)card.append(el('p','',T('Rounds')+': '+report.total_round));
    if(result?.mode==='arena3v3'){
      const meta=report.arena3v3||{},series=report.series||{};
      card.append(el('p','',meta.sweep?'Thắng 2–0: hệ số điểm xếp hạng 1,25 đã áp dụng.':'Kết quả loạt đấu 3v3 đã được lưu.'));
      for(const r of series.rounds||[])card.append(el('div','online-mini-row',`Lượt ${Number(r.round)+1}: ${String(r.winner_uid)===String(mine)?'Bạn thắng':'Đối thủ thắng'} · ${Number(r.total_round||0)} vòng`));
      card.append(el('p','online-note','Phần thưởng của hai người chơi đã được gửi vào Hòm Thư.'));
    }
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