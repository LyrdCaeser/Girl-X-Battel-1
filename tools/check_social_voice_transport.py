"""Real SFU transport smoke test, synthetic test tone, never uses game accounts."""
import sys,secrets,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gxb2 import social_voice as v
from playwright.sync_api import sync_playwright

def main():
 room='qa-'+secrets.token_hex(8)
 ids=['qa-listener','qa-speaker']
 grants={'roomJoin':True,'room':room,'canSubscribe':True,'canPublish':False,'canPublishData':False,'canPublishSources':['microphone']}
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox','--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream','--autoplay-policy=no-user-gesture-required'])
  try:
   pages=[]
   for ident in ids:
    ctx=browser.new_context(permissions=['microphone'])
    page=ctx.new_page()
    page.route('https://180-93-111-99.sslip.io/voice-qa-page',lambda route:route.fulfill(content_type='text/html',body='<html><body>Voice QA</body></html>'))
    page.goto('https://180-93-111-99.sslip.io/voice-qa-page')
    page.add_script_tag(url='https://180-93-111-99.sslip.io/vendor/livekit-client-2.15.6.js')
    page.evaluate("""async ({url,token,relay})=>{
      window.room=new LivekitClient.Room();
      window.received=null;
      room.on(LivekitClient.RoomEvent.TrackSubscribed,(t)=>{if(t.kind==='audio'){window.received=t;t.attach().play().catch(()=>{});}});
      await room.connect(url,token,relay?{rtcConfig:{iceTransportPolicy:"relay"}}:{});
    }""",{'url':v.PUBLIC_URL,'token':v.token(ident,grants,ttl=60),'relay':os.getenv('QA_FORCE_TURN')=='1'})
    pages.append(page)
   assert all(page.evaluate("room.state==='connected'") for page in pages)
   assert not pages[1].evaluate('room.localParticipant.permissions.canPublish')
   reply=v.rpc('UpdateParticipant',room,identity=ids[1],permission=v.permission(True))
   assert reply and (reply['permission'].get('canPublish') or reply['permission'].get('can_publish'))
   pages[1].wait_for_function('room.localParticipant.permissions.canPublish',timeout=5000)
   pages[1].evaluate('room.localParticipant.setMicrophoneEnabled(true)')
   pages[0].wait_for_function('!!window.received',timeout=12000)
   pages[0].wait_for_function("""async()=>{const stats=await received.getRTCStatsReport();return !!stats&&Array.from(stats.values()).some(s=>s.type==='inbound-rtp'&&s.bytesReceived>0)}""",timeout=12000)
   print('PASS: WSS connected, listener cannot publish until approved, microphone RTP received; TURN forced='+str(os.getenv('QA_FORCE_TURN')=='1'))
   v.rpc('UpdateParticipant',room,identity=ids[1],permission=v.permission(False))
   pages[1].wait_for_function('!room.localParticipant.permissions.canPublish',timeout=5000)
   v.rpc('RemoveParticipant',room,identity=ids[0])
   pages[0].wait_for_function("room.state==='disconnected'",timeout=8000)
   print('PASS: server-side mic revoke and disconnect')
  finally:
   browser.close()
   for ident in ids:v.rpc('RemoveParticipant',room,identity=ident)
if __name__=='__main__':main()
