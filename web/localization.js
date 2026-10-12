'use strict';
window.GxbLocale=(()=>{
  const supported=['vi'];
  let lang='vi',dict={};
  try{localStorage.setItem('gxb3-language','vi');}catch{}
  const current=()=>lang;
  const t=value=>{const s=String(value??'');const trimmed=s.trim();if(!trimmed)return s;const hit=dict[trimmed];return hit? s.replace(trimmed,hit):s;};
  async function load(){
    try{dict=await fetch('/localization/'+lang+'.json',{cache:'no-store'}).then(r=>r.json());}catch{dict={};}
    document.documentElement.lang=lang==='zh-CN'?'zh-CN':lang;
    translate(document.body);installSelector();observe();
  }
  function translate(root){
    if(!root)return;
    const apply=n=>{if(n.nodeType===Node.TEXT_NODE){const x=t(n.nodeValue||'');if(x!==n.nodeValue)n.nodeValue=x;}};
    if(root.nodeType===Node.TEXT_NODE){apply(root);return;}
    if(root.nodeType!==Node.ELEMENT_NODE&&root.nodeType!==Node.DOCUMENT_FRAGMENT_NODE)return;
    const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);const nodes=[];while(w.nextNode())nodes.push(w.currentNode);nodes.forEach(apply);
    if(root.querySelectorAll)for(const el of root.querySelectorAll('[title],[aria-label],[placeholder]'))for(const a of ['title','aria-label','placeholder']){const v=el.getAttribute(a);if(v&&dict[v])el.setAttribute(a,dict[v]);}
  }
  let observer=null;
  function observe(){observer?.disconnect();observer=new MutationObserver(rs=>{for(const r of rs){for(const n of r.addedNodes)translate(n);if(r.type==='characterData')translate(r.target);}});observer.observe(document.documentElement,{subtree:true,childList:true,characterData:true});}
  function installSelector(){
    const rows=[...document.querySelectorAll('.profile-setting-row')];
    const row=rows.find(r=>['Language','Ngôn Ngữ','语言'].includes(r.querySelector('strong')?.textContent.trim()||''));
    if(!row)return;
    const host=row.querySelector('div')||row;
    host.querySelector('#gxb3-language')?.remove();
    const small=host.querySelector('small');
    if(small)small.textContent='Tiếng Việt';
  }
  document.addEventListener('DOMContentLoaded',load,{once:true});
  return{current,t,setLanguage:()=>{},supported};
})();
