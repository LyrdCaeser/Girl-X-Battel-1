'use strict';
/* Bag/Smithy vocabulary sourced from the game's original English text.
   Localizes display strings only; all IDs, quantities, prices and rewards
   stay exactly as their original tables and server state define. */
window.GxbBagVi=(()=>{
 const exact=Object.freeze({
  'Gear':'Trang bị','Items':'Vật phẩm','Consumable':'Vật phẩm tiêu hao',
  'Antiques':'Cổ vật','Anima Gear':'Trang bị Linh hồn',
  'Girl Shards':'Mảnh Nữ Thần','Girls Shards':'Mảnh Nữ Thần',
  'Forge':'Rèn','Auto Forge':'Tự động rèn',
  'Weapon':'Vũ khí','Clothes':'Áo','Accessory':'Phụ kiện','Shoes':'Giày',
  'Coin':'Vàng','Gem':'Kim Cương','EXP':'EXP','Regular Currency':'Đơn vị tiền tệ phổ thông',
  'The most valuable rare Currency.':'Loại tiền tệ quý hiếm.',
  'Use to upgrade Player Level':'Dùng để tăng cấp người chơi.',
  'Academy Chest':'Rương Học Viện',
  'Girls Chest':'Rương Nữ Thần',
  'Girls Customized Chest':'Rương Nữ Thần tự chọn',
  'Kratos or Nephilim Chest':'Rương Kratos hoặc Nephilim',
  'Customized Girl Chest (Exclusive)':'Rương Nữ Thần tự chọn (Độc quyền)',
  'Customized Class Set Chest':'Rương tự chọn bộ trang bị theo hệ',
  'Mugwort Customized Chest':'Rương Ngải Cứu tự chọn',
  'Lantern Customization Chest':'Rương Lồng Đèn tự chọn',
  'Customized Anima Stone Set Chest':'Rương tự chọn bộ Đá Linh hồn',
  'Customized 6-star Blue Anima Stone Chest':'Rương tự chọn Đá Linh hồn xanh 6 sao',
  'Random Anima Stone Set Chest':'Rương bộ Đá Linh hồn ngẫu nhiên',
  'Random 6-star Blue Anima Stone Chest':'Rương Đá Linh hồn xanh 6 sao ngẫu nhiên',
  'Warrior\'s Set':'Bộ Chiến Binh',
  'Mage\'s Set':'Bộ Pháp Sư',
  'Ranger\'s Set':'Bộ Xạ Thủ',
  'Assassin\'s Set':'Bộ Sát Thủ',
  'Priest\'s Set':'Bộ Linh Mục',
  'League Chest':'Rương Đấu Trường',
  'Steam Lucky Box':'Hộp May Mắn Hơi Nước',
  'Scavenger\'s Loot (24H Coins)':'Chiến lợi phẩm thám hiểm (Vàng 24 giờ)',
  'Scavenger\'s Loot (24H Exp Juice)':'Chiến lợi phẩm thám hiểm (Nước EXP 24 giờ)',
  'Scavenger\'s Loot (8H Coins)':'Chiến lợi phẩm thám hiểm (Vàng 8 giờ)',
  'Scavenger\'s Loot (8H Exp Juice)':'Chiến lợi phẩm thám hiểm (Nước EXP 8 giờ)',
  'Gift Box':'Hộp Quà','Lucky Gift':'Quà May Mắn','Lovely Gift':'Quà Yêu Thương',
  'Gift of Love':'Quà Tình Yêu',
  'Halloween Gift Box':'Hộp Quà Halloween',
  'Christmas Surprise Chest':'Rương Bất Ngờ Giáng Sinh',
  'Easter Compensation Chest':'Rương Quà Bù Lễ Phục Sinh',
  'Guild Chest':'Rương Bang Hội',
  'Guild Gem Box':'Hộp Kim Cương Bang Hội',
  'Blue Magic Box':'Hộp Ma Thuật Xanh',
  'Purple Magic Box':'Hộp Ma Thuật Tím',
  'Electronic Set Chest':'Rương Bộ Điện Tử',
  'Demonic Set Chest':'Rương Bộ Ma Tộc',
  'Angel Set Chest':'Rương Bộ Thiên Thần',
  'Holy Spirit Set Chest':'Rương Bộ Thánh Linh',
  'Elite Skill Chest':'Rương Kỹ Năng Tinh Anh',
  'Elite Skill Promotion Chest':'Rương Tăng Cấp Kỹ Năng Tinh Anh',
  'Advanced Resource Chest':'Rương Tài Nguyên Cao Cấp',
  'Christmas limited Chest':'Rương Giáng Sinh giới hạn',
  'Gold':'Vàng','Servant Cookie':'Bánh Quy Người Hầu','Spirit Cookie':'Bánh Quy Linh Hồn',
  'Servant Crystal':'Pha Lê Người Hầu','Standard File':'Hồ Sơ Thường',
  'Exclusive File':'Hồ Sơ Độc Quyền','Tarnished Sphere':'Cầu Xỉn Màu',
  'Brilliant Sphere':'Cầu Rực Rỡ','Fantasy Dust':'Bụi Kỳ Ảo',
  'Fantasy Talisman':'Bùa Kỳ Ảo','Soul Gem':'Ngọc Linh Hồn',
  'Soul Essence':'Tinh Hoa Linh Hồn','Afterglow':'Dư Quang',
  'Slot Ticket':'Vé Máy Quay',
  'Guild Coin':'Xu Bang Hội',
  'Guild EXP':'EXP Bang Hội',
  'EXP Juice':'Nước EXP',
  'Lunch Box':'Hộp Cơm',
  'Coupon':'Phiếu Giảm Giá',
  'Class List':'Danh Sách Hệ',
  'Crystal Chisel':'Đục Pha Lê',
  'Sacred Page':'Trang Sách Thánh',
  'You can choose one of the rewards after opening this chest.':'Mở rương để chọn một trong những phần thưởng có trong danh sách gốc.',
  'Select to acquire 50 shards of Izanami or Uriel for opening this chest.':'Mở rương để tự chọn 50 mảnh Izanami hoặc 50 mảnh Uriel.',
  'A mysterious chest that can provide 50 5-Star Kratos shards or 50 5-Star Nephilim shards at your proposal for opening it.':'Mở rương để tự chọn 50 mảnh Kratos 5 sao hoặc 50 mảnh Nephilim 5 sao.',
  'A mysterious chest that can provide 50 5-Star Kratos shards or 50 5-Star Nephilim shards at your proposal for opening it. The option for 5-Star Nephilim shards will become available after the girl is actually updated into the game':'Rương tự chọn 50 mảnh Kratos hoặc Nephilim 5 sao. Trong bản gốc, phần thưởng Nephilim chỉ khả dụng sau khi nhân vật được cập nhật.',
  'You can get a set of Warrior\'s Gear for opening this chest':'Mở rương để nhận một bộ trang bị Chiến Binh.',
  'You can get a random reward for opening this chest (including Gems, Adv. Capsule Coins, Slot Tickets, Girls Shards, common resources, etc.)':'Mở rương để nhận một phần thưởng ngẫu nhiên, gồm Kim Cương, Xu Triệu Hồi Cao Cấp, Vé Máy Quay, Mảnh Nữ Thần hoặc tài nguyên.',
  'Collect 50 shards to summon the girl':'Thu thập 50 mảnh để triệu hồi Nữ Thần.',
  'Each round of Regular Slot Machine costs 1 Slot Ticket.':'Mỗi lượt Máy Quay thường tiêu tốn 1 vé.',
  'You can select to get a reward for opening this chest. (Tap the magnifying glass in the item for the option details; The options here won\'t be updated)':'Mở rương để chọn một phần thưởng theo danh sách gốc. Danh sách không thay đổi.',
  'You can select to get a reward for opening this chest. (Tap the magnifying glass in the item for the option details)':'Mở rương để chọn một phần thưởng theo danh sách gốc.',
  'You can choose to get a 6-star Blue Anima Stone for opening this chest. ( in the item for the details) (Anima Gears can be equipped on Girls over Lv.200)':'Mở rương để chọn một Đá Linh hồn xanh 6 sao. Nữ Thần trên cấp 200 có thể trang bị Linh hồn.'
 });
 const phrases=[
  [/(\d+)[- ]star (.+)/i,(_,n,name)=>name+' '+n+' sao'],
  [/^Customized (.+) Chest$/i,(_,name)=>'Rương tự chọn '+name],
  [/^Random (.+) Chest$/i,(_,name)=>'Rương '+name+' ngẫu nhiên'],
  [/^(.+) Chest$/i,(_,name)=>'Rương '+name],
  [/^(.+) Shards?$/i,(_,name)=>'Mảnh '+name],
  [/^(.+) Gift Box$/i,(_,name)=>'Hộp quà '+name],
  [/^(.+) Set Chest$/i,(_,name)=>'Rương bộ '+name],
 ];
 const terms=[
  [/\bGirls?\b/gi,'Nữ Thần'],[/\bShards?\b/gi,'mảnh'],
  [/\bChest\b/gi,'rương'],[/\bGift Box\b/gi,'hộp quà'],
  [/\bGear\b/gi,'trang bị'],[/\bAntique\b/gi,'cổ vật'],
  [/\bCoins?\b/gi,'Vàng'],[/\bGems?\b/gi,'Kim Cương'],
  [/\bLoot\b/gi,'chiến lợi phẩm'],[/\bReward\b/gi,'phần thưởng'],
  [/\bSummon\b/gi,'triệu hồi'],[/\bStar\b/gi,'sao'],
  [/\bEquipment\b/gi,'trang bị'],[/\bRandom\b/gi,'ngẫu nhiên'],
  [/\bSelect\b/gi,'chọn'],[/\bCustomized\b/gi,'tự chọn'],
  [/\bMagic\b/gi,'ma thuật'],[/\bAdvanced\b/gi,'cao cấp'],
  [/\bExclusive\b/gi,'độc quyền'],[/\bLegendary\b/gi,'huyền thoại'],
  [/\bBlue\b/gi,'xanh'],[/\bPurple\b/gi,'tím'],
  [/\bOrange\b/gi,'cam'],[/\bRed\b/gi,'đỏ'],
  [/\bGreen\b/gi,'lục'],[/\bGold\b/gi,'vàng'],
  [/\bGhost\b/gi,'Ma tộc'],[/\bHuman\b/gi,'Nhân tộc'],
  [/\bMonster\b/gi,'Yêu tộc'],[/\bFairy\b/gi,'Tiên tộc'],
  [/\bResource\b/gi,'tài nguyên'],[/\bItem\b/gi,'vật phẩm']
 ];
 const t=value=>{
  const s=String(value??'').trim();
  if(!s)return s;
  if(Object.prototype.hasOwnProperty.call(exact,s))return exact[s];

  // Descriptions from the original optional reward table include label*amount
  // lists. Keep quantities verbatim while localizing only display labels.
  const prefix='You can choose one of the rewards after opening this chest';
  if(s.startsWith(prefix)&&s.length>prefix.length){
    const rest=s.slice(prefix.length).replace(/^[.:\s：]+/,'').replace(/^[「\[]/,'').replace(/[」\].]+$/,'');
    if(rest){
      const pieces=rest.split(/,\s*/).map(piece=>{
        const match=piece.trim().match(/^(.+?)\s*\*\s*([\d.]+)$/);
        return match?t(match[1].trim())+' ×'+match[2]:t(piece.trim());
      });
      return 'Mở rương để chọn một phần thưởng gốc: '+pieces.join(', ')+'.';
    }
  }

  const fromExisting=window.GxbVi?.t(s);
  if(fromExisting&&fromExisting!==s)return fromExisting;
  for(const [pattern,convert] of phrases){
    const match=s.match(pattern);
    if(match){const result=s.replace(pattern,convert);
      if(result!==s){let out=result;for(const [re,vi] of terms)out=out.replace(re,vi);return out;}
    }
  }
  if(s.length>130)return s; // Keep unverified original descriptions, don't invent lore.
  let out=s;
  for(const [re,vi] of terms)out=out.replace(re,vi);
  return out;
 };
 return Object.freeze({t});
})();
