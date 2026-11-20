"""GXB3 live chat security and authenticity: no seeded chats, no UID spoofing.

Tests use an isolated disposable SQLite database; never production/player data.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gxb2 import database, live_service


class LiveChatRC7Tests(unittest.TestCase):
    def setUp(self):
        if database.is_postgres():
            self.skipTest("This test is for isolated SQLite, not the live PostgreSQL DB")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "live-chat.sqlite3"
        self.patch_path = patch.object(live_service, "DB_PATH", self.path)
        self.patch_path.start()
        self.addCleanup(self.patch_path.stop)
        live_service.register_player("UID-A", "S1", "Người chơi A")
        live_service.register_player("UID-B", "S1", "Người chơi B")
        live_service.create_world("S2", "Máy chủ S2")
        live_service.register_player("UID-C", "S2", "Người chơi C")

    def test_empty_chat_is_really_empty(self):
        self.assertEqual(live_service.chat_messages("UID-A", "S1", "world"), [])
        home=(Path(__file__).resolve().parents[1]/"web"/"home-menus.js").read_text(encoding="utf-8")
        self.assertNotIn("Bots.chat(tab)",home)
        self.assertIn("api('/api/chat/send'",home)
        self.assertNotIn("Channel messages come from simulated players",home)

    def test_public_chat_persists_only_on_correct_server_and_channel(self):
        a=live_service.send_chat_message("UID-A","S1","world","Xin chào thế giới")
        self.assertEqual(a["character_name"],"Người chơi A")
        self.assertEqual([r["message"] for r in live_service.chat_messages("UID-B","S1","world")],
                         ["Xin chào thế giới"])
        self.assertEqual(live_service.chat_messages("UID-C","S2","world"),[])
        self.assertEqual(live_service.chat_messages("UID-A","S1","recruit"),[])

    def test_private_messages_are_never_exposed_to_third_party(self):
        live_service.register_player("UID-D","S1","Người chơi D")
        live_service.send_chat_message("UID-A","S1","private","Chỉ gửi cho B","UID-B")
        self.assertEqual(len(live_service.chat_messages("UID-B","S1","private")),1)
        self.assertEqual(len(live_service.chat_messages("UID-A","S1","private","UID-B")),1)
        self.assertEqual(live_service.chat_messages("UID-D","S1","private"),[])
        self.assertEqual(live_service.chat_messages("UID-C","S2","private"),[])
        self.assertEqual(live_service.chat_messages("UID-D","S1","private","UID-A"),[])

    def test_cannot_message_unknown_uid_or_cross_server(self):
        with self.assertRaisesRegex(ValueError,"UID"):
            live_service.send_chat_message("UID-A","S1","private","Tin nhắn","UID-C")
        with self.assertRaisesRegex(ValueError,"UID"):
            live_service.send_chat_message("UID-A","S1","private","Tin nhắn","UID-NONE")
        with self.assertRaisesRegex(ValueError,"người nhận"):
            live_service.send_chat_message("UID-A","S1","world","Tin nhắn","UID-B")

    def test_sender_name_is_always_from_server_and_banned_cannot_chat(self):
        live_service.set_ban("UID-A","S1",True,"Kiểm tra")
        with self.assertRaisesRegex(ValueError,"quyền"):
            live_service.send_chat_message("UID-A","S1","world","Thử gửi")
        with self.assertRaisesRegex(ValueError,"quyền"):
            live_service.chat_messages("UID-A","S1","world")

    def test_sender_length_and_spam_prevention(self):
        with self.assertRaisesRegex(ValueError,"280"):
            live_service.send_chat_message("UID-A","S1","world","x"*281)
        live_service.send_chat_message("UID-A","S1","world","Tin số 1")
        with self.assertRaisesRegex(ValueError,"quá nhanh"):
            live_service.send_chat_message("UID-A","S1","world","Tin số 2")


if __name__ == "__main__":
    unittest.main()
