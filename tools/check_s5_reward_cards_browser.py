"""Isolated browser UI regression; never accesses a live account or DB."""
import json
import mimetypes
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]/'web'
home=(ROOT/'home-menus.js').read_text()
app=(ROOT/'app.js').read_text()
girl=(ROOT/'girl-ui.js').read_text()
extract=lambda src,a,b:src[src.index(a):src.index(b,src.index(a))]
js=extract(home,' function s5StarBadge(', ' function serverMail(parent)')
portrait=extract(app,'function portrait(', 'function error(')
stars=extract(girl,' function stars(n,', ' return {detail,load,picture,stars')
catalog=json.loads((ROOT/'assets/girls-catalog.json').read_text())
avatars=json.loads((ROOT/'assets/avatars.json').read_text())
ordinary=next(g for g in catalog if g['stars']==10 and g['group']==1 and str(g['id']) in avatars)
cosmos=next(g for g in catalog if g['stars']==10 and g['group']==7 and str(g['id']) in avatars)
sonia=next(g for g in catalog if g['id']==758001)
rows=[ordinary,cosmos,sonia]
hosts=[dict(partner_id=i+1,name=g['name'],stars=n,kit_claimed=False,job=g['job'],gear_claimed=False) for i,(g,n) in enumerate(zip(rows,(10,14,24)))]
roster=[dict(partner_id=i+1,table_id=g['id'],name=g['name'],group=g['group'],stars=n,equips=[0]*7) for i,(g,n) in enumerate(zip(rows,(10,14,24)))]
gear_sets={str(j):[1000*slot+100*j+69 for slot in (1,2,3,4)] for j in range(1,6)}
fixture=dict(claimed=True,remaining=1,hosts=hosts,gear_sets=gear_sets,skins=[dict(id=7001,name='Trang phục 1'),dict(id=7002,name='Trang phục 2')])
html='<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">'+''.join('<link rel="stylesheet" href="/'+f+'">' for f in ('style.css','home-menus.css','girl-ui.css','hero-glow.css','mobile-layout.css','desktop-layout.css'))+'</head><body></body></html>'
setup="""
const node=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e};
const el=(tag,text,cls)=>node(tag,cls,text);
let pending=false;let calls=[];
const cardIds=new Set(),artIds=new Set(),skinAvatarIds=new Set(),skinCardIds=new Set([7001,7002]);
const artId=id=>id,detailImage=id=>'/assets/skins/'+id+'.png';
const itemPicture=item=>'/assets/item-icons/'+item.icon+'.png';
const api=async(path,req)=>{if(req){calls.push(req);if(req.action==='kit')fixture.hosts.find(h=>h.partner_id===req.partner_id).kit_claimed=true;else if(req.action==='gear')fixture.hosts.find(h=>h.partner_id===req.partner_id).gear_claimed=true;else {fixture.remaining-=req.ids.length;fixture.skins=fixture.skins.filter(s=>!req.ids.includes(s.id));}return {state};}return fixture;};
const GirlUI=(()=>{const el=(tag,cls,text)=>node(tag,cls,text);const img=(src,cls,alt='')=>{const i=el('img',cls);i.src=src;i.alt=alt;return i};"""+stars+""";return {stars};})();
"""
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    for width,height,columns in ((320,700,2),(390,844,3),(1280,800,4)):
        page=browser.new_page(viewport=dict(width=width,height=height))
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        def route(r):
            path=r.request.url.split('qa.invalid/',1)[-1].split('?')[0]
            f=ROOT/path
            if not path:r.fulfill(status=200,content_type='text/html',body=html)
            elif f.is_file():r.fulfill(status=200,content_type=mimetypes.guess_type(f)[0] or 'application/octet-stream',path=f)
            else:r.fulfill(status=404,body='')
        page.route('http://qa.invalid/**',route)
        page.goto('http://qa.invalid/',wait_until='load')
        page.add_script_tag(content='const itemCatalog='+json.dumps(json.loads((ROOT/'assets/items-catalog.json').read_text()))+';const avatars='+json.dumps(avatars)+';const girlsCatalog='+json.dumps(rows)+';let state='+json.dumps(dict(roster=roster))+';const fixture='+json.dumps(fixture)+';'+setup+portrait+js+';openS5Rewards();')
        page.locator('.s5-reward-card').first.wait_for()
        page.wait_for_function("Array.from(document.querySelectorAll('.s5-girl-art img,.s5-rank img')).every(i=>i.complete&&i.naturalWidth>0)",timeout=3000)
        assert page.locator('.s5-reward-card').count()==3
        assert page.locator('.s5-rank .gu-emblem').count()==6
        assert 'star_orange.png' in page.locator('.s5-rank img').first.get_attribute('src')
        assert '_group_7_max.png' in page.locator('.s5-reward-card').nth(1).locator('.s5-rank img').last.get_attribute('src')
        assert '_group_7_max.png' in page.locator('.s5-reward-card').nth(2).locator('.s5-rank img').last.get_attribute('src')
        assert page.locator('.s5-reward-card').nth(2).inner_text().find('25 sao')>=0
        assert page.locator('.s5-rewards-grid').evaluate("e=>getComputedStyle(e).gridTemplateColumns.split(' ').length")==columns
        assert page.locator('#s5-rewards-dialog').evaluate("e=>e.scrollWidth<=e.clientWidth+1 && e.getBoundingClientRect().height<=innerHeight")
        assert page.locator('.s5-reward-card').evaluate_all("es=>es.every(e=>e.scrollWidth<=e.clientWidth+1)")
        page.locator('.s5-search').fill(rows[2]['name'])
        assert page.locator('.s5-reward-card').count()==1
        page.locator('.s5-reward-card').click()
        page.wait_for_function("document.querySelector('.s5-reward-card')?.disabled")
        assert page.evaluate('calls[0].partner_id')==3
        page.locator('.s5-tab').nth(1).click()
        page.locator('.s5-skin-card').first.click()
        page.locator('.s5-skin-card').nth(1).click()
        assert page.locator('.s5-skin-card.selected').count()==1
        page.locator('.s5-confirm').click()
        page.wait_for_function("document.querySelector('.s5-tab.active')?.textContent.endsWith('0')")
        assert page.evaluate('calls[1].ids')==[7001]
        page.locator('.s5-tab').nth(2).click()
        assert page.locator('.s5-gear-icons img').count()==12
        page.locator('.s5-gear-icons img').evaluate_all("es=>es.forEach(e=>e.loading='eager')")
        page.wait_for_function("Array.from(document.querySelectorAll('.s5-gear-icons img')).every(i=>i.complete&&i.naturalWidth>0)",timeout=5000)
        page.locator('.s5-reward-card').first.click()
        page.wait_for_function("document.querySelector('.s5-reward-card')?.disabled")
        assert page.evaluate('calls[2].action')=='gear'
        assert page.locator('.s5-reward-card').first.inner_text().find('Đã nhận trang bị')>=0
        page.locator('.s5-close').click()
        page.locator('#s5-rewards-dialog').wait_for(state='detached')
        assert not errors,errors
        print('PASS',width,'px:',columns,'columns, original images/stars, no overflow, search, claim, skin limit, close')
        page.close()
    browser.close()
