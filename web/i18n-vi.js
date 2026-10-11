'use strict';
(() => {
  const TEXT = new Map(Object.entries({
    'Saved on this device':'Đã lưu trên thiết bị',
    'Gift Packs':'Gói quà',
    'Luvly’s Castle':'Lâu đài Luvly',
    'Events':'Sự kiện',
    'Limited Gift':'Quà giới hạn',
    'Adrift Message':'Tin nhắn trôi dạt',
    'Friends':'Bạn bè',
    'Fantasy Book':'Sách Kỳ Ảo',
    'Servant':'Linh thú',
    'Excursion':'Thám hiểm',
    'Cosmos Portal':'Cổng Vũ Trụ',
    'Campus':'Học Viện',
    'Campaign':'Chiến Dịch',
    'League':'Đấu Trường',
    'FrontPage':'Trang Chủ',
    'Girls':'Nữ Sinh',
    'Bag':'Túi Đồ',
    'Capsule':'Triệu Hồi',
    'Guild':'Bang Hội',
    'Menu':'Menu',
    'Study':'Học Tập',
    'Life':'Đời Sống',
    'Battle':'Chiến Đấu',
    'Graduate':'Tiến Hóa',
    'Preset':'Đội Hình',
    'Shards':'Mảnh Ghép',
    'Gallery':'Thư Viện',
    'Girl Shards':'Mảnh Nữ Sinh',
    'Shards collected:':'Mảnh đã thu thập:',
    'Load more':'Xem thêm',
    'YOUR TEAM':'ĐỘI HÌNH',
    'Lineup':'Đội hình',
    'Remove from slot':'Gỡ khỏi vị trí',
    'Save lineup':'Lưu đội hình',
    'LOCAL CAMPAIGN':'CHIẾN DỊCH LOCAL',
    'Attribute':'Thuộc tính',
    'Gear':'Trang bị',
    'Skins':'Trang phục',
    'Awake':'Thức tỉnh',
    'Grade':'Bậc',
    'Level up once':'Tăng 1 cấp',
    'In your Bag':'Trong Túi Đồ',
    'Forge':'Rèn',
    'Battle':'Chiến đấu',
    'View results':'Xem kết quả',
    'Back to event':'Về sự kiện',
    'Tests in Academy':'Thử Thách Học Viện',
    'Floor rewards':'Thưởng tầng',
    'Practice':'Luyện tập',
    'Replay battle':'Xem lại trận',
    'Daily Quiz':'Thử Thách Hằng Ngày',
    'Categories':'Danh mục',
    'Difficulties':'Độ khó',
    'My profile':'Hồ Sơ',
    'Profile':'Hồ Sơ',
    'Settings':'Cài Đặt',
    'Student':'Học viên',
    'Edit name':'Đổi tên',
    'Signature':'Chữ ký',
    'Edit signature':'Sửa chữ ký',
    'Choose avatar and frame':'Chọn avatar và khung',
    'Account':'Tài khoản',
    'Sound':'Âm thanh',
    'Language':'Ngôn ngữ',
    'English':'Tiếng Việt',
    'Notices':'Thông báo',
    'Avatars and frames':'Avatar và khung',
    'Avatars':'Avatar',
    'Frames':'Khung',
    'Use selection':'Sử dụng',
    'Cancel':'Hủy',
    'Save':'Lưu',
    'Developer Mode':'Chế độ Quản Trị',
    'Khóa QTV':'Khóa QTV',
    'Nhập khóa hiển thị trong Terminal':'Nhập khóa hiển thị trong Terminal',
    'Back to my save':'Về bản lưu thường',
    'Enable Developer Mode':'Bật chế độ Quản Trị',
    'Add Girl':'Thêm Nữ Sinh',
    'All Girls':'Tất cả Nữ Sinh',
    'Girl to 15★':'Nữ Sinh lên 15★',
    'Apply level to the entire collection':'Áp dụng cấp cho toàn bộ bộ sưu tập',
    'Go to floor':'Đến tầng',
    'Unlock all 30 visible stages':'Mở 30 ải đang hiển thị',
    'Close':'Đóng',
    'Girl':'Nữ Sinh',
    'Copies':'Số lượng',
    'Level':'Cấp',
    'Tests floor':'Tầng Thử Thách',
    'Separate test save. Your regular save is preserved.':'Bản lưu Quản Trị tách riêng. Bản lưu thường vẫn được giữ nguyên.',
    'Activate a separate test save to experiment.':'Bật bản lưu Quản Trị riêng để thử nghiệm.',
    'Applied to the developer save.':'Đã áp dụng vào bản lưu Quản Trị.',
    'Resources refill · free summons · unlimited Quiz · unlimited Tests Tokens.':'Tự nạp tài nguyên · triệu hồi miễn phí · Quiz không giới hạn · vé Thử Thách không giới hạn.',
    'Local preservation in development.':'Bản Local đang được hoàn thiện.'
  }));

  const ATTRS = ['title','aria-label','placeholder'];
  const translateText = (s) => {
    const trimmed = s.trim();
    if (!trimmed) return s;
    if (TEXT.has(trimmed)) return s.replace(trimmed, TEXT.get(trimmed));
    return s;
  };

  function translateNode(root) {
    if (!root) return;
    if (root.nodeType === Node.TEXT_NODE) {
      const next = translateText(root.nodeValue || '');
      if (next !== root.nodeValue) root.nodeValue = next;
      return;
    }
    if (root.nodeType !== Node.ELEMENT_NODE && root.nodeType !== Node.DOCUMENT_FRAGMENT_NODE) return;
    if (root.nodeType === Node.ELEMENT_NODE) {
      for (const a of ATTRS) {
        const v = root.getAttribute(a);
        if (v && TEXT.has(v)) root.setAttribute(a, TEXT.get(v));
      }
    }
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const n of nodes) translateNode(n);
    if (root.querySelectorAll) {
      for (const el of root.querySelectorAll('[title],[aria-label],[placeholder]')) {
        for (const a of ATTRS) {
          const v = el.getAttribute(a);
          if (v && TEXT.has(v)) el.setAttribute(a, TEXT.get(v));
        }
      }
    }
  }

  document.documentElement.lang = 'vi';
  document.title = 'Girls X Battle 2 · Local Việt Hóa';
  const run = () => {
    translateNode(document.body);
    const dev = document.getElementById('dev-open');
    if (dev) dev.textContent = 'QTV';
    const lang = [...document.querySelectorAll('.profile-setting-row strong')]
      .find(x => x.textContent.trim() === 'Ngôn ngữ');
    if (lang) {
      const small = lang.parentElement && lang.parentElement.querySelector('small');
      if (small) small.textContent = 'Tiếng Việt';
    }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run, {once:true});
  else run();

  const observer = new MutationObserver(records => {
    for (const r of records) {
      for (const n of r.addedNodes) translateNode(n);
      if (r.type === 'characterData') translateNode(r.target);
    }
  });
  observer.observe(document.documentElement, {subtree:true, childList:true, characterData:true});
})();
