'use strict';
// Lobby speech uses preserved quotes from the original character catalog.
// Vietnamese subtitles are translations of the actual quotes, not invented dialogue.
const LobbyDialogue=(()=>{
  const dialogues={
    41001:{name:'Zombia',text:'Đã là xác sống thì chẳng cần ăn, ngủ hay mơ mộng gì cả. Cậu không thấy như thế dễ chịu hơn sao?'},
    42001:{name:'Miya',text:'Nếu tôi thao tác chính xác, chỉ hơi đau một chút thôi. Nếu tôi... thao tác... chính xác... Ờm.'},
    43001:{name:'Nun',text:'Thế giới này được Thượng Đế tạo ra. Vậy nên, hãy bày tỏ lòng biết ơn với Người.'}
  };
  const heroes=[41001,42001,43001];
  let shownId=0,selectedId=heroes[0],stage,bubble,nameEl,lineEl;
  function currentHero(){
    try{return heroes[((Number(homeHeroIndex)||0)%heroes.length+heroes.length)%heroes.length];}
    catch{return heroes[0];}
  }
  function speak(){
    if(!stage||!bubble)return;
    const id=selectedId,entry=dialogues[id];
    if(!entry)return;
    shownId=id;
    nameEl.textContent=entry.name;
    lineEl.textContent=entry.text;
    bubble.hidden=false;
  }
  function sync(id){
    const requested=Number(id);
    const selected=heroes.includes(requested)?requested:currentHero();
    if(selected!==selectedId||selected!==shownId){
      selectedId=selected;
      speak();
    }
  }
  function init(){
    stage=document.querySelector('#home-view .home-stage');
    if(!stage||stage.querySelector('#gxb3-lobby-speech'))return;
    const speakBtn=document.createElement('button');
    speakBtn.type='button';speakBtn.id='gxb3-lobby-speak';
    speakBtn.setAttribute('aria-label','Xem lời thoại nhân vật sảnh');
    speakBtn.title='Chạm nhân vật để xem lời thoại';
    speakBtn.addEventListener('click',speak);
    stage.appendChild(speakBtn);
    bubble=document.createElement('div');
    bubble.id='gxb3-lobby-speech';bubble.setAttribute('role','status');
    nameEl=document.createElement('strong');
    lineEl=document.createElement('span');
    bubble.append(nameEl,lineEl);
    stage.appendChild(bubble);
    speak();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
  function translateQuote(id,source){
    const entry=dialogues[Number(id)];
    return entry?entry.text:typeof window.GxbVi?.t==='function'?window.GxbVi.t(source||''):source||'';
  }
  return{sync,speak,translateQuote};
})();
