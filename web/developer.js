'use strict';
// GM access is granted by the server to the existing owner's account only.
document.getElementById('dev-open')?.remove();
sessionStorage.removeItem('gxb2-developer');
sessionStorage.removeItem('gxb2-admin-key');
if(!document.querySelector('script[data-gxb2-i18n]')){
  const script=document.createElement('script');
  script.src='/i18n-vi.js';
  script.defer=true;
  script.dataset.gxb2I18n='1';
  document.head.appendChild(script);
}
