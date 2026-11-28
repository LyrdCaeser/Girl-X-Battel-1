"""Two real game sessions + real SFU using temporary SQLite, synthetic mic."""
import importlib.util,sys
from pathlib import Path
from unittest.mock import patch
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
spec=importlib.util.spec_from_file_location('qa',root/'tests/test_pvp_http_sessions_20261113.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)
from gxb2 import social_bar as bar,social_voice as voice,live_service,s5_test
case=qa.PvPHttpSessionTests('test_social_bar_authenticated_http');case.setUp()
try:
 live_service.create_world("S4","S4 QA");live_service.create_world("S5",s5_test.NAME)
 with patch.object(bar,'enabled',return_value=True),patch.object(voice,'enabled',return_value=True),patch.object(voice,'_start',return_value=None):
  base=f'http://127.0.0.1:{case.port}'
  with sync_playwright() as p:
   browser=p.chromium.launch(headless=True,args=['--no-sandbox','--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream','--autoplay-policy=no-user-gesture-required'])
   pages=[]
   try:
    for i in (0,1):
     ctx=browser.new_context(viewport={'width':390,'height':844},permissions=['microphone'],is_mobile=True,has_touch=True,bypass_csp=True)
     k,v=case.tokens[i].split('=',1);ctx.add_cookies([{'name':k,'value':v,'url':base}])
     page=ctx.new_page();page.set_default_timeout(12000)
     page.goto(base+'/',wait_until='domcontentloaded')
     page.wait_for_function("typeof state!=='undefined'&&state?.social_bar_enabled===true&&view==='home'")
     page.locator('.home-bottom button[data-coming=Menu]').click()
     page.get_by_text('Quán Bar',exact=True).click()
     page.get_by_text('Phòng Liên Server',exact=True).first.click()
     page.get_by_role('button',name='Vào phòng',exact=True).first.click()
     page.locator('.social-voice-toggle').click()
     page.get_by_role('button',name='Tham gia Voice',exact=True).click()
     page.get_by_role('button',name='Bật Mic',exact=True).wait_for()
     pages.append(page)
    pages[0].get_by_role('button',name='Bật Loa',exact=True).click()
    pages[1].get_by_role('button',name='Bật Mic',exact=True).click()
    pages[1].get_by_role('button',name='Tắt Mic',exact=True).wait_for()
    pages[0].wait_for_function("Array.from(document.querySelectorAll('audio')).some(a=>a.srcObject?.getAudioTracks().some(t=>t.readyState==='live')&&!a.muted)",timeout=15000)
    print('PASS actual game UI: two authenticated sessions, join, microphone and live remote audio track')
    pages[1].get_by_role('button',name='Tắt Mic',exact=True).click()
    pages[1].get_by_role('button',name='Bật Mic',exact=True).wait_for()
    pages[0].get_by_role('button',name='Rời Voice',exact=True).click()
    pages[0].get_by_role('button',name='Tham gia Voice',exact=True).wait_for()
    print('PASS actual game UI: turn off mic and leave voice')
   finally:
    browser.close()
    for key,lease in list(voice._leases.items()):voice._remove(key,lease)
finally:case.doCleanups()
