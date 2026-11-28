import sys,importlib.util,time
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
spec=importlib.util.spec_from_file_location('qa',root/'tests/test_pvp_http_sessions_20261113.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)
case=qa.PvPHttpSessionTests('test_world_rankings_authenticated_saved_data_and_isolation')
case.setUp()
try:
 from gxb2 import live_service
 live_service.create_world('S4','S4 QA')
 st=case.call('GET','/api/state',user=0)
 assert case.request('GET','/api/lobby/events')[0]==401
 data=case.call('GET','/api/lobby/events?server_id=S5',user=0)
 assert data['server_id']=='S1'
 assert all(e['start']<=data['now']<e['end'] for e in data['events'])
 assert len(data['events'])>=7
 base=f'http://127.0.0.1:{case.port}'
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
  ctx=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,bypass_csp=True)
  key,value=case.tokens[0].split('=',1);ctx.add_cookies([{'name':key,'value':value,'url':base}])
  page=ctx.new_page()
  page.goto(base+'/',wait_until='domcontentloaded')
  page.wait_for_function("document.querySelectorAll('.home-timed-event').length===6",timeout=20000)
  actual=page.locator('.home-timed-event').evaluate_all("xs=>xs.map(x=>x.dataset.eventKey)")
  assert actual==[e['key'] for e in data['events'][:6]]
  assert page.locator('.home-live-events [data-coming="Limited Gift"]').count()==0
  page.locator('.home-timed-event').first.click()
  page.wait_for_function("view==='events'")
  # Test expiration with a controlled clock response only in the isolated QA browser.
  altered={**data,'events':[dict(e) for e in data['events']]}
  altered['events'][0]['end']=data['now']+3
  page.route('**/api/lobby/events',lambda r:r.fulfill(json=altered))
  with page.expect_response("**/api/lobby/events",timeout=20000):
   page.evaluate("showView('home');LobbyEvents.sync()")
  first=actual[0]
  page.wait_for_function("(key)=>!Array.from(document.querySelectorAll('.home-timed-event')).some(x=>x.dataset.eventKey===key)",arg=first,timeout=9000)
  result=page.locator('.home-timed-event').evaluate_all("xs=>xs.map(x=>x.dataset.eventKey)")
  assert len(result)==6 and data['events'][6]['key'] in result,(result,actual)
  print('PASS real authenticated API, correct live shortcuts, direct event opening, automatic expiry and replacement without reload')
  browser.close()
finally:case.doCleanups()
