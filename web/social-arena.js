'use strict';
const SocialArena=(()=>{
 const el=(tag,cls,t)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(t!==undefined)e.textContent=t;return e;};
 const btn=(t,fn,white=false)=>{const b=el('button','gs-btn'+(white?' white':''),t);b.type='button';b.onclick=fn;return b;};
 const endpoint='/api/social-arena/action';
 let panel=null,active=false,identity='',busy=false,watching=false,referee=false,tab='board',message='',latest=null;
 const watched=new Set();
 function same(){return identity===state?.uid+'|'+state?.server_id&&state?.server_id==='S5';}
 function makePanel(){
  panel=GirlUI.win({title:'Đấu Trường Giao Lưu',cls:'social-arena-win world-rank-win'});
 }
 function open(){
  if(state?.server_id!=='S5')return;
  identity=state.uid+'|'+state.server_id;active=true;message='';tab='board';latest=null;makePanel();poll();
 }
 async function act(action,match_id,round_no){
  if(busy)return;busy=true;message='';
  try{const data=await api(endpoint,{action,match_id,round_no});if(same()){latest=data;render();}}
  catch(e){message=e.message;if(same())render();}
  finally{busy=false;}
 }
 function rankList(body,data){
  const list=el('div','wr-list social-ranks');
  for(const r of data.board||[]){
   const row=Arena.rankRow({...r,me:r.uid===state.uid,server_id:'S5',lv:r.level,score:r.points,score_label:'Điểm giao lưu'},r.rank-1,r.power,null);
   for(const c of row.children)for(const prop of ['left','top','width','height'])c.style.removeProperty(prop);
   row.classList.add('wr-has-extra');
   row.append(el('small','wr-extra-score',r.wins+' thắng · '+r.losses+' thua · '+r.draws+' hòa'));
   list.append(row);
  }
  if(!list.children.length)list.append(el('p','wr-note','Chưa có kết quả giao lưu.'));
  body.append(list);
 }
 function lineup(parent,m){
  const left=el('div','social-lineups');
  for(const [i,p] of (m.formations||[]).entries()){
   const r=el('div','social-lineup');r.dataset.side=i<2?'A':'B';
   r.append(el('b','',(i<2?'Đội A · ':'Đội B · ')+(p.name||'')),el('small','',Number(p.power||0).toLocaleString('vi-VN')));
   const grid=el('div','social-girls');
   for(const g of p.team){
    const cell=el('div','social-girl');cell.append(portrait(g.table_id,40,{stars:g.stars,group:g.group,equips:{6:g.skin_id}}),GirlUI.stars(g.stars),el('small','','Lv '+g.level));
    grid.append(cell);
   }r.append(grid);left.append(r);
  }parent.append(left);
 }
 function render(){
  if(!panel?.win.isConnected||!latest||watching)return;
  const data=latest,m=data.match,body=panel.body;
  body.replaceChildren();
  const points=data.me?.points??100;
  body.append(el('b','social-score','Điểm cá nhân: '+points),el('small','wr-status',message||({waiting:'Chờ mở lúc 20:00',open:'Đang mở ghép trận',closing:'Đã dừng ghép trận',closed:'Đã kết thúc'})[data.phase]||''));
  if(m&&m.status==='accept'){
   body.append(el('h3','','Đã tìm thấy trận đấu!'),el('p','',m.accepted.length+'/4 người đã xác nhận'));
   const b=btn('Xác nhận tham gia',()=>act('accept',m.id));b.disabled=m.accepted.includes(state.uid);
   body.append(b,btn('Từ chối',()=>act('cancel',m.id),true));
  }else if(m&&['preview','ready'].includes(m.status)){
   const remaining=Math.max(0,m.preview_until-data.server_time);
   body.append(el('h3','',remaining?'Xem trước đội hình · '+remaining+' giây':'Đội hình đã sẵn sàng'));
   lineup(body,m);
   const b=btn(m.started.includes(state.uid)?'Đang chờ đồng đội…':'Bắt Đầu',()=>act('begin',m.id));
   b.disabled=remaining>0||m.started.includes(state.uid);
   body.append(b,btn('Hủy',()=>act('cancel',m.id),true));
  }else if(m){body.append(el('p','','Đang chuẩn bị trận đấu…'));}
  else if(data.queued){body.append(el('h3','','Đang ghép trận… '+Math.min(4,data.queue_count)+'/4'),btn('Hủy ghép trận',()=>act('cancel'),true));}
  else if(!referee){
   const b=btn(points<=0||data.me?.disqualified?'Đã bị loại':'Chiến Đấu',()=>act('join'));
   b.disabled=data.phase!=='open'||points<=0||!!data.me?.disqualified;body.append(b);
  }else body.append(el('p','','Bạn đang ở chế độ trọng tài, không tranh hạng.'));
  const tabs=el('div','wr-tabs');tabs.append(btn('BXH Giao Lưu',()=>{tab='board';render();},tab!=='board'),btn('Lịch sử',()=>{tab='history';render();},tab!=='history'));body.append(tabs);
  if(tab==='board')rankList(body,data);
  else for(const h of [...(data.history||[])].reverse()){
   const row=el('div','social-history');
   row.append(el('b','',h.status==='finished'?'Kết quả '+h.score.join(' – '):'Trận đã hủy'));
   if(h.status==='finished')for(const r of [0,1])row.append(btn('Xem lượt '+(r+1),()=>playHistory(h,r),true));
   body.append(row);
  }
 }
 async function playHistory(m,r){
  try{const data=await api(endpoint,{action:'replay',match_id:m.id,round_no:r});await watchEventBattle({report:data.report},'arena','Giao Lưu · Lượt '+(r+1));}
  catch(e){GirlUI.toast(e.message);}
 }
 async function play(m,serverTime){
  const key=m.id+':'+m.round_no;
  if(watched.has(key)||watching)return;
  watching=true;
  try{
   const result=await api(endpoint,{action:'replay',match_id:m.id,round_no:m.round_no});
   const delay=Math.max(0,Math.min(5000,(m.play_at-serverTime)*1000));if(delay)await new Promise(r=>setTimeout(r,delay));
   if(!same()||!active)return;
   if(panel?.win.isConnected)panel.close();
   await watchEventBattle({report:result.report,livePvP:true,tournament:true,roundScore:result.score},'arena','Giao Lưu · Lượt '+(m.round_no+1));
   if(same()&&view==='event-battle'){
    await api(endpoint,{action:'watched',match_id:m.id,round_no:m.round_no});watched.add(key);
   }
  }catch(e){message=e.message;}
  finally{watching=false;}
 }
 async function poll(){
  if(!active||!same()){SocialVoice.hide('arena');return;}
  if(busy||watching||document.hidden)return;
  if(view!=='event-battle'&&(!panel?.win.isConnected||view!=='arena')){active=false;SocialVoice.hide('arena');return;}
  busy=true;
  try{
   const data=await api('/api/social-arena/status');if(!same())return;
   latest=data;referee=!!data.referee;
   if(data.voice_enabled&&['preview','ready','running','viewing'].includes(data.match?.status))SocialVoice.show('arena',data.match.id,'Voice Giao Lưu');
   else SocialVoice.hide('arena');

   if(data.match?.status==='viewing'){
    busy=false;await play(data.match,data.server_time);return;
   }
   if(view==='event-battle'&&!data.match){
    showView('arena');makePanel();tab='history';
   }
   render();
  }catch(e){message=e.message;render();}
  finally{busy=false;}
 }
 setInterval(poll,1500);
 return {open};
})();
