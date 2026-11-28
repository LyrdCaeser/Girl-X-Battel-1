"""Check the dedicated home shortcut in real browser sessions, isolated SQLite."""
import importlib.util,sys,json
from pathlib import Path
from unittest.mock import patch
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
spec=importlib.util.spec_from_file_location('qa',root/'tests/test_pvp_http_sessions_20261113.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)
from gxb2 import social_bar,live_service,s5_test
case=qa.PvPHttpSessionTests('test_social_bar_authenticated_http');case.setUp()
try:
 live_service.create_world('S4','S4 QA');live_service.create_world('S5',s5_test.NAME)
 with patch.object(social_bar,'enabled',return_value=True):
  base=f'http://127.0.0.1:{case.port}'
  with sync_playwright() as p:
   browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
   for w,h in [(390,844),(320,568),(1280,900)]:
    ctx=browser.new_context(viewport={'width':w,'height':h},is_mobile=w<600,has_touch=w<600,bypass_csp=True)
    k,v=case.tokens[0].split('=',1);ctx.add_cookies([{'name':k,'value':v,'url':base}])
    page=ctx.new_page();page.set_default_timeout(12000)
    page.goto(base+'/',wait_until='domcontentloaded')
    trigger=page.locator('.home-social-bar')
    trigger.wait_for(state='visible')
    assert trigger.locator('img').evaluate('i=>i.complete && i.naturalWidth>0')
    print('geometry',w,h,page.locator('.home-right>button').evaluate_all('xs=>xs.map(x=>[x.innerText,Math.round(x.getBoundingClientRect().top),Math.round(x.getBoundingClientRect().bottom)])'),flush=True)
    overlap=page.evaluate("""()=>{let a=[...document.querySelectorAll('.home-right>button')],b=[...document.querySelectorAll('.home-destinations>button,.home-bottom>button')];return a.flatMap(x=>b.filter(y=>{let r=x.getBoundingClientRect(),s=y.getBoundingClientRect();return Math.min(r.right,s.right)-Math.max(r.left,s.left)>2&&Math.min(r.bottom,s.bottom)-Math.max(r.top,s.top)>2}).map(y=>[x.innerText,y.innerText]))}""")
    assert not overlap,overlap
    trigger.click()
    page.locator('.social-bar-win .wr-tabs').get_by_text('Phòng Liên Server',exact=True).click()
    page.locator('.social-bar-win').get_by_role('button',name='Vào phòng',exact=True).first.click()
    page.locator('.social-bar-compose').wait_for()
    assert page.evaluate("view==='home'")
    sender=case.call('GET','/api/state',user=1)
    db=live_service._db()
    try:
     live_service._ensure_social_tables(db)
     db.execute('INSERT INTO player_profiles(uid,server_id,data,updated_at) VALUES(?,?,?,?) ON CONFLICT(uid,server_id) DO UPDATE SET data=excluded.data',(sender['uid'],'S1',json.dumps({'profile':{'avatar':'head_1001','frame':'frame_8001'}}),1));db.commit()
    finally:db.close()
    case.call('POST','/api/social-bar/action',{'action':'enter','room_id':'public:CROSS'},1)
    mid=case.call('POST','/api/social-bar/action',{'action':'send','room_id':'public:CROSS','text':'Avatar QA '+str(w)},1)['message_id']
    face=page.locator('.social-bar-msg').filter(has_text='Avatar QA '+str(w)).locator('.social-bar-avatar')
    face.wait_for()
    page.wait_for_function("Array.from(document.querySelectorAll('.social-bar-avatar img')).every(i=>i.complete&&i.naturalWidth>0)")
    assert face.get_attribute('data-frame')=='frame_8001'
    assert face.evaluate("e=>e.getBoundingClientRect().right<=e.nextElementSibling.getBoundingClientRect().left")
    db=live_service._db()
    try:
     db.execute('UPDATE player_profiles SET data=? WHERE uid=? AND server_id=?',(json.dumps({'profile':{'avatar':'head_1001','frame':'frame_8002'}}),sender['uid'],'S1'));db.commit()
    finally:db.close()
    page.wait_for_function("Array.from(document.querySelectorAll('.social-bar-msg')).some(e=>e.innerText.includes('Avatar QA "+str(w)+"')&&e.querySelector('.social-bar-avatar')?.dataset.frame==='frame_8002')")
    print('PASS equipped avatar/frame refresh on existing message',w,flush=True)

    page.locator('.social-bar-win .gs-win-x').click()
    page.wait_for_timeout(2300)
    assert not page.locator('.social-bar-win').count()
    print('PASS home icon + cross room',w,h,flush=True)
    ctx.close()
   browser.close()
finally:case.doCleanups()
