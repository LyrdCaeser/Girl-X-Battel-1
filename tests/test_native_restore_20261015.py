"""Non-production regression guards for the restored original GXB3 interfaces."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class NativeRestore20261015Tests(unittest.TestCase):
    def read(self,p): return (ROOT/p).read_text(encoding='utf-8')

    def test_event_catalog_visible_without_inventing_payouts(self):
        ui=self.read('web/events.js')
        self.assertIn('const rows=[...all];',ui)
        self.assertIn('publicGemPacks.filter',ui)
        self.assertIn('Chức năng nhận thưởng chưa được xác thực',ui)

    def test_mail_attachments_reuse_publisher_item_icons(self):
        ui=self.read('web/home-menus.js')
        self.assertIn('const nativePicture=',ui)
        self.assertIn('itemPicture(original)',ui)
        self.assertIn('if(id===\'999999991\')',ui)

    def test_original_assistant_hit_areas_exist(self):
        html=self.read('web/index.html')
        css=self.read('web/game-assistant.css')
        js=self.read('web/game-assistant.js')
        self.assertIn('/game-assistant.css?',html)
        self.assertIn('.ga2-stage>*{position:absolute;',css)
        self.assertIn('.ga2-scroll{z-index:8;',css)
        self.assertIn('.ga2-btn{cursor:pointer;z-index:12;',css)
        self.assertIn("'/api/assistant/run'",js)

    def test_live_guild_retries_instead_of_frozen_loading(self):
        ui=self.read('web/guild.js')
        self.assertIn("api('/api/world-guild')",ui)
        self.assertIn('Promise.race',ui)
        self.assertIn("'Tải lại Bang Hội'",ui)
        self.assertIn('renderOnlineGuild',ui)

    def test_native_mobile_book_and_evolution_vietnamese(self):
        ui=self.read('web/fantasy-book.js')
        app=self.read('web/app.js')
        engine=self.read('gxb2/engine.py')
        self.assertIn("st.style.setProperty('--u',scale+'px','important')",ui)
        self.assertIn('Đã đủ nguyên liệu.',app)
        self.assertIn("GameError('Không đủ nguyên liệu')",engine)

if __name__=='__main__':
    unittest.main()
