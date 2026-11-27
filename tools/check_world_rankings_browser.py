import sys,importlib.util,json
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
 states=[case.call('GET','/api/state',user=i) for i in (0,1)]
 db=live_service._db()
 try:
  live_service._ensure_social_tables(db)
  for i,st in enumerate(states):
   uid=st['uid'];engine=case.pool.get(uid,'S1',st['name'])
   saved=engine._load();saved['max_stage']=i+1;saved['tower']={'max_stage':10+i}
   db.execute("INSERT INTO player_profiles(uid,server_id,data,updated_at) VALUES(?,?,?,?) ON CONFLICT(uid,server_id) DO UPDATE SET data=excluded.data",(uid,'S1',json.dumps(saved),1))
  db.commit()
 finally:db.close()
 base=f'http://127.0.0.1:{case.port}'
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
  for w,h in [(390,844),(320,568),(1280,900)]:
   ctx=browser.new_context(viewport={'width':w,'height':h},is_mobile=w<600,has_touch=w<600,bypass_csp=True)
   key,value=case.tokens[0].split('=',1);ctx.add_cookies([{'name':key,'value':value,'url':base}])
   page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(base+'/',wait_until='domcontentloaded',timeout=25000)
   try:
    page.wait_for_function("typeof state!=='undefined' && state?.uid && typeof WorldRankings!=='undefined' && view==='home'",timeout=20000)
    trigger=page.locator('.home-rankings');trigger.wait_for(state='visible')
    box=trigger.bounding_box(); assert box['x']>=0 and box['x']+box['width']<=w,(w,box)
    diary=page.locator('.home-left .gd-home').nth(1)
    event=page.locator('.home-left button').filter(has=page.locator('[data-sprite="act_bg_img_2_v3_h5"]'))
    diary_box=diary.bounding_box()
    event_icon=event.locator('.home-original').bounding_box()
    rank_icon=trigger.locator('.home-original').bounding_box()
    print('Lobby geometry',w,h,box,diary_box,event_icon,rank_icon,flush=True)
    assert abs(box['y']-diary_box['y'])<=1
    assert abs(rank_icon['width']-event_icon['width'])<=1 and abs(rank_icon['height']-event_icon['height'])<=1
    assert box['x']>=diary_box['x']+diary_box['width']

    trigger.click()
    page.locator('.world-rank-win .ar-row2').first.wait_for(timeout=12000)
    assert page.locator('.world-rank-win .ar-row2').count()==2
    assert page.locator('.wr-tabs button').count()==7
    page.locator('.wr-tabs').get_by_role('button',name='Liên Server',exact=True).click()
    page.wait_for_function("document.querySelector('.wr-status')?.textContent.startsWith('Liên Server · S1–S3')")
    assert page.locator('.wr-cross .ar2-server').first.is_visible()
    assert page.locator('.wr-cross .ar2-server b').first.inner_text()=='S1'
    page.locator('.wr-tabs').get_by_role('button',name='Chiến Dịch',exact=True).click()
    page.wait_for_function("document.querySelector('.wr-list .ar2-plabel')?.textContent==='Ải đã vượt'")
    page.locator('.wr-tabs').get_by_role('button',name='Các Hệ',exact=True).click()
    page.locator('.wr-groups button').first.wait_for()
    assert page.locator('.wr-groups button').count()==8
    assert page.locator('.wr-groups button img').evaluate_all("(xs)=>xs.map(x=>x.getAttribute('src'))")==['/assets/factions/group'+str(i)+'.png' for i in [1,2,3,4,6,5,7,8]]
    page.locator('.wr-groups').get_by_role('button',name='Hệ Hỗn Độn',exact=True).click()
    page.wait_for_function("document.querySelector('.wr-status')?.textContent.includes('0 người chơi')")
    assert page.locator('.wr-list .ar-empty').is_visible()
    page.locator('.wr-tabs').get_by_role('button',name='Lực Chiến',exact=True).click()
    page.locator('.world-rank-win .ar-row2').first.wait_for(timeout=10000)
    assert page.locator('.world-rank-win').evaluate("e=>{const r=e.getBoundingClientRect();return r.left>=-1&&r.right<=innerWidth+1&&r.top>=-1&&r.bottom<=innerHeight+1}")
    assert page.locator('.wr-list').evaluate("e=>e.scrollWidth<=e.clientWidth+2")
    print('PASS real game UI',w,h,'native controls, all icons, rank rows, no horizontal overflow',flush=True)
   except Exception:
    print('Browser errors',errors[-8:]);print('View:',page.evaluate("typeof view==='undefined'?'undefined':view"));print('Body:',page.locator('body').inner_text()[:500]);raise
   finally:ctx.close()
  browser.close()
finally:case.doCleanups()
