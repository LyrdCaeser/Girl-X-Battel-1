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
  // Kept for compatibility with renderHome(): never inject a new home UI panel.
  function sync(_id){}
  function translateQuote(id,source){
    const quote=dialogues[Number(id)];
    return quote || (typeof window.GxbVi?.t==='function'?window.GxbVi.t(source||''):source||'');
  }
  return{sync,translateQuote};
})();
