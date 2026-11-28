import sys,importlib.util, json, time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('qa',ROOT/'tests/test_pvp_http_sessions_20261113.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)
root=ROOT/'web'
case=qa.PvPHttpSessionTests('test_http_auth_cookies_real_pvp_and_replay_access')
case.setUp()
html="""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>#app-frame{position:relative;width:100%;height:95vh}.ar-stage{position:relative;height:70vh;--u:.5px}.ar-overlay{position:absolute;top:0;left:0;z-index:3;background:white}.ar-win{padding:8px}.ar-fight{position:static!important;width:auto!important;height:auto!important}</style></head><body><main id="app-frame"><section id="home-systems-view"></section><section id="event-battle-view" hidden></section></main></body></html>"""
setup="""
const $=id=>document.getElementById(id),number=n=>String(n);let state,view='home',developerMode=false;
const api=async(url,body)=>{const r=await fetch(url,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const x=await r.json();if(!r.ok)throw Error(x.error);return x;};
const showView=v=>{view=v;for(const id of ['arena-view','arena3v3-view','event-battle-view'])if($(id))$(id).hidden=id!==v+'-view';};
const Arena={chrome:()=>{},rankRow:()=>document.createElement('div'),inspect:()=>{}};
const GirlUI={notice:x=>window.notices.push(x),toast:x=>window.notices.push(x),stars:()=>document.createElement('span')};
const portrait=()=>document.createElement('span'),Shops={open:()=>{}},Arena3v3={open:()=>{}};
window.notices=[];window.played=[];window.audioPackets=0;window.audioPlayed=0;
const NativeAudio=window.Audio;window.Audio=function(src){const a=new NativeAudio(src);if(src.startsWith('blob:')){window.audioPackets++;a.addEventListener('playing',()=>window.audioPlayed++);}return a;};
async function watchEventBattle(data,origin,label){showView('event-battle');window.played.push({time:Date.now(),frames:data.report.frames.length,win:data.report.isWin,live:data.livePvP});await new Promise(r=>setTimeout(r,18000));}
"""
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox','--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream','--autoplay-policy=no-user-gesture-required'])
  pages=[]
  base=f'http://127.0.0.1:{case.port}'
  for i in range(2):
   ctx=browser.new_context(viewport={'width':390,'height':844},permissions=['microphone'])
   name,value=case.tokens[i].split('=',1)
   ctx.add_cookies([{'name':name,'value':value,'url':base}])
   page=ctx.new_page()
   page.route(base+'/qa',lambda r:r.fulfill(status=200,content_type='text/html',body=html,headers={'Permissions-Policy':'camera=(), microphone=(self), geolocation=()','Content-Security-Policy':"media-src 'self' blob:"}))
   page.goto(base+'/qa')
   page.add_style_tag(content=(root/'arena3v3.css').read_text())
   page.add_script_tag(content=setup+(root/'arena-online-native.js').read_text())
   page.evaluate("async()=>{state=await api('/api/state')}")
   pages.append(page)
  a,b=pages
  a.evaluate("NativeOnlineArenas.open('arena','home')")
  a.locator('.ar-fight').click(force=True)
  a.get_by_role('button',name='So Tài',exact=True).first.click(force=True)
  b.get_by_role('button',name='Đồng ý',exact=True).wait_for(timeout=10000)
  assert b.evaluate("played.length")==0
  b.get_by_role('button',name='Đồng ý',exact=True).click()
  a.get_by_role('button',name='Chọn Đội Hình Tấn Công',exact=True).wait_for(timeout=15000)
  a.get_by_role('button',name='Chọn Đội Hình Tấn Công',exact=True).click(force=True)
  a.locator('.ar-win').get_by_role('button',name='Chiến Đấu',exact=True).click(force=True)
  for pg in pages:pg.locator('.pvp-bubble').wait_for(timeout=20000)
  t1,t2=[pg.evaluate('played[0]') for pg in pages]
  assert t1['frames']==t2['frames'] and t1['win']!=t2['win'] and t1['live'] and t2['live'],(t1,t2)
  assert abs(t1['time']-t2['time'])<4000,(t1,t2)
  for pg in pages:pg.locator('.pvp-bubble>button').click()
  a.locator('.pvp-bubble-form input').fill('Xin chào trong trận')
  a.locator('.pvp-bubble-form button').click()
  b.locator('.pvp-bubble-messages').get_by_text('Xin chào trong trận',exact=False).wait_for(timeout=6000)
  b.get_by_role('button',name='🔊 Loa',exact=True).click()
  a.get_by_role('button',name='🎙 Mic',exact=True).click()
  b.wait_for_function('window.audioPlayed>0',timeout=10000)
  a.get_by_role('button',name='🔊 Loa',exact=True).click()
  b.get_by_role('button',name='🎙 Mic',exact=True).click()
  a.wait_for_function('window.audioPlayed>0',timeout=10000)
  a.evaluate("NativeOnlineArenas.stopComms()")
  assert a.locator('.pvp-bubble').count()==0
  print('PASS two browser contexts, real HTTP invite/accept, same battle frames, text and fake-device microphone relay; start delta ms:',abs(t1['time']-t2['time']),flush=True)
  browser.close()
finally:case.doCleanups()
