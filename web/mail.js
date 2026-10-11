'use strict';
window.GxbMail=(()=>{
  let overlay=null;
  const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  function close(){overlay?.remove();overlay=null;}
  async function claim(id,status){
    try{const r=await api('/api/mail/claim',{mail_id:id});state=r.state;status.textContent='Đã nhận vật phẩm.';draw();}
    catch(e){status.textContent=e.message;}
  }
  function draw(){
    if(!overlay)return;
    overlay.replaceChildren();
    const box=el('section','mail-box');
    const head=el('header','mail-head');head.append(el('h2','','Thư'),(()=>{const b=el('button','mail-close','✕');b.onclick=close;return b;})());box.append(head);
    const meta=el('p','mail-meta',`${state?.server_id||'S1'} · ${state?.uid||'-'} · ${state?.name||'-'}`);box.append(meta);
    const list=el('div','mail-list'),mails=state?.mail_info||[];
    if(!mails.length)list.append(el('p','mail-empty','Chưa có thư.'));
    for(const m of mails){const row=el('article','mail-row'+(m.status==='claimed'?' claimed':''));const top=el('div','mail-row-top');top.append(el('b','',m.title||'Thư từ GM'),el('small','',new Date(m.created_at*1000).toLocaleString()));row.append(top);
      if(m.body)row.append(el('p','',m.body));
      const rewards=el('div','mail-rewards');for(const [id,n] of Object.entries(m.attachments||{}))rewards.append(el('span','',`#${id} × ${number(n)}`));row.append(rewards);
      const st=el('small','mail-status',m.status==='claimed'?'Đã nhận':'');if(m.status==='pending'){const b=el('button','mail-claim','Nhận');b.onclick=()=>claim(m.id,st);row.append(b);}row.append(st);list.append(row);
    }
    box.append(list);overlay.append(box);
  }
  function open(){close();overlay=el('div','mail-overlay');overlay.onclick=e=>{if(e.target===overlay)close();};(window.GxbFrame?.root()||document.body).append(overlay);draw();}
  function bind(){const b=document.querySelector('.home-mail');if(!b||b.dataset.mailBound)return;b.dataset.mailBound='1';b.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();open();},true);}
  document.addEventListener('DOMContentLoaded',bind,{once:true});
  return{open,close,bind};
})();