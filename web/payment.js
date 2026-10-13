'use strict';
window.GxbPayment=(()=>{
  let overlay=null;
  const ZALO='0856848557';
  const T=s=>window.GxbLocale?GxbLocale.t(s):s;
  const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};

  function close(){overlay?.remove();overlay=null;}

  async function copy(value,status){
    try{await navigator.clipboard.writeText(value);status.textContent=T('Copied.');}
    catch{status.textContent=T('Cannot copy automatically. Please copy manually.');}
  }

  async function catalog(){
    try{
      const out=await api('/api/payment/packages');
      return Array.isArray(out?.packages)?out.packages:[];
    }catch{
      return [{id:'CUSTOM',name:T('Custom package'),price_label:T('Contact via Zalo'),manual_reward:true}];
    }
  }

  async function createOrder(packageId,note,status){
    try{
      const order=await api('/api/order/create',{package:packageId,note:note.trim()});
      status.textContent=T('Order created')+' '+order.id+'. '+T('Send this order code via Zalo.');
      return order;
    }catch(e){status.textContent=e.message;return null;}
  }

  async function open(selectedPackageId=null){
    close();
    const packages=await catalog();
    overlay=el('div','pay-overlay');
    overlay.onclick=e=>{if(e.target===overlay)close();};
    const box=el('section','pay-box');
    const head=el('header','pay-head');
    const title=el('div');title.append(el('small','','Nữ Thần Chiến Đấu - GXB 3'),el('h2','',T('Top up via Zalo')));
    const x=el('button','pay-close','✕');x.type='button';x.onclick=close;head.append(title,x);box.append(head);
    box.append(el('p','pay-note',T('Payment is verified manually by the GM. Never send your password, OTP, or game login credentials in messages.')));

    const row=el('div','pay-contact');
    const info=el('div');info.append(el('span','',T('Payment Zalo')),el('strong','',ZALO));
    const cp=el('button','pay-copy',T('Copy number'));const status=el('small','pay-status','');cp.onclick=()=>copy(ZALO,status);
    row.append(info,cp);box.append(row,status);

    const uid=state?.uid||'GXB3-000001',server=state?.server_id||'S1',name=state?.name||'Nữ Thần';
    const pkg=document.createElement('select');pkg.className='pay-input';
    for(const p of packages){
      const o=el('option','',p.name+(p.price_label?' · '+p.price_label:''));
      o.value=p.id;o.dataset.manual=p.manual_reward?'1':'0';pkg.append(o);
    }
    if(selectedPackageId && packages.some(p=>p.id===selectedPackageId))pkg.value=selectedPackageId;
    if(!packages.length){
      const o=el('option','',T('No top-up package is currently available'));o.value='';pkg.append(o);pkg.disabled=true;
    }
    const custom=document.createElement('input');custom.className='pay-input';custom.placeholder=T('Describe the package or amount you want');
    const note=document.createElement('textarea');note.className='pay-template';note.placeholder=T('Additional note (optional)');
    const customLabel=el('label','pay-label',T('Custom request'));
    function syncCustom(){
      const current=packages.find(x=>x.id===pkg.value);
      const show=!!current?.manual_reward;
      custom.hidden=!show;customLabel.hidden=!show;
    }
    pkg.onchange=syncCustom;
    box.append(el('label','pay-label',T('Top-up package')),pkg,customLabel,custom,el('label','pay-label',T('Note')),note);
    syncCustom();

    const actions=el('div','pay-actions');
    const create=el('button','pay-primary',T('Create top-up order'));
    const openZalo=el('a','pay-zalo',T('Open Zalo'));openZalo.href='https://zalo.me/'+ZALO;openZalo.target='_blank';openZalo.rel='noopener noreferrer';
    create.onclick=async()=>{
      if(!pkg.value){status.textContent=T('No top-up package is currently available');return;}
      create.disabled=true;
      try{
        const current=packages.find(x=>x.id===pkg.value)||{};
        const extra=current.manual_reward&&custom.value.trim()?T('Custom request')+': '+custom.value.trim():'';
        const fullNote=[extra,note.value.trim()].filter(Boolean).join('\n');
        const order=await createOrder(pkg.value,fullNote,status);if(!order)return;
        const packageText=(current.name||pkg.value)+(current.price_label?' · '+current.price_label:'');
        const template=[
          'Nữ Thần Chiến Đấu - GXB 3',
          T('Order code')+': '+order.id,
          'UID: '+uid,
          T('Server')+': '+server,
          T('Character Name')+': '+name,
          T('Top-up package')+': '+packageText,
          extra,
          note.value.trim()?T('Note')+': '+note.value.trim():''
        ].filter(Boolean).join('\n');
        await copy(template,status);
        status.textContent=T('Order and message template copied. Send it via Zalo for GM reconciliation.');
      }finally{create.disabled=false;}
    };
    actions.append(create,openZalo);box.append(actions);
    box.append(el('p','pay-foot',T('After approval, rewards are delivered by in-game Mail to the exact UID + Server + Character Name on the order.')));
    overlay.append(box);(window.GxbFrame?.root()||document.body).append(overlay);
  }

  return{open,close};
})();
