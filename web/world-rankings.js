'use strict';
// Original common window + original ArenaWindowItem rows and game button sprites.
const WorldRankings=(()=>{
 const modes=[['power','Lực Chiến'],['level','Cấp Độ'],['campaign','Chiến Dịch'],['guild','Bang Hội'],['tower','Tháp Thử Thách Học Viện'],['faction','Hệ Nguyên Tố']];
 const crossWorlds=['S1','S2','S3'];
 const factions=[[1,'U Linh Ma'],[2,'Nhân Tộc'],[3,'Ma Thú'],[4,'Tinh Linh'],[6,'Ánh Sáng'],[5,'Bóng Tối'],[7,'Vũ Trụ'],[8,'Hỗn Độn']];
 const el=(tag,cls,txt)=>{const x=document.createElement(tag);if(cls)x.className=cls;if(txt!==undefined)x.textContent=txt;return x;};
 let panel=null,mode='power',group=1,seq=0;
 const fmt=n=>Number(n).toLocaleString('vi-VN');
 function active(p){return panel===p&&p.win.isConnected&&view==='home'&&p.identity===state.uid+'|'+state.server_id;}
 function button(text,fn,selected=false){const b=el('button','gs-btn'+(selected?'':' white'),text);b.type='button';b.onclick=fn;b.setAttribute('aria-pressed',String(selected));return b;}
 function select(m,g=group){mode=m;group=g;renderTabs();load(true);}
 function renderTabs(){
  if(!panel)return;
  panel.tabs.replaceChildren();
  for(const [id,name] of modes)panel.tabs.append(button(name,()=>select(id),id===mode));
  if(crossWorlds.includes(state.server_id)){const b=button('Liên Server',()=>select('cross'),mode==='cross');b.classList.add('wr-cross-tab');panel.tabs.append(b);}
  panel.list.classList.toggle('wr-cross',mode==='cross');
  panel.groups.replaceChildren();panel.groups.hidden=mode!=='faction';
  if(mode==='faction')factions.forEach(([id,name])=>{
   const b=button('',()=>select('faction',id),group===id);
   b.setAttribute('aria-label','Hệ '+name);b.title='Hệ '+name;
   const icon=el('img');icon.src='/assets/factions/group'+id+'.png';icon.alt='';b.append(icon);panel.groups.append(b);
  });
  panel.note.textContent=mode==='cross'?'Xếp theo lực chiến đội hình chính toàn S1–S3. Không tính S4 và S5.':mode==='faction'?'Tổng lực chiến của tối đa 6 nữ thần mạnh nhất thuộc hệ đã chọn.':mode==='guild'?'Xếp theo tổng lực chiến đội hình chính của thành viên đang hoạt động.':mode==='campaign'?'Xếp theo ải Chiến Dịch cao nhất đã vượt.':mode==='tower'?'Xếp theo tầng Tháp Thử Thách Học Viện cao nhất đã vượt.':'';
 }
 async function load(clear=false){
  const p=panel;if(!p||!active(p))return;
  if(p.pending&&!clear)return;
  const token=++seq;p.pending=true;
  if(clear){p.list.replaceChildren();p.status.textContent='Đang tải bảng xếp hạng…';}
  try{
   const result=await api('/api/world-rankings?mode='+encodeURIComponent(mode)+'&group='+group);
   if(!active(p)||token!==seq)return;
   const top=p.list.scrollTop;p.list.replaceChildren();
   for(const r of result.ranking){
    const row=Arena.rankRow({...r,lv:r.level,display_score:r.guild_flag?fmt(r.score):mode==='campaign'?r.display_score:fmt(r.score)},r.rank-1,r.power,null);
    // Remove prefab coordinates only in this responsive ranking grid.
    for(const child of row.children)for(const prop of ['left','top','width','height'])child.style.removeProperty(prop);
    if(r.guild_flag)row.querySelector('.ar2-lv').textContent=String(r.level);
    row.querySelector('.ar2-icon').style.cursor='default';
    // Reserve the right-hand column for actual guild membership in every player board.
    const scoreLabel=row.querySelector('.ar2-plabel'),scoreValue=row.querySelector('.ar2-points');
    if(r.guild_flag){
     row.querySelector('.ar2-power b').textContent=fmt(r.power);
     row.append(el('small','wr-extra-score',r.member_count+' thành viên'));
    }else if(!['power','cross'].includes(result.mode)){
     row.append(el('small','wr-extra-score',scoreLabel.textContent+': '+scoreValue.textContent));
    }
    scoreLabel.remove();scoreValue.remove();
    const guildName=el('b','wr-guild-name',r.guild_flag?'':(r.guild_name||''));
    if(guildName.textContent)guildName.title=guildName.textContent;
    row.append(guildName);
    if(row.querySelector('.wr-extra-score'))row.classList.add('wr-has-extra');
    p.list.append(row);
   }
   if(!result.ranking.length)p.list.append(el('p','ar-empty','Chưa có người chơi phù hợp.'));
   p.list.scrollTop=top;
   p.status.textContent='';
   p.updated.textContent='Cập nhật '+new Date(result.server_time*1000).toLocaleTimeString('vi-VN');
  }catch(e){if(active(p)&&token===seq)p.status.textContent='Không tải được BXH. '+(p.list.children.length?'Đang giữ kết quả lần trước.':'Vui lòng thử lại.');}
  finally{if(token===seq)p.pending=false;}
 }
 function open(){
  if(!state?.uid||developerMode)return GirlUI.notice('Hãy đăng nhập nhân vật để xem Bảng Xếp Hạng.');
  const win=GirlUI.win({title:'Bảng Xếp Hạng',cls:'world-rank-win'});
  mode='power';group=1;
  const p={...win,identity:state.uid+'|'+state.server_id,pending:false,tabs:el('nav','wr-tabs'),groups:el('nav','wr-groups'),note:el('p','wr-note'),status:el('p','wr-status'),list:el('div','wr-list ar-rank-list'),updated:el('small','wr-updated')};panel=p;
  const footer=el('div','wr-footer');footer.append(p.updated,button('Làm mới',()=>load(false),true));
  const frame=el('div','wr-list-frame ar-rank');frame.append(p.list);
  p.body.append(p.tabs,p.groups,p.note,p.status,frame,footer);
  renderTabs();load(true);
 }
 setInterval(()=>{if(panel&&active(panel)&&!document.hidden)load();},10000);
 return {open};
})();
