"""Native League guide retains pictures while Vietnamese labels replace English."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class ArenaGuideViTest(unittest.TestCase):
    def test_all_prose_localized_and_original_images_preserved(self):
        guide=json.loads((ROOT/'web/assets/img-guides/catalog.json').read_text())['guides']['arena_window']
        self.assertEqual(len(guide['pages']),2)
        self.assertEqual(guide['name'],'Đấu Trường')
        captions=[]
        images=[]
        for page in guide['pages']:
            for node in page['nodes']:
                if node.get('src'):images.append(node['src'])
                elif node.get('text'):
                    captions.append(node['text'])
        for text in captions:
            if text.strip().rstrip('/').strip() in ('1','2','3','4'):continue
            self.assertTrue(any(t in text for t in ('đội hình','Chạm','Chọn','Chiến thắng',
                'Điểm','Phần thưởng','Mùa Đấu Trường','Kim Cương')),text)
        self.assertEqual(len(images),21)
        self.assertTrue(any('img_guide_arena_icon6_en_en' in url for url in images))

    def test_button_overlays_and_web_cache(self):
        script=(ROOT/'web/img-guides.js').read_text()
        self.assertIn("['Hằng Ngày','daily']",script)
        self.assertIn("['Theo Mùa','season']",script)
        html=(ROOT/'web/index.html').read_text()
        self.assertIn('/img-guides.js?v=20261116-arena-guide-vi-r2',html)
        self.assertIn('/img-guides.css?v=20261116-arena-guide-vi-r2',html)


if __name__=='__main__':unittest.main()
