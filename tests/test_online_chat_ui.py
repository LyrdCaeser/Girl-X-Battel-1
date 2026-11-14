"""Only real authenticated chat messages may appear in the in-game chat UI."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class RealChatUiTests(unittest.TestCase):
    def test_chat_uses_online_server_and_never_renders_npc_chat(self):
        home=(ROOT/"web/home-menus.js").read_text(encoding="utf-8")
        start=home.index(" function chat(parent){")
        end=home.index("\n async function claimServerMail(",start)
        screen=home[start:end]
        self.assertNotIn("Bots.chat",screen)
        self.assertNotIn("simulated players",screen)
        self.assertNotIn("local drafts",screen)
        self.assertIn("refreshRealChat",screen)
        self.assertIn("submitRealChat",screen)
        self.assertIn("m.character_name",screen)
        self.assertIn("m.message",screen)

    def test_authenticated_server_api_is_used_for_chat(self):
        home=(ROOT/"web/home-menus.js").read_text(encoding="utf-8")
        server=(ROOT/"server.py").read_text(encoding="utf-8")
        live=(ROOT/"gxb2/live_service.py").read_text(encoding="utf-8")
        self.assertIn("'/api/chat/messages?channel='",home)
        self.assertIn("api('/api/chat/send'",home)
        self.assertIn("window.setInterval",home)
        self.assertIn("path == '/api/chat/messages'",server)
        self.assertIn("path == '/api/chat/send'",server)
        self.assertIn("chat_messages(",live)
        self.assertIn("send_chat_message(",live)
        self.assertIn("world_chat_messages",live)

if __name__=="__main__":
    unittest.main()
