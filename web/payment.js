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
  async function createOrder(pkg,note,status){
    if(!pkg.trim()){status.textContent='Hãy nhập gói muốn nạp.';return null;}
    try{
      const order=await api('/api/order/create',{package:pkg.trim(),note:note.trim()});
      status.textContent='Đã tạo đơn '+order.id+'. Hãy gửi mã đơn này qua Zalo.';
      return order;
    }catch(e){status.textContent=e.message;return null;}
  }
  function open(){
    close();
    overlay=el('div','pay-overlay');
    overlay.onclick=e=>{if(e.target===overlay)close();};
    const box=el('section','pay-box');
    const head=el('header','pay-head');
    const title=el('div');title.append(el('small','','Nữ Thần Chiến Đấu - GXB 3'),el('h2','','Nạp qua Zalo'));
    const x=el('button','pay-close','✕');x.type='button';x.onclick=close;head.append(title,x);box.append(head);
    box.append(el('p','pay-note','QTV xác nhận giao dịch thủ công. Không gửi mật khẩu, OTP hoặc thông tin đăng nhập game qua tin nhắn.'));
    const row=el('div','pay-contact');
    const info=el('div');info.append(el('span','','Zalo thanh toán'),el('strong','',ZALO));
    const cp=el('button','pay-copy','Sao chép số');const status=el('small','pay-status','');cp.onclick=()=>copy(ZALO,status);
    row.append(info,cp);box.append(row,status);

    const uid=state?.uid||'GXB3-000001',server=state?.server_id||'S1',name=state?.name||'Nữ Thần';
    const pkg=document.createElement('input');pkg.className='pay-input';pkg.placeholder='VD: Gói 100.000đ / 1000 Gems';
    const note=document.createElement('textarea');note.className='pay-template';note.placeholder='Ghi chú thêm (không bắt buộc)';
    box.append(el('label','pay-label','Gói muốn nạp'),pkg,el('label','pay-label','Ghi chú'),note);

    const actions=el('div','pay-actions');
    const create=el('button','pay-primary','Tạo đơn nạp');
    const openZalo=el('a','pay-zalo','Mở Zalo');openZalo.href='https://zalo.me/'+ZALO;openZalo.target='_blank';openZalo.rel='noopener noreferrer';
    create.onclick=async()=>{
      const order=await createOrder(pkg.value,note.value,status);if(!order)return;
      const template=`Nữ Thần Chiến Đấu - GXB 3\nMã đơn: ${order.id}\nUID: ${uid}\nServer: ${server}\nTên Nhân Vật: ${name}\nGói muốn nạp: ${pkg.value.trim()}\nGhi chú: ${note.value.trim()}`;
      await copy(template,status);
      status.textContent='Đã tạo '+order.id+' và sao chép mẫu tin. Gửi nội dung này qua Zalo để QTV đối soát.';
    };
    actions.append(create,openZalo);box.append(actions);
    box.append(el('p','pay-foot','QTV duyệt đơn trong Hệ Thống QTV. Khi duyệt, phần thưởng được gửi vào Thư của đúng UID + Server + Tên Nhân Vật.'));
    overlay.append(box);(window.GxbFrame?.root()||document.body).append(overlay);
  }
  return{open,close};
})();