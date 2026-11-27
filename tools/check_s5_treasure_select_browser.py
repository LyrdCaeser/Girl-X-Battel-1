"""Browser UI check with original assets and isolated request fixture."""
import json,mimetypes
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]/'web'
from urllib.request import urlopen
catalog=json.load(urlopen('http://127.0.0.1:9080/assets/equipment/catalog.json',timeout=5))
script=(ROOT/'equipment.js').read_text()
girl=(ROOT/'girl-ui.js').read_text()
win=girl[girl.index(' function win('):girl.index(' function notice(')]
html='<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/equipment.css"><link rel="stylesheet" href="/girl-ui.css"></head><body><section id="girl-detail-view" style="position:relative;height:95vh;width:100%;--u:0.5px"><div id="detail-gear"></div></section></body></html>'
setup="""
const $=id=>document.getElementById(id),number=n=>String(n),view='detail';
const el=(tag,cls,txt)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(txt!==undefined)e.textContent=txt;return e;};
const sheetRoot=()=>$('girl-detail-view');
const GirlUI=(()=>{"""+win+""";return {win,toast:()=>{}};})();
let state={server_id:'S5',items:{},roster:[{partner_id:1,table_id:755013,lv:1,equips:[0,0,0,0,5108,0,0]}]},requests=[];
const renderGirlDetail=()=>Equipment.gear(state.roster[0]);
const api=async(path,req)=>{if(!req)return catalog;requests.push(req);state.roster[0].equips[4]=req.item_id;return {state,treasure:req.item_id};};
"""
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width,height in [(320,700),(390,844),(1280,800)]:
  page=browser.new_page(viewport={'width':width,'height':height})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   path=r.request.url.split('qa.invalid/',1)[-1].split('?')[0];f=ROOT/path
   if not path:r.fulfill(status=200,content_type='text/html',body=html)
   elif f.is_file():r.fulfill(status=200,content_type=mimetypes.guess_type(f)[0] or 'application/octet-stream',path=f)
   else:r.fulfill(status=404,body='')
  page.route('http://qa.invalid/**',route);page.goto('http://qa.invalid/')
  page.add_script_tag(content='const catalog='+json.dumps(catalog)+';'+setup+script+';Equipment.load().then(renderGirlDetail)')
  page.locator('.eq-slot.s5').click()
  assert page.get_by_role('button',name='Sửa Thuộc Tính',exact=True).count()==1
  page.get_by_role('button',name='Chọn Bảo Vật Khác',exact=True).click()
  assert page.locator('.eq-select-level select').input_value()=='1'
  assert page.locator('.eq-select-card').count()==2
  page.locator('.eq-select-level select').select_option('23')
  page.locator('.eq-select-card').first.click()
  apply=page.get_by_role('button',name='Chọn Bảo Vật',exact=True)
  assert apply.is_disabled()
  page.locator('.eq-select-confirm input').check()
  assert apply.is_enabled()
  assert page.locator('.eq-select-grid').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
  page.locator('.eq-select-card img').evaluate_all("es=>es.forEach(e=>e.loading='eager')")
  page.wait_for_function("Array.from(document.querySelectorAll('.eq-select-card img')).every(i=>i.complete&&i.naturalWidth>0)",timeout=5000)
  apply.click()
  page.wait_for_function('requests.length===1')
  assert page.evaluate('requests[0].confirm_level_change') is True
  assert page.evaluate('state.roster[0].equips[4]')==5749
  page.evaluate("state.server_id='S1';renderGirlDetail()")
  page.locator('.eq-slot.s5').click()
  assert page.get_by_role('button',name='Chọn Bảo Vật Khác',exact=True).count()==0
  assert not errors,errors
  print('PASS',width,'px: original art, level selection, explicit confirmation, S1 button hidden')
  page.close()
 browser.close()
