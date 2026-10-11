'use strict';
window.GxbPayment=(()=>{
  let overlay=null;
  const ZALO='0856848557';
  const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  function close(){overlay?.remove();overlay=null;}
  async function copy(value,status){
    try{await navigator.clipboard.writeText(value);status.textContent='Đã sao chép.';}
    catch{status.textContent='Không thể tự sao chép. Hãy sao chép thủ công.';}
  }
  function open(){
    close();
    overlay=el('div','pay-overlay');
    overlay.onclick=e=>{if(e.target===overlay)close();};
    const box=el('section','pay-box');
    const head=el('header','pay-head');
    const title=el('div');title.append(el('small','','Nữ Thần Chiến Đấu - GXB 3'),el('h2','','Nạp qua Zalo'));
    const x=el('button','pay-close','✕');x.type='button';x.onclick=close;head.append(title,x);box.append(head);
    box.append(el('p','pay-note','Hệ thống hiện xác nhận giao dịch thủ công. Không gửi mật khẩu, mã OTP hoặc thông tin đăng nhập tài khoản game qua tin nhắn.'));
    const row=el('div','pay-contact');
    const info=el('div');info.append(el('span','','Zalo thanh toán'),el('strong','',ZALO));
    const cp=el('button','pay-copy','Sao chép số');const status=el('small','pay-status','');cp.onclick=()=>copy(ZALO,status);
    row.append(info,cp);box.append(row,status);
    const uid=state?.profile?.uid||state?.uid||'local-player-1';
    const server=state?.server_id||'S1';
    const template=`Nữ Thần Chiến Đấu - GXB 3\nUID: ${uid}\nServer: ${server}\nGói muốn nạp: \nGhi chú: `;
    const msg=el('textarea','pay-template');msg.readOnly=true;msg.value=template;box.append(el('label','pay-label','Mẫu tin nhắn'),msg);
    const actions=el('div','pay-actions');
    const copyMsg=el('button','pay-primary','Sao chép mẫu tin');copyMsg.onclick=()=>copy(template,status);
    const openZalo=el('a','pay-zalo','Mở Zalo');openZalo.href='https://zalo.me/'+ZALO;openZalo.target='_blank';openZalo.rel='noopener noreferrer';
    actions.append(copyMsg,openZalo);box.append(actions);
    box.append(el('p','pay-foot','Sau khi nhắn, QTV sẽ kiểm tra giao dịch và cộng vật phẩm theo đơn. Hệ thống không tự động trừ tiền hay tự xác nhận chuyển khoản.'));
    overlay.append(box);(window.GxbFrame?.root()||document.body).append(overlay);
  }
  return{open,close};
})();
