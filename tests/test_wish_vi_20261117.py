"""Wish localization guard: text-only change, preserve draw odds and rewards."""
import hashlib, json, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class WishVietnameseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.new=json.loads((ROOT/'data/wish.json').read_text())

 def test_gameplay_data_not_changed(self):
  gameplay={key:self.new[key] for key in ('rows','partners','odds')}
  canonical=json.dumps(gameplay,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
  self.assertEqual(hashlib.sha256(canonical).hexdigest(),'a7da743d376118b93a1f2eb9fdb88a474bc61587f61f2b54c3b9a60b0faaf84c')
  self.assertEqual(len(self.new['text']),31)
 def test_screenshot_paragraph_fully_vietnamese(self):
  line=self.new['text']['WISH_GACHA_TIPS_3']
  self.assertIn('Bạn có thể tự do chọn hoặc thay đổi Nữ Thần Ước Nguyện',line)
  self.assertIn('không làm thay đổi tỷ lệ',line)
  for english in ('The Wish Girl','The odds','The Chance-increase','Changing'):
   self.assertNotIn(english,line)
 def test_other_help_text_translated(self):
  text=self.new['text']
  for key in ('WISH_GACHA_TIPS_1','WISH_GACHA_TIPS_2','WISH_GACHA_TIPS_3','WISH_GACHA_TEXT10',
              'WISH_GACHA_SELECT_PARTNER_WINDOW','WISH_GACHA_TEXT6'):
   self.assertTrue(any(ord(ch)>127 for ch in text[key]), key)
  for key in ('WISH_GACHA_NUM1','WISH_GACHA_NUM2','WISH_GACHA_NUM3','WISH_GACHA_NUM4','WISH_GACHA_NUM5',
              'WISH_GACHA_NUM6','WISH_GACHA_NUM7','WISH_GACHA_NUM8','WISH_GACHA_NUM9',
              'WISH_GACHA_TEXT7','WISH_GACHA_TEXT8'):
   self.assertRegex(text[key],r'^(?:[0-9x{}/ ]+)$')
 def test_frontend_uses_current_asset_version(self):
  js=(ROOT/'web/wish.js').read_text()
  html=(ROOT/'web/index.html').read_text()
  self.assertIn("T('WISH_GACHA_TIPS_3')",js)
  self.assertIn('/assets/wish.json?v=20261117-full-vi-r1',js)
  self.assertIn('/wish.js?v=20261117-full-vi-r1',html)
if __name__=='__main__':unittest.main()
