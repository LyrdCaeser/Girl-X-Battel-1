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
        self.assertIn('.ga2-x,.ga2-help,.ga2-tab,.ga2-btn{cursor:pointer;',css)
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

    def test_login_remember_and_safeguards(self):
        auth=self.read('web/auth.js')
        server=self.read('server.py')
        css=self.read('web/auth.css')
        self.assertIn("Lưu đăng nhập",auth)
        self.assertIn("remember_login:save.checked",auth)
        self.assertIn("localStorage.setItem(REMEMBER_KEY",auth)
        self.assertNotIn("password:pass.value",auth.split("localStorage.setItem(REMEMBER_KEY")[1].split("localStorage.removeItem")[0])
        self.assertIn("data.get('remember_login') is True",server)
        self.assertIn("cookie += f\"; Max-Age={auth.SESSION_TTL}\"",server)
        self.assertIn("HttpOnly; SameSite=Lax",server)
        self.assertIn("url('/assets/login/gxb3-wedding-promo.webp')",css)
        promo=ROOT/'web/assets/login/gxb3-wedding-promo.webp'
        self.assertTrue(promo.is_file(), 'Referenced login background must exist')
        self.assertGreater(promo.stat().st_size,30000,'Preserve mobile-resolution original background')
        self.assertEqual(promo.read_bytes()[:4],b'RIFF')
        self.assertIn("prefers-reduced-motion",css)

    def test_original_girl_voice_and_viewport(self):
        app=self.read('web/app.js')
        girls=self.read('web/girl-ui.css')
        dates=self.read('web/dates.js')
        summon=self.read('web/summon-anim.js')
        summon_css=self.read('web/summon-anim.css')
        self.assertIn("Dates.playGirlVoice(h.table_id)",app)
        self.assertIn("async function playGirlVoice(tableId)",dates)
        self.assertIn("allLines({table_id:id})",dates)
        self.assertIn("'/assets/voices/'+sound+'.mp3'",dates)
        self.assertIn("voiceIndex.set(key,(next+1)%lines.length)",dates)
        self.assertIn("Dates.playGirlVoice(p.table_id)",summon)
        self.assertIn("max-width:none!important;object-fit:contain;",girls)
        self.assertIn("background:linear-gradient(#fff,#eef3ffed)",girls)
        self.assertIn(".sa-stage{inset:0;width:100%;height:100%;transform:none}",summon_css)

if __name__=='__main__':
    unittest.main()
