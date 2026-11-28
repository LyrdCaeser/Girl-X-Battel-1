import base64,io,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from gxb2 import database,live_service,social_bar as b

class BarTests(unittest.TestCase):
    def setUp(self):
        self.assertFalse(database.is_postgres())
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        path=Path(t.name)/'bar.sqlite'
        p=patch.object(live_service,'_db',lambda:database.connect(path,'live'));p.start();self.addCleanup(p.stop)
        self.now=2000000000
    def test_scope_and_cross_chat(self):
        n=self.now
        self.assertEqual(len(b.rooms('A','S1',n)),2)
        with self.assertRaises(ValueError):b.enter('B','S2','B','public:S1',now=n)
        for uid,w in [('A','S1'),('B','S5'),('C','S4')]:b.enter(uid,w,uid,'public:CROSS',now=n)
        mid=b.send('A','S1','A','public:CROSS','Xin chào',now=n)
        data=b.poll('B','S5','public:CROSS',n+1)
        self.assertEqual(data['messages'][0]['id'],mid)
        self.assertEqual(len(data['members']),3)
        self.assertFalse(data['voice_enabled'])
        with self.assertRaises(ValueError):b.send('A','S1','A','public:CROSS','Spam',now=n+1)
        with self.assertRaises(ValueError):b.poll('D','S3','public:CROSS',n+1)
        b.action('B','S5','public:CROSS','block',target='A',now=n+1)
        self.assertEqual(b.poll('B','S5','public:CROSS',n+2)['messages'],[])
        b.action('B','S5','public:CROSS','unblock',target='A',now=n+2)
        b.action('A','S1','public:CROSS','delete',mid=mid,now=n+3)
        self.assertEqual(b.poll('B','S5','public:CROSS',n+4)['messages'],[])
    def test_private_room_image_and_moderation(self):
        n=self.now
        room=b.create('A','S1','Phòng riêng','CROSS','private','abcd',now=n)
        b.enter('A','S1','A',room,now=n)
        with self.assertRaises(ValueError):b.enter('B','S5','B',room,'bad',now=n)
        b.enter('B','S5','B',room,'abcd',now=n)
        buf=io.BytesIO();Image.new('RGB',(100,100),'blue').save(buf,'PNG')
        raw=base64.b64encode(buf.getvalue()).decode()
        mid=b.send('A','S1','A',room,'Ảnh',image=raw,now=n)
        img=b.image('B','S5',room,mid,n+1)
        with Image.open(io.BytesIO(base64.b64decode(img))) as im:self.assertEqual(im.format,'WEBP')
        with self.assertRaises(ValueError):b.image('C','S3',room,mid,n+1)
        with self.assertRaises(ValueError):b.send('B','S5','B',room,'Ảnh lỗi',image='not-valid',now=n+2)
        with self.assertRaises(ValueError):b.action('B','S5',room,'kick',target='A',now=n+2)
        b.action('B','S5',room,'report',mid=mid,reason='Test',now=n+2)
        b.action('A','S1',room,'chat',target='B',now=n+2)
        with self.assertRaises(ValueError):b.send('B','S5','B',room,'Bị cấm',now=n+3)
        b.action('A','S1',room,'kick',target='B',now=n+3)
        with self.assertRaises(ValueError):b.poll('B','S5',room,n+4)
        b.action('A','S1',room,'close',now=n+4)
        with self.assertRaises(ValueError):b.enter('B','S5','B',room,'abcd',now=n+5)
    def test_server_room_and_presence_expire(self):
        n=self.now
        b.enter('A','S1','A','public:S1',now=n)
        self.assertEqual(b.poll('A','S1','public:S1',n+10)['members'][0]['name'],'A')
        with self.assertRaises(ValueError):b.poll('A','S1','public:S1',n+56)
        with self.assertRaises(ValueError):b.create('A','S1','QTV','CROSS','gm',now=n)
