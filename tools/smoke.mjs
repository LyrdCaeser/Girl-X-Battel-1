// Smoke test: open every screen in headless Chrome, collect JS errors, failed requests and broken images.
import {spawn} from 'node:child_process';
const port=9333,dir=process.env.SP+'/chrome-prof';
async function ver(){try{return await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();}catch{return null;}}
if(!await ver()){const c=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',['--headless=new',`--remote-debugging-port=${port}`,`--user-data-dir=${dir}`,'--window-size=480,860','about:blank'],{stdio:'ignore',detached:true});c.unref();for(let i=0;i<50&&!await ver();i++)await new Promise(r=>setTimeout(r,200));}
const page=(await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find(t=>t.type==='page');
const ws=new WebSocket(page.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);let id=0;const pend={};const errors=[],failed=[];let cur='boot';
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&pend[m.id]){pend[m.id](m);delete pend[m.id];return;}
 if(m.method==='Runtime.exceptionThrown')errors.push([cur,(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text||'').split('\n').slice(0,2).join(' | ').slice(0,260)]);
 if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push([cur,'console: '+m.params.args.map(a=>a.value||a.description||'').join(' ').slice(0,200)]);
 if(m.method==='Network.responseReceived'&&m.params.response.status>=400)failed.push([cur,m.params.response.status,m.params.response.url.replace('http://localhost:9180','')]);};
const send=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method,params}));});
const ev=async(expr)=>{const r=await send('Runtime.evaluate',{expression:`(async()=>{${expr}})()`,awaitPromise:true,returnByValue:true});if(r.result?.exceptionDetails)errors.push([cur,'eval: '+(r.result.exceptionDetails.exception?.description||'').split('\n')[0].slice(0,200)]);return r.result?.result?.value;};
await send('Page.enable');await send('Runtime.enable');await send('Network.enable');await send('Emulation.setDeviceMetricsOverride',{width:480,height:860,deviceScaleFactor:1,mobile:false});
await send('Page.addScriptToEvaluateOnNewDocument',{source:"try{sessionStorage.setItem('gxb2-developer','1')}catch{}"});
await send('Page.navigate',{url:'http://localhost:9180/'});await new Promise(r=>setTimeout(r,4500));
const steps=JSON.parse(process.argv[2]);const broken=[];
for(const [name,js,extra] of steps){cur=name;await ev(js);await new Promise(r=>setTimeout(r,2200));
 for(const x of (extra||[])){cur=name+' › '+x[0];await ev(x[1]);await new Promise(r=>setTimeout(r,1500));}
 const b=await ev("return [...document.querySelectorAll('img')].filter(i=>i.complete&&!i.naturalWidth&&i.getAttribute('src')&&i.offsetParent).map(i=>i.getAttribute('src')).slice(0,6)");if(b&&b.length)broken.push([cur,b]);
 await ev("document.querySelectorAll('.gs-overlay,.ga2-wrap,.st-root,.ex-pop-wrap').forEach(e=>e.remove());if(typeof CampaignUI!=='undefined')document.querySelectorAll('.cu-popup,.campaign-popup').forEach(e=>e.remove());");}
console.log(JSON.stringify({errors,failed:failed.slice(0,60),broken},null,1));ws.close();process.exit(0);
