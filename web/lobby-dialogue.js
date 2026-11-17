'use strict';
// The MainWindow in the archived game has no standalone speech bubble.
// Keep the original character quotes for the existing character-details view;
// story scenes use their own StoryPlayer dialogue frame.
const LobbyDialogue=(()=>{
  const dialogues={
    41001:'Đã là xác sống thì chẳng cần ăn, ngủ hay mơ mộng gì cả. Cậu không thấy như thế dễ chịu hơn sao?',
    42001:'Nếu tôi thao tác chính xác, chỉ hơi đau một chút thôi. Nếu tôi... thao tác... chính xác... Ờm.',
    43001:'Thế giới này được Thượng Đế tạo ra. Vậy nên, hãy bày tỏ lòng biết ơn với Người.'
  };
  let active=null,token=0;
  const root=()=>document.querySelector('#home-view .home-stage');
  function sync(id){
    const next=Number(id)||null;
    if(next!==active){active=next;token++;root()?.querySelector('.lb-quote')?.remove();}
    const stage=root();if(!stage?.dataset||typeof stage.addEventListener!=='function'||stage.dataset.voiceTapBound)return;
    stage.dataset.voiceTapBound='1';
    stage.addEventListener('click',event=>{
      if(view!=='home'||!active||event.target.closest('button,a,input,nav,.home-side,.home-top,.home-bottom,.home-destinations'))return;
      void speak();
    });
  }
  async function speak(){
    if(!active||typeof Dates==='undefined')return false;
    const stage=root();if(!stage)return false;
    const at=token;
    return Dates.playGirlVoice(active,line=>{
      if(token!==at||view!=='home'||!line)return;
      let bubble=stage.querySelector('.lb-quote');
      if(!bubble){bubble=document.createElement('div');bubble.className='lb-quote';bubble.setAttribute('role','status');stage.append(bubble);}
      bubble.textContent=line;
      bubble.classList.add('show');
      clearTimeout(bubble._hide);
      bubble._hide=setTimeout(()=>bubble.classList.remove('show'),4300);
    });
  }
  function translateQuote(id,source){
    const quote=dialogues[Number(id)];
    return quote || (typeof window.GxbVi?.t==='function'?window.GxbVi.t(source||''):source||'');
  }
  return{sync,translateQuote,speak};
})();
