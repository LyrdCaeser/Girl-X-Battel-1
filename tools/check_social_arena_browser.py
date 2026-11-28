"""One real mobile browser plus three other authenticated HTTP participants."""
import sys,importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
spec=importlib.util.spec_from_file_location('qa',root/'tests/test_pvp_http_sessions_20261113.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)
case=qa.PvPHttpSessionTests('test_social_arena_four_authenticated_sessions');case.setUp()
try:
 from gxb2 import social_arena as a,s5_test as s,live_service as l
 l.create_world('S4','S4 QA');l.create_world('S5',s.NAME)
 st,p,h=case.request('POST','/api/auth/register',{'username':'HttpTestPlayer3','password':'ExamplePassword123A','character_name':'Player 4','server_id':'S1'})
 assert st==200,p;case.tokens.append(h['set-cookie'].split(';',1)[0])
 now=[a.START+60]
 with patch.object(a,'enabled',return_value=True),patch.object(a,'time',SimpleNamespace(time=lambda:now[0])),patch.object(s,'schedule',return_value=s.schedule(now[0])):
  for i in range(4):case.call('POST','/api/auth/create-character',{'server_id':'S5','character_name':'Giao Luu '+str(i)},i)
  for i in (1,2,3):case.call('POST','/api/social-arena/action',{'action':'join'},i)
  base=f'http://127.0.0.1:{case.port}'
  with sync_playwright() as p:
   b=p.chromium.launch(headless=True,args=['--no-sandbox'])
   ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,bypass_csp=True)
   k,v=case.tokens[0].split('=',1);ctx.add_cookies([{'name':k,'value':v,'url':base}])
   page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(base+'/',wait_until='domcontentloaded',timeout=20000)
   page.wait_for_function("typeof state!=='undefined'&&state?.server_id==='S5'&&view==='home'",timeout=20000)
   page.locator('.home-destinations button[data-view=league]').click(timeout=15000)
   page.wait_for_function("view==='league'",timeout=12000)
   page.evaluate("NativeOnlineArenas.open('arena','league')")
   page.wait_for_function("view==='arena'",timeout=12000)
   try:page.locator('.social-arena-entry').wait_for(timeout=7000)
   except Exception:
    print('Arena HTTP:',case.request('GET','/api/pvp/status?mode=arena',user=0)[0],flush=True)
    print('browser',page.evaluate("({view,app:typeof SocialArena,body:document.body.innerText.slice(0,1000)})"),errors[-8:],flush=True)
    raise
   page.locator('.social-arena-entry').click()
   page.get_by_role('button',name='Chiến Đấu',exact=True).click(timeout=10000)
   page.get_by_text('Đã tìm thấy trận đấu!',exact=True).wait_for(timeout=10000)
   mid=case.call('GET','/api/social-arena/status',user=1)['match']['id']
   page.get_by_role('button',name='Xác nhận tham gia',exact=True).click()
   for i in (1,2,3):case.call('POST','/api/social-arena/action',{'action':'accept','match_id':mid},i)
   page.locator('.social-lineup').first.wait_for(timeout=10000)
   assert page.locator('.social-lineup').count()==4
   assert page.get_by_role('button',name='Bắt Đầu',exact=True).is_disabled()
   now[0]+=6
   page.wait_for_function("!Array.from(document.querySelectorAll('.social-arena-win button')).find(e=>e.textContent==='Bắt Đầu')?.disabled",timeout=10000)
   assert page.locator('.social-arena-win').evaluate("e=>{let r=e.getBoundingClientRect();return r.left>=-1&&r.right<=innerWidth+1}")
   print('PASS mobile native entry, four formations, 5s preview gate')
   print('Browser errors:',errors[-3:]);b.close()
finally:case.doCleanups()
