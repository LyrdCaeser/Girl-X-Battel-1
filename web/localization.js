'use strict';
window.GxbLocale=(()=>{
  const supported=['vi','en','zh-CN'];
  let lang=localStorage.getItem('gxb3-language')||'vi',dict={};
  if(!supported.includes(lang))lang='vi';
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
    const row=rows.find(r=>r.querySelector('strong')?.textContent.trim()===t('Language')||r.querySelector('strong')?.textContent.trim()==='Language'||r.querySelector('strong')?.textContent.trim()==='Ngôn Ngữ'||r.querySelector('strong')?.textContent.trim()==='语言');
    if(!row||row.querySelector('#gxb3-language'))return;
    const host=row.querySelector('div')||row;const old=host.querySelector('small');if(old)old.remove();
    const sel=document.createElement('select');sel.id='gxb3-language';
    [['vi','Tiếng Việt'],['en','English'],['zh-CN','简体中文']].forEach(([v,n])=>{const o=document.createElement('option');o.value=v;o.textContent=n;o.selected=v===lang;sel.append(o);});
    sel.onchange=()=>{localStorage.setItem('gxb3-language',sel.value);location.reload();};host.append(sel);
  }
  document.addEventListener('DOMContentLoaded',load,{once:true});
  return{current,t,setLanguage:v=>{if(supported.includes(v)){localStorage.setItem('gxb3-language',v);location.reload();}},supported};
})();
