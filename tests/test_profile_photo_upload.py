"""Real HTTP photo upload, identity isolation, image sanitation and deletion."""
import http.client
import io
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from gxb2 import auth, database, live_service, player_engines, profile_photos
from gxb2.engine import Engine
from server import make_servers


class ProfilePhotoHTTPTests(unittest.TestCase):
    def setUp(self):
        if database.POSTGRES:
            self.skipTest('Never run isolated fixture tests on Production/Neon')
        self.temp = tempfile.TemporaryDirectory(prefix='gxb3-profile-photo-')
        self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name)
        for module,path,kind in ((auth,root/'accounts.sqlite3','auth'),
                                 (live_service,root/'world.sqlite3','live')):
            context = patch.object(module, '_db', lambda p=path,k=kind: database.connect(p,k))
            context.start();self.addCleanup(context.stop)
        for module,field,value in ((player_engines,'ROOT',root),
                                   (profile_photos,'LOCAL_DB',root/'photos.sqlite3')):
            context=patch.object(module,field,value)
            context.start();self.addCleanup(context.stop)
        self.engine=Engine(root/'developer.sqlite3')
        self.pool=player_engines.PlayerEnginePool()
        self.http,self.tcp=make_servers(self.engine,0,0,player_engines=self.pool,trust_proxy=False)
        self.thread=threading.Thread(target=self.http.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)
        self.port=self.http.server_port
        self.cookies=[]
        for i in range(2):
            status,result,headers=self.request('POST','/api/auth/register',json_data={
                'username':'PhotoTester'+str(i),'password':'ExamplePassword123A',
                'character_name':'Photo Tester '+str(i),'server_id':'S1'})
            self.assertEqual(status,200,result)
            self.cookies.append(headers['set-cookie'].split(';',1)[0])

    def stop(self):
        self.http.shutdown();self.http.server_close();self.tcp.server_close()
        self.thread.join(timeout=5)
        self.pool.close();self.engine.close()

    def request(self,method,path,raw=None,ctype=None,user=None,json_data=None,extra_headers=None):
        headers=dict(extra_headers or {})
        if user is not None:headers['Cookie']=self.cookies[user]
        if json_data is not None:
            raw=json.dumps(json_data).encode();ctype='application/json'
        if ctype:headers['Content-Type']=ctype
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=30)
        try:
            conn.request(method,path,body=raw,headers=headers)
            res=conn.getresponse();buf=res.read()
            body=buf if res.getheader('Content-Type','').startswith('image/webp') else json.loads(buf)
            return res.status,body,{k.lower():v for k,v in res.getheaders()}
        finally:conn.close()

    def png(self,colour='red'):
        image=Image.new('RGB',(840,580),colour)
        exif=Image.Exif();exif[271]='Sensitive camera metadata'
        output=io.BytesIO();image.save(output,'JPEG',exif=exif)
        return output.getvalue()

    def test_authenticated_upload_renders_public_reencoded_photo_and_locks_owner(self):
        original=self.png()
        code,_,_=self.request('POST','/api/profile/photo/upload',raw=original,ctype='image/jpeg')
        self.assertEqual(code,401)
        code,uploaded,_=self.request('POST','/api/profile/photo/upload',raw=original,ctype='image/jpeg',user=0)
        self.assertEqual(code,200,uploaded)
        key=uploaded['avatar'];self.assertRegex(key,r'^custom_[0-9a-f]{32}$')
        self.assertEqual(uploaded['state']['profile']['avatar'],key)
        self.assertEqual(uploaded['state']['profile']['uploaded_avatar'],key)
        path='/api/profile/photo/'+key+'.webp'
        code,data,headers=self.request('GET',path)
        self.assertEqual(code,200)
        self.assertTrue(data.startswith(b'RIFF') and data[8:12]==b'WEBP')
        self.assertNotIn(b'Sensitive camera metadata',data)
        self.assertLess(len(data),profile_photos.MAX_STORED_BYTES)
        with Image.open(io.BytesIO(data)) as img:
            self.assertEqual(img.size,(320,320))
            self.assertEqual(img.format,'WEBP')
            self.assertFalse(img.info.get('exif'))
        state=self.request('GET','/api/state',user=0)[1]
        self.assertEqual(state['profile']['frame'],'frame_8007')
        self.assertEqual(state['profile']['avatar'],key)
        deny=self.request('POST','/api/profile',json_data={'avatar':key},user=1)
        self.assertEqual(deny[0],400,'A different UID must never select someone else\'s photo token')
        ok=self.request('POST','/api/profile',json_data={'avatar':key},user=0)
        self.assertEqual(ok[0],200)
        self.assertEqual(ok[1]['state']['profile']['avatar'],key)

    def test_replace_then_delete_photo_preserves_original_frame_and_unlocks(self):
        c,a,_=self.request('POST','/api/profile/photo/upload',raw=self.png('blue'),ctype='image/jpeg',user=0)
        self.assertEqual(c,200,a);old=a['avatar']
        # Switching to an original unlocked head does not lose the uploaded photo.
        c,original,_=self.request('POST','/api/profile',json_data={'avatar':'head_1001'},user=0)
        self.assertEqual(c,200,original)
        self.assertEqual(original['state']['profile']['uploaded_avatar'],old)
        c,b,_=self.request('POST','/api/profile/photo/upload',raw=self.png('green'),ctype='image/jpeg',user=0)
        self.assertEqual(c,200,b)
        self.assertNotEqual(old,b['avatar'])
        self.assertEqual(self.request('GET','/api/profile/photo/'+old+'.webp')[0],404)
        self.assertEqual(self.request('GET','/api/profile/photo/'+b['avatar']+'.webp')[0],200)
        c,d,_=self.request('POST','/api/profile/photo/delete',user=0)
        self.assertEqual(c,200,d)
        self.assertEqual(d['state']['profile']['avatar'],'head_1001')
        self.assertNotIn('uploaded_avatar',d['state']['profile'])
        self.assertEqual(d['state']['profile']['frame'],'frame_8007')
        self.assertEqual(self.request('GET','/api/profile/photo/'+b['avatar']+'.webp')[0],404)
        self.assertEqual(self.request('POST','/api/profile',json_data={'avatar':b['avatar']},user=0)[0],400)

    def test_reject_fake_payload_bad_origin_bad_format_and_limit(self):
        self.assertEqual(self.request('POST','/api/profile/photo/upload',raw=b'<svg><script>x</script></svg>',ctype='image/svg+xml',user=0)[0],400)
        self.assertEqual(self.request('POST','/api/profile/photo/upload',raw=b'not a png',ctype='image/png',user=0)[0],400)
        self.assertEqual(self.request('POST','/api/profile/photo/upload',raw=self.png(),ctype='image/jpeg',user=0,extra_headers={'Origin':'https://attacker.invalid'})[0],403)
        invalid=self.request('GET','/api/profile/photo/custom_deadbeef.webp')
        self.assertEqual(invalid[0],401)
        # Unauthenticated API routes are private except for valid public image tokens.
        self.assertEqual(self.request('GET','/api/profile/photo/custom_'+'0'*32+'.webp')[0],404)

    def test_raw_upload_size_and_oversized_image_rejected(self):
        huge=Image.new('RGB',(5000,2500),'white')
        b=io.BytesIO();huge.save(b,'PNG')
        status,value,_=self.request('POST','/api/profile/photo/upload',raw=b.getvalue(),ctype='image/png',user=0)
        self.assertEqual(status,400,value)
        status,value,_=self.request('POST','/api/profile/photo/upload',raw=b'X',ctype='image/jpeg',user=1,extra_headers={'Content-Length':str(3*1024*1024+1)})
        self.assertEqual(status,413,value)

    def test_web_and_native_gallery_pickers_are_wired(self):
        root=Path(__file__).resolve().parents[1]
        index=(root/'web/index.html').read_text(encoding='utf-8')
        browser=(root/'web/app.js').read_text(encoding='utf-8')
        for marker in ('profile-photo-file','profile-photo-upload','profile-photo-delete','image/jpeg,image/png,image/webp'):
            self.assertIn(marker,index)
        for marker in ('/api/profile/photo/upload','/api/profile/photo/delete','profilePhotoBlob','custom_[0-9a-f]{32}'):
            self.assertIn(marker,browser)
        for file in ('web/guild.js','web/arena.js'):
            self.assertIn('/api/profile/photo/',(root/file).read_text(encoding='utf-8'))
        android=(root/'clients/android/app/src/main/java/com/gxb3/game/MainActivity.java').read_text(encoding='utf-8')
        for marker in ('onShowFileChooser','ACTION_OPEN_DOCUMENT','onActivityResult','setAllowFileAccess(false)','setAllowContentAccess(true)'):
            self.assertIn(marker,android)
        import plistlib
        with (root/'clients/ios/Info.plist').open('rb') as f:
            self.assertIn('NSPhotoLibraryUsageDescription',plistlib.load(f))
        workflow=(root/'.github/workflows/gxb3-clients.yml').read_text(encoding='utf-8')
        self.assertIn('default: false',workflow)
        self.assertIn("github.event_name == 'workflow_dispatch' && inputs.publish == true",workflow)

    def test_upload_rate_limit_is_per_account_not_shared_wifi(self):
        for i in range(3):
            self.assertEqual(self.request('POST','/api/profile/photo/upload',raw=self.png(),ctype='image/jpeg',user=0)[0],200)
        self.assertEqual(self.request('POST','/api/profile/photo/upload',raw=self.png(),ctype='image/jpeg',user=0)[0],429)
        self.assertEqual(self.request('POST','/api/profile/photo/upload',raw=self.png(),ctype='image/jpeg',user=1)[0],200)


if __name__=='__main__':unittest.main()
