'use strict';
// Compatibility entry point: show server and original archived mail together.
// The native HomeMenus mailbox handles UI and attachment claims;
// do not intercept the original .home-mail button with a separate modal.
window.GxbMail=(()=>{
  function open(){
    if(typeof HomeMenus!=='undefined')HomeMenus.open('mail','home');
    else window.GirlUI?.notice?.('Hòm Thư chưa sẵn sàng. Vui lòng tải lại trang.',{title:'Hòm Thư'});
  }
  function close(){}
  function bind(){}
  return{open,close,bind};
})();
