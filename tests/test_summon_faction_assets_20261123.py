"""Real HTTP checks for original faction art used by the Wish Spine reveal.

Only a disposable localhost HTTP server is started; no production database
or player data is opened or modified.
"""
from hashlib import sha256
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen
import json
import threading
import unittest

from server import HTTPHandler

ROOT=Path(__file__).resolve().parents[1]


class QuietHandler(HTTPHandler):
    def log_message(self,*args):pass


class SummonFactionAssetRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=ThreadingHTTPServer(('127.0.0.1',0),QuietHandler)
        cls.http.public_origin=''
        cls.http.trust_proxy=False
        cls.worker=threading.Thread(target=cls.http.serve_forever,daemon=True)
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.worker.join(timeout=5)

    def get(self,path):
        return urlopen(f'http://127.0.0.1:{self.http.server_port}{path}',timeout=5)

    def test_faction_original_images_reachable_through_both_existing_urls(self):
        for group in range(1,9):
            original=(ROOT/f'web/assets/factions/group{group}.png').read_bytes()
            self.assertTrue(original.startswith(b'\x89PNG\r\n\x1a\n'))
            for path in (f'/assets/factions/{group}.png',
                         f'/assets/factions/group{group}.png'):
                with self.subTest(group=group,path=path),self.get(path) as response:
                    self.assertEqual(response.status,200)
                    self.assertEqual(response.headers['Content-Type'],'image/png')
                    self.assertEqual(sha256(response.read()).digest(),sha256(original).digest())

    def test_mythra_correct_group_4_and_matching_asset(self):
        catalog=json.loads((ROOT/'web/assets/girls-catalog.json').read_text())
        mythra=next(g for g in catalog if g['id']==34003)
        self.assertEqual(mythra['name'],'Mythra')
        self.assertEqual(mythra['group'],4)
        with self.get('/assets/factions/group4.png') as response:
            self.assertEqual(response.status,200)
            self.assertEqual(response.read()[:8],b'\x89PNG\r\n\x1a\n')

    def test_reject_unknown_or_non_faction_paths(self):
        for path in ('/assets/factions/0.png','/assets/factions/9.png',
                     '/assets/factions/group0.png','/assets/factions/group9.png',
                     '/assets/factions/mythra.png','/assets/factions/../server.py',
                     '/assets/factions/group4.json'):
            with self.subTest(path=path),self.assertRaises(HTTPError) as error:
                self.get(path)
            self.assertEqual(error.exception.code,404)

    def test_reveal_uses_live_canonical_image_and_clears_wrong_baked_icon(self):
        js=(ROOT/'web/summon-anim.js').read_text()
        html=(ROOT/'web/index.html').read_text()
        self.assertIn("PIXI.Sprite.from('/assets/factions/'+group+'.png')",js)
        self.assertIn("fig.hackTextureBySlotName('zhiye',PIXI.Texture.EMPTY",js)
        self.assertIn("nativeFaction(e.fig,p);",js)
        self.assertIn('summon-anim.js?v=20261123-faction-reveal-r6',html)

if __name__=='__main__':unittest.main()
